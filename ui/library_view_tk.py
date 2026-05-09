import customtkinter as ctk
import os
from database.db import get_history, clear_history
from ui.components import Badge, show_toast

class LibraryRow(ctk.CTkFrame):
    def __init__(self, parent, item_id, title, ftype, date, path):
        super().__init__(parent, fg_color=("gray90", "gray12"), corner_radius=10)
        self.path = path
        
        self.grid_columnconfigure(0, weight=1)
        
        # Left side: Title and Type
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)
        
        title_lbl = ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"))
        title_lbl.pack(anchor="w")
        
        badges_date_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        badges_date_frame.pack(anchor="w", pady=(5,0))
        
        b_color = "#FF0000" if ftype.lower() == "video" else "#555555"
        Badge(badges_date_frame, text=ftype.upper(), color=b_color).pack(side="left")
        
        ctk.CTkLabel(badges_date_frame, text=f" • {date}", text_color="gray", font=ctk.CTkFont(family="Segoe UI", size=12)).pack(side="left", padx=(5,0))
        
        # Right side: Action Button
        btn = ctk.CTkButton(self, text="📁 Abrir carpeta", width=120, height=35, fg_color="transparent", 
                            border_width=1, border_color="#FF0000", text_color="#FF0000", 
                            hover_color=("#FFCCCC", "#330000"),
                            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"),
                            command=self.open_folder)
        btn.grid(row=0, column=1, padx=20, pady=15)

    def open_folder(self):
        if self.path and os.path.exists(self.path):
            os.startfile(os.path.dirname(self.path))
        elif self.path and os.path.exists(os.path.dirname(self.path)):
            os.startfile(os.path.dirname(self.path))


class LibraryView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        title = ctk.CTkLabel(header_frame, text="Biblioteca de Descargas", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"))
        title.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(header_frame, text="🗑️ Limpiar", width=100, fg_color="transparent", 
                                       border_width=1, border_color="gray", text_color=("gray10", "gray90"), 
                                       hover_color=("gray70", "gray30"), command=self.clear_history)
        self.clear_btn.pack(side="right")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 40))

    def clear_history(self):
        clear_history()
        self.on_show()
        show_toast(self.winfo_toplevel(), "🗑️ Historial limpiado", duration=2000)

    def on_show(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        rows = get_history()
        if not rows:
            ctk.CTkLabel(self.scroll_frame, text="Aún no hay descargas.", text_color="gray").pack(pady=50)
            return
            
        for row in rows:
            # id(0), title(1), url(2), file_type(3), quality(4), date(5), size(6), path(7)
            item = LibraryRow(self.scroll_frame, row[0], row[1], row[3], row[5], row[7])
            item.pack(fill="x", padx=10, pady=5)