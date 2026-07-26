import flet as ft
from services.downloader import InfoExtractor
from core.config import config
import os

class FormatCard(ft.Container):
    def __init__(self, f_type, label, desc, options, on_click):
        super().__init__()
        self.f_type = f_type
        self.label = label
        self.options = options
        self.on_click_callback = on_click
        
        icon = ft.Icons.ONDEMAND_VIDEO if f_type == "video" else ft.Icons.AUDIOTRACK
        
        self.content = ft.Row(
            [
                ft.Icon(icon, color=ft.Colors.PURPLE_400, size=20),
                ft.Column(
                    [
                        ft.Text(label, weight=ft.FontWeight.BOLD, size=13),
                        ft.Text(desc, size=11, color=ft.Colors.GREY_400),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.PURPLE_400, size=18, visible=False)
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=12
        )
        self.padding = ft.Padding(14, 8, 14, 8)
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE))
        self.bgcolor = ft.Colors.with_opacity(0.03, ft.Colors.WHITE)
        self.on_click = self._handle_click
        self.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT)

    async def _handle_click(self, e):
        await self.on_click_callback(self)

    async def set_selected(self, selected):
        if selected:
            self.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.PURPLE_400)
            self.border = ft.Border.all(2, ft.Colors.PURPLE_400)
            self.content.controls[2].visible = True
        else:
            self.bgcolor = ft.Colors.with_opacity(0.03, ft.Colors.WHITE)
            self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
            self.content.controls[2].visible = False
        
        try:
            self.update()
        except:
            pass

class HomeView(ft.Column):
    def __init__(self, download_manager, nav_to_downloads):
        super().__init__()
        self.download_manager = download_manager
        self.nav_to_downloads = nav_to_downloads
        self.current_info = None
        self.selected_card = None
        
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 18
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")

        # Hero Section
        self.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Nova Downloader", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400),
                    ft.Text("La forma más rápida y elegante de bajar contenido" if lang == "es" else "The fastest and most elegant way to download content", size=13, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                margin=ft.Margin(0, 15, 0, 5)
            )
        )

        # Input Section
        self.url_input = ft.TextField(
            hint_text="Pega un enlace aquí (YouTube, etc...)" if lang == "es" else "Paste a link here (YouTube, etc...)",
            border_radius=12,
            height=50,
            text_size=14,
            expand=True,
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            focused_border_color=ft.Colors.PURPLE_400,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            on_submit=self.on_analyze,
            prefix_icon=ft.Icons.LINK_ROUNDED,
            content_padding=ft.Padding(15, 0, 15, 0)
        )
        
        self.analyze_btn = ft.ElevatedButton(
            "Analizar" if lang == "es" else "Analyze",
            height=50,
            width=130,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor=ft.Colors.PURPLE_600,
                color=ft.Colors.WHITE,
            ),
            on_click=self.on_analyze
        )

        self.paste_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CONTENT_PASTE_ROUNDED,
                icon_color=ft.Colors.PURPLE_300,
                tooltip="Pegar desde el portapapeles" if lang == "es" else "Paste from clipboard",
                on_click=self.on_paste
            ),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            height=50,
            alignment=ft.Alignment.CENTER
        )

        self.controls.append(
            ft.Row([self.url_input, self.paste_btn, self.analyze_btn], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        )

        # Status & Loading
        self.status_text = ft.Text("", size=13, color=ft.Colors.PURPLE_200)
        self.progress_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2.5, color=ft.Colors.PURPLE_400)
        self.controls.append(ft.Row([self.progress_ring, self.status_text], alignment=ft.MainAxisAlignment.CENTER))

        # Results Area
        self.results_container = ft.Column(visible=False, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.START)
        
        self.info_title = ft.Text("Título del Video", size=20, weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
        self.info_meta = ft.Text("", size=13, color=ft.Colors.GREY_400)
        self.thumbnail = ft.Image(src="", width=260, height=145, border_radius=12, fit=ft.BoxFit.COVER, visible=False)
        
        self.playlist_checkbox = ft.Checkbox(
            label="Descargar Playlist Completa" if lang == "es" else "Download Entire Playlist", 
            visible=False,
            value=True,
            on_change=self.on_playlist_toggle
        )
        
        self.playlist_items_container = ft.Column(visible=False, spacing=10)
        self.playlist_items_list = ft.ListView(expand=True, spacing=5, height=200)
        
        self.format_sections = ft.Column(spacing=15)
        self.video_list = ft.Column(spacing=8)
        self.audio_list = ft.Column(spacing=8)
        
        self.download_btn = ft.ElevatedButton(
            "Descargar Ahora" if lang == "es" else "Download Now",
            disabled=True,
            height=50,
            width=220,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=14),
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.PURPLE_700, ft.ControlState.DISABLED: ft.Colors.with_opacity(0.1, ft.Colors.WHITE)},
                color=ft.Colors.WHITE,
                elevation=6
            ),
            on_click=self.on_download
        )

        self.results_container.controls.extend([
            ft.Container(
                content=ft.Row([
                    self.thumbnail,
                    ft.Column([
                        self.info_title,
                        self.info_meta,
                        self.playlist_checkbox,
                    ], expand=True, spacing=12)
                ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=35),
                padding=25,
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                border_radius=25,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
            ),
            self.playlist_items_container,
            self.format_sections
        ])

        self.playlist_items_container.controls.extend([
            ft.Text("Selecciona los videos a descargar:" if lang == "es" else "Select videos to download:", size=16, weight=ft.FontWeight.W_600),
            ft.Container(
                content=self.playlist_items_list,
                padding=10,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=15,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE)
            )
        ])

        self.format_sections.controls.extend([
            ft.Column([
                ft.Row([ft.Icon(ft.Icons.VIDEOCAM, size=20, color=ft.Colors.PURPLE_300), ft.Text("Vídeo (MP4)" if lang == "es" else "Video (MP4)", size=18, weight=ft.FontWeight.W_600)]),
                self.video_list
            ], spacing=10),
            ft.Column([
                ft.Row([ft.Icon(ft.Icons.MUSIC_NOTE, size=20, color=ft.Colors.PURPLE_300), ft.Text("Solo Audio" if lang == "es" else "Audio Only", size=18, weight=ft.FontWeight.W_600)]),
                self.audio_list
            ], spacing=10),
            ft.Row([
                ft.Text("Selecciona una calidad para continuar" if lang == "es" else "Select a quality to continue", color=ft.Colors.GREY_500, expand=True, italic=True), 
                self.download_btn
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

        self.controls.append(self.results_container)

    async def on_playlist_toggle(self, e):
        self.playlist_items_container.visible = not self.playlist_checkbox.value
        try:
            self.update()
        except:
            pass

    def get_clipboard_text(self):
        if hasattr(self.page, "get_clipboard"):
            try:
                res = self.page.get_clipboard()
                if res: return res.strip()
            except:
                pass
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
        try:
            val = self.get_clipboard_text()
            if val:
                self.url_input.value = val
                try:
                    self.update()
                except:
                    pass
        except Exception as ex:
            print(f"Paste error: {ex}")

    async def on_analyze(self, e):
        url = self.url_input.value.strip()
        if not url: return
        
        lang = config.get("language", "es")
        self.status_text.value = "Analizando contenido..." if lang == "es" else "Analyzing content..."
        self.progress_ring.visible = True
        self.analyze_btn.disabled = True
        self.results_container.visible = False
        
        try:
            self.update()
        except:
            pass
        
        try:
            info = await InfoExtractor.extract(url)
            await self.on_analyze_finished(info)
        except Exception as ex:
            await self.on_analyze_error(str(ex))

    def _format_seconds(self, seconds):
        if not seconds: return "N/A"
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0: return f"{int(h)}h {int(m)}m {int(s)}s"
        return f"{int(m)}m {int(s)}s"

    async def on_analyze_finished(self, info):
        self.current_info = info
        self.status_text.value = ""
        self.progress_ring.visible = False
        self.analyze_btn.disabled = False
        
        title = info.get('title', 'Unknown Title')
        uploader = info.get('uploader', 'Unknown Author')
        duration = self._format_seconds(info.get('duration'))
        views = info.get('view_count', 0)
        
        if info.get('_type') == 'playlist':
            entries = info.get('entries', [])
            count = len(entries)
            self.info_meta.value = f"{uploader} • {count} videos"
            self.playlist_checkbox.visible = True
            self.playlist_checkbox.value = True
            self.playlist_items_container.visible = False
            
            # Fill playlist items list
            self.playlist_items_list.controls.clear()
            for entry in entries:
                self.playlist_items_list.controls.append(
                    ft.Checkbox(label=entry.get('title', 'Video'), value=True, data=entry.get('url'))
                )
        else:
            self.info_meta.value = f"{uploader} • {duration} • {views:,} views"
            self.playlist_checkbox.visible = False
            self.playlist_items_container.visible = False
            
        self.info_title.value = title
        
        # Thumbnail
        thumb_url = info.get('thumbnail')
        if thumb_url:
            self.thumbnail.src = thumb_url
            self.thumbnail.visible = True
        else:
            self.thumbnail.visible = False
            
        await self._create_cards()
        self.results_container.visible = True
        try:
            self.update()
        except:
            pass

    async def on_analyze_error(self, err):
        self.status_text.value = f"Error: {err}"
        self.progress_ring.visible = False
        self.analyze_btn.disabled = False
        try:
            self.update()
        except:
            pass

    async def _create_cards(self):
        self.video_list.controls.clear()
        self.audio_list.controls.clear()
        self.selected_card = None
        self.download_btn.disabled = True
        config.get("language", "es")

        video_qualities = [
            ("4K Ultra HD", "Calidad máxima (2160p)", {'format': 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}),
            ("1080p Full HD", "Alta definición", {'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}),
            ("720p HD", "Calidad estándar", {'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}),
            ("480p / 360p", "Ahorro de datos", {'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}),
        ]
        
        embed_meta = config.get("embed_metadata", True)
        
        mp3_high_pps = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
        mp3_std_pps = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        m4a_pps = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}]
        wav_pps = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]
        
        if embed_meta:
            mp3_high_pps.extend([{'key': 'FFmpegMetadata', 'add_metadata': True}, {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}])
            mp3_std_pps.extend([{'key': 'FFmpegMetadata', 'add_metadata': True}, {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}])
            m4a_pps.extend([{'key': 'FFmpegMetadata', 'add_metadata': True}, {'key': 'EmbedThumbnail', 'already_have_thumbnail': False}])
            wav_pps.extend([{'key': 'FFmpegMetadata', 'add_metadata': True}])

        audio_qualities = [
            ("MP3 Alta Fidelidad", "320kbps - Con portada y metadatos" if embed_meta else "320kbps - Calidad CD", {
                'format': 'bestaudio/best',
                'writethumbnail': embed_meta,
                'postprocessors': mp3_high_pps
            }),
            ("MP3 Estándar", "192kbps - Recomendado", {
                'format': 'bestaudio/best',
                'writethumbnail': embed_meta,
                'postprocessors': mp3_std_pps
            }),
            ("M4A / AAC", "Formato de audio ligero", {
                'format': 'bestaudio/best',
                'writethumbnail': embed_meta,
                'postprocessors': m4a_pps
            }),
            ("Formato WAV", "Sin compresión (Peso alto)", {
                'format': 'bestaudio/best',
                'postprocessors': wav_pps
            }),
        ]

        for label, desc, opts in video_qualities:
            card = FormatCard("video", label, desc, opts, self.on_card_selected)
            self.video_list.controls.append(card)
            
        for label, desc, opts in audio_qualities:
            card = FormatCard("audio", label, desc, opts, self.on_card_selected)
            self.audio_list.controls.append(card)
        
        try:
            self.update()
        except:
            pass

    async def on_card_selected(self, card):
        if self.selected_card:
            await self.selected_card.set_selected(False)
        self.selected_card = card
        await self.selected_card.set_selected(True)
        self.download_btn.disabled = False
        try:
            self.update()
        except:
            pass

    async def on_download(self, e):
        if not self.current_info or not self.selected_card:
            return
            
        output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))
        from services.downloader import DownloadTask
        import uuid
        
        base_options = dict(self.selected_card.options)
        
        if self.current_info.get('_type') == 'playlist':
            is_full = self.playlist_checkbox.value
            if is_full:
                title = self.current_info.get('title', 'Playlist')
                safe_title = "".join([c for c in title if c.isalnum() or c in ' -_']).strip()
                output_path = os.path.join(output_dir, safe_title)
                
                options = dict(base_options)
                options['outtmpl'] = os.path.join(output_path, '%(playlist_index)s - %(title)s.%(ext)s')
                options['yesplaylist'] = True
                
                task = DownloadTask(
                    url=self.url_input.value,
                    options=options,
                    output_path=output_path,
                    title=title,
                    file_type=self.selected_card.f_type,
                    task_id=str(uuid.uuid4()),
                    thumbnail_url=self.current_info.get('thumbnail')
                )
                await self.download_manager.add_task(task)
            else:
                selected_urls = [cb.data for cb in self.playlist_items_list.controls if cb.value]
                if not selected_urls: return
                
                for url in selected_urls:
                    entry = next((item for item in self.current_info.get('entries', []) if item.get('url') == url), {})
                    title = entry.get('title', 'Video')
                    options = dict(base_options)
                    options['noplaylist'] = True
                    
                    task = DownloadTask(
                        url=url,
                        options=options,
                        output_path=output_dir,
                        title=title,
                        file_type=self.selected_card.f_type,
                        task_id=str(uuid.uuid4())
                    )
                    await self.download_manager.add_task(task)
        else:
            title = self.current_info.get('title', 'Video')
            options = dict(base_options)
            options['noplaylist'] = True
            
            task = DownloadTask(
                url=self.url_input.value,
                options=options,
                output_path=output_dir,
                title=title,
                file_type=self.selected_card.f_type,
                task_id=str(uuid.uuid4()),
                thumbnail_url=self.current_info.get('thumbnail')
            )
            await self.download_manager.add_task(task)
            
        self.nav_to_downloads()
