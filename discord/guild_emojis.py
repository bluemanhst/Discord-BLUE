# discord/guild_emojis.py
# Tra danh sách emoji custom (guild) theo channel — dùng cho preview chat.
# Author: bluemanhst

import threading

import requests

from utils.constants import DISCORD_API_BASE

# Cache theo guild_id, sống trong phiên (không ghi ra file)
_cache = {}
_lock = threading.Lock()


def emoji_image_url(emoji_id, animated=False, size=48):
    """URL ảnh emoji trên CDN Discord (gif nếu animated)."""
    ext = "gif" if animated else "png"
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size={size}"


def get_guild_id(channel_id, token):
    """Lấy guild_id chứa channel bằng user token. Thất bại -> None."""
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(f"{DISCORD_API_BASE}/channels/{str(channel_id).strip()}",
                         headers=headers, timeout=8)
        if r.status_code == 200:
            gid = r.json().get("guild_id")
            return str(gid) if gid else None
    except Exception:
        pass
    return None


def fetch_emojis_for_channel(channel_id, token, use_cache=True):
    """Trả {name_lower: {"id", "animated}} của guild chứa channel.

    - Dùng user token (giống channel_validator).
    - Cache theo guild_id trong phiên; lỗi/403 -> {} (preview vẫn render markdown).
    """
    guild_id = get_guild_id(channel_id, token)
    if not guild_id:
        return {}
    if use_cache:
        with _lock:
            hit = _cache.get(guild_id)
        if hit is not None:
            return hit
    headers = {"Authorization": token, "Content-Type": "application/json"}
    try:
        r = requests.get(f"{DISCORD_API_BASE}/guilds/{guild_id}/emojis",
                         headers=headers, timeout=8)
        if r.status_code != 200:
            return {}
        out = {}
        for e in r.json() or []:
            name = str(e.get("name") or "").lower()
            eid = str(e.get("id") or "")
            if name and eid:
                out[name] = {"id": eid, "animated": bool(e.get("animated"))}
        with _lock:
            _cache[guild_id] = out
        return out
    except Exception:
        return {}
