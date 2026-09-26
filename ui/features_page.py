# ui/features_page.py
# Trang tính năng - Scrollable với nhiều checkboxes và entries
# Author: bluemanhst

import tkinter as tk
from utils.theme import (
    get_theme, create_card_frame, create_section_header,
    create_styled_button, create_styled_entry,
    FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION, FONT_SECTION
)
from config import config_data
import language


def create_features_page(root):
    """
    Tạo trang tính năng với cấu trúc Cards phân cấp rõ ràng, dễ scan
    
    Args:
        root: Root window
    
    Returns:
        tuple: (frame_features_page, các biến UI)
    """
    t = get_theme()

    frame_features_page = tk.Frame(root, bg=t["bg_app"])

    # Scrollable container
    frame_scroll_container = tk.Frame(frame_features_page, bg=t["bg_app"])
    frame_scroll_container.pack(fill="both", expand=True, padx=20, pady=16)

    canvas_features = tk.Canvas(frame_scroll_container, bg=t["bg_app"], highlightthickness=0)
    scrollbar_features = tk.Scrollbar(frame_scroll_container, orient="vertical", command=canvas_features.yview)
    canvas_features.pack(side="left", fill="both", expand=True)
    scrollbar_features.pack(side="right", fill="y")
    canvas_features.configure(yscrollcommand=scrollbar_features.set)

    # Frame chứa nội dung (dạng stack cards)
    frame_content = tk.Frame(canvas_features, bg=t["bg_app"])
    canvas_window = canvas_features.create_window((0, 0), window=frame_content, anchor="nw")

    def _on_frame_configure(event):
        canvas_features.configure(scrollregion=canvas_features.bbox("all"))

    frame_content.bind("<Configure>", _on_frame_configure)

    def _on_canvas_configure(event):
        canvas_features.itemconfig(canvas_window, width=event.width)

    canvas_features.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(event):
        if frame_features_page.winfo_ismapped():
            canvas_features.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas_features.bind_all("<MouseWheel>", _on_mousewheel)

    # Helper tạo card tính năng
    def make_feature_card(title, is_checked_var):
        card, inner = create_card_frame(frame_content, padx=20, pady=16)
        card.pack(fill="x", pady=(0, 14))

        chk = tk.Checkbutton(
            inner,
            text=title,
            variable=is_checked_var,
            bg=t["bg_panel"],
            fg=t["text_primary"],
            selectcolor=t["bg_input"],
            activebackground=t["bg_panel"],
            activeforeground=t["text_primary"],
            font=FONT_SECTION,
            cursor="hand2"
        )
        chk.pack(anchor="w")

        body_frame = tk.Frame(inner, bg=t["bg_panel"])
        body_frame.pack(fill="x", padx=26, pady=(8, 0))
        return card, body_frame

    # ===== TÍNH NĂNG #1: Auto Delete =====
    var_auto_delete = tk.BooleanVar(value=config_data.get("features", {}).get("auto_delete", False))
    _, body_delete = make_feature_card(language.t("features_page.auto_delete"), var_auto_delete)

    tk.Label(
        body_delete,
        text=language.t("features_page.delete_delay_label"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY_BOLD
    ).pack(anchor="w")

    _, entry_delete_delay = create_styled_entry(body_delete, width=15)
    entry_delete_delay.master.pack(anchor="w", pady=(4, 6))
    entry_delete_delay.insert(0, str(config_data.get("features", {}).get("delete_delay_ms", 0)))

    tk.Label(
        body_delete,
        text=language.t("features_page.delete_delay_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #2: Auto Typing =====
    var_auto_typing = tk.BooleanVar(value=config_data.get("features", {}).get("auto_typing", False))
    _, body_typing = make_feature_card(language.t("features_page.auto_typing"), var_auto_typing)

    typing_row = tk.Frame(body_typing, bg=t["bg_panel"])
    typing_row.pack(anchor="w", pady=(0, 6))

    tk.Label(
        typing_row,
        text=language.t("features_page.typing_range_label"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_typing_min = create_styled_entry(typing_row, width=6)
    entry_typing_min.master.pack(side="left", padx=6)
    entry_typing_min.insert(0, str(config_data.get("features", {}).get("typing_min_sec", 2)))

    tk.Label(
        typing_row,
        text=language.t("features_page.typing_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_typing_max = create_styled_entry(typing_row, width=6)
    entry_typing_max.master.pack(side="left", padx=6)
    entry_typing_max.insert(0, str(config_data.get("features", {}).get("typing_max_sec", 5)))

    tk.Label(
        body_typing,
        text=language.t("features_page.typing_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #3: Auto Break =====
    var_auto_break = tk.BooleanVar(value=config_data.get("features", {}).get("auto_break", False))
    _, body_break = make_feature_card(language.t("features_page.auto_break"), var_auto_break)

    break_after_row = tk.Frame(body_break, bg=t["bg_panel"])
    break_after_row.pack(anchor="w", pady=(0, 6))

    tk.Label(
        break_after_row,
        text=language.t("features_page.break_after_label"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_after_min = create_styled_entry(break_after_row, width=6)
    entry_break_after_min.master.pack(side="left", padx=6)
    entry_break_after_min.insert(0, str(config_data.get("features", {}).get("break_after_min", 15)))

    tk.Label(
        break_after_row,
        text=language.t("features_page.break_after_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_after_max = create_styled_entry(break_after_row, width=6)
    entry_break_after_max.master.pack(side="left", padx=6)
    entry_break_after_max.insert(0, str(config_data.get("features", {}).get("break_after_max", 25)))

    tk.Label(
        break_after_row,
        text=language.t("features_page.break_after_end"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left", padx=(4, 0))

    break_dur_row = tk.Frame(body_break, bg=t["bg_panel"])
    break_dur_row.pack(anchor="w", pady=(0, 6))

    tk.Label(
        break_dur_row,
        text=language.t("features_page.break_duration_label"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_duration_min = create_styled_entry(break_dur_row, width=6)
    entry_break_duration_min.master.pack(side="left", padx=6)
    entry_break_duration_min.insert(0, str(config_data.get("features", {}).get("break_duration_min", 10)))

    tk.Label(
        break_dur_row,
        text=language.t("features_page.break_duration_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_duration_max = create_styled_entry(break_dur_row, width=6)
    entry_break_duration_max.master.pack(side="left", padx=6)
    entry_break_duration_max.insert(0, str(config_data.get("features", {}).get("break_duration_max", 30)))

    tk.Label(
        break_dur_row,
        text=language.t("features_page.break_duration_end"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left", padx=(4, 0))

    tk.Label(
        body_break,
        text=language.t("features_page.break_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #4: Auto Stop on Ban =====
    var_auto_stop_ban = tk.BooleanVar(value=config_data.get("features", {}).get("auto_stop_on_ban", True))
    _, body_ban = make_feature_card(language.t("features_page.auto_stop_ban"), var_auto_stop_ban)

    tk.Label(
        body_ban,
        text=language.t("features_page.auto_stop_ban_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #5: Schedule =====
    var_schedule = tk.BooleanVar(value=config_data.get("features", {}).get("schedule", False))
    _, body_sched = make_feature_card(language.t("features_page.schedule"), var_schedule)

    sched_row = tk.Frame(body_sched, bg=t["bg_panel"])
    sched_row.pack(anchor="w", pady=(0, 6))

    tk.Label(
        sched_row,
        text=language.t("features_page.schedule_from"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_schedule_start = create_styled_entry(sched_row, width=6)
    entry_schedule_start.master.pack(side="left", padx=6)
    entry_schedule_start.insert(0, str(config_data.get("features", {}).get("schedule_start", "09:00")))

    tk.Label(
        sched_row,
        text=language.t("features_page.schedule_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_schedule_end = create_styled_entry(sched_row, width=6)
    entry_schedule_end.master.pack(side="left", padx=6)
    entry_schedule_end.insert(0, str(config_data.get("features", {}).get("schedule_end", "17:00")))

    tk.Label(
        body_sched,
        text=language.t("features_page.schedule_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #6: Smart Templates =====
    var_smart_templates = tk.BooleanVar(value=config_data.get("features", {}).get("smart_templates", False))
    _, body_smart = make_feature_card(language.t("features_page.smart_templates"), var_smart_templates)

    btn_smart_templates_info = create_styled_button(
        body_smart,
        text=language.t("features_page.smart_templates_btn"),
        command=show_smart_templates_info,
        variant="ghost",
        padx=10,
        pady=4
    )
    btn_smart_templates_info.pack(anchor="w", pady=(2, 4))

    # ===== TÍNH NĂNG #7: Sound Notifications =====
    var_sound_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("sound_enabled", False))
    _, body_sound = make_feature_card(language.t("features_page.sound_enabled"), var_sound_enabled)

    var_sound_error = tk.BooleanVar(value=config_data.get("features", {}).get("sound_error", True))
    var_sound_stop = tk.BooleanVar(value=config_data.get("features", {}).get("sound_stop", True))
    var_sound_success = tk.BooleanVar(value=config_data.get("features", {}).get("sound_success", True))

    sound_options = [
        ("features_page.sound_error", var_sound_error),
        ("features_page.sound_stop", var_sound_stop),
        ("features_page.sound_success", var_sound_success)
    ]

    for label_key, sound_var in sound_options:
        chk_opt = tk.Checkbutton(
            body_sound,
            text=language.t(label_key),
            variable=sound_var,
            bg=t["bg_panel"],
            fg=t["text_secondary"],
            selectcolor=t["bg_input"],
            activebackground=t["bg_panel"],
            activeforeground=t["text_primary"],
            font=FONT_BODY,
            cursor="hand2"
        )
        chk_opt.pack(anchor="w", pady=2)

    return (
        frame_features_page,
        var_auto_delete, entry_delete_delay,
        var_auto_typing, entry_typing_min, entry_typing_max,
        var_auto_break, entry_break_after_min, entry_break_after_max,
        entry_break_duration_min, entry_break_duration_max,
        var_auto_stop_ban,
        var_schedule, entry_schedule_start, entry_schedule_end,
        var_smart_templates,
        var_sound_enabled, var_sound_error, var_sound_stop, var_sound_success
    )


def show_smart_templates_info():
    """Hiển thị modal popup hướng dẫn cú pháp Smart Template chuẩn chỉnh"""
    from tkinter import Toplevel, scrolledtext
    t = get_theme()

    info_window = Toplevel()
    info_window.title(language.t("features_page.smart_templates_title"))
    info_window.geometry("560x520")
    info_window.configure(bg=t["bg_app"])

    container = tk.Frame(info_window, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=20)

    card, inner = create_card_frame(container, padx=16, pady=16)
    card.pack(fill="both", expand=True)

    create_section_header(
        inner,
        title=language.t("features_page.smart_templates_title")
    )

    info_text = scrolledtext.ScrolledText(
        inner,
        height=16,
        bg=t["bg_input"],
        fg=t["text_primary"],
        font=FONT_BODY,
        relief="flat",
        bd=4,
        wrap="word"
    )
    info_text.pack(fill="both", expand=True, pady=(8, 12))

    explanation = language.t("features_page.smart_templates_content")
    info_text.insert("1.0", explanation)
    info_text.config(state="disabled")

    btn_close = create_styled_button(
        inner,
        text=language.t("features_page.smart_templates_close"),
        command=info_window.destroy,
        variant="secondary",
        padx=16,
        pady=6
    )
    btn_close.pack(anchor="e")