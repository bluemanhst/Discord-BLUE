# ui/dashboard_page.py
# Trang Dashboard thống kê hoạt động tool
# Author: bluemanhst

import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import BG_DARK, BG_PANEL, TXT_GOLD, TXT_WHITE, FONT_LABEL
from discord.dashboard import dashboard
import language


def create_dashboard_page(root):
    """
    Tạo trang dashboard thống kê
    
    Args:
        root: Root window
    
    Returns:
        tuple: (frame_dashboard_page)
    """
    # Frame chính của trang
    frame_dashboard_page = tk.Frame(root, bg=BG_DARK)
    
    # Frame chứa nội dung dashboard
    frame_dashboard_main = tk.Frame(frame_dashboard_page, bg=BG_PANEL, bd=2, relief="ridge")
    frame_dashboard_main.pack(fill="both", expand=True, padx=15, pady=10)
    
    # Tiêu đề
    tk.Label(frame_dashboard_main, text=language.t("dashboard_page.title"), 
           bg=BG_PANEL, fg=TXT_GOLD, font=("Arial", 14, "bold")).pack(pady=15)
    
    # Frame chứa thống kê tổng quan
    frame_overview = tk.Frame(frame_dashboard_main, bg=BG_PANEL)
    frame_overview.pack(fill="x", padx=20, pady=10)
    
    # Grid cho thống kê tổng quan
    stats_labels = [
        (language.t("dashboard_page.runtime"), "runtime"),
        (language.t("dashboard_page.total_messages"), "total_messages_sent"),
        (language.t("dashboard_page.deleted_messages"), "total_messages_deleted"),
        (language.t("dashboard_page.total_errors"), "total_errors"),
        (language.t("dashboard_page.active_accounts"), "active_accounts"),
        (language.t("dashboard_page.speed"), "speed"),
        (language.t("dashboard_page.success_rate"), "success_rate")
    ]
    
    for i, (label_text, stat_key) in enumerate(stats_labels):
        row = i // 2
        col = (i % 2) * 2
        
        tk.Label(frame_overview, text=label_text, 
               bg=BG_PANEL, fg=TXT_WHITE, font=FONT_LABEL).grid(row=row, column=col, sticky="w", padx=5, pady=5)
        
        stat_label = tk.Label(frame_overview, text="--", 
                            bg=BG_PANEL, fg=TXT_GOLD, font=("Arial", 10, "bold"))
        stat_label.grid(row=row, column=col+1, sticky="w", padx=5, pady=5)
        stat_label.stat_key = stat_key  # Lưu key để cập nhật sau
    
    # Frame nút điều khiển
    frame_controls = tk.Frame(frame_dashboard_main, bg=BG_PANEL)
    frame_controls.pack(fill="x", padx=20, pady=10)
    
    btn_refresh = tk.Button(frame_controls, text=language.t("dashboard_page.btn_refresh"), 
                           bg="#4CAF50", fg=TXT_WHITE, font=("Arial", 10, "bold"), bd=2)
    btn_refresh.pack(side="left", padx=5)
    
    btn_reset = tk.Button(frame_controls, text=language.t("dashboard_page.btn_reset"), 
                        bg="#FF5722", fg=TXT_WHITE, font=("Arial", 10, "bold"), bd=2)
    btn_reset.pack(side="left", padx=5)
    
    btn_export = tk.Button(frame_controls, text=language.t("dashboard_page.btn_export"), 
                         bg="#2196F3", fg=TXT_WHITE, font=("Arial", 10, "bold"), bd=2)
    btn_export.pack(side="left", padx=5)
    
    # Frame cho thống kê chi tiết
    frame_details = tk.Frame(frame_dashboard_main, bg=BG_PANEL)
    frame_details.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Notebook cho các tab chi tiết
    notebook = ttk.Notebook(frame_details)
    notebook.pack(fill="both", expand=True)
    
    # Tab thống kê theo tài khoản
    frame_accounts = tk.Frame(notebook, bg=BG_PANEL)
    notebook.add(frame_accounts, text=language.t("dashboard_page.tab_accounts"))
    
    # Treeview cho thống kê tài khoản
    columns_accounts = ("account", "sent", "deleted", "errors", "success_rate")
    tree_accounts = ttk.Treeview(frame_accounts, columns=columns_accounts, show="headings")
    tree_accounts.heading("account", text=language.t("dashboard_page.col_account"))
    tree_accounts.heading("sent", text=language.t("dashboard_page.col_sent"))
    tree_accounts.heading("deleted", text=language.t("dashboard_page.col_deleted"))
    tree_accounts.heading("errors", text=language.t("dashboard_page.col_errors"))
    tree_accounts.heading("success_rate", text=language.t("dashboard_page.col_success_rate"))
    
    tree_accounts.column("account", width=150)
    tree_accounts.column("sent", width=100)
    tree_accounts.column("deleted", width=100)
    tree_accounts.column("errors", width=100)
    tree_accounts.column("success_rate", width=120)
    
    tree_accounts.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Tab thống kê theo kênh
    frame_channels = tk.Frame(notebook, bg=BG_PANEL)
    notebook.add(frame_channels, text=language.t("dashboard_page.tab_channels"))
    
    # Treeview cho thống kê kênh
    columns_channels = ("channel", "sent", "deleted", "errors")
    tree_channels = ttk.Treeview(frame_channels, columns=columns_channels, show="headings")
    tree_channels.heading("channel", text=language.t("dashboard_page.col_channel"))
    tree_channels.heading("sent", text=language.t("dashboard_page.col_sent"))
    tree_channels.heading("deleted", text=language.t("dashboard_page.col_deleted"))
    tree_channels.heading("errors", text=language.t("dashboard_page.col_errors"))
    
    tree_channels.column("channel", width=200)
    tree_channels.column("sent", width=100)
    tree_channels.column("deleted", width=100)
    tree_channels.column("errors", width=100)
    
    tree_channels.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Hàm cập nhật thống kê
    def update_dashboard():
        """Cập nhật tất cả thống kê"""
        overall_stats = dashboard.get_overall_stats()
        
        # Cập nhật thống kê tổng quan
        for widget in frame_overview.winfo_children():
            if hasattr(widget, 'stat_key'):
                stat_key = widget.stat_key
                if stat_key == "runtime":
                    widget.config(text=overall_stats.get("runtime", "0:00:00"))
                elif stat_key == "total_messages_sent":
                    widget.config(text=str(overall_stats.get("total_messages_sent", 0)))
                elif stat_key == "total_messages_deleted":
                    widget.config(text=str(overall_stats.get("total_messages_deleted", 0)))
                elif stat_key == "total_errors":
                    widget.config(text=str(overall_stats.get("total_errors", 0)))
                elif stat_key == "active_accounts":
                    widget.config(text=f"{overall_stats.get('active_accounts', 0)}/{overall_stats.get('total_accounts', 0)}")
                elif stat_key == "speed":
                    speed = dashboard.calculate_speed()
                    widget.config(text=f"{speed:.2f}")
                elif stat_key == "success_rate":
                    widget.config(text=f"{overall_stats.get('success_rate', 0):.1f}%")
        
        # Cập nhật thống kê tài khoản
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
        
        # Cập nhật thống kê kênh
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
        """Reset tất cả thống kê"""
        dashboard.reset_stats()
        update_dashboard()
    
    def export_dashboard():
        """Export thống kê ra file"""
        try:
            from tkinter import filedialog
            import json
            
            stats_data = dashboard.export_stats()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Dashboard Stats"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, indent=4, ensure_ascii=False, default=str)
                messagebox.showinfo("Thành công", f"Đã export thống kê thành công!\n\nFile: {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể export thống kê:\n{e}")
    
    # Gán command cho các nút
    btn_refresh.config(command=update_dashboard)
    btn_reset.config(command=reset_dashboard)
    btn_export.config(command=export_dashboard)
    
    # Cập nhật lần đầu
    update_dashboard()
    
    return frame_dashboard_page