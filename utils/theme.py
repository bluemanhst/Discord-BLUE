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
    # Terminal Neon - phong cách Roblox BLUE (gần đen + accent xanh, bo góc)
    "Terminal Neon": {
        "name": "Terminal Neon",
        "bg_app": "#0B0E13",          # Giong Roblox C_Bg - nen terminal gan den
        "bg_sidebar": "#11161D",      # Roblox C_Panel - thanh dieu huong/statusbar
        "bg_panel": "#151B24",        # Roblox C_Card - mat the noi dung
        "bg_input": "#0D1015",        # O nhap re sau hon nen app
        "bg_hover": "#19212E",        # Roblox C_RowHover
        "bg_active": "#1E293B",       # Roblox C_RowSel
        "border": "#2C3748",          # Roblox C_CardBorder
        "border_subtle": "#1E2632",   # Roblox C_Border - divider tinh te
        "border_focus": "#3B82F6",    # Roblox C_Accent
        "text_primary": "#E6EDF3",    # Roblox C_Text
        "text_secondary": "#8B98AB",  # Roblox C_Muted
        "text_muted": "#5F697A",      # Roblox C_Dim
        "accent": "#3B82F6",          # Roblox C_Accent - xanh duong neon
        "accent_hover": "#60A5FA",    # Roblox C_AccentHover
        "accent_active": "#2563EB",   # Bam xuong (darker)
        "accent_text": "#FFFFFF",
        "success": "#22C55E",         # Roblox C_Ok
        "success_hover": "#16A34A",
        "danger": "#EF4444",          # Roblox C_Err
        "danger_hover": "#DC2626",
        "info": "#38BDF8",
        "info_hover": "#0EA5E9",
        "log_bg": "#0A0C10",          # Terminal log toi hon nua
        "log_fg": "#93C5FD",          # Chu terminal xanh neon
    },
    "Dragon Ball": {
        "name": "Dragon Ball",
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
DEFAULT_THEME_NAME = "Terminal Neon"

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
def _parent_bg(parent, fallback):
    """Lay mau nen thuc te cua parent (de ve corner 'trong suot' giong backend)."""
    try:
        bg = parent.cget("bg")
        if bg:
            return bg
    except Exception:
        pass
    return fallback


def draw_round_rect(canvas, x1, y1, x2, y2, radius=10, **kw):
    """Ve hinh chu nhat bo goc tren Canvas (smooth polygon - cong thuc pho bien)."""
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


def create_card_frame(parent, padx=16, pady=12, radius=10):
    """Card bo goc 10px + border tinh te (giong FillCard/StrokeCard Roblox BLUE).

    Canvas ve nen bo goc DUOI inner frame; corners lo mau parent -> nhin khong giong.
    Giu nguyen API cu: tra ve (card, inner).
    """
    t = get_theme()
    behind = _parent_bg(parent, t["bg_app"])
    card = tk.Frame(parent, bg=behind)
    canvas = tk.Canvas(card, bg=behind, highlightthickness=0, bd=0)
    canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
    inner = tk.Frame(card, bg=t["bg_panel"])
    inner.pack(fill="both", expand=True, padx=padx, pady=pady)

    def _redraw(event=None):
        try:
            w = card.winfo_width()
            h = card.winfo_height()
        except Exception:
            return
        if w < 4 or h < 4:
            return
        canvas.delete("all")
        draw_round_rect(canvas, 0, 0, w - 1, h - 1, radius,
                        fill=t["bg_panel"], outline=t["border"], width=1)

    card.bind("<Configure>", lambda e: _redraw())
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


class RoundedButton(tk.Canvas):
    """Button bo goc 8px ve bang Canvas - phong cach DrawButton cua Roblox BLUE.

    Giu nguyen API tk.Button o muc su dung thong thuong:
    .pack/.grid, .config(command=...), .config(state=...), .config(text=...),
    .config(width=...) (ky tu), ["state"], attribute .menu.
    """

    def __init__(self, parent, text="", command=None, variant="secondary",
                 width=None, padx=12, pady=6, font=None, **kw):
        self._text = text
        self._command = command
        self._variant = variant
        self._state = "normal"
        self._hover = False
        self._width_chars = width
        self._padx = padx
        self._pady = pady
        self._font = font or FONT_BUTTON
        behind = _parent_bg(parent, get_theme()["bg_panel"])
        px, py = self._measure()
        self._px, self._py = px, py
        try:
            super().__init__(parent, width=px, height=py, bg=behind,
                             highlightthickness=0, bd=0, cursor="hand2", **kw)
        except TypeError:
            super().__init__(parent)
        self._redraw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", lambda e: self._redraw())

    def _measure(self):
        text = self._text or "W"
        try:
            from tkinter import font as tkfont
            f = tkfont.Font(font=self._font)
            tw = f.measure(text)
            th = f.metrics("linespace")
            if self._width_chars:
                tw = max(tw, f.measure("0" * int(self._width_chars)))
        except Exception:
            tw = max(len(text), 1) * 8
            th = 16
            if self._width_chars:
                tw = max(tw, int(self._width_chars) * 8)
        return tw + 2 * self._padx + 8, th + 2 * self._pady + 4

    def _colors(self):
        t = get_theme()
        v = self._variant
        if self._state == "disabled":
            return t["bg_sidebar"], t["border_subtle"], t["text_muted"]
        if v == "primary":
            fill = t["accent_hover"] if self._hover else t["accent"]
            return fill, t["accent_hover"], t["accent_text"]
        if v == "danger":
            if self._hover:
                return "#2D161C", t["danger"], t["danger"]
            return t["bg_panel"], "#783237", t["danger"]
        if v == "success":
            fill = t["success_hover"] if self._hover else t["success"]
            return fill, t["success"], "#FFFFFF"
        if v == "ghost":
            fill = t["bg_hover"] if self._hover else _parent_bg(self.master, t["bg_panel"])
            return fill, t["border"], t["text_secondary"]
        # secondary / neutral
        if self._hover:
            return t["bg_hover"], t["accent"], t["text_primary"]
        return t["bg_panel"], t["border"], t["text_primary"]

    def _redraw(self, event=None):
        try:
            w = int(self.winfo_width()) or self._px
            h = int(self.winfo_height()) or self._py
        except Exception:
            w, h = self._px, self._py
        if w < 4 or h < 4:
            return
        try:
            self.delete("all")
        except Exception:
            return
        fill, border, fg = self._colors()
        radius = min(8, h // 2)
        draw_round_rect(self, 0, 0, w - 1, h - 1, radius,
                        fill=fill, outline=border, width=1)
        self.create_text(w // 2, h // 2, text=self._text, font=self._font, fill=fg)

    def config(self, cnf=None, **kw):
        if isinstance(cnf, dict):
            kw = {**cnf, **kw}
        redraw = False
        if "state" in kw:
            self._state = str(kw.pop("state"))
            redraw = True
        if "command" in kw:
            self._command = kw.pop("command")
        if "text" in kw:
            self._text = str(kw.pop("text"))
            self._px, self._py = self._measure()
            redraw = True
        if "width" in kw:
            self._width_chars = kw.pop("width")
            self._px, self._py = self._measure()
            redraw = True
        if kw:
            try:
                super().config(**kw)
            except Exception:
                pass
        if redraw:
            self._redraw()

    configure = config

    def cget(self, key):
        if key == "state":
            return self._state
        if key == "command":
            return self._command
        if key == "text":
            return self._text
        try:
            return super().cget(key)
        except Exception:
            return ""

    def __getitem__(self, key):
        return self.cget(key)

    def _on_enter(self, e):
        if self._state != "disabled" and not self._hover:
            self._hover = True
            self._redraw()

    def _on_leave(self, e):
        if self._hover:
            self._hover = False
            self._redraw()

    def _on_click(self, e):
        if self._state == "disabled":
            return
        if callable(self._command):
            self._command()


def create_styled_button(parent, text, command, variant="secondary", width=None, padx=12, pady=6):
    """
    Tạo button bo goc (Canvas) có phân cấp rõ ràng (primary, secondary, danger,
    success, ghost) với hover state tự nhiên - phong cach Roblox BLUE.
    """
    return RoundedButton(parent, text=text, command=command, variant=variant,
                         width=width, padx=padx, pady=pady)


def create_styled_checkbutton(parent, text="", variable=None, command=None,
                              font=None, **_ignored):
    """Toggle switch pill (giong DrawToggle Roblox BLUE) thay cho tk.Checkbutton.

    API tuong thich: .pack/.grid nhu widget binh thuong; nhan de bat/tat variable
    roi goi command. Vi du cu: tk.Checkbutton(parent, text=..., variable=...,
    font=..., cursor="hand2") -> create_styled_checkbutton(parent, text=...,
    variable=..., font=...).
    """
    from utils.anim import AnimLoop, lerp
    t = get_theme()
    behind = _parent_bg(parent, t["bg_panel"])
    frame = tk.Frame(parent, bg=behind, cursor="hand2")
    pill = tk.Canvas(frame, width=38, height=20, bg=behind,
                     highlightthickness=0, bd=0, cursor="hand2")
    pill.pack(side="left", padx=(0, 8) if text else (0, 0))
    if text:
        lbl = tk.Label(frame, text=text, bg=behind, fg=t["text_primary"],
                       font=font or FONT_BODY, cursor="hand2")
        lbl.pack(side="left")

    state = {"frac": 1.0 if (variable and variable.get()) else 0.0,
             "animating": False, "loop": None}

    def _set_knob(frac):
        state["frac"] = frac
        try:
            pill.delete("all")
        except Exception:
            return
        on = frac >= 0.5
        fill = t["accent"] if on else t["bg_input"]
        border = t["accent"] if on else t["border"]
        draw_round_rect(pill, 1, 1, 36, 18, 9, fill=fill, outline=border, width=1)
        cx = 10.0 + 18.0 * frac
        pill.create_oval(cx - 6, 4, cx + 6, 16, fill="#FFFFFF", outline="")

    def _draw():
        _set_knob(1.0 if (variable and variable.get()) else 0.0)

    def _on_var_change(*_):
        # Thay doi tu ben ngoai (reload profile...) -> ve ngay, khong anim
        if not state["animating"]:
            _draw()

    def _toggle(*_):
        if variable is None:
            if command:
                command()
            return
        target = 0.0 if variable.get() else 1.0
        variable.set(not variable.get())
        if command:
            command()
        start = state["frac"]
        state["animating"] = True

        def _step(p):
            _set_knob(lerp(start, target, p))

        def _done():
            state["animating"] = False
            _set_knob(target)

        state["loop"] = AnimLoop(frame, duration_ms=120, on_step=_step, on_done=_done)
        state["loop"].start()

    if variable is not None:
        try:
            variable.trace_add("write", _on_var_change)
        except Exception:
            pass

    widgets = [frame, pill]
    if text:
        widgets.append(lbl)
    for w in widgets:
        w.bind("<Button-1>", lambda e: _toggle())

    _draw()
    return frame


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
