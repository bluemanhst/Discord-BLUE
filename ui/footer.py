# ui/footer.py
# Status bar duoi cung - phong cach Roblox BLUE (clients | msg | gio + VI/EN)
# + icon Discord/Facebook + copyright (giu nguyen tinh nang cu)
# Author: bluemanhst

import tkinter as tk
import webbrowser
from datetime import datetime
from utils.constants import DISCORD_LINK, FACEBOOK_LINK, DISCORD_ICON, FACEBOOK_ICON
from utils.theme import get_theme, FONT_CAPTION
import language


def create_footer(root, bot_running=None):
    """
    Tao status bar duoi cung.
    Tra ve frame footer (API cu: create_footer(root)).

    Args:
        root: Root window
        bot_running: (optional) list [bool] - ref thread-safe trang thai bot
    """
    t = get_theme()

    # Outer container with top subtle border
    frame_footer = tk.Frame(root, bg=t["border_subtle"], height=30)
    frame_footer.pack(side="bottom", fill="x")
    frame_footer.pack_propagate(False)

    footer_inner = tk.Frame(frame_footer, bg=t["bg_sidebar"])
    footer_inner.pack(fill="both", expand=True, padx=14, pady=(1, 1))

    # ===== TRAI: social icons + copyright =====
    frame_social = tk.Frame(footer_inner, bg=t["bg_sidebar"])
    frame_social.pack(side="left", fill="y")

    def open_discord():
        webbrowser.open(DISCORD_LINK)

    def open_facebook():
        webbrowser.open(FACEBOOK_LINK)

    try:
        discord_img = tk.PhotoImage(file=DISCORD_ICON)
        btn_discord = tk.Button(
            frame_social, image=discord_img, command=open_discord,
            bg=t["bg_sidebar"], bd=0, cursor="hand2", relief="flat",
            activebackground=t["bg_hover"], padx=4, pady=1
        )
        btn_discord.image = discord_img
        btn_discord.pack(side="left", padx=(0, 2))

        def on_discord_enter(e):
            btn_discord.config(bg=t["bg_hover"])

        def on_discord_leave(e):
            btn_discord.config(bg=t["bg_sidebar"])

        btn_discord.bind("<Enter>", on_discord_enter)
        btn_discord.bind("<Leave>", on_discord_leave)
    except Exception:
        pass

    try:
        facebook_img = tk.PhotoImage(file=FACEBOOK_ICON)
        btn_facebook = tk.Button(
            frame_social, image=facebook_img, command=open_facebook,
            bg=t["bg_sidebar"], bd=0, cursor="hand2", relief="flat",
            activebackground=t["bg_hover"], padx=4, pady=1
        )
        btn_facebook.image = facebook_img
        btn_facebook.pack(side="left", padx=(0, 8))

        def on_fb_enter(e):
            btn_facebook.config(bg=t["bg_hover"])

        def on_fb_leave(e):
            btn_facebook.config(bg=t["bg_sidebar"])

        btn_facebook.bind("<Enter>", on_fb_enter)
        btn_facebook.bind("<Leave>", on_fb_leave)
    except Exception:
        pass

    lbl_copyright = tk.Label(
        footer_inner,
        text=language.t("footer.copyright"),
        bg=t["bg_sidebar"], fg=t["text_muted"], font=FONT_CAPTION
    )
    lbl_copyright.pack(side="left", pady=4)

    # ===== PHAI: status bot + dong ho + ngon ngu =====
    lbl_status = tk.Label(
        footer_inner, text="",
        bg=t["bg_sidebar"], fg=t["text_muted"], font=("Consolas", 9)
    )
    lbl_status.pack(side="right", pady=4, padx=(10, 0))

    lbl_clock = tk.Label(
        footer_inner, text="",
        bg=t["bg_sidebar"], fg=t["text_secondary"], font=("Consolas", 9)
    )
    lbl_clock.pack(side="right", pady=4, padx=(10, 0))

    lang_code = "VI" if language.get_current_language() == "vietnamese" else "EN"

    def _tick():
        # Cap nhat status bot + dong ho (chay tren luong Tkinter)
        try:
            if not frame_footer.winfo_exists():
                return
        except Exception:
            return
        running = bool(bot_running[0]) if bot_running else False
        if running:
            lbl_status.config(text="● RUN", fg=t["success"])
        else:
            lbl_status.config(text="○ IDLE", fg=t["text_muted"])
        lbl_clock.config(text=datetime.now().strftime("%H:%M:%S") + f"   {lang_code}")
        try:
            root.after(1000, _tick)
        except Exception:
            pass

    try:
        root.after(1000, _tick)
    except Exception:
        pass

    return frame_footer
