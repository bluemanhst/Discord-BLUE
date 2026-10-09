# ui/navigation.py
# Sidebar trai - dieu huong cac trang, phong cach Roblox BLUE (pill truot animated)
# Author: bluemanhst

import tkinter as tk
from utils.theme import get_theme, draw_round_rect, FONT_BUTTON, FONT_SECTION
from utils.anim import AnimLoop, lerp
import language


def create_navigation_bar(root, show_main_page, show_features_page, show_config_page,
                          show_theme_page, show_dashboard_page, show_settings_page):
    """
    Tao sidebar trai (190px) voi pill indicator truot mượt khi chuyen tab.
    Giu API cu: tra ve frame co .set_active(key) nhu navigation bar truoc day.
    """
    t = get_theme()

    SIDEBAR_W = 190
    Y0 = 12           # vi tri y pill cua tab dau tien
    ITEM_H = 34
    STRIDE = 40

    nav = tk.Frame(root, bg=t["bg_sidebar"], width=SIDEBAR_W, highlightthickness=0)
    nav.pack(side="left", fill="y")
    nav.pack_propagate(False)

    # Brand header
    header = tk.Frame(nav, bg=t["bg_sidebar"])
    header.pack(fill="x", padx=16, pady=(16, 6))
    tk.Label(
        header, text="● " + language.t("app_name"),
        bg=t["bg_sidebar"], fg=t["accent"],
        font=("Consolas", 13, "bold"), anchor="w"
    ).pack(anchor="w")
    tk.Label(
        header, text="by bluemanhst",
        bg=t["bg_sidebar"], fg=t["text_muted"],
        font=("Consolas", 9), anchor="w"
    ).pack(anchor="w")

    div = tk.Frame(nav, bg=t["border_subtle"], height=1)
    div.pack(fill="x", padx=16, pady=(8, 4))

    cw = SIDEBAR_W - 16  # chieu rong canvas

    # Canvas chua cac tab + pill animated
    canvas = tk.Canvas(nav, bg=t["bg_sidebar"], highlightthickness=0, bd=0,
                       width=cw, height=6 * STRIDE + Y0)
    canvas.pack(padx=8, pady=(4, 0), anchor="n")

    nav_items = [
        ("main", language.t("navigation.main"), show_main_page),
        ("features", language.t("navigation.features"), show_features_page),
        ("config", language.t("navigation.config"), show_config_page),
        ("theme", language.t("navigation.theme"), show_theme_page),
        ("dashboard", language.t("navigation.dashboard"), show_dashboard_page),
        ("settings", language.t("navigation.settings"), show_settings_page),
    ]
    n_items = len(nav_items)

    state = {
        "active": "main",
        "hover": -1,
        "pill_y": float(Y0),       # vi tri hien tai (animated)
        "loop": None,
    }

    def _item_y(i):
        return Y0 + i * STRIDE

    def _redraw():
        try:
            canvas.delete("all")
        except Exception:
            return
        # Pill active (bo goc + vien accent) - giong Roblox BLUE
        py = state["pill_y"]
        draw_round_rect(canvas, 4, py, cw - 4, py + ITEM_H, 8,
                        fill=t["bg_active"], outline=t["accent"], width=1)
        # Thanh accent ben trai
        draw_round_rect(canvas, 8, py + 6, 12, py + ITEM_H - 6, 2,
                        fill=t["accent"])
        for i, (key, label, _cmd) in enumerate(nav_items):
            iy = _item_y(i)
            active = (key == state["active"])
            hov = (i == state["hover"] and not active)
            if hov:
                draw_round_rect(canvas, 4, iy, cw - 4, iy + ITEM_H, 8,
                                fill=t["bg_hover"])
            color = t["text_primary"] if (active or hov) else t["text_secondary"]
            font = FONT_SECTION if active else FONT_BUTTON
            canvas.create_text(22, iy + ITEM_H // 2, text=label, anchor="w",
                               font=font, fill=color)

    def _hit_item(y):
        for i in range(n_items):
            iy = _item_y(i)
            if iy <= y < iy + ITEM_H:
                return i
        return -1

    def _animate_pill(target_y):
        start = state["pill_y"]

        def _step(p):
            state["pill_y"] = lerp(start, target_y, p)
            _redraw()

        if state["loop"] is not None:
            state["loop"].cancel()
        state["loop"] = AnimLoop(canvas, duration_ms=220, on_step=_step)
        state["loop"].start()

    def set_active(key):
        for i, (k, _l, _c) in enumerate(nav_items):
            if k == key:
                state["active"] = key
                _animate_pill(float(_item_y(i)))
                return

    def _on_click(e):
        i = _hit_item(e.y)
        if i < 0:
            return
        key, _label, cmd = nav_items[i]
        set_active(key)
        try:
            cmd()
        except Exception:
            pass

    def _on_motion(e):
        i = _hit_item(e.y)
        if i != state["hover"]:
            state["hover"] = i
            _redraw()

    def _on_leave(e):
        if state["hover"] != -1:
            state["hover"] = -1
            _redraw()

    canvas.bind("<Button-1>", _on_click)
    canvas.bind("<Motion>", _on_motion)
    canvas.bind("<Leave>", _on_leave)

    # Divider + thong tin duoi sidebar
    div2 = tk.Frame(nav, bg=t["border_subtle"], height=1)
    div2.pack(side="bottom", fill="x", padx=16, pady=(0, 8))
    badge = tk.Frame(nav, bg=t["bg_sidebar"])
    badge.pack(side="bottom", fill="x", padx=16, pady=12)
    tk.Label(
        badge, text="Discord BLUE v1.1",
        bg=t["bg_sidebar"], fg=t["text_muted"], font=("Consolas", 9)
    ).pack(anchor="w")

    _redraw()

    # Lưu hàm set_active lên nav de goi tu ngoai ( API cu )
    nav.set_active = set_active
    return nav
