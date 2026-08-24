import flet as ft
from core.config import config, save_config
import asyncio
import tkinter as tk
from tkinter import filedialog
from ui.flet_styles import AppEvents

class SettingsView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 15
        self.padding = ft.Padding.all(20)
        self.scroll = ft.ScrollMode.AUTO
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        is_embed = config.get("embed_metadata", True)
        sub_enabled = config.get("download_subtitles", False)
        sub_lang = config.get("subtitle_lang", "es")
        embed_subs = config.get("embed_subtitles", True)
        
        # Header
        self.controls.append(
            ft.Column([
                ft.Text("Configuración" if lang == "es" else "Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Personaliza tus preferencias de descarga e idioma" if lang == "es" else "Customize your download preferences and language", size=12, color=ft.Colors.GREY_400),
            ], spacing=1)
        )
        
        # Section 1: Descargas & Almacenamiento
        self.path_input = ft.TextField(
            label="Ruta de guardado" if lang == "es" else "Save path",
            value=config.get("download_dir", ""),
            read_only=True,
            expand=True,
            border_radius=10,
            text_size=13,
            content_padding=ft.Padding(12, 10, 12, 10),
        )
        
        path_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_SPECIAL_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Carpeta de Descargas" if lang == "es" else "Download Folder", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                ft.Row([
                    self.path_input,
                    ft.ElevatedButton(
                        "Cambiar" if lang == "es" else "Change",
                        icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            bgcolor=ft.Colors.PURPLE_600,
                            color=ft.Colors.WHITE,
                        ),
                        height=42,
                        on_click=self.pick_folder,
                    )
                ], spacing=8)
            ], spacing=10),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # Section 2: Música y Metadatos
        self.embed_switch = ft.Switch(
            label="Incrustar metadatos (título, artista) y portada automáticamente" if lang == "es" else "Automatically embed metadata (title, artist) & album cover",
            value=is_embed,
            active_color=ft.Colors.PURPLE_500,
            on_change=self.save_settings
        )

        meta_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Música y Portadas" if lang == "es" else "Music & Album Art", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                self.embed_switch
            ], spacing=10),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # Section 3: Subtítulos
        self.sub_switch = ft.Switch(
            label="Descargar subtítulos automáticamente al bajar videos" if lang == "es" else "Download subtitles automatically when saving videos",
            value=sub_enabled,
            active_color=ft.Colors.PURPLE_500,
            on_change=self.save_settings
        )

        self.embed_sub_switch = ft.Switch(
            label="Incrustar subtítulos dentro del video (si se desactiva, guarda .srt independiente)" if lang == "es" else "Embed subtitles inside video file (otherwise saves standalone .srt)",
            value=embed_subs,
            active_color=ft.Colors.PURPLE_500,
            on_change=self.save_settings
        )

        self.sub_lang_dropdown = ft.Dropdown(
            label="Idioma preferido de subtítulos" if lang == "es" else "Preferred subtitle language",
            value=sub_lang,
            border_radius=10,
            options=[
                ft.DropdownOption("es", "Español (es)"),
                ft.DropdownOption("en", "Inglés (en)"),
                ft.DropdownOption("es,en", "Español e Inglés (es,en)"),
                ft.DropdownOption("all", "Todos los idiomas disponibles (all)"),
            ],
            on_select=self.save_settings,
            expand=True
        )

        subs_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.SUBTITLES_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Subtítulos" if lang == "es" else "Subtitles", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                self.sub_switch,
                self.embed_sub_switch,
                ft.Row([self.sub_lang_dropdown], spacing=8)
            ], spacing=12),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # Section 4: Idioma
        self.lang_dropdown = ft.Dropdown(
            label="Idioma de la aplicación" if lang == "es" else "App Language",
            value=lang,
            border_radius=10,
            options=[
                ft.DropdownOption("es", "Español"),
                ft.DropdownOption("en", "English"),
            ],
            on_select=self.save_settings,
            expand=True
        )

        ui_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LANGUAGE_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Idioma" if lang == "es" else "Language", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                ft.Row([self.lang_dropdown], spacing=8)
            ], spacing=12),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # Section 5: Caché y Almacenamiento Temporal
        self.cache_status_lbl = ft.Text("", size=11, color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD)

        cache_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CLEANING_SERVICES_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Caché de Reproducción Online" if lang == "es" else "Online Player Cache", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                ft.Row([
                    ft.Text("Libera espacio eliminado las canciones temporales almacenadas." if lang == "es" else "Free up disk space by deleting temporary cached tracks.", size=12, color=ft.Colors.GREY_400, expand=True),
                    ft.ElevatedButton(
                        "Vaciar Caché" if lang == "es" else "Clear Cache",
                        icon=ft.Icons.DELETE_SWEEP_ROUNDED,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            bgcolor=ft.Colors.PURPLE_700,
                            color=ft.Colors.WHITE,
                        ),
                        height=38,
                        on_click=self.clear_player_cache,
                    )
                ], spacing=8),
                self.cache_status_lbl
            ], spacing=10),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # About Footer Card with Developer Credit
        about_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CODE_ROUNDED, color=ft.Colors.PURPLE_300, size=18),
                ft.Text("Nova Downloader v2.1.0 • Desarrollado por David496", size=12, color=ft.Colors.PURPLE_300, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            padding=12,
            alignment=ft.Alignment.CENTER
        )

        self.controls.extend([
            path_card,
            meta_card,
            subs_card,
            cache_card,
            ui_card,
            about_card
        ])

    def clear_player_cache(self, e):
        import os, tempfile
        cache_dir = os.path.join(tempfile.gettempdir(), "nova_stream_cache")
        count = 0
        try:
            if os.path.exists(cache_dir):
                for f in os.listdir(cache_dir):
                    f_path = os.path.join(cache_dir, f)
                    try:
                        if os.path.isfile(f_path):
                            os.remove(f_path)
                            count += 1
                    except Exception:
                        pass
        except Exception:
            pass
        
        lang = config.get("language", "es")
        msg = f"Caché liberada ({count} archivos eliminados)" if lang == "es" else f"Cache cleared ({count} files removed)"
        self.cache_status_lbl.value = f"✓ {msg}"
        try:
            self.cache_status_lbl.update()
        except Exception:
            pass

    def _ask_directory_dialog(self):
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            path = filedialog.askdirectory()
            root.destroy()
            return path
        except Exception as e:
            print(f"Error opening folder picker: {e}")
            return ""

    async def pick_folder(self, e):
        path = await asyncio.to_thread(self._ask_directory_dialog)
        if path:
            self.path_input.value = path
            self.save_settings(None)
            try:
                self.path_input.update()
            except Exception:
                pass

    def save_settings(self, e):
        config["download_dir"] = self.path_input.value
        config["language"] = self.lang_dropdown.value
        config["theme"] = "dark"
        config["embed_metadata"] = self.embed_switch.value
        config["download_subtitles"] = self.sub_switch.value
        config["embed_subtitles"] = self.embed_sub_switch.value
        config["subtitle_lang"] = self.sub_lang_dropdown.value
        save_config(config)
        
        # Global Refresh
        AppEvents.notify()
