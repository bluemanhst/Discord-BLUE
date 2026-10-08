# utils/constants.py
# Hằng số TĨNH dùng chung: kích thước cửa sổ, đường dẫn file, Discord API, social links.
# Màu sắc & Font KHÔNG khai báo ở đây nữa - toàn bộ UI đọc token qua utils.theme.get_theme()
# Author: bluemanhst

from utils.paths import resource_path, user_path

# ===== CẤU HÌNH CỬA SỔ =====
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 740
MIN_WIDTH = 880
MIN_HEIGHT = 640

# ===== CẤU HÌNH DISCORD API =====
DISCORD_API_BASE = "https://discord.com/api/v10"

# ===== CẤU HÌNH FILE =====
CONFIG_FILE = user_path("config.json")
LANGUAGES_DIR = resource_path("languages")
APP_ICON = resource_path("assets", "logo_discord_blue.ico")

# ===== CẤU HÌNH SOCIAL LINKS =====
DISCORD_LINK = "https://discord.com/users/481280614956400690"
FACEBOOK_LINK = "https://www.facebook.com/bluemanhst"

# ===== CẤU HÌNH ICON FOOTER =====
DISCORD_ICON = resource_path("assets", "discord_logo.png")
FACEBOOK_ICON = resource_path("assets", "facebook_logo.png")

