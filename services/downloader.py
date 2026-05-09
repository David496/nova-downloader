import yt_dlp
import threading
import queue
import os

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
        self.task_queue = queue.Queue()
        self.progress_cb = progress_cb
        self.finished_cb = finished_cb
        self.error_cb = error_cb
        self._stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        self.current_task = None

    def add_task(self, task):
        self.task_queue.put(task)

    def _worker_loop(self):
        while not self._stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue
                
            self.current_task = task
            ydl_opts = {
                'outtmpl': os.path.join(task.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }
            # Remove any specific outtmpl if provided in options to avoid conflict, or handle safely
            task_options = dict(task.options)
            if 'outtmpl' in task_options:
                ydl_opts['outtmpl'] = task_options['outtmpl']
                del task_options['outtmpl']
                
            ydl_opts.update(task_options)
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(task.url, download=True)
                    if info:
                        self.finished_cb(task, {'title': info.get('title'), 'ext': info.get('ext'), 'path': ydl.prepare_filename(info)})
                    else:
                        self.error_cb(task, "Error o elemento saltado.")
            except Exception as e:
                self.error_cb(task, str(e))
            finally:
                self.task_queue.task_done()
                self.current_task = None

    def _progress_hook(self, d):
        if self._stop_event.is_set():
            raise Exception("Cancelled by user")
        if d['status'] == 'downloading':
            self.progress_cb(self.current_task, d)
        elif d['status'] == 'finished':
            self.progress_cb(self.current_task, {'status': 'converting', 'filename': d.get('filename')})

    def stop(self):
        self._stop_event.set()


class InfoExtractor(threading.Thread):
    def __init__(self, url, success_cb, error_cb):
        super().__init__(daemon=True)
        self.url = url
        self.success_cb = success_cb
        self.error_cb = error_cb

    def run(self):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.success_cb(info)
        except Exception as e:
            self.error_cb(str(e))