import sys
import customtkinter as ctk

from ui.main_window_tk import MainWindow
from ui.home_view_tk import HomeView
from ui.downloads_view_tk import DownloadsView
from ui.library_view_tk import LibraryView
from ui.settings_view_tk import SettingsView
from services.downloader import DownloadManager

def main():
    app = MainWindow()
    
    downloads_view = DownloadsView(app.content_area)
    
    # Initialize download manager
    download_manager = DownloadManager(
        progress_cb=downloads_view.on_progress,
        finished_cb=downloads_view.on_finished,
        error_cb=downloads_view.on_error
    )
    
    home_view = HomeView(app.content_area, download_manager, lambda: app.show_view("downloads"))
    library_view = LibraryView(app.content_area)
    settings_view = SettingsView(app.content_area)
    
    app.views["home"] = home_view
    app.views["downloads"] = downloads_view
    app.views["library"] = library_view
    app.views["settings"] = settings_view
    
    app.show_view("home")
    
    # Handle closing properly
    def on_closing():
        download_manager.stop()
        app.destroy()
        sys.exit(0)
        
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()