import customtkinter as ctk
from tkinter import filedialog
from core.config import config, save_config

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        self.center_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(self.center_frame, text="Configuración", font=ctk.CTkFont(size=28, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 30))
        
        # Directory setting
        dir_frame = ctk.CTkFrame(self.center_frame, fg_color=("gray85", "gray15"), corner_radius=8)
        dir_frame.grid(row=1, column=0, sticky="ew", pady=10)
        dir_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(dir_frame, text="Ruta de descarga predeterminada:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        input_frame = ctk.CTkFrame(dir_frame, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.dir_var = ctk.StringVar(value=config.get("download_dir", ""))
        dir_entry = ctk.CTkEntry(input_frame, textvariable=self.dir_var, state="readonly", height=40)
        dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        btn = ctk.CTkButton(input_frame, text="Cambiar", height=40, fg_color="transparent", border_width=1, border_color="gray", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=self.change_dir)
        btn.grid(row=0, column=1)

    def change_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.dir_var.get())
        if new_dir:
            self.dir_var.set(new_dir)
            config["download_dir"] = new_dir
            save_config(config)
