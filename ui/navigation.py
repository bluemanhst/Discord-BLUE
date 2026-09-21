# ui/navigation.py
# Navigation bar - Thanh điều hướng các trang
# Author: bluemanhst

import tkinter as tk
from utils.constants import BG_PANEL, BG_DARK, TXT_GOLD, TXT_WHITE, HEADER_HOVER_BG
import language


def create_navigation_bar(root, show_main_page, show_features_page, show_config_page, show_theme_page, show_dashboard_page, show_settings_page):
    """
    Tạo navigation bar ở trên cùng cửa sổ
    Luôn hiển thị để dễ dàng chuyển giữa các trang
    
    Args:
        root: Root window
        show_main_page: Hàm để hiển thị trang chính
        show_features_page: Hàm để hiển thị trang tính năng
        show_config_page: Hàm để hiển thị trang cấu hình
        show_theme_page: Hàm để hiển thị trang theme
        show_dashboard_page: Hàm để hiển thị trang dashboard
        show_settings_page: Hàm để hiển thị trang cài đặt
    
    Returns:
        Frame: Navigation bar frame
    """
    nav_bar = tk.Frame(root, bg=BG_PANEL, height=50)
    nav_bar.pack(side="top", fill="x", padx=5, pady=5)

    # Danh sách các nút navigation
    nav_btns = [
        ("🏠 " + language.t("navigation.main"), show_main_page),
        ("⚙️  " + language.t("navigation.features"), show_features_page),
        ("💾 " + language.t("navigation.config"), show_config_page),
        ("🎨 " + language.t("navigation.theme"), show_theme_page),
        ("📊 " + language.t("navigation.dashboard"), show_dashboard_page),
        ("⚙️  " + language.t("navigation.settings"), show_settings_page)
    ]

    # Tạo các nút
    for text, command in nav_btns:
        btn = tk.Button(nav_bar, text=text, command=command,
                      bg=BG_DARK, fg=TXT_GOLD, font=("Arial", 9, "bold"),
                      activebackground=HEADER_HOVER_BG, activeforeground=TXT_WHITE,
                      bd=2, relief="ridge", padx=10, pady=5)
        btn.pack(side="left", padx=2, expand=True, fill="x")

    return nav_bar
