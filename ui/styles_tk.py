import tkinter as tk
from tkinter import ttk

# YouTube Dark Mode Inspired Theme
YT_THEME = {
    "bg_main": "#0F0F0F",
    "bg_surface": "#212121",
    "bg_hover": "#3D3D3D",
    "text_primary": "#F1F1F1",
    "text_secondary": "#AAAAAA",
    "accent": "#FF0000",        # YouTube Red
    "accent_hover": "#CC0000",
    "border": "#3D3D3D",
    "error": "#FF4E4E",
    "font_main": ("Segoe UI", 11),
    "font_title": ("Segoe UI", 20, "bold"),
    "font_subtitle": ("Segoe UI", 13),
}

def setup_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    
    bg = YT_THEME["bg_main"]
    surface = YT_THEME["bg_surface"]
    fg = YT_THEME["text_primary"]
    fg_sec = YT_THEME["text_secondary"]
    accent = YT_THEME["accent"]
    border = YT_THEME["border"]
    
    style.configure(".", background=bg, foreground=fg, font=YT_THEME["font_main"])
    style.configure("TFrame", background=bg)
    style.configure("Surface.TFrame", background=surface)
    
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("Surface.TLabel", background=surface, foreground=fg)
    
    style.configure("Title.TLabel", font=YT_THEME["font_title"], foreground=fg)
    style.configure("Subtitle.TLabel", font=YT_THEME["font_subtitle"], foreground=fg_sec)
    style.configure("Error.TLabel", foreground=YT_THEME["error"])
    
    # Primary Button (Red)
    style.configure("Primary.TButton", background=accent, foreground="#FFFFFF", bordercolor=accent, 
                    lightcolor=accent, darkcolor=accent, borderwidth=0, font=("Segoe UI", 11, "bold"))
    style.map("Primary.TButton", 
              background=[("active", YT_THEME["accent_hover"]), ("disabled", surface)],
              foreground=[("disabled", fg_sec)])
              
    # Secondary Button
    style.configure("Secondary.TButton", background=surface, foreground=fg, bordercolor=border, 
                    lightcolor=surface, darkcolor=surface, borderwidth=1)
    style.map("Secondary.TButton", 
              background=[("active", YT_THEME["bg_hover"])])
    
    # Sidebar Button
    style.configure("Sidebar.TButton", background=surface, foreground=fg, borderwidth=0, anchor="w", padding=(15, 10))
    style.map("Sidebar.TButton", background=[("active", YT_THEME["bg_hover"])])
    
    # Entries
    style.configure("TEntry", fieldbackground=surface, foreground=fg, bordercolor=border, 
                    lightcolor=surface, darkcolor=surface, padding=5)
    
    # Progressbar
    style.configure("Horizontal.TProgressbar", background=accent, troughcolor=surface, bordercolor=border)

    # Treeview
    style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg, 
                    rowheight=35, bordercolor=border, borderwidth=0)
    style.configure("Treeview.Heading", background=surface, foreground=fg_sec, 
                    font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
    style.map("Treeview", background=[('selected', surface)], foreground=[('selected', fg)])
    style.map("Treeview.Heading", background=[('active', YT_THEME["bg_hover"])])
    
    # Checkbutton and Radiobutton
    style.configure("TCheckbutton", background=bg, foreground=fg)
    style.map("TCheckbutton", background=[("active", bg)])
    
    style.configure("TRadiobutton", background=bg, foreground=fg)
    style.map("TRadiobutton", background=[("active", bg)])