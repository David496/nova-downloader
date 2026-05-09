def get_stylesheet(theme="dark"):
    # Base configuration
    if theme == "dark":
        bg_main = "#0E0E10"
        bg_sidebar = "#18181B"
        border = "#27272A"
        text_primary = "#FFFFFF"
        text_secondary = "#A1A1AA"
        input_bg = "#18181B"
        btn_hover = "#27272A"
        card_bg = "#18181B"
        card_hover = "#27272A"
        card_selected = "#2D1B69"
        accent = "#8B5CF6"
        accent_hover = "#7C3AED"
        accent_pressed = "#6D28D9"
    else: # Light theme
        bg_main = "#F4F4F5"
        bg_sidebar = "#FFFFFF"
        border = "#E4E4E7"
        text_primary = "#18181B"
        text_secondary = "#52525B"
        input_bg = "#FFFFFF"
        btn_hover = "#E4E4E7"
        card_bg = "#FFFFFF"
        card_hover = "#F4F4F5"
        card_selected = "#EBE5FA"
        accent = "#7C3AED"
        accent_hover = "#6D28D9"
        accent_pressed = "#5B21B6"

    return f"""
    /* Global Styles */
    QWidget {{
        background-color: {bg_main};
        color: {text_primary};
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 13px; /* More compact font size */
    }}

    /* Sidebar */
    #Sidebar {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border};
    }}

    QPushButton.SidebarButton {{
        background-color: transparent;
        color: {text_secondary};
        text-align: left;
        padding: 8px 15px; /* More compact */
        border: none;
        border-radius: 6px;
        font-weight: 600;
        margin-bottom: 2px;
    }}

    QPushButton.SidebarButton:hover {{
        background-color: {btn_hover};
        color: {text_primary};
    }}

    QPushButton.SidebarButton:checked {{
        background-color: {accent};
        color: #FFFFFF;
    }}

    /* Inputs */
    QLineEdit {{
        background-color: {input_bg};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 10px 12px;
        color: {text_primary};
        font-size: 14px;
    }}

    QLineEdit:focus {{
        border: 1px solid {accent};
    }}

    /* Buttons */
    QPushButton.PrimaryButton {{
        background-color: {accent};
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 14px;
    }}

    QPushButton.PrimaryButton:hover {{
        background-color: {accent_hover};
    }}

    QPushButton.PrimaryButton:pressed {{
        background-color: {accent_pressed};
    }}

    QPushButton.PrimaryButton:disabled {{
        background-color: {border};
        color: {text_secondary};
    }}

    QPushButton.SecondaryButton {{
        background-color: {btn_hover};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 14px;
    }}

    QPushButton.SecondaryButton:hover {{
        background-color: {border};
    }}

    /* Format Cards (Quality Selection) */
    QFrame.FormatCard {{
        background-color: {card_bg};
        border-radius: 8px;
        border: 1px solid {border};
        padding: 10px;
    }}

    QFrame.FormatCard:hover {{
        border: 1px solid {accent};
        background-color: {card_hover};
    }}

    QFrame.FormatCard[selected="true"] {{
        border: 2px solid {accent};
        background-color: {card_selected};
    }}

    /* Progress Bar */
    QProgressBar {{
        border: none;
        background-color: {border};
        border-radius: 4px;
        text-align: center;
        color: transparent;
        height: 8px;
    }}

    QProgressBar::chunk {{
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent_hover});
        border-radius: 4px;
    }}

    /* Labels */
    QLabel.Title {{
        font-size: 22px;
        font-weight: 800;
        color: {text_primary};
    }}

    QLabel.SectionTitle {{
        font-size: 16px;
        font-weight: bold;
        color: {text_primary};
    }}

    QLabel.Subtitle {{
        font-size: 13px;
        color: {text_secondary};
    }}

    QLabel.FormatTitle {{
        font-size: 14px;
        font-weight: bold;
        color: {text_primary};
    }}

    QLabel.FormatDesc {{
        font-size: 11px;
        color: {text_secondary};
    }}
    
    /* Table Widget */
    QTableWidget {{ 
        background-color: transparent; 
        border: none; 
        color: {text_primary};
    }}
    QHeaderView::section {{ 
        background-color: {bg_sidebar}; 
        padding: 5px; 
        border: none; 
        font-weight: bold; 
        color: {text_primary};
    }}
    QTableWidget::item {{ 
        padding: 5px; 
        border-bottom: 1px solid {border}; 
    }}
    
    QScrollBar:vertical {{
        background: {bg_main};
        width: 10px;
    }}
    QScrollBar::handle:vertical {{
        background: {border};
        border-radius: 5px;
    }}
    """
