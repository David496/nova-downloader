import yt_dlp
import asyncio
import threading
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

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

        # Run yt-dlp in a thread to not block the event loop
        with ThreadPoolExecutor() as executor:
            await self._loop.run_in_executor(executor, self._run_ydl, task, ydl_opts)

    def _run_ydl(self, task, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task.url, download=True)
                if info:
                    # Notify UI that the main task (or playlist) is done
                    self._loop.call_soon_threadsafe(self.finished_cb, task, {
                        'title': info.get('title'), 
                        'ext': info.get('ext'), 
                        'path': ydl.prepare_filename(info) if info.get('_type') != 'playlist' else task.output_path
                    })
                else:
                    self._loop.call_soon_threadsafe(self.error_cb, task, "Error o elemento saltado.")
        except Exception as e:
            self._loop.call_soon_threadsafe(self.error_cb, task, str(e))

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
            self._loop.call_soon_threadsafe(self.finished_cb, self.current_sub_task, {'title': current_title, 'path': d.get('filename')})

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
