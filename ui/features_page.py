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


def create_features_page(root, profile_provider=None):
    """
    Tạo trang tính năng với cấu trúc Cards phân cấp rõ ràng, dễ scan

    Args:
        root: Root window
        profile_provider: hàm trả về profile đang chọn ở TRANG CHÍNH
            (để tab này sửa features riêng từng token). Bỏ trống = dùng global cũ.

    Returns:
        tuple: (frame_features_page, các biến UI)
    """
    t = get_theme()

    def _active_features():
        try:
            if callable(profile_provider):
                prof = profile_provider()
                if isinstance(prof, dict) and isinstance(prof.get("features"), dict):
                    return prof.get("features")
        except Exception:
            pass
        return config_data.get("features", {})

    def _active_profile_name():
        try:
            if callable(profile_provider):
                prof = profile_provider()
                if isinstance(prof, dict):
                    return str(prof.get("name", "")).strip()
        except Exception:
            pass
        return ""

    frame_features_page = tk.Frame(root, bg=t["bg_app"])

    banner, banner_inner = create_card_frame(frame_features_page, padx=16, pady=10)
    banner.pack(fill="x", padx=20, pady=(16, 0))
    lbl_profile_banner = tk.Label(
        banner_inner, text="", bg=t["bg_panel"],
        fg=t["accent"], font=FONT_BODY_BOLD, anchor="w",
    )
    lbl_profile_banner.pack(fill="x")

    def refresh_profile_banner():
        name = _active_profile_name()
        if name:
            lbl_profile_banner.config(text=language.t("profiles_panel.editing_profile", name))
        else:
            lbl_profile_banner.config(text="")
    refresh_profile_banner()
    frame_features_page.refresh_profile_banner = refresh_profile_banner

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
    var_auto_delete = tk.BooleanVar(value=_active_features().get("auto_delete", False))
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
    entry_delete_delay.insert(0, str(_active_features().get("delete_delay_ms", 0)))

    tk.Label(
        body_delete,
        text=language.t("features_page.delete_delay_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #2: Auto Typing =====
    var_auto_typing = tk.BooleanVar(value=_active_features().get("auto_typing", False))
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
    entry_typing_min.insert(0, str(_active_features().get("typing_min_sec", 2)))

    tk.Label(
        typing_row,
        text=language.t("features_page.typing_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_typing_max = create_styled_entry(typing_row, width=6)
    entry_typing_max.master.pack(side="left", padx=6)
    entry_typing_max.insert(0, str(_active_features().get("typing_max_sec", 5)))

    tk.Label(
        body_typing,
        text=language.t("features_page.typing_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #3: Auto Break =====
    var_auto_break = tk.BooleanVar(value=_active_features().get("auto_break", False))
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
    entry_break_after_min.insert(0, str(_active_features().get("break_after_min", 15)))

    tk.Label(
        break_after_row,
        text=language.t("features_page.break_after_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_after_max = create_styled_entry(break_after_row, width=6)
    entry_break_after_max.master.pack(side="left", padx=6)
    entry_break_after_max.insert(0, str(_active_features().get("break_after_max", 25)))

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
    entry_break_duration_min.insert(0, str(_active_features().get("break_duration_min", 10)))

    tk.Label(
        break_dur_row,
        text=language.t("features_page.break_duration_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_break_duration_max = create_styled_entry(break_dur_row, width=6)
    entry_break_duration_max.master.pack(side="left", padx=6)
    entry_break_duration_max.insert(0, str(_active_features().get("break_duration_max", 30)))

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
    var_auto_stop_ban = tk.BooleanVar(value=_active_features().get("auto_stop_on_ban", True))
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
    var_schedule = tk.BooleanVar(value=_active_features().get("schedule", False))
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
    entry_schedule_start.insert(0, str(_active_features().get("schedule_start", "09:00")))

    tk.Label(
        sched_row,
        text=language.t("features_page.schedule_to"),
        bg=t["bg_panel"],
        fg=t["text_secondary"],
        font=FONT_BODY
    ).pack(side="left")

    _, entry_schedule_end = create_styled_entry(sched_row, width=6)
    entry_schedule_end.master.pack(side="left", padx=6)
    entry_schedule_end.insert(0, str(_active_features().get("schedule_end", "17:00")))

    tk.Label(
        body_sched,
        text=language.t("features_page.schedule_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    ).pack(anchor="w")

    # ===== TÍNH NĂNG #6: Smart Templates =====
    var_smart_templates = tk.BooleanVar(value=_active_features().get("smart_templates", False))
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
    # Sound để chung toàn app, không tách theo token để khỏi loạn chuông.
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

    def _to_int(entry, default=0):
        try:
            return max(0, int(str(entry.get()).strip() or default))
        except ValueError:
            return default

    def save_to_active_profile():
        """Ghi toàn bộ tab Tính năng vào features của profile đang chọn."""
        try:
            feats = _active_features()
            if not isinstance(feats, dict):
                return False
            feats["auto_delete"] = bool(var_auto_delete.get())
            feats["delete_delay_ms"] = _to_int(entry_delete_delay, 0)
            feats["auto_typing"] = bool(var_auto_typing.get())
            feats["typing_min_sec"] = _to_int(entry_typing_min, 2)
            feats["typing_max_sec"] = _to_int(entry_typing_max, 5)
            feats["auto_break"] = bool(var_auto_break.get())
            feats["break_after_min"] = _to_int(entry_break_after_min, 15)
            feats["break_after_max"] = _to_int(entry_break_after_max, 25)
            feats["break_duration_min"] = _to_int(entry_break_duration_min, 10)
            feats["break_duration_max"] = _to_int(entry_break_duration_max, 30)
            feats["auto_stop_on_ban"] = bool(var_auto_stop_ban.get())
            feats["schedule"] = bool(var_schedule.get())
            feats["schedule_start"] = entry_schedule_start.get().strip() or "09:00"
            feats["schedule_end"] = entry_schedule_end.get().strip() or "17:00"
            feats["smart_templates"] = bool(var_smart_templates.get())
            feats["sound_enabled"] = bool(var_sound_enabled.get())
            feats["sound_error"] = bool(var_sound_error.get())
            feats["sound_stop"] = bool(var_sound_stop.get())
            feats["sound_success"] = bool(var_sound_success.get())
            # Sound vẫn sync về global để các module cũ đọc được
            config_data.setdefault("features", {}).update({
                "sound_enabled": feats["sound_enabled"],
                "sound_error": feats["sound_error"],
                "sound_stop": feats["sound_stop"],
                "sound_success": feats["sound_success"],
            })
            return True
        except Exception:
            return False

    _ui_loading = {"flag": False}

    def reload_from_active_profile():
        """Load lại tab Tính năng từ profile đang chọn (gọi khi đổi acc)."""
        _ui_loading["flag"] = True
        try:
            feats = _active_features()
            var_auto_delete.set(bool(feats.get("auto_delete", False)))
            entry_delete_delay.delete(0, tk.END)
            entry_delete_delay.insert(0, str(feats.get("delete_delay_ms", 0)))
            var_auto_typing.set(bool(feats.get("auto_typing", False)))
            entry_typing_min.delete(0, tk.END)
            entry_typing_min.insert(0, str(feats.get("typing_min_sec", 2)))
            entry_typing_max.delete(0, tk.END)
            entry_typing_max.insert(0, str(feats.get("typing_max_sec", 5)))
            var_auto_break.set(bool(feats.get("auto_break", False)))
            entry_break_after_min.delete(0, tk.END)
            entry_break_after_min.insert(0, str(feats.get("break_after_min", 15)))
            entry_break_after_max.delete(0, tk.END)
            entry_break_after_max.insert(0, str(feats.get("break_after_max", 25)))
            entry_break_duration_min.delete(0, tk.END)
            entry_break_duration_min.insert(0, str(feats.get("break_duration_min", 10)))
            entry_break_duration_max.delete(0, tk.END)
            entry_break_duration_max.insert(0, str(feats.get("break_duration_max", 30)))
            var_auto_stop_ban.set(bool(feats.get("auto_stop_on_ban", True)))
            var_schedule.set(bool(feats.get("schedule", False)))
            entry_schedule_start.delete(0, tk.END)
            entry_schedule_start.insert(0, str(feats.get("schedule_start", "09:00")))
            entry_schedule_end.delete(0, tk.END)
            entry_schedule_end.insert(0, str(feats.get("schedule_end", "17:00")))
            var_smart_templates.set(bool(feats.get("smart_templates", False)))
            refresh_profile_banner()
            return True
        except Exception:
            return False
        finally:
            _ui_loading["flag"] = False

    frame_features_page.save_to_active_profile = save_to_active_profile
    frame_features_page.reload_from_active_profile = reload_from_active_profile

    # ===== Tự lưu features của profile đang chọn mỗi khi tích/gõ =====
    # Nhờ vậy chuyển Acc 1 -> Acc 2 -> Acc 1 không mất setting đã tích.
    def _auto_save(*_args):
        if _ui_loading["flag"]:
            return
        save_to_active_profile()

    for _v in (var_auto_delete, var_auto_typing, var_auto_break, var_auto_stop_ban,
               var_schedule, var_smart_templates,
               var_sound_enabled, var_sound_error, var_sound_stop, var_sound_success):
        try:
            _v.trace_add("write", _auto_save)
        except Exception:
            pass

    for _e in (entry_delete_delay, entry_typing_min, entry_typing_max,
               entry_break_after_min, entry_break_after_max,
               entry_break_duration_min, entry_break_duration_max,
               entry_schedule_start, entry_schedule_end):
        _e.bind("<KeyRelease>", _auto_save)
        _e.bind("<FocusOut>", _auto_save)

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