# ui/dashboard_page.py
# Trang Dashboard thống kê hoạt động tool
# Author: bluemanhst

import tkinter as tk
from tkinter import ttk, messagebox
from utils.theme import (
    get_theme, create_card_frame, create_section_header,
    create_styled_button, FONT_BODY, FONT_BODY_BOLD, FONT_CAPTION,
    FONT_SECTION, FONT_TITLE
)
from discord.dashboard import dashboard
import language


def create_dashboard_page(root):
    """
    Tạo trang dashboard thống kê theo phong cách SaaS Analytics hiện đại
    
    Args:
        root: Root window
    
    Returns:
        Frame: frame_dashboard_page
    """
    t = get_theme()

    frame_dashboard_page = tk.Frame(root, bg=t["bg_app"])

    container = tk.Frame(frame_dashboard_page, bg=t["bg_app"])
    container.pack(fill="both", expand=True, padx=20, pady=16)

    # ===== TOP CONTROLS & HEADER =====
    header_row = tk.Frame(container, bg=t["bg_app"])
    header_row.pack(fill="x", pady=(0, 14))

    lbl_dash_title = tk.Label(
        header_row,
        text=language.t("dashboard_page.title"),
        bg=t["bg_app"],
        fg=t["text_primary"],
        font=FONT_TITLE
    )
    lbl_dash_title.pack(side="left")

    actions_frame = tk.Frame(header_row, bg=t["bg_app"])
    actions_frame.pack(side="right")

    btn_refresh = create_styled_button(
        actions_frame,
        text=language.t("dashboard_page.btn_refresh"),
        command=lambda: None,
        variant="secondary",
        padx=12,
        pady=5
    )
    btn_refresh.pack(side="left", padx=4)

    btn_export = create_styled_button(
        actions_frame,
        text=language.t("dashboard_page.btn_export"),
        command=lambda: None,
        variant="ghost",
        padx=12,
        pady=5
    )
    btn_export.pack(side="left", padx=4)

    btn_reset = create_styled_button(
        actions_frame,
        text=language.t("dashboard_page.btn_reset"),
        command=lambda: None,
        variant="danger",
        padx=12,
        pady=5
    )
    btn_reset.pack(side="left", padx=4)

    # ===== STATS OVERVIEW CARDS (Grid 4 cột) =====
    stats_card, stats_inner = create_card_frame(container, padx=16, pady=14)
    stats_card.pack(fill="x", pady=(0, 14))

    stats_config = [
        (language.t("dashboard_page.runtime"), "runtime", t["text_primary"]),
        (language.t("dashboard_page.total_messages"), "total_messages_sent", t["accent"]),
        (language.t("dashboard_page.deleted_messages"), "total_messages_deleted", t["info"]),
        (language.t("dashboard_page.total_errors"), "total_errors", t["danger"]),
        (language.t("dashboard_page.active_accounts"), "active_accounts", t["success"]),
        (language.t("dashboard_page.speed"), "speed", t["accent"]),
        (language.t("dashboard_page.success_rate"), "success_rate", t["success"])
    ]

    stat_label_widgets = {}

    grid_frame = tk.Frame(stats_inner, bg=t["bg_panel"])
    grid_frame.pack(fill="x")

    for idx, (label_text, stat_key, color) in enumerate(stats_config):
        row = idx // 4
        col = idx % 4

        cell = tk.Frame(
            grid_frame,
            bg=t["bg_input"],
            highlightthickness=1,
            highlightbackground=t["border_subtle"],
            padx=12,
            pady=10
        )
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        grid_frame.grid_columnconfigure(col, weight=1)

        lbl_desc = tk.Label(
            cell,
            text=label_text,
            bg=t["bg_input"],
            fg=t["text_muted"],
            font=FONT_CAPTION,
            anchor="w"
        )
        lbl_desc.pack(anchor="w")

        lbl_val = tk.Label(
            cell,
            text="--",
            bg=t["bg_input"],
            fg=color,
            font=FONT_SECTION,
            anchor="w"
        )
        lbl_val.pack(anchor="w", pady=(4, 0))
        lbl_val.stat_key = stat_key
        stat_label_widgets[stat_key] = lbl_val

    # ===== DETAILS TABLE CARD (Notebook) =====
    table_card, table_inner = create_card_frame(container, padx=16, pady=14)
    table_card.pack(fill="both", expand=True)

    notebook = ttk.Notebook(table_inner)
    notebook.pack(fill="both", expand=True)

    # Tab 1: Accounts
    frame_accounts = tk.Frame(notebook, bg=t["bg_panel"])
    notebook.add(frame_accounts, text=language.t("dashboard_page.tab_accounts"))

    columns_accounts = ("account", "sent", "deleted", "errors", "success_rate")
    tree_accounts = ttk.Treeview(frame_accounts, columns=columns_accounts, show="headings")
    tree_accounts.heading("account", text=language.t("dashboard_page.col_account"))
    tree_accounts.heading("sent", text=language.t("dashboard_page.col_sent"))
    tree_accounts.heading("deleted", text=language.t("dashboard_page.col_deleted"))
    tree_accounts.heading("errors", text=language.t("dashboard_page.col_errors"))
    tree_accounts.heading("success_rate", text=language.t("dashboard_page.col_success_rate"))

    tree_accounts.column("account", width=180, anchor="w")
    tree_accounts.column("sent", width=100, anchor="center")
    tree_accounts.column("deleted", width=100, anchor="center")
    tree_accounts.column("errors", width=100, anchor="center")
    tree_accounts.column("success_rate", width=120, anchor="center")

    scroll_acc = ttk.Scrollbar(frame_accounts, orient="vertical", command=tree_accounts.yview)
    tree_accounts.configure(yscrollcommand=scroll_acc.set)
    tree_accounts.pack(side="left", fill="both", expand=True)
    scroll_acc.pack(side="right", fill="y")

    # Tab 2: Channels
    frame_channels = tk.Frame(notebook, bg=t["bg_panel"])
    notebook.add(frame_channels, text=language.t("dashboard_page.tab_channels"))

    columns_channels = ("channel", "sent", "deleted", "errors")
    tree_channels = ttk.Treeview(frame_channels, columns=columns_channels, show="headings")
    tree_channels.heading("channel", text=language.t("dashboard_page.col_channel"))
    tree_channels.heading("sent", text=language.t("dashboard_page.col_sent"))
    tree_channels.heading("deleted", text=language.t("dashboard_page.col_deleted"))
    tree_channels.heading("errors", text=language.t("dashboard_page.col_errors"))

    tree_channels.column("channel", width=220, anchor="w")
    tree_channels.column("sent", width=100, anchor="center")
    tree_channels.column("deleted", width=100, anchor="center")
    tree_channels.column("errors", width=100, anchor="center")

    scroll_ch = ttk.Scrollbar(frame_channels, orient="vertical", command=tree_channels.yview)
    tree_channels.configure(yscrollcommand=scroll_ch.set)
    tree_channels.pack(side="left", fill="both", expand=True)
    scroll_ch.pack(side="right", fill="y")

    # ===== LOGIC CẬP NHẬT STATS =====
    def update_dashboard():
        overall_stats = dashboard.get_overall_stats()

        for key, widget in stat_label_widgets.items():
            if key == "runtime":
                widget.config(text=overall_stats.get("runtime", "0:00:00"))
            elif key == "total_messages_sent":
                widget.config(text=str(overall_stats.get("total_messages_sent", 0)))
            elif key == "total_messages_deleted":
                widget.config(text=str(overall_stats.get("total_messages_deleted", 0)))
            elif key == "total_errors":
                widget.config(text=str(overall_stats.get("total_errors", 0)))
            elif key == "active_accounts":
                widget.config(text=f"{overall_stats.get('active_accounts', 0)}/{overall_stats.get('total_accounts', 0)}")
            elif key == "speed":
                speed = dashboard.calculate_speed()
                widget.config(text=f"{speed:.2f} msg/m")
            elif key == "success_rate":
                widget.config(text=f"{overall_stats.get('success_rate', 0):.1f}%")

        # Accounts Tree
        for item in tree_accounts.get_children():
            tree_accounts.delete(item)

        top_accounts = dashboard.get_top_accounts(10)
        for account_id, stats in top_accounts:
            total_attempts = stats["messages_sent"] + stats["errors"]
            success_rate = (stats["messages_sent"] / total_attempts * 100) if total_attempts > 0 else 0
            tree_accounts.insert("", "end", values=(
                account_id,
                stats["messages_sent"],
                stats["messages_deleted"],
                stats["errors"],
                f"{success_rate:.1f}%"
            ))

        # Channels Tree
        for item in tree_channels.get_children():
            tree_channels.delete(item)

        top_channels = dashboard.get_top_channels(10)
        for channel_id, stats in top_channels:
            tree_channels.insert("", "end", values=(
                channel_id,
                stats["messages_sent"],
                stats["messages_deleted"],
                stats["errors"]
            ))

    def reset_dashboard():
        dashboard.reset_stats()
        update_dashboard()

    def export_dashboard():
        try:
            from tkinter import filedialog
            import json

            stats_data = dashboard.export_stats()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title=language.t("dashboard_page.export_dialog_title")
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, indent=4, ensure_ascii=False, default=str)
                messagebox.showinfo(
                    language.t("common.success_title"),
                    language.t("dashboard_page.export_success_msg", file_path)
                )
        except Exception as e:
            messagebox.showerror(
                language.t("common.error_title"),
                language.t("dashboard_page.export_error_msg", str(e))
            )

    btn_refresh.config(command=update_dashboard)
    btn_reset.config(command=reset_dashboard)
    btn_export.config(command=export_dashboard)

    update_dashboard()

    return frame_dashboard_page