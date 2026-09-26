# ui/config_page.py
# Trang quản lý cấu hình - Export/Import
# Author: bluemanhst

import tkinter as tk
from utils.theme import get_theme, create_card_frame, create_section_header, create_styled_button
from config import config_data, export_config, import_and_apply_config
import language


def create_config_page(root):
    """
    Tạo trang quản lý cấu hình với thiết kế Card phẳng chuyên nghiệp
    
    Args:
        root: Root window
    
    Returns:
        Frame: frame_config_page
    """
    t = get_theme()

    frame_config_page = tk.Frame(root, bg=t["bg_app"])

    container = tk.Frame(frame_config_page, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    # Main Card
    card, card_inner = create_card_frame(container, padx=24, pady=20)
    card.pack(fill="both", expand=True)

    create_section_header(
        card_inner,
        title=language.t("config_page.btn_export") + " / " + language.t("config_page.btn_import"),
        subtitle=language.t("config_page.config_hint")
    )

    # Actions container
    actions_frame = tk.Frame(card_inner, bg=t["bg_panel"])
    actions_frame.pack(anchor="w", pady=(16, 8))

    btn_export = create_styled_button(
        actions_frame,
        text=language.t("config_page.btn_export"),
        command=lambda: export_config(config_data),
        variant="primary",
        padx=18,
        pady=8
    )
    btn_export.pack(side="left", padx=(0, 10))

    btn_import = create_styled_button(
        actions_frame,
        text=language.t("config_page.btn_import"),
        command=import_and_apply_config,
        variant="secondary",
        padx=18,
        pady=8
    )
    btn_import.pack(side="left")

    return frame_config_page
