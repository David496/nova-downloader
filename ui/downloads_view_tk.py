import customtkinter as ctk
from database.db import add_download
from utils.image_utils import load_image_async
from ui.components import Badge, show_toast
import time

class DownloadRow(ctk.CTkFrame):
    def __init__(self, parent, task):
        super().__init__(parent, fg_color=("gray85", "gray15"), corner_radius=8)
        self.task = task
        
        self.grid_columnconfigure(1, weight=1)
        
        # Left side: Thumbnail
        self.thumb_lbl = ctk.CTkLabel(self, text="...", width=120, height=68, fg_color="#212121", corner_radius=6)
        self.thumb_lbl.grid(row=0, column=0, rowspan=3, padx=15, pady=15, sticky="w")
        
        if task.thumbnail_url:
            load_image_async(self, task.thumbnail_url, (120, 68), self.on_image_loaded)
            
        # Top-right: Title & Badges
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=(15, 0))
        top_frame.grid_columnconfigure(0, weight=1)
        
        self.title_lbl = ctk.CTkLabel(top_frame, text=task.title, font=ctk.CTkFont(weight="bold"), anchor="w")
        self.title_lbl.grid(row=0, column=0, sticky="ew")
        
        b_color = "#FF0000" if task.file_type == "Video" else "#555555"
        self.badge = Badge(top_frame, text=task.file_type.upper(), color=b_color)
        self.badge.grid(row=0, column=1, sticky="e")
        
        # Middle-right: Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, progress_color="#FF0000", height=6)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=(10, 5))
        
        # Bottom-right: Status & Speed
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=(0, 15))
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        self.status_lbl = ctk.CTkLabel(bottom_frame, text="Iniciando...", text_color="gray", font=ctk.CTkFont(size=11), anchor="w")
        self.status_lbl.grid(row=0, column=0, sticky="w")
        
        self.speed_lbl = ctk.CTkLabel(bottom_frame, text="", text_color="gray", font=ctk.CTkFont(size=11), anchor="e")
        self.speed_lbl.grid(row=0, column=1, sticky="e")

    def on_image_loaded(self, ctk_image):
        if not self.winfo_exists(): return
        
        try:
            if ctk_image:
                self.current_image = ctk_image
                self.thumb_lbl.configure(image=ctk_image, text="")
            else:
                self.thumb_lbl.configure(text="Sin\nImagen")
        except Exception as e:
            print(f"Error updating row thumbnail: {e}")
            self.thumb_lbl.configure(image=None, text="Error")

    def update_progress(self, percent, speed_str, downloaded_str):
        self.progress_bar.set(percent / 100)
        self.status_lbl.configure(text=f"Descargando... {percent}%")
        self.speed_lbl.configure(text=f"{downloaded_str} • {speed_str}")

    def set_converting(self):
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_lbl.configure(text="Procesando archivo (FFmpeg)...")
        self.speed_lbl.configure(text="")

    def set_finished(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1)
        self.progress_bar.configure(progress_color="#00AA00")
        self.status_lbl.configure(text="Completado", text_color="#00AA00")
        self.speed_lbl.configure(text="")

    def set_error(self, err):
        self.progress_bar.stop()
        self.progress_bar.configure(progress_color="#FF4E4E")
        self.status_lbl.configure(text=f"Error: {err}", text_color="#FF4E4E")
        self.speed_lbl.configure(text="")


class DownloadsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        title = ctk.CTkLabel(header_frame, text="Cola de Descargas", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(side="left")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 40))
        
        self.rows = {}
        self.last_update = {}

    def on_progress(self, task, d):
        # Throttle UI updates to max 10fps per task
        now = time.time()
        if task.task_id in self.last_update:
            if now - self.last_update[task.task_id] < 0.1 and d['status'] == 'downloading':
                return
        self.last_update[task.task_id] = now

        def update():
            if task.task_id not in self.rows:
                row = DownloadRow(self.scroll_frame, task)
                row.pack(fill="x", padx=10, pady=5)
                self.rows[task.task_id] = row
            
            row = self.rows[task.task_id]
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                if total:
                    downloaded = d.get('downloaded_bytes', 0)
                    percent = int(downloaded / total * 100)
                    speed = d.get('speed')
                    speed_str = f" {(speed / 1024 / 1024):.1f} MB/s" if speed else ""
                    downloaded_str = f"{(downloaded / 1024 / 1024):.1f} MB"
                    row.update_progress(percent, speed_str, downloaded_str)
            elif d['status'] == 'converting':
                row.set_converting()
        
        self.after(0, update)

    def on_finished(self, task, result):
        def update():
            if task.task_id not in self.rows:
                row = DownloadRow(self.scroll_frame, task)
                row.pack(fill="x", padx=10, pady=5)
                self.rows[task.task_id] = row
            
            self.rows[task.task_id].set_finished()
            add_download(task.title, task.url, task.file_type, "N/A", "N/A", result.get('path', ''))
            show_toast(self.winfo_toplevel(), f"✅ Descarga completada: {task.title[:20]}...", duration=4000)
        self.after(0, update)

    def on_error(self, task, error):
        def update():
            if task.task_id not in self.rows:
                row = DownloadRow(self.scroll_frame, task)
                row.pack(fill="x", padx=10, pady=5)
                self.rows[task.task_id] = row
            self.rows[task.task_id].set_error(error)
            show_toast(self.winfo_toplevel(), f"❌ Error en descarga", duration=4000)
        self.after(0, update)