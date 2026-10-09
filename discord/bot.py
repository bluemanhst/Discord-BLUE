# discord/bot.py
# Logic Discord API - Gửi tin nhắn, typing indicator, auto delete
# Author: bluemanhst

import requests
import random
import threading
import tkinter as tk
from utils.constants import DISCORD_API_BASE
from utils.helpers import (is_in_schedule, process_smart_template,
                           interruptible_sleep, should_stop)
from utils.sound import notify as notify_sound
from discord.dashboard import dashboard
import language

# Số giây chờ giữa 2 lần kiểm tra khung giờ khi đang nằm ngoài schedule
SCHEDULE_CHECK_INTERVAL = 60


# ===== HELPER: CHẠY SONG SONG TỪNG KÊNH =====
def _short_name(profile_name, token, account_index):
    if profile_name and str(profile_name).strip():
        return str(profile_name).strip()
    if len(token or "") > 10:
        return f"{token[:4]}...{token[-4:]}"
    return f"Acc {account_index}"


def _ch_cooldown(ch, fb_min, fb_max):
    try:
        a = max(0, int((ch or {}).get("cd_min", fb_min)))
        b = max(0, int((ch or {}).get("cd_max", fb_max)))
    except (TypeError, ValueError):
        a, b = fb_min, fb_max
    if a > b:
        a, b = b, a
    return a, b


# ===== HÀM CHẠY TÀI KHOẢN ĐỘC LẬP (Multi-threading) =====
def run_single_account(token, account_index, channel_ids, cooldown_min, cooldown_max, 
                      messages, log_widget, features, bot_running_ref,
                      run_id=None, generation_ref=None, profile_name=None, channels=None,
                      emoji_guilds=None):
    """
    Chạy bot cho TỪNG tài khoản Discord riêng biệt.
    Mỗi acc 1 thread quản lý, bên trong tự spawn 1 worker/kênh chạy SONG SONG
    độc lập (mỗi kênh CD/break riêng, không chờ nhau).
    - 401 (token chết) -> dừng mọi worker cùng acc.
    - 403/404 + auto_stop_on_ban -> chỉ dừng worker-channel lỗi.

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
    short_token = _short_name(profile_name, token, account_index)

    # Account ID cho dashboard
    account_id = f"account_{account_index}"

    # Biến dùng cho worker (trước đây là local của vòng lặp gửi cũ; bị mất
    # trong đợt refactor song song từng kênh -> NameError im lặng, bot không
    # gửi tin nào dù status vẫn "ĐANG CHẠY").
    schedule_enabled = bool(features.get("schedule", False))
    schedule_start = str(features.get("schedule_start", "09:00"))
    schedule_end = str(features.get("schedule_end", "17:00"))
    smart_templates = bool(features.get("smart_templates", False))
    default_messages = [str(m) for m in (messages or []) if str(m).strip()]

    # Chuẩn hoá danh sách kênh song song (mỗi kênh = 1 worker độc lập)
    if channels:
        targets = []
        for c in channels:
            if not isinstance(c, dict):
                continue
            cid = str(c.get("id") or "").strip()
            if not cid:
                continue
            cmin, cmax = _ch_cooldown(c, cooldown_min, cooldown_max)
            own = [m for m in (c.get("messages") or []) if str(m).strip()]
            targets.append({"id": cid, "cd_min": cmin, "cd_max": cmax,
                            "pool": own or default_messages})
    else:
        ids = [str(x).strip() for x in (channel_ids or []) if str(x).strip()]
        targets = [{"id": cid, "cd_min": cooldown_min, "cd_max": cooldown_max,
                    "pool": default_messages} for cid in ids]

    if not targets or not default_messages and not any(t["pool"] for t in targets):
        log_widget.insert(tk.END, language.t("log_messages.no_target", short_token), "fail")
        log_widget.see(tk.END)
        return

    # Event dùng chung: token chết (401) -> dừng mọi channel cùng acc
    token_invalid = threading.Event()

    def _dead():
        try:
            return bool(token_invalid.is_set())
        except Exception:
            return False

    # Server emoji da tick (theo acc) -> truyen xuong worker resolve :ten:.
    profile_emoji_guilds = [str(g).strip() for g in (emoji_guilds or [])
                            if str(g).strip()]

    workers = []
    for order, tgt in enumerate(targets):
        if not tgt["pool"]:
            continue
        th = threading.Thread(
            target=_run_one_channel,
            args=(token, account_index, short_token, account_id, tgt,
                  dict(features or {}), log_widget,
                  bot_running_ref, run_id, generation_ref,
                  schedule_enabled, schedule_start, schedule_end,
                  smart_templates, token_invalid, order,
                  list(profile_emoji_guilds)),
            daemon=True)
        th.start()
        workers.append(th)

    for th in workers:
        while th.is_alive():
            if should_stop(bot_running_ref, run_id, generation_ref) or _dead():
                break
            th.join(timeout=0.5)
        if should_stop(bot_running_ref, run_id, generation_ref) or _dead():
            continue


def _run_one_channel(token, account_index, short_token, account_id, target,
                     features, log_widget, bot_running_ref, run_id,
                     generation_ref, schedule_enabled, schedule_start,
                     schedule_end, smart_templates, token_invalid, order,
                     profile_emoji_guilds=None):
    """Worker chạy 1 kênh: CD/break/typing/delete độc lập, không chờ kênh khác."""
    import requests as _rq
    import random as _rd
    headers = {"Authorization": token, "Content-Type": "application/json"}
    channel_id = target["id"]
    ch_cd_min, ch_cd_max = target["cd_min"], target["cd_max"]
    pool = target["pool"]
    url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"

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

    def _token_dead():
        try:
            return bool(token_invalid is not None and token_invalid.is_set())
        except Exception:
            return False

    # Stagger start: tránh N channel cùng burst request gây 429
    if order > 0:
        if interruptible_sleep(min(order * 2, 10), bot_running_ref, run_id, generation_ref):
            return

    log_widget.insert(
        tk.END,
        language.t("log_messages.channel_start", short_token, channel_id,
                   ch_cd_min, ch_cd_max),
        "system")
    log_widget.see(tk.END)

    # Discord chi render custom emoji voi format CO ID (<:name:id>/<a:name:id>),
    # gui nguyen :name: se hien text -> doi truoc khi gui. Map = guild cua
    # channel (uu tien) + server da tick trong profile["emoji_guilds"].
    # Trung ten (:test: o ca sv1/sv2): guild channel thang, roi theo thu tu
    # tick. Loi/thieu -> giu nguyen text.
    try:
        from discord.guild_emojis import build_selected_emoji_map
        from utils.chat_markup import resolve_emoji_shortcodes
        _sel = list((profile_emoji_guilds or []))
        _emap = build_selected_emoji_map(token, channel_id, _sel) or {}
        if _emap:
            pool = [resolve_emoji_shortcodes(str(m), _emap) for m in pool]
    except Exception:
        pass

    sent_count = 0
    try:
        next_break_at = _rd.randint(int(break_after_min), int(break_after_max))
    except (TypeError, ValueError):
        next_break_at = 20

    # Vòng lặp chính - chạy liên tục khi bot đang hoạt động
    while not should_stop(bot_running_ref, run_id, generation_ref) and not _token_dead():
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

        # Random chọn 1 tin nhắn (tin đa dòng giữ nguyên \n - Discord hỗ trợ sẵn)
        msg = _rd.choice(pool)

        # Tính năng Smart Templates: Xử lý random hóa
        if smart_templates:
            msg = process_smart_template(msg)

        payload = {"content": msg}

        try:
            # Tính năng Auto Typing: Giả lập "Đang gõ..." trước khi gửi
            if auto_typing:
                try:
                    typing_url = f"{DISCORD_API_BASE}/channels/{channel_id}/typing"
                    _rq.post(typing_url, headers=headers)
                except Exception:
                    pass
                typing_time = _rd.randint(int(typing_min_sec), int(typing_max_sec))
                log_widget.insert(tk.END, language.t("log_messages.typing", short_token, typing_time), "wait")
                log_widget.see(tk.END)
                if interruptible_sleep(typing_time, bot_running_ref, run_id, generation_ref):
                    break

            # Gửi tin nhắn
            response = _rq.post(url, json=payload, headers=headers)
            
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
                            delete_response = _rq.delete(delete_url, headers=headers)
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
                # Token sai hoặc hết hạn -> dừng cả acc
                log_widget.insert(tk.END, language.t("log_messages.invalid_token", short_token), "fail")
                dashboard.record_error(account_id, channel_id, "invalid_token")
                notify_sound("error")
                try:
                    if token_invalid is not None:
                        token_invalid.set()
                except Exception:
                    pass
                break

            elif response.status_code in (403, 404) and auto_stop_on_ban:
                # Kênh này bị cấm/kick/mute -> chỉ dừng channel này
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
        if should_stop(bot_running_ref, run_id, generation_ref) or _token_dead():
            break

        # Tính năng Auto Break: Nghỉ dài định kỳ để tránh bị Discord để ý
        if auto_break and sent_count >= next_break_at:
            break_minutes = _rd.randint(int(break_duration_min), int(break_duration_max))
            log_widget.insert(
                tk.END,
                language.t("log_messages.break", short_token, sent_count, break_minutes),
                "system")
            log_widget.see(tk.END)
            if interruptible_sleep(break_minutes * 60, bot_running_ref, run_id, generation_ref):
                break
            sent_count = 0
            next_break_at = _rd.randint(break_after_min, break_after_max)
            continue

        # Tính thời gian chờ ngẫu nhiên trước khi gửi tin tiếp theo (CD riêng kênh)
        delay = _rd.randint(ch_cd_min, ch_cd_max)
        log_widget.insert(tk.END, language.t("log_messages.waiting", short_token, delay), "wait")
        log_widget.see(tk.END)

        if interruptible_sleep(delay, bot_running_ref, run_id, generation_ref):
            break

    log_widget.insert(
        tk.END,
        language.t("log_messages.channel_stopped", short_token, channel_id),
        "system")
    log_widget.see(tk.END)

