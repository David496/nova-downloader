import yt_dlp
import asyncio
import threading
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from core.config import config

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
        self._loop = None
        self._stop_event = threading.Event()

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

    async def _process_task(self, task):
        self.current_parent_task = task
        self.current_sub_task = None
        ydl_opts = {
            'outtmpl': os.path.join(task.output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        task_options = dict(task.options)
        if 'outtmpl' in task_options:
            ydl_opts['outtmpl'] = task_options['outtmpl']
            del task_options['outtmpl']
            
        ydl_opts.update(task_options)

        # Enforce metadata & thumbnail embedding for audio tasks if enabled in settings
        if task.file_type == "audio" and config.get("embed_metadata", True):
            pps = list(ydl_opts.get('postprocessors', []))
            
            # Check codec
            extract_pp = next((p for p in pps if p.get('key') == 'FFmpegExtractAudio'), None)
            codec = extract_pp.get('preferredcodec') if extract_pp else 'mp3'

            if not any(p.get('key') == 'FFmpegMetadata' for p in pps):
                pps.append({'key': 'FFmpegMetadata', 'add_metadata': True})
                
            if codec in ['mp3', 'm4a', 'flac', 'aac', 'm4b']:
                ydl_opts['writethumbnail'] = True
                if not any(p.get('key') == 'EmbedThumbnail' for p in pps):
                    pps.append({'key': 'EmbedThumbnail', 'already_have_thumbnail': False})
                    
            ydl_opts['postprocessors'] = pps

        # Enforce subtitles downloading/embedding if enabled in settings (ONLY for video tasks)
        if task.file_type == "video" and config.get("download_subtitles", False):
            sub_lang_str = config.get("subtitle_lang", "es")
            langs = [l.strip() for l in sub_lang_str.split(',') if l.strip()]
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = langs
            
            if config.get("embed_subtitles", True):
                ydl_opts['embedsubtitles'] = True
                pps = list(ydl_opts.get('postprocessors', []))
                if not any(p.get('key') == 'FFmpegEmbedSubtitle' for p in pps):
                    pps.append({'key': 'FFmpegEmbedSubtitle'})
                ydl_opts['postprocessors'] = pps

        # Run yt-dlp in a thread to not block the event loop
        with ThreadPoolExecutor() as executor:
            await self._loop.run_in_executor(executor, self._run_ydl, task, ydl_opts)

    def _get_final_path(self, info, ydl, task):
        if info.get('_type') == 'playlist':
            return task.output_path
        
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

    def _run_ydl(self, task, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task.url, download=True)
                target_task = self.current_sub_task if self.current_sub_task else task
                if info:
                    if info.get('_type') == 'playlist':
                        entries = info.get('entries', [])
                        for entry in entries:
                            if entry:
                                final_path = self._get_final_path(entry, ydl, task)
                                title = entry.get('title', task.title)
                                self._loop.call_soon_threadsafe(self.finished_cb, target_task, {
                                    'title': title,
                                    'ext': entry.get('ext'),
                                    'path': final_path
                                })
                    else:
                        final_path = self._get_final_path(info, ydl, task)
                        title = info.get('title') or task.title
                        self._loop.call_soon_threadsafe(self.finished_cb, target_task, {
                            'title': title, 
                            'ext': info.get('ext'), 
                            'path': final_path
                        })
                else:
                    self._loop.call_soon_threadsafe(self.error_cb, target_task, "Error o elemento saltado.")
        except Exception as e:
            target_task = self.current_sub_task if self.current_sub_task else task
            self._loop.call_soon_threadsafe(self.error_cb, target_task, str(e))

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

        if not self.current_sub_task or self.current_sub_task.title != current_title:
            self.current_sub_task = DownloadTask(
                url=self.current_parent_task.url,
                options=self.current_parent_task.options,
                output_path=self.current_parent_task.output_path,
                title=current_title,
                file_type=self.current_parent_task.file_type,
                task_id=str(uuid.uuid4()) if self.current_parent_task.options.get('yesplaylist') else self.current_parent_task.task_id
            )
            
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
            'extract_flat': 'in_playlist'
        }
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, InfoExtractor._run_ydl, url, ydl_opts)

    @staticmethod
    def _run_ydl(url, ydl_opts):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
