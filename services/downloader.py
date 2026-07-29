import yt_dlp
import asyncio
import threading
import os
import uuid
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from core.config import config
from utils.cookies import apply_auto_cookies

def get_ffmpeg_location():
    """Detects and returns the absolute directory path of ffmpeg.exe to ensure instant 1st-run video/audio merging."""
    ff = shutil.which('ffmpeg')
    if ff:
        return os.path.dirname(ff)
    for candidate in [r"C:\ffmpeg\bin", r"C:\ffmpeg", os.path.join(os.path.dirname(os.path.dirname(__file__)), "ffmpeg")]:
        if os.path.exists(os.path.join(candidate, "ffmpeg.exe")):
            return candidate
    return None

class DownloadTask:
    def __init__(self, url, options, output_path, title, file_type, task_id, thumbnail_url=None):
        self.url = url
        self.options = options
        self.output_path = output_path
        self.title = title
        self.file_type = file_type
        self.task_id = task_id
        self.thumbnail_url = thumbnail_url

class DownloadManager:
    def __init__(self, progress_cb, finished_cb, error_cb):
        self.progress_cb = progress_cb
        self.finished_cb = finished_cb
        self.error_cb = error_cb
        self.queue = asyncio.Queue()
        self.current_parent_task = None
        self.current_sub_task = None
        self.sub_tasks_map = {} # title -> DownloadTask
        self.finished_titles = set()
        self._loop = None
        self._stop_event = threading.Event()
        self._ffmpeg_path = get_ffmpeg_location()

    async def start(self):
        self._loop = asyncio.get_running_loop()
        while not self._stop_event.is_set():
            try:
                task = await self.queue.get()
                await self._process_task(task)
                self.queue.task_done()
            except asyncio.CancelledError:
                break

    def stop(self):
        self._stop_event.set()

    async def add_task(self, task):
        # Notify UI instantly
        if self._loop:
            self._loop.call_soon_threadsafe(self.progress_cb, task, {'status': 'queued'})
        await self.queue.put(task)

    def _cleanup_thumbnail_files(self, output_path, title):
        """Removes leftover temporary .png, .webp, and .jpg thumbnail files ONLY after embedding completes."""
        if not output_path or not os.path.exists(output_path):
            return
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        
        # Specific exact name cleanup
        for ext in ['.png', '.webp', '.jpg', '.jpeg']:
            for fname in [f"{clean_title}{ext}", f"{title}{ext}"]:
                file_p = os.path.join(output_path, fname)
                if os.path.exists(file_p):
                    try:
                        os.remove(file_p)
                    except Exception:
                        pass

        # Search for any leftover PNG or WEBP matching title in directory
        try:
            for f in os.listdir(output_path):
                f_lower = f.lower()
                if f_lower.endswith(('.png', '.webp')) and (clean_title.lower() in f_lower):
                    try:
                        os.remove(os.path.join(output_path, f))
                    except Exception:
                        pass
        except Exception:
            pass

    async def _process_task(self, task):
        self.current_parent_task = task
        self.current_sub_task = None
        self.sub_tasks_map.clear()
        self.finished_titles.clear()
        
        ydl_opts = {
            'outtmpl': os.path.join(task.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'postprocessor_hooks': [self._postprocessor_hook],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
        }

        if self._ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self._ffmpeg_path
        
        task_options = dict(task.options)
        if 'outtmpl' in task_options:
            ydl_opts['outtmpl'] = task_options['outtmpl']
            del task_options['outtmpl']
            
        ydl_opts.update(task_options)

        # Enforce metadata & thumbnail embedding for audio tasks if enabled in settings
        if task.file_type == "audio" and config.get("embed_metadata", True):
            pps = list(ydl_opts.get('postprocessors', []))
            
            # Extract audio codec check
            extract_pp = next((p for p in pps if p.get('key') == 'FFmpegExtractAudio'), None)
            codec = extract_pp.get('preferredcodec') if extract_pp else 'mp3'

            # Build exact ordered postprocessor pipeline:
            # 1. FFmpegExtractAudio
            # 2. FFmpegThumbnailsConvertor (converts webp/png -> jpg for mutagen/FFmpeg)
            # 3. FFmpegMetadata (writes ID3/MP4 metadata tags)
            # 4. EmbedThumbnail (embeds converted jpg into mp3/m4a tags)
            
            new_pps = []
            if extract_pp:
                new_pps.append(extract_pp)
            else:
                new_pps.append({'key': 'FFmpegExtractAudio', 'preferredcodec': codec})

            if codec in ['mp3', 'm4a', 'flac', 'aac', 'm4b']:
                ydl_opts['writethumbnail'] = True
                new_pps.append({'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'})
                new_pps.append({'key': 'FFmpegMetadata', 'add_metadata': True})
                new_pps.append({'key': 'EmbedThumbnail', 'already_have_thumbnail': False})
            else:
                new_pps.append({'key': 'FFmpegMetadata', 'add_metadata': True})

            ydl_opts['postprocessors'] = new_pps

        # Enforce subtitles downloading/embedding if enabled in settings (ONLY for video tasks)
        if task.file_type == "video" and config.get("download_subtitles", False):
            sub_lang_str = config.get("subtitle_lang", "es")
            langs = [l.strip() for l in sub_lang_str.split(',') if l.strip()]
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = langs
            ydl_opts['ignoreerrors'] = True # Ensures HTTP 429 subtitle warnings never block the video download
            
            if config.get("embed_subtitles", True):
                ydl_opts['embedsubtitles'] = True
                ydl_opts['postprocessor_args'] = {
                    'ffmpegembedsubtitle': ['-c:s', 'mov_text']
                }
                pps = list(ydl_opts.get('postprocessors', []))
                if not any(p.get('key') == 'FFmpegEmbedSubtitle' for p in pps):
                    pps.append({'key': 'FFmpegEmbedSubtitle'})
                ydl_opts['postprocessors'] = pps

        # Run yt-dlp in a thread to not block the event loop
        with ThreadPoolExecutor() as executor:
            await self._loop.run_in_executor(executor, self._run_ydl, task, ydl_opts)

    def _get_final_path(self, info, ydl, task):
        if info and info.get('_type') == 'playlist':
            return task.output_path
        
        if info:
            prep_path = ydl.prepare_filename(info)
            reqs = info.get('_requested_downloads', [])
            if reqs and reqs[0].get('filepath'):
                if os.path.exists(reqs[0]['filepath']):
                    return reqs[0]['filepath']
                    
            if os.path.exists(prep_path):
                return prep_path
                
            base, _ = os.path.splitext(prep_path)
            for ext in ['.mp3', '.m4a', '.wav', '.flac', '.aac', '.ogg', '.mp4']:
                candidate = base + ext
                if os.path.exists(candidate):
                    return candidate
                    
            return prep_path

        # Fallback file search if info is None
        clean_title = re.sub(r'[\\/*?:"<>|]', "", task.title).strip()
        for fname in os.listdir(task.output_path):
            if clean_title.lower() in fname.lower():
                return os.path.join(task.output_path, fname)
                
        return task.output_path

    def _run_ydl(self, task, ydl_opts):
        ydl_opts = apply_auto_cookies(ydl_opts)
        if self._ffmpeg_path and 'ffmpeg_location' not in ydl_opts:
            ydl_opts['ffmpeg_location'] = self._ffmpeg_path

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task.url, download=True)
                
                # If info is None due to ignoreerrors on non-critical assets (like subtitles)
                if not info:
                    try:
                        info = ydl.extract_info(task.url, download=False)
                    except Exception:
                        info = {'title': task.title}

                if info.get('_type') == 'playlist':
                    entries = info.get('entries', [])
                    for entry in entries:
                        if entry:
                            title = entry.get('title', task.title)
                            self._cleanup_thumbnail_files(task.output_path, title)
                            if title not in self.finished_titles:
                                self.finished_titles.add(title)
                                final_path = self._get_final_path(entry, ydl, task)
                                sub_task = self.sub_tasks_map.get(title) or DownloadTask(
                                    url=task.url,
                                    options=task.options,
                                    output_path=task.output_path,
                                    title=title,
                                    file_type=task.file_type,
                                    task_id=str(uuid.uuid4())
                                )
                                self._loop.call_soon_threadsafe(self.finished_cb, sub_task, {
                                    'title': title,
                                    'ext': entry.get('ext'),
                                    'path': final_path
                                })
                    # Mark parent playlist task finished at the end of playlist execution
                    self._loop.call_soon_threadsafe(self.finished_cb, task, {
                        'title': task.title,
                        'ext': '',
                        'path': task.output_path
                    })
                else:
                    title = info.get('title') or task.title
                    self._cleanup_thumbnail_files(task.output_path, title)
                    final_path = self._get_final_path(info, ydl, task)
                    target_task = self.sub_tasks_map.get(title) or task
                    self._loop.call_soon_threadsafe(self.finished_cb, target_task, {
                        'title': title, 
                        'ext': info.get('ext', 'mp4'), 
                        'path': final_path
                    })
        except Exception as e:
            target_task = self.current_sub_task if self.current_sub_task else task
            self._loop.call_soon_threadsafe(self.error_cb, target_task, str(e))

    def _postprocessor_hook(self, d):
        """Triggers immediately when postprocessors (FFmpeg conversion/metadata) finish for each song."""
        if self._stop_event.is_set():
            raise Exception("Cancelled by user")

        if d.get('status') == 'finished':
            info = d.get('info_dict', {})
            title = info.get('title', '')
            
            sub_task = self.sub_tasks_map.get(title) or (self.current_sub_task if self.current_sub_task and self.current_sub_task.title == title else None)
            
            # ONLY trigger finished_cb if the EmbedThumbnail / final postprocessor has completed (or if no embed pp)
            pp_name = d.get('postprocessor', '')
            if pp_name in ['EmbedThumbnail', 'FFmpegMetadata', 'FFmpegEmbedSubtitle', ''] or not sub_task:
                if sub_task and title and title not in self.finished_titles:
                    self.finished_titles.add(title)
                    prep_path = d.get('filepath') or info.get('_filename') or info.get('filepath') or ''
                    
                    self._loop.call_soon_threadsafe(self.finished_cb, sub_task, {
                        'title': title,
                        'ext': info.get('ext', ''),
                        'path': prep_path
                    })

    def _progress_hook(self, d):
        if self._stop_event.is_set():
            raise Exception("Cancelled by user")

        info_dict = d.get('info_dict', {})
        current_title = info_dict.get('title', self.current_parent_task.title)
        
        # If it's a playlist, update the parent task status with item index
        if self.current_parent_task.options.get('yesplaylist'):
            idx = info_dict.get('playlist_index', '?')
            total = info_dict.get('n_entries', '?')
            self._loop.call_soon_threadsafe(self.progress_cb, self.current_parent_task, {
                'status': 'playlist_progress', 
                'msg': f"Bajando elemento {idx}/{total}..."
            })

        if current_title not in self.sub_tasks_map:
            sub_t = DownloadTask(
                url=self.current_parent_task.url,
                options=self.current_parent_task.options,
                output_path=self.current_parent_task.output_path,
                title=current_title,
                file_type=self.current_parent_task.file_type,
                task_id=str(uuid.uuid4()) if self.current_parent_task.options.get('yesplaylist') else self.current_parent_task.task_id
            )
            self.sub_tasks_map[current_title] = sub_t
            
        self.current_sub_task = self.sub_tasks_map[current_title]
            
        if d['status'] == 'downloading':
            self._loop.call_soon_threadsafe(self.progress_cb, self.current_sub_task, d)
        elif d['status'] == 'finished':
            self._loop.call_soon_threadsafe(self.progress_cb, self.current_sub_task, {'status': 'converting', 'filename': d.get('filename')})

class InfoExtractor:
    @staticmethod
    async def extract(url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'nocheckcertificate': True,
        }
        ff_loc = get_ffmpeg_location()
        if ff_loc:
            ydl_opts['ffmpeg_location'] = ff_loc

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, InfoExtractor._run_ydl, url, ydl_opts)

    @staticmethod
    def _run_ydl(url, ydl_opts):
        ydl_opts = apply_auto_cookies(ydl_opts)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
