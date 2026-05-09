import customtkinter as ctk
import os

ctk.set_appearance_mode("dark")
# We will use custom red colors directly on widgets instead of a non-existent global 'red' theme.

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nova Downloader")
        self.geometry("1100x750")
        
        # Configure layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) # spacer
        
        # Content Area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)
        
        self.views = {}
        self.current_view = None
        self.setup_sidebar()

    def setup_sidebar(self):
        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar, text="▶ NOVA", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FF0000")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))
        
        # Buttons
        self.btn_home = ctk.CTkButton(self.sidebar, text="Inicio", fg_color="transparent", text_color=("gray10", "gray90"), 
                                      hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.show_view("home"))
        self.btn_home.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_downloads = ctk.CTkButton(self.sidebar, text="Descargas", fg_color="transparent", text_color=("gray10", "gray90"), 
                                           hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.show_view("downloads"))
        self.btn_downloads.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_library = ctk.CTkButton(self.sidebar, text="Biblioteca", fg_color="transparent", text_color=("gray10", "gray90"), 
                                         hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.show_view("library"))
        self.btn_library.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙️  Configuración", fg_color="transparent", text_color=("gray10", "gray90"), 
                                          hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.show_view("settings"))
        self.btn_settings.grid(row=6, column=0, padx=10, pady=(5, 20), sticky="ew")

    def register_view(self, name, view_class, **kwargs):
        view = view_class(self.content_area, **kwargs)
        self.views[name] = view
        # We don't grid them immediately to prevent overlapping issues and lag

    def show_view(self, name):
        if self.current_view:
            self.views[self.current_view].grid_forget()
        
        self.views[name].grid(row=0, column=0, sticky="nsew")
        self.current_view = name
        
        if hasattr(self.views[name], 'on_show'):
            self.views[name].on_show()
            
        # Update button colors
        for btn_name, btn in [("home", self.btn_home), ("downloads", self.btn_downloads), 
                              ("library", self.btn_library), ("settings", self.btn_settings)]:
            if btn_name == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
