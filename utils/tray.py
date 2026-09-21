# utils/tray.py
# Icon khay hệ thống (System Tray) - dùng pystray, tự động fallback nếu thiếu thư viện
# Author: bluemanhst

import os
import queue
import threading

# ===== KIỂM TRA THƯ VIỆN TRAY =====
try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except Exception:
    pystray = None
    Image = None
    TRAY_AVAILABLE = False


class TrayManager:
    """
    Quản lý icon dưới khay hệ thống.

    Lưu ý quan trọng: menu của tray được bấm từ thread của pystray, nên KHÔNG
    được gọi trực tiếp hàm Tkinter trong đó. Các lệnh được đẩy vào `commands`,
    luồng chính của Tkinter sẽ gọi drain() định kỳ để xử lý.
    """

    def __init__(self, icon_path=None, title="Discord BLUE",
                 menu_show="Mở Discord BLUE", menu_quit="Thoát"):
        self.icon_path = icon_path
        self.title = title
        self.menu_show = menu_show
        self.menu_quit = menu_quit
        self.commands = queue.Queue()
        self._icon = None
        self._running = False

    @property
    def running(self):
        """Icon tray đang hiển thị hay không"""
        return self._running

    def _load_image(self):
        """Ảnh icon cho tray (ưu tiên logo.ico trong assets)"""
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                return Image.open(self.icon_path)
            except Exception:
                pass
        # Ảnh dự phòng: ô vuông màu Discord Blurple
        return Image.new("RGBA", (64, 64), (88, 101, 242, 255))

    def start(self):
        """
        Tạo icon tray trong thread riêng.

        Returns:
            bool: True nếu tạo được icon
        """
        if not TRAY_AVAILABLE or self._running:
            return False

        try:
            menu = pystray.Menu(
                pystray.MenuItem(self.menu_show,
                                 lambda icon, item: self.commands.put("show"),
                                 default=True),
                pystray.MenuItem(self.menu_quit,
                                 lambda icon, item: self.commands.put("quit"))
            )
            self._icon = pystray.Icon("DiscordBLUE", self._load_image(), self.title, menu)
            threading.Thread(target=self._icon.run, daemon=True).start()
            self._running = True
            return True
        except Exception:
            self._icon = None
            self._running = False
            return False

    def stop(self):
        """Gỡ icon tray"""
        if self._icon is not None:
            try:
                self._icon.stop()
            except Exception:
                pass
        self._icon = None
        self._running = False

    def notify(self, message, title=None):
        """Hiện thông báo (balloon tip) từ icon tray nếu hệ thống hỗ trợ"""
        if not self._running or self._icon is None:
            return
        try:
            self._icon.notify(message, title or self.title)
        except Exception:
            pass

    def drain(self, on_show=None, on_quit=None):
        """
        Xử lý các lệnh bấm từ menu tray.
        CHỈ ĐƯỢC GỌI TỪ LUỒNG CHÍNH của Tkinter (qua root.after).
        """
        while True:
            try:
                command = self.commands.get_nowait()
            except queue.Empty:
                return

            if command == "show" and on_show:
                on_show()
            elif command == "quit" and on_quit:
                on_quit()
