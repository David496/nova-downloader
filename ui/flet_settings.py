import flet as ft
from core.config import config, save_config
import os
import tkinter as tk
from tkinter import filedialog
from ui.flet_styles import AppEvents

class SettingsView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 30
        self.padding = ft.Padding.all(30)
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        is_dark = config.get("theme", "dark") == "dark"
        
        self.controls.append(ft.Text("Configuración" if lang == "es" else "Settings", size=28, weight=ft.FontWeight.BOLD))
        
        # Path selection
        self.path_input = ft.TextField(
            label="Carpeta de Descargas" if lang == "es" else "Download Folder",
            value=config.get("download_dir", ""),
            read_only=True,
            expand=True,
            border_radius=12,
        )
        
        path_row = ft.Row([
            self.path_input,
            ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN,
                icon_color=ft.Colors.PURPLE_400,
                on_click=self.pick_folder,
                tooltip="Cambiar Carpeta" if lang == "es" else "Change Folder"
            )
        ])
        
        # Language
        self.lang_dropdown = ft.Dropdown(
            label="Idioma" if lang == "es" else "Language",
            value=lang,
            border_radius=12,
            options=[
                ft.DropdownOption("es", "Español"),
                ft.DropdownOption("en", "English"),
            ],
            on_select=self.save_settings
        )

        # Theme
        self.theme_switch = ft.Switch(
            label="Modo Oscuro" if lang == "es" else "Dark Mode",
            value=is_dark,
            on_change=self.save_settings
        )

        self.controls.extend([
            ft.Text("General" if lang == "es" else "General", size=20, weight=ft.FontWeight.W_600),
            path_row,
            self.lang_dropdown,
            ft.Divider(height=40, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            ft.Text("Apariencia" if lang == "es" else "Appearance", size=20, weight=ft.FontWeight.W_600),
            self.theme_switch
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
        save_config(config)
        
        # Global Refresh
        AppEvents.notify()
