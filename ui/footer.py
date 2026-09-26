# ui/footer.py
# Footer với Discord và Facebook links + copyright label
# Author: bluemanhst

import tkinter as tk
import webbrowser
from utils.constants import DISCORD_LINK, FACEBOOK_LINK, DISCORD_ICON, FACEBOOK_ICON
from utils.theme import get_theme, FONT_CAPTION
import language


def create_footer(root):
    """
    Tạo footer thanh lịch, đồng bộ thiết kế với top navigation.
    
    Args:
        root: Root window
    
    Returns:
        Frame: Footer frame
    """
    t = get_theme()

    # Outer container with top subtle border
    frame_footer = tk.Frame(root, bg=t["border_subtle"], height=38)
    frame_footer.pack(side="bottom", fill="x")

    footer_inner = tk.Frame(frame_footer, bg=t["bg_sidebar"])
    footer_inner.pack(fill="x", padx=16, pady=(1, 0))

    # Social icons container
    frame_social = tk.Frame(footer_inner, bg=t["bg_sidebar"])
    frame_social.pack(side="left", pady=6)

    def open_discord():
        webbrowser.open(DISCORD_LINK)

    def open_facebook():
        webbrowser.open(FACEBOOK_LINK)

    # Discord icon button (clean flat style)
    try:
        discord_img = tk.PhotoImage(file=DISCORD_ICON)
        btn_discord = tk.Button(
            frame_social,
            image=discord_img,
            command=open_discord,
            bg=t["bg_sidebar"],
            bd=0,
            cursor="hand2",
            relief="flat",
            activebackground=t["bg_hover"],
            padx=4,
            pady=2
        )
        btn_discord.image = discord_img
        btn_discord.pack(side="left", padx=4)

        def on_discord_enter(e):
            btn_discord.config(bg=t["bg_hover"])

        def on_discord_leave(e):
            btn_discord.config(bg=t["bg_sidebar"])

        btn_discord.bind("<Enter>", on_discord_enter)
        btn_discord.bind("<Leave>", on_discord_leave)
    except Exception:
        pass

    # Facebook icon button
    try:
        facebook_img = tk.PhotoImage(file=FACEBOOK_ICON)
        btn_facebook = tk.Button(
            frame_social,
            image=facebook_img,
            command=open_facebook,
            bg=t["bg_sidebar"],
            bd=0,
            cursor="hand2",
            relief="flat",
            activebackground=t["bg_hover"],
            padx=4,
            pady=2
        )
        btn_facebook.image = facebook_img
        btn_facebook.pack(side="left", padx=4)

        def on_fb_enter(e):
            btn_facebook.config(bg=t["bg_hover"])

        def on_fb_leave(e):
            btn_facebook.config(bg=t["bg_sidebar"])

        btn_facebook.bind("<Enter>", on_fb_enter)
        btn_facebook.bind("<Leave>", on_fb_leave)
    except Exception:
        pass

    # Copyright label
    lbl_copyright = tk.Label(
        footer_inner,
        text=language.t("footer.copyright"),
        bg=t["bg_sidebar"],
        fg=t["text_muted"],
        font=FONT_CAPTION
    )
    lbl_copyright.pack(side="right", pady=8)

    return frame_footer
