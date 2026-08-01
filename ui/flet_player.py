import flet as ft
import os
import uuid
import random
import asyncio
import time
import re
from core.config import config
from services.player import PlayerService, QtAudioPlayer
from services.downloader import DownloadTask
from ui.flet_styles import AppEvents
import database.db as db

class PlayerView(ft.Column):
    def __init__(self, download_manager):
        super().__init__()
        self.download_manager = download_manager
        self.player_service = PlayerService()
        
        self.queue = []
        self.current_index = -1
        self.current_track = None
        
        self.is_shuffle = False
        self.is_repeat = False
        self.is_user_seeking = False
        self.is_muted = False
        self.last_volume = 0.8
        self.seek_lock_time = 0
        self.last_updated_sec = -1
        self.is_loading_track = False
        
        self.active_download_urls = set()
        self.active_download_titles = set()
        
        self.expand = True
        self.spacing = 12
        self.padding = ft.Padding.all(18)
        self.scroll = ft.ScrollMode.AUTO
        
        self.loop = None
        
        self.audio_player = QtAudioPlayer(
            on_position=self._on_audio_position,
            on_finished=self._on_audio_finished,
            on_error=self._on_audio_error
        )
        
        self._build_ui()
        AppEvents.subscribe(self.on_global_refresh)

    def did_mount(self):
        try:
            self.loop = asyncio.get_running_loop()
            self.audio_player.set_loop(self.loop)
        except Exception:
            pass
        self._update_hero_ui()
        self._update_queue_ui()

    def on_global_refresh(self):
        if self.loop and self.loop.is_running():
            try:
                self.loop.call_soon_threadsafe(self._refresh_queue_realtime)
            except Exception:
                pass
        else:
            self._refresh_queue_realtime()

    def _refresh_queue_realtime(self):
        self._update_hero_ui()
        self._update_queue_ui()

    def _sanitize_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', "", name).strip()

    def _get_downloaded_sets(self):
        urls = set()
        titles = set()
        dir_files = set()
        try:
            output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))
            if os.path.exists(output_dir):
                dir_files = {f.lower() for f in os.listdir(output_dir)}
        except Exception:
            pass

        try:
            history = db.get_history()
            for row in history:
                file_path = row[7] if len(row) > 7 else ""
                if file_path:
                    fname = os.path.basename(file_path).lower()
                    if fname in dir_files or os.path.exists(file_path):
                        if row[2]:
                            urls.add(row[2].strip().lower())
                        if row[1]:
                            titles.add(row[1].strip().lower())
        except Exception:
            pass
        return urls, titles, dir_files

    def _is_track_downloaded(self, track, downloaded_urls, downloaded_titles, dir_files=None):
        clean_t = self._sanitize_filename(track.title).lower()
        t_url = (track.url or "").strip().lower()
        
        if (t_url in downloaded_urls) or (clean_t in downloaded_titles) or (track.title.strip().lower() in downloaded_titles):
            return True

        if dir_files is not None:
            clean_fname = self._sanitize_filename(track.title).lower()
            for ext in ['.mp3', '.m4a', '.webm', '.opus', '.wav', '.mp4']:
                if f"{clean_fname}{ext}" in dir_files:
                    return True
        return False

    def _update_hero_ui(self):
        lang = config.get("language", "es")
        if self.current_track:
            self.track_title.value = self.current_track.title
            self.track_artist.value = self.current_track.artist
            self.total_time_lbl.value = self._format_seconds(self.current_track.duration)
            if self.current_track.thumbnail:
                self.thumbnail_img.src = self.current_track.thumbnail
                self.thumbnail_img.visible = True
                self.placeholder_icon.visible = False
            else:
                self.thumbnail_img.visible = False
                self.placeholder_icon.visible = True
                
            if self.is_loading_track:
                self.badge_lbl.value = "CARGANDO..."
                self.status_dot.bgcolor = ft.Colors.AMBER_400
            elif self.audio_player.is_playing:
                self.badge_lbl.value = "EN REPRODUCCIÓN" if lang == "es" else "PLAYING"
                self.status_dot.bgcolor = ft.Colors.GREEN_400
                self.play_btn.content.icon = ft.Icons.PAUSE_ROUNDED
            else:
                self.badge_lbl.value = "EN PAUSA" if lang == "es" else "PAUSED"
                self.status_dot.bgcolor = ft.Colors.AMBER_400
                self.play_btn.content.icon = ft.Icons.PLAY_ARROW_ROUNDED
        else:
            self.track_title.value = "Selecciona una canción" if lang == "es" else "Select a song"
            self.track_artist.value = "Haz clic en cualquier tema de la lista" if lang == "es" else "Click on any track in the queue"
            self.thumbnail_img.visible = False
            self.placeholder_icon.visible = True
            self.badge_lbl.value = "ESPERANDO PISTA" if lang == "es" else "READY"
            self.status_dot.bgcolor = ft.Colors.PURPLE_400
            self.play_btn.content.icon = ft.Icons.PLAY_ARROW_ROUNDED
            
        try:
            self.hero_card.update()
        except Exception:
            self._safe_update()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        # ---------------- HEADER ----------------
        header_icon = ft.Container(
            content=ft.Icon(ft.Icons.RADIO_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
            padding=8,
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_500),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400))
        )

        header = ft.Row([
            header_icon,
            ft.Column([
                ft.Text("Reproductor en Línea" if lang == "es" else "Online Player", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Escucha música en streaming en directo sin ocupar espacio en disco" if lang == "es" else "Stream live audio instantly without using disk storage", size=11, color=ft.Colors.GREY_400),
            ], spacing=1)
        ], spacing=12)

        # ---------------- SEARCH BAR SECTION ----------------
        self.search_input = ft.TextField(
            hint_text="Escribe una canción, artista o pega un enlace de YouTube..." if lang == "es" else "Search title, artist or paste YouTube link...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_radius=14,
            height=44,
            text_size=12,
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            focused_border_color=ft.Colors.PURPLE_400,
            content_padding=ft.Padding(14, 0, 14, 0),
            on_submit=self.on_search
        )

        self.paste_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CONTENT_PASTE_ROUNDED,
                icon_color=ft.Colors.PURPLE_300,
                icon_size=18,
                tooltip="Pegar enlace" if lang == "es" else "Paste link",
                on_click=self.on_paste
            ),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
            height=44,
            alignment=ft.Alignment.CENTER,
            ink=True,
            ink_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400)
        )

        self.search_btn = ft.ElevatedButton(
            "Buscar" if lang == "es" else "Search",
            icon=ft.Icons.HEADSET_ROUNDED,
            height=44,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                bgcolor=ft.Colors.PURPLE_600,
                color=ft.Colors.WHITE,
                elevation=3
            ),
            on_click=self.on_search
        )

        self.loading_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5, color=ft.Colors.PURPLE_400)

        self.save_playlist_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.PUSH_PIN_ROUNDED,
                icon_color=ft.Colors.PURPLE_300,
                icon_size=18,
                tooltip="Guardar Playlist de YouTube" if lang == "es" else "Pin YouTube Playlist",
                on_click=self.on_save_playlist_click
            ),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
            height=44,
            alignment=ft.Alignment.CENTER,
            ink=True,
            ink_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400)
        )

        search_row = ft.Row([
            self.search_input,
            self.paste_btn,
            self.save_playlist_btn,
            self.search_btn,
            self.loading_ring
        ], spacing=8, alignment=ft.MainAxisAlignment.START)

        self.saved_playlists_row = ft.Row([], spacing=8, scroll=ft.ScrollMode.AUTO)

        # ---------------- HERO PLAYER CARD (MORE PADDING & GENEROUS MARGINS) ----------------
        self.thumbnail_img = ft.Image(
            src="",
            width=175,
            height=175,
            border_radius=18,
            fit=ft.BoxFit.COVER,
            visible=False
        )
        
        self.placeholder_icon = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.DISC_FULL_ROUNDED, size=64, color=ft.Colors.with_opacity(0.25, ft.Colors.PURPLE_300)),
                ft.Text("NOVA PLAYER", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.with_opacity(0.35, ft.Colors.PURPLE_300))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            width=175,
            height=175,
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE)),
            alignment=ft.Alignment.CENTER
        )

        # Status Pill Badge
        self.status_dot = ft.Container(width=7, height=7, border_radius=3.5, bgcolor=ft.Colors.PURPLE_400)
        self.badge_lbl = ft.Text("ESPERANDO PISTA" if lang == "es" else "READY", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_200)
        
        self.badge_icon = ft.Container(
            content=ft.Row([
                self.status_dot,
                self.badge_lbl
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            padding=ft.Padding(10, 4, 10, 4),
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_500),
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400))
        )

        # HQ 320 KBPS Audio Quality Badge
        self.hq_badge = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HIGH_QUALITY_ROUNDED, color=ft.Colors.PURPLE_300, size=14),
                ft.Text("HQ • 320 KBPS", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_200)
            ], spacing=3),
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE_500),
            border_radius=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.PURPLE_400))
        )

        badge_header_row = ft.Row([
            self.badge_icon,
            self.hq_badge
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.track_title = ft.Text("Selecciona una canción" if lang == "es" else "Select a song", size=15, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE)
        self.track_artist = ft.Text("Haz clic en cualquier tema de la lista", size=11, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        
        self.current_time_lbl = ft.Text("00:00", size=10, color=ft.Colors.PURPLE_300, weight=ft.FontWeight.W_600)
        self.total_time_lbl = ft.Text("00:00", size=10, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_600)

        # Progress Slider
        self.progress_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            active_color=ft.Colors.PURPLE_400,
            inactive_color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
            on_change_start=self.on_slider_start,
            on_change=self.on_slider_change,
            on_change_end=self.on_slider_end,
        )

        # Player Control Buttons
        self.shuffle_container = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.SHUFFLE_ROUNDED,
                icon_color=ft.Colors.GREY_400,
                icon_size=18,
                tooltip="Modo Aleatorio" if lang == "es" else "Shuffle Mode",
                on_click=self.toggle_shuffle
            ),
            border_radius=10
        )

        self.prev_btn = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=28,
            tooltip="Anterior" if lang == "es" else "Previous",
            on_click=lambda _: self.play_prev()
        )

        self.play_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                icon_color=ft.Colors.WHITE,
                icon_size=34,
                on_click=self.toggle_play_pause
            ),
            width=56,
            height=56,
            border_radius=28,
            bgcolor=ft.Colors.PURPLE_600,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(2, ft.Colors.with_opacity(0.4, ft.Colors.PURPLE_300)),
            ink=True,
            ink_color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)
        )

        self.next_btn = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT_ROUNDED,
            icon_color=ft.Colors.WHITE,
            icon_size=28,
            tooltip="Siguiente" if lang == "es" else "Next",
            on_click=lambda _: self.play_next()
        )

        self.repeat_container = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.REPEAT_ROUNDED,
                icon_color=ft.Colors.GREY_400,
                icon_size=18,
                tooltip="Repetir canción" if lang == "es" else "Repeat song",
                on_click=self.toggle_repeat
            ),
            border_radius=10
        )

        controls_row = ft.Row([
            self.shuffle_container,
            self.prev_btn,
            self.play_btn,
            self.next_btn,
            self.repeat_container
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

        # Volume control
        self.volume_icon_btn = ft.IconButton(
            icon=ft.Icons.VOLUME_UP_ROUNDED,
            icon_color=ft.Colors.PURPLE_300,
            icon_size=16,
            on_click=self.toggle_mute
        )

        self.volume_val_lbl = ft.Text("80%", size=10, color=ft.Colors.PURPLE_200, weight=ft.FontWeight.BOLD)
        
        self.volume_badge = ft.Container(
            content=self.volume_val_lbl,
            padding=ft.Padding(6, 2, 6, 2),
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_500),
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400))
        )

        self.volume_slider = ft.Slider(
            min=0.0,
            max=1.0,
            value=0.8,
            active_color=ft.Colors.PURPLE_300,
            inactive_color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
            on_change=self.on_volume_change,
            expand=True
        )

        volume_row = ft.Row([
            self.volume_icon_btn,
            self.volume_slider,
            self.volume_badge
        ], spacing=2)

        # Hero Card with generous internal padding (24px)
        self.hero_card = ft.Container(
            content=ft.Column([
                badge_header_row,
                ft.Row([self.thumbnail_img, self.placeholder_icon], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column([
                    self.track_title,
                    self.track_artist,
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                
                ft.Column([
                    self.progress_slider,
                    ft.Row([self.current_time_lbl, self.total_time_lbl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=0),

                controls_row,
                volume_row
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=24,
            width=365,
            height=490,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE))
        )

        # ---------------- RIGHT QUEUE / PLAYLIST PANEL (SAME HEIGHT 490px) ----------------
        self.queue_count_lbl = ft.Container(
            content=ft.Text("0 canciones" if lang == "es" else "0 tracks", size=11, color=ft.Colors.PURPLE_300, weight=ft.FontWeight.W_600),
            padding=ft.Padding(10, 4, 10, 4),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE_500),
            border_radius=10
        )

        self.queue_list = ft.ListView(expand=True, spacing=8)

        self.clear_queue_btn = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.GREY_400,
            icon_size=18,
            tooltip="Vaciar lista" if lang == "es" else "Clear list",
            on_click=self.clear_queue
        )

        queue_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.QUEUE_MUSIC_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Cola de Reproducción" if lang == "es" else "Playback Queue", size=15, weight=ft.FontWeight.BOLD, expand=True, color=ft.Colors.WHITE),
                    self.queue_count_lbl,
                    self.clear_queue_btn
                ], spacing=8),
                ft.Divider(height=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
                self.queue_list
            ], spacing=10),
            padding=20,
            expand=True,
            height=490,
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
            border_radius=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        main_layout = ft.Row([
            self.hero_card,
            queue_container
        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=18, expand=True)

        self.controls.extend([
            header,
            search_row,
            self.saved_playlists_row,
            main_layout
        ])
        
        self._update_queue_ui()
        self._refresh_saved_playlists_ui()

    def _refresh_saved_playlists_ui(self):
        lang = config.get("language", "es")
        saved_items = db.get_saved_playlists() or []
        
        chips = [
            ft.Text("📌 Playlists guardadas:" if lang == "es" else "📌 Pinned Playlists:", size=11, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_600)
        ]

        if not saved_items:
            chips.append(
                ft.Text("Pega un enlace de playlist de YouTube y pulsa 📌 para fijarla aquí" if lang == "es" else "Paste a YouTube playlist URL and click 📌 to pin it here", size=11, color=ft.Colors.GREY_500, italic=True)
            )
        else:
            for item in saved_items:
                p_id, p_title, p_url, p_thumb, p_count, p_date = item
                chips.append(self._create_saved_playlist_chip(p_id, p_title, p_url, p_thumb, p_count))

        self.saved_playlists_row.controls = chips
        try:
            self.saved_playlists_row.update()
        except Exception:
            self._safe_update()

    def _create_saved_playlist_chip(self, p_id, title, url, thumb, count):
        lang = config.get("language", "es")
        disp_title = (title[:22] + "...") if len(title) > 25 else title
        count_str = f" • {count} canciones" if count > 0 else ""
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PLAYLIST_PLAY_ROUNDED, color=ft.Colors.PURPLE_300, size=15),
                ft.Text(f"{disp_title}{count_str}", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED,
                    icon_color=ft.Colors.GREY_400,
                    icon_size=12,
                    tooltip="Quitar de guardados" if lang == "es" else "Remove pinned",
                    on_click=lambda _: asyncio.create_task(self.delete_saved_playlist(p_id))
                )
            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.Padding(8, 2, 4, 2),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PURPLE_500),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.PURPLE_400)),
            ink=True,
            ink_color=ft.Colors.with_opacity(0.25, ft.Colors.PURPLE_400),
            on_click=lambda _: asyncio.create_task(self.load_saved_playlist(url))
        )

    async def delete_saved_playlist(self, p_id):
        db.delete_saved_playlist(p_id)
        self._refresh_saved_playlists_ui()

    async def load_saved_playlist(self, url):
        self.search_input.value = url
        self._safe_update()
        await self.on_search(None)

    async def on_save_playlist_click(self, e=None):
        url = self.search_input.value.strip()
        if not url and self.queue and self.current_track:
            url = self.current_track.url

        if not url:
            return

        title = "Playlist Guardada"
        thumb = ""
        count = len(self.queue)
        
        if self.queue:
            title = self.queue[0].title
            thumb = self.queue[0].thumbnail

        db.add_saved_playlist(title=title, url=url, thumbnail=thumb, track_count=count)
        self._refresh_saved_playlists_ui()

    def clear_queue(self, e=None):
        self.queue.clear()
        self.current_index = -1
        self.current_track = None
        self.active_download_urls.clear()
        self.active_download_titles.clear()
        self.audio_player.stop()
        self._update_hero_ui()
        self._update_queue_ui()

    def get_clipboard_text(self):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            val = root.clipboard_get()
            root.destroy()
            return val.strip() if val else ""
        except Exception:
            return ""

    async def on_paste(self, e):
        val = self.get_clipboard_text()
        if val:
            self.search_input.value = val
            self._safe_update()

    async def on_search(self, e):
        query = self.search_input.value.strip()
        if not query:
            return

        self.loading_ring.visible = True
        self.search_btn.disabled = True
        self._safe_update()

        tracks = await self.player_service.search_or_extract(query)

        self.loading_ring.visible = False
        self.search_btn.disabled = False

        if tracks:
            self.queue = tracks
            self.current_index = -1
            self._update_queue_ui()

        self._safe_update()

    def _update_queue_ui(self):
        self.queue_list.controls.clear()
        lang = config.get("language", "es")
        self.queue_count_lbl.content.value = f"{len(self.queue)} canciones" if lang == "es" else f"{len(self.queue)} tracks"

        if not self.queue:
            self.queue_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=44, color=ft.Colors.with_opacity(0.3, ft.Colors.PURPLE_300)),
                        ft.Text("Busca una canción o pega un enlace de YouTube para ver la lista" if lang == "es" else "Search a song or paste a YouTube link to view list", color=ft.Colors.GREY_400, size=12, text_align=ft.TextAlign.CENTER)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment.CENTER,
                    padding=50
                )
            )
            try:
                self.queue_list.update()
            except Exception:
                self._safe_update()
            return

        downloaded_urls, downloaded_titles, dir_files = self._get_downloaded_sets()

        for idx, track in enumerate(self.queue):
            is_active = idx == self.current_index
            
            clean_t = self._sanitize_filename(track.title).lower()
            t_url = (track.url or "").strip().lower()
            
            is_downloaded = self._is_track_downloaded(track, downloaded_urls, downloaded_titles, dir_files)
            is_downloading = not is_downloaded and ((t_url in self.active_download_urls) or (clean_t in self.active_download_titles))

            if is_active:
                bg = ft.Colors.with_opacity(0.18, ft.Colors.PURPLE_600)
                card_border = ft.Border(
                    left=ft.BorderSide(4, ft.Colors.PURPLE_400),
                    top=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400)),
                    right=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400)),
                    bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400))
                )
            else:
                bg = ft.Colors.with_opacity(0.04, ft.Colors.WHITE)
                card_border = ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))

            dur_str = self._format_seconds(track.duration)

            badges = []
            if is_active:
                badges.append(
                    ft.Container(
                        content=ft.Text("▶ REPRODUCIENDO" if lang == "es" else "▶ PLAYING", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        padding=ft.Padding(6, 2, 6, 2),
                        bgcolor=ft.Colors.PURPLE_600,
                        border_radius=6
                    )
                )
            if is_downloaded:
                badges.append(
                    ft.Container(
                        content=ft.Text("✓ DESCARGADO" if lang == "es" else "✓ IN LIBRARY", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        padding=ft.Padding(6, 2, 6, 2),
                        bgcolor=ft.Colors.GREEN_700,
                        border_radius=6
                    )
                )
            elif is_downloading:
                badges.append(
                    ft.Container(
                        content=ft.Text("⏳ DESCARGANDO..." if lang == "es" else "⏳ DOWNLOADING...", size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        padding=ft.Padding(6, 2, 6, 2),
                        bgcolor=ft.Colors.AMBER_800,
                        border_radius=6
                    )
                )

            thumb_control = ft.Image(src=track.thumbnail, width=42, height=42, border_radius=8, fit=ft.BoxFit.COVER) if track.thumbnail else ft.Container(
                content=ft.Icon(ft.Icons.MUSIC_NOTE, size=20, color=ft.Colors.PURPLE_300),
                width=42, height=42, border_radius=8, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), alignment=ft.Alignment.CENTER
            )

            if is_downloaded:
                dl_icon = ft.Icons.CHECK_CIRCLE_ROUNDED
                dl_color = ft.Colors.GREEN_400
                dl_tooltip = "Ya descargado en tu biblioteca"
            elif is_downloading:
                dl_icon = ft.Icons.HOURGLASS_TOP_ROUNDED
                dl_color = ft.Colors.AMBER_400
                dl_tooltip = "Descargando en segundo plano..."
            else:
                dl_icon = ft.Icons.DOWNLOAD_ROUNDED
                dl_color = ft.Colors.GREY_400
                dl_tooltip = "Descargar MP3" if lang == "es" else "Download MP3"

            # Native Flet Material Ink & Hover Effect over the ENTIRE song rectangle
            item = ft.Container(
                content=ft.Row([
                    ft.Text(f"{idx+1}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300 if is_active else ft.Colors.GREY_500, width=22),
                    thumb_control,
                    ft.Column([
                        ft.Text(track.title, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.WHITE if is_active else ft.Colors.GREY_200),
                        ft.Row([
                            ft.Text(f"{track.artist} • {dur_str}", size=10, color=ft.Colors.PURPLE_200 if is_active else ft.Colors.GREY_400),
                            *badges
                        ], spacing=4)
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW_ROUNDED if not (is_active and self.audio_player.is_playing) else ft.Icons.PAUSE_ROUNDED,
                        icon_color=ft.Colors.PURPLE_300 if is_active else ft.Colors.WHITE,
                        icon_size=20,
                        tooltip="Reproducir" if lang == "es" else "Play",
                        on_click=lambda _, i=idx: asyncio.create_task(self.play_track_at(i))
                    ),
                    ft.IconButton(
                        icon=dl_icon,
                        icon_color=dl_color,
                        icon_size=17,
                        tooltip=dl_tooltip,
                        on_click=lambda _, t=track, downloaded=is_downloaded: asyncio.create_task(self.on_download_track(t, downloaded))
                    )
                ], spacing=8),
                padding=ft.Padding(12, 8, 12, 8),
                bgcolor=bg,
                border_radius=12,
                border=card_border,
                ink=True,
                ink_color=ft.Colors.with_opacity(0.25, ft.Colors.PURPLE_500),
                on_click=lambda _, i=idx: asyncio.create_task(self.play_track_at(i))
            )
            self.queue_list.controls.append(item)

        try:
            self.queue_list.update()
        except Exception:
            self._safe_update()

    async def play_track_at(self, index, force_refresh=False):
        if index < 0 or index >= len(self.queue) or self.is_loading_track:
            return

        self.is_loading_track = True
        self.current_index = index
        self.current_track = self.queue[index]

        self._update_hero_ui()
        self._update_queue_ui()

        # Resolve stream URL
        stream_url = await self.player_service.resolve_stream_url(self.current_track, force_refresh=force_refresh)
        
        # If cached link failed, retry once with fresh extraction!
        if not stream_url and not force_refresh:
            stream_url = await self.player_service.resolve_stream_url(self.current_track, force_refresh=True)

        if stream_url:
            self.audio_player.play_url(stream_url)
            self.is_loading_track = False
            self._update_hero_ui()
            
            # Prefetch next track in queue asynchronously
            next_idx = (index + 1) % len(self.queue) if self.queue else 0
            if next_idx < len(self.queue) and next_idx != index:
                asyncio.create_task(self.player_service.resolve_stream_url(self.queue[next_idx]))
        else:
            await asyncio.sleep(1.0)
            self.is_loading_track = False
            self.play_next()
            return

    def toggle_play_pause(self, e=None):
        if not self.current_track:
            return

        if self.audio_player.is_playing:
            self.audio_player.pause()
        else:
            self.audio_player.resume()

        self._update_hero_ui()

    def play_next(self):
        if not self.queue:
            return
        if self.is_shuffle:
            next_idx = random.randint(0, len(self.queue) - 1)
        else:
            next_idx = (self.current_index + 1) % len(self.queue)
        asyncio.create_task(self.play_track_at(next_idx))

    def play_prev(self):
        if not self.queue:
            return
        prev_idx = (self.current_index - 1) % len(self.queue)
        asyncio.create_task(self.play_track_at(prev_idx))

    def toggle_shuffle(self, e=None):
        self.is_shuffle = not self.is_shuffle
        if self.is_shuffle:
            self.shuffle_container.bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_500)
            self.shuffle_container.content.icon_color = ft.Colors.PURPLE_300
        else:
            self.shuffle_container.bgcolor = None
            self.shuffle_container.content.icon_color = ft.Colors.GREY_400
        self._safe_update()

    def toggle_repeat(self, e=None):
        self.is_repeat = not self.is_repeat
        if self.is_repeat:
            self.repeat_container.bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_500)
            self.repeat_container.content.icon_color = ft.Colors.PURPLE_300
        else:
            self.repeat_container.bgcolor = None
            self.repeat_container.content.icon_color = ft.Colors.GREY_400
        self._safe_update()

    def toggle_mute(self, e=None):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.last_volume = self.volume_slider.value
            self.audio_player.set_volume(0.0)
            self.volume_slider.value = 0.0
            self.volume_val_lbl.value = "0%"
            self.volume_icon_btn.icon = ft.Icons.VOLUME_OFF_ROUNDED
        else:
            self.audio_player.set_volume(self.last_volume)
            self.volume_slider.value = self.last_volume
            self.volume_val_lbl.value = f"{int(self.last_volume * 100)}%"
            self.volume_icon_btn.icon = ft.Icons.VOLUME_UP_ROUNDED
        self._safe_update()

    def on_volume_change(self, e):
        val = float(e.control.value)
        self.audio_player.set_volume(val)
        self.volume_val_lbl.value = f"{int(val * 100)}%"
        if val == 0:
            self.volume_icon_btn.icon = ft.Icons.VOLUME_OFF_ROUNDED
            self.is_muted = True
        else:
            self.volume_icon_btn.icon = ft.Icons.VOLUME_UP_ROUNDED
            self.is_muted = False
        try:
            self.volume_val_lbl.update()
        except Exception:
            self._safe_update()

    def on_slider_start(self, e):
        self.is_user_seeking = True

    def on_slider_change(self, e):
        val = float(e.control.value)
        if self.audio_player.duration_sec > 0:
            target_sec = (val / 100.0) * self.audio_player.duration_sec
            self.current_time_lbl.value = self._format_seconds(target_sec)
            try:
                self.current_time_lbl.update()
            except Exception:
                pass

    def on_slider_end(self, e):
        val = float(e.control.value)
        if self.audio_player.duration_sec > 0:
            target_sec = (val / 100.0) * self.audio_player.duration_sec
            self.audio_player.seek(target_sec)
        self.seek_lock_time = time.time() + 0.3
        self.is_user_seeking = False

    def _on_audio_position(self, pos_sec, dur_sec):
        if time.time() < self.seek_lock_time or self.is_user_seeking:
            return

        current_sec = int(pos_sec)
        if current_sec == self.last_updated_sec:
            return
        self.last_updated_sec = current_sec

        if dur_sec > 0:
            percent = min(100.0, max(0.0, (pos_sec / dur_sec) * 100.0))
            self.progress_slider.value = percent
            self.total_time_lbl.value = self._format_seconds(dur_sec)
        
        self.current_time_lbl.value = self._format_seconds(pos_sec)

        # Isolated direct updates ONLY to timeline controls to prevent re-rendering the thumbnail
        try:
            self.progress_slider.update()
            self.current_time_lbl.update()
            self.total_time_lbl.update()
        except Exception:
            pass

    def _on_audio_finished(self):
        if self.is_repeat and self.current_index >= 0:
            self.audio_player.seek(0)
            self.audio_player.resume()
        else:
            self.play_next()

    def _on_audio_error(self):
        """Called automatically if QMediaPlayer encounters an expired link, stall timeout, or playback error."""
        if self.current_track:
            saved_pos = getattr(self.audio_player, 'position_sec', 0)
            asyncio.create_task(self._auto_recover_playback(saved_pos))

    async def _auto_recover_playback(self, resume_sec=0):
        if self.current_track and self.current_index >= 0:
            fresh_url = await self.player_service.resolve_stream_url(self.current_track, force_refresh=True)
            if fresh_url:
                self.audio_player.play_url(fresh_url)
                if resume_sec > 5:
                    await asyncio.sleep(0.3)
                    self.audio_player.seek(resume_sec)

    async def _poll_download_completion(self, clean_title, t_url):
        output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))
        for _ in range(120): # Poll for up to 60 seconds (every 500ms)
            await asyncio.sleep(0.5)
            for ext in ['.mp3', '.m4a', '.webm', '.opus', '.wav']:
                if os.path.exists(os.path.join(output_dir, f"{clean_title}{ext}")):
                    self.active_download_urls.discard(t_url)
                    self.active_download_titles.discard(clean_title.lower())
                    self._update_hero_ui()
                    self._update_queue_ui()
                    return

    async def on_download_track(self, track, already_downloaded=False):
        if already_downloaded:
            return

        clean_title = self._sanitize_filename(track.title)
        t_url = (track.url or "").strip().lower()
        
        self.active_download_urls.add(t_url)
        self.active_download_titles.add(clean_title.lower())
        self._update_hero_ui()
        self._update_queue_ui()

        asyncio.create_task(self._poll_download_completion(clean_title, t_url))

        output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))
        embed_meta = config.get("embed_metadata", True)
        
        pps = [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}
        ]
        if embed_meta:
            pps.extend([
                {'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'},
                {'key': 'FFmpegMetadata', 'add_metadata': True},
                {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}
            ])

        options = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, f"{clean_title}.%(ext)s"),
            'writethumbnail': embed_meta,
            'postprocessors': pps,
            'noplaylist': True
        }

        task = DownloadTask(
            url=track.url,
            options=options,
            output_path=output_dir,
            title=clean_title,
            file_type="audio",
            task_id=str(uuid.uuid4()),
            thumbnail_url=track.thumbnail
        )
        
        await self.download_manager.add_task(task)
        self._update_hero_ui()
        self._update_queue_ui()

    def _safe_update(self):
        try:
            self.update()
        except:
            pass

    def _format_seconds(self, seconds):
        if not seconds or seconds < 0: return "00:00"
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"
