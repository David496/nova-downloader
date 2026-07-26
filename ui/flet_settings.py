import flet as ft
from core.config import config, save_config
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
        is_dark = config.get("theme", "dark") == "dark"
        is_embed = config.get("embed_metadata", True)
        
        # Header
        self.controls.append(
            ft.Column([
                ft.Text("Configuración" if lang == "es" else "Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Personaliza tus preferencias de descarga y apariencia" if lang == "es" else "Customize your download preferences and appearance", size=12, color=ft.Colors.GREY_400),
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

        # Section 3: Interfaz & Apariencia
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

        self.theme_switch = ft.Switch(
            label="Modo Oscuro (Dark Theme)" if lang == "es" else "Dark Mode",
            value=is_dark,
            active_color=ft.Colors.PURPLE_500,
            on_change=self.save_settings
        )

        ui_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE_ROUNDED, color=ft.Colors.PURPLE_400, size=20),
                    ft.Text("Apariencia e Idioma" if lang == "es" else "Appearance & Language", size=15, weight=ft.FontWeight.W_600),
                ], spacing=8),
                ft.Row([self.lang_dropdown], spacing=8),
                self.theme_switch
            ], spacing=12),
            padding=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.WHITE))
        )

        # About Footer Card with Developer Credit
        about_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CODE_ROUNDED, color=ft.Colors.PURPLE_300, size=18),
                ft.Text("Nova Downloader v2.0 • Desarrollado por David496", size=12, color=ft.Colors.PURPLE_300, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            padding=12,
            alignment=ft.Alignment.CENTER
        )

        self.controls.extend([
            path_card,
            meta_card,
            ui_card,
            about_card
        ])

    def pick_folder(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        path = filedialog.askdirectory()
        root.destroy()
        
        if path:
            self.path_input.value = path
            self.save_settings(None)

    def save_settings(self, e):
        config["download_dir"] = self.path_input.value
        config["language"] = self.lang_dropdown.value
        config["theme"] = "dark" if self.theme_switch.value else "light"
        config["embed_metadata"] = self.embed_switch.value
        save_config(config)
        
        # Global Refresh
        AppEvents.notify()
