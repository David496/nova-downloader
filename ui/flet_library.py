import flet as ft
import database.db as db
import os
from core.config import config

class LibraryView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 10
        self.padding = ft.Padding.all(16)
        self.scroll = ft.ScrollMode.AUTO
        
        self.search_query = ""
        self.filter_type = "all" # all, audio, video
        self.raw_history = []
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        # Compact Header
        self.title_text = ft.Text("Biblioteca" if lang == "es" else "Library", size=20, weight=ft.FontWeight.BOLD)
        self.subtitle_text = ft.Text("Historial de descargas" if lang == "es" else "Download history", size=11, color=ft.Colors.GREY_400)
        
        header_info = ft.Column([
            self.title_text,
            self.subtitle_text
        ], spacing=1)

        self.refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_size=18,
            icon_color=ft.Colors.PURPLE_300,
            tooltip="Refrescar" if lang == "es" else "Refresh", 
            on_click=lambda _: self.load_data(force_db=True)
        )
        
        self.clear_btn = ft.IconButton(
            icon=ft.Icons.DELETE_SWEEP_ROUNDED, 
            icon_color=ft.Colors.RED_400, 
            icon_size=18,
            tooltip="Limpiar historial" if lang == "es" else "Clear history", 
            on_click=self.confirm_clear_history
        )

        header = ft.Row(
            [
                header_info,
                ft.Row([self.refresh_btn, self.clear_btn], spacing=2)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Compact Search Input
        self.search_field = ft.TextField(
            hint_text="Buscar en la biblioteca..." if lang == "es" else "Search library...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_radius=10,
            height=38,
            text_size=11,
            content_padding=ft.Padding(10, 0, 10, 0),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            focused_border_color=ft.Colors.PURPLE_400,
            expand=True,
            on_change=self.on_search_change
        )

        # Compact Filter Chips
        def make_chip(label, icon_enum, f_key):
            is_active = self.filter_type == f_key
            controls = [ft.Text(label, size=11, weight=ft.FontWeight.W_600)]
            if icon_enum:
                controls.insert(0, ft.Icon(icon_enum, size=14))
                
            return ft.Container(
                content=ft.Row(controls, spacing=4) if icon_enum else controls[0],
                padding=ft.Padding(10, 4, 10, 4),
                border_radius=12,
                bgcolor=ft.Colors.PURPLE_600 if is_active else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                ink=True,
                ink_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400),
                on_click=lambda _: self.set_filter(f_key)
            )

        self.all_chip = make_chip("Todos" if lang == "es" else "All", None, "all")
        self.audio_chip = make_chip("Música" if lang == "es" else "Music", ft.Icons.MUSIC_NOTE_ROUNDED, "audio")
        self.video_chip = make_chip("Videos", ft.Icons.VIDEOCAM_ROUNDED, "video")

        self.chips_row = ft.Row([self.all_chip, self.audio_chip, self.video_chip], spacing=6)

        filter_row = ft.Row([
            self.search_field,
            self.chips_row
        ], spacing=10, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # List Container
        self.list_container = ft.Column(spacing=6)

        self.controls.extend([
            header,
            filter_row,
            self.list_container
        ])
        
        self.load_data(force_db=True)

    def set_filter(self, f_type):
        self.filter_type = f_type
        lang = config.get("language", "es")
        
        # Re-render chips concisely
        def make_chip(label, icon_enum, f_key):
            is_active = self.filter_type == f_key
            controls = [ft.Text(label, size=11, weight=ft.FontWeight.W_600)]
            if icon_enum:
                controls.insert(0, ft.Icon(icon_enum, size=14))
                
            return ft.Container(
                content=ft.Row(controls, spacing=4) if icon_enum else controls[0],
                padding=ft.Padding(10, 4, 10, 4),
                border_radius=12,
                bgcolor=ft.Colors.PURPLE_600 if is_active else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                ink=True,
                ink_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_400),
                on_click=lambda _: self.set_filter(f_key)
            )

        self.chips_row.controls = [
            make_chip("Todos" if lang == "es" else "All", None, "all"),
            make_chip("Música" if lang == "es" else "Music", ft.Icons.MUSIC_NOTE_ROUNDED, "audio"),
            make_chip("Videos", ft.Icons.VIDEOCAM_ROUNDED, "video")
        ]
        self.apply_filter_render()

    def on_search_change(self, e):
        self.search_query = self.search_field.value.strip().lower()
        self.apply_filter_render()

    def load_data(self, force_db=False):
        if force_db or not self.raw_history:
            self.raw_history = db.get_history() or []
        self.apply_filter_render()

    def apply_filter_render(self):
        self.list_container.controls.clear()
        lang = config.get("language", "es")
        
        if not self.raw_history:
            self.list_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER_OFF_ROUNDED, size=46, color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        ft.Text("No hay descargas registradas aún" if lang == "es" else "No downloads in history yet", size=14, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    alignment=ft.Alignment.CENTER,
                    padding=50,
                    bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                    border_radius=16,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
                )
            )
            try:
                self.update()
            except:
                pass
            return

        # Memory filter without redundant DB calls
        filtered = []
        q = self.search_query
        f_type = self.filter_type

        for item in self.raw_history:
            # item: (id, title, url, file_type, quality, date, size, path)
            _, title, url, item_ftype, quality, date, size, path = item
            
            if f_type != "all" and item_ftype != f_type:
                continue
                
            if q and (q not in (title or "").lower()) and (q not in (url or "").lower()):
                continue
                    
            filtered.append(item)

        if not filtered:
            self.list_container.controls.append(
                ft.Container(
                    content=ft.Text("No se encontraron coincidencias" if lang == "es" else "No matching items found", color=ft.Colors.GREY_400, size=13),
                    alignment=ft.Alignment.CENTER,
                    padding=35
                )
            )
        else:
            new_controls = [self.create_list_item(item) for item in filtered]
            self.list_container.controls.extend(new_controls)

        try:
            self.list_container.update()
        except:
            try:
                self.update()
            except:
                pass

    def create_list_item(self, item):
        # item: (id, title, url, file_type, quality, date, size, path)
        item_id, title, url, f_type, quality, date, size, path = item
        lang = config.get("language", "es")
        
        is_audio = f_type == "audio"
        icon_type = ft.Icons.MUSIC_NOTE_ROUNDED if is_audio else ft.Icons.PLAY_CIRCLE_FILL_ROUNDED
        icon_bg = ft.Colors.PURPLE_900 if is_audio else ft.Colors.DEEP_PURPLE_800
        badge_text = "AUDIO" if is_audio else "VIDEO"
        badge_color = ft.Colors.PURPLE_400 if is_audio else ft.Colors.AMBER_400

        file_exists = path and os.path.exists(path)

        return ft.Container(
            content=ft.Row(
                [
                    # Leading Icon
                    ft.Container(
                        content=ft.Icon(icon_type, color=ft.Colors.WHITE, size=16),
                        width=34,
                        height=34,
                        border_radius=8,
                        bgcolor=icon_bg,
                        alignment=ft.Alignment.CENTER
                    ),
                    
                    # File Info
                    ft.Column(
                        [
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(badge_text, size=8.5, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    bgcolor=badge_color,
                                    padding=ft.Padding(4, 1, 4, 1),
                                    border_radius=4
                                ),
                                ft.Text(date, size=10, color=ft.Colors.GREY_400),
                            ], spacing=6),
                            ft.Text(title, weight=ft.FontWeight.W_600, size=12.5, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                path if path else ("Sin ruta guardada" if lang == "es" else "No path saved"), 
                                size=9.5, 
                                color=ft.Colors.GREY_500, 
                                max_lines=1, 
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                        ],
                        spacing=1,
                        expand=True
                    ),
                    
                    # Compact Action Buttons
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED if file_exists else ft.Icons.PLAY_DISABLED_ROUNDED,
                                icon_color=ft.Colors.GREEN_400 if file_exists else ft.Colors.GREY_600,
                                icon_size=18,
                                tooltip=("Reproducir / Abrir" if lang == "es" else "Play / Open") if file_exists else ("Archivo no encontrado" if lang == "es" else "File not found"),
                                disabled=not file_exists,
                                on_click=lambda _, p=path: self.open_file(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                icon_color=ft.Colors.PURPLE_300,
                                icon_size=18,
                                tooltip="Abrir carpeta" if lang == "es" else "Open folder",
                                on_click=lambda _, p=path: self.open_folder(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=18,
                                tooltip="Eliminar de historial" if lang == "es" else "Remove from history",
                                on_click=lambda _, i=item_id: self.delete_item(i)
                            ),
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10
            ),
            padding=ft.Padding(10, 6, 10, 6),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            ink=True,
            ink_color=ft.Colors.with_opacity(0.15, ft.Colors.PURPLE_500),
            on_click=lambda _, p=path: self.open_file(p) if (path and os.path.exists(path)) else None
        )

    def open_file(self, path):
        if path and os.path.exists(path):
            try:
                os.startfile(path)
            except Exception as e:
                print(f"Error opening file: {e}")

    def open_folder(self, path):
        if path:
            target = path if os.path.exists(path) and os.path.isdir(path) else os.path.dirname(path)
            if os.path.exists(target):
                try:
                    os.startfile(target)
                except Exception as e:
                    print(f"Error opening folder: {e}")

    def delete_item(self, item_id):
        db.delete_from_history(item_id)
        self.load_data(force_db=True)

    def confirm_clear_history(self, e):
        db.clear_history()
        self.load_data(force_db=True)
