from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QFrame, QLabel, QSizePolicy)
from PySide6.QtCore import Qt
from ui.styles import get_stylesheet
from core.config import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nova Downloader")
        self.resize(1000, 700)
        self.apply_theme()

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(5)

        # Logo/Title
        logo_label = QLabel("NOVA")
        logo_label.setProperty("class", "Title")
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addSpacing(30)

        # Navigation Buttons
        self.nav_buttons = []
        
        btn_home = QPushButton("🏠 Inicio" if config["language"] == "es" else "🏠 Home")
        btn_home.setCheckable(True)
        btn_home.setChecked(True)
        
        btn_downloads = QPushButton("⬇️ Descargas" if config["language"] == "es" else "⬇️ Downloads")
        btn_downloads.setCheckable(True)
        
        btn_library = QPushButton("📚 Biblioteca" if config["language"] == "es" else "📚 Library")
        btn_library.setCheckable(True)
        
        btn_settings = QPushButton("⚙️ Configuración" if config["language"] == "es" else "⚙️ Settings")
        btn_settings.setCheckable(True)

        for btn in [btn_home, btn_downloads, btn_library, btn_settings]:
            btn.setProperty("class", "SidebarButton")
            btn.setCursor(Qt.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            btn.clicked.connect(self.on_nav_clicked)

        sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # Content Area (Stacked Widget)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        from ui.home_view import HomeView
        from ui.downloads_view import DownloadsView
        from ui.library_view import LibraryView
        from ui.settings_view import SettingsView
        
        self.home_view = HomeView()
        self.downloads_view = DownloadsView()
        self.library_view = LibraryView()
        self.settings_view = SettingsView()
        
        self.stacked_widget.addWidget(self.home_view)
        self.stacked_widget.addWidget(self.downloads_view)
        self.stacked_widget.addWidget(self.library_view)
        self.stacked_widget.addWidget(self.settings_view)

        # Signals
        self.home_view.analyze_requested.connect(self.on_analyze_requested)
        self.home_view.download_requested.connect(self.start_download)
        self.settings_view.settings_changed.connect(self.on_settings_changed)

    def apply_theme(self):
        theme = config.get("theme", "dark")
        self.setStyleSheet(get_stylesheet(theme))

    def on_settings_changed(self):
        self.apply_theme()
        # To truly change language on the fly, we'd need to retranslate texts.
        # For simplicity, we just apply theme, and texts will apply on next restart.

    def on_nav_clicked(self):
        sender = self.sender()
        for i, btn in enumerate(self.nav_buttons):
            if btn == sender:
                btn.setChecked(True)
                self.stacked_widget.setCurrentIndex(i)
                if i == 2: # Library view
                    self.library_view.load_data()
            else:
                btn.setChecked(False)

    def on_analyze_requested(self, info):
        pass
        
    def start_download(self, url, options, title):
        self.downloads_view.add_download(url, options, title)
        self.nav_buttons[1].click()