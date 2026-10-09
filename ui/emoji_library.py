# ui/emoji_library.py
# Chon server dung emoji (Nitro): danh sach server ten + avatar + checkbox,
# KHONG tai emoji o at -> het lag. Ghi vao profile["emoji_guilds"].
# Preview/bot resolve :ten: tu server da tick (+ guild cua channel uu tien).
# Author: bluemanhst

import threading

import tkinter as tk

from utils.theme import (get_theme, create_card_frame, create_styled_button,
                         create_styled_entry, FONT_BODY, FONT_BODY_BOLD)

import language

_AVATAR_POOL = None
_AVATAR_SESSION = None
_AVATAR_BYTES = {}
_AVATAR_PHOTOS = {}
_AVATAR_PENDING = set()


def _avatar_pool():
    global _AVATAR_POOL
    if _AVATAR_POOL is None:
        from concurrent.futures import ThreadPoolExecutor
        _AVATAR_POOL = ThreadPoolExecutor(max_workers=4,
                                          thread_name_prefix="avatar")
    return _AVATAR_POOL


def _avatar_session():
    global _AVATAR_SESSION
    if _AVATAR_SESSION is None:
        import requests
        _AVATAR_SESSION = requests.Session()
    return _AVATAR_SESSION


def _var_true(var):
    try:
        return bool(var.get()) if var is not None else False
    except Exception:
        return False




def open_emoji_library(parent, get_profile, save_profile, token,
                       channel_id=None, on_change=None):
    """Popup chon server dung emoji cho acc hien tai."""
    t = get_theme()
    win = tk.Toplevel(parent)
    win.title(language.t("profiles_panel.emoji_picker_title"))
    win.geometry("460x540")
    win.configure(bg=t["bg_panel"])
    win.transient(parent)

    card, inner = create_card_frame(win, padx=12, pady=10)
    card.pack(fill="both", expand=True, padx=10, pady=10)

    hdr = tk.Frame(inner, bg=t["bg_panel"])
    hdr.pack(fill="x", pady=(0, 4))
    tk.Label(hdr, text=language.t("profiles_panel.emoji_picker_title"),
             bg=t["bg_panel"], fg=t["text_primary"],
             font=FONT_BODY_BOLD).pack(side="left")
    lbl_status = tk.Label(hdr, text=language.t("profiles_panel.emoji_loading"),
                          bg=t["bg_panel"], fg=t["text_muted"], font=FONT_BODY)
    lbl_status.pack(side="right")

    tk.Label(inner, text=language.t("profiles_panel.emoji_picker_hint"),
             bg=t["bg_panel"], fg=t["text_secondary"], font=FONT_BODY,
             wraplength=400, justify="left").pack(fill="x", pady=(0, 6))

    _srch_box, entry_search = create_styled_entry(inner, width=40)
    _srch_box.pack(fill="x", pady=(0, 6))
    entry_search.insert(0, language.t("profiles_panel.emoji_search_placeholder"))
    entry_search.config(fg=t["text_muted"])

    grid_card, grid_inner = create_card_frame(inner, padx=6, pady=6)
    grid_card.pack(fill="both", expand=True, pady=(6, 0))
    canvas = tk.Canvas(grid_inner, bg=t["bg_panel"], highlightthickness=0)
    scroll = tk.Scrollbar(grid_inner, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas, bg=t["bg_panel"])
    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    win_id = canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    frame.columnconfigure(0, weight=1)

    state = {"guilds": [], "vars": {}, "after_id": None, "gen": 0,
             "current_gid": None}

    def _on_focus_in(_e):
        if entry_search.get() == language.t("profiles_panel.emoji_search_placeholder"):
            entry_search.delete(0, tk.END)
            entry_search.config(fg=t["text_primary"])

    entry_search.bind("<FocusIn>", _on_focus_in)

    def _query():
        q = entry_search.get().strip().lower()
        ph = language.t("profiles_panel.emoji_search_placeholder").lower()
        return "" if q == ph else q

    def _avatar_for(gid, icon_hash):
        key = (str(gid), str(icon_hash or ""))
        ph = _AVATAR_PHOTOS.get(key)
        if ph is not None:
            return ph
        data = _AVATAR_BYTES.get(key)
        if data is None:
            return None
        try:
            import io
            from PIL import Image, ImageTk
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            img = img.resize((32, 32), Image.Resampling.BILINEAR)
            ph = ImageTk.PhotoImage(img)
            _AVATAR_PHOTOS[key] = ph
            return ph
        except Exception:
            return None

    def _apply_avatar(lbl, gid, icon_hash):
        try:
            if not win.winfo_exists() or not lbl.winfo_exists():
                return
        except Exception:
            return
        ph = _avatar_for(gid, icon_hash)
        if ph is not None:
            try:
                lbl.config(image=ph)
            except Exception:
                pass

    def _fetch_avatar(gid, icon_hash, lbl):
        from discord.guild_emojis import guild_icon_url
        url = guild_icon_url(gid, icon_hash, size=64)
        if not url:
            return
        key = (str(gid), str(icon_hash or ""))
        if key in _AVATAR_PENDING or key in _AVATAR_BYTES:
            return
        _AVATAR_PENDING.add(key)
        gen = state["gen"]

        def _work():
            try:
                r = _avatar_session().get(url, timeout=6)
                if r.status_code == 200 and r.content:
                    _AVATAR_BYTES[key] = r.content
            except Exception:
                pass
            _AVATAR_PENDING.discard(key)
            try:
                if gen == state["gen"] and win.winfo_exists():
                    win.after(0, lambda: _apply_avatar(lbl, gid, icon_hash))
            except Exception:
                pass

        _avatar_pool().submit(_work)



    def _filtered_guilds():
        q = _query()
        if not q:
            return list(state["guilds"])
        return [g for g in state["guilds"] if q in str(g.get("name", "")).lower()]

    def _render_rows():
        for w in frame.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        items = _filtered_guilds()
        cur = state.get("current_gid")
        for g in items:
            gid = str(g.get("id", ""))
            row = tk.Frame(frame, bg=t["bg_panel"])
            row.pack(fill="x", padx=2, pady=2)
            row.columnconfigure(2, weight=1)
            var = state["vars"].setdefault(gid, tk.BooleanVar(value=False))
            tk.Checkbutton(row, variable=var, bg=t["bg_panel"],
                           activebackground=t["bg_panel"]).grid(
                row=0, column=0, padx=(0, 4))
            avt = tk.Label(row, width=32, bg=t["bg_input"], fg=t["text_muted"],
                           font=FONT_BODY, anchor="center")
            avt.grid(row=0, column=1, sticky="w", padx=(0, 6))
            name = str(g.get("name") or gid)
            if cur and gid == cur:
                disp = name + language.t("profiles_panel.emoji_current_guild")
            else:
                disp = name
            tk.Label(row, text=disp, bg=t["bg_panel"], fg=t["text_primary"],
                     font=FONT_BODY, anchor="w").grid(row=0, column=2,
                                                      sticky="ew")
            icon = g.get("icon")
            if icon:
                ph = _avatar_for(gid, icon)
                if ph is not None:
                    avt.config(image=ph, text="")
                else:
                    avt.config(text=name[:1].upper())
                    _fetch_avatar(gid, icon, avt)
            else:
                avt.config(text=name[:1].upper())
        try:
            lbl_status.config(text=language.t("profiles_panel.emoji_guild_count",
                                              len(items), len(state["guilds"])))
        except Exception:
            pass

    def _reload():
        state["gen"] += 1
        _render_rows()

    def _on_search(*_a):
        if state["after_id"] is not None:
            try:
                win.after_cancel(state["after_id"])
            except Exception:
                pass
        state["after_id"] = win.after(150, _reload)

    entry_search.bind("<KeyRelease>", _on_search)

    def _on_guilds(guilds, cur_gid):
        state["guilds"] = list(guilds or [])
        state["current_gid"] = cur_gid
        try:
            sel = list((get_profile() or {}).get("emoji_guilds") or [])
        except Exception:
            sel = []
        if not sel and cur_gid:
            sel = [cur_gid]
        for g in state["guilds"]:
            gid = str(g.get("id", ""))
            state["vars"].setdefault(gid, tk.BooleanVar(value=gid in sel))
            try:
                state["vars"][gid].set(gid in sel)
            except Exception:
                pass
        try:
            if win.winfo_exists():
                win.after(0, _reload)
        except Exception:
            pass

    def _load_guilds():
        from discord.guild_emojis import list_user_guilds, get_guild_id
        guilds = []
        cur_gid = None
        try:
            guilds = list_user_guilds(token) or []
        except Exception:
            guilds = []
        try:
            if channel_id:
                cur_gid = get_guild_id(str(channel_id), token)
        except Exception:
            cur_gid = None
        if not guilds:
            try:
                if win.winfo_exists():
                    win.after(0, lambda: lbl_status.config(
                        text=language.t("profiles_panel.emoji_guild_empty")))
            except Exception:
                pass
            return
        _on_guilds(guilds, cur_gid)

    def _do_save():
        order = [str(g.get("id") or "") for g in state["guilds"]]
        sel = [gid for gid in order
               if gid and _var_true(state["vars"].get(gid))]
        try:
            save_profile(sel)
        except Exception:
            pass
        try:
            if callable(on_change):
                on_change()
        except Exception:
            pass
        try:
            win.destroy()
        except Exception:
            pass

    btns = tk.Frame(inner, bg=t["bg_panel"])
    btns.pack(fill="x", pady=(8, 0))
    create_styled_button(btns, text=language.t("profiles_panel.emoji_save"),
                         command=_do_save, variant="primary",
                         padx=12, pady=4).pack(side="right", padx=(6, 0))
    create_styled_button(btns, text=language.t("common.cancel"),
                         command=win.destroy, variant="secondary",
                         padx=12, pady=4).pack(side="right")

    threading.Thread(target=_load_guilds, daemon=True).start()
    return win

