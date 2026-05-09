from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton)
from PySide6.QtCore import Qt
from database.db import get_history
from core.config import config
import os

class LibraryView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_text = "Biblioteca" if config.get("language") == "es" else "Library"
        title = QLabel(title_text)
        title.setProperty("class", "Title")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        
        headers = ["Título", "Tipo", "Fecha", "Acción"] if config.get("language") == "es" else ["Title", "Type", "Date", "Action"]
        self.table.setHorizontalHeaderLabels(headers)
        
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        rows = get_history()
        btn_text = "Abrir Carpeta" if config.get("language") == "es" else "Open Folder"
        
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            # id, title, url, file_type, quality, date, size, path
            self.table.setItem(i, 0, QTableWidgetItem(str(row[1])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[3])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row[5])))
            
            # Action button
            btn = QPushButton(btn_text)
            btn.setProperty("class", "SecondaryButton")
            btn.setCursor(Qt.PointingHandCursor)
            
            # Use a lambda with default argument to capture the current path
            path = row[7]
            btn.clicked.connect(lambda checked=False, p=path: self.open_folder(p))
            
            self.table.setCellWidget(i, 3, btn)
            # Make the row a bit taller to fit the button nicely
            self.table.setRowHeight(i, 45)

    def open_folder(self, path):
        if path and os.path.exists(path):
            os.startfile(os.path.dirname(path))
        elif path and os.path.exists(os.path.dirname(path)):
            os.startfile(os.path.dirname(path))