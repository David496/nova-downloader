import flet as ft
import database.db as db
import re
import asyncio
from core.config import config

class DownloadItem(ft.Container):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.task_id = task.task_id
        
        self.title_text = ft.Text(task.title, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        self.status_text = ft.Text("En cola..." if config.get("language") == "es" else "Queued...", size=12, color=ft.Colors.GREY_400)
        self.progress_bar = ft.ProgressBar(value=0, height=10, border_radius=5, color=ft.Colors.PURPLE_400, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        self.percentage_text = ft.Text("0%", size=12, weight=ft.FontWeight.W_600)
        
        self.content = ft.Column(
            [
                self.title_text,
                ft.Row([self.status_text, ft.Container(expand=True), self.percentage_text]),
                self.progress_bar
            ],
            spacing=8
        )
        self.padding = 20
        self.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        self.border_radius = 15
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        self.animate = ft.Animation(300, ft.AnimationCurve.DECELERATE)

    async def update_progress_async(self, d):
        if d['status'] == 'queued':
            self.status_text.value = "Esperando..." if config.get("language") == "es" else "Waiting..."
            self.progress_bar.value = 0
        elif d['status'] == 'playlist_progress':
            self.status_text.value = d.get('msg', 'Bajando playlist...')
            self.progress_bar.value = None # Indeterminate
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
            self.status_text.value = f"Descargando... {speed}" if config.get("language") == "es" else f"Downloading... {speed}"
            
        elif d['status'] == 'converting':
            self.progress_bar.value = None
            self.status_text.value = "Procesando archivos..." if config.get("language") == "es" else "Processing files..."
        
        try:
            self.update()
        except:
            pass

    async def set_finished_async(self):
        self.progress_bar.value = 1
        self.percentage_text.value = "100%"
        self.status_text.value = "Completado" if config.get("language") == "es" else "Finished"
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
        self.spacing = 20
        self.padding = ft.Padding.all(30)
        self.scroll = ft.ScrollMode.AUTO
        self.items = {} # task_id -> DownloadItem
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        self.title_label = ft.Text("Descargas Activas" if lang == "es" else "Active Downloads", size=28, weight=ft.FontWeight.BOLD)
        self.list_container = ft.Column(spacing=15)
        
        for item in self.items.values():
            self.list_container.controls.append(item)
            
        self.controls.extend([self.title_label, self.list_container])

    def on_progress(self, task, d):
        asyncio.create_task(self._on_progress_async(task, d))

    async def _on_progress_async(self, task, d):
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
        if task.task_id in self.items:
            await self.items[task.task_id].set_finished_async()
            
        db.add_download(
            title=task.title,
            url=task.url,
            file_type=task.file_type,
            quality=task.options.get('format', 'N/A'),
            size="N/A",
            path=info.get('path', '')
        )

    def on_error(self, task, err):
        asyncio.create_task(self._on_error_async(task, err))

    async def _on_error_async(self, task, err):
        if task.task_id in self.items:
            await self.items[task.task_id].set_error_async(err)
