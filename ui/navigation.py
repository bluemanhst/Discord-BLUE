# ui/navigation.py
# Navigation bar - Thanh điều hướng các trang
# Author: bluemanhst

import tkinter as tk
from utils.theme import get_theme, FONT_BUTTON
import language


def create_navigation_bar(root, show_main_page, show_features_page, show_config_page, show_theme_page, show_dashboard_page, show_settings_page):
    """
    Tạo navigation bar ở trên cùng cửa sổ với phong cách thanh lịch, hiện đại.
    Hiển thị active indicator và hover mượt mà.
    
    Args:
        root: Root window
        show_main_page: Hàm hiển thị trang chính
        show_features_page: Hàm hiển thị trang tính năng
        show_config_page: Hàm hiển thị trang cấu hình
        show_theme_page: Hàm hiển thị trang theme
        show_dashboard_page: Hàm hiển thị trang dashboard
        show_settings_page: Hàm hiển thị trang cài đặt
    
    Returns:
        Frame: Navigation bar frame
    """
    t = get_theme()

    # Outer container with bottom subtle border
    nav_bar = tk.Frame(root, bg=t["border_subtle"], height=52)
    nav_bar.pack(side="top", fill="x")

    nav_inner = tk.Frame(nav_bar, bg=t["bg_sidebar"])
    nav_inner.pack(fill="x", padx=0, pady=(0, 1))

    # Danh sách các nút navigation
    nav_items = [
        ("main", language.t("navigation.main"), show_main_page),
        ("features", language.t("navigation.features"), show_features_page),
        ("config", language.t("navigation.config"), show_config_page),
        ("theme", language.t("navigation.theme"), show_theme_page),
        ("dashboard", language.t("navigation.dashboard"), show_dashboard_page),
        ("settings", language.t("navigation.settings"), show_settings_page)
    ]

    button_widgets = {}
    active_key = ["main"]

    def set_active(key):
        active_key[0] = key
        for k, btn in button_widgets.items():
            if k == key:
                btn.config(
                    bg=t["bg_panel"],
                    fg=t["accent"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"]
                )
            else:
                btn.config(
                    bg=t["bg_sidebar"],
                    fg=t["text_secondary"],
                    highlightbackground=t["bg_sidebar"],
                    highlightcolor=t["bg_sidebar"]
                )

    # Frame chứa các nút
    btn_container = tk.Frame(nav_inner, bg=t["bg_sidebar"])
    btn_container.pack(fill="x", padx=16, pady=8)

    for key, text, cmd in nav_items:
        def make_handler(target_key=key, target_cmd=cmd):
            def handler():
                set_active(target_key)
                target_cmd()
            return handler

        btn = tk.Button(
            btn_container,
            text=text,
            command=make_handler(),
            bg=t["bg_panel"] if key == "main" else t["bg_sidebar"],
            fg=t["accent"] if key == "main" else t["text_secondary"],
            font=FONT_BUTTON,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=t["border"] if key == "main" else t["bg_sidebar"],
            activebackground=t["bg_hover"],
            activeforeground=t["text_primary"],
            cursor="hand2",
            padx=14,
            pady=6
        )
        btn.pack(side="left", padx=3)
        button_widgets[key] = btn

        # Hover states for non-active buttons
        def on_enter(e, b=btn, k=key):
            if active_key[0] != k:
                b.config(bg=t["bg_hover"], fg=t["text_primary"])

        def on_leave(e, b=btn, k=key):
            if active_key[0] != k:
                b.config(bg=t["bg_sidebar"], fg=t["text_secondary"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Lưu hàm set_active lên nav_bar để có thể gọi từ ngoài nếu cần
    nav_bar.set_active = set_active

    return nav_bar
