# ui/theme_page.py
# Trang chọn theme - Dragon Ball, Discord, Dark Professional
# Author: bluemanhst

import sys
import os
# Thêm đường dẫn root để import được các module khi chạy file trực tiếp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
from utils.constants import BG_PANEL, BG_DARK, TXT_GOLD, TXT_WHITE
from config import config_data, save_config
import language


def create_theme_page(root):
    """
    Tạo trang chọn theme với các preset theme

    Theme chỉ được LƯU vào config; người dùng đóng và mở lại tool
    để áp dụng (an toàn cho bản EXE, tránh restart process).

    Returns:
        tuple: (frame_theme_page)
    """
    # Frame chính của trang
    frame_theme_page = tk.Frame(root, bg=BG_DARK)

    # Frame chứa theme options
    frame_theme_main = tk.Frame(frame_theme_page, bg=BG_PANEL, bd=2, relief="ridge")
    frame_theme_main.pack(fill="both", expand=True, padx=15, pady=10)

    # Theme presets
    themes = {
        "Dragon Ball (Mặc định)": {
            "BG_DARK": "#1E1E24",
            "BG_PANEL": "#2A2A35", 
            "TXT_GOLD": "#FFCC00",
            "TXT_WHITE": "#FFFFFF",
            "BTN_ORANGE": "#FF6600",
            "BTN_RED": "#CC0000",
            "LOG_BLUE": "#00DDFF"
        },
        "Discord": {
            "BG_DARK": "#36393f",
            "BG_PANEL": "#2f3136",
            "TXT_GOLD": "#5865F2", 
            "TXT_WHITE": "#FFFFFF",
            "BTN_ORANGE": "#5865F2",
            "BTN_RED": "#ED4245",
            "LOG_BLUE": "#5865F2"
        },
        "Dark Professional": {
            "BG_DARK": "#121212",
            "BG_PANEL": "#1E1E1E",
            "TXT_GOLD": "#BB86FC",
            "TXT_WHITE": "#E0E0E0", 
            "BTN_ORANGE": "#BB86FC",
            "BTN_RED": "#CF6679",
            "LOG_BLUE": "#03DAC6"
        }
    }

    # Lấy theme hiện tại từ config (mặc định là Dragon Ball)
    current_theme = config_data.get("current_theme", "Dragon Ball (Mặc định)")

    def apply_theme(theme_name):
        """Lưu theme; người dùng mở lại tool để áp dụng"""
        nonlocal current_theme
        theme = themes[theme_name]
        
        # Cập nhật theme hiện tại
        current_theme = theme_name
        
        # Lưu vào config (chi luu, KHONG restart app)
        config_data["current_theme"] = theme_name
        if not save_config(config_data):
            return

        # Cập nhật label hiển thị theme đang chọn
        lbl_current_theme.config(
            text=f"{language.t('theme_page.theme_current')} {theme_name}",
            bg=theme["BG_PANEL"], fg=theme["TXT_GOLD"])
        
        # Cập nhật màu các frame chính trong trang theme
        frame_theme_page.configure(bg=theme["BG_DARK"])
        frame_theme_main.configure(bg=theme["BG_PANEL"])
        
        # Cập nhật lại các nút theme
        for btn in frame_theme_main.winfo_children():
            if isinstance(btn, tk.Button):
                btn_name = btn.cget("text")
                if btn_name in themes:
                    btn_theme = themes[btn_name]
                    btn.configure(bg=btn_theme["BTN_ORANGE"])
            elif isinstance(btn, tk.Label):
                btn.configure(bg=theme["BG_PANEL"], fg=theme["TXT_GOLD"])
        
        # KHONG tu restart app (nguyen nhan loi init.tcl trong EXE khi doi
        # theme lien tuc); thong bao nguoi dung tu dong/mo lai tool
        messagebox.showinfo(
            "Theme", f"{language.t('theme_page.theme_current')} {theme_name}\n\n"
            + language.t("theme_page.theme_reopen"))

    # Label hiển thị theme đang chọn
    tk.Label(frame_theme_main, text=language.t("theme_page.theme_label"), bg=BG_PANEL, fg=TXT_GOLD, 
           font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(20, 5))
    
    lbl_current_theme = tk.Label(frame_theme_main, text=f"{language.t('theme_page.theme_current')} {current_theme}", 
                                bg=BG_PANEL, fg=TXT_GOLD, font=("Arial", 10))
    lbl_current_theme.pack(anchor="w", padx=30, pady=(0, 15))

    # Theme buttons
    tk.Label(frame_theme_main, text=language.t("theme_page.select_theme"), bg=BG_PANEL, fg=TXT_GOLD, 
           font=("Arial", 10, "bold")).pack(anchor="w", padx=30, pady=(10, 10))

    for i, (theme_name, theme_data) in enumerate(themes.items()):
        btn_theme = tk.Button(frame_theme_main, text=theme_name, 
                            command=lambda t=theme_name: apply_theme(t),
                            bg=theme_data["BTN_ORANGE"], fg=TXT_WHITE,
                            font=("Arial", 10, "bold"), bd=3, relief="ridge", padx=20, pady=10)
        btn_theme.pack(fill="x", padx=30, pady=5)

    return frame_theme_page
