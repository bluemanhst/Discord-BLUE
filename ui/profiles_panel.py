# ui/profiles_panel.py
# Panel Master-Detail: danh sách Profile / token bên trái, editor bên phải
# Author: bluemanhst

import tkinter as tk
from tkinter import messagebox
from utils.theme import (
    get_theme, create_card_frame, create_styled_button,
    create_styled_entry,
    FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION, FONT_CODE
)
from config import config_data
import language
import threading


def _short_profile_name(profile, index=1):
    try:
        from profiles import short_profile_name
        return short_profile_name(profile, index=index)
    except Exception:
        name = str((profile or {}).get("name") or f"Acc {index}").strip() or f"Acc {index}"
        return name


def create_profiles_panel(parent, on_profile_changed=None):
    """Tạo panel quản lý profile riêng cho từng token."""
    t = get_theme()
    state = {"index": 0, "loading": False}

    def _get_profiles():
        """Luôn đọc list mới nhất từ config (tránh stale sau ensure in-place)."""
        return config_data.setdefault("profiles", [])

    def current_profile():
        from profiles import default_profile, normalize_profile
        plist = _get_profiles()
        if not plist:
            plist.append(normalize_profile(default_profile(name="Acc 1"), index=1))
        state["index"] = max(0, min(state["index"], len(plist) - 1))
        return plist[state["index"]]

    card, inner = create_card_frame(parent, padx=14, pady=12)
    card.pack(fill="both", expand=True)

    header = tk.Frame(inner, bg=t["bg_panel"])
    header.pack(fill="x", pady=(0, 8))
    tk.Label(
        header,
        text=language.t("profiles_panel.title"),
        bg=t["bg_panel"], fg=t["text_primary"], font=FONT_BODY_BOLD,
    ).pack(side="left")
    lbl_editing = tk.Label(
        header, text="", bg=t["bg_panel"], fg=t["accent"], font=FONT_BODY_BOLD,
    )
    lbl_editing.pack(side="right")

    body = tk.Frame(inner, bg=t["bg_panel"])
    body.pack(fill="both", expand=True)

    left = tk.Frame(body, bg=t["bg_panel"], width=200)
    left.pack(side="left", fill="y", padx=(0, 10))
    left.pack_propagate(False)

    listbox = tk.Listbox(
        left, bg=t["bg_input"], fg=t["text_primary"],
        selectbackground=t["accent"], selectforeground="#FFFFFF",
        font=FONT_BODY, relief="flat", bd=4, highlightthickness=1,
        highlightbackground=t["border"], exportselection=False,
    )
    listbox.pack(fill="both", expand=True)

    btn_row = tk.Frame(left, bg=t["bg_panel"])
    btn_row.pack(fill="x", pady=(8, 0))
    btn_add = create_styled_button(btn_row, text=language.t("profiles_panel.add"),
                                   command=lambda: None, variant="secondary", padx=8, pady=4)
    btn_add.pack(side="left", expand=True, fill="x", padx=(0, 4))
    btn_dup = create_styled_button(btn_row, text=language.t("profiles_panel.duplicate"),
                                   command=lambda: None, variant="secondary", padx=8, pady=4)
    btn_dup.pack(side="left", expand=True, fill="x", padx=(0, 4))
    btn_del = create_styled_button(btn_row, text=language.t("profiles_panel.delete"),
                                   command=lambda: None, variant="danger", padx=8, pady=4)
    btn_del.pack(side="left", expand=True, fill="x")

    right = tk.Frame(body, bg=t["bg_panel"])
    right.pack(side="left", fill="both", expand=True)

    top_row = tk.Frame(right, bg=t["bg_panel"])
    top_row.pack(fill="x", pady=(0, 6))
    var_enabled = tk.BooleanVar(value=True)
    chk_enabled = tk.Checkbutton(
        top_row, text=language.t("profiles_panel.enabled"),
        variable=var_enabled, bg=t["bg_panel"], fg=t["text_primary"],
        selectcolor=t["bg_input"], activebackground=t["bg_panel"],
        activeforeground=t["text_primary"], font=FONT_BODY_BOLD, cursor="hand2",
    )
    chk_enabled.pack(side="left")
    tk.Label(top_row, text=language.t("profiles_panel.name"),
             bg=t["bg_panel"], fg=t["text_secondary"], font=FONT_BODY).pack(side="left", padx=(12, 6))
    _, entry_name = create_styled_entry(top_row, width=18)
    entry_name.master.pack(side="left")

    tk.Label(right, text=language.t("profiles_panel.token"),
             bg=t["bg_panel"], fg=t["text_primary"], font=FONT_BODY_BOLD).pack(anchor="w")
    token_row = tk.Frame(right, bg=t["bg_panel"])
    token_row.pack(fill="x", pady=(4, 8))
    _, txt_token = create_styled_entry(token_row, width=40)
    txt_token.master.pack(side="left", fill="x", expand=True)
    btn_check_token = create_styled_button(
        token_row, text=language.t("profiles_panel.check_token"),
        command=lambda: None, variant="secondary", padx=10, pady=4)
    btn_check_token.pack(side="right", padx=(6, 0))

    tk.Label(right, text=language.t("profiles_panel.channels"),
             bg=t["bg_panel"], fg=t["text_primary"], font=FONT_BODY_BOLD).pack(anchor="w")
    btn_edit_channels = create_styled_button(right, text=language.t("profiles_panel.channels_btn"),
                                                command=lambda: None, width=24)
    btn_edit_channels.pack(fill="x", pady=(4, 2))
    _, label_channels_summary = create_styled_entry(right, width=40)
    label_channels_summary.master.pack(fill="x", pady=(0, 8))

    tk.Label(right, text=language.t("profiles_panel.messages"),
             bg=t["bg_panel"], fg=t["text_primary"], font=FONT_BODY_BOLD).pack(anchor="w")
    btn_edit_chat = create_styled_button(right, text=language.t("profiles_panel.messages_btn"),
                                         command=lambda: None, width=24)
    btn_edit_chat.pack(fill="x", pady=(4, 2))
    _, label_chat_summary = create_styled_entry(right, width=40)
    label_chat_summary.master.pack(fill="x", pady=(0, 8))

    # Option B: Ẩn CD mặc định của acc (chỉ giữ trong JSON để migrate cũ).
    # Mọi cooldown chạy theo CD riêng từng kênh trong popup.
    cool_row = tk.Frame(right, bg=t["bg_panel"])
    # Không pack cool_row -> ẩn khỏi UI, giữ entry ẩn để code cũ không lỗi.
    _, entry_p_min = create_styled_entry(cool_row, width=8)
    entry_p_min.insert(0, "60")
    _, entry_p_max = create_styled_entry(cool_row, width=8)
    entry_p_max.insert(0, "90")

    tk.Label(right, text=language.t("profiles_panel.hint"),
             bg=t["bg_panel"], fg=t["text_muted"], font=FONT_CAPTION,
             justify="left", wraplength=420).pack(fill="x", pady=(2, 0))
    def refresh_list(select_index=None):
        plist = _get_profiles()
        if select_index is not None:
            state["index"] = select_index
        listbox.delete(0, tk.END)
        for i, prof in enumerate(plist):
            listbox.insert(tk.END, _short_profile_name(prof, index=i + 1))
        if plist:
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(state["index"])
            listbox.see(state["index"])

    def save_current_to_model():
        plist = _get_profiles()
        if not plist:
            return
        prof = current_profile()
        prof["enabled"] = bool(var_enabled.get())
        prof["name"] = entry_name.get().strip() or prof.get("name", "Acc 1")
        prof["token"] = txt_token.get().strip()
        if not isinstance(prof.get("messages"), list):
            prof["messages"] = []
        _sync_channels(prof)
        # Option B: CD acc ẩn UI -> giữ nguyên số trong JSON, không đọc từ
        # entry ẩn (tránh ghi đè 60/90 lên data migrate cũ).

    def open_channels_editor():
        from tkinter import messagebox
        from tkinter import ttk

        prof = current_profile()
        title = language.t("profiles_panel.channels_editor_title").format(prof.get("name", "Acc 1"))
        win = tk.Toplevel(card)
        win.title(title)
        win.transient(card)
        win.grab_set()
        win.configure(bg=t["bg_panel"])
        win.columnconfigure(0, weight=1)
        win.rowconfigure(2, weight=1)

        tk.Label(win, text=title, bg=t["bg_panel"], fg=t["text_primary"],
                 font=FONT_BODY_BOLD, anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 4))
        tk.Label(win, text=language.t("profiles_panel.channels_hint",
                                      prof.get("cooldown_min", 60),
                                      prof.get("cooldown_max", 90)),
                 bg=t["bg_panel"], fg=t["text_secondary"], wraplength=440,
                 justify="left").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8))

        cols = ("id", "cd_min", "cd_max", "chat")
        # Treeview tối giống trang chính: style riêng cho popup — dòng nền tối,
        # chữ trắng sáng, heading rõ chữ (không phụ thuộc style global)
        style = ttk.Style(win)
        style.configure("Blue.Treeview",
                        background=t["bg_input"],
                        fieldbackground=t["bg_input"],
                        foreground=t["text_primary"],
                        borderwidth=0,
                        font=FONT_BODY,
                        rowheight=26)
        style.map("Blue.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("Blue.Treeview.Heading",
                        background=t["bg_sidebar"],
                        foreground=t["text_primary"],
                        font=FONT_BODY_BOLD,
                        padding=(8, 6))
        style.map("Blue.Treeview.Heading",
                  background=[("active", t["bg_hover"])],
                  foreground=[("active", t["text_primary"])])
        tree = ttk.Treeview(win, columns=cols, show="headings", height=7,
                            style="Blue.Treeview")
        for c, w in zip(cols, (130, 80, 80, 70)):
            tree.heading(c, text=language.t("profiles_panel.column_" + c))
            tree.column(c, width=w, anchor="w")
        tree_sb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_sb.set)
        tree.grid(row=2, column=0, sticky="nsew", padx=(12, 0), pady=(0, 8))
        tree_sb.grid(row=2, column=1, sticky="ns", padx=(0, 12), pady=(0, 8))
        win.rowconfigure(2, weight=1)

        def refresh_tree():
            for r in tree.get_children():
                tree.delete(r)
            for c in prof.get("channels") or []:
                own = [m for m in (c.get("messages") or []) if str(m).strip()]
                # Cột Chat: số tin riêng, "-" = đang dùng chat mặc định của acc
                tree.insert("", "end",
                            values=(c["id"], c["cd_min"], c["cd_max"],
                                    str(len(own)) if own else "-"))

        def select_row(_evt=None):
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0], "values")
            id_var.set(vals[0] or "")
            min_var.set(vals[1] or "")
            max_var.set(vals[2] or "")

        tree.bind("<<TreeviewSelect>>", select_row)

        id_var = tk.StringVar()
        min_var = tk.StringVar()
        max_var = tk.StringVar()
        entry_row = tk.Frame(win, bg=t["bg_panel"])
        entry_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        entry_row.columnconfigure(0, weight=1)
        tk.Label(entry_row, text=language.t("profiles_panel.column_id"),
                 bg=t["bg_panel"], fg=t["text_secondary"], font=FONT_BODY).grid(
            row=0, column=0, sticky="w", padx=(0, 4))
        _, entry_id = create_styled_entry(entry_row, width=18)
        entry_id.config(textvariable=id_var)
        entry_id.master.grid(row=0, column=1, sticky="w")
        tk.Label(entry_row, text=language.t("profiles_panel.column_cd_min"),
                 bg=t["bg_panel"], fg=t["text_secondary"], font=FONT_BODY).grid(
            row=0, column=2, sticky="w", padx=(14, 4))
        _, entry_min = create_styled_entry(entry_row, width=8)
        entry_min.config(textvariable=min_var)
        entry_min.master.grid(row=0, column=3, sticky="w")
        tk.Label(entry_row, text=language.t("profiles_panel.column_cd_max"),
                 bg=t["bg_panel"], fg=t["text_secondary"], font=FONT_BODY).grid(
            row=0, column=4, sticky="w", padx=(14, 4))
        _, entry_max = create_styled_entry(entry_row, width=8)
        entry_max.config(textvariable=max_var)
        entry_max.master.grid(row=0, column=5, sticky="w")

        def parse_int(v):
            try:
                return max(0, int(float(str(v).strip())))
            except (TypeError, ValueError):
                return None

        def add_channels():
            # Hỗ trợ dán nhiều ID 1 lần: tách theo space/enter/dấu phẩy/chấm phẩy
            raw = id_var.get().replace(",", " ").replace(";", " ")
            ids = [x for x in raw.split() if x]
            if not ids:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.channel_id_required"))
                return
            bad = [x for x in ids if not x.isdigit()]
            if bad:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.invalid_channel_ids",
                                                  ", ".join(bad)))
                return
            mn = parse_int(min_var.get())
            mx = parse_int(max_var.get())
            if mn is None or mx is None:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.invalid_cooldown"))
                return
            if mn > mx:
                mn, mx = mx, mn
            chs = prof.get("channels") or []
            have = {str(c.get("id") or "").lower() for c in chs}
            new_ids, dup_ids = [], []
            for cid in ids:
                if cid.lower() in have:
                    dup_ids.append(cid)
                else:
                    have.add(cid.lower())
                    new_ids.append(cid)
            if not new_ids and dup_ids:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.dup_channel",
                                                  ", ".join(dup_ids)))
                return
            for cid in new_ids:
                chs.append({"id": cid, "cd_min": mn, "cd_max": mx, "messages": []})
            if dup_ids:
                # Fix mất cập nhật lần 2: ID đã tồn tại -> ghi đè CD mới.
                want = {d.lower() for d in dup_ids}
                for c in chs:
                    if str(c.get("id") or "").lower() in want:
                        c["cd_min"], c["cd_max"] = mn, mx
            prof["channels"] = chs
            refresh_tree()
            id_var.set("")
            min_var.set("")
            max_var.set("")
            _sync_channels(prof)
            try:
                from config import save_config
                save_config(config_data)
            except Exception:
                pass
            _notify_changed()
            if dup_ids:
                messagebox.showinfo(language.t("common.info_title"),
                                     language.t("profiles_panel.channels_added",
                                                len(new_ids), len(dup_ids)))

        def update_selected():
            """Sửa ID/CD của kênh ĐANG CHỌN trong bảng (khác với Thêm = tạo mới)."""
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.update_select_channel"))
                return
            old_id = str(tree.item(sel[0], "values")[0])
            raw = id_var.get().replace(",", " ").replace(";", " ")
            ids = [x for x in raw.split() if x]
            if not ids:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.channel_id_required"))
                return
            if len(ids) > 1:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.update_single_channel"))
                return
            new_id = ids[0]
            if not new_id.isdigit():
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.invalid_channel_ids",
                                                  new_id))
                return
            mn = parse_int(min_var.get())
            mx = parse_int(max_var.get())
            if mn is None or mx is None:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.invalid_cooldown"))
                return
            if mn > mx:
                mn, mx = mx, mn
            chs = prof.get("channels") or []
            # Đổi ID không được trùng kênh khác
            if (new_id.lower() != old_id.lower()
                    and any(str(c.get("id") or "").lower() == new_id.lower()
                            for c in chs)):
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.dup_channel", new_id))
                return
            target = next((c for c in chs
                           if str(c.get("id") or "") == old_id), None)
            if target is None:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.update_select_channel"))
                return
            target["id"] = new_id
            target["cd_min"], target["cd_max"] = mn, mx
            prof["channels"] = chs
            refresh_tree()
            # Chọn lại dòng vừa sửa (select_row tự nạp ID/CD vào ô nhập)
            for r in tree.get_children():
                if str(tree.item(r, "values")[0]) == new_id:
                    tree.selection_set(r)
                    tree.see(r)
                    break
            _sync_channels(prof)
            try:
                from config import save_config
                save_config(config_data)
            except Exception:
                pass
            _notify_changed()
            messagebox.showinfo(language.t("common.info_title"),
                                language.t("profiles_panel.channel_updated", new_id))

        def remove_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.remove_selected"))
                return
            if messagebox.askyesno(language.t("common.warning_title"),
                                   language.t("profiles_panel.remove_channel_confirm")):
                chs = [c for c in prof.get("channels") or []
                       if c["id"].lower() != tree.item(sel[0], "values")[0].lower()]
                prof["channels"] = chs
                refresh_tree()
                _sync_channels(prof)
                try:
                    from config import save_config
                    save_config(config_data)
                except Exception:
                    pass
                _notify_changed()

        def _selected_channel():
            sel = tree.selection()
            if not sel:
                return None
            cid = str(tree.item(sel[0], "values")[0])
            for c in prof.get("channels") or []:
                if str(c.get("id") or "") == cid:
                    return c
            return None

        def edit_selected_chat():
            """Sửa chat riêng của kênh đang chọn (inline: ghi thẳng vào dict kênh)."""
            ch = _selected_channel()
            if ch is None:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_select_channel"))
                return
            title = language.t("profiles_panel.chat_editor_title").format(ch.get("id", ""))
            open_chat_editor(
                title,
                get_list=lambda c=ch: c.setdefault("messages", []),
                set_list=lambda v, c=ch: c.__setitem__("messages", v),
                on_change=refresh_tree,
                default_getter=lambda: prof.get("messages") or [],
                channel_id=str(ch.get("id") or ""))

        def check_selected_channels():
            """Kiểm kênh của acc này - chọn 1 kênh thì kiểm kênh đó, chưa chọn thì hỏi kiểm tất cả."""
            token = str(prof.get("token") or "").strip()
            if not token:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.check_token_empty"))
                return
            sel = tree.selection()
            if sel:
                ids = [str(tree.item(sel[0], "values")[0])]
            else:
                ids = [str(c.get("id") or "").strip()
                       for c in prof.get("channels") or []]
                ids = [i for i in ids if i]
                if ids and not messagebox.askyesno(
                        language.t("common.warning_title"),
                        language.t("profiles_panel.check_all_confirm")):
                    return
            if not ids:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("main_page.channel_validator_no_channels"))
                return
            try:
                from ui.main_page import validate_channel_items
            except ImportError:
                return
            acc = str(prof.get("name") or "").strip()
            validate_channel_items([{"acc": acc, "tokens": [token], "channel_id": cid}
                                    for cid in ids])

        btn_row2 = tk.Frame(win, bg=t["bg_panel"])
        btn_row2.grid(row=4, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        btn_row2.columnconfigure(2, weight=1)
        create_styled_button(btn_row2, text=language.t("profiles_panel.add_channel"),
                             command=add_channels, variant="primary",
                             padx=14, pady=4).grid(row=0, column=0, sticky="ew", pady=2)
        create_styled_button(btn_row2, text=language.t("profiles_panel.update_channel"),
                             command=update_selected, variant="primary",
                             padx=14, pady=4).grid(row=0, column=1, sticky="ew",
                                                   padx=(4, 0), pady=2)
        create_styled_button(btn_row2, text=language.t("profiles_panel.remove_channel"),
                             command=remove_selected, variant="danger",
                             padx=14, pady=4).grid(row=0, column=2, sticky="ew",
                                                   padx=(4, 0), pady=2)
        create_styled_button(btn_row2, text=language.t("profiles_panel.done"),
                             command=win.destroy, variant="secondary",
                             padx=14, pady=4).grid(row=0, column=3, sticky="ew",
                                                   padx=(4, 0), pady=2)

        # Hàng nút thứ 2: chat riêng của kênh + kiểm kênh bằng token acc này
        btn_row3 = tk.Frame(win, bg=t["bg_panel"])
        btn_row3.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))
        btn_row3.columnconfigure(0, weight=1)
        btn_row3.columnconfigure(1, weight=1)
        create_styled_button(btn_row3, text=language.t("profiles_panel.edit_chat"),
                             command=edit_selected_chat, variant="primary",
                             padx=14, pady=4).grid(
            row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
        create_styled_button(btn_row3, text=language.t("profiles_panel.check_channels"),
                             command=check_selected_channels, variant="secondary",
                             padx=14, pady=4).grid(
            row=0, column=1, sticky="ew", pady=2)

        refresh_tree()

    def _messages_summary(msgs):
        msgs = [m for m in (msgs or []) if str(m).strip()]
        if not msgs:
            return ""
        first_line = str(msgs[0]).splitlines()[0].strip()
        if len(first_line) > 32:
            first_line = first_line[:32] + "..."
        return f"{len(msgs)} x {first_line}"

    def _refresh_chat_summary(prof=None):
        try:
            prof = prof or current_profile()
            label_chat_summary.delete(0, tk.END)
            label_chat_summary.insert(0, _messages_summary(prof.get("messages") or []))
        except Exception:
            pass

    def open_chat_editor(title_text, get_list, set_list, on_change=None, default_getter=None,
                         channel_id=None):
        """
        Popup sửa list tin nhắn (chat mặc định của acc hoặc chat riêng của kênh).
        Mỗi mục = 1 tin nhắn; Shift+Enter để xuống hàng BÊN TRONG tin nhắn (đa dòng).
        channel_id: kênh chứa guild -> tra emoji server cho ô Xem trước (bỏ qua được).
        """
        win = tk.Toplevel(card)
        win.title(title_text)
        win.transient(card)
        win.grab_set()
        win.minsize(480, 400)
        win.columnconfigure(0, weight=1)
        win.rowconfigure(2, weight=1)
        win.configure(bg=t["bg_panel"])

        tk.Label(win, text=title_text, bg=t["bg_panel"], fg=t["text_primary"],
                 font=FONT_BODY_BOLD, anchor="w").grid(
            row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        tk.Label(win, text=language.t("profiles_panel.chat_editor_hint"),
                 bg=t["bg_panel"], fg=t["text_secondary"], wraplength=440,
                 justify="left").grid(
            row=1, column=0, sticky="w", padx=12, pady=(0, 8))

        list_frame = tk.Frame(win, bg=t["bg_panel"])
        list_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        lb = tk.Listbox(list_frame, bg=t["bg_input"], fg=t["text_primary"],
                        selectbackground=t["accent"], selectforeground="#FFFFFF",
                        font=FONT_BODY, relief="flat", bd=4, highlightthickness=1,
                        highlightbackground=t["border"], exportselection=False, height=6)
        sb = tk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.config(yscrollcommand=sb.set)
        lb.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        editor = tk.Text(list_frame, height=4, bg=t["bg_input"], fg=t["text_primary"],
                         insertbackground=t["text_primary"], font=FONT_BODY,
                         relief="flat", bd=4, highlightthickness=1,
                         highlightbackground=t["border"], wrap="word")
        editor.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Ô soạn hiện viền cam khi click vào nhập (giống ô input trang chính)
        def _editor_focus_in(_e):
            editor.config(highlightbackground=t["border_focus"])

        def _editor_focus_out(_e):
            editor.config(highlightbackground=t["border"])

        editor.bind("<FocusIn>", _editor_focus_in)
        editor.bind("<FocusOut>", _editor_focus_out)

        # Đếm ký tự trực tiếp (Discord giới hạn 2000 ký tự/tin)
        lbl_len = tk.Label(list_frame, text=language.t("profiles_panel.chat_len_counter", 0),
                           bg=t["bg_panel"], fg=t["text_muted"], font=FONT_BODY, anchor="w")
        lbl_len.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        def _update_len(_evt=None):
            n = len(_editor_text())
            lbl_len.config(text=language.t("profiles_panel.chat_len_counter", n),
                           fg=t["danger"] if n > 2000 else t["text_muted"])

        # ===== Xem trước Discord: emoji server + markdown (ô soạn giữ text gốc) =====
        lbl_preview = tk.Label(list_frame,
                               text=language.t("profiles_panel.chat_preview"),
                               bg=t["bg_panel"], fg=t["text_secondary"],
                               font=FONT_BODY, anchor="w")
        lbl_preview.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        preview = tk.Text(list_frame, height=3, bg=t["bg_input"], fg=t["text_primary"],
                          font=FONT_BODY, relief="flat", bd=4, highlightthickness=1,
                          highlightbackground=t["border"], wrap="word",
                          state="disabled", cursor="arrow")
        preview.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        from utils.chat_markup import parse_markup

        _emoji_map = {}     # name_lower -> {"id","animated"} (tu guild API)
        _img_bytes = {}     # emoji_id -> bytes anh da tai
        _img_photos = {}    # emoji_id -> PhotoImage (giu reference cho Text)
        _img_pending = set()

        try:
            import tkinter.font as tkfont
            _fam, _sz = FONT_BODY[0], FONT_BODY[1]
            preview.tag_config("bold", font=tkfont.Font(family=_fam, size=_sz, weight="bold"))
            preview.tag_config("italic", font=tkfont.Font(family=_fam, size=_sz, slant="italic"))
            preview.tag_config("bold_italic", font=tkfont.Font(
                family=_fam, size=_sz, weight="bold", slant="italic"))
            preview.tag_config("code", font=tkfont.Font(family=FONT_CODE[0], size=FONT_CODE[1]),
                               background=t["bg_hover"])
            preview.tag_config("underline", underline=True)
            preview.tag_config("strike", overstrike=True)
            preview.tag_config("unknown_emoji", foreground=t["danger"])
        except Exception:
            pass

        def _style_tags(styles):
            styles = set(styles or ())
            if "code" in styles:
                return ("code",)
            tags = []
            if "bold" in styles and "italic" in styles:
                tags.append("bold_italic")
            elif "bold" in styles:
                tags.append("bold")
            elif "italic" in styles:
                tags.append("italic")
            if "underline" in styles:
                tags.append("underline")
            if "strike" in styles:
                tags.append("strike")
            return tuple(tags)

        def _photo(eid):
            """Chuyen bytes -> PhotoImage lan dau tien, sau do lay tu cache."""
            photo = _img_photos.get(eid)
            if photo is not None:
                return photo
            data = _img_bytes.get(eid)
            if data is None:
                return None
            try:
                import io
                from PIL import Image, ImageTk
                img = Image.open(io.BytesIO(data))
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                _img_photos[eid] = photo
                return photo
            except Exception:
                return None

        def _fetch_img_async(eid, animated):
            """Tai anh emoji trong thread rieng (khong block UI); xong -> render lai."""
            if not eid or eid in _img_pending or eid in _img_bytes:
                return
            _img_pending.add(eid)

            def _work():
                try:
                    import requests
                    from discord.guild_emojis import emoji_image_url
                    r = requests.get(emoji_image_url(eid, animated), timeout=6)
                    if r.status_code == 200:
                        _img_bytes[eid] = r.content
                except Exception:
                    pass
                _img_pending.discard(eid)
                try:
                    if win.winfo_exists():
                        win.after(0, _render_preview)
                except Exception:
                    pass

            threading.Thread(target=_work, daemon=True).start()

        def _render_preview(*_a):
            try:
                if not win.winfo_exists():
                    return
            except Exception:
                return
            raw = editor.get("1.0", "end-1c")
            try:
                preview.config(state="normal")
                preview.delete("1.0", tk.END)
                for seg in parse_markup(raw):
                    stype = seg.get("type")
                    if stype == "newline":
                        preview.insert("end", "\n")
                    elif stype == "text":
                        preview.insert("end", seg.get("text") or "",
                                       _style_tags(seg.get("styles")))
                    else:
                        eid, animated, name = None, False, seg.get("name") or ""
                        if stype == "emoji_id":
                            eid, animated = seg.get("id"), bool(seg.get("animated"))
                        elif stype == "emoji_name":
                            info = _emoji_map.get(name.lower())
                            if info:
                                eid, animated = info.get("id"), bool(info.get("animated"))
                        photo = _photo(eid) if eid else None
                        if photo is not None:
                            preview.image_create("end", image=photo)
                        else:
                            if eid:
                                _fetch_img_async(eid, animated)
                            # Chua tra duoc (kho load/guild loi) -> giu text, mau do
                            preview.insert("end", f":{name}:", ("unknown_emoji",))
            finally:
                try:
                    preview.config(state="disabled")
                except Exception:
                    pass

        def _on_editor_change(*_a):
            _update_len()
            _render_preview()

        # Tra list emoji cua guild chua channel dang sua chat (thread rieng)
        if channel_id:
            _tok = str(current_profile().get("token") or "").strip()
            if _tok:
                lbl_preview.config(text=language.t("profiles_panel.chat_preview_loading"))

                def _after_guild_loaded():
                    try:
                        if win.winfo_exists():
                            lbl_preview.config(
                                text=language.t("profiles_panel.chat_preview"))
                            _render_preview()
                    except Exception:
                        pass

                def _load_guild_emojis():
                    from discord.guild_emojis import fetch_emojis_for_channel
                    try:
                        found = fetch_emojis_for_channel(str(channel_id), _tok)
                    except Exception:
                        found = {}
                    _emoji_map.update(found or {})
                    try:
                        if win.winfo_exists():
                            win.after(0, _after_guild_loaded)
                    except Exception:
                        pass

                threading.Thread(target=_load_guild_emojis, daemon=True).start()

        editor.bind("<KeyRelease>", _on_editor_change)
        editor.bind("<<Paste>>", lambda _e: win.after(1, _on_editor_change))

        def refresh(selected=None):
            lb.delete(0, tk.END)
            for m in get_list():
                lines = str(m).splitlines() or [""]
                disp = lines[0]
                if len(lines) > 1:
                    disp += f" ↵ +{len(lines) - 1}"
                lb.insert(tk.END, disp)
            if selected is not None and 0 <= selected < lb.size():
                lb.selection_clear(0, tk.END)
                lb.selection_set(selected)
                lb.see(selected)

        def on_select(_evt=None):
            sel = lb.curselection()
            if not sel:
                return
            editor.delete("1.0", tk.END)
            editor.insert("1.0", str(get_list()[sel[0]]))
            _update_len()
            _render_preview()

        lb.bind("<<ListboxSelect>>", on_select)

        def _after_change():
            if callable(on_change):
                on_change()
            _notify_changed()
            _refresh_chat_summary()

        def _editor_text():
            return editor.get("1.0", "end-1c").strip()

        def do_add():
            msg = _editor_text()
            if not msg:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_msg_required"))
                return
            if len(msg) > 2000:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_msg_too_long",
                                                  len(msg)))
                return
            lst = list(get_list())
            lst.append(msg)
            set_list(lst)
            refresh(len(lst) - 1)
            editor.delete("1.0", tk.END)
            _on_editor_change()
            _after_change()

        def do_update():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_select_item"))
                return
            msg = _editor_text()
            if not msg:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_msg_required"))
                return
            if len(msg) > 2000:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_msg_too_long",
                                                  len(msg)))
                return
            lst = list(get_list())
            lst[sel[0]] = msg
            set_list(lst)
            refresh(sel[0])
            _after_change()

        def do_delete():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning(language.t("common.warning_title"),
                                       language.t("profiles_panel.chat_select_item"))
                return
            lst = list(get_list())
            del lst[sel[0]]
            set_list(lst)
            editor.delete("1.0", tk.END)
            _on_editor_change()
            refresh(min(sel[0], len(lst) - 1) if lst else None)
            _after_change()

        btns = tk.Frame(win, bg=t["bg_panel"])
        btns.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 10))

        def _mk(text, cmd, variant="secondary"):
            # Nút dùng chung design system: có hover (đổi màu khi rê chuột)
            b = create_styled_button(btns, text=text, command=cmd, variant=variant,
                                     padx=10, pady=4)
            b.pack(side="left", padx=(0, 6))
            return b

        _mk(language.t("profiles_panel.chat_add"), do_add, "primary")
        _mk(language.t("profiles_panel.chat_update"), do_update, "secondary")
        _mk(language.t("profiles_panel.chat_delete"), do_delete, "danger")

        if callable(default_getter):
            def copy_default():
                set_list([str(m) for m in default_getter() if str(m).strip()])
                refresh()
                editor.delete("1.0", tk.END)
                _on_editor_change()
                _after_change()

            def use_default():
                set_list([])
                refresh()
                editor.delete("1.0", tk.END)
                _on_editor_change()
                _after_change()

            _mk(language.t("profiles_panel.chat_copy_default"), copy_default)
            _mk(language.t("profiles_panel.chat_use_default"), use_default)

        spacer = tk.Frame(btns, bg=t["bg_panel"])
        spacer.pack(side="left", fill="x", expand=True)
        _mk(language.t("profiles_panel.done"), win.destroy)

        refresh()
        _on_editor_change()

    def open_default_chat_editor():
        """Sửa bộ chat mặc định của acc hiện tại."""
        prof = current_profile()
        title = language.t("profiles_panel.chat_editor_title").format(prof.get("name", "Acc 1"))
        # Emoji preview tra theo guild của kênh đầu tiên (chat acc không thuộc kênh nào)
        _chs = prof.get("channels") or []
        first_ch = str(_chs[0].get("id") or "").strip() if _chs else ""
        if not first_ch:
            _ids = [str(c or "").strip() for c in (prof.get("channel_ids") or [])]
            first_ch = next((i for i in _ids if i), "")
        open_chat_editor(
            title,
            get_list=lambda: prof.setdefault("messages", []),
            set_list=lambda v: prof.__setitem__("messages", v),
            on_change=lambda: _refresh_chat_summary(prof),
            channel_id=first_ch or None)

    def _check_current_token():
        """Kiểm tra token của acc đang chọn."""
        save_current_to_model()
        token = str(current_profile().get("token") or "").strip()
        if not token:
            messagebox.showwarning(language.t("common.warning_title"),
                                   language.t("profiles_panel.check_token_empty"))
            return
        try:
            from ui.main_page import validate_token_list
        except ImportError:
            return
        validate_token_list([token])

    def _channels_summary(prof):
        chs = prof.get("channels") or []
        if not chs:
            return ""
        return ", ".join(f"{c['id']}={c['cd_min']}-{c['cd_max']}s" for c in chs)

    def _sync_channels(prof):
        chs = prof.get("channels") or []
        prof["channel_ids"] = [c["id"] for c in chs]

    def load_profile_to_ui(index):
        state["loading"] = True
        try:
            plist = _get_profiles()
            if not plist:
                return
            index = max(0, min(int(index), len(plist) - 1))
            state["index"] = index
            prof = plist[index]
            var_enabled.set(bool(prof.get("enabled", True)))
            entry_name.delete(0, tk.END)
            entry_name.insert(0, str(prof.get("name", f"Acc {index + 1}")))
            txt_token.delete(0, tk.END)
            txt_token.insert(0, str(prof.get("token", "")))
            _refresh_chat_summary(prof)
            label_channels_summary.delete(0, tk.END)
            label_channels_summary.insert(0, _channels_summary(prof))
            entry_p_min.delete(0, tk.END)
            entry_p_min.insert(0, str(prof.get("cooldown_min", 60)))
            entry_p_max.delete(0, tk.END)
            entry_p_max.insert(0, str(prof.get("cooldown_max", 90)))
            lbl_editing.config(text=f"{language.t('profiles_panel.editing')} {prof.get('name', '')}")
        finally:
            state["loading"] = False

    def _notify_changed():
        try:
            if callable(on_profile_changed):
                on_profile_changed()
        except Exception:
            pass

    def on_select(_event=None):
        if state["loading"] or not _get_profiles():
            return
        sel = listbox.curselection()
        if not sel:
            return
        save_current_to_model()
        state["index"] = int(sel[0])
        load_profile_to_ui(state["index"])
        refresh_list(select_index=state["index"])
        _notify_changed()
    def on_add():
        save_current_to_model()
        from profiles import default_profile
        plist = _get_profiles()
        base = current_profile() if plist else default_profile()
        import copy
        import uuid
        new_prof = copy.deepcopy(base)
        new_prof["id"] = f"prof_{uuid.uuid4().hex[:8]}"
        new_prof["name"] = f"Acc {len(plist) + 1}"
        new_prof["token"] = ""
        plist.append(new_prof)
        refresh_list(select_index=len(plist) - 1)
        load_profile_to_ui(len(plist) - 1)
        _notify_changed()

    def on_duplicate():
        plist = _get_profiles()
        if not plist:
            return
        save_current_to_model()
        import copy
        import uuid
        src = copy.deepcopy(current_profile())
        src["id"] = f"prof_{uuid.uuid4().hex[:8]}"
        src["name"] = f"{src.get('name', 'Acc')} copy"
        plist.insert(state["index"] + 1, src)
        refresh_list(select_index=state["index"] + 1)
        load_profile_to_ui(state["index"] + 1)
        _notify_changed()

    def on_delete():
        plist = _get_profiles()
        if len(plist) <= 1:
            messagebox.showwarning(
                language.t("common.warning_title"),
                language.t("profiles_panel.keep_one"),
            )
            return
        plist.pop(state["index"])
        state["index"] = max(0, state["index"] - 1)
        refresh_list(select_index=state["index"])
        load_profile_to_ui(state["index"])
        _notify_changed()

    def on_field_change(*_args):
        if state["loading"]:
            return
        save_current_to_model()
        pos = listbox.curselection()
        refresh_list(select_index=pos[0] if pos else state["index"])
        try:
            prof = current_profile()
            lbl_editing.config(text=f"{language.t('profiles_panel.editing')} {prof.get('name', '')}")
        except Exception:
            pass
        _notify_changed()

    btn_add.config(command=on_add)
    btn_dup.config(command=on_duplicate)
    btn_del.config(command=on_delete)
    listbox.bind("<<ListboxSelect>>", on_select)
    var_enabled.trace_add("write", on_field_change)
    for widget in (entry_name, txt_token, entry_p_min, entry_p_max):
        widget.bind("<KeyRelease>", on_field_change)
        widget.bind("<FocusOut>", on_field_change)
    btn_edit_channels.config(command=open_channels_editor)
    btn_edit_chat.config(command=open_default_chat_editor)
    btn_check_token.config(command=_check_current_token)

    refresh_list(select_index=0)
    load_profile_to_ui(0)

    # Proxy trả về luôn đọc động từ config_data — tránh reference list cũ
    # (ensure_profiles/panel từng giữ 2 list khác nhau -> mất cập nhật).
    class _ProfilesProxy:
        def _l(self):
            return _get_profiles()

        def __len__(self):
            return len(self._l())

        def __iter__(self):
            return iter(self._l())

        def __getitem__(self, i):
            return self._l()[i]

        def __bool__(self):
            return bool(self._l())

    return {
        "frame": card,
        "profiles": _ProfilesProxy(),
        "get_selected_index": lambda: state["index"],
        "get_selected_profile": lambda: current_profile(),
        "save_current": save_current_to_model,
        "open_channels_editor": open_channels_editor,
        "channels_summary": _channels_summary,
        "refresh": refresh_list,
    }