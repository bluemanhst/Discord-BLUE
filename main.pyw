# main.pyw
# Entry point của ứng dụng - Khởi tạo và chạy GUI
# Author: bluemanhst
# App Name: Discord BLUE

import tkinter as tk
from tkinter import messagebox
import threading
import sys
import os
from datetime import datetime

# Import config trước để load theme
from config import config_data, save_config
import language

# Tiện ích: log an toàn + âm thanh + tray (đường dẫn icon lấy từ utils.constants.APP_ICON)
from utils.helpers import ThreadSafeLog
from utils.sound import set_all as set_sound_enabled, notify as notify_sound
from utils.tray import TrayManager

# Load theme từ config TRƯỚC khi import các module UI
# (các module UI lấy màu qua utils.theme.get_theme() nên phải chốt theme trước)
from utils.theme import (
    THEMES, DEFAULT_THEME_NAME, ThemeManager, configure_ttk_styles, get_theme
)

saved_theme_name = config_data.get("current_theme", DEFAULT_THEME_NAME)
theme_mgr = ThemeManager.get_instance()
if saved_theme_name in THEMES:
    theme_mgr.set_theme(saved_theme_name)
else:
    # Config chứa tên theme cũ/không hợp lệ -> quay về theme mặc định (ghi file khi user lưu cấu hình)
    theme_mgr.set_theme(DEFAULT_THEME_NAME)
    config_data["current_theme"] = DEFAULT_THEME_NAME

# Import các hằng số UI tĩnh (kích thước cửa sổ, icon) sau khi đã chốt theme
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WIDTH, MIN_HEIGHT, APP_ICON
from discord.bot import run_single_account
from discord.dashboard import dashboard
from ui.navigation import create_navigation_bar
from ui.main_page import (create_main_page, validate_tokens_widget, validate_channels_widget,
                          validate_token_list, validate_channel_items)
from ui.features_page import create_features_page
from ui.config_page import create_config_page
from ui.theme_page import create_theme_page
from ui.dashboard_page import create_dashboard_page
from ui.settings_page import create_settings_page
from ui.footer import create_footer

# ===== BIẾN TOÀN CỤC =====
bot_running = [False]        # Dùng list để thread-safe
bot_generation = [0]         # Tăng mỗi lần BẮT/DỪNG để vô hiệu hoá thread của lượt cũ
account_threads = []
current_theme = None         # Theme hiện tại
log_proxy = ThreadSafeLog()  # Cầu nối log an toàn cho các thread gửi tin

# Icon khay hệ thống - tạo sẵn để dùng chung cho cả app
tray_manager = TrayManager(
    icon_path=APP_ICON,
    title=language.t("app_name"),
    menu_show=language.t("settings_page.tray_menu_show"),
    menu_quit=language.t("settings_page.tray_menu_quit")
)

# ===== HÀM CHUYỂN TRANG =====
def _persist_features_and_config():
    """Ghi tab Tính năng vào profile đang chọn rồi lưu config.json."""
    try:
        profiles_ctx["save_current"]()
    except Exception:
        pass
    try:
        if hasattr(frame_features_page, "save_to_active_profile"):
            frame_features_page.save_to_active_profile()
    except Exception:
        pass
    try:
        save_config(config_data)
    except Exception:
        pass

def show_main_page():
    """Hiển thị trang chính"""
    _persist_features_and_config()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_main_page.pack(fill="both", expand=True)

def show_features_page():
    """Hiển thị trang tính năng"""
    try:
        profiles_ctx["save_current"]()
    except Exception:
        pass
    try:
        if hasattr(frame_features_page, "reload_from_active_profile"):
            frame_features_page.reload_from_active_profile()
        save_config(config_data)
    except Exception:
        pass
    frame_main_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_features_page.pack(fill="both", expand=True)

def show_config_page():
    """Hiển thị trang cấu hình"""
    try:
        save_config(config_data)
    except Exception:
        pass
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_config_page.pack(fill="both", expand=True)

def show_theme_page():
    """Hiển thị trang theme"""
    try:
        save_config(config_data)
    except Exception:
        pass
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_theme_page.pack(fill="both", expand=True)

def show_dashboard_page():
    """Hiển thị trang dashboard"""
    try:
        save_config(config_data)
    except Exception:
        pass
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_dashboard_page.pack(fill="both", expand=True)

def show_settings_page():
    """Hiển thị trang cài đặt"""
    try:
        save_config(config_data)
    except Exception:
        pass
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack(fill="both", expand=True)

# ===== HÀM BẬT TOOL =====
def start_trigger():
    """Bắt đầu chạy tool - mỗi profile/token chạy settings riêng."""
    global bot_running, bot_generation, account_threads
    warn_title = language.t("common.warning_title")
    if bot_running[0]:
        messagebox.showinfo(language.t("common.info_title"), language.t("main_page.info_running"))
        return

    try:
        from profiles import ensure_profiles
        profiles_ctx["save_current"]()
        if hasattr(frame_features_page, "save_to_active_profile"):
            frame_features_page.save_to_active_profile()
        profiles = ensure_profiles(config_data)
    except Exception:
        profiles = config_data.get("profiles", [])
    active_profiles = [p for p in profiles
                       if p.get("enabled", True) and str(p.get("token") or "").strip()]
    if not active_profiles:
        messagebox.showwarning(warn_title, language.t("main_page.warning_no_tokens"))
        return

    def _valid_channels(p):
        """Chỉ tính kênh có id thật; id rỗng ('') do normalize bù -> coi như thiếu."""
        ids = [c for c in (p.get("channels") or []) if str(c.get("id") or "").strip()]
        if ids:
            return ids
        return [c for c in (p.get("channel_ids") or []) if str(c or "").strip()]

    bad = [str(p.get("name") or "Acc") for p in active_profiles
           if not _valid_channels(p) or not p.get("messages")]
    if bad:
        messagebox.showwarning(warn_title, language.t("main_page.warning_no_channels"))
        return

    for prof in active_profiles:
        try:
            prof["cooldown_min"] = max(0, int(prof.get("cooldown_min", 60)))
            prof["cooldown_max"] = max(0, int(prof.get("cooldown_max", 90)))
        except (TypeError, ValueError):
            prof["cooldown_min"], prof["cooldown_max"] = 60, 90
        if prof["cooldown_min"] > prof["cooldown_max"]:
            messagebox.showwarning(warn_title, language.t("main_page.warning_cooldown_range"))
            return

    # Đồng bộ channel_ids từ fields channels mới (giữ tương thích validator + cấu hình cũ)
    for prof in active_profiles:
        if prof.get("channels"):
            prof["channel_ids"] = [c["id"] for c in prof["channels"]]

    # Giữ tương thích file cũ: sync profile đầu tiên về các key global
    try:
        first = active_profiles[0]
        config_data["tokens"] = [str(p.get("token") or "").strip() for p in active_profiles]
        config_data["channel_ids"] = list(first.get("channels") or first.get("channel_ids", []))
        config_data["cooldown_min"] = int(first.get("cooldown_min", 60))
        config_data["cooldown_max"] = int(first.get("cooldown_max", 90))
        config_data["custom_message"] = list(first.get("messages", ["Hello"]))
    except Exception:
        pass
    save_config(config_data)
    new_config = config_data

    # Cấu hình âm thanh thông báo (dùng chung cho UI và các thread gửi tin)
    sound_master = new_config["features"]["sound_enabled"]
    set_sound_enabled({
        "error": sound_master and new_config["features"]["sound_error"],
        "stop": sound_master and new_config["features"]["sound_stop"],
        "success": sound_master and new_config["features"]["sound_success"]
    })

    bot_running[0] = True
    bot_generation[0] += 1  # Vô hiệu hoá thread còn sót của lượt chạy trước
    current_run = bot_generation[0]
    account_threads = []

    # Bắt đầu theo dõi dashboard
    dashboard.start_tracking()

    total_channels = sum(len(p.get("channel_ids", [])) for p in active_profiles)
    log_area.insert(tk.END, "==================================================\n", "system")
    log_area.insert(tk.END, language.t("log_messages.system_start", len(active_profiles), total_channels), "system")
    # Dòng tóm tắt trạng thái các tính năng (dịch theo ngôn ngữ đang chọn)
    feature_status = {True: language.t("log_messages.on"), False: language.t("log_messages.off")}
    first_feats = active_profiles[0].get("features", {})
    first_schedule_start = str(first_feats.get("schedule_start", "09:00"))
    first_schedule_end = str(first_feats.get("schedule_end", "17:00"))
    feature_lines = [
        ("log_messages.feature_auto_delete", feature_status[bool(first_feats.get("auto_delete", False))]),
        ("log_messages.feature_auto_typing", feature_status[bool(first_feats.get("auto_typing", False))]),
        ("log_messages.feature_auto_break", feature_status[bool(first_feats.get("auto_break", False))]),
        ("log_messages.feature_auto_stop_ban", feature_status[bool(first_feats.get("auto_stop_on_ban", True))]),
        ("log_messages.feature_schedule", feature_status[bool(first_feats.get("schedule", False))],
         first_schedule_start, first_schedule_end),
        ("log_messages.feature_smart_templates",
         feature_status[bool(first_feats.get("smart_templates", False))])
    ]
    for line_key, *line_args in feature_lines:
        log_area.insert(tk.END, language.t(line_key, *line_args), "system")
    log_area.insert(tk.END, language.t("log_messages.profiles_running",
                                       ", ".join(str(p.get("name", "Acc"))
                                                for p in active_profiles)), "system")
    log_area.insert(tk.END, "==================================================\n", "system")

    for index, prof in enumerate(active_profiles, start=1):
        ch_list = list(prof.get("channels") or [])
        if not ch_list:
            ch_list = [{"id": c, "cd_min": int(prof.get("cooldown_min", 60)),
                        "cd_max": int(prof.get("cooldown_max", 90))}
                       for c in prof.get("channel_ids", [])]

        t = threading.Thread(target=run_single_account, args=(
            str(prof.get("token") or "").strip(), index, list(prof.get("channel_ids", [])),
            int(prof.get("cooldown_min", 60)), int(prof.get("cooldown_max", 90)),
            list(prof.get("messages", ["Hello"])), log_proxy,
            dict(prof.get("features", {})), bot_running
        ), kwargs={"run_id": current_run, "generation_ref": bot_generation,
            "channels": ch_list,
            "emoji_guilds": list(prof.get("emoji_guilds", []) or []),

                   "profile_name": str(prof.get("name") or f"Acc {index}")}, daemon=True)
        account_threads.append(t)
        t.start()

    lbl_status.config(text=language.t("main_page.status_running"),
                      fg=get_theme()["success"])

# ===== HÀM DỪNG TOOL =====
def stop_trigger():
    """Dừng tool"""
    bot_running[0] = False
    bot_generation[0] += 1  # Buộc mọi thread đang ngủ phải thoát ra ngay
    lbl_status.config(text=language.t("main_page.status_stopped"),
                      fg=get_theme()["danger"])
    log_area.insert(tk.END, language.t("log_messages.stopped"), "system")
    log_area.see(tk.END)
    notify_sound("stop")

    # Dashboard tự động dừng tracking khi bot_running = False


# ===== HÀM ĐỒNG BỘ LOG / TRAY VỚI LUỒNG CHÍNH =====
def pump_log_queue():
    """Ghi log mà các thread đã đẩy vào hàng đợi (chạy ở luồng chính Tkinter)"""
    log_proxy.drain(log_area)
    root.after(100, pump_log_queue)


def show_window_from_tray():
    """Mở lại cửa sổ khi bấm icon khay hệ thống"""
    root.deiconify()
    root.lift()
    root.focus_force()


def quit_from_tray():
    """Thoát ứng dụng từ menu của icon khay hệ thống"""
    _persist_features_and_config()
    stop_trigger()
    tray_manager.stop()
    root.destroy()


def pump_tray_commands():
    """Xử lý các lệnh bấm từ menu icon khay hệ thống (luồng chính Tkinter)"""
    tray_manager.drain(on_show=show_window_from_tray, on_quit=quit_from_tray)
    root.after(300, pump_tray_commands)

# ===== KHỞI TẠO ROOT WINDOW =====
root = tk.Tk()
root.withdraw()
root.title(f"{language.t('app_name')} -- ~/main")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.minsize(MIN_WIDTH, MIN_HEIGHT)
root.configure(bg=get_theme()["bg_app"])

# Titlebar toi mau (DWM immersive dark) - Windows 10/11; neu khong ho tro thi bo qua
try:
    import ctypes
    _hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    if _hwnd:
        _val = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            _hwnd, 20, ctypes.byref(_val), ctypes.sizeof(_val))
except Exception:
    pass

# ===== SPLASH SCREEN =====
# Chỉ hiện splash trước, ẩn hẳn cửa sổ chính cho tới khi splash đóng xong
from utils.splash_screen import show_splash_screen

# Hiển thị splash screen (tự động đóng sau khi đạt 100%)
_splash = show_splash_screen(root, None)
import time
if _splash is not None:
    try:
        while _splash.splash.winfo_exists():
            root.update()
            time.sleep(0.05)
    except Exception:
        pass

root.configure(bg=get_theme()["bg_app"])

# Áp dụng ttk styles đồng bộ
configure_ttk_styles(root)

# Load icon app (đường dẫn đã được utils.paths tính đúng cho cả source lẫn EXE)
if os.path.exists(APP_ICON):
    try:
        root.iconbitmap(APP_ICON)
    except Exception:
        pass  # Không load được icon thì bỏ qua, không ảnh hưởng tool

# ===== TẠO STATUS BAR (pack truoc sidebar de full-width, giong Roblox) =====
frame_footer = create_footer(root, bot_running)

# ===== TẠO NAVIGATION BAR =====
nav_bar = create_navigation_bar(root, show_main_page, show_features_page,
                                show_config_page, show_theme_page, show_dashboard_page, show_settings_page)

# ===== TẠO CÁC TRANG =====
# Trang chính (kèm panel Profiles Master-Detail)
def _on_profile_changed_from_panel():
    try:
        if "frame_features_page" in dir() and hasattr(frame_features_page, "reload_from_active_profile"):
            frame_features_page.reload_from_active_profile()
    except Exception:
        pass

(frame_main_page, frame_content, txt_tokens, txt_channels, txt_messages,
 entry_min, entry_max, lbl_status, log_area, btn_start, btn_stop, btn_validate,
 profiles_ctx) = create_main_page(root, on_profile_changed=_on_profile_changed_from_panel)

# Gán command cho nút: trang chính kiểm TẤT CẢ acc
# (kiểm token/kênh của 1 acc riêng nằm trong panel Profiles)
def _all_profiles():
    try:
        profiles_ctx["save_current"]()
        from profiles import ensure_profiles
        return ensure_profiles(config_data)
    except Exception:
        return [p for p in config_data.get("profiles", []) if isinstance(p, dict)]

def _validate_all_tokens():
    """Kiểm tra TẤT CẢ token của MỌI profile."""
    tokens = [str(p.get("token") or "").strip() for p in _all_profiles()]
    validate_token_list([t for t in tokens if t])

def _validate_all_channels():
    """Kiểm tra toàn bộ kênh của MỌI acc - kênh nào kiểm bằng token của acc đó."""
    items = []
    for prof in _all_profiles():
        token = str(prof.get("token") or "").strip()
        if not token:
            continue  # acc thiếu token thì bỏ qua (không thể kiểm kênh)
        name = str(prof.get("name") or "").strip()
        chs = prof.get("channels") or [
            {"id": c} for c in (prof.get("channel_ids") or []) if str(c).strip()]
        for ch in chs:
            if isinstance(ch, dict):
                cid = str(ch.get("id") or "").strip()
            else:
                cid = str(ch or "").strip()
            if cid:
                items.append({"acc": name, "tokens": [token], "channel_id": cid})
    validate_channel_items(items)

# Nút KIỂM TRA gộp: nối 2 lệnh vào menu dropdown (entryconfig theo index)
try:
    btn_validate.menu.entryconfig(0, command=_validate_all_tokens)
    btn_validate.menu.entryconfig(1, command=_validate_all_channels)
except Exception:
    btn_validate.config(command=_validate_all_tokens)
btn_start.config(command=start_trigger)
btn_stop.config(command=stop_trigger)

# Trang tính năng (sửa features của profile đang chọn ở TRANG CHÍNH)
def _active_profile_for_features():
    try:
        profiles_ctx["save_current"]()
        return profiles_ctx["get_selected_profile"]()
    except Exception:
        return None

(frame_features_page, var_auto_delete, entry_delete_delay,
 var_auto_typing, entry_typing_min, entry_typing_max,
 var_auto_break, entry_break_after_min, entry_break_after_max,
 entry_break_duration_min, entry_break_duration_max,
 var_auto_stop_ban,
 var_schedule, entry_schedule_start, entry_schedule_end,
 var_smart_templates,
 var_sound_enabled, var_sound_error, var_sound_stop, var_sound_success) = create_features_page(root, profile_provider=_active_profile_for_features)

# Trang cấu hình
frame_config_page = create_config_page(root)

# Trang theme
frame_theme_page = create_theme_page(root)

# Trang dashboard
frame_dashboard_page = create_dashboard_page(root)

# Trang cài đặt (truyền tray_manager để quản lý icon khay hệ thống)
(frame_settings_page, var_tray_enabled, var_startup_enabled, _) = create_settings_page(
    root, bot_running, stop_trigger, tray_manager)

# ===== KẾT NỐI HÀNG ĐỢI LOG + LỆNH TRAY VỚI LUỒNG CHÍNH =====
root.after(100, pump_log_queue)
root.after(300, pump_tray_commands)

# Bật icon khay hệ thống nếu người dùng đã bật từ lần chạy trước
if config_data.get("features", {}).get("tray_enabled"):
    if tray_manager.start():
        log_area.insert(tk.END, language.t("log_messages.tray_enabled"), "system")

# ===== HIỂN THỊ TRANG CHÍNH BAN ĐẦU =====
show_main_page()

# Chỉ show app sau khi build xong toàn bộ UI (chống cửa sổ trắng)
root.deiconify()
root.lift()
root.focus_force()

# ===== CHẠY ỨNG DỤNG =====
root.mainloop()
