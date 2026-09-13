import flet as ft
from core.config import config

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

class ThemePalette:
    def __init__(
        self,
        id_name,
        name,
        icon,
        desc_es,
        desc_en,
        primary,
        light,
        dark,
        deep,
        hex_preview,
        glow_spread=1,
        glow_blur=28
    ):
        self.id = id_name
        self.name = name
        self.icon = icon
        self.desc_es = desc_es
        self.desc_en = desc_en
        
        # Color objects (ft.Colors or hex)
        self.primary = primary
        self.light = light
        self.dark = dark
        self.deep = deep
        self.hex_preview = hex_preview
        
        # Computed visual helpers for UI
        self.glow_shadow = ft.BoxShadow(
            spread_radius=glow_spread,
            blur_radius=glow_blur,
            color=ft.Colors.with_opacity(0.42, self.primary),
            offset=ft.Offset(0, 5)
        )
        self.tint_bg = ft.Colors.with_opacity(0.12, self.primary)
        self.tint_border = ft.Colors.with_opacity(0.25, self.primary)
        self.hover_bg = ft.Colors.with_opacity(0.08, self.primary)
        self.hover_border = ft.Colors.with_opacity(0.35, self.primary)
        self.active_bg = ft.Colors.with_opacity(0.18, self.primary)

THEMES = {
    "nebula_violet": ThemePalette(
        id_name="nebula_violet",
        name="Nebula Violet",
        icon="🔮",
        desc_es="Púrpura Eléctrico & Cyberpunk Original",
        desc_en="Electric Purple & Classic Cyberpunk",
        primary=ft.Colors.PURPLE_400,
        light=ft.Colors.PURPLE_300,
        dark=ft.Colors.PURPLE_600,
        deep=ft.Colors.PURPLE_900,
        hex_preview="#9D4EDD"
    ),
    "cyber_matrix": ThemePalette(
        id_name="cyber_matrix",
        name="Cyber Matrix",
        icon="⚡",
        desc_es="Verde Esmeralda Neón & Terminal Hacker",
        desc_en="Neon Emerald & Hacker Terminal",
        primary=ft.Colors.GREEN_ACCENT_400,
        light=ft.Colors.GREEN_300,
        dark=ft.Colors.GREEN_700,
        deep=ft.Colors.GREEN_900,
        hex_preview="#00FF88"
    ),
    "crimson_blood": ThemePalette(
        id_name="crimson_blood",
        name="Crimson Blood",
        icon="🩸",
        desc_es="Rojo Carmesí Rubí & Furia Escarlata",
        desc_en="Ruby Crimson & Scarlet Fury",
        primary=ft.Colors.RED_ACCENT_400,
        light=ft.Colors.RED_300,
        dark=ft.Colors.RED_700,
        deep=ft.Colors.RED_900,
        hex_preview="#FF1E56"
    ),
    "abyssal_blue": ThemePalette(
        id_name="abyssal_blue",
        name="Abyssal Blue",
        icon="🌊",
        desc_es="Azul Zafiro Cuántico & Océano Profundo",
        desc_en="Quantum Sapphire & Deep Ocean",
        primary=ft.Colors.BLUE_400,
        light=ft.Colors.BLUE_300,
        dark=ft.Colors.BLUE_700,
        deep=ft.Colors.BLUE_900,
        hex_preview="#0080FF"
    ),
    "cosmic_cyan": ThemePalette(
        id_name="cosmic_cyan",
        name="Cosmic Cyan",
        icon="🌌",
        desc_es="Cian Glacial & Turquesa Aurora",
        desc_en="Glacial Cyan & Aurora Synthwave",
        primary=ft.Colors.CYAN_ACCENT_400,
        light=ft.Colors.CYAN_300,
        dark=ft.Colors.CYAN_700,
        deep=ft.Colors.CYAN_900,
        hex_preview="#00F2FE"
    ),
    "golden_eclipse": ThemePalette(
        id_name="golden_eclipse",
        name="Golden Eclipse",
        icon="👑",
        desc_es="Ámbar Solar & Oro Cósmico de Lujo",
        desc_en="Solar Amber & Luxury Cosmic Gold",
        primary=ft.Colors.AMBER_400,
        light=ft.Colors.AMBER_300,
        dark=ft.Colors.AMBER_700,
        deep=ft.Colors.AMBER_900,
        hex_preview="#FFB703"
    ),
    "neon_sakura": ThemePalette(
        id_name="neon_sakura",
        name="Neon Sakura",
        icon="🌸",
        desc_es="Magenta Láser & Luces de Neo-Tokio",
        desc_en="Laser Magenta & Neo-Tokyo Lights",
        primary=ft.Colors.PINK_ACCENT_400,
        light=ft.Colors.PINK_300,
        dark=ft.Colors.PINK_700,
        deep=ft.Colors.PINK_900,
        hex_preview="#FF2E93"
    ),
}

def get_current_palette() -> ThemePalette:
    palette_key = config.get("theme_palette", "nebula_violet")
    return THEMES.get(palette_key, THEMES["nebula_violet"])

class AppColors:
    # Palette logic
    def __init__(self, is_dark=True):
        self.PALETTE = get_current_palette()
        self.PRIMARY = self.PALETTE.primary
        self.LIGHT = self.PALETTE.light
        self.DARK = self.PALETTE.dark
        self.DEEP = self.PALETTE.deep
        self.ACCENT = self.PALETTE.primary
        self.ACCENT_DARK = self.PALETTE.dark
        
        if is_dark:
            self.BG_MAIN = "#0F0F12"
            self.BG_SIDEBAR = "#16161D"
            self.BG_CARD = "#1C1C26"
            self.BORDER = "#2D2D3D"
            self.TEXT_PRIMARY = "#F8F8F2"
            self.TEXT_SECONDARY = "#9494B8"
        else:
            self.BG_MAIN = "#F8F9FA"
            self.BG_SIDEBAR = "#FFFFFF"
            self.BG_CARD = "#FFFFFF"
            self.BORDER = "#E9ECEF"
            self.TEXT_PRIMARY = "#212529"
            self.TEXT_SECONDARY = "#6C757D"

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
