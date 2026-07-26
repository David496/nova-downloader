import flet as ft
import database.db as db
import os
from core.config import config

class LibraryView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 15
        self.padding = ft.Padding.all(20)
        self.scroll = ft.ScrollMode.AUTO
        
        self.search_query = ""
        self.filter_type = "all" # all, audio, video
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        # Header
        header = ft.Row(
            [
                ft.Column([
                    ft.Text("Biblioteca" if lang == "es" else "Library", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Historial de elementos descargados" if lang == "es" else "History of downloaded files", size=12, color=ft.Colors.GREY_400),
                ], spacing=1, expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH, 
                    tooltip="Refrescar" if lang == "es" else "Refresh", 
                    on_click=lambda _: self.load_data()
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_SWEEP_ROUNDED, 
                    icon_color=ft.Colors.RED_400, 
                    tooltip="Limpiar historial" if lang == "es" else "Clear history", 
                    on_click=self.confirm_clear_history
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # Search and Filter bar
        self.search_field = ft.TextField(
            hint_text="Buscar en la biblioteca..." if lang == "es" else "Search library...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=12,
            height=45,
            content_padding=ft.Padding(12, 0, 12, 0),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            focused_border_color=ft.Colors.PURPLE_400,
            expand=True,
            on_change=self.on_search_change
        )

        # Filter Chips
        self.all_chip = ft.Container(
            content=ft.Text("Todos" if lang == "es" else "All", size=13, weight=ft.FontWeight.W_600),
            padding=ft.Padding(14, 8, 14, 8),
            border_radius=20,
            bgcolor=ft.Colors.PURPLE_600,
            on_click=lambda _: self.set_filter("all")
        )
        self.audio_chip = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.MUSIC_NOTE, size=16), ft.Text("Música" if lang == "es" else "Music", size=13)], spacing=5),
            padding=ft.Padding(14, 8, 14, 8),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
            on_click=lambda _: self.set_filter("audio")
        )
        self.video_chip = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.VIDEOCAM, size=16), ft.Text("Videos", size=13)], spacing=5),
            padding=ft.Padding(14, 8, 14, 8),
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
            on_click=lambda _: self.set_filter("video")
        )

        filter_row = ft.Row([
            self.search_field,
            ft.Row([self.all_chip, self.audio_chip, self.video_chip], spacing=8)
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # List Container
        self.list_container = ft.Column(spacing=12)

        self.controls.extend([
            header,
            filter_row,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.list_container
        ])
        
        self.load_data()

    def set_filter(self, f_type):
        self.filter_type = f_type
        # Update chip styles
        for chip, name in [(self.all_chip, "all"), (self.audio_chip, "audio"), (self.video_chip, "video")]:
            if name == f_type:
                chip.bgcolor = ft.Colors.PURPLE_600
            else:
                chip.bgcolor = ft.Colors.with_opacity(0.06, ft.Colors.WHITE)
        self.load_data()

    def on_search_change(self, e):
        self.search_query = self.search_field.value.strip().lower()
        self.load_data()

    def load_data(self):
        self.list_container.controls.clear()
        history = db.get_history()
        lang = config.get("language", "es")
        
        if not history:
            self.list_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER_OFF_ROUNDED, size=55, color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        ft.Text("No hay descargas registradas aún" if lang == "es" else "No downloads in history yet", size=16, color=ft.Colors.GREY_400),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.Alignment.CENTER,
                    padding=60,
                    bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                    border_radius=20,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
                )
            )
            try:
                self.update()
            except:
                pass
            return

        # Filter items
        filtered = []
        for item in history:
            # item: (id, title, url, file_type, quality, date, size, path)
            _, title, url, f_type, quality, date, size, path = item
            
            # Type filter
            if self.filter_type != "all" and f_type != self.filter_type:
                continue
                
            # Search query filter
            if self.search_query:
                if self.search_query not in title.lower() and self.search_query not in url.lower():
                    continue
                    
            filtered.append(item)

        if not filtered:
            self.list_container.controls.append(
                ft.Container(
                    content=ft.Text("No se encontraron coincidencias" if lang == "es" else "No matching items found", color=ft.Colors.GREY_400, size=15),
                    alignment=ft.Alignment.CENTER,
                    padding=40
                )
            )
        else:
            for item in filtered:
                self.list_container.controls.append(self.create_list_item(item))

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

        # File status check
        file_exists = path and os.path.exists(path)

        return ft.Container(
            content=ft.Row(
                [
                    # Leading Icon
                    ft.Container(
                        content=ft.Icon(icon_type, color=ft.Colors.WHITE, size=20),
                        width=40,
                        height=40,
                        border_radius=10,
                        bgcolor=icon_bg,
                        alignment=ft.Alignment.CENTER
                    ),
                    
                    # File Info
                    ft.Column(
                        [
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(badge_text, size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    bgcolor=badge_color,
                                    padding=ft.Padding(5, 1, 5, 1),
                                    border_radius=5
                                ),
                                ft.Text(date, size=11, color=ft.Colors.GREY_400),
                            ], spacing=8),
                            ft.Text(title, weight=ft.FontWeight.W_600, size=14, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                path if path else ("Sin ruta guardada" if lang == "es" else "No path saved"), 
                                size=10, 
                                color=ft.Colors.GREY_500, 
                                max_lines=1, 
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                        ],
                        spacing=2,
                        expand=True
                    ),
                    
                    # Action Buttons
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED if file_exists else ft.Icons.PLAY_DISABLED,
                                icon_color=ft.Colors.GREEN_400 if file_exists else ft.Colors.GREY_600,
                                icon_size=20,
                                tooltip=("Reproducir / Abrir" if lang == "es" else "Play / Open") if file_exists else ("Archivo no encontrado" if lang == "es" else "File not found"),
                                disabled=not file_exists,
                                on_click=lambda _, p=path: self.open_file(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                icon_color=ft.Colors.PURPLE_300,
                                icon_size=20,
                                tooltip="Abrir carpeta" if lang == "es" else "Open folder",
                                on_click=lambda _, p=path: self.open_folder(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                icon_color=ft.Colors.RED_400,
                                icon_size=20,
                                tooltip="Eliminar de historial" if lang == "es" else "Remove from history",
                                on_click=lambda _, i=item_id: self.delete_item(i)
                            ),
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=12
            ),
            padding=ft.Padding(12, 8, 12, 8),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT)
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
        self.load_data()

    def confirm_clear_history(self, e):
        db.clear_history()
        self.load_data()
