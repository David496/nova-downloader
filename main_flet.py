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
    page.window_height = 820
    page.window_min_width = 1050
    page.window_min_height = 680
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
    library_view = LibraryView()
    settings_view = SettingsView()
    
    views = [home_view, player_view, downloads_view, library_view, settings_view]

    content_container = ft.Container(
        content=views[0], 
        expand=True, 
        padding=ft.Padding(25, 15, 25, 15),
        bgcolor=colors_init.BG_MAIN,
        animate=ft.Animation(250, ft.AnimationCurve.DECELERATE)
    )

    def navigate(index):
        rail.selected_index = index
        content_container.content = views[index]
        if index == 3: # Library
            library_view.load_data()
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

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)),
                content_container,
            ],
            expand=True,
            spacing=0
        )
    )
    
    AppEvents.subscribe(apply_settings)
    apply_settings()

if __name__ == "__main__":
    ft.run(main)
