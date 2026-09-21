# utils/constants.py
# Chứa các hằng số về màu sắc, font, và cấu hình UI
# Author: bluemanhst

from utils.paths import resource_path, user_path

# ===== PHỐI MÀU DRAGON BALL THEME =====
# Màu nền chính (đen/tối)
BG_DARK = "#1E1E24"

# Màu nền các panel (xám tối)
BG_PANEL = "#2A2A35"

# Màu chữ vàng đặc trưng (Dragon Ball)
TXT_GOLD = "#FFCC00"

# Màu chữ trắng
TXT_WHITE = "#FFFFFF"

# Màu nút cam (nút chính)
BTN_ORANGE = "#FF6600"

# Màu nút đỏ (nút dừng/xóa)
BTN_RED = "#CC0000"

# Màu log area (xanh)
LOG_BLUE = "#00DDFF"

# Màu hover cho header/navigation
HEADER_HOVER_BG = "#3D3D4D"

# ===== CẤU HÌNH FONT =====
# Font cho các label/tiêu đề
FONT_LABEL = ("Arial", 10, "bold")

# Font cho các ô nhập liệu
FONT_ENTRY = ("Consolas", 10)

# ===== CẤU HÌNH CỬA SỔ =====
# Kích thước mặc định của cửa sổ
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 720

# Kích thước tối thiểu (không cho nhỏ hơn)
MIN_WIDTH = 800
MIN_HEIGHT = 600

# ===== CẤU HÌNH DISCORD API =====
# Endpoint API Discord
DISCORD_API_BASE = "https://discord.com/api/v10"

# ===== CẤU HÌNH FILE =====
# Tên file cấu hình (đặt cạnh file EXE khi build, hoặc ở gốc project khi chạy source)
CONFIG_FILE = user_path("config.json")

# Thư mục chứa file ngôn ngữ (assets/ và languages/ được PyInstaller giải nén vào _MEIPASS)
LANGUAGES_DIR = resource_path("languages")

# Tên file icon app (đường dẫn tuyệt đối, hoạt động cả khi chạy source lẫn EXE)
APP_ICON = resource_path("assets", "logo.ico")

# ===== CẤU HÌNH SOCIAL LINKS =====
# Link Discord
DISCORD_LINK = "https://discord.com/users/481280614956400690"

# Link Facebook
FACEBOOK_LINK = "https://www.facebook.com/bluemanhstv4seo"

# ===== CẤU HÌNH ICON FOOTER =====
# File icon Discord
DISCORD_ICON = resource_path("assets", "discord_logo.png")

# File icon Facebook
FACEBOOK_ICON = resource_path("assets", "facebook_logo.png")
