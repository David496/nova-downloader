import flet as ft
import database.db as db
import os
from core.config import config

class LibraryView(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 20
        self.padding = ft.Padding.all(30)
        self.scroll = ft.ScrollMode.AUTO
        self._build_ui()

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        
        self.controls.append(
            ft.Row([
                ft.Text("Biblioteca" if lang == "es" else "Library", size=28, weight=ft.FontWeight.BOLD, expand=True),
                ft.IconButton(ft.Icons.REFRESH, tooltip="Refrescar" if lang == "es" else "Refresh", on_click=lambda _: self.load_data()),
                ft.IconButton(ft.Icons.DELETE_SWEEP, icon_color=ft.Colors.RED_400, tooltip="Limpiar historial" if lang == "es" else "Clear history", on_click=self.clear_history)
            ])
        )
        
        self.grid = ft.ResponsiveRow(spacing=15, run_spacing=15)
        self.controls.append(self.grid)
        self.load_data()

    def load_data(self):
        self.grid.controls.clear()
        history = db.get_history()
        lang = config.get("language", "es")
        
        if not history:
            self.grid.controls.append(
                ft.Container(
                    content=ft.Text("No hay descargas aún." if lang == "es" else "No downloads yet.", color=ft.Colors.GREY_400),
                    alignment=ft.Alignment.CENTER,
                    padding=50
                )
            )
        else:
            for item in history:
                self.grid.controls.append(
                    ft.Column(
                        [self.create_history_card(item)],
                        col={"sm": 12, "md": 6, "lg": 4}
                    )
                )
        
        try:
            self.update()
        except:
            pass

    def create_history_card(self, item):
        # item: (id, title, url, file_type, quality, date, size, path)
        id, title, url, f_type, quality, date, size, path = item
        lang = config.get("language", "es")
        
        icon = ft.Icons.VIDEO_LIBRARY if f_type == "video" else ft.Icons.AUDIO_FILE
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(icon, color=ft.Colors.PURPLE_400),
                        title=ft.Text(title, weight=ft.FontWeight.W_600, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        subtitle=ft.Text(f"{date} • {f_type.upper()}", size=12, color=ft.Colors.GREY_400),
                    ),
                    ft.Row(
                        [
                            ft.TextButton("Carpeta" if lang == "es" else "Folder", icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: self.open_folder(path)),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda _, i=id: self.delete_item(i))
                        ],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                spacing=0
            ),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=15,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            padding=5,
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
        )

    def open_folder(self, path):
        if path and os.path.exists(path):
            if os.path.isdir(path):
                os.startfile(path)
            else:
                os.startfile(os.path.dirname(path))

    def delete_item(self, item_id):
        db.delete_from_history(item_id)
        self.load_data()

    def clear_history(self, e):
        db.clear_history()
        self.load_data()
