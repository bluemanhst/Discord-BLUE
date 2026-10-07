# discord/bot.py
# Logic Discord API - Gửi tin nhắn, typing indicator, auto delete
# Author: bluemanhst

import requests
import random
import tkinter as tk
from utils.constants import DISCORD_API_BASE
from utils.helpers import (is_in_schedule, process_smart_template,
                           interruptible_sleep, should_stop)
from utils.sound import notify as notify_sound
from discord.dashboard import dashboard
import language

# Số giây chờ giữa 2 lần kiểm tra khung giờ khi đang nằm ngoài schedule
SCHEDULE_CHECK_INTERVAL = 60


# ===== HÀM CHẠY TÀI KHOẢN ĐỘC LẬP (Multi-threading) =====
def run_single_account(token, account_index, channel_ids, cooldown_min, cooldown_max, 
                      messages, log_widget, features, bot_running_ref,
                      run_id=None, generation_ref=None, profile_name=None, channels=None):
    """
    Chạy bot cho TỪNG tài khoản Discord riêng biệt
    Mỗi tài khoản chạy trong thread riêng để không ảnh hưởng nhau
    
    Args:
        token (str): Discord token của tài khoản
        account_index (int): Số thứ tự tài khoản
        channel_ids (list): Danh sách channel ID để gửi tin
        cooldown_min (int): Thời gian chờ tối thiểu (giây)
        cooldown_max (int): Thời gian chờ tối đa (giây)
        channels (list|None): MỚI - [{"id", "cd_min", "cd_max", "messages"}]: CD + chat riêng từng kênh (messages rỗng -> dùng bộ mặc định của profile).
        messages (list): Danh sách tin nhắn để gửi
        log_widget: Widget log (hoặc ThreadSafeLog) để hiển thị hoạt động
        features (dict): Các tính năng bật/tắt
        bot_running_ref (list): Reference đến list [bot_running] để thread-safe
        run_id (int|None): Mã lượt chạy hiện tại (tránh thread cũ "sống dậy")
        generation_ref (list|None): Reference đến list [generation] của app
    """
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    # Tên hiển thị ngắn gọn cho token (ưu tiên tên profile riêng)
    if profile_name and str(profile_name).strip():
        short_token = str(profile_name).strip()
    else:
        short_token = f"{token[:4]}...{token[-4:]}" if len(token) > 10 else f"Acc {account_index}"
    
    # Account ID cho dashboard
    account_id = f"account_{account_index}"

    # Lấy các tính năng từ config
    auto_delete = features.get("auto_delete", False)
    delete_delay_ms = features.get("delete_delay_ms", 0)
    auto_typing = features.get("auto_typing", False)
    typing_min_sec = features.get("typing_min_sec", 2)
    typing_max_sec = features.get("typing_max_sec", 5)
    auto_break = features.get("auto_break", False)
    break_after_min = features.get("break_after_min", 15)
    break_after_max = features.get("break_after_max", 25)
    break_duration_min = features.get("break_duration_min", 10)
    break_duration_max = features.get("break_duration_max", 30)
    auto_stop_on_ban = features.get("auto_stop_on_ban", True)
    
    # Tính năng Schedule (hẹn giờ)
    schedule_enabled = features.get("schedule", False)
    schedule_start = features.get("schedule_start", "09:00")
    schedule_end = features.get("schedule_end", "17:00")
    
    # Tính năng Smart Templates (random hóa tin nhắn)
    smart_templates = features.get("smart_templates", False)

    # Bộ tin nhắn: kênh không có chat riêng -> dùng bộ mặc định của profile
    default_messages = [m for m in (messages or []) if str(m).strip()]
    if channels:
        eff_channels = []
        for c in channels:
            if not isinstance(c, dict):
                continue
            own = [m for m in (c.get("messages") or []) if str(m).strip()]
            eff = dict(c)
            eff["messages"] = own or default_messages
            if eff["messages"]:
                eff_channels.append(eff)
    else:
        eff_channels = None

    # Bộ đếm phục vụ tính năng Nghỉ dài định kỳ
    sent_count = 0
    next_break_at = random.randint(break_after_min, break_after_max) if auto_break else None

    log_widget.insert(tk.END, language.t("log_messages.account_start", short_token), "system")
    log_widget.see(tk.END)

    # Vòng lặp chính - chạy liên tục khi bot đang hoạt động
    while not should_stop(bot_running_ref, run_id, generation_ref):
        # Tính năng Schedule: Kiểm tra xem có nằm trong khung giờ không
        if not is_in_schedule(schedule_enabled, schedule_start, schedule_end):
            log_widget.insert(
                tk.END,
                language.t("log_messages.schedule_wait", short_token, schedule_start, schedule_end),
                "wait")
            log_widget.see(tk.END)
            if interruptible_sleep(SCHEDULE_CHECK_INTERVAL, bot_running_ref, run_id, generation_ref):
                break
            continue

        # Không có kênh hoặc không có nội dung tin nhắn -> không thể gửi gì
        if not channel_ids or not (eff_channels or default_messages):
            log_widget.insert(tk.END, language.t("log_messages.no_target", short_token), "fail")
            log_widget.see(tk.END)
            break

        # Random chọn 1 kênh từ danh sách để gửi tin (CD riêng theo từng kênh)
        if eff_channels:
            ch = random.choice(eff_channels)
            channel_id = str(ch.get("id") or "").strip()
            if not channel_id:
                continue
            try:
                ch_cd_min = max(0, int(ch.get("cd_min", cooldown_min)))
                ch_cd_max = max(0, int(ch.get("cd_max", cooldown_max)))
            except (TypeError, ValueError):
                ch_cd_min, ch_cd_max = cooldown_min, cooldown_max
            if ch_cd_min > ch_cd_max:
                ch_cd_min, ch_cd_max = ch_cd_max, ch_cd_min
            # Ưu tiên chat riêng của kênh (eff đã fallback về bộ mặc định)
            pool = ch.get("messages") or default_messages
        else:
            channel_id = random.choice(channel_ids)
            ch_cd_min, ch_cd_max = cooldown_min, cooldown_max
            pool = default_messages
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"

        # Random chọn 1 tin nhắn (tin đa dòng giữ nguyên \n - Discord hỗ trợ sẵn)
        msg = random.choice(pool)
        
        # Tính năng Smart Templates: Xử lý random hóa
        if smart_templates:
            msg = process_smart_template(msg)
        
        payload = {"content": msg}

        try:
            # Tính năng Auto Typing: Giả lập "Đang gõ..." trước khi gửi
            if auto_typing:
                try:
                    typing_url = f"{DISCORD_API_BASE}/channels/{channel_id}/typing"
                    requests.post(typing_url, headers=headers)
                except Exception:
                    pass
                typing_time = random.randint(int(typing_min_sec), int(typing_max_sec))
                log_widget.insert(tk.END, language.t("log_messages.typing", short_token, typing_time), "wait")
                log_widget.see(tk.END)
                if interruptible_sleep(typing_time, bot_running_ref, run_id, generation_ref):
                    break

            # Gửi tin nhắn
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # Gửi thành công
                log_widget.insert(
                    tk.END,
                    language.t("log_messages.success", short_token, channel_id,
                               msg.replace("\n", " ↵ ")),
                    "success")
                sent_count += 1
                notify_sound("success")
                
                # Dashboard tracking
                dashboard.record_message_sent(account_id, channel_id)


                # Tính năng Auto Delete: Xóa tin nhắn sau khi gửi
                if auto_delete:
                    try:
                        message_data = response.json()
                        message_id = message_data.get("id")
                        if message_id:
                            if delete_delay_ms > 0:
                                log_widget.insert(
                                    tk.END,
                                    language.t("log_messages.delete_wait", short_token, delete_delay_ms),
                                    "wait")
                                log_widget.see(tk.END)
                                if interruptible_sleep(delete_delay_ms / 1000, bot_running_ref,
                                                       run_id, generation_ref):
                                    break
                            delete_url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages/{message_id}"
                            delete_response = requests.delete(delete_url, headers=headers)
                            if delete_response.status_code == 204:
                                log_widget.insert(tk.END, language.t("log_messages.deleted", short_token), "delete")
                                # Dashboard tracking
                                dashboard.record_message_deleted(account_id, channel_id)
                            else:
                                log_widget.insert(
                                    tk.END,
                                    language.t("log_messages.delete_error", short_token,
                                               delete_response.status_code),
                                    "fail")
                    except Exception as e:
                        log_widget.insert(tk.END, language.t("log_messages.delete_fail", short_token, e), "fail")
                        
            elif response.status_code == 401:
                # Token sai hoặc hết hạn
                log_widget.insert(tk.END, language.t("log_messages.invalid_token", short_token), "fail")
                dashboard.record_error(account_id, channel_id, "invalid_token")
                notify_sound("error")
                break
                
            elif response.status_code in (403, 404) and auto_stop_on_ban:
                # Tài khoản bị cấm/kick/mute khỏi kênh
                log_widget.insert(
                    tk.END,
                    language.t("log_messages.banned", short_token, channel_id, response.status_code),
                    "fail")
                dashboard.record_error(account_id, channel_id, f"banned_kicked_{response.status_code}")
                notify_sound("error")
                break
                
            else:
                # Lỗi kết nối khác
                log_widget.insert(
                    tk.END,
                    language.t("log_messages.connection_error", short_token, response.status_code),
                    "fail")
                dashboard.record_error(account_id, channel_id, f"connection_error_{response.status_code}")
                notify_sound("error")
                
        except Exception as e:
            # Lỗi hệ thống
            log_widget.insert(tk.END, language.t("log_messages.system_error", short_token, e), "fail")
            dashboard.record_error(account_id, channel_id, f"system_error_{str(e)}")

        log_widget.see(tk.END)
        if should_stop(bot_running_ref, run_id, generation_ref):
            break

        # Tính năng Auto Break: Nghỉ dài định kỳ để tránh bị Discord để ý
        if auto_break and sent_count >= next_break_at:
            break_minutes = random.randint(int(break_duration_min), int(break_duration_max))
            log_widget.insert(
                tk.END,
                language.t("log_messages.break", short_token, sent_count, break_minutes),
                "system")
            log_widget.see(tk.END)
            if interruptible_sleep(break_minutes * 60, bot_running_ref, run_id, generation_ref):
                break
            sent_count = 0
            next_break_at = random.randint(break_after_min, break_after_max)
            continue

        # Tính thời gian chờ ngẫu nhiên trước khi gửi tin tiếp theo (theo kênh vừa chọn)
        delay = random.randint(ch_cd_min, ch_cd_max)
        log_widget.insert(tk.END, language.t("log_messages.waiting", short_token, delay), "wait")
        log_widget.see(tk.END)

        if interruptible_sleep(delay, bot_running_ref, run_id, generation_ref):
            break

