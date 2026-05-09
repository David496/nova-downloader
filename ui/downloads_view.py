from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QProgressBar, QPushButton)
from PySide6.QtCore import Qt
from services.downloader import DownloadWorker
from database.db import add_download
from datetime import datetime
import os

class DownloadItem(QFrame):
    def __init__(self, url, options, title):
        super().__init__()
        self.setProperty("class", "Card")
        self.setFixedHeight(100)
        
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")
        self.status_label = QLabel("Iniciando...")
        self.status_label.setProperty("class", "Subtitle")
        self.status_label.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)
        
        # Worker
        output_path = os.path.dirname(options.get('outtmpl', '~/Downloads'))
        self.worker = DownloadWorker(url, options, output_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
        self.file_type = "Audio" if 'postprocessors' in options else "Video"
        self.url = url
        self.final_path = ""

    def update_progress(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                downloaded = d.get('downloaded_bytes', 0)
                percent = int(downloaded / total * 100)
                self.progress_bar.setValue(percent)
                speed = d.get('speed')
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.2f} MB/s"
                    self.status_label.setText(f"Descargando... {speed_str}")
        elif d['status'] == 'converting':
            self.status_label.setText("Convirtiendo (ffmpeg)...")
            self.progress_bar.setValue(0) # Indeterminate for conversion in ui could be better, but this works

    def on_finished(self, result):
        self.progress_bar.setValue(100)
        self.status_label.setText("Completado")
        self.status_label.setStyleSheet("color: #1DB954;")
        self.final_path = result.get('path', '')
        # Save to DB
        add_download(self.title_label.text(), self.url, self.file_type, "N/A", "N/A", self.final_path)

    def on_error(self, err):
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("color: #E22134;")

class DownloadsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Descargas Activas")
        title.setProperty("class", "Title")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.scroll_widget)
        layout.addWidget(scroll)

    def add_download(self, url, options, title):
        item = DownloadItem(url, options, title)
        self.scroll_layout.addWidget(item)
