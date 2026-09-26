# ui/settings_page.py
# Trang cài đặt - Minimize to tray, Sound settings, Startup, Language
# Author: bluemanhst

import tkinter as tk
import os
import sys
from tkinter import messagebox, ttk
from utils.tray import TRAY_AVAILABLE
from utils.theme import (
    get_theme, create_card_frame, create_section_header,
    FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION
)
from config import config_data, save_config
import language


def create_settings_page(root, bot_running_ref, stop_trigger_func, tray_manager=None):
    """
    Tạo trang cài đặt với các section card hiện đại, rõ ràng.
    
    Args:
        root: Root window
        bot_running_ref: Reference đến list [bot_running] để thread-safe
        stop_trigger_func: Hàm để dừng bot
        tray_manager: Đối tượng TrayManager để quản lý icon khay hệ thống
    
    Returns:
        tuple: (frame_settings_page, var_tray_enabled, var_startup_enabled, language_var)
    """
    t = get_theme()

    frame_settings_page = tk.Frame(root, bg=t["bg_app"])

    container = tk.Frame(frame_settings_page, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    # ===== SECTION 1: SYSTEM & STARTUP =====
    card_sys, sys_inner = create_card_frame(container, padx=20, pady=16)
    card_sys.pack(fill="x", pady=(0, 14))

    create_section_header(
        sys_inner,
        title=language.t("navigation.settings"),
        subtitle=language.t("settings_page.section_system_subtitle")
    )

    # 1. Startup with Windows
    var_startup_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("startup_enabled", False))

    def toggle_startup_wrapper():
        toggle_startup(var_startup_enabled)

    chk_startup = tk.Checkbutton(
        sys_inner,
        text=language.t("settings_page.startup_enabled"),
        variable=var_startup_enabled,
        bg=t["bg_panel"],
        fg=t["text_primary"],
        selectcolor=t["bg_input"],
        activebackground=t["bg_panel"],
        activeforeground=t["text_primary"],
        font=FONT_BODY_BOLD,
        command=toggle_startup_wrapper,
        cursor="hand2"
    )
    chk_startup.pack(anchor="w", pady=(4, 2))

    lbl_startup_hint = tk.Label(
        sys_inner,
        text=language.t("settings_page.startup_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    )
    lbl_startup_hint.pack(anchor="w", padx=24, pady=(0, 12))

    # Divider line
    div1 = tk.Frame(sys_inner, bg=t["border_subtle"], height=1)
    div1.pack(fill="x", pady=8)

    # 2. Minimize to Tray
    var_tray_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("tray_enabled", False))

    def on_tray_toggle():
        if var_tray_enabled.get():
            if tray_manager is not None and tray_manager.start():
                tray_manager.notify(language.t("settings_page.tray_notification"), "Discord BLUE")
            else:
                var_tray_enabled.set(False)
                messagebox.showwarning(
                    language.t("settings_page.tray_unavailable_title"),
                    language.t("settings_page.tray_unavailable_msg")
                )
        elif tray_manager is not None:
            tray_manager.stop()

    chk_tray = tk.Checkbutton(
        sys_inner,
        text=language.t("settings_page.tray_enabled"),
        variable=var_tray_enabled,
        bg=t["bg_panel"],
        fg=t["text_primary"],
        selectcolor=t["bg_input"],
        activebackground=t["bg_panel"],
        activeforeground=t["text_primary"],
        font=FONT_BODY_BOLD,
        command=on_tray_toggle,
        cursor="hand2"
    )
    chk_tray.pack(anchor="w", pady=(8, 2))

    lbl_tray_hint = tk.Label(
        sys_inner,
        text=language.t("settings_page.tray_hint"),
        bg=t["bg_panel"],
        fg=t["text_muted"],
        font=FONT_CAPTION,
        justify="left"
    )
    lbl_tray_hint.pack(anchor="w", padx=24, pady=(0, 4))

    if not TRAY_AVAILABLE:
        lbl_tray_warn = tk.Label(
            sys_inner,
            text="⚠️ " + language.t("settings_page.tray_unavailable_msg"),
            bg=t["bg_panel"],
            fg=t["danger"],
            font=FONT_BODY_BOLD,
            justify="left"
        )
        lbl_tray_warn.pack(anchor="w", padx=24, pady=(4, 0))

    # ===== SECTION 2: LANGUAGE SELECTION =====
    card_lang, lang_inner = create_card_frame(container, padx=20, pady=16)
    card_lang.pack(fill="x")

    create_section_header(
        lang_inner,
        title=language.t("settings_page.language_label"),
        subtitle=language.t("settings_page.section_language_subtitle")
    )

    supported_languages = language.get_supported_languages()
    language_options = [f"{code} - {name}" for code, name in supported_languages.items()]

    current_lang = config_data.get("language", "vietnamese")
    initial_language_val = f"{current_lang} - {supported_languages.get(current_lang, current_lang)}"
    language_var = tk.StringVar(value=initial_language_val)

    language_combo = ttk.Combobox(
        lang_inner,
        textvariable=language_var,
        values=language_options,
        state="readonly",
        font=FONT_BODY
    )
    language_combo.pack(fill="x", pady=(4, 8))

    def on_language_change(event):
        selected = language_var.get()
        if selected:
            language_code = selected.split(" - ")[0]
            if language.set_language(language_code):
                messagebox.showinfo(
                    language.t("common.success_title"),
                    language.t("settings_page.language_changed_msg",
                               language.get_language_name(language_code))
                )

    language_combo.bind("<<ComboboxSelected>>", on_language_change)

    # ===== XỬ LÝ ĐÓNG CỬA SỔ =====
    def quit_application():
        if bot_running_ref[0]:
            if not messagebox.askyesno(
                language.t("settings_page.confirm_exit"),
                language.t("settings_page.confirm_exit_msg")
            ):
                return
            stop_trigger_func()

        if tray_manager is not None:
            tray_manager.stop()
        root.destroy()

    def on_closing():
        tray_ready = (var_tray_enabled.get() and tray_manager is not None and tray_manager.running)
        if tray_ready:
            root.withdraw()
            tray_manager.notify(language.t("settings_page.tray_notification"), "Discord BLUE")
        else:
            quit_application()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    return frame_settings_page, var_tray_enabled, var_startup_enabled, language_var


def toggle_startup(var_startup):
    """Toggle startup with Windows (User hive - không cần quyền Admin)"""
    try:
        import winreg

        if getattr(sys, 'frozen', False):
            command_str = f'"{sys.executable}"'
        else:
            exe_path = os.path.abspath(sys.argv[0])
            command_str = f'"{sys.executable}" "{exe_path}"'

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "DiscordBLUE"

        access_rights = winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, access_rights)

        try:
            winreg.QueryValueEx(key, app_name)
            winreg.DeleteValue(key, app_name)
            config_data.setdefault("features", {})["startup_enabled"] = False
            save_config(config_data)
            var_startup.set(False)
            messagebox.showinfo("Startup", language.t("settings_page.startup_removed"))
        except FileNotFoundError:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command_str)
            config_data.setdefault("features", {})["startup_enabled"] = True
            save_config(config_data)
            var_startup.set(True)
            messagebox.showinfo("Startup", language.t("settings_page.startup_added"))
        finally:
            winreg.CloseKey(key)

    except Exception as e:
        messagebox.showerror("Lỗi", f"{language.t('settings_page.startup_error')} {str(e)}")
        var_startup.set(config_data.get("features", {}).get("startup_enabled", False))
