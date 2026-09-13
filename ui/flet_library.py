import flet as ft
import database.db as db
import os
from core.config import config
from ui.flet_styles import get_current_palette

class LibraryView(ft.Column):
    def __init__(self, on_play_audio=None):
        super().__init__()
        self.on_play_audio = on_play_audio
        self.view_mode = "list" # "list" or "grid"
        self.expand = True
        self.spacing = 10
        self.padding = ft.Padding.all(16)
        self.scroll = ft.ScrollMode.AUTO
        
        self.search_query = ""
        self.filter_type = "all" # all, audio, video
        self.raw_history = []
        self._build_ui()

    def set_view_mode(self, mode):
        if self.view_mode == mode:
            return
        self.view_mode = mode
        pal = get_current_palette()
        self.list_mode_btn.icon_color = pal.light if self.view_mode == "list" else ft.Colors.GREY_500
        self.list_mode_btn.bgcolor = pal.tint_bg if self.view_mode == "list" else ft.Colors.TRANSPARENT
        self.grid_mode_btn.icon_color = pal.light if self.view_mode == "grid" else ft.Colors.GREY_500
        self.grid_mode_btn.bgcolor = pal.tint_bg if self.view_mode == "grid" else ft.Colors.TRANSPARENT
        self.apply_filter_render()
        try:
            self.update()
        except Exception:
            pass

    def _build_ui(self):
        self.controls.clear()
        lang = config.get("language", "es")
        pal = get_current_palette()
        
        # Compact Header
        self.title_text = ft.Text("Biblioteca" if lang == "es" else "Library", size=20, weight=ft.FontWeight.BOLD)
        self.subtitle_text = ft.Text("Historial de descargas" if lang == "es" else "Download history", size=11, color=ft.Colors.GREY_400)
        
        header_info = ft.Column([
            self.title_text,
            self.subtitle_text
        ], spacing=1)

        self.list_mode_btn = ft.IconButton(
            icon=ft.Icons.VIEW_LIST_ROUNDED,
            icon_size=18,
            icon_color=pal.light if self.view_mode == "list" else ft.Colors.GREY_500,
            bgcolor=pal.tint_bg if self.view_mode == "list" else ft.Colors.TRANSPARENT,
            tooltip="Vista en lista" if lang == "es" else "List view",
            on_click=lambda _: self.set_view_mode("list")
        )
        self.grid_mode_btn = ft.IconButton(
            icon=ft.Icons.GRID_VIEW_ROUNDED,
            icon_size=18,
            icon_color=pal.light if self.view_mode == "grid" else ft.Colors.GREY_500,
            bgcolor=pal.tint_bg if self.view_mode == "grid" else ft.Colors.TRANSPARENT,
            tooltip="Vista en cuadrícula / carátulas" if lang == "es" else "Grid view",
            on_click=lambda _: self.set_view_mode("grid")
        )
        view_toggle = ft.Container(
            content=ft.Row([self.list_mode_btn, self.grid_mode_btn], spacing=2),
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border_radius=10,
            padding=2
        )

        self.refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_size=18,
            icon_color=pal.light,
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
                ft.Row([view_toggle, self.refresh_btn, self.clear_btn], spacing=4)
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
            focused_border_color=pal.primary,
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
                bgcolor=pal.dark if is_active else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                ink=True,
                ink_color=pal.tint_border,
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
        pal = get_current_palette()
        
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
                bgcolor=pal.dark if is_active else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                ink=True,
                ink_color=pal.tint_border,
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
            if self.view_mode == "grid":
                grid_row = ft.Row(
                    wrap=True, 
                    spacing=14, 
                    run_spacing=14, 
                    controls=[self.create_grid_item(item) for item in filtered]
                )
                self.list_container.controls.append(grid_row)
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

    def handle_play(self, item):
        item_id, title, url, f_type, quality, date, size, path = item
        lang = config.get("language", "es")
        if not path or not os.path.exists(path):
            target_page = getattr(self, 'page', None)
            if target_page:
                try:
                    target_page.open(ft.SnackBar(
                        ft.Text("El archivo físico ya no se encuentra en el disco." if lang == "es" else "The file no longer exists on disk.", color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_800,
                        duration=2500
                    ))
                except Exception:
                    pass
            return
            
        is_audio = f_type == "audio" or path.lower().endswith((".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus"))
        if is_audio and self.on_play_audio:
            self.on_play_audio(path, title=title)
        else:
            self.open_file(path)

    def create_grid_item(self, item):
        item_id, title, url, f_type, quality, date, size, path = item
        lang = config.get("language", "es")
        pal = get_current_palette()
        
        file_exists = path and os.path.exists(path)
        is_audio = f_type == "audio" or (path and path.lower().endswith((".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus")))
        
        # Check thumbnail
        thumb_path = None
        if path:
            candidate = os.path.splitext(path)[0] + ".jpg"
            if os.path.exists(candidate):
                thumb_path = candidate

        if thumb_path:
            cover_control = ft.Image(src=thumb_path, width=180, height=115, fit=ft.BoxFit.COVER, border_radius=10)
        else:
            cover_control = ft.Container(
                content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED if is_audio else ft.Icons.VIDEOCAM_ROUNDED, size=40, color=pal.light),
                width=180,
                height=115,
                border_radius=10,
                bgcolor=pal.tint_bg,
                alignment=ft.Alignment.CENTER
            )

        badge_bg = pal.primary if is_audio else ft.Colors.AMBER_400
        badge_text = "AUDIO" if is_audio else "VIDEO"
        pill = ft.Container(
            content=ft.Text(badge_text, size=8.5, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            bgcolor=badge_bg,
            padding=ft.Padding(5, 2, 5, 2),
            border_radius=4
        )

        cover_stack = ft.Stack([
            cover_control,
            ft.Container(content=pill, top=6, right=6)
        ])

        actions = ft.Row([
            ft.IconButton(
                icon=ft.Icons.PLAY_ARROW_ROUNDED if file_exists else ft.Icons.PLAY_DISABLED_ROUNDED,
                icon_color=ft.Colors.GREEN_400 if file_exists else ft.Colors.GREY_600,
                icon_size=19,
                tooltip="Reproducir en Nova Player" if (is_audio and file_exists) else ("Abrir archivo" if file_exists else "No encontrado"),
                disabled=not file_exists,
                on_click=lambda _, it=item: self.handle_play(it)
            ),
            ft.IconButton(
                icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                icon_color=pal.light,
                icon_size=17,
                tooltip="Abrir carpeta" if lang == "es" else "Open folder",
                on_click=lambda _, p=path: self.open_folder(p)
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                icon_color=ft.Colors.RED_400,
                icon_size=17,
                tooltip="Eliminar" if lang == "es" else "Delete",
                on_click=lambda _, i=item_id: self.delete_item(i)
            )
        ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        card = ft.Container(
            content=ft.Column([
                cover_stack,
                ft.Column([
                    ft.Text(title, size=11.5, weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.WHITE),
                    ft.Text(f"{date} • {size}" if size else f"{date}", size=9.5, color=ft.Colors.GREY_400, max_lines=1),
                ], spacing=2, expand=True),
                actions
            ], spacing=6),
            width=190,
            height=240,
            padding=10,
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE)),
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
            ink=True,
            ink_color=pal.tint_border,
            on_click=lambda _, it=item: self.handle_play(it) if file_exists else None
        )

        def _make_grid_hover(c):
            def _h(e):
                if e.data == "true":
                    c.bgcolor = pal.hover_bg
                    c.border = ft.Border.all(1, pal.hover_border)
                else:
                    c.bgcolor = ft.Colors.with_opacity(0.04, ft.Colors.WHITE)
                    c.border = ft.Border.all(1, ft.Colors.with_opacity(0.07, ft.Colors.WHITE))
                try:
                    c.update()
                except Exception:
                    pass
            return _h

        card.on_hover = _make_grid_hover(card)
        return card

    def create_list_item(self, item):
        # item: (id, title, url, file_type, quality, date, size, path)
        item_id, title, url, f_type, quality, date, size, path = item
        lang = config.get("language", "es")
        pal = get_current_palette()
        
        is_audio = f_type == "audio" or (path and path.lower().endswith((".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus")))
        icon_type = ft.Icons.MUSIC_NOTE_ROUNDED if is_audio else ft.Icons.PLAY_CIRCLE_FILL_ROUNDED
        icon_bg = pal.deep if is_audio else ft.Colors.BLUE_GREY_900
        badge_text = "AUDIO" if is_audio else "VIDEO"
        badge_color = pal.primary if is_audio else ft.Colors.AMBER_400

        file_exists = path and os.path.exists(path)

        item_cnt = ft.Container(
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
                                tooltip=("Reproducir en Nova Player" if (is_audio and file_exists) else ("Abrir archivo" if file_exists else "Archivo no encontrado")),
                                disabled=not file_exists,
                                on_click=lambda _, it=item: self.handle_play(it)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                icon_color=pal.light,
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
            ink_color=pal.tint_border,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            on_click=lambda _, it=item: self.handle_play(it) if file_exists else None
        )

        def _make_list_hover(cnt):
            def _h(e):
                if e.data == "true":
                    cnt.bgcolor = pal.hover_bg
                    cnt.border = ft.Border.all(1, pal.hover_border)
                else:
                    cnt.bgcolor = ft.Colors.with_opacity(0.04, ft.Colors.WHITE)
                    cnt.border = ft.Border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
                try:
                    cnt.update()
                except Exception:
                    pass
            return _h

        item_cnt.on_hover = _make_list_hover(item_cnt)
        return item_cnt

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
        lang = config.get("language", "es")
        target_page = getattr(self, 'page', None)
        if not target_page and e and hasattr(e, 'control') and e.control:
            target_page = e.control.page
        if not target_page and e and hasattr(e, 'page') and e.page:
            target_page = e.page

        if not target_page:
            db.clear_history()
            self.load_data(force_db=True)
            return

        def close_dialog(ev=None):
            if hasattr(target_page, "close"):
                try:
                    target_page.close(dlg)
                except Exception:
                    dlg.open = False
            else:
                dlg.open = False
            try:
                target_page.update()
            except Exception:
                pass

        def on_confirm(ev=None):
            close_dialog()
            db.clear_history()
            self.load_data(force_db=True)

        title_text = "Vaciar Historial" if lang == "es" else "Clear History"
        content_text = "¿Estás seguro de que deseas eliminar todo el historial de descargas? Los archivos en tu disco no serán borrados." if lang == "es" else "Are you sure you want to clear all download history? Downloaded files on disk will not be deleted."
        confirm_label = "Sí, vaciar" if lang == "es" else "Yes, clear"
        cancel_label = "Cancelar" if lang == "es" else "Cancel"

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400, size=24),
                ft.Text(title_text, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            content=ft.Text(content_text, size=13),
            actions=[
                ft.TextButton(cancel_label, on_click=close_dialog),
                ft.ElevatedButton(
                    confirm_label,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
                    on_click=on_confirm
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if hasattr(target_page, "open"):
            target_page.open(dlg)
        else:
            if dlg not in target_page.overlay:
                target_page.overlay.append(dlg)
            target_page.dialog = dlg
            dlg.open = True
            target_page.update()
