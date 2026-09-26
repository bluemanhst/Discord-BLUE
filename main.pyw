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

# Tiện ích đường dẫn (chạy source lẫn EXE) + log an toàn + âm thanh + tray
from utils.paths import resource_path
from utils.helpers import ThreadSafeLog
from utils.sound import set_all as set_sound_enabled, notify as notify_sound
from utils.tray import TrayManager

# Load theme từ config và cập nhật constants TRƯỚC khi import
import utils.constants as constants
saved_theme_name = config_data.get("current_theme", "Dragon Ball (Mặc định)")
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

if saved_theme_name in themes:
    saved_theme = themes[saved_theme_name]
    constants.BG_DARK = saved_theme["BG_DARK"]
    constants.BG_PANEL = saved_theme["BG_PANEL"]
    constants.TXT_GOLD = saved_theme["TXT_GOLD"]
    constants.TXT_WHITE = saved_theme["TXT_WHITE"]
    constants.BTN_ORANGE = saved_theme["BTN_ORANGE"]
    constants.BTN_RED = saved_theme["BTN_RED"]
    constants.LOG_BLUE = saved_theme["LOG_BLUE"]

# Import từ các module đã tách (sau khi đã cập nhật constants)
from utils.constants import *
from utils.helpers import is_in_schedule, process_smart_template
from discord.bot import run_single_account
from discord.dashboard import dashboard
from ui.navigation import create_navigation_bar
from ui.main_page import create_main_page, validate_tokens_widget, validate_channels_widget
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
    title="Discord BLUE",
    menu_show=language.t("settings_page.tray_menu_show"),
    menu_quit=language.t("settings_page.tray_menu_quit")
)

# ===== HÀM CHUYỂN TRANG =====
def show_main_page():
    """Hiển thị trang chính"""
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_main_page.pack(fill="both", expand=True)

def show_features_page():
    """Hiển thị trang tính năng"""
    frame_main_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_features_page.pack(fill="both", expand=True)

def show_config_page():
    """Hiển thị trang cấu hình"""
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_config_page.pack(fill="both", expand=True)

def show_theme_page():
    """Hiển thị trang theme"""
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_theme_page.pack(fill="both", expand=True)

def show_dashboard_page():
    """Hiển thị trang dashboard"""
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_settings_page.pack_forget()
    frame_dashboard_page.pack(fill="both", expand=True)

def show_settings_page():
    """Hiển thị trang cài đặt"""
    frame_main_page.pack_forget()
    frame_features_page.pack_forget()
    frame_config_page.pack_forget()
    frame_theme_page.pack_forget()
    frame_dashboard_page.pack_forget()
    frame_settings_page.pack(fill="both", expand=True)

# ===== HÀM BẬT TOOL =====
def start_trigger():
    """Bắt đầu chạy tool"""
    global bot_running, bot_generation, account_threads
    if bot_running[0]:
        messagebox.showinfo("Thông báo", language.t("main_page.info_running"))
        return

    raw_tokens = txt_tokens.get("1.0", tk.END).strip().split('\n')
    tokens = [t.strip() for t in raw_tokens if t.strip()]

    if not tokens:
        messagebox.showwarning("Cảnh báo", language.t("main_page.warning_no_tokens"))
        return

    raw_channels = txt_channels.get("1.0", tk.END).strip().split('\n')
    channel_ids = [c.strip() for c in raw_channels if c.strip()]

    if not channel_ids:
        messagebox.showwarning("Cảnh báo", language.t("main_page.warning_no_channels"))
        return

    try:
        cooldown_min = int(entry_min.get().strip() or 60)
        cooldown_max = int(entry_max.get().strip() or 90)
        delete_delay_ms = int(entry_delete_delay.get().strip() or 0)
        typing_min_sec = int(entry_typing_min.get().strip() or 2)
        typing_max_sec = int(entry_typing_max.get().strip() or 5)
        break_after_min = int(entry_break_after_min.get().strip() or 15)
        break_after_max = int(entry_break_after_max.get().strip() or 25)
        break_duration_min = int(entry_break_duration_min.get().strip() or 10)
        break_duration_max = int(entry_break_duration_max.get().strip() or 30)
        
        # Validate schedule time format
        schedule_start = entry_schedule_start.get().strip()
        schedule_end = entry_schedule_end.get().strip()
        try:
            datetime.strptime(schedule_start, "%H:%M")
            datetime.strptime(schedule_end, "%H:%M")
        except ValueError:
            messagebox.showwarning("Cảnh báo", language.t("main_page.warning_invalid_format"))
            return
        
        if min(cooldown_min, cooldown_max, delete_delay_ms, typing_min_sec, typing_max_sec,
               break_after_min, break_after_max, break_duration_min, break_duration_max) < 0:
            raise ValueError
        if cooldown_min > cooldown_max:
            messagebox.showwarning("Cảnh báo", language.t("main_page.warning_cooldown_range"))
            return
        if typing_min_sec > typing_max_sec:
            messagebox.showwarning("Cảnh báo", language.t("main_page.warning_typing_range"))
            return
        if break_after_min > break_after_max:
            messagebox.showwarning("Cảnh báo", language.t("main_page.warning_break_range"))
            return
        if break_duration_min > break_duration_max:
            messagebox.showwarning("Cảnh báo", language.t("main_page.warning_break_duration_range"))
            return
    except ValueError:
        messagebox.showwarning("Cảnh báo", language.t("main_page.warning_invalid_numbers"))
        return

    # Chỉ cập nhật những gì người dùng nhập trên UI và GIỮ NGUYÊN các key khác
    # (language, current_theme...) - trước đây ghi đè cả file nên bị mất cài đặt
    custom_message = [m.strip() for m in
                      txt_messages.get("1.0", tk.END).strip().split('\n') if m.strip()]
    if not custom_message:
        custom_message = ["Hello"]

    new_features = {
        "auto_delete": var_auto_delete.get(),
        "delete_delay_ms": delete_delay_ms,
        "auto_typing": var_auto_typing.get(),
        "typing_min_sec": typing_min_sec,
        "typing_max_sec": typing_max_sec,
        "auto_break": var_auto_break.get(),
        "break_after_min": break_after_min,
        "break_after_max": break_after_max,
        "break_duration_min": break_duration_min,
        "break_duration_max": break_duration_max,
        "auto_stop_on_ban": var_auto_stop_ban.get(),
        "schedule": var_schedule.get(),
        "schedule_start": schedule_start,
        "schedule_end": schedule_end,
        "smart_templates": var_smart_templates.get(),
        "sound_enabled": var_sound_enabled.get(),
        "sound_error": var_sound_error.get(),
        "sound_stop": var_sound_stop.get(),
        "sound_success": var_sound_success.get(),
        "tray_enabled": var_tray_enabled.get(),
        "startup_enabled": var_startup_enabled.get()
    }

    config_data["tokens"] = tokens
    config_data["channel_ids"] = channel_ids
    config_data["cooldown_min"] = cooldown_min
    config_data["cooldown_max"] = cooldown_max
    config_data["custom_message"] = custom_message
    config_data.setdefault("features", {}).update(new_features)
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

    log_area.insert(tk.END, "==================================================\n", "system")
    log_area.insert(tk.END, language.t("log_messages.system_start", len(tokens), len(channel_ids)), "system")
    # Dòng tóm tắt trạng thái các tính năng (dịch theo ngôn ngữ đang chọn)
    feature_status = {True: language.t("log_messages.on"), False: language.t("log_messages.off")}
    feature_lines = [
        ("log_messages.feature_auto_delete", feature_status[new_config['features']['auto_delete']]),
        ("log_messages.feature_auto_typing", feature_status[new_config['features']['auto_typing']]),
        ("log_messages.feature_auto_break", feature_status[new_config['features']['auto_break']]),
        ("log_messages.feature_auto_stop_ban", feature_status[new_config['features']['auto_stop_on_ban']]),
        ("log_messages.feature_schedule", feature_status[new_config['features']['schedule']],
         schedule_start, schedule_end),
        ("log_messages.feature_smart_templates",
         feature_status[new_config['features']['smart_templates']])
    ]
    for line_key, *line_args in feature_lines:
        log_area.insert(tk.END, language.t(line_key, *line_args), "system")
    log_area.insert(tk.END, "==================================================\n", "system")

    for index, current_token in enumerate(tokens, start=1):
        t = threading.Thread(target=run_single_account, args=(
            current_token, index, new_config["channel_ids"],
            new_config["cooldown_min"], new_config["cooldown_max"],
            new_config["custom_message"], log_proxy,
            new_config["features"], bot_running
        ), kwargs={"run_id": current_run, "generation_ref": bot_generation}, daemon=True)
        account_threads.append(t)
        t.start()

    lbl_status.config(text=language.t("main_page.status_running"), fg="#FFCC00")

# ===== HÀM DỪNG TOOL =====
def stop_trigger():
    """Dừng tool"""
    bot_running[0] = False
    bot_generation[0] += 1  # Buộc mọi thread đang ngủ phải thoát ra ngay
    lbl_status.config(text=language.t("main_page.status_stopped"), fg="#FF3333")
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
    stop_trigger()
    tray_manager.stop()
    root.destroy()


def pump_tray_commands():
    """Xử lý các lệnh bấm từ menu icon khay hệ thống (luồng chính Tkinter)"""
    tray_manager.drain(on_show=show_window_from_tray, on_quit=quit_from_tray)
    root.after(300, pump_tray_commands)

# ===== KHỞI TẠO ROOT WINDOW =====
root = tk.Tk()
root.title("Discord BLUE by bluemanhst")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.minsize(MIN_WIDTH, MIN_HEIGHT)
root.configure(bg=BG_DARK)

# Load icon app (đường dẫn đã được utils.paths tính đúng cho cả source lẫn EXE)
icon_path = resource_path("assets", "logo.ico")
if os.path.exists(icon_path):
    try:
        root.iconbitmap(icon_path)
    except Exception:
        pass  # Không load được icon thì bỏ qua, không ảnh hưởng tool

# ===== TẠO NAVIGATION BAR =====
nav_bar = create_navigation_bar(root, show_main_page, show_features_page,
                                show_config_page, show_theme_page, show_dashboard_page, show_settings_page)

# ===== TẠO CÁC TRANG =====
# Trang chính
(frame_main_page, frame_content, txt_tokens, txt_channels, txt_messages, 
 entry_min, entry_max, lbl_status, log_area, btn_start, btn_stop, btn_validate, btn_validate_channels) = create_main_page(root)

# Gán command cho nút
btn_validate.config(command=lambda: validate_tokens_widget(txt_tokens))
btn_validate_channels.config(command=lambda: validate_channels_widget(txt_channels, txt_tokens))
btn_start.config(command=start_trigger)
btn_stop.config(command=stop_trigger)

# Trang tính năng
(frame_features_page, var_auto_delete, entry_delete_delay,
 var_auto_typing, entry_typing_min, entry_typing_max,
 var_auto_break, entry_break_after_min, entry_break_after_max, 
 entry_break_duration_min, entry_break_duration_max,
 var_auto_stop_ban,
 var_schedule, entry_schedule_start, entry_schedule_end,
 var_smart_templates,
 var_sound_enabled, var_sound_error, var_sound_stop, var_sound_success) = create_features_page(root)

# Trang cấu hình
frame_config_page = create_config_page(root)

# Trang theme
frame_theme_page = create_theme_page(root)

# Trang dashboard
frame_dashboard_page = create_dashboard_page(root)

# Trang cài đặt (truyền tray_manager để quản lý icon khay hệ thống)
(frame_settings_page, var_tray_enabled, var_startup_enabled, _) = create_settings_page(
    root, bot_running, stop_trigger, tray_manager)

# ===== TẠO FOOTER =====
frame_footer = create_footer(root)

# ===== KẾT NỐI HÀNG ĐỢI LOG + LỆNH TRAY VỚI LUỒNG CHÍNH =====
root.after(100, pump_log_queue)
root.after(300, pump_tray_commands)

# Bật icon khay hệ thống nếu người dùng đã bật từ lần chạy trước
if config_data.get("features", {}).get("tray_enabled"):
    if tray_manager.start():
        log_area.insert(tk.END, "🖥️ Đã bật icon khay hệ thống (System Tray).\n", "system")

# ===== HIỂN THỊ TRANG CHÍNH BAN ĐẦU =====
show_main_page()

# ===== CHẠY ỨNG DỤNG =====
root.mainloop()
