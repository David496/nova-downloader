from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QComboBox, QPushButton, QFileDialog)
from PySide6.QtCore import Qt, Signal
from core.config import config, save_config

class SettingsView(QWidget):
    settings_changed = Signal() # Emitted when theme/language changes

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("Configuración")
        title.setProperty("class", "Title")
        layout.addWidget(title)

        # Download Directory
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directorio de Descarga:")
        dir_label.setProperty("class", "SectionTitle")
        
        self.dir_value = QLabel(config.get("download_dir", ""))
        self.dir_value.setProperty("class", "Subtitle")
        
        dir_btn = QPushButton("Cambiar")
        dir_btn.setProperty("class", "SecondaryButton")
        dir_btn.clicked.connect(self.change_dir)
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_value)
        dir_layout.addStretch()
        dir_layout.addWidget(dir_btn)
        
        layout.addLayout(dir_layout)

        # Theme
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Tema:")
        theme_label.setProperty("class", "SectionTitle")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Oscuro", "dark")
        self.theme_combo.addItem("Claro", "light")
        
        # Set current
        index = self.theme_combo.findData(config.get("theme", "dark"))
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
            
        self.theme_combo.currentIndexChanged.connect(self.save_settings)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        # Language
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Idioma:")
        lang_label.setProperty("class", "SectionTitle")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("English", "en")
        
        # Set current
        index = self.lang_combo.findData(config.get("language", "es"))
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
            
        self.lang_combo.currentIndexChanged.connect(self.save_settings)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        layout.addStretch()

    def change_dir(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", config.get("download_dir"))
        if new_dir:
            config["download_dir"] = new_dir
            self.dir_value.setText(new_dir)
            self.save_settings()

    def save_settings(self):
        theme = self.theme_combo.currentData()
        lang = self.lang_combo.currentData()
        
        changed = False
        if config["theme"] != theme or config["language"] != lang:
            changed = True
            
        config["theme"] = theme
        config["language"] = lang
        save_config(config)
        
        if changed:
            self.settings_changed.emit()
