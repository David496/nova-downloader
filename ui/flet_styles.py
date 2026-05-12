import flet as ft

class AppEvents:
    """Global event bus for UI updates."""
    _callbacks = []

    @classmethod
    def subscribe(cls, callback):
        if callback not in cls._callbacks:
            cls._callbacks.append(callback)

    @classmethod
    def notify(cls):
        for callback in cls._callbacks:
            try:
                callback()
            except:
                pass

class AppColors:
    # Palette logic
    def __init__(self, is_dark=True):
        if is_dark:
            self.BG_MAIN = "#0F0F12"
            self.BG_SIDEBAR = "#16161D"
            self.BG_CARD = "#1C1C26"
            self.BORDER = "#2D2D3D"
            self.TEXT_PRIMARY = "#F8F8F2"
            self.TEXT_SECONDARY = "#9494B8"
            self.ACCENT = "#9D4EDD" # Electric Purple
            self.ACCENT_DARK = "#7B2CBF"
        else:
            self.BG_MAIN = "#F8F9FA"
            self.BG_SIDEBAR = "#FFFFFF"
            self.BG_CARD = "#FFFFFF"
            self.BORDER = "#E9ECEF"
            self.TEXT_PRIMARY = "#212529"
            self.TEXT_SECONDARY = "#6C757D"
            self.ACCENT = "#7B2CBF"
            self.ACCENT_DARK = "#5A189A"

def get_theme(theme_mode="dark"):
    is_dark = theme_mode == "dark"
    colors = AppColors(is_dark)
    
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=colors.ACCENT,
            on_primary=ft.Colors.WHITE,
            secondary=colors.ACCENT_DARK,
            surface=colors.BG_SIDEBAR,
            on_surface=colors.TEXT_PRIMARY,
            outline=colors.BORDER,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
