# profiles.py
# Quản lý Profile riêng cho từng Token - chat / delay / tính năng độc lập
# Author: bluemanhst

import copy
import uuid

_FALLBACK_FEATURES = {
    "auto_delete": False,
    "delete_delay_ms": 0,
    "auto_typing": False,
    "typing_min_sec": 2,
    "typing_max_sec": 5,
    "auto_break": False,
    "break_after_min": 15,
    "break_after_max": 25,
    "break_duration_min": 10,
    "break_duration_max": 30,
    "auto_stop_on_ban": True,
    "schedule": False,
    "schedule_start": "09:00",
    "schedule_end": "17:00",
    "smart_templates": False,
    "sound_enabled": False,
    "sound_error": True,
    "sound_stop": True,
    "sound_success": True,
    "tray_enabled": False,
    "startup_enabled": False,
}


def _base_template():
    """Template global: ưu tiên đọc từ config nếu có, không import cứng để tránh vòng lặp."""
    try:
        from config import DEFAULT_CONFIG
        return copy.deepcopy(DEFAULT_CONFIG)
    except Exception:
        return {
            "channel_ids": [""],
            "custom_message": ["Hello"],
            "cooldown_min": 60,
            "cooldown_max": 90,
            "features": copy.deepcopy(_FALLBACK_FEATURES),
        }


def default_profile(name="Acc 1", token=""):
    """Tạo 1 profile mới từ template global hiện tại."""
    base = _base_template()
    return {
        "id": f"prof_{uuid.uuid4().hex[:8]}",
        "name": name,
        "token": (token or "").strip(),
        "enabled": True,
        "channel_ids": list(base.get("channel_ids", [""])),
        "messages": list(base.get("custom_message", ["Hello"])),
        "cooldown_min": int(base.get("cooldown_min", 60)),
        "cooldown_max": int(base.get("cooldown_max", 90)),
        "features": copy.deepcopy(base.get("features", {})),
    }


def normalize_profile(raw, index=1, fallback=None):
    """Chuẩn hoá 1 profile, thiếu gì bù đó, sai range thì tự sửa."""
    fb = fallback or default_profile(name=f"Acc {index}")
    if not isinstance(raw, dict):
        raw = {}
    out = copy.deepcopy(fb)
    out.update({k: v for k, v in raw.items() if k in out})

    out["id"] = str(raw.get("id") or out["id"])
    out["name"] = str(raw.get("name") or f"Acc {index}").strip() or f"Acc {index}"
    out["token"] = str(raw.get("token", "") or "").strip()
    out["enabled"] = bool(raw.get("enabled", True))

    def _clean_list(values, default):
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, (list, tuple)):
            return list(default)
        cleaned = [str(v).strip() for v in values if str(v).strip()]
        return cleaned or list(default)

    out["channel_ids"] = _clean_list(raw.get("channel_ids"), fb["channel_ids"])
    out["messages"] = _clean_list(raw.get("messages"), fb["messages"])

    def _int(value, default):
        try:
            return max(0, int(float(str(value).strip())))
        except (TypeError, ValueError):
            return default

    def _clean_channel_messages(raw_msgs):
        """Chat riêng của kênh: mỗi phần tử = 1 tin, giữ nguyên xuống hàng trong tin."""
        if isinstance(raw_msgs, str):
            raw_msgs = [raw_msgs]
        if not isinstance(raw_msgs, (list, tuple)):
            return []
        return [str(m).strip() for m in raw_msgs if str(m).strip()]

    def _normalize_channels(raw_channels, default_min, default_max, fallback_ids):
        channels = []
        if isinstance(raw_channels, list) and raw_channels:
            for ch in raw_channels:
                ch_msgs = []
                if isinstance(ch, dict):
                    cid = str(ch.get("id") or "").strip()
                    if not cid:
                        continue
                    cd_min = _int(ch.get("cd_min"), default_min)
                    cd_max = _int(ch.get("cd_max"), default_max)
                    ch_msgs = _clean_channel_messages(ch.get("messages"))
                else:
                    cid = str(ch).strip()
                    if not cid:
                        continue
                    cd_min, cd_max = default_min, default_max
                if cd_min > cd_max:
                    cd_min, cd_max = cd_max, cd_min
                channels.append({"id": cid, "cd_min": cd_min, "cd_max": cd_max,
                                 "messages": ch_msgs})
            seen, dedup = set(), []
            for c in channels:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    dedup.append(c)
            return dedup
        if fallback_ids:
            return [{"id": c, "cd_min": default_min, "cd_max": default_max,
                     "messages": []} for c in fallback_ids]
        return []

    out["channels"] = _normalize_channels(
        raw.get("channels"), out["cooldown_min"], out["cooldown_max"], out["channel_ids"])
    out["channel_ids"] = [c["id"] for c in out["channels"]]

    out["cooldown_min"] = _int(raw.get("cooldown_min"), fb["cooldown_min"])
    out["cooldown_max"] = _int(raw.get("cooldown_max"), fb["cooldown_max"])
    if out["cooldown_min"] > out["cooldown_max"]:
        out["cooldown_min"], out["cooldown_max"] = out["cooldown_max"], out["cooldown_min"]

    feats = raw.get("features") if isinstance(raw.get("features"), dict) else {}
    base_feats = copy.deepcopy(fb.get("features", {}))
    for key, default in base_feats.items():
        value = feats.get(key, default)
        if isinstance(default, bool):
            base_feats[key] = bool(value)
        elif isinstance(default, (int, float)):
            base_feats[key] = _int(value, default)
        else:
            base_feats[key] = value if isinstance(value, str) and value.strip() else default
    for low, high in (("typing_min_sec", "typing_max_sec"),
                      ("break_after_min", "break_after_max"),
                      ("break_duration_min", "break_duration_max")):
        if base_feats.get(low, 0) > base_feats.get(high, 0):
            base_feats[low], base_feats[high] = base_feats[high], base_feats[low]
    out["features"] = base_feats
    return out


def migrate_legacy_to_profiles(config_data):
    """Migrate config cũ tokens[] chung -> profiles[] riêng, giữ nguyên settings cũ."""
    tokens = [str(t).strip() for t in config_data.get("tokens", []) if str(t).strip()]
    if not tokens:
        tokens = [""]
    legacy_channels = list(config_data.get("channel_ids", [""]) or [""])
    legacy_messages = list(config_data.get("custom_message", ["Hello"]) or ["Hello"])
    try:
        legacy_min = max(0, int(config_data.get("cooldown_min", 60)))
    except (TypeError, ValueError):
        legacy_min = 60
    try:
        legacy_max = max(0, int(config_data.get("cooldown_max", 90)))
    except (TypeError, ValueError):
        legacy_max = 90
    if legacy_min > legacy_max:
        legacy_min, legacy_max = legacy_max, legacy_min
    legacy_features = copy.deepcopy(config_data.get("features", {}) or {})
    profiles = []
    for i, token in enumerate(tokens, start=1):
        prof = default_profile(name=f"Acc {i}", token=token)
        prof["channel_ids"] = list(legacy_channels)
        prof["messages"] = list(legacy_messages)
        prof["cooldown_min"] = legacy_min
        prof["cooldown_max"] = legacy_max
        merged = copy.deepcopy(prof["features"])
        merged.update(copy.deepcopy(legacy_features))
        prof["features"] = merged
        profiles.append(normalize_profile(prof, index=i))
    return profiles


def ensure_profiles(config_data):
    """Đảm bảo config luôn có profiles[] hợp lệ, tự migrate nếu thiếu.

    Update IN-PLACE để giữ reference cho panel (tránh stale list):
    - Không gán list mới, mà mutate list/dict cũ đang được UI giữ.
    """
    raw_profiles = config_data.get("profiles")
    if isinstance(raw_profiles, list) and raw_profiles:
        fallback = default_profile()
        cleaned = [normalize_profile(p, index=i, fallback=fallback)
                   for i, p in enumerate(raw_profiles, start=1)]
        # Update in-place: giữ nguyên object list cũ
        for i, new_prof in enumerate(cleaned):
            if i < len(raw_profiles) and isinstance(raw_profiles[i], dict):
                raw_profiles[i].clear()
                raw_profiles[i].update(new_prof)
            elif i < len(raw_profiles):
                raw_profiles[i] = new_prof
            else:
                raw_profiles.append(new_prof)
        while len(raw_profiles) > len(cleaned):
            raw_profiles.pop()
        config_data["profiles"] = raw_profiles
        return raw_profiles
    profiles = migrate_legacy_to_profiles(config_data)
    existing = config_data.get("profiles")
    if isinstance(existing, list):
        existing.clear()
        existing.extend(profiles)
        return existing
    config_data["profiles"] = profiles
    return profiles


def short_profile_name(profile, index=1):
    name = str(profile.get("name") or f"Acc {index}").strip() or f"Acc {index}"
    token = str(profile.get("token") or "").strip()
    mark = "" if profile.get("enabled", True) else " [TẮT]"
    if token and len(token) > 10:
        return f"{name} ({token[:4]}...{token[-4:]}){mark}"
    if token:
        return f"{name}{mark}"
    return f"{name} (chưa có token){mark}"
