# ui/main_page.py
# Trang chính - Nhập tokens, channels, messages, validator popups và log terminal
# Author: bluemanhst

import queue
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel
from utils.theme import (
    get_theme, create_card_frame, create_section_header,
    create_styled_button, create_styled_entry, create_styled_text,
    FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION, FONT_SECTION, FONT_CODE, FONT_TITLE
)
from config import config_data
import language


def validate_tokens_widget(txt_tokens_widget):
    """
    Hiển thị modal validate tokens với giao diện clean card

    Args:
        txt_tokens_widget: Widget text chứa tokens
    """
    raw_tokens = txt_tokens_widget.get("1.0", tk.END).strip().split('\n')
    validate_token_list([t.strip() for t in raw_tokens if t.strip()])


def validate_token_list(tokens):
    """
    Kiểm tra danh sách token (list[str]) - không cần widget text.

    Args:
        tokens: Danh sách token cần kiểm tra
    """
    try:
        from discord.token_validator import validate_multiple_tokens, get_avatar_url, nitro_label
    except ImportError:
        messagebox.showerror(
            language.t("common.error_title"),
            language.t("main_page.validator_module_missing", "discord.token_validator")
        )
        return

    tokens = [str(t).strip() for t in (tokens or []) if str(t).strip()]

    if not tokens:
        messagebox.showwarning(
            language.t("common.warning_title"),
            language.t("main_page.validator_no_tokens")
        )
        return

    t = get_theme()

    validator_window = Toplevel()
    validator_window.title(language.t("main_page.validator_title"))
    validator_window.geometry("820x620")
    validator_window.minsize(680, 480)
    validator_window.configure(bg=t["bg_app"])
    # Grab modal CHỈ khi đang có grab khác giữ toàn bộ click (vd popup Kênh
    # grab_set) -> nếu không, cửa sổ này đơ, bấm Đóng/X không được. Mở từ
    # trang chính (không grab) thì bỏ qua, giữ nguyên hành vi cũ không modal.
    try:
        if validator_window.tk.call("grab", "current"):
            validator_window.grab_set()
    except Exception:
        pass

    container = tk.Frame(validator_window, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    # Top Header Card
    top_card, top_inner = create_card_frame(container, padx=16, pady=12)
    top_card.pack(fill="x", pady=(0, 10))

    lbl_title = tk.Label(
        top_inner,
        text=language.t("main_page.validator_result_title"),
        bg=t["bg_panel"],
        fg=t["text_primary"],
        font=FONT_SECTION
    )
    lbl_title.pack(side="left")

    lbl_progress = tk.Label(
        top_inner,
        text=language.t("main_page.validator_checking", len(tokens)),
        bg=t["bg_panel"],
        fg=t["accent"],
        font=FONT_BODY_BOLD
    )
    lbl_progress.pack(side="right")

    # Scrollable results area
    scroll_card, scroll_inner = create_card_frame(container, padx=8, pady=8)
    scroll_card.pack(fill="both", expand=True, pady=(0, 12))

    canvas = tk.Canvas(scroll_inner, bg=t["bg_panel"], highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_inner, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=t["bg_panel"])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", _on_canvas_resize)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Result state
    result_queue = queue.Queue()
    progress = {"checked": 0, "total": len(tokens)}

    def worker():
        for token in tokens:
            try:
                checked = validate_multiple_tokens([token])
                item = checked[0] if checked else {
                    "valid": False, "error": language.t("common.unknown")
                }
            except Exception as e:
                item = {"valid": False, "error": str(e), "token": token[:8] + "..."}
            result_queue.put(item)
        result_queue.put(None)

    def poll():
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
            lbl_progress.config(
                text=language.t("main_page.validator_progress",
                                progress["checked"], progress["total"]),
                fg=t["accent"]
            )

        if finished:
            lbl_progress.config(
                text=language.t("main_page.validator_done", progress["total"]),
                fg=t["success"]
            )
            btn_close.config(state="normal")
            return

        validator_window.after(100, poll)

    def render_token_result(result):
        is_valid = result.get("valid", False)
        status_color = t["success"] if is_valid else t["danger"]
        status_text = language.t("main_page.validator_status_valid") if is_valid \
            else language.t("main_page.validator_status_invalid")
        token_display = result.get("token", language.t("common.unknown"))

        frame_token = tk.Frame(
            scrollable_frame,
            bg=t["bg_input"],
            highlightthickness=1,
            highlightbackground=t["border_subtle"],
            padx=12,
            pady=10
        )
        frame_token.pack(fill="x", padx=4, pady=4)

        # Header status row
        top_row = tk.Frame(frame_token, bg=t["bg_input"])
        top_row.pack(fill="x", pady=(0, 6))

        tk.Label(
            top_row,
            text=token_display,
            bg=t["bg_input"],
            fg=t["text_primary"],
            font=FONT_CODE
        ).pack(side="left")

        badge = tk.Label(
            top_row,
            text=f" {status_text} ",
            bg=t["bg_hover"],
            fg=status_color,
            font=FONT_BODY_BOLD
        )
        badge.pack(side="right")

        if is_valid:
            info_row = tk.Frame(frame_token, bg=t["bg_input"])
            info_row.pack(fill="x")

            # Avatar column
            frame_avatar = tk.Frame(info_row, bg=t["bg_input"])
            frame_avatar.pack(side="left", padx=(0, 12))

            avatar_loaded = False
            avatar_url = get_avatar_url(result.get('id', ''), result.get('avatar', ''), size=128)
            if avatar_url:
                try:
                    import requests
                    import io
                    from PIL import Image, ImageTk

                    res = requests.get(avatar_url, timeout=5)
                    if res.status_code == 200:
                        image = Image.open(io.BytesIO(res.content))
                        image = image.resize((48, 48), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        lbl_img = tk.Label(frame_avatar, image=photo, bg=t["bg_input"])
                        lbl_img.image = photo
                        lbl_img.pack()
                        avatar_loaded = True
                except Exception:
                    avatar_loaded = False

            if not avatar_loaded:
                tk.Label(
                    frame_avatar,
                    text="👤",
                    font=("Segoe UI", 24),
                    bg=t["bg_input"],
                    fg=t["text_muted"]
                ).pack()

            # Details
            frame_details = tk.Frame(info_row, bg=t["bg_input"])
            frame_details.pack(side="left", fill="both", expand=True)

            line1 = (f"Username: {result.get('username', language.t('common.unknown'))}"
                     f"#{result.get('discriminator', '0000')}"
                     f"  |  ID: {result.get('id', language.t('common.unknown'))}")
            yes_no = {True: language.t("common.yes"), False: language.t("common.no")}
            on_off = {True: language.t("common.enabled"), False: language.t("common.disabled")}
            line2 = (f"Email: {result.get('email', 'N/A')}"
                     f"  |  Verified: {yes_no[bool(result.get('verified'))]}"
                     f"  |  2FA: {on_off[bool(result.get('mfa_enabled'))]}"
                     f"  |  Type: {result.get('token_type', 'User')}"
                     f"  |  Nitro: {nitro_label(result.get('premium_type', 0))}")

            tk.Label(
                frame_details,
                text=line1,
                bg=t["bg_input"],
                fg=t["text_primary"],
                font=FONT_BODY_BOLD,
                anchor="w"
            ).pack(anchor="w")

            tk.Label(
                frame_details,
                text=line2,
                bg=t["bg_input"],
                fg=t["text_secondary"],
                font=FONT_CAPTION,
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))
        else:
            error_text = language.t(
                "main_page.validator_error_prefix",
                result.get("error", language.t("main_page.token_error_default"))
            )
            tk.Label(
                frame_token,
                text=error_text,
                bg=t["bg_input"],
                fg=t["danger"],
                font=FONT_CAPTION,
                anchor="w"
            ).pack(anchor="w")

    # Bottom Actions
    btn_close = create_styled_button(
        container,
        text=language.t("main_page.validator_close"),
        command=validator_window.destroy,
        variant="secondary",
        padx=18,
        pady=6
    )
    btn_close.pack(anchor="e")
    btn_close.config(state="disabled")

    threading.Thread(target=worker, daemon=True).start()
    validator_window.after(100, poll)


def validate_channels_widget(txt_channels_widget, txt_tokens_widget):
    """
    Hiển thị modal validate channel IDs với layout hiện đại

    Args:
        txt_channels_widget: Widget text chứa channels
        txt_tokens_widget: Widget text chứa tokens
    """
    raw_channels = txt_channels_widget.get("1.0", tk.END).strip().split('\n')
    channels = [c.strip() for c in raw_channels if c.strip()]

    if not channels:
        messagebox.showwarning(
            language.t("common.warning_title"),
            language.t("main_page.channel_validator_no_channels")
        )
        return

    raw_tokens = txt_tokens_widget.get("1.0", tk.END).strip().split('\n')
    tokens = [t.strip() for t in raw_tokens if t.strip()]

    if not tokens:
        messagebox.showwarning(
            language.t("common.warning_title"),
            language.t("main_page.channel_validator_no_tokens")
        )
        return

    validate_channel_items([{"acc": "", "tokens": list(tokens), "channel_id": c}
                            for c in channels])


def validate_channel_items(items):
    """
    Kiểm tra kênh theo cặp (acc, token, channel_id):
    mỗi kênh được kiểm đúng bằng token của acc sở hữu, kết quả hiển thị tên acc.

    Args:
        items: [{"acc": str, "tokens": list[str], "channel_id": str}, ...]
    """
    try:
        from discord.channel_validator import validate_channel
    except ImportError:
        messagebox.showerror(
            language.t("common.error_title"),
            language.t("main_page.validator_module_missing", "discord.channel_validator")
        )
        return

    items = [i for i in (items or [])
             if isinstance(i, dict) and str(i.get("channel_id") or "").strip()]

    if not items:
        messagebox.showwarning(
            language.t("common.warning_title"),
            language.t("main_page.channel_validator_no_channels")
        )
        return

    t = get_theme()

    validator_window = Toplevel()
    validator_window.title(language.t("main_page.channel_validator_title"))
    validator_window.geometry("820x620")
    validator_window.minsize(680, 480)
    validator_window.configure(bg=t["bg_app"])
    # Grab modal CHỈ khi đang có grab khác giữ toàn bộ click (vd popup Kênh
    # grab_set) -> nếu không, cửa sổ này đơ, bấm Đóng/X không được. Mở từ
    # trang chính (không grab) thì bỏ qua, giữ nguyên hành vi cũ không modal.
    try:
        if validator_window.tk.call("grab", "current"):
            validator_window.grab_set()
    except Exception:
        pass

    container = tk.Frame(validator_window, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    # Top Header Card
    top_card, top_inner = create_card_frame(container, padx=16, pady=12)
    top_card.pack(fill="x", pady=(0, 10))

    lbl_title = tk.Label(
        top_inner,
        text=language.t("main_page.channel_validator_result_title"),
        bg=t["bg_panel"],
        fg=t["text_primary"],
        font=FONT_SECTION
    )
    lbl_title.pack(side="left")

    lbl_progress = tk.Label(
        top_inner,
        text=language.t("main_page.channel_validator_checking", len(items)),
        bg=t["bg_panel"],
        fg=t["accent"],
        font=FONT_BODY_BOLD
    )
    lbl_progress.pack(side="right")

    # Scrollable results area
    scroll_card, scroll_inner = create_card_frame(container, padx=8, pady=8)
    scroll_card.pack(fill="both", expand=True, pady=(0, 12))

    canvas = tk.Canvas(scroll_inner, bg=t["bg_panel"], highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_inner, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=t["bg_panel"])

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", _on_canvas_resize)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    result_queue = queue.Queue()
    progress = {"checked": 0, "total": len(items)}

    def worker():
        for item in items:
            ch_id = str(item.get("channel_id") or "").strip()
            acc_name = str(item.get("acc") or "")
            try:
                res = validate_channel(ch_id, list(item.get("tokens") or []))
            except Exception as e:
                res = {"valid": False, "id": ch_id, "error": str(e)}
            res["acc"] = acc_name
            result_queue.put(res)
        result_queue.put(None)

    def poll():
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
            render_channel_result(item)
            lbl_progress.config(
                text=language.t("main_page.channel_validator_progress",
                                progress["checked"], progress["total"]),
                fg=t["accent"]
            )

        if finished:
            lbl_progress.config(
                text=language.t("main_page.channel_validator_done", progress["total"]),
                fg=t["success"]
            )
            btn_close.config(state="normal")
            return

        validator_window.after(100, poll)

    def render_channel_result(result):
        ch_id = result.get("id", language.t("common.unknown"))
        is_valid = result.get("valid", False)
        status_color = t["success"] if is_valid else t["danger"]
        status_text = language.t("main_page.validator_status_valid") if is_valid \
            else language.t("main_page.validator_status_invalid")

        frame_ch = tk.Frame(
            scrollable_frame,
            bg=t["bg_input"],
            highlightthickness=1,
            highlightbackground=t["border_subtle"],
            padx=12,
            pady=10
        )
        frame_ch.pack(fill="x", padx=4, pady=4)

        top_row = tk.Frame(frame_ch, bg=t["bg_input"])
        top_row.pack(fill="x", pady=(0, 6))

        acc_name = str(result.get("acc") or "")
        if acc_name:
            tk.Label(
                top_row,
                text=f"{acc_name} →",
                bg=t["bg_input"],
                fg=t["accent"],
                font=FONT_BODY_BOLD
            ).pack(side="left")

        tk.Label(
            top_row,
            text=language.t("main_page.channel_id_label", ch_id),
            bg=t["bg_input"],
            fg=t["text_primary"],
            font=FONT_CODE
        ).pack(side="left")

        badge = tk.Label(
            top_row,
            text=f" {status_text} ",
            bg=t["bg_hover"],
            fg=status_color,
            font=FONT_BODY_BOLD
        )
        badge.pack(side="right")

        if is_valid:
            info_row = tk.Frame(frame_ch, bg=t["bg_input"])
            info_row.pack(fill="x")

            frame_avatar = tk.Frame(info_row, bg=t["bg_input"])
            frame_avatar.pack(side="left", padx=(0, 12))

            icon_url = result.get("guild_icon_url")
            avatar_loaded = False

            if icon_url:
                try:
                    import requests
                    import io
                    from PIL import Image, ImageTk

                    response = requests.get(icon_url, timeout=5)
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content))
                        image = image.resize((48, 48), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        avatar_label = tk.Label(frame_avatar, image=photo, bg=t["bg_input"])
                        avatar_label.image = photo
                        avatar_label.pack()
                        avatar_loaded = True
                except Exception:
                    avatar_loaded = False

            if not avatar_loaded:
                tk.Label(
                    frame_avatar,
                    text="🏰",
                    font=("Segoe UI", 24),
                    bg=t["bg_input"],
                    fg=t["text_muted"]
                ).pack()

            frame_details = tk.Frame(info_row, bg=t["bg_input"])
            frame_details.pack(side="left", fill="both", expand=True)

            ch_name = result.get("name", language.t("common.unknown"))
            guild_name = result.get("guild_name", language.t("main_page.channel_unknown_server"))
            type_name = result.get("type_name", language.t("common.unknown"))
            guild_id = result.get("guild_id", "N/A")

            tk.Label(
                frame_details,
                text=f"#{ch_name}  ({type_name})",
                bg=t["bg_input"],
                fg=t["text_primary"],
                font=FONT_BODY_BOLD,
                anchor="w"
            ).pack(anchor="w")

            tk.Label(
                frame_details,
                text=f"Server: {guild_name} (ID: {guild_id})",
                bg=t["bg_input"],
                fg=t["text_secondary"],
                font=FONT_CAPTION,
                anchor="w"
            ).pack(anchor="w", pady=(3, 0))
        else:
            error_text = language.t(
                "main_page.validator_error_prefix",
                result.get("error", language.t("main_page.channel_error_default"))
            )
            tk.Label(
                frame_ch,
                text=error_text,
                bg=t["bg_input"],
                fg=t["danger"],
                font=FONT_CAPTION,
                anchor="w"
            ).pack(anchor="w")

    btn_close = create_styled_button(
        container,
        text=language.t("main_page.validator_close"),
        command=validator_window.destroy,
        variant="secondary",
        padx=18,
        pady=6
    )
    btn_close.pack(anchor="e")
    btn_close.config(state="disabled")

    threading.Thread(target=worker, daemon=True).start()
    validator_window.after(100, poll)


def create_main_page(root, on_profile_changed=None):
    """
    Tạo trang chính với bố cục 2 cột (Cấu hình chạy / Live Log Terminal)

    Args:
        root: Root window
        on_profile_changed: callback khi đổi/sửa profile ở panel trái

    Returns:
        tuple: (frame_main_page, frame_content, txt_tokens, txt_channels,
                txt_messages, entry_min, entry_max, lbl_status, log_area,
                btn_start, btn_stop, btn_validate,
                profiles_ctx)
    """
    t = get_theme()

    frame_main_page = tk.Frame(root, bg=t["bg_app"])

    frame_content = tk.Frame(frame_main_page, bg=t["bg_app"])
    frame_content.pack(fill="both", expand=True, padx=20, pady=14)

    # Chia layout thành 2 khu vực: Left Pane (Inputs) & Right Pane (Log Terminal)
    pane_container = tk.Frame(frame_content, bg=t["bg_app"])
    pane_container.pack(fill="both", expand=True)

    left_pane = tk.Frame(pane_container, bg=t["bg_app"])
    left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))

    right_pane = tk.Frame(pane_container, bg=t["bg_app"], width=420)
    right_pane.pack(side="right", fill="both", expand=True, padx=(10, 0))

    # =========================================================================
    # LEFT PANE: PROFILES + STATUS + CONTROLS
    # Mỗi token là 1 profile riêng: token/channels/messages/cooldown riêng.
    # Tab TÍNH NĂNG sẽ sửa features của profile đang chọn ở đây.
    # =========================================================================
    from ui.profiles_panel import create_profiles_panel
    profiles_ctx = create_profiles_panel(left_pane, on_profile_changed=on_profile_changed)

    # Giữ các widget cũ dưới dạng ẩn để main.pyw không vỡ (start_trigger mới không dùng tới)
    hidden_holder = tk.Frame(left_pane)
    try:
        from utils.theme import create_styled_text as _mk_text, create_styled_entry as _mk_entry
        _, txt_tokens = _mk_text(hidden_holder, height=1)
        _, txt_channels = _mk_text(hidden_holder, height=1)
        _, txt_messages = _mk_text(hidden_holder, height=1)
        _, entry_min = _mk_entry(hidden_holder, width=8)
        _, entry_max = _mk_entry(hidden_holder, width=8)
        entry_min.insert(0, "60")
        entry_max.insert(0, "90")
    except Exception:
        txt_tokens = txt_channels = txt_messages = entry_min = entry_max = None
    try:
        hidden_holder.pack_forget()
    except Exception:
        pass

    status_holder, inner_inputs = create_card_frame(left_pane, padx=16, pady=14)
    status_holder.pack(fill="x", pady=(10, 0))

    # 5. Status Banner
    status_card = tk.Frame(
        inner_inputs,
        bg=t["bg_input"],
        highlightthickness=1,
        highlightbackground=t["border_subtle"],
        padx=12,
        pady=8
    )
    status_card.pack(fill="x", pady=(0, 12))

    lbl_status = tk.Label(
        status_card,
        text=language.t("main_page.status_stopped"),
        bg=t["bg_input"],
        fg=t["danger"],
        font=FONT_BODY_BOLD
    )
    lbl_status.pack(anchor="w")

    # 6. Action Buttons Grid
    frame_btn = tk.Frame(inner_inputs, bg=t["bg_panel"])
    frame_btn.pack(fill="x")

    # Nút KIỂM TRA gộp (menu dropdown) thay cho 2 nút dài dễ bấm nhầm cạnh BẬT/DỪNG:
    # main.pyw sẽ nối lệnh kiểm token/kênh vào 2 mục của btn_validate.menu
    def _post_check_menu():
        try:
            check_menu.tk_popup(
                btn_validate.winfo_rootx(),
                btn_validate.winfo_rooty() + btn_validate.winfo_height())
        except Exception:
            pass

    btn_validate = create_styled_button(
        frame_btn,
        text=language.t("main_page.btn_check_menu"),
        command=_post_check_menu,
        variant="secondary",
        padx=10,
        pady=7
    )
    btn_validate.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="ew")

    check_menu = tk.Menu(btn_validate, tearoff=0)
    check_menu.add_command(label=language.t("main_page.btn_validate"),
                           command=lambda: None)
    check_menu.add_command(label=language.t("main_page.btn_validate_channels"),
                           command=lambda: None)
    btn_validate.menu = check_menu  # main.pyw nối 2 lệnh kiểm tra vào đây

    btn_start = create_styled_button(
        frame_btn,
        text=language.t("main_page.btn_start"),
        command=lambda: None,
        variant="primary",
        padx=12,
        pady=7
    )
    btn_start.grid(row=0, column=1, padx=(0, 5), pady=2, sticky="ew")

    btn_stop = create_styled_button(
        frame_btn,
        text=language.t("main_page.btn_stop"),
        command=lambda: None,
        variant="danger",
        padx=12,
        pady=7
    )
    btn_stop.grid(row=0, column=2, pady=2, sticky="ew")

    frame_btn.grid_columnconfigure(0, weight=1)
    frame_btn.grid_columnconfigure(1, weight=1)
    frame_btn.grid_columnconfigure(2, weight=1)

    # =========================================================================
    # RIGHT PANE: LIVE TERMINAL LOG
    # =========================================================================
    card_log, inner_log = create_card_frame(right_pane, padx=14, pady=12)
    card_log.pack(fill="both", expand=True)

    log_header = tk.Frame(inner_log, bg=t["bg_panel"])
    log_header.pack(fill="x", pady=(0, 8))

    tk.Label(
        log_header,
        text=language.t("main_page.log_label"),
        bg=t["bg_panel"],
        fg=t["text_primary"],
        font=FONT_BODY_BOLD
    ).pack(side="left")

    # Terminal Log Frame
    terminal_frame = tk.Frame(
        inner_log,
        bg=t["log_bg"],
        highlightthickness=1,
        highlightbackground=t["border"]
    )
    terminal_frame.pack(fill="both", expand=True)

    log_area = scrolledtext.ScrolledText(
        terminal_frame,
        bg=t["log_bg"],
        fg=t["log_fg"],
        insertbackground=t["text_primary"],
        font=FONT_CODE,
        relief="flat",
        bd=6,
        wrap="word"
    )
    log_area.pack(fill="both", expand=True)

    # Tag styles for log highlights
    log_area.tag_config("system", foreground=t["accent"])
    log_area.tag_config("success", foreground=t["success"])
    log_area.tag_config("fail", foreground=t["danger"])
    log_area.tag_config("wait", foreground=t["text_muted"])
    log_area.tag_config("delete", foreground=t["info"])

    return (
        frame_main_page, frame_content, txt_tokens, txt_channels,
        txt_messages, entry_min, entry_max, lbl_status, log_area,
        btn_start, btn_stop, btn_validate,
        profiles_ctx
    )
