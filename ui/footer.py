# ui/footer.py
# Footer với Discord và Facebook icons + hover animation
# Author: bluemanhst

import tkinter as tk
import webbrowser
import os
from utils.constants import BG_PANEL, DISCORD_LINK, FACEBOOK_LINK, DISCORD_ICON, FACEBOOK_ICON
import language


def create_footer(root):
    """
    Tạo footer với Discord và Facebook icons
    
    Args:
        root: Root window
    
    Returns:
        Frame: Footer frame
    """
    # Animation flags (dùng list để có thể thay đổi trong nested function)
    discord_animating = [False]
    facebook_animating = [False]

    # Frame footer
    frame_footer = tk.Frame(root, bg=BG_PANEL, height=60)
    frame_footer.pack(side="bottom", fill="x", padx=10, pady=5)

    # Frame chính giữa để chứa các nút
    frame_footer_center = tk.Frame(frame_footer, bg=BG_PANEL)
    frame_footer_center.pack(expand=True)

    # Hàm mở link khi click vào logo
    def open_discord():
        webbrowser.open(DISCORD_LINK)

    def open_facebook():
        webbrowser.open(FACEBOOK_LINK)

    # Discord icon với hover animation
    try:
        # Đường dẫn đã được utils.paths tính sẵn (đúng cả khi chạy source lẫn EXE)
        discord_img = tk.PhotoImage(file=DISCORD_ICON)
        btn_discord = tk.Button(frame_footer_center, image=discord_img, command=open_discord,
                               bg=BG_PANEL, bd=0, cursor="hand2", relief="flat", padx=8, pady=8)
        btn_discord.image = discord_img  # Giữ reference

        # Animation functions
        def on_discord_enter(e):
            discord_animating[0] = True
            animate_discord_hover(0)

        def animate_discord_hover(step):
            if not discord_animating[0] or step > 10:
                discord_animating[0] = False
                return
            
            colors = ["#4E5D94", "#5E6DA4", "#6E7DB4", "#7E8DC4", "#5865F2"]
            color = colors[min(step, len(colors)-1)]
            bd = min(step // 2, 4)
            btn_discord.config(bg=color, relief="raised", bd=bd)
            root.after(30, lambda: animate_discord_hover(step + 1))

        def on_discord_leave(e):
            discord_animating[0] = False
            btn_discord.config(bg=BG_PANEL, relief="flat", bd=0)

        btn_discord.bind("<Enter>", on_discord_enter)
        btn_discord.bind("<Leave>", on_discord_leave)
        btn_discord.pack(side="left", padx=10)
    except:
        # Fallback nếu không load được icon
        pass

    # Facebook icon với hover animation
    try:
        # Đường dẫn đã được utils.paths tính sẵn (đúng cả khi chạy source lẫn EXE)
        facebook_img = tk.PhotoImage(file=FACEBOOK_ICON)
        btn_facebook = tk.Button(frame_footer_center, image=facebook_img, command=open_facebook,
                                bg=BG_PANEL, bd=0, cursor="hand2", relief="flat", padx=8, pady=8)
        btn_facebook.image = facebook_img  # Giữ reference

        def on_facebook_enter(e):
            facebook_animating[0] = True
            animate_facebook_hover(0)

        def animate_facebook_hover(step):
            if not facebook_animating[0] or step > 10:
                facebook_animating[0] = False
                return
            
            colors = ["#2D4A8F", "#3D5A9F", "#4D6AAF", "#5D7ABF", "#1877F2"]
            color = colors[min(step, len(colors)-1)]
            bd = min(step // 2, 4)
            btn_facebook.config(bg=color, relief="raised", bd=bd)
            root.after(30, lambda: animate_facebook_hover(step + 1))

        def on_facebook_leave(e):
            facebook_animating[0] = False
            btn_facebook.config(bg=BG_PANEL, relief="flat", bd=0)

        btn_facebook.bind("<Enter>", on_facebook_enter)
        btn_facebook.bind("<Leave>", on_facebook_leave)
        btn_facebook.pack(side="left", padx=10)
    except:
        # Fallback nếu không load được icon
        pass

    # Copyright label
    lbl_copyright = tk.Label(frame_footer, text=language.t("footer.copyright"), 
                           bg=BG_PANEL, fg="#888888", font=("Arial", 8))
    lbl_copyright.pack(side="right", padx=10)

    return frame_footer
