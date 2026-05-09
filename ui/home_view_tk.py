import customtkinter as ctk
from services.downloader import InfoExtractor
from core.config import config
import os
from utils.image_utils import load_image_async
from ui.components import Badge, LoadingSpinner, show_toast


class HomeView(ctk.CTkFrame):
    def __init__(self, parent, download_manager, go_to_downloads_cb):
        super().__init__(parent, fg_color="transparent")
        self.download_manager = download_manager
        self.go_to_downloads_cb = go_to_downloads_cb

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        self.center_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.center_frame,
            text="Descarga contenido de YouTube",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
        )
        title.grid(row=0, column=0, pady=(0, 10))

        subtitle = ctk.CTkLabel(
            self.center_frame,
            text="Pega un enlace para comenzar la descarga",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, pady=(0, 40))

        # Input Frame
        input_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.url_var,
            height=50,
            placeholder_text="https://www.youtube.com/watch?v=...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            border_width=2,
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.analyze_btn = ctk.CTkButton(
            input_frame,
            text="Analizar",
            height=50,
            width=140,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color="#FF0000",
            hover_color="#CC0000",
            corner_radius=8,
            command=self.analyze,
        )
        self.analyze_btn.grid(row=0, column=1)

        # Loading Container
        self.loading_container = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.loading_container.grid(row=3, column=0, pady=25)
        self.loading_spinner = None

        self.error_label = ctk.CTkLabel(
            self.center_frame, text="", text_color="#FF4E4E",
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.error_label.grid(row=3, column=0, pady=25)
        self.error_label.grid_remove()

        # Results Frame
        self.results_frame = ctk.CTkScrollableFrame(
            self.center_frame, fg_color="transparent",
            label_text="Resultado del análisis",
            label_font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.results_frame.grid(row=4, column=0, sticky="nsew", pady=10)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(4, weight=1)

        # Inner padding for results
        self.res_inner = ctk.CTkFrame(self.results_frame, fg_color=("#e5e5e5", "#1e1e1e"), corner_radius=12)
        self.res_inner.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.res_inner.grid_columnconfigure(1, weight=1)

        # Left side: Thumbnail
        self.thumb_lbl = ctk.CTkLabel(
            self.res_inner,
            text="",
            width=240,
            height=135,
            fg_color="#000000",
            corner_radius=8,
        )
        self.thumb_lbl.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        # Right side: Info Container
        self.info_container = ctk.CTkFrame(self.res_inner, fg_color="transparent")
        self.info_container.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.info_container.grid_columnconfigure(0, weight=1)

        self.title_var = ctk.StringVar()
        self.title_lbl = ctk.CTkLabel(
            self.info_container,
            textvariable=self.title_var,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            wraplength=500,
            justify="left",
        )
        self.title_lbl.grid(row=0, column=0, sticky="nw", pady=(0, 8))

        self.badges_frame = ctk.CTkFrame(self.info_container, fg_color="transparent")
        self.badges_frame.grid(row=1, column=0, sticky="w", pady=(0, 20))
        self.type_badge = Badge(self.badges_frame, text="VIDEO", color="#FF0000")
        self.type_badge.pack(side="left")

        self.playlist_var = ctk.BooleanVar(value=True)
        self.playlist_cb = ctk.CTkCheckBox(
            self.info_container,
            text="Descargar Playlist Completa",
            variable=self.playlist_var,
            fg_color="#FF0000",
            hover_color="#CC0000",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self.toggle_playlist_selection,
        )
        self.playlist_cb.grid(row=2, column=0, sticky="w", pady=(0, 15))
        self.playlist_cb.grid_remove()

        self.entries_frame = ctk.CTkFrame(
            self.info_container, fg_color=("gray90", "gray12"), corner_radius=8
        )
        self.entries_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.entries_frame.grid_remove()

        self.entry_vars = []
        self.entry_checkboxes = []
        self.current_image = None

        # Qualities
        self.quality_frame = ctk.CTkFrame(self.info_container, fg_color="transparent")
        self.quality_frame.grid(row=4, column=0, sticky="ew", pady=(0, 25))

        ctk.CTkLabel(
            self.quality_frame,
            text="Selecciona un formato:",
            font=ctk.CTkFont(family="Segoe UI", weight="bold", size=14),
        ).pack(anchor="w", pady=(0, 10))

        self.selected_quality = ctk.StringVar(value="")
        self.qualities = {
            "Video 4K (2160p)": {
                "format": "bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
            },
            "Video HD (1080p)": {
                "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
            },
            "Video SD (720p)": {
                "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
            },
            "Audio MP3 (320kbps)": {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }
                ],
            },
            "Audio FLAC": {
                "format": "bestaudio/best",
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "flac"}
                ],
            },
        }

        for q in self.qualities.keys():
            rb = ctk.CTkRadioButton(
                self.quality_frame,
                text=q,
                variable=self.selected_quality,
                value=q,
                fg_color="#FF0000",
                hover_color="#CC0000",
            )
            rb.pack(anchor="w", pady=3)

        self.download_btn = ctk.CTkButton(
            self.info_container,
            text="⭳ Iniciar Descarga",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#FF0000",
            hover_color="#CC0000",
            command=self.download,
        )
        self.download_btn.grid(row=5, column=0, sticky="w")

        self.results_frame.grid_remove()
        self.current_info = None

        self.results_frame.grid_remove()
        self.current_info = None

    def set_loading(self, is_loading):
        if is_loading:
            self.error_label.grid_remove()
            if not self.loading_spinner:
                self.loading_spinner = LoadingSpinner(self.loading_container)
                self.loading_spinner.pack()
            self.analyze_btn.configure(state="disabled")
        else:
            if self.loading_spinner:
                self.loading_spinner.stop()
                self.loading_spinner = None
            self.analyze_btn.configure(state="normal")

    def toggle_playlist_selection(self):
        if not self.playlist_var.get():
            self.entries_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        else:
            self.entries_frame.grid_remove()

    def analyze(self):
        url = self.url_var.get().strip()
        if not url:
            return

        self.set_loading(True)
        self.results_frame.grid_remove()
        self.playlist_cb.grid_remove()
        self.entries_frame.grid_remove()

        try:
            # Try to clear image separately first
            self.thumb_lbl.configure(image=None)
            self.thumb_lbl.configure(text="Cargando imagen...")
        except Exception:
            # Fallback if the previous image object is already invalid in Tcl
            try:
                self.thumb_lbl.configure(text="Cargando imagen...")
            except Exception:
                pass

        extractor = InfoExtractor(url, self.on_analyze_success, self.on_analyze_error)
        extractor.start()

    def on_image_loaded(self, ctk_image):
        if not self.winfo_exists():
            return

        try:
            if ctk_image:
                # Update label BEFORE replacing self.current_image reference
                # This ensures the old image is still alive in Tcl while the widget updates
                self.thumb_lbl.configure(image=ctk_image, text="")
                self.current_image = ctk_image
            else:
                self.thumb_lbl.configure(image=None, text="Sin Imagen")
                self.current_image = None
        except Exception as e:
            print(f"Error updating thumbnail: {e}")
            try:
                # Try to clear the image to recover the widget state
                self.thumb_lbl.configure(image=None, text="Error imagen")
                self.current_image = None
            except Exception:
                # If everything fails, just set text
                try:
                    self.thumb_lbl.configure(text="Error imagen")
                except Exception:
                    pass

    def on_analyze_success(self, info):
        def update_ui():
            self.current_info = info
            self.set_loading(False)

            title = info.get("title", "Desconocido")
            thumbnail_url = info.get("thumbnail")

            if thumbnail_url:
                load_image_async(self, thumbnail_url, (240, 135), self.on_image_loaded)
            else:
                self.thumb_lbl.configure(text="Sin Imagen")

            for cb in self.entry_checkboxes:
                cb.destroy()
            self.entry_checkboxes.clear()
            self.entry_vars.clear()

            if info.get("_type") == "playlist":
                self.type_badge.label.configure(text="PLAYLIST")
                entries = info.get("entries", [])
                title = f"{title} ({len(entries)} videos)"
                self.playlist_cb.grid(row=2, column=0, sticky="w", pady=(0, 10))
                self.playlist_var.set(True)

                # Limit the max number of displayed checkboxes to prevent UI freeze
                display_entries = entries[:100]
                for i, entry in enumerate(display_entries):
                    if not entry:
                        continue
                    var = ctk.BooleanVar(value=True)
                    self.entry_vars.append((entry, var))
                    cb_text = entry.get("title", f"Video {i+1}")
                    cb = ctk.CTkCheckBox(
                        self.entries_frame,
                        text=cb_text,
                        variable=var,
                        fg_color="#FF0000",
                        hover_color="#CC0000",
                    )
                    cb.pack(anchor="w", pady=2, padx=10)
                    self.entry_checkboxes.append(cb)

                if len(entries) > 100:
                    lbl = ctk.CTkLabel(
                        self.entries_frame,
                        text=f"...y {len(entries) - 100} videos más",
                        text_color="gray",
                    )
                    lbl.pack(anchor="w", pady=2, padx=10)
                    self.entry_checkboxes.append(lbl)
                    # For the hidden ones, just track variables without drawing widgets
                    for i in range(100, len(entries)):
                        entry = entries[i]
                        if not entry:
                            continue
                        var = ctk.BooleanVar(value=True)
                        self.entry_vars.append((entry, var))
            else:
                self.type_badge.label.configure(text="VIDEO")

            self.title_var.set(title)

            if not self.selected_quality.get():
                self.selected_quality.set("Video HD (1080p)")

            self.results_frame.grid()

        self.after(0, update_ui)

    def on_analyze_error(self, error):
        def update_ui():
            self.set_loading(False)
            self.error_label.configure(text=f"Error: {error}")
            self.error_label.grid()

        self.after(0, update_ui)

    def download(self):
        if not self.current_info:
            return
        quality_key = self.selected_quality.get()
        if not quality_key:
            return

        options = dict(self.qualities[quality_key])
        output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))

        from services.downloader import DownloadTask
        import time

        is_playlist = self.current_info.get("_type") == "playlist"
        file_type = "Audio" if "Audio" in quality_key else "Video"

        if is_playlist:
            download_entire = self.playlist_var.get()
            safe_title = "".join(
                [
                    c
                    for c in self.current_info.get("title", "Playlist")
                    if c.isalpha() or c.isdigit() or c in " -_"
                ]
            ).rstrip()
            final_dir = os.path.join(output_dir, safe_title)

            entries_to_download = []
            if download_entire:
                entries_to_download = self.current_info.get("entries", [])
            else:
                for entry, var in self.entry_vars:
                    if var.get():
                        entries_to_download.append(entry)

            if not entries_to_download:
                self.error_label.configure(text="No has seleccionado ningún video.")
                self.error_label.grid()
                return

            for i, entry in enumerate(entries_to_download, 1):
                if not entry:
                    continue
                url = entry.get("url", entry.get("webpage_url"))
                if not url:
                    continue

                t_opts = dict(options)
                t_opts["outtmpl"] = os.path.join(
                    final_dir, f"{i:02d} - %(title)s.%(ext)s"
                )
                title = entry.get("title", f"Video {i}")
                thumb = entry.get("thumbnail")
                task = DownloadTask(
                    url,
                    t_opts,
                    final_dir,
                    title,
                    file_type,
                    str(time.time()) + str(i),
                    thumb,
                )
                self.download_manager.add_task(task)
        else:
            url = self.url_var.get()
            title = self.current_info.get("title", "Video")
            thumb = self.current_info.get("thumbnail")
            task = DownloadTask(
                url, options, output_dir, title, file_type, str(time.time()), thumb
            )
            self.download_manager.add_task(task)

        self.url_var.set("")
        self.results_frame.grid_remove()

        # Show success toast using the main window
        show_toast(
            self.winfo_toplevel(), "✅ Añadido a la cola de descargas", duration=3000
        )
        self.go_to_downloads_cb()
