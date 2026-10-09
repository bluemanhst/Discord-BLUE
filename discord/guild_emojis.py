# discord/guild_emojis.py
# Tra danh sach emoji custom (guild) - cho preview chat + thu vien emoji.
# Nitro: user dung duoc emoji cua MOI server da join -> fetch toan bo guild.
# Author: bluemanhst

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from utils.constants import DISCORD_API_BASE

# Cache theo guild_id, song trong phien (khong ghi ra file)
_cache = {}
_lock = threading.Lock()

# Cache guild_id theo channel (session-level, tranh goi lai API)
_guild_id_cache = {}

# Cache dia thu vien emoji (canh config.json / exe)
EMOJI_CACHE_FILE = "emoji_cache.json"
EMOJI_CACHE_TTL = 24 * 60 * 60  # 24 gio

# Build thu vien 1 lan/process
_lib_building = False
_lib_callbacks = []


def emoji_image_url(emoji_id, animated=False, size=48):
    """URL anh emoji tren CDN Discord (gif neu animated)."""
    ext = "gif" if animated else "png"
    return f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size={size}"


def get_guild_id(channel_id, token):
    """Lay guild_id chua channel bang user token. That bai -> None.
    Cache session theo (channel, token) de khong goi lai API."""
    key = (str(channel_id).strip(), str(token))
    with _lock:
        if key in _guild_id_cache:
            return _guild_id_cache[key]
    headers = {"Authorization": token, "Content-Type": "application/json"}
    gid = None
    try:
        r = requests.get(f"{DISCORD_API_BASE}/channels/{str(channel_id).strip()}",
                         headers=headers, timeout=8)
        if r.status_code == 200:
            g = r.json().get("guild_id")
            gid = str(g) if g else None
    except Exception:
        pass
    with _lock:
        _guild_id_cache[key] = gid
    return gid


def fetch_emojis_for_channel(channel_id, token, use_cache=True):
    """Tra {name_lower: {"id", "animated"}} cua guild chua channel.

    - Dung user token (giong channel_validator).
    - Cache theo guild_id trong phien; loi/403 -> {} (preview van render markdown).
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


# ===== CHON SERVER DUNG EMOJI (Nitro: tick server can dung) =====
# Popup thu vien chi hien danh sach server (ten + avatar), KHONG tai emoji
# o at -> het lag. Emoji JSON cua server da tick moi duoc fetch (vai KB).

# Cache session danh sach guild theo token (tranh goi lai API)
_guild_list_cache = {}


def list_user_guilds(token, timeout=8):
    """Danh sach server user da join: [{id, name, icon}] (co cache session).

    - icon: hash avatar server (None neu server khong co avatar).
    - Loi/timeout -> [] (popup hien trang thai loi, khong crash).
    """
    t = str(token or "")
    if not t:
        return []
    with _lock:
        hit = _guild_list_cache.get(t)
    if hit is not None:
        return [dict(g) for g in hit]
    headers = {"Authorization": t, "Content-Type": "application/json"}
    out = []
    after = None
    try:
        for _ in range(5):
            url = f"{DISCORD_API_BASE}/users/@me/guilds?limit=200"
            if after:
                url += f"&after={after}"
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code != 200:
                break
            data = r.json() or []
            if not data:
                break
            for g in data:
                gid = str(g.get("id") or "")
                if gid:
                    out.append({"id": gid,
                                "name": str(g.get("name") or gid),
                                "icon": g.get("icon")})
            if len(data) < 200:
                break
            after = out[-1]["id"] if out else None
    except Exception:
        pass
    with _lock:
        _guild_list_cache[t] = [dict(g) for g in out]
    return out


def guild_icon_url(guild_id, icon_hash, size=64):
    """URL avatar server; None neu server khong dat avatar (hien chu cai)."""
    if not icon_hash:
        return None
    ext = "gif" if str(icon_hash).startswith("a_") else "png"
    return (f"https://cdn.discordapp.com/icons/{guild_id}/"
            f"{icon_hash}.{ext}?size={size}")


def fetch_emojis_for_guilds(token, guild_ids, timeout=6, max_workers=4):
    """Chi fetch emoji cua server da tick -> {name_lower: {id, animated, guild_id}}.

    - Thu tu guild_ids = thu tu uu tien khi trung ten (server tick truoc thang).
    - Guild cua channel dang chat phai de DAU TIEN (uu tien cao nhat).
    - Server loi/timeout -> bo qua, khong anh huong server khac.
    """
    gids = [str(g).strip() for g in (guild_ids or []) if str(g).strip()]
    if not gids or not str(token or ""):
        return {}
    seen, ordered = set(), []
    for g in gids:
        if g not in seen:
            seen.add(g)
            ordered.append(g)
    headers = {"Authorization": str(token), "Content-Type": "application/json"}

    def _work(gid):
        try:
            r = requests.get(f"{DISCORD_API_BASE}/guilds/{gid}/emojis",
                             headers=headers, timeout=timeout)
            if r.status_code != 200:
                return []
            out = []
            for e in r.json() or []:
                name = str(e.get("name") or "").lower()
                eid = str(e.get("id") or "")
                if name and eid:
                    out.append((name, {"id": eid,
                                       "animated": bool(e.get("animated")),
                                       "guild_id": gid}))
            return out
        except Exception:
            return []

    merged = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for result in ex.map(_work, ordered):
            for name, info in result:
                if name not in merged:
                    merged[name] = info
    return merged


def build_selected_emoji_map(token, channel_id, selected_guild_ids):
    """Map emoji cho preview/gui: guild cua channel + server da tick.

    Thu tu uu tien khi trung ten (vi du :test: o ca sv1 va sv2):
      1. guild cua channel dang chat (dung ngu canh nhat),
      2. server tick dau tien, 3. cac server tick con lai theo thu tu.
    Khong co channel/token -> chi dung thu tu tick. Loi -> {}.
    """
    gid = None
    try:
        if channel_id:
            gid = get_guild_id(str(channel_id), token)
    except Exception:
        gid = None
    ordered = ([gid] if gid else []) + \
        [str(g).strip() for g in (selected_guild_ids or []) if str(g).strip()]
    if not ordered:
        return {}
    try:
        return fetch_emojis_for_guilds(token, ordered)
    except Exception:
        return {}

# ===== THU VIEN EMOJI TOAN CUC (giữ làm fallback khi acc chưa tick server) =====
def _cache_path():
    from utils.paths import user_path
    return user_path(EMOJI_CACHE_FILE)


def load_disk_cache(max_age=EMOJI_CACHE_TTL, path=None):
    """Doc cache dia; None neu khong co / loi / qua han (max_age giay)."""
    try:
        p = path if path else _cache_path()
        if not os.path.exists(p):
            return None
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        if time.time() - float(data.get("time", 0)) > max_age:
            return None
        emojis = data.get("emojis")
        return emojis if isinstance(emojis, dict) else None
    except Exception:
        return None


def save_disk_cache(emoji_map, path=None):
    """Ghi cache dia (that bai -> bo qua, khong anh huong chay)."""
    try:
        with open(path or _cache_path(), "w", encoding="utf-8") as f:
            json.dump({"time": time.time(), "emojis": emoji_map},
                      f, ensure_ascii=False)
    except Exception:
        pass


def merge_emoji_maps(base_map, prefer_guild_id):
    """Map moi: emoji cua prefer_guild_id thang khi trung ten (uu tien hien thi
    + resolve). Tham so khong hop le -> tra ban sao dict goc."""
    base = dict(base_map or {})
    if not prefer_guild_id or not isinstance(base_map, dict):
        return base
    prefer, rest = {}, {}
    for k, v in base.items():
        if str((v or {}).get("guild_id") or "") == str(prefer_guild_id):
            prefer[k] = v
        else:
            rest[k] = v
    for k, v in rest.items():
        if k not in prefer:
            prefer[k] = v
    return prefer


def _list_guild_ids(token, headers, timeout):
    """Danh sach guild user da join (GET /users/@me/guilds, phan trang 200)."""
    ids = []
    after = None
    for _ in range(5):
        url = f"{DISCORD_API_BASE}/users/@me/guilds?limit=200"
        if after:
            url += f"&after={after}"
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code != 200:
                break
            data = r.json() or []
            if not data:
                break
            for g in data:
                gid = str(g.get("id") or "")
                if gid:
                    ids.append(gid)
            if len(data) < 200:
                break
            after = ids[-1]
        except Exception:
            break
    return ids


def fetch_all_guild_emojis(token, prefer_guild_id=None, use_cache=True,
                           save_cache=True, max_workers=8, timeout=6):
    """Lay emoji cua MOI guild -> {name_lower: {"id","animated","guild_id"}}.

    - prefer_guild_id: guild cua channel -> fetch truoc (thang khi trung ten).
    - use_cache: doc cache dia neu con fresh (TTL 24h).
    - Song song max_workers thread, timeout 6s, server loi -> bo qua.
    """
    if use_cache:
        cached = load_disk_cache()
        if cached is not None:
            return merge_emoji_maps(cached, prefer_guild_id)
    headers = {"Authorization": token, "Content-Type": "application/json"}
    guild_ids = _list_guild_ids(token, headers, timeout)
    if not guild_ids:
        return {}
    ordered = ([prefer_guild_id] if prefer_guild_id else []) + \
              [g for g in guild_ids if g != prefer_guild_id]

    def _work(gid):
        try:
            r = requests.get(f"{DISCORD_API_BASE}/guilds/{gid}/emojis",
                             headers=headers, timeout=timeout)
            if r.status_code != 200:
                return []
            out = []
            for e in r.json() or []:
                name = str(e.get("name") or "").lower()
                eid = str(e.get("id") or "")
                if name and eid:
                    out.append((name, {"id": eid,
                                       "animated": bool(e.get("animated")),
                                       "guild_id": gid}))
            return out
        except Exception:
            return []

    merged = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for result in ex.map(_work, ordered):
            for name, info in result:
                if name not in merged:
                    merged[name] = info
    if save_cache and merged:
        save_disk_cache(merged)
    return merged


def ensure_emoji_library(token, on_done=None, prefer_guild_id=None):
    """Build thu vien toan cuc 1 lan/process trong thread rieng.

    on_done(emoji_map) duoc goi trong THREAD NGUON -> caller phai marshal ve
    main thread (win.after) neu can update UI.
    """
    global _lib_building
    if callable(on_done):
        with _lock:
            _lib_callbacks.append(on_done)
    with _lock:
        if _lib_building:
            return
        _lib_building = True

    def _run():
        global _lib_building
        try:
            emap = fetch_all_guild_emojis(token, prefer_guild_id=prefer_guild_id)
        except Exception:
            emap = {}
        with _lock:
            _lib_building = False
            cbs = list(_lib_callbacks)
            _lib_callbacks.clear()
        for cb in cbs:
            try:
                cb(emap)
            except Exception:
                pass

    threading.Thread(target=_run, daemon=True).start()
