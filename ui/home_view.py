from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLineEdit, QPushButton, QLabel, QFrame, QScrollArea, QFileDialog, QCheckBox)
from PySide6.QtCore import Qt, Signal
from services.downloader import InfoExtractor
from core.config import config
import os

class FormatCard(QFrame):
    clicked = Signal(str, str, dict) # type, label, options

    def __init__(self, f_type, label, desc, options):
        super().__init__()
        self.setProperty("class", "FormatCard")
        self.setProperty("selected", "false")
        self.setCursor(Qt.PointingHandCursor)
        self.f_type = f_type
        self.label_text = label
        self.options = options
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel(label)
        title.setProperty("class", "FormatTitle")
        
        description = QLabel(desc)
        description.setProperty("class", "FormatDesc")
        
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.f_type, self.label_text, self.options)
        super().mousePressEvent(event)
        
    def set_selected(self, is_selected):
        self.setProperty("selected", "true" if is_selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

class HomeView(QWidget):
    analyze_requested = Signal(dict)
    download_requested = Signal(str, dict, str)

    def __init__(self):
        super().__init__()
        self.lang = config.get("language", "es")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.scroll_widget = QWidget()
        self.layout = QVBoxLayout(self.scroll_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        
        scroll.setWidget(self.scroll_widget)
        self.main_layout.addWidget(scroll)

        # Title
        t_desc = "Descarga contenido en segundos" if self.lang == "es" else "Download content in seconds"
        title = QLabel(t_desc)
        title.setProperty("class", "Title")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Input Area
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega un enlace de YouTube aquí..." if self.lang == "es" else "Paste a YouTube link here...")
        self.url_input.setMinimumHeight(45)
        
        self.analyze_btn = QPushButton("Analizar" if self.lang == "es" else "Analyze")
        self.analyze_btn.setProperty("class", "PrimaryButton")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.on_analyze)
        
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.analyze_btn)
        
        self.layout.addLayout(input_layout)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setProperty("class", "Subtitle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # --- Results Area ---
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0,0,0,0)
        self.results_widget.setVisible(False)
        
        self.info_title = QLabel("Título del Video")
        self.info_title.setProperty("class", "Title")
        self.info_title.setWordWrap(True)
        self.results_layout.addWidget(self.info_title)
        
        self.playlist_checkbox = QCheckBox("Descargar Playlist Completa" if self.lang == "es" else "Download Entire Playlist")
        self.playlist_checkbox.setVisible(False)
        self.results_layout.addWidget(self.playlist_checkbox)
        
        # Video Section
        video_title = QLabel("Calidad de Video (MP4)" if self.lang == "es" else "Video Quality (MP4)")
        video_title.setProperty("class", "SectionTitle")
        self.results_layout.addWidget(video_title)
        
        self.video_grid = QGridLayout()
        self.results_layout.addLayout(self.video_grid)
        
        # Audio Section
        audio_title = QLabel("Calidad de Audio" if self.lang == "es" else "Audio Quality")
        audio_title.setProperty("class", "SectionTitle")
        self.results_layout.addWidget(audio_title)
        
        self.audio_grid = QGridLayout()
        self.results_layout.addLayout(self.audio_grid)
        
        # Download Controls
        dl_layout = QHBoxLayout()
        self.selected_format_label = QLabel("Selecciona un formato arriba" if self.lang == "es" else "Select a format above")
        self.selected_format_label.setProperty("class", "Subtitle")
        
        self.dl_btn = QPushButton("Iniciar Descarga" if self.lang == "es" else "Start Download")
        self.dl_btn.setProperty("class", "PrimaryButton")
        self.dl_btn.setEnabled(False)
        self.dl_btn.clicked.connect(self.on_download)
        
        dl_layout.addWidget(self.selected_format_label)
        dl_layout.addStretch()
        dl_layout.addWidget(self.dl_btn)
        
        self.results_layout.addSpacing(20)
        self.results_layout.addLayout(dl_layout)
        
        self.layout.addWidget(self.results_widget)
        self.layout.addStretch()
        
        self.current_info = None
        self.selected_options = None
        self.cards = []

    def on_analyze(self):
        url = self.url_input.text().strip()
        if not url:
            return
            
        self.status_label.setText("Analizando enlace..." if self.lang == "es" else "Analyzing link...")
        self.analyze_btn.setEnabled(False)
        self.results_widget.setVisible(False)
        self.selected_options = None
        self.dl_btn.setEnabled(False)
        self.selected_format_label.setText("Selecciona un formato arriba" if self.lang == "es" else "Select a format above")
        self.playlist_checkbox.setVisible(False)
        
        self.extractor = InfoExtractor(url)
        self.extractor.finished.connect(self.on_analyze_finished)
        self.extractor.error.connect(self.on_analyze_error)
        self.extractor.start()

    def create_cards(self):
        for i in reversed(range(self.video_grid.count())): 
            self.video_grid.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.audio_grid.count())): 
            self.audio_grid.itemAt(i).widget().setParent(None)
        self.cards.clear()

        video_qualities = [
            ("4K (2160p)", "Alta calidad" if self.lang == "es" else "High quality", {'format': 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'}),
            ("2K (1440p)", "Excelente" if self.lang == "es" else "Excellent", {'format': 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'}),
            ("HD (1080p)", "Buena calidad" if self.lang == "es" else "Good quality", {'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'}),
            ("HD (720p)", "Estándar" if self.lang == "es" else "Standard", {'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'}),
            ("SD (360p)", "Ahorro" if self.lang == "es" else "Data saver", {'format': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'merge_output_format': 'mp4'}),
        ]
        
        audio_qualities = [
            ("MP3 320kbps", "Alta calidad" if self.lang == "es" else "High quality", {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]}),
            ("MP3 192kbps", "Estándar" if self.lang == "es" else "Standard", {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}),
            ("WAV", "Sin pérdida" if self.lang == "es" else "Lossless", {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}]}),
            ("FLAC", "Sin pérdida" if self.lang == "es" else "Lossless", {'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'flac'}]}),
        ]

        for i, (label, desc, opts) in enumerate(video_qualities):
            card = FormatCard("video", label, desc, opts)
            card.clicked.connect(self.on_format_selected)
            self.video_grid.addWidget(card, i // 3, i % 3)
            self.cards.append(card)
            
        for i, (label, desc, opts) in enumerate(audio_qualities):
            card = FormatCard("audio", label, desc, opts)
            card.clicked.connect(self.on_format_selected)
            self.audio_grid.addWidget(card, i // 3, i % 3)
            self.cards.append(card)

    def on_format_selected(self, f_type, label, options):
        self.selected_options = options
        self.dl_btn.setEnabled(True)
        t_sel = "Formato seleccionado: " if self.lang == "es" else "Selected format: "
        self.selected_format_label.setText(f"{t_sel}{label}")
        
        for card in self.cards:
            if card == self.sender():
                card.set_selected(True)
            else:
                card.set_selected(False)

    def on_analyze_finished(self, info):
        self.current_info = info
        self.status_label.setText("")
        self.analyze_btn.setEnabled(True)
        
        title = info.get('title', 'Unknown Title')
        if info.get('_type') == 'playlist':
            entries = info.get('entries', [])
            count = len(entries)
            title = f"Playlist: {title} ({count} videos)"
            self.playlist_checkbox.setVisible(True)
            self.playlist_checkbox.setChecked(True)
            
        self.info_title.setText(title)
        self.create_cards()
        self.results_widget.setVisible(True)
        self.analyze_requested.emit(info)
        
    def on_analyze_error(self, err):
        self.status_label.setText(f"Error: {err}")
        self.analyze_btn.setEnabled(True)

    def on_download(self):
        if not self.current_info or not self.selected_options:
            return
            
        output_dir = config.get("download_dir", os.path.expanduser("~/Downloads"))
        url = self.url_input.text()
        title = self.current_info.get('title', 'Video')
        
        options = dict(self.selected_options)
        
        is_playlist = self.current_info.get('_type') == 'playlist' and self.playlist_checkbox.isChecked()
        
        if is_playlist:
            # Create a subfolder for the playlist
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' -_']).rstrip()
            output_dir = os.path.join(output_dir, safe_title)
            options['outtmpl'] = os.path.join(output_dir, '%(playlist_index)s - %(title)s.%(ext)s')
            options['yesplaylist'] = True
        else:
            options['outtmpl'] = os.path.join(output_dir, '%(title)s.%(ext)s')
            options['noplaylist'] = True
            
        self.download_requested.emit(url, options, title)
        
        self.status_label.setText("¡Descarga iniciada! Revisa la pestaña de descargas." if self.lang == "es" else "Download started! Check the downloads tab.")
