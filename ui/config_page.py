# ui/config_page.py
# Trang quản lý cấu hình - Export/Import
# Author: bluemanhst

import tkinter as tk
from utils.constants import BG_PANEL, BTN_ORANGE, TXT_WHITE
from config import config_data, export_config, import_and_apply_config
import language


def create_config_page(root):
    """
    Tạo trang quản lý cấu hình với nút Export/Import
    
    Args:
        root: Root window
    
    Returns:
        tuple: (frame_config_page)
    """
    # Frame chính của trang
    frame_config_page = tk.Frame(root, bg=BG_PANEL)

    # Frame chứa các nút
    frame_config_main = tk.Frame(frame_config_page, bg=BG_PANEL, bd=2, relief="ridge")
    frame_config_main.pack(fill="both", expand=True, padx=15, pady=10)

    frame_config_buttons = tk.Frame(frame_config_main, bg=BG_PANEL)
    frame_config_buttons.pack(anchor="w", padx=30, pady=(20, 8), fill="x")

    btn_export = tk.Button(frame_config_buttons, text=language.t("config_page.btn_export"), command=lambda: export_config(config_data),
                          bg=BTN_ORANGE, fg=TXT_WHITE, font=("Arial", 10, "bold"),
                          activebackground="#E65C00", activeforeground=TXT_WHITE, bd=3, relief="ridge", padx=20, pady=10)
    btn_export.pack(side="left", padx=10)

    btn_import = tk.Button(frame_config_buttons, text=language.t("config_page.btn_import"), command=import_and_apply_config,
                          bg=BTN_ORANGE, fg=TXT_WHITE, font=("Arial", 10, "bold"),
                          activebackground="#E65C00", activeforeground=TXT_WHITE, bd=3, relief="ridge", padx=20, pady=10)
    btn_import.pack(side="left", padx=10)

    tk.Label(frame_config_main, text=language.t("config_page.config_hint"), 
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 9), justify="left").pack(anchor="w", padx=30, pady=10)

    return frame_config_page
