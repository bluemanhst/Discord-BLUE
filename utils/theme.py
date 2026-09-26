# utils/theme.py
# Design System & Central Theme Manager
# Author: bluemanhst
# Provides unified color tokens, fonts, spacing, and widget styling helpers

import tkinter as tk
from tkinter import ttk

# ==============================================================================
# 1. THEME PRESETS (DESIGN TOKENS)
# Professional desktop utility palettes inspired by modern developer tools
# ==============================================================================
THEMES = {
    "Dragon Ball (Mặc định)": {
        "name": "Dragon Ball (Mặc định)",
        "bg_app": "#16171D",          # Deep slate app background
        "bg_sidebar": "#121318",      # Slightly darker sidebar/header
        "bg_panel": "#1E2029",        # Clean card/panel surface
        "bg_input": "#14151B",        # Recessed input field background
        "bg_hover": "#282B37",        # Hover state
        "bg_active": "#323646",       # Active / pressed state
        "border": "#2D303E",          # Default border
        "border_subtle": "#232632",   # Subtle divider border
        "border_focus": "#E67E22",    # Active focus border
        "text_primary": "#F2F4F8",    # High contrast primary text
        "text_secondary": "#A0A5B5",  # Balanced secondary text
        "text_muted": "#686D7F",      # Subtle hint text
        "accent": "#E67E22",          # Warm amber primary accent
        "accent_hover": "#D35400",    # Accent hover
        "accent_active": "#BA4A00",   # Accent pressed
        "accent_text": "#FFFFFF",     # Text on accent button
        "success": "#2ECC71",         # Emerald success
        "success_hover": "#27AE60",
        "danger": "#E74C3C",          # Coral danger
        "danger_hover": "#C0392B",
        "info": "#3498DB",            # Soft blue
        "info_hover": "#2980B9",
        "log_bg": "#0D0E12",          # Terminal dark background
        "log_fg": "#A5B4FC",          # Code text foreground
    },
    "Discord": {
        "name": "Discord",
        "bg_app": "#1E1F22",          # Official Discord dark base
        "bg_sidebar": "#18191C",      # Darker nav column
        "bg_panel": "#2B2D31",        # Discord message panel surface
        "bg_input": "#1E1F22",        # Recessed input box
        "bg_hover": "#35373C",
        "bg_active": "#3F4147",
        "border": "#3A3C42",
        "border_subtle": "#2B2D31",
        "border_focus": "#5865F2",
        "text_primary": "#F2F3F5",
        "text_secondary": "#B5BAC1",
        "text_muted": "#80848E",
        "accent": "#5865F2",          # Discord Blurple
        "accent_hover": "#4752C4",
        "accent_active": "#3C45A5",
        "accent_text": "#FFFFFF",
        "success": "#23A55A",
        "success_hover": "#1D8B4B",
        "danger": "#F23F43",
        "danger_hover": "#DA373C",
        "info": "#00A8FC",
        "info_hover": "#0088CC",
        "log_bg": "#111214",
        "log_fg": "#949BA4",
    },
    "Dark Professional": {
        "name": "Dark Professional",
        "bg_app": "#0F1117",          # Modern charcoal/zinc
        "bg_sidebar": "#090A0E",
        "bg_panel": "#181B23",
        "bg_input": "#12141A",
        "bg_hover": "#222632",
        "bg_active": "#2B3040",
        "border": "#282C3A",
        "border_subtle": "#1D212C",
        "border_focus": "#6366F1",    # Indigo accent
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#6366F1",
        "accent_hover": "#4F46E5",
        "accent_active": "#4338CA",
        "accent_text": "#FFFFFF",
        "success": "#10B981",
        "success_hover": "#059669",
        "danger": "#EF4444",
        "danger_hover": "#DC2626",
        "info": "#0EA5E9",
        "info_hover": "#0284C7",
        "log_bg": "#08090D",
        "log_fg": "#CBD5E1",
    }
}

# Tên theme mặc định - DÙNG CHUNG cho config.py, ui/theme_page.py và main.pyw
# (tránh mỗi nơi hardcode một chuỗi, dễ lệch nhau khi đổi tên theme)
DEFAULT_THEME_NAME = "Dragon Ball (Mặc định)"

# ==============================================================================
# 2. TYPOGRAPHY SYSTEM
# Native-first, clean system font stack (Segoe UI on Windows, SF Pro on macOS, Arial fallback)
# ==============================================================================
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

# Standard Type Scale
FONT_TITLE = (FONT_FAMILY, 15, "bold")
FONT_SECTION = (FONT_FAMILY, 11, "bold")
FONT_SUBSECTION = (FONT_FAMILY, 10, "bold")
FONT_BODY = (FONT_FAMILY, 9)
FONT_BODY_BOLD = (FONT_FAMILY, 9, "bold")
FONT_CAPTION = (FONT_FAMILY, 8)
FONT_CODE = (FONT_MONO, 9)
FONT_BUTTON = (FONT_FAMILY, 9, "bold")
FONT_BADGE = (FONT_FAMILY, 8, "bold")


# ==============================================================================
# 3. THEME MANAGER SINGLETON
# Holds current theme state and provides reactive helpers
# ==============================================================================
class ThemeManager:
    _instance = None

    def __init__(self):
        self.current_name = DEFAULT_THEME_NAME
        self.t = THEMES[self.current_name]
        self._listeners = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.current_name = theme_name
            self.t = THEMES[theme_name]
            for callback in self._listeners:
                try:
                    callback(self.t)
                except Exception:
                    pass

    def add_listener(self, callback):
        self._listeners.append(callback)

    def tokens(self):
        return self.t


def get_theme():
    return ThemeManager.get_instance().tokens()


# ==============================================================================
# 4. TTK STYLING & GLOBAL COMPONENT BUILDERS
# Clean flat widgets without bevels, 3D borders, or harsh contrasts
# ==============================================================================
def configure_ttk_styles(root=None):
    """Cấu hình lại ttk styles (Combobox, Treeview, Notebook, Scrollbar) đồng bộ theme"""
    style = ttk.Style(root)
    # Dùng theme 'clam' làm nền vì nó cho phép tùy biến màu phẳng tốt nhất
    if "clam" in style.theme_names():
        try:
            style.theme_use("clam")
        except Exception:
            pass

    t = get_theme()

    # --- TCombobox ---
    style.configure(
        "TCombobox",
        background=t["bg_input"],
        foreground=t["text_primary"],
        fieldbackground=t["bg_input"],
        darkcolor=t["border"],
        lightcolor=t["border"],
        bordercolor=t["border"],
        arrowcolor=t["text_secondary"],
        padding=5,
        font=FONT_BODY
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", t["bg_input"]), ("disabled", t["bg_app"])],
        foreground=[("readonly", t["text_primary"]), ("disabled", t["text_muted"])],
        bordercolor=[("focus", t["border_focus"])],
        arrowcolor=[("focus", t["text_primary"])]
    )

    # --- Treeview (Tables / Lists) ---
    style.configure(
        "Treeview",
        background=t["bg_panel"],
        foreground=t["text_primary"],
        fieldbackground=t["bg_panel"],
        bordercolor=t["border_subtle"],
        borderwidth=0,
        font=FONT_BODY,
        rowheight=26
    )
    style.map(
        "Treeview",
        background=[("selected", t["bg_hover"])],
        foreground=[("selected", t["text_primary"])]
    )
    style.configure(
        "Treeview.Heading",
        background=t["bg_sidebar"],
        foreground=t["text_secondary"],
        bordercolor=t["border_subtle"],
        borderwidth=1,
        font=FONT_BODY_BOLD,
        padding=(8, 6)
    )
    style.map(
        "Treeview.Heading",
        background=[("active", t["bg_panel"])],
        foreground=[("active", t["text_primary"])]
    )

    # --- TNotebook (Tabs) ---
    style.configure(
        "TNotebook",
        background=t["bg_app"],
        bordercolor=t["border_subtle"],
        borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=t["bg_panel"],
        foreground=t["text_secondary"],
        font=FONT_BODY_BOLD,
        padding=(14, 7),
        bordercolor=t["border"],
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", t["bg_app"]), ("active", t["bg_hover"])],
        foreground=[("selected", t["text_primary"]), ("active", t["text_primary"])]
    )


# ==============================================================================
# 5. REUSABLE UI COMPONENT HELPERS (CLEAN, PRO LOOK)
# ==============================================================================
def create_card_frame(parent, padx=16, pady=12):
    """Tạo một Panel/Card phẳng, có border tinh tế, không bóng bẩy AI"""
    t = get_theme()
    card = tk.Frame(
        parent,
        bg=t["bg_panel"],
        highlightthickness=1,
        highlightbackground=t["border"],
        highlightcolor=t["border"]
    )
    inner = tk.Frame(card, bg=t["bg_panel"])
    inner.pack(fill="both", expand=True, padx=padx, pady=pady)
    return card, inner


def create_section_header(parent, title, subtitle=None):
    """Header phân đoạn chuẩn chỉnh với title và mô tả phụ (caption)"""
    t = get_theme()
    header_frame = tk.Frame(parent, bg=t["bg_panel"])
    header_frame.pack(fill="x", pady=(0, 10))

    lbl_title = tk.Label(
        header_frame,
        text=title,
        bg=t["bg_panel"],
        fg=t["text_primary"],
        font=FONT_SECTION,
        anchor="w"
    )
    lbl_title.pack(anchor="w")

    if subtitle:
        lbl_sub = tk.Label(
            header_frame,
            text=subtitle,
            bg=t["bg_panel"],
            fg=t["text_muted"],
            font=FONT_CAPTION,
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

    return header_frame


def create_styled_button(parent, text, command, variant="secondary", width=None, padx=12, pady=6):
    """
    Tạo button có phân cấp rõ ràng (primary, secondary, danger, success, ghost)
    với hover state tự nhiên và border tinh tế.
    """
    t = get_theme()

    if variant == "primary":
        bg_col = t["accent"]
        fg_col = t["accent_text"]
        hover_col = t["accent_hover"]
        active_col = t["accent_active"]
        border_col = t["accent"]
    elif variant == "danger":
        bg_col = t["danger"]
        fg_col = "#FFFFFF"
        hover_col = t["danger_hover"]
        active_col = t["danger_hover"]
        border_col = t["danger"]
    elif variant == "success":
        bg_col = t["success"]
        fg_col = "#FFFFFF"
        hover_col = t["success_hover"]
        active_col = t["success_hover"]
        border_col = t["success"]
    elif variant == "ghost":
        bg_col = t["bg_panel"]
        fg_col = t["text_secondary"]
        hover_col = t["bg_hover"]
        active_col = t["bg_active"]
        border_col = t["border"]
    else:  # secondary (default)
        bg_col = t["bg_hover"]
        fg_col = t["text_primary"]
        hover_col = t["bg_active"]
        active_col = t["border"]
        border_col = t["border"]

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_col,
        fg=fg_col,
        font=FONT_BUTTON,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=border_col,
        highlightcolor=t["border_focus"],
        activebackground=active_col,
        activeforeground=fg_col,
        cursor="hand2",
        padx=padx,
        pady=pady
    )
    if width:
        btn.config(width=width)

    def on_enter(e):
        if btn["state"] != "disabled":
            btn.config(bg=hover_col)

    def on_leave(e):
        if btn["state"] != "disabled":
            btn.config(bg=bg_col)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


def create_styled_entry(parent, width=None):
    """Tạo ô input text chuẩn với border phẳng và focus state tự động"""
    t = get_theme()
    frame = tk.Frame(
        parent,
        bg=t["border"],
        bd=0,
        highlightthickness=1,
        highlightbackground=t["border"],
        highlightcolor=t["border_focus"]
    )
    entry = tk.Entry(
        frame,
        bg=t["bg_input"],
        fg=t["text_primary"],
        insertbackground=t["text_primary"],
        font=FONT_CODE,
        relief="flat",
        bd=4
    )
    if width:
        entry.config(width=width)
    entry.pack(fill="both", expand=True)

    def on_focus_in(e):
        frame.config(highlightbackground=t["border_focus"], highlightcolor=t["border_focus"])

    def on_focus_out(e):
        frame.config(highlightbackground=t["border"], highlightcolor=t["border"])

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return frame, entry


def create_styled_text(parent, height=5):
    """Tạo text area chuẩn với viền phẳng và focus state"""
    t = get_theme()
    frame = tk.Frame(
        parent,
        bg=t["border"],
        bd=0,
        highlightthickness=1,
        highlightbackground=t["border"],
        highlightcolor=t["border_focus"]
    )
    txt = tk.Text(
        frame,
        height=height,
        bg=t["bg_input"],
        fg=t["text_primary"],
        insertbackground=t["text_primary"],
        font=FONT_CODE,
        relief="flat",
        bd=4,
        wrap="none"
    )
    txt.pack(fill="both", expand=True)

    def on_focus_in(e):
        frame.config(highlightbackground=t["border_focus"], highlightcolor=t["border_focus"])

    def on_focus_out(e):
        frame.config(highlightbackground=t["border"], highlightcolor=t["border"])

    txt.bind("<FocusIn>", on_focus_in)
    txt.bind("<FocusOut>", on_focus_out)

    return frame, txt
