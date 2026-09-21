# ui/features_page.py
# Trang tính năng - Scrollable với nhiều checkboxes và entries
# Author: bluemanhst

import tkinter as tk
from utils.constants import BG_DARK, BG_PANEL, TXT_GOLD, TXT_WHITE, FONT_LABEL, FONT_ENTRY, BTN_RED
from config import config_data
import language


def create_features_page(root):
    """
    Tạo trang tính năng với scrollable frame
    
    Args:
        root: Root window
    
    Returns:
        tuple: (frame_features_page, các biến UI)
    """
    # Frame chính của trang
    frame_features_page = tk.Frame(root, bg=BG_DARK)
    
    # Frame chứa các tính năng (có thanh cuộn)
    frame_scroll_container = tk.Frame(frame_features_page, bg=BG_DARK)
    frame_scroll_container.pack(fill="both", expand=True, padx=15, pady=10)

    # Canvas và scrollbar cho scrollable
    canvas_features = tk.Canvas(frame_scroll_container, bg=BG_PANEL, highlightthickness=0)
    scrollbar_features = tk.Scrollbar(frame_scroll_container, orient="vertical", command=canvas_features.yview)
    canvas_features.pack(side="left", fill="both", expand=True)
    scrollbar_features.pack(side="right", fill="y")
    canvas_features.configure(yscrollcommand=scrollbar_features.set)

    # Frame chứa nội dung
    frame_feature_options = tk.Frame(canvas_features, bg=BG_PANEL, bd=2, relief="ridge")
    canvas_features_window = canvas_features.create_window((0, 0), window=frame_feature_options, anchor="nw")

    # Event handlers cho scroll
    def _on_feature_frame_configure(event):
        canvas_features.configure(scrollregion=canvas_features.bbox("all"))
    frame_feature_options.bind("<Configure>", _on_feature_frame_configure)

    def _on_features_canvas_configure(event):
        canvas_features.itemconfig(canvas_features_window, width=event.width)
    canvas_features.bind("<Configure>", _on_features_canvas_configure)

    def _on_features_mousewheel(event):
        if frame_features_page.winfo_ismapped():
            canvas_features.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas_features.bind_all("<MouseWheel>", _on_features_mousewheel)

    # ===== TÍNH NĂNG #1: Auto Delete =====
    var_auto_delete = tk.BooleanVar(value=config_data.get("features", {}).get("auto_delete", False))
    chk_auto_delete = tk.Checkbutton(frame_feature_options, text=language.t("features_page.auto_delete"),
                                  variable=var_auto_delete, bg=BG_PANEL, fg=TXT_WHITE,
                                  selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_auto_delete.pack(anchor="w", padx=10, pady=8)

    frame_delete_delay = tk.Frame(frame_feature_options, bg=BG_PANEL)
    frame_delete_delay.pack(anchor="w", padx=30, pady=(0, 8), fill="x")

    tk.Label(frame_delete_delay, text=language.t("features_page.delete_delay_label"), 
           bg=BG_PANEL, fg=TXT_WHITE, font=FONT_LABEL).pack(anchor="w")
    entry_delete_delay = tk.Entry(frame_delete_delay, width=15, bg=BG_DARK, fg=TXT_WHITE, 
                               insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_delete_delay.pack(anchor="w", pady=4)
    entry_delete_delay.insert(0, str(config_data.get("features", {}).get("delete_delay_ms", 0)))

    lbl_delay_hint = tk.Label(
        frame_delete_delay,
        text=language.t("features_page.delete_delay_hint"),
        bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 8, "italic"), justify="left"
    )
    lbl_delay_hint.pack(anchor="w", pady=(0, 4))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #2: Auto Typing =====
    var_auto_typing = tk.BooleanVar(value=config_data.get("features", {}).get("auto_typing", False))
    chk_auto_typing = tk.Checkbutton(frame_feature_options, text=language.t("features_page.auto_typing"),
                                  variable=var_auto_typing, bg=BG_PANEL, fg=TXT_WHITE,
                                  selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_auto_typing.pack(anchor="w", padx=10, pady=8)

    frame_typing = tk.Frame(frame_feature_options, bg=BG_PANEL)
    frame_typing.pack(anchor="w", padx=30, pady=(0, 8), fill="x")

    frame_typing_time = tk.Frame(frame_typing, bg=BG_PANEL)
    frame_typing_time.pack(anchor="w")
    tk.Label(frame_typing_time, text=language.t("features_page.typing_range_label"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=0, sticky="w")
    entry_typing_min = tk.Entry(frame_typing_time, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                               insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_typing_min.grid(row=0, column=1, padx=5)
    entry_typing_min.insert(0, str(config_data.get("features", {}).get("typing_min_sec", 2)))
    tk.Label(frame_typing_time, text=language.t("features_page.typing_to"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=2)
    entry_typing_max = tk.Entry(frame_typing_time, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                               insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_typing_max.grid(row=0, column=3, padx=5)
    entry_typing_max.insert(0, str(config_data.get("features", {}).get("typing_max_sec", 5)))

    tk.Label(frame_typing, text=language.t("features_page.typing_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 8, "italic"), justify="left").pack(anchor="w", pady=(4, 0))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #3: Auto Break =====
    var_auto_break = tk.BooleanVar(value=config_data.get("features", {}).get("auto_break", False))
    chk_auto_break = tk.Checkbutton(frame_feature_options, text=language.t("features_page.auto_break"),
                                   variable=var_auto_break, bg=BG_PANEL, fg=TXT_WHITE,
                                   selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_auto_break.pack(anchor="w", padx=10, pady=8)

    frame_break = tk.Frame(frame_feature_options, bg=BG_PANEL)
    frame_break.pack(anchor="w", padx=30, pady=(0, 8), fill="x")

    frame_break_after = tk.Frame(frame_break, bg=BG_PANEL)
    frame_break_after.pack(anchor="w")
    tk.Label(frame_break_after, text=language.t("features_page.break_after_label"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=0, sticky="w")
    entry_break_after_min = tk.Entry(frame_break_after, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                     insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_break_after_min.grid(row=0, column=1, padx=5)
    entry_break_after_min.insert(0, str(config_data.get("features", {}).get("break_after_min", 15)))
    tk.Label(frame_break_after, text=language.t("features_page.break_after_to"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=2)
    entry_break_after_max = tk.Entry(frame_break_after, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                     insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_break_after_max.grid(row=0, column=3, padx=5)
    entry_break_after_max.insert(0, str(config_data.get("features", {}).get("break_after_max", 25)))
    tk.Label(frame_break_after, text=language.t("features_page.break_after_end"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=4, padx=(5, 0))

    frame_break_duration = tk.Frame(frame_break, bg=BG_PANEL)
    frame_break_duration.pack(anchor="w", pady=(6, 0))
    tk.Label(frame_break_duration, text=language.t("features_page.break_duration_label"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=0, sticky="w")
    entry_break_duration_min = tk.Entry(frame_break_duration, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                        insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_break_duration_min.grid(row=0, column=1, padx=5)
    entry_break_duration_min.insert(0, str(config_data.get("features", {}).get("break_duration_min", 10)))
    tk.Label(frame_break_duration, text=language.t("features_page.break_duration_to"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=2)
    entry_break_duration_max = tk.Entry(frame_break_duration, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                        insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_break_duration_max.grid(row=0, column=3, padx=5)
    entry_break_duration_max.insert(0, str(config_data.get("features", {}).get("break_duration_max", 30)))
    tk.Label(frame_break_duration, text=language.t("features_page.break_duration_end"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=4, padx=(5, 0))

    tk.Label(frame_break, text=language.t("features_page.break_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 8, "italic"), justify="left").pack(anchor="w", pady=(6, 0))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #4: Auto Stop on Ban =====
    var_auto_stop_ban = tk.BooleanVar(value=config_data.get("features", {}).get("auto_stop_on_ban", True))
    chk_auto_stop_ban = tk.Checkbutton(frame_feature_options, text=language.t("features_page.auto_stop_ban"),
                                      variable=var_auto_stop_ban, bg=BG_PANEL, fg=TXT_WHITE,
                                      selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_auto_stop_ban.pack(anchor="w", padx=10, pady=8)

    tk.Label(frame_feature_options,
           text=language.t("features_page.auto_stop_ban_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 8, "italic"), justify="left").pack(anchor="w", padx=30, pady=(0, 8))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #5: Schedule =====
    var_schedule = tk.BooleanVar(value=config_data.get("features", {}).get("schedule", False))
    chk_schedule = tk.Checkbutton(frame_feature_options, text=language.t("features_page.schedule"),
                               variable=var_schedule, bg=BG_PANEL, fg=TXT_WHITE,
                               selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_schedule.pack(anchor="w", padx=10, pady=8)

    frame_schedule = tk.Frame(frame_feature_options, bg=BG_PANEL)
    frame_schedule.pack(anchor="w", padx=30, pady=(0, 8), fill="x")

    frame_schedule_time = tk.Frame(frame_schedule, bg=BG_PANEL)
    frame_schedule_time.pack(anchor="w")
    tk.Label(frame_schedule_time, text=language.t("features_page.schedule_from"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=0, sticky="w")
    entry_schedule_start = tk.Entry(frame_schedule_time, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                    insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_schedule_start.grid(row=0, column=1, padx=5)
    entry_schedule_start.insert(0, str(config_data.get("features", {}).get("schedule_start", "09:00")))
    tk.Label(frame_schedule_time, text=language.t("features_page.schedule_to"), bg=BG_PANEL, fg=TXT_WHITE, 
           font=FONT_LABEL).grid(row=0, column=2)
    entry_schedule_end = tk.Entry(frame_schedule_time, width=6, bg=BG_DARK, fg=TXT_WHITE, 
                                  insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_schedule_end.grid(row=0, column=3, padx=5)
    entry_schedule_end.insert(0, str(config_data.get("features", {}).get("schedule_end", "17:00")))

    tk.Label(frame_schedule, text=language.t("features_page.schedule_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 8, "italic"), justify="left").pack(anchor="w", pady=(4, 0))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #6: Smart Templates =====
    var_smart_templates = tk.BooleanVar(value=config_data.get("features", {}).get("smart_templates", False))
    chk_smart_templates = tk.Checkbutton(frame_feature_options, text=language.t("features_page.smart_templates"),
                                        variable=var_smart_templates, bg=BG_PANEL, fg=TXT_WHITE,
                                        selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_smart_templates.pack(anchor="w", padx=10, pady=8)
    
    # Nút xem chi tiết
    btn_smart_templates_info = tk.Button(frame_feature_options, text=language.t("features_page.smart_templates_btn"),
                                       bg="#2196F3", fg=TXT_WHITE, font=("Arial", 9, "bold"),
                                       activebackground="#1976D2", activeforeground=TXT_WHITE, bd=2,
                                       command=show_smart_templates_info)
    btn_smart_templates_info.pack(anchor="w", padx=10, pady=(0, 8))

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL).pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    # ===== TÍNH NĂNG #7: Sound Notifications =====
    var_sound_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("sound_enabled", False))
    chk_sound = tk.Checkbutton(frame_feature_options, text=language.t("features_page.sound_enabled"),
                             variable=var_sound_enabled, bg=BG_PANEL, fg=TXT_WHITE,
                             selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL)
    chk_sound.pack(anchor="w", padx=10, pady=8)

    frame_sound = tk.Frame(frame_feature_options, bg=BG_PANEL)
    frame_sound.pack(anchor="w", padx=30, pady=(0, 8), fill="x")

    # ===== CÁC LOẠI ÂM THANH (bật/tắt riêng từng loại) =====
    var_sound_error = tk.BooleanVar(value=config_data.get("features", {}).get("sound_error", True))
    var_sound_stop = tk.BooleanVar(value=config_data.get("features", {}).get("sound_stop", True))
    var_sound_success = tk.BooleanVar(value=config_data.get("features", {}).get("sound_success", True))

    sound_options = [
        ("features_page.sound_error", var_sound_error),
        ("features_page.sound_stop", var_sound_stop),
        ("features_page.sound_success", var_sound_success)
    ]

    for label_key, sound_var in sound_options:
        chk_opt = tk.Checkbutton(frame_sound, text="• " + language.t(label_key), variable=sound_var,
                               bg=BG_PANEL, fg="#AAAAAA", selectcolor=BG_PANEL,
                               font=("Arial", 8), activebackground=BG_PANEL)
        chk_opt.pack(anchor="w", padx=5)

    # Dòng phân cách
    tk.Label(frame_feature_options, text="", bg=BG_PANEL). pack(pady=2)
    tk.Label(frame_feature_options, text="─" * 60, bg=BG_PANEL, fg="#555555").pack(pady=5)

    return (frame_features_page, 
            var_auto_delete, entry_delete_delay,
            var_auto_typing, entry_typing_min, entry_typing_max,
            var_auto_break, entry_break_after_min, entry_break_after_max, 
            entry_break_duration_min, entry_break_duration_max,
            var_auto_stop_ban,
            var_schedule, entry_schedule_start, entry_schedule_end,
            var_smart_templates,
            var_sound_enabled, var_sound_error, var_sound_stop, var_sound_success)


def show_smart_templates_info():
    """
    Hiển thị popup giải thích chi tiết về random hóa tin nhắn
    """
    from tkinter import Toplevel, scrolledtext
    
    # Tạo cửa sổ popup
    info_window = Toplevel()
    info_window.title(language.t("features_page.smart_templates_title"))
    info_window.geometry("560x520")
    info_window.configure(bg=BG_DARK)
    
    # Frame chứa nội dung
    frame_content = tk.Frame(info_window, bg=BG_DARK)
    frame_content.pack(fill="both", expand=True, padx=15, pady=15)
    
    # Tiêu đề
    tk.Label(frame_content, text=language.t("features_page.smart_templates_title"), 
           bg=BG_DARK, fg=TXT_GOLD, font=("Arial", 11, "bold")).pack(pady=8)
    
    # Scrollable text cho nội dung
    info_text = scrolledtext.ScrolledText(frame_content, height=18, bg=BG_PANEL, fg=TXT_WHITE, 
                                       font=("Arial", 9), wrap="word")
    info_text.pack(fill="both", expand=True, pady=8)
    
    # Nội dung giải thích
    explanation = language.t("features_page.smart_templates_content")
    
    info_text.insert("1.0", explanation)
    info_text.config(state="disabled")
    
    # Nút dong
    tk.Button(frame_content, text=language.t("features_page.smart_templates_close"), command=info_window.destroy,
             bg=BTN_RED, fg=TXT_WHITE, font=("Arial", 10, "bold"), bd=2).pack(pady=8)