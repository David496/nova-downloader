import flet as ft
from services.downloader import DownloadManager
from ui.flet_home import HomeView
from ui.flet_downloads import DownloadsView
from ui.flet_library import LibraryView
from ui.flet_settings import SettingsView
from ui.flet_player import PlayerView
from ui.flet_styles import get_theme, AppColors, AppEvents
from core.config import config
import asyncio
import os

async def main(page: ft.Page):
    def apply_settings():
        theme_mode = "dark"
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = get_theme("dark")
        
        colors = AppColors(True)
        page.bgcolor = colors.BG_MAIN
        rail.bgcolor = colors.BG_SIDEBAR
        content_container.bgcolor = colors.BG_MAIN
        
        lang = config.get("language", "es")
        labels = {
            "es": ["Inicio", "Reproductor", "Descargas", "Biblioteca", "Ajustes"],
            "en": ["Home", "Player", "Downloads", "Library", "Settings"]
        }
        for i, dest in enumerate(rail.destinations):
            if i < len(labels[lang]):
                dest.label = labels[lang][i]
            
        page.update()
        
        for view in views:
            if hasattr(view, "_build_ui"):
                view._build_ui()
                try:
                    view.update()
                except:
                    pass

    page.title = "Nova Downloader"
    
    icon_file = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    if not os.path.exists(icon_file):
        icon_file = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_file):
        page.window.icon = icon_file

    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_theme("dark")
    page.window_width = 1250
    page.window_height = 960
    page.window_min_width = 1050
    page.window_min_height = 750
    page.padding = 0
    
    colors_init = AppColors(True)
    page.bgcolor = colors_init.BG_MAIN

    # Views initialization
    downloads_view = DownloadsView()
    
    download_manager = DownloadManager(
        progress_cb=downloads_view.on_progress,
        finished_cb=downloads_view.on_finished,
        error_cb=downloads_view.on_error
    )
    
    # Start the download manager loop as a background task
    asyncio.create_task(download_manager.start())
    
    home_view = HomeView(download_manager, lambda: navigate(2))
    player_view = PlayerView(download_manager)
    library_view = LibraryView(on_play_audio=player_view.play_local_file)
    settings_view = SettingsView()
    
    views = [home_view, player_view, downloads_view, library_view, settings_view]

    content_container = ft.Container(
        content=views[0], 
        expand=True, 
        padding=ft.Padding(25, 15, 25, 15),
        bgcolor=colors_init.BG_MAIN,
        animate=ft.Animation(250, ft.AnimationCurve.DECELERATE)
    )

    # ---------------- Persistent Floating Bottom Mini-Player Bar Dock ----------------
    dock_thumb_img = ft.Image(src="", width=42, height=42, border_radius=8, fit=ft.BoxFit.COVER, visible=False)
    dock_thumb_icon = ft.Container(
        content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=20, color=ft.Colors.PURPLE_300),
        width=42,
        height=42,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_500),
        alignment=ft.Alignment.CENTER
    )
    dock_thumb_stack = ft.Stack([dock_thumb_icon, dock_thumb_img])
    dock_title = ft.Text("No hay reproducción activa", size=12, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, color=ft.Colors.WHITE)
    dock_artist = ft.Text("Toca para abrir reproductor", size=10, color=ft.Colors.PURPLE_200, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
    
    dock_info_col = ft.Container(
        content=ft.Row([
            dock_thumb_stack,
            ft.Column([dock_title, dock_artist], spacing=1, expand=True)
        ], spacing=10),
        width=260,
        ink=True,
        on_click=lambda _: navigate(1)
    )

    dock_prev_btn = ft.IconButton(
        icon=ft.Icons.SKIP_PREVIOUS_ROUNDED,
        icon_size=20,
        icon_color=ft.Colors.WHITE,
        tooltip="Anterior",
        on_click=lambda _: player_view.play_prev()
    )
    dock_play_btn = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        icon_size=22,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PURPLE_600,
        tooltip="Reproducir / Pausar",
        on_click=lambda _: player_view.toggle_play_pause()
    )
    dock_next_btn = ft.IconButton(
        icon=ft.Icons.SKIP_NEXT_ROUNDED,
        icon_size=20,
        icon_color=ft.Colors.WHITE,
        tooltip="Siguiente",
        on_click=lambda _: player_view.play_next()
    )

    dock_time_current = ft.Text("00:00", size=10, color=ft.Colors.GREY_400)
    dock_time_total = ft.Text("00:00", size=10, color=ft.Colors.GREY_400)
    dock_slider = ft.Slider(
        min=0.0,
        max=100.0,
        value=0.0,
        height=18,
        active_color=ft.Colors.PURPLE_300,
        inactive_color=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        expand=True
    )

    def on_dock_seek(e):
        if player_view.audio_player and player_view.audio_player.duration_sec > 0:
            target_sec = (dock_slider.value / 100.0) * player_view.audio_player.duration_sec
            player_view.audio_player.seek(target_sec)
    dock_slider.on_change = on_dock_seek

    dock_center = ft.Column([
        ft.Row([dock_prev_btn, dock_play_btn, dock_next_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        ft.Row([dock_time_current, dock_slider, dock_time_total], spacing=6, alignment=ft.MainAxisAlignment.CENTER)
    ], spacing=0, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    dock_vol_icon = ft.IconButton(
        icon=ft.Icons.VOLUME_UP_ROUNDED,
        icon_size=18,
        icon_color=ft.Colors.PURPLE_300
    )
    dock_vol_slider = ft.Slider(
        min=0.0,
        max=1.0,
        value=0.8,
        width=80,
        active_color=ft.Colors.PURPLE_300,
        inactive_color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE)
    )

    def on_dock_volume(e):
        if player_view.audio_player:
            player_view.audio_player.set_volume(dock_vol_slider.value)
        if hasattr(player_view, 'volume_slider'):
            player_view.volume_slider.value = dock_vol_slider.value
            try:
                player_view.volume_slider.update()
            except Exception:
                pass
    dock_vol_slider.on_change = on_dock_volume

    dock_expand_btn = ft.IconButton(
        icon=ft.Icons.OPEN_IN_FULL_ROUNDED,
        icon_size=18,
        icon_color=ft.Colors.PURPLE_300,
        tooltip="Abrir reproductor completo",
        on_click=lambda _: navigate(1)
    )
    dock_right = ft.Row([dock_vol_icon, dock_vol_slider, dock_expand_btn], spacing=2)

    bottom_dock = ft.Container(
        content=ft.Row([
            dock_info_col,
            dock_center,
            dock_right
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=14),
        height=72,
        padding=ft.Padding(18, 6, 18, 6),
        bgcolor=ft.Colors.with_opacity(0.92, colors_init.BG_SIDEBAR),
        border=ft.Border(top=ft.BorderSide(1, ft.Colors.with_opacity(0.12, ft.Colors.PURPLE_400))),
        visible=False,
        animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT)
    )

    def update_mini_player_state():
        if player_view.current_track:
            # Hide dock when user is already in the full Player tab (navigate(1)) to prevent duplicate controls
            bottom_dock.visible = (rail.selected_index != 1)
            dock_title.value = player_view.current_track.title
            dock_artist.value = player_view.current_track.artist
            if player_view.current_track.thumbnail:
                dock_thumb_img.src = player_view.current_track.thumbnail
                dock_thumb_img.visible = True
            else:
                dock_thumb_img.visible = False
            
            if player_view.audio_player.is_playing:
                dock_play_btn.icon = ft.Icons.PAUSE_ROUNDED
            else:
                dock_play_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED
                
            dock_time_total.value = player_view._format_seconds(player_view.current_track.duration)
        else:
            bottom_dock.visible = False

        try:
            bottom_dock.update()
        except Exception:
            pass

    def update_mini_player_position(pos_sec, dur_sec):
        if not bottom_dock.visible:
            return
        if dur_sec > 0:
            dock_slider.value = min(100.0, max(0.0, (pos_sec / dur_sec) * 100.0))
            dock_time_total.value = player_view._format_seconds(dur_sec)
        dock_time_current.value = player_view._format_seconds(pos_sec)
        try:
            dock_slider.update()
            dock_time_current.update()
            dock_time_total.update()
        except Exception:
            pass

    player_view.add_state_listener(update_mini_player_state)
    player_view.add_position_listener(update_mini_player_position)

    def navigate(index):
        rail.selected_index = index
        content_container.content = views[index]
        if index == 1: # Player
            player_view.on_global_refresh()
        elif index == 3: # Library
            library_view.load_data()
        update_mini_player_state()
        page.update()

    # Visually Enhanced Modern Glassmorphic Sidebar
    rail = ft.NavigationRail(
        selected_index=0,
        extended=True,
        min_width=90,
        min_extended_width=210,
        group_alignment=-0.95,
        bgcolor=colors_init.BG_SIDEBAR,
        indicator_color=ft.Colors.with_opacity(0.18, ft.Colors.PURPLE_500),
        indicator_shape=ft.RoundedRectangleBorder(radius=14),
        selected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12.5),
        unselected_label_text_style=ft.TextStyle(color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500, size=12.5),
        leading=ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.DOWNLOAD_FOR_OFFLINE_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                    padding=8,
                    bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PURPLE_500),
                    border_radius=12,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.25, ft.Colors.PURPLE_400))
                ),
                ft.Column([
                    ft.Text("NOVA", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text("DOWNLOADER", size=9, weight=ft.FontWeight.W_600, color=ft.Colors.PURPLE_300)
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            padding=ft.Padding(12, 18, 12, 18),
            margin=ft.Margin(0, 0, 0, 10)
        ),
        trailing=ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CODE_ROUNDED, size=13, color=ft.Colors.PURPLE_300),
                        ft.Text("Desarrollado por", size=10, color=ft.Colors.GREY_400)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    ft.Text("David496", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_300)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.Padding(12, 8, 12, 8),
                bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                border_radius=14,
                border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE))
            ),
            padding=ft.Padding(12, 0, 12, 20)
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.HOME_OUTLINED, color=ft.Colors.GREY_400, size=20),
                selected_icon=ft.Icon(ft.Icons.HOME_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                label="Inicio"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.RADIO_OUTLINED, color=ft.Colors.GREY_400, size=20),
                selected_icon=ft.Icon(ft.Icons.RADIO_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                label="Reproductor"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ft.Colors.GREY_400, size=20),
                selected_icon=ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                label="Descargas"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.VIDEO_LIBRARY_OUTLINED, color=ft.Colors.GREY_400, size=20),
                selected_icon=ft.Icon(ft.Icons.VIDEO_LIBRARY_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                label="Biblioteca"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color=ft.Colors.GREY_400, size=20),
                selected_icon=ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=ft.Colors.PURPLE_300, size=22),
                label="Ajustes"
            ),
        ],
        on_change=lambda e: navigate(e.control.selected_index),
    )

    main_column = ft.Column(
        [
            content_container,
            bottom_dock
        ],
        expand=True,
        spacing=0
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
                main_column,
            ],
            expand=True,
            spacing=0
        )
    )
    
    def on_window_event(e):
        if e.data in ["close", "window_close"]:
            try:
                if hasattr(player_view, "audio_player") and player_view.audio_player:
                    player_view.audio_player.stop()
            except Exception:
                pass
            os._exit(0)

    page.window.on_event = on_window_event

    AppEvents.subscribe(apply_settings)
    apply_settings()

if __name__ == "__main__":
    import sys
    ft.run(main)
