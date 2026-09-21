# ui/settings_page.py
# Trang cài đặt - Minimize to tray, Sound settings, Startup, Language
# Author: bluemanhst

import tkinter as tk
import os
import sys
from tkinter import messagebox, ttk
from utils.constants import BG_PANEL, TXT_WHITE, FONT_LABEL
from utils.tray import TRAY_AVAILABLE
from config import config_data, save_config
import language


def create_settings_page(root, bot_running_ref, stop_trigger_func, tray_manager=None):
    """
    Tạo trang cài đặt với minimize to tray, sound và startup
    
    Args:
        root: Root window
        bot_running_ref: Reference đến list [bot_running] để thread-safe
        stop_trigger_func: Hàm để dừng bot
        tray_manager: Đối tượng TrayManager (do main.pyw tạo) để quản lý icon khay hệ thống
    
    Returns:
        tuple: (frame_settings_page, var_tray_enabled, var_startup_enabled)
    """
    # Frame chính của trang
    frame_settings_page = tk.Frame(root, bg=BG_PANEL)

    # Frame chứa cài đặt
    frame_settings_main = tk.Frame(frame_settings_page, bg=BG_PANEL, bd=2, relief="ridge")
    frame_settings_main.pack(fill="both", expand=True, padx=15, pady=10)

    # ===== Startup with Windows =====
    var_startup_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("startup_enabled", False))
    
    def toggle_startup_wrapper():
        """Bật/tắt khởi động cùng Windows"""
        toggle_startup(var_startup_enabled)
    
    chk_startup = tk.Checkbutton(frame_settings_main, text=language.t("settings_page.startup_enabled"),
                               variable=var_startup_enabled, bg=BG_PANEL, fg=TXT_WHITE,
                               selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL,
                               command=toggle_startup_wrapper)
    chk_startup.pack(anchor="w", padx=30, pady=20)

    frame_startup = tk.Frame(frame_settings_main, bg=BG_PANEL)
    frame_startup.pack(anchor="w", padx=30, pady=(0, 20), fill="x")

    tk.Label(frame_startup, text=language.t("settings_page.startup_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 9), justify="left").pack(anchor="w")

    # ===== Minimize to Tray =====
    var_tray_enabled = tk.BooleanVar(value=config_data.get("features", {}).get("tray_enabled", False))

    def on_tray_toggle():
        """Bật/tắt icon khay hệ thống ngay khi người dùng tích chọn"""
        if var_tray_enabled.get():
            if tray_manager is not None and tray_manager.start():
                tray_manager.notify(language.t("settings_page.tray_notification"), "Discord BLUE")
            else:
                # Không tạo được icon tray -> không cho bật (tránh mất cửa sổ)
                var_tray_enabled.set(False)
                messagebox.showwarning(language.t("settings_page.tray_unavailable_title"),
                                       language.t("settings_page.tray_unavailable_msg"))
        elif tray_manager is not None:
            tray_manager.stop()

    chk_tray = tk.Checkbutton(frame_settings_main, text=language.t("settings_page.tray_enabled"),
                            variable=var_tray_enabled, bg=BG_PANEL, fg=TXT_WHITE,
                            selectcolor=BG_PANEL, font=FONT_LABEL, activebackground=BG_PANEL,
                            command=on_tray_toggle)
    chk_tray.pack(anchor="w", padx=30, pady=20)

    frame_tray = tk.Frame(frame_settings_main, bg=BG_PANEL)
    frame_tray.pack(anchor="w", padx=30, pady=(0, 20), fill="x")

    tk.Label(frame_tray, text=language.t("settings_page.tray_hint"),
           bg=BG_PANEL, fg="#AAAAAA", font=("Arial", 9), justify="left").pack(anchor="w")

    if not TRAY_AVAILABLE:
        # Thiếu thư viện pystray -> nói rõ để người dùng không bật nhầm
        tk.Label(frame_tray, text="⚠️ " + language.t("settings_page.tray_unavailable_msg"),
               bg=BG_PANEL, fg="#FFAA00", font=("Arial", 9, "bold"),
               justify="left").pack(anchor="w", pady=(4, 0))

    # ===== Language Selection =====
    frame_language = tk.Frame(frame_settings_main, bg=BG_PANEL, bd=2, relief="ridge")
    frame_language.pack(fill="x", padx=30, pady=20)

    tk.Label(frame_language, text=language.t("settings_page.language_label"), 
           bg=BG_PANEL, fg=TXT_WHITE, font=FONT_LABEL).pack(anchor="w", padx=10, pady=10)

    # Get supported languages
    supported_languages = language.get_supported_languages()
    language_options = [f"{code} - {name}" for code, name in supported_languages.items()]
    
    # Language dropdown
    current_lang = config_data.get("language", "vietnamese")
    initial_language_val = f"{current_lang} - {supported_languages.get(current_lang, current_lang)}"
    language_var = tk.StringVar(value=initial_language_val)
    
    language_combo = ttk.Combobox(frame_language, textvariable=language_var, 
                                  values=language_options, state="readonly",
                                  font=("Arial", 10))
    language_combo.pack(fill="x", padx=10, pady=5)
    
    def on_language_change(event):
        """Xử lý khi đổi ngôn ngữ"""
        selected = language_var.get()
        if selected:
            # Extract language code from format "code - name"
            language_code = selected.split(" - ")[0]
            if language.set_language(language_code):
                messagebox.showinfo("Thành công", f"Đã đổi ngôn ngữ thành {language.get_language_name(language_code)}!\n\nVui lòng restart ứng dụng để áp dụng thay đổi.")
    
    language_combo.bind("<<ComboboxSelected>>", on_language_change)

    # ===== XỬ LÝ ĐÓNG CỬA SỔ =====
    def quit_application():
        """Thoát hoàn toàn ứng dụng (có xác nhận nếu bot đang chạy)"""
        if bot_running_ref[0]:
            if not messagebox.askyesno(language.t("settings_page.confirm_exit"),
                                       language.t("settings_page.confirm_exit_msg")):
                return
            stop_trigger_func()

        if tray_manager is not None:
            tray_manager.stop()
        root.destroy()

    def on_closing():
        """Đóng cửa sổ: ẩn xuống khay hệ thống nếu tray đang bật và có icon thật"""
        tray_ready = (var_tray_enabled.get() and tray_manager is not None
                      and tray_manager.running)
        if tray_ready:
            # Ẩn cửa sổ - vẫn mở lại được từ icon dưới khay hệ thống
            root.withdraw()
            tray_manager.notify(language.t("settings_page.tray_notification"), "Discord BLUE")
        else:
            quit_application()

    # Bind closing event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    return frame_settings_page, var_tray_enabled, var_startup_enabled, language_var


def toggle_startup(var_startup):
    """Toggle startup with Windows"""
    try:
        import winreg
        
        # Đường dẫn/lệnh thực thi của app
        if getattr(sys, 'frozen', False):
            command_str = f'"{sys.executable}"'
        else:
            exe_path = os.path.abspath(sys.argv[0])
            command_str = f'"{sys.executable}" "{exe_path}"'
        
        # Registry key for startup (User hive - không cần quyền Admin)
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "DiscordBLUE"
        
        # Mở registry key với quyền đọc và ghi giá trị
        access_rights = winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, access_rights)
        
        try:
            # Kiểm tra xem đã có trong startup chưa
            winreg.QueryValueEx(key, app_name)
            # Đã có -> Xóa khỏi startup
            winreg.DeleteValue(key, app_name)
            config_data.setdefault("features", {})["startup_enabled"] = False
            save_config(config_data)
            var_startup.set(False)
            messagebox.showinfo("Startup", language.t("settings_page.startup_removed"))
        except FileNotFoundError:
            # Chưa có -> Thêm vào startup
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command_str)
            config_data.setdefault("features", {})["startup_enabled"] = True
            save_config(config_data)
            var_startup.set(True)
            messagebox.showinfo("Startup", language.t("settings_page.startup_added"))
        finally:
            winreg.CloseKey(key)
        
    except Exception as e:
        messagebox.showerror("Lỗi", f"{language.t('settings_page.startup_error')} {str(e)}")
        # Reset checkbox về trạng thái cũ nếu có lỗi
        var_startup.set(config_data.get("features", {}).get("startup_enabled", False))
