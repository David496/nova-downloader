import os
import sys

# Suppress Qt/FFmpeg C-level logging to keep console 100% clean
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.multimedia*=false;qt*=false;default.debug=false"
os.environ["FFMPEG_LOG_LEVEL"] = "quiet"
os.environ["AV_LOG_FORCE_NOCOLOR"] = "1"

try:
    if sys.platform == "win32":
        _nul_fd = os.open("NUL", os.O_WRONLY)
        os.dup2(_nul_fd, 2)
        os.close(_nul_fd)
except Exception:
    pass

import yt_dlp
import asyncio
import time
import threading
import queue
import re
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QCoreApplication, QUrl, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices

class MusicTrack:
    def __init__(self, title, artist, duration, thumbnail, url, track_id, stream_url=None):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.thumbnail = thumbnail
        self.url = url
        self.track_id = track_id
        self.stream_url = stream_url

class QtAudioPlayer:
    def __init__(self, loop=None, on_position=None, on_finished=None, on_error=None):
        self.loop = loop
        self.on_position = on_position
        self.on_finished = on_finished
        self.on_error = on_error
        self.is_playing = False
        self.duration_sec = 0
        self.position_sec = 0
        self.player = None
        self.audio_output = None
        self.media_devices = None
        self.app = None
        self.cmd_queue = queue.Queue()
        self._init_qt()

    def set_loop(self, loop):
        self.loop = loop

    def _on_audio_device_changed(self):
        try:
            default_dev = QMediaDevices.defaultAudioOutput()
            if default_dev and self.audio_output:
                self.audio_output.setDevice(default_dev)
        except Exception:
            pass

    def _init_qt(self):
        def qt_thread():
            if not QCoreApplication.instance():
                self.app = QCoreApplication(sys.argv)
            else:
                self.app = QCoreApplication.instance()

            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()

            # Dynamically bind to current Windows default audio output device & auto-update on device change
            try:
                default_dev = QMediaDevices.defaultAudioOutput()
                if default_dev:
                    self.audio_output.setDevice(default_dev)
                self.media_devices = QMediaDevices()
                self.media_devices.audioOutputsChanged.connect(self._on_audio_device_changed)
            except Exception:
                pass

            self.player.setAudioOutput(self.audio_output)
            self.audio_output.setVolume(0.8)

            self.player.positionChanged.connect(self._handle_position)
            self.player.durationChanged.connect(self._handle_duration)
            self.player.mediaStatusChanged.connect(self._handle_status)

            def process_q():
                while not self.cmd_queue.empty():
                    try:
                        cmd, args = self.cmd_queue.get_nowait()
                        if cmd == 'play_url':
                            self.player.stop()
                            target_src = args[0]
                            if target_src.startswith("http://") or target_src.startswith("https://"):
                                self.player.setSource(QUrl(target_src))
                            else:
                                self.player.setSource(QUrl.fromLocalFile(target_src))
                            self.player.play()
                        elif cmd == 'pause':
                            self.player.pause()
                        elif cmd == 'resume':
                            self.player.play()
                        elif cmd == 'stop':
                            self.player.stop()
                        elif cmd == 'seek':
                            self.player.setPosition(int(args[0] * 1000))
                        elif cmd == 'set_volume':
                            self.audio_output.setVolume(max(0.0, min(1.0, args[0])))
                    except Exception:
                        pass
                self.app.processEvents()

            self.timer = QTimer()
            self.timer.setInterval(30)
            self.timer.timeout.connect(process_q)
            self.timer.start()

            if hasattr(self.app, 'exec'):
                self.app.exec()
            else:
                self.app.exec_()

        self._loop_thread = threading.Thread(target=qt_thread, daemon=True)
        self._loop_thread.start()

        for _ in range(50):
            if self.player is not None:
                break
            time.sleep(0.05)

    def _handle_position(self, pos_ms):
        self.position_sec = pos_ms / 1000.0
        if self.on_position:
            if self.loop:
                try:
                    self.loop.call_soon_threadsafe(self.on_position, self.position_sec, self.duration_sec)
                except Exception:
                    pass
            else:
                try:
                    self.on_position(self.position_sec, self.duration_sec)
                except Exception:
                    pass

    def _handle_duration(self, dur_ms):
        self.duration_sec = dur_ms / 1000.0

    def _handle_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.is_playing = False
            if self.on_finished:
                if self.loop:
                    try:
                        self.loop.call_soon_threadsafe(self.on_finished)
                    except Exception:
                        pass
                else:
                    try:
                        self.on_finished()
                    except Exception:
                        pass
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.is_playing = False
            if self.on_error:
                if self.loop:
                    try:
                        self.loop.call_soon_threadsafe(self.on_error)
                    except Exception:
                        pass
                else:
                    try:
                        self.on_error()
                    except Exception:
                        pass
        elif status == QMediaPlayer.MediaStatus.StalledMedia:
            # Auto-recover from temporary buffer underruns
            if self.player and self.is_playing:
                try:
                    self.player.play()
                except Exception:
                    pass

    def play_url(self, stream_url):
        self.is_playing = True
        self.cmd_queue.put(('play_url', (stream_url,)))

    def pause(self):
        self.is_playing = False
        self.cmd_queue.put(('pause', ()))

    def resume(self):
        self.is_playing = True
        self.cmd_queue.put(('resume', ()))

    def stop(self):
        self.is_playing = False
        self.cmd_queue.put(('stop', ()))

    def seek(self, target_sec):
        self.cmd_queue.put(('seek', (target_sec,)))

    def set_volume(self, volume_val):
        self.cmd_queue.put(('set_volume', (volume_val,)))

class PlayerService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.stream_cache = {}

    async def search_or_extract(self, query):
        query = query.strip()
        if not query:
            return []

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._run_search, query)

    def _run_search(self, query):
        is_url = bool(re.match(r'^(https?://|www\.)', query))
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
        }

        if is_url:
            target = query
        else:
            target = f"ytsearch6:{query}"

        tracks = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target, download=False)
                if not info:
                    return []

                entries = []
                if '_type' in info and info['_type'] == 'playlist':
                    entries = info.get('entries', [])
                elif 'entries' in info:
                    entries = info.get('entries', [])
                else:
                    entries = [info]

                for entry in entries:
                    if not entry:
                        continue
                    
                    video_id = entry.get('id', '')
                    url = entry.get('url') or (f"https://www.youtube.com/watch?v={video_id}" if video_id else "")
                    title = entry.get('title', 'Desconocido')
                    
                    # Enhanced multi-tier artist extraction
                    uploader = entry.get('channel') or entry.get('uploader') or entry.get('uploader_id') or entry.get('artist') or entry.get('creator')
                    if uploader and uploader.lower().endswith(' - topic'):
                        uploader = uploader[:-8].strip()

                    parsed_artist = None
                    for sep in [' - ', ' – ', ' | ']:
                        if sep in title:
                            parts = title.split(sep, 1)
                            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                                parsed_artist = parts[0].strip()
                                break

                    artist = uploader or parsed_artist or 'Artista Desconocido'
                    duration = entry.get('duration') or 0
                    thumbnail = entry.get('thumbnail') or (f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else "")

                    tracks.append(MusicTrack(
                        title=title,
                        artist=artist,
                        duration=duration,
                        thumbnail=thumbnail,
                        url=url,
                        track_id=video_id or url
                    ))
        except Exception as e:
            print(f"Error in PlayerService search: {e}")

        return tracks

    async def resolve_stream_url(self, track, force_refresh=False):
        if force_refresh:
            track.stream_url = None
            self.stream_cache.pop(track.url, None)

        if track.stream_url:
            return track.stream_url

        if track.url in self.stream_cache and not force_refresh:
            cached_url = self.stream_cache[track.url]
            track.stream_url = cached_url
            return track.stream_url

        loop = asyncio.get_running_loop()
        stream_url = await loop.run_in_executor(self.executor, self._run_resolve, track.url)
        if stream_url:
            self.stream_cache[track.url] = stream_url
            track.stream_url = stream_url
        return stream_url

    def _run_resolve(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'skip_download': True,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'url' in info:
                    return info['url']
        except Exception as e:
            print(f"Error resolving stream URL: {e}")
        return None
