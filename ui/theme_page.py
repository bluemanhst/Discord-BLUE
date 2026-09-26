# ui/theme_page.py
# Trang chọn theme - Dragon Ball, Discord, Dark Professional
# Author: bluemanhst

import tkinter as tk
from tkinter import messagebox
from utils.theme import (
    THEMES, DEFAULT_THEME_NAME, get_theme,
    create_card_frame, create_section_header, FONT_BODY, FONT_BUTTON
)
from config import config_data, save_config
import language


def create_theme_page(root):
    """
    Tạo trang chọn theme với thiết kế dạng danh sách lựa chọn chuyên nghiệp.
    Lưu theme vào config và thông báo khởi động lại để áp dụng an toàn.
    
    Returns:
        Frame: frame_theme_page
    """
    t = get_theme()

    frame_theme_page = tk.Frame(root, bg=t["bg_app"])

    container = tk.Frame(frame_theme_page, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    card, card_inner = create_card_frame(container, padx=24, pady=20)
    card.pack(fill="both", expand=True)

    current_theme = config_data.get("current_theme", DEFAULT_THEME_NAME)

    create_section_header(
        card_inner,
        title=language.t("theme_page.select_theme"),
        subtitle=language.t("theme_page.theme_reopen")
    )

    # Current theme indicator banner
    status_banner = tk.Frame(
        card_inner,
        bg=t["bg_hover"],
        highlightthickness=1,
        highlightbackground=t["border"],
        padx=14,
        pady=10
    )
    status_banner.pack(fill="x", pady=(0, 16))

    lbl_status_title = tk.Label(
        status_banner,
        text=language.t("theme_page.theme_label"),
        bg=t["bg_hover"],
        fg=t["text_secondary"],
        font=FONT_BODY
    )
    lbl_status_title.pack(side="left")

    lbl_current_theme = tk.Label(
        status_banner,
        text=current_theme,
        bg=t["bg_hover"],
        fg=t["accent"],
        font=FONT_BUTTON
    )
    lbl_current_theme.pack(side="left", padx=(8, 0))

    theme_buttons = {}

    def apply_theme(theme_name):
        nonlocal current_theme
        current_theme = theme_name

        config_data["current_theme"] = theme_name
        if not save_config(config_data):
            return

        lbl_current_theme.config(text=theme_name)

        # Highlight selected theme button
        for name, btn in theme_buttons.items():
            if name == theme_name:
                btn.config(
                    bg=t["bg_hover"],
                    highlightbackground=t["accent"],
                    highlightcolor=t["accent"]
                )
            else:
                btn.config(
                    bg=t["bg_panel"],
                    highlightbackground=t["border"],
                    highlightcolor=t["border"]
                )

        messagebox.showinfo(
            language.t("common.info_title"),
            f"{language.t('theme_page.theme_current')} {theme_name}\n\n"
            + language.t("theme_page.theme_reopen")
        )

    # Theme options list
    themes_list_frame = tk.Frame(card_inner, bg=t["bg_panel"])
    themes_list_frame.pack(fill="x", pady=4)

    for theme_name, theme_data in THEMES.items():
        is_selected = (theme_name == current_theme)

        opt_frame = tk.Frame(
            themes_list_frame,
            bg=t["bg_hover"] if is_selected else t["bg_panel"],
            highlightthickness=1,
            highlightbackground=t["accent"] if is_selected else t["border"],
            cursor="hand2"
        )
        opt_frame.pack(fill="x", pady=6)
        theme_buttons[theme_name] = opt_frame

        # Inner content
        content_box = tk.Frame(opt_frame, bg=opt_frame["bg"])
        content_box.pack(fill="x", padx=16, pady=12)

        # Color preview pills
        preview_box = tk.Frame(content_box, bg=opt_frame["bg"])
        preview_box.pack(side="right", padx=(10, 0))

        for color_key in ["bg_app", "bg_panel", "accent", "text_primary"]:
            pill = tk.Frame(
                preview_box,
                bg=theme_data[color_key],
                width=16,
                height=16,
                highlightthickness=1,
                highlightbackground=t["border"]
            )
            pill.pack(side="left", padx=2)

        lbl_name = tk.Label(
            content_box,
            text=theme_name,
            bg=opt_frame["bg"],
            fg=t["text_primary"],
            font=FONT_BUTTON,
            anchor="w"
        )
        lbl_name.pack(side="left")

        # Click handler for entire card
        def make_click_handler(tn=theme_name):
            return lambda e: apply_theme(tn)

        handler = make_click_handler()
        opt_frame.bind("<Button-1>", handler)
        content_box.bind("<Button-1>", handler)
        lbl_name.bind("<Button-1>", handler)

    return frame_theme_page
