# ui/main_page.py
# Trang chính - Nhập tokens, channels, messages, và log area
# Author: bluemanhst

import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
from utils.constants import *
from config import config_data
import language


def validate_tokens_widget(txt_tokens_widget):
    """
    Hiển thị cửa sổ validate tokens
    
    Args:
        txt_tokens_widget: Widget text chứa tokens
    """
    try:
        from discord.token_validator import validate_multiple_tokens, get_avatar_url, check_token_age
    except ImportError:
        messagebox.showerror("Lỗi", "Module token_validator không tìm thấy!")
        return
    
    # Lấy tokens từ widget
    raw_tokens = txt_tokens_widget.get("1.0", tk.END).strip().split('\n')
    tokens = [t.strip() for t in raw_tokens if t.strip()]
    
    if not tokens:
        messagebox.showwarning("Cảnh báo", "Không có token nào để kiểm tra!")
        return
    
    # Tạo cửa sổ mới
    validator_window = Toplevel()
    validator_window.title(language.t("main_page.validator_title"))
    validator_window.geometry("800x600")
    validator_window.configure(bg=BG_DARK)
    
    # Frame chứa kết quả
    frame_results = tk.Frame(validator_window, bg=BG_DARK)
    frame_results.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Header
    tk.Label(frame_results, text=language.t("main_page.validator_result_title"), 
           bg=BG_DARK, fg=TXT_GOLD, font=("Arial", 14, "bold")).pack(pady=10)

    lbl_progress = tk.Label(frame_results, text=language.t("main_page.validator_checking", len(tokens)),
                            bg=BG_DARK, fg=TXT_WHITE, font=("Arial", 10))
    lbl_progress.pack(pady=(0, 6))
    
    # Scrollable frame cho kết quả
    canvas = tk.Canvas(frame_results, bg=BG_PANEL, highlightthickness=0)
    scrollbar = tk.Scrollbar(frame_results, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_PANEL)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Hiển thị kết quả validate
    result_queue = queue.Queue()
    progress = {"checked": 0, "total": len(tokens)}

    def worker():
        """Kiểm tra token trong thread riêng để cửa sổ không bị đơ"""
        for token in tokens:
            try:
                checked = validate_multiple_tokens([token])
                item = checked[0] if checked else {"valid": False, "error": "Không xác định"}
            except Exception as e:
                item = {"valid": False, "error": str(e), "token": token[:8] + "..."}
            result_queue.put(item)
        result_queue.put(None)  # Đánh dấu đã kiểm tra xong

    def poll():
        """Đọc kết quả từ hàng đợi và hiển thị (CHỈ chạy ở luồng chính Tkinter)"""
        finished = False
        while True:
            try:
                item = result_queue.get_nowait()
            except queue.Empty:
                break

            if item is None:
                finished = True
                break

            progress["checked"] += 1
            render_token_result(item)
            lbl_progress.config(text=language.t("main_page.validator_progress",
                                                progress["checked"], progress["total"]))

        if finished:
            lbl_progress.config(text=language.t("main_page.validator_done", progress["total"]))
            btn_close.config(state="normal")
            return

        validator_window.after(100, poll)
    
    def render_token_result(result):
        """Vẽ kết quả kiểm tra của 1 token vào khung kết quả"""
        frame_token = tk.Frame(scrollable_frame, bg=BG_PANEL, bd=1, relief="ridge")
        frame_token.pack(fill="x", padx=5, pady=5)
        
        token_display = result.get("token", "Unknown")
        is_valid = result.get("valid", False)
        
        # Token info
        color = "#00FF66" if is_valid else "#FF3333"
        status = "✅ HỢP LỆ" if is_valid else "❌ KHÔNG HỢP LỆ"
        
        tk.Label(frame_token, text=f"{token_display} - {status}", 
               bg=BG_PANEL, fg=color, font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=5)
        
        if is_valid:
            # Frame chứa avatar và thông tin
            frame_info = tk.Frame(frame_token, bg=BG_PANEL)
            frame_info.pack(fill="x", padx=10, pady=5)
            
            # Cột avatar
            frame_avatar = tk.Frame(frame_info, bg=BG_PANEL)
            frame_avatar.pack(side="left", padx=10)
            
            # Thử tải và hiển thị avatar
            try:
                from discord.token_validator import get_avatar_url
                avatar_url = get_avatar_url(result.get('id', ''), result.get('avatar', ''), size=128)
                
                if avatar_url:
                    # Tải avatar từ URL
                    import requests
                    import io
                    
                    try:
                        from PIL import Image, ImageTk
                    except ImportError:
                        # Avatar mặc định nếu không có Pillow
                        tk.Label(frame_avatar, text="👤", font=("Arial", 32), 
                               bg=BG_PANEL, fg=TXT_WHITE).pack()
                        raise ImportError("Pillow not available")
                    
                    try:
                        response = requests.get(avatar_url, timeout=5)
                        if response.status_code == 200:
                            image_data = response.content
                            image = Image.open(io.BytesIO(image_data))
                            image = image.resize((64, 64), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(image)
                            
                            avatar_label = tk.Label(frame_avatar, image=photo, bg=BG_PANEL)
                            avatar_label.image = photo  # Giữ reference
                            avatar_label.pack()
                        else:
                            # Avatar mặc định nếu không tải được
                            tk.Label(frame_avatar, text="👤", font=("Arial", 32), 
                                   bg=BG_PANEL, fg=TXT_WHITE).pack()
                    except Exception as e:
                        # Avatar mặc định nếu có lỗi
                        tk.Label(frame_avatar, text="👤", font=("Arial", 32), 
                               bg=BG_PANEL, fg=TXT_WHITE).pack()
                else:
                    # Avatar mặc định nếu không có avatar
                    tk.Label(frame_avatar, text="👤", font=("Arial", 32), 
                           bg=BG_PANEL, fg=TXT_WHITE).pack()
            except Exception as e:
                # Avatar mặc định nếu có lỗi import
                tk.Label(frame_avatar, text="👤", font=("Arial", 32), 
                       bg=BG_PANEL, fg=TXT_WHITE).pack()
            
            # Cột thông tin
            frame_details = tk.Frame(frame_info, bg=BG_PANEL)
            frame_details.pack(side="left", fill="both", expand=True, padx=10)
            
            info_text = f"Username: {result.get('username', 'Unknown')}#{result.get('discriminator', '0000')}\n"
            info_text += f"ID: {result.get('id', 'Unknown')}\n"
            info_text += f"Email: {result.get('email', 'N/A')}\n"
            info_text += f"Verified: {'✅' if result.get('verified', False) else '❌'}\n"
            info_text += f"MFA: {'✅' if result.get('mfa_enabled', False) else '❌'}\n"
            info_text += f"Token Type: {result.get('token_type', 'Unknown')}"
            
            tk.Label(frame_details, text=info_text, 
                   bg=BG_PANEL, fg=TXT_WHITE, font=("Arial", 9), justify="left").pack(anchor="w")
        else:
            # Hiển thị lỗi
            error_text = f"Lỗi: {result.get('error', 'Unknown error')}"
            tk.Label(frame_token, text=error_text, 
                   bg=BG_PANEL, fg="#FF6666", font=("Arial", 9), justify="left").pack(anchor="w", padx=20, pady=5)
    
    # Nút đóng
    btn_close = tk.Button(frame_results, text=language.t("main_page.validator_close"), command=validator_window.destroy,
             bg=BTN_RED, fg=TXT_WHITE, font=("Arial", 10, "bold"), bd=2)
    btn_close.pack(pady=10)
    btn_close.config(state="disabled")

    # Chạy kiểm tra trong thread riêng, đọc kết quả ở luồng chính của Tkinter
    threading.Thread(target=worker, daemon=True).start()
    validator_window.after(100, poll)


def create_main_page(root):
    """
    Tạo trang chính với các ô nhập liệu và log area
    
    Args:
        root: Root window
    
    Returns:
        tuple: (frame_main_page, frame_content, txt_tokens, txt_channels, 
                txt_messages, entry_min, entry_max, lbl_status, log_area)
    """
    # Frame chính của trang
    frame_main_page = tk.Frame(root, bg=BG_DARK)
    
    # Frame chứa nội dung chính
    frame_content = tk.Frame(frame_main_page, bg=BG_DARK)
    frame_content.pack(fill="both", expand=True, padx=15, pady=10)

    # ===== Ô NHẬP TOKENS =====
    tk.Label(frame_content, text=language.t("main_page.tokens_label"), 
             bg=BG_DARK, fg=TXT_GOLD, font=FONT_LABEL).pack(anchor="w", pady=4)
    txt_tokens = tk.Text(frame_content, height=5, bg=BG_PANEL, fg=TXT_WHITE, 
                        insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    txt_tokens.pack(fill="x", pady=2)
    txt_tokens.insert("1.0", "\n".join(config_data.get("tokens", [])))

    # ===== Ô NHẬP CHANNEL IDs =====
    tk.Label(frame_content, text=language.t("main_page.channels_label"), 
             bg=BG_DARK, fg=TXT_GOLD, font=FONT_LABEL).pack(anchor="w", pady=4)
    tk.Label(frame_content, text=language.t("main_page.channels_tip"), 
             bg=BG_DARK, fg="#39FF14", font=("Arial", 9, "italic")).pack(anchor="w", pady=(2, 4))
    txt_channels = tk.Text(frame_content, height=3, bg=BG_PANEL, fg=TXT_WHITE, 
                          insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    txt_channels.pack(fill="x", pady=2)
    txt_channels.insert("1.0", "\n".join(config_data.get("channel_ids", [""])))

    # ===== CẤU HÌNH THỜI GIAN CHỜ (Cooldown) =====
    frame_time = tk.Frame(frame_content, bg=BG_DARK)
    frame_time.pack(fill="x", pady=8)
    
    tk.Label(frame_time, text=language.t("main_page.cooldown_min"), bg=BG_DARK, fg=TXT_WHITE, 
             font=FONT_LABEL).grid(row=0, column=0, sticky="w")
    entry_min = tk.Entry(frame_time, width=10, bg=BG_PANEL, fg=TXT_WHITE, 
                         insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_min.grid(row=0, column=1, padx=5)
    entry_min.insert(0, str(config_data.get("cooldown_min", 60)))

    tk.Label(frame_time, text=language.t("main_page.cooldown_max"), bg=BG_DARK, fg=TXT_WHITE, 
             font=FONT_LABEL).grid(row=0, column=2, sticky="w", padx=20)
    entry_max = tk.Entry(frame_time, width=10, bg=BG_PANEL, fg=TXT_WHITE, 
                         insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    entry_max.grid(row=0, column=3, padx=5)
    entry_max.insert(0, str(config_data.get("cooldown_max", 90)))

    # ===== Ô NHẬP DANH SÁCH TIN NHẮN =====
    tk.Label(frame_content, text=language.t("main_page.messages_label"), 
             bg=BG_DARK, fg=TXT_GOLD, font=FONT_LABEL).pack(anchor="w", pady=4)
    txt_messages = tk.Text(frame_content, height=6, bg=BG_PANEL, fg=TXT_WHITE, 
                          insertbackground=TXT_WHITE, font=FONT_ENTRY, bd=2, relief="ridge")
    txt_messages.pack(fill="x", pady=2)
    txt_messages.insert("1.0", "\n".join(config_data.get("custom_message", ["Hello"])))

    # ===== LABEL TRẠNG THÁI =====
    lbl_status = tk.Label(frame_content, text=language.t("main_page.status_stopped"), 
                          bg=BG_DARK, fg="#FF3333", font=("Arial", 11, "bold"))
    lbl_status.pack(pady=8)

    # ===== NÚT BẬT/DỪNG =====
    frame_btn = tk.Frame(frame_content, bg=BG_DARK)
    frame_btn.pack(pady=5)
    
    # Nút validate tokens
    btn_validate = tk.Button(frame_btn, text=language.t("main_page.btn_validate"), 
                           bg="#4CAF50", fg=TXT_WHITE, width=18, 
                           font=("Arial", 10, "bold"), 
                           activebackground="#45a049", activeforeground=TXT_WHITE, bd=3)
    btn_validate.grid(row=0, column=0, padx=10)
    
    # Các nút sẽ được gán command sau
    btn_start = tk.Button(frame_btn, text=language.t("main_page.btn_start"), 
                          bg=BTN_ORANGE, fg=TXT_WHITE, width=18, 
                          font=("Arial", 10, "bold"), 
                          activebackground="#E65C00", activeforeground=TXT_WHITE, bd=3)
    btn_start.grid(row=0, column=1, padx=10)
    
    btn_stop = tk.Button(frame_btn, text=language.t("main_page.btn_stop"), 
                         bg=BTN_RED, fg=TXT_WHITE, width=18, 
                         font=("Arial", 10, "bold"), 
                         activebackground="#B30000", activeforeground=TXT_WHITE, bd=3)
    btn_stop.grid(row=0, column=2, padx=10)

    # ===== LOG AREA (Nhật ký hoạt động) =====
    tk.Label(frame_content, text=language.t("main_page.log_label"), 
             bg=BG_DARK, fg=TXT_GOLD, font=FONT_LABEL).pack(anchor="w", pady=4)
    log_area = scrolledtext.ScrolledText(frame_content, height=13, bg="#0F1015", 
                                        fg=LOG_BLUE, font=("Consolas", 10))
    log_area.pack(fill="both", expand=True, pady=5)

    # Cấu hình màu cho các tag log
    log_area.tag_config("system", foreground="#FFFF00")
    log_area.tag_config("success", foreground="#00FF66")
    log_area.tag_config("fail", foreground="#FF3333")
    log_area.tag_config("wait", foreground="#AAAAAA")
    log_area.tag_config("delete", foreground="#FF00FF")

    return frame_main_page, frame_content, txt_tokens, txt_channels, txt_messages, entry_min, entry_max, lbl_status, log_area, btn_start, btn_stop, btn_validate
