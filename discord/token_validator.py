# discord/token_validator.py
# Validate Discord tokens và lấy thông tin tài khoản
# Author: bluemanhst

import requests
import json
from datetime import datetime
from utils.constants import DISCORD_API_BASE


def validate_token(token):
    """
    Validate một Discord token và lấy thông tin tài khoản
    
    Args:
        token (str): Discord token cần validate
    
    Returns:
        dict: Thông tin tài khoản hoặc None nếu token không hợp lệ
        {
            "valid": bool,
            "username": str,
            "discriminator": str,
            "id": str,
            "avatar": str,
            "email": str,
            "verified": bool,
            "mfa_enabled": bool,
            "phone": str,
            "locale": str,
            "flags": int,
            "premium_type": int,
            "public_flags": int,
            "token_type": str
        }
    """
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    try:
        # Gọi API lấy thông tin user
        response = requests.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "valid": True,
                "username": user_data.get("username", "Unknown"),
                "discriminator": user_data.get("discriminator", "0000"),
                "id": user_data.get("id", ""),
                "avatar": user_data.get("avatar", ""),
                "email": user_data.get("email", "N/A"),
                "verified": user_data.get("verified", False),
                "mfa_enabled": user_data.get("mfa_enabled", False),
                "phone": user_data.get("phone", "N/A"),
                "locale": user_data.get("locale", "en-US"),
                "flags": user_data.get("flags", 0),
                "premium_type": user_data.get("premium_type", 0),
                "public_flags": user_data.get("public_flags", 0),
                "token_type": determine_token_type(token)
            }
        elif response.status_code == 401:
            return {
                "valid": False,
                "error": "Token không hợp lệ hoặc hết hạn"
            }
        elif response.status_code == 403:
            return {
                "valid": False,
                "error": "Token bị khóa hoặc bị rate limit"
            }
        else:
            return {
                "valid": False,
                "error": f"Lỗi không xác định (HTTP {response.status_code})"
            }
            
    except Exception as e:
        return {
            "valid": False,
            "error": f"Lỗi kết nối: {str(e)}"
        }


def determine_token_type(token):
    """
    Xác định loại token (User Token, Bot Token, OAuth Token)
    
    Args:
        token (str): Discord token
    
    Returns:
        str: Loại token
    """
    if token.startswith("MFA"):
        return "MFA Token"
    elif len(token) == 59 and token.startswith("mfa"):
        return "MFA Token"
    elif len(token) == 72:
        return "Bot Token"
    elif len(token) >= 50 and len(token) <= 70:
        return "User Token"
    else:
        return "Unknown"


def validate_multiple_tokens(tokens):
    """
    Validate nhiều token cùng lúc
    
    Args:
        tokens (list): Danh sách Discord tokens
    
    Returns:
        list: Danh sách kết quả validate cho từng token
    """
    results = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
            
        result = validate_token(token)
        result["token"] = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else token
        results.append(result)
    
    return results


def get_avatar_url(user_id, avatar_hash, size=128):
    """
    Tạo URL avatar từ user_id và avatar_hash
    
    Args:
        user_id (str): Discord user ID
        avatar_hash (str): Avatar hash
        size (int): Kích thước avatar (mặc định 128)
    
    Returns:
        str: URL avatar hoặc None nếu không có avatar
    """
    if not avatar_hash:
        return None
    
    if avatar_hash.startswith("a_"):
        # Animated avatar
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.gif?size={size}"
    else:
        # Static avatar
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size={size}"


def check_token_age(user_data):
    """
    Kiểm tra "tuổi" của token (ước lượng dựa trên snowflake ID)
    
    Args:
        user_data (dict): Thông tin user từ validate_token
    
    Returns:
        dict: Thông tin về tuổi token
    """
    user_id = user_data.get("id", "")
    if not user_id:
        return {"age_days": "Unknown", "created_at": "Unknown"}
    
    try:
        # Discord snowflake timestamp
        timestamp = (int(user_id) >> 22) + 1420070400000
        created_at = datetime.fromtimestamp(timestamp / 1000)
        age_days = (datetime.now() - created_at).days
        
        return {
            "age_days": age_days,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {"age_days": "Unknown", "created_at": "Unknown"}