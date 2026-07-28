import flet as ft
import database.db as db
import re
import asyncio
from core.config import config
from ui.flet_styles import AppEvents

class DownloadItem(ft.Container):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.task_id = task.task_id
        
        is_audio = task.file_type == "audio"
        icon_type = ft.Icons.MUSIC_NOTE_ROUNDED if is_audio else ft.Icons.VIDEO_LIBRARY_ROUNDED
        icon_color = ft.Colors.PURPLE_300 if is_audio else ft.Colors.AMBER_300

        self.title_text = ft.Text(task.title, weight=ft.FontWeight.BOLD, size=13, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        self.status_text = ft.Text("En cola..." if config.get("language") == "es" else "Queued...", size=10, color=ft.Colors.GREY_400)
        self.progress_bar = ft.ProgressBar(value=0, height=4, border_radius=2, color=ft.Colors.PURPLE_400, bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE))
        self.percentage_text = ft.Text("0%", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300)
        
        self.content = ft.Column(
            [
                ft.Row([
                    ft.Icon(icon_type, color=icon_color, size=16),
                    ft.Container(content=self.title_text, expand=True),
                    self.percentage_text
                ], spacing=6),
                self.progress_bar,
                ft.Row([self.status_text]),
            ],
            spacing=4
        )
        self.padding = ft.Padding(12, 6, 12, 6)
        self.bgcolor = ft.Colors.with_opacity(0.04, ft.Colors.WHITE)
        self.border_radius = 10
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        self.animate = ft.Animation(150, ft.AnimationCurve.DECELERATE)

    async def update_progress_async(self, d):
        if d['status'] == 'queued':
            self.status_text.value = "Esperando..." if config.get("language") == "es" else "Waiting..."
            self.progress_bar.value = 0
        elif d['status'] == 'playlist_progress':
            self.status_text.value = d.get('msg', 'Bajando playlist...')
            self.progress_bar.value = None
        elif d['status'] == 'downloading':
            p_raw = d.get('_percent_str', '0%')
            p_clean = re.sub(r'\x1b[^m]*m', '', p_raw).replace('%', '').strip()
            
            try:
                val = float(p_clean) / 100
                self.progress_bar.value = val
                self.percentage_text.value = f"{p_clean}%"
            except:
                pass
                
            speed = re.sub(r'\x1b[^m]*m', '', d.get('_speed_str', '')).strip()
            eta = re.sub(r'\x1b[^m]*m', '', d.get('_eta_str', '')).strip()
            extra = f" • {speed}" if speed else ""
            if eta:
                extra += f" • ETA {eta}"
            
            lang = config.get("language", "es")
            self.status_text.value = f"Descargando{extra}" if lang == "es" else f"Downloading{extra}"
            
        elif d['status'] == 'converting':
            self.progress_bar.value = None
            self.status_text.value = "Procesando archivos y metadatos..." if config.get("language") == "es" else "Processing files & metadata..."
        
        try:
            self.update()
        except:
            pass

    async def set_finished_async(self):
        self.progress_bar.value = 1
        self.percentage_text.value = "100%"
        self.percentage_text.color = ft.Colors.GREEN_400
        self.status_text.value = "Completado ✓" if config.get("language") == "es" else "Finished ✓"
        self.status_text.color = ft.Colors.GREEN_400
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.GREEN_400))
        try:
            self.update()
        except:
            pass

    async def set_error_async(self, err):
        self.progress_bar.value = 0
        self.status_text.value = f"Error: {err}"
        self.status_text.color = ft.Colors.RED_400
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.RED_400))
        try:
            self.update()
        except:
            pass

class DownloadsView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 12
        self.padding = ft.Padding.all(16)
        self.scroll = ft.ScrollMode.AUTO
        self.items = {} # task_id -> DownloadItem
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        self.title_label = ft.Text("Descargas Activas" if lang == "es" else "Active Downloads", size=20, weight=ft.FontWeight.BOLD)
        
        self.clear_btn = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED,
            icon_color=ft.Colors.GREY_400,
            icon_size=20,
            tooltip="Limpiar lista" if lang == "es" else "Clear list",
            on_click=self.clear_list
        )

        header_row = ft.Row([
            self.title_label,
            ft.Container(expand=True),
            self.clear_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.list_container = ft.Column(spacing=8)
        
        if not self.items:
            self.empty_card = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.DOWNLOAD_DONE_ROUNDED, size=46, color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                    ft.Text("No hay descargas activas en este momento" if lang == "es" else "No active downloads right now", size=14, color=ft.Colors.GREY_400),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                alignment=ft.Alignment.CENTER,
                padding=50,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                border_radius=16,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
            )
            self.list_container.controls.append(self.empty_card)
        else:
            for item in self.items.values():
                self.list_container.controls.append(item)
            
        self.controls.extend([header_row, self.list_container])

    def clear_list(self, e=None):
        self.items.clear()
        self._build_ui()
        try:
            self.update()
        except:
            pass

    def on_progress(self, task, d):
        asyncio.create_task(self._on_progress_async(task, d))

    async def _on_progress_async(self, task, d):
        if hasattr(self, 'empty_card') and self.empty_card in self.list_container.controls:
            self.list_container.controls.remove(self.empty_card)

        if task.task_id not in self.items:
            item = DownloadItem(task)
            self.items[task.task_id] = item
            self.list_container.controls.insert(0, item)
            try:
                self.update()
            except:
                pass
        
        await self.items[task.task_id].update_progress_async(d)

    def on_finished(self, task, info):
        asyncio.create_task(self._on_finished_async(task, info))

    async def _on_finished_async(self, task, info):
        target_title = (info.get('title') or task.title or "").strip().lower()
        
        # 1. Direct task_id match
        if task.task_id in self.items:
            await self.items[task.task_id].set_finished_async()

        # 2. Matching title search
        for item in list(self.items.values()):
            it_title = (item.task.title or "").strip().lower()
            if it_title and (it_title == target_title or target_title in it_title or it_title in target_title):
                await item.set_finished_async()

        # 3. If this is a parent playlist task finishing, resolve all remaining playlist items
        if task.options.get('yesplaylist'):
            for item in list(self.items.values()):
                st = str(item.status_text.value)
                if "Bajando elemento" in st or "Procesando" in st or "Descargando" in st:
                    await item.set_finished_async()

        db.add_download(
            title=info.get('title') or task.title,
            url=task.url,
            file_type=task.file_type,
            quality=task.options.get('format', 'N/A'),
            size="N/A",
            path=info.get('path', '')
        )
        AppEvents.notify()

    def on_error(self, task, err):
        asyncio.create_task(self._on_error_async(task, err))

    async def _on_error_async(self, task, err):
        item = self.items.get(task.task_id)
        if not item:
            for it in self.items.values():
                if "Procesando" in str(it.status_text.value) or "Descargando" in str(it.status_text.value):
                    item = it
                    break
        if item:
            await item.set_error_async(err)
