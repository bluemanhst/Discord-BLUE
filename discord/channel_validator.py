# discord/channel_validator.py
# Validate Discord Channel IDs và lấy thông tin kênh, server, avatar máy chủ
# Author: bluemanhst

import requests
from utils.constants import DISCORD_API_BASE


def get_guild_icon_url(guild_id, icon_hash, size=128):
    """
    Tạo URL avatar của máy chủ (guild) từ guild_id và icon_hash
    
    Args:
        guild_id (str): Discord Guild/Server ID
        icon_hash (str): Guild icon hash
        size (int): Kích thước ảnh (mặc định 128)
        
    Returns:
        str: URL avatar hoặc None
    """
    if not guild_id or not icon_hash:
        return None
        
    if str(icon_hash).startswith("a_"):
        return f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.gif?size={size}"
    else:
        return f"https://cdn.discordapp.com/icons/{guild_id}/{icon_hash}.png?size={size}"


def get_channel_type_name(channel_type):
    """
    Chuyển mã số loại channel thành tên thân thiện
    
    Args:
        channel_type (int): Discord Channel Type ID
        
    Returns:
        str: Tên loại channel
    """
    types = {
        0: "Văn bản (Text)",
        1: "Tin nhắn riêng (DM)",
        2: "Thoại (Voice)",
        3: "Nhóm riêng (Group DM)",
        4: "Danh mục (Category)",
        5: "Thông báo (Announcement)",
        10: "Thông báo con (News Thread)",
        11: "Chủ đề công khai (Public Thread)",
        12: "Chủ đề riêng tư (Private Thread)",
        13: "Sân khấu (Stage Voice)",
        15: "Diễn đàn (Forum)",
        16: "Phương tiện (Media)"
    }
    return types.get(channel_type, f"Khác (Type {channel_type})")


def validate_channel(channel_id, tokens):
    """
    Kiểm tra một Channel ID bằng danh sách tokens được cung cấp.
    Thử lần lượt các token cho đến khi thành công hoặc hết token.
    
    Args:
        channel_id (str): Discord Channel ID cần kiểm tra
        tokens (list): Danh sách token Discord của người dùng
        
    Returns:
        dict: Kết quả kiểm tra
        {
            "valid": bool,
            "id": str,
            "name": str,
            "type_name": str,
            "guild_id": str,
            "guild_name": str,
            "guild_icon_url": str,
            "error": str (khi valid=False)
        }
    """
    channel_id = str(channel_id).strip()
    if not channel_id:
        return {"valid": False, "id": "", "error": "Channel ID rỗng"}
        
    valid_tokens = [t.strip() for t in tokens if t and t.strip()]
    if not valid_tokens:
        return {
            "valid": False,
            "id": channel_id,
            "error": "Cần ít nhất 1 Token hợp lệ để kiểm tra Channel!"
        }

    last_error = "Không xác định"

    for token in valid_tokens:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        
        try:
            url = f"{DISCORD_API_BASE}/channels/{channel_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                ch_data = response.json()
                ch_name = ch_data.get("name", "Không có tên")
                ch_type = ch_data.get("type", 0)
                guild_id = ch_data.get("guild_id")
                
                guild_name = "Máy chủ không xác định"
                guild_icon_url = None
                
                if guild_id:
                    # Lấy thông tin Guild để lấy Icon và Server Name
                    try:
                        g_res = requests.get(f"{DISCORD_API_BASE}/guilds/{guild_id}", headers=headers, timeout=8)
                        if g_res.status_code == 200:
                            g_data = g_res.json()
                            guild_name = g_data.get("name", f"Server {guild_id}")
                            guild_icon = g_data.get("icon")
                            if guild_icon:
                                guild_icon_url = get_guild_icon_url(guild_id, guild_icon)
                        elif g_res.status_code == 403:
                            # Không có quyền view guild info trực tiếp, thử preview endpoint
                            prev_res = requests.get(f"{DISCORD_API_BASE}/guilds/{guild_id}/preview", headers=headers, timeout=8)
                            if prev_res.status_code == 200:
                                p_data = prev_res.json()
                                guild_name = p_data.get("name", f"Server {guild_id}")
                                guild_icon = p_data.get("icon")
                                if guild_icon:
                                    guild_icon_url = get_guild_icon_url(guild_id, guild_icon)
                            else:
                                guild_name = f"Server ID: {guild_id}"
                        else:
                            guild_name = f"Server ID: {guild_id}"
                    except Exception:
                        guild_name = f"Server ID: {guild_id}"
                else:
                    if ch_type == 1:
                        guild_name = "Tin nhắn riêng (Direct Message)"
                    elif ch_type == 3:
                        guild_name = "Nhóm riêng (Group Chat)"
                    else:
                        guild_name = "Không thuộc máy chủ"
                
                return {
                    "valid": True,
                    "id": channel_id,
                    "name": ch_name,
                    "type_name": get_channel_type_name(ch_type),
                    "guild_id": guild_id or "N/A",
                    "guild_name": guild_name,
                    "guild_icon_url": guild_icon_url
                }
            elif response.status_code == 401:
                last_error = "Token không hợp lệ hoặc hết hạn"
                continue  # Thử token tiếp theo
            elif response.status_code == 403:
                last_error = "Tài khoản không có quyền xem kênh này (hoặc chưa tham gia server)"
                continue  # Thử token tiếp theo
            elif response.status_code == 404:
                return {
                    "valid": False,
                    "id": channel_id,
                    "error": "Không tìm thấy Channel ID này trên Discord"
                }
            elif response.status_code == 429:
                return {
                    "valid": False,
                    "id": channel_id,
                    "error": "Bị Discord giới hạn tần suất (Rate Limit), vui lòng thử lại sau"
                }
            else:
                last_error = f"Lỗi Discord API (HTTP {response.status_code})"
                
        except requests.exceptions.RequestException as e:
            last_error = f"Lỗi kết nối mạng: {str(e)}"
            
    return {
        "valid": False,
        "id": channel_id,
        "error": last_error
    }

