# discord/dashboard.py
# Dashboard thống kê theo dõi hoạt động tool
# Author: bluemanhst

import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict


class Dashboard:
    """Lớp quản lý thống kê hoạt động tool"""
    
    def __init__(self):
        """Khởi tạo dashboard với các thống kê cơ bản"""
        self.start_time = None
        self.total_messages_sent = 0
        self.total_messages_deleted = 0
        self.total_errors = 0
        
        # Thống kê theo tài khoản
        self.account_stats = defaultdict(lambda: {
            "messages_sent": 0,
            "messages_deleted": 0,
            "errors": 0,
            "last_active": None,
            "first_active": None
        })
        
        # Thống kê theo thời gian (để vẽ biểu đồ)
        self.hourly_stats = defaultdict(lambda: {
            "messages_sent": 0,
            "messages_deleted": 0,
            "errors": 0
        })
        
        # Thống kê theo kênh
        self.channel_stats = defaultdict(lambda: {
            "messages_sent": 0,
            "messages_deleted": 0,
            "errors": 0
        })
        
        # Lock để thread-safe (dùng RLock để tránh deadlock khi export_stats gọi get_overall_stats)
        self.lock = threading.RLock()
    
    def start_tracking(self):
        """Bắt đầu theo dõi thời gian"""
        with self.lock:
            self.start_time = datetime.now()
    
    def record_message_sent(self, account_id, channel_id):
        """
        Ghi nhận tin nhắn được gửi
        
        Args:
            account_id (str): ID tài khoản
            channel_id (str): ID kênh
        """
        with self.lock:
            self.total_messages_sent += 1
            
            # Cập nhật thống kê theo tài khoản
            self.account_stats[account_id]["messages_sent"] += 1
            self.account_stats[account_id]["last_active"] = datetime.now()
            if self.account_stats[account_id]["first_active"] is None:
                self.account_stats[account_id]["first_active"] = datetime.now()
            
            # Cập nhật thống kê theo kênh
            self.channel_stats[channel_id]["messages_sent"] += 1
            
            # Cập nhật thống kê theo giờ
            current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
            self.hourly_stats[current_hour]["messages_sent"] += 1
    
    def record_message_deleted(self, account_id, channel_id):
        """
        Ghi nhận tin nhắn được xóa
        
        Args:
            account_id (str): ID tài khoản
            channel_id (str): ID kênh
        """
        with self.lock:
            self.total_messages_deleted += 1
            
            # Cập nhật thống kê theo tài khoản
            self.account_stats[account_id]["messages_deleted"] += 1
            
            # Cập nhật thống kê theo kênh
            self.channel_stats[channel_id]["messages_deleted"] += 1
            
            # Cập nhật thống kê theo giờ
            current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
            self.hourly_stats[current_hour]["messages_deleted"] += 1
    
    def record_error(self, account_id, channel_id, error_type):
        """
        Ghi nhận lỗi
        
        Args:
            account_id (str): ID tài khoản
            channel_id (str): ID kênh
            error_type (str): Loại lỗi
        """
        with self.lock:
            self.total_errors += 1
            
            # Cập nhật thống kê theo tài khoản
            self.account_stats[account_id]["errors"] += 1
            
            # Cập nhật thống kê theo kênh
            self.channel_stats[channel_id]["errors"] += 1
            
            # Cập nhật thống kê theo giờ
            current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
            self.hourly_stats[current_hour]["errors"] += 1
    
    def get_overall_stats(self):
        """
        Lấy thống kê tổng quan
        
        Returns:
            dict: Thống kê tổng quan
        """
        with self.lock:
            if self.start_time is None:
                runtime = "0:00:00"
            else:
                runtime = str(datetime.now() - self.start_time).split(".")[0]
            
            return {
                "runtime": runtime,
                "total_messages_sent": self.total_messages_sent,
                "total_messages_deleted": self.total_messages_deleted,
                "total_errors": self.total_errors,
                "active_accounts": len([acc for acc, stats in self.account_stats.items() 
                                      if stats["messages_sent"] > 0]),
                "total_accounts": len(self.account_stats),
                "success_rate": self._calculate_success_rate()
            }
    
    def get_account_stats(self, account_id):
        """
        Lấy thống kê theo tài khoản
        
        Args:
            account_id (str): ID tài khoản
        
        Returns:
            dict: Thống kê tài khoản
        """
        with self.lock:
            return self.account_stats.get(account_id, {
                "messages_sent": 0,
                "messages_deleted": 0,
                "errors": 0,
                "last_active": None,
                "first_active": None
            })
    
    def get_channel_stats(self, channel_id):
        """
        Lấy thống kê theo kênh
        
        Args:
            channel_id (str): ID kênh
        
        Returns:
            dict: Thống kê kênh
        """
        with self.lock:
            return self.channel_stats.get(channel_id, {
                "messages_sent": 0,
                "messages_deleted": 0,
                "errors": 0
            })
    
    def get_hourly_stats(self, hours=24):
        """
        Lấy thống kê theo giờ
        
        Args:
            hours (int): Số giờ gần nhất cần lấy
        
        Returns:
            list: Danh sách thống kê theo giờ
        """
        with self.lock:
            now = datetime.now()
            stats = []
            
            for i in range(hours):
                hour_time = now - timedelta(hours=i)
                hour_key = hour_time.strftime("%Y-%m-%d %H:00")
                
                if hour_key in self.hourly_stats:
                    stats.append({
                        "hour": hour_key,
                        "messages_sent": self.hourly_stats[hour_key]["messages_sent"],
                        "messages_deleted": self.hourly_stats[hour_key]["messages_deleted"],
                        "errors": self.hourly_stats[hour_key]["errors"]
                    })
            
            return stats[::-1]  # Đảo ngược để từ cũ đến mới
    
    def get_top_accounts(self, limit=5):
        """
        Lấy top tài khoản hoạt động nhiều nhất
        
        Args:
            limit (int): Số tài khoản cần lấy
        
        Returns:
            list: Danh sách top tài khoản
        """
        with self.lock:
            sorted_accounts = sorted(
                self.account_stats.items(),
                key=lambda x: x[1]["messages_sent"],
                reverse=True
            )
            
            return sorted_accounts[:limit]
    
    def get_top_channels(self, limit=5):
        """
        Lấy top kênh hoạt động nhiều nhất
        
        Args:
            limit (int): Số kênh cần lấy
        
        Returns:
            list: Danh sách top kênh
        """
        with self.lock:
            sorted_channels = sorted(
                self.channel_stats.items(),
                key=lambda x: x[1]["messages_sent"],
                reverse=True
            )
            
            return sorted_channels[:limit]
    
    def calculate_speed(self):
        """
        Tính tốc độ gửi tin nhắn (tin/phút)
        
        Returns:
            float: Tốc độ gửi tin nhắn
        """
        with self.lock:
            if self.start_time is None:
                return 0.0
            
            runtime_seconds = (datetime.now() - self.start_time).total_seconds()
            if runtime_seconds == 0:
                return 0.0
            
            return (self.total_messages_sent / runtime_seconds) * 60
    
    def _calculate_success_rate(self):
        """
        Tính tỷ lệ thành công
        
        Returns:
            float: Tỷ lệ thành công (%)
        """
        total_attempts = self.total_messages_sent + self.total_errors
        if total_attempts == 0:
            return 0.0
        
        return (self.total_messages_sent / total_attempts) * 100
    
    def reset_stats(self):
        """Reset tất cả thống kê"""
        with self.lock:
            self.start_time = None
            self.total_messages_sent = 0
            self.total_messages_deleted = 0
            self.total_errors = 0
            self.account_stats.clear()
            self.hourly_stats.clear()
            self.channel_stats.clear()
    
    def export_stats(self):
        """
        Export thống kê ra dict để lưu file
        
        Returns:
            dict: Thống kê dạng dict
        """
        with self.lock:
            # Chuyển đổi account_stats để datetime thành chuỗi, tránh lỗi json serialize
            formatted_account_stats = {}
            for acc_id, stats in self.account_stats.items():
                item = dict(stats)
                if isinstance(item.get("last_active"), datetime):
                    item["last_active"] = item["last_active"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(item.get("first_active"), datetime):
                    item["first_active"] = item["first_active"].strftime("%Y-%m-%d %H:%M:%S")
                formatted_account_stats[acc_id] = item

            return {
                "export_time": datetime.now().isoformat(),
                "runtime": str(datetime.now() - self.start_time).split(".")[0] if self.start_time else "0:00:00",
                "overall_stats": self.get_overall_stats(),
                "account_stats": formatted_account_stats,
                "channel_stats": dict(self.channel_stats),
                "hourly_stats": dict(self.hourly_stats)
            }


# Dashboard global instance
dashboard = Dashboard()