import customtkinter as ctk

class Badge(ctk.CTkFrame):
    """A small pill-shaped badge for displaying tags like [4K] or [MP3]"""
    def __init__(self, parent, text, color="#FF0000", text_color="#FFFFFF", **kwargs):
        super().__init__(parent, fg_color=color, corner_radius=10, **kwargs)
        self.label = ctk.CTkLabel(self, text=text, text_color=text_color, font=ctk.CTkFont(size=10, weight="bold"))
        self.label.pack(padx=8, pady=2)


class ToastNotification(ctk.CTkFrame):
    """A toast notification that slides up from the bottom and fades/disappears"""
    def __init__(self, parent, message, duration=3000, **kwargs):
        super().__init__(parent, fg_color="#1a1a1a", border_width=1, border_color="#FF0000", corner_radius=12, **kwargs)
        self.parent = parent
        self.duration = duration
        
        self.lbl = ctk.CTkLabel(self, text=message, text_color="white", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
        self.lbl.pack(padx=25, pady=12)
        
        # Force parent update to get correct dimensions
        self.parent.update_idletasks()
        
        # Center horizontally relative to parent
        self.target_y = parent.winfo_height() - 80
        self.current_y = parent.winfo_height() + 100
        
        # Use relx to center it, and anchor="center" to keep it balanced
        self.place(relx=0.5, y=self.current_y, anchor="center")
        self.animate_in()

    def animate_in(self):
        if self.current_y > self.target_y:
            self.current_y -= 8
            self.place(relx=0.5, y=self.current_y, anchor="center")
            self.after(10, self.animate_in)
        else:
            self.after(self.duration, self.animate_out)

    def animate_out(self):
        if self.current_y < self.parent.winfo_height() + 100:
            self.current_y += 8
            self.place(relx=0.5, y=self.current_y, anchor="center")
            self.after(10, self.animate_out)
        else:
            self.destroy()

def show_toast(parent, message, duration=3000):
    # Only show if window is initialized
    if parent.winfo_width() > 1:
        ToastNotification(parent, message, duration)


class LoadingSpinner(ctk.CTkFrame):
    """A pulsing progress bar to indicate loading state"""
    def __init__(self, parent, text="Cargando...", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.label = ctk.CTkLabel(self, text=text, text_color="gray", font=ctk.CTkFont(size=12))
        self.label.pack(side="left", padx=(0, 10))
        
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=100, height=4, progress_color="#FF0000")
        self.progress.pack(side="left")
        self.progress.start()
        
    def stop(self):
        self.progress.stop()
        self.destroy()
