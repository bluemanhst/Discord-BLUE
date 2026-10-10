# utils/chat_markup.py
# Parse Markdown + emoji Discord thành segments để UI render preview chat.
# KHÔNG đổi nội dung gửi đi — chỉ dùng cho Xem trước.
# Author: bluemanhst

import json
import re

# Emoji copy từ bản chat Discord: <:name:id> hoặc <a:name:id> (animated)
_RE_EMOJI_ID = re.compile(r"<a?:([A-Za-z0-9_]{2,32}):(\d{10,})>")
# Emoji chỉ có tên (nhập tay): :name: — không khớp số giờ "10:30", URL "https:"
# Lookbehind loai '<' de khong match :name: ben trong <:name:id> co san
# Char class: chu/so/_ + '+' '-' (+1/-1) + Latinh mo rong (piñata); do dai 1-64
# de bat ten 1 ky tu (:a: :b: :x:) va ten dai (face_with_open_eyes...).
_RE_EMOJI_NAME = re.compile(r"(?<![\w:<]):([A-Za-z0-9À-ÿ_+\-]{1,64}):(?![\w:])")
_RE_CODE = re.compile(r"`([^`\n]+)`")
_RE_BOLD = re.compile(r"\*\*([^\*\n]+)\*\*")
_RE_STRIKE = re.compile(r"~~([^~\n]+)~~")
_RE_UNDER = re.compile(r"__([^_\n]+)__")
_RE_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

# ===== EMOJI GỐC UNICODE CỦA DISCORD (không cần guild/network) ====="
# ===== EMOJI GỐC UNICODE CỦA DISCORD (không cần guild/network) =====
# Bảng shortcode -> ký tự emoji thật (vd "face_holding_back_tears" -> 🥹).
# Load lazy 1 lần/process từ assets/emoji_unicode.json (bundle trong EXE).
# Dùng khi :name: không phải custom emoji của server -> gửi/preview hiện icon.
_UNICODE_EMOJI = None  # cache {name_lower: char}


def _load_unicode_emoji():
    """Đọc assets/emoji_unicode.json 1 lần, trả {name_lower: char}. Lỗi -> {}."""
    global _UNICODE_EMOJI
    if _UNICODE_EMOJI is not None:
        return _UNICODE_EMOJI
    data = {}
    try:
        from utils.paths import resource_path
        path = resource_path("assets", "emoji_unicode.json")
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            for name, char in raw.items():
                if isinstance(name, str) and isinstance(char, str) and char:
                    data[name.lower()] = char
    except Exception:
        data = {}
    _UNICODE_EMOJI = data
    return _UNICODE_EMOJI


def unicode_emoji(name):
    """Tra ký tự emoji gốc theo shortcode (không phân biệt hoa/thường).

    Trả về char (vd '🥹') nếu `:name:` là emoji Unicode của Discord, else None.
    Thuần O(1) sau lần load đầu — không network, không lag.
    """
    if not name:
        return None
    return _load_unicode_emoji().get(str(name).lower())


# CDN Twemoji (ảnh PNG màu) — render preview cho emoji gốc (Tkinter không tô màu).
# jdecked/twemoji là bản fork duy trì của Twitter Twemoji (MIT).
_TWEMOJI_CDN = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/72x72"


def twemoji_url(char, size=None):
    """URL ảnh PNG màu (Twemoji) cho 1 ký tự emoji Unicode.

    Chuyển ký tự -> codepoint hex thường, bỏ U+FE0F (variation selector),
    nhiều codepoint (ZWJ/skin-tone) nối bằng '-'. Trả None nếu không phải emoji.
    Dùng cho PREVIEW (Tkinter Text không render được color emoji).
    """
    if not char:
        return None
    cps = []
    for ch in str(char):
        cp = ord(ch)
        if cp == 0xFE0F:      # bỏ variation selector-16
            continue
        if cp == 0x200D:      # giữ ZWJ trong chuỗi nối
            cps.append(cp)
            continue
        cps.append(cp)
    if not cps:
        return None
    hexed = "-".join("%x" % c for c in cps)
    url = f"{_TWEMOJI_CDN}/{hexed}.png"
    if size:
        url += f"?size={size}"
    return url

# Thứ tự ưu tiên khi trùng vị trí bắt: code > bold > strike > underline > italic > emoji
_PATTERNS = (
    ("code", _RE_CODE),
    ("bold", _RE_BOLD),
    ("strike", _RE_STRIKE),
    ("underline", _RE_UNDER),
    ("italic", _RE_ITALIC),
    ("emoji_id", _RE_EMOJI_ID),
    ("emoji_name", _RE_EMOJI_NAME),
)


def parse_markup(text):
    """Tách tin nhắn thành list segment phẳng để render preview.

    Segment (dict):
      {"type": "text", "text": str, "styles": set}
          # styles ⊆ {bold, italic, strike, underline, code}
      {"type": "emoji_id", "name": str, "id": str, "animated": bool}
          # <:name:id> / <a:name:id> — tải thẳng từ CDN, không cần guild API
      {"type": "emoji_name", "name": str}
          # :name: — cần tra trong emoji list của guild
      {"type": "newline"}
    """
    segments = []
    lines = str(text if text is not None else "").split("\n")
    for i, line in enumerate(lines):
        if i:
            segments.append({"type": "newline"})
        _parse_line(line, frozenset(), segments)
    return segments


def _parse_line(line, styles, out):
    """Tìm token bắt sớm nhất trong dòng, tách text thường còn lại, đệ quy tiếp."""
    best_pos, best_m, best_kind = None, None, None
    for kind, rx in _PATTERNS:
        m = rx.search(line)
        if m and (best_pos is None or m.start() < best_pos):
            best_pos, best_m, best_kind = m.start(), m, kind
    if best_m is None:
        if line:
            out.append({"type": "text", "text": line, "styles": set(styles)})
        return
    if best_pos:
        out.append({"type": "text", "text": line[:best_pos], "styles": set(styles)})
    m, kind = best_m, best_kind
    if kind == "emoji_id":
        out.append({"type": "emoji_id", "name": m.group(1),
                    "id": m.group(2), "animated": m.group(0).startswith("<a:")})
    elif kind == "emoji_name":
        out.append({"type": "emoji_name", "name": m.group(1)})
    else:
        inner = m.group(1)
        if kind == "code":
            # Trong `code` không render tiếp markup
            out.append({"type": "text", "text": inner,
                        "styles": set(styles | {kind})})
        else:
            _parse_line(inner, styles | {kind}, out)
    _parse_line(line[m.end():], styles, out)


def resolve_emoji_shortcodes(text, emoji_map):
    """Đổi :name: -> <:name:id> (hoặc <a:name:id> nếu animated) trước khi GỬI.

    Discord chỉ render custom emoji với format CÓ ID; text `:name:` thuần sẽ
    hiện nguyên văn trong chat. Hàm này thuần (không network) — emoji_map do
    caller tra từ guild_emojis.fetch_emojis_for_channel.

    Args:
        text: tin nhắn gốc (giữ nguyên phần markdown/text khác).
        emoji_map: {name_lower: {"id": str, "animated": bool}}

    Returns:
        str: chuỗi đã convert theo thứ tự ưu tiên:
            1) custom emoji có ID trong emoji_map (guild);
            2) emoji gốc Unicode của Discord (:smile: -> 😄, :two: -> 2️⃣, :+1: -> 👍);
            3) không match gì -> giữ nguyên :name:.
        (Gửi và preview dùng CHUNG nguồn unicode_emoji -> luôn đồng bộ.)
    """
    if not text:
        return str(text if text is not None else "")

    def _sub(m):
        name = m.group(1)
        # 1) Ưu tiên custom emoji có ID trong map (guild).
        info = (emoji_map or {}).get(name.lower())
        if info and info.get("id"):
            prefix = "<a:" if info.get("animated") else "<:"
            return f"{prefix}{name}:{info['id']}>"
        # 2) Fallback: emoji gốc Unicode của Discord -> ký tự emoji thật.
        #    (vd :smile: -> 😄, :two: -> 2️⃣, :+1: -> 👍, :piñata: -> 🪅)
        #    Cùng nguồn với preview nên gửi/preview luôn khớp nhau.
        uni = unicode_emoji(name)
        if uni:
            return uni
        # 3) Không match gì -> giữ nguyên :name:
        return m.group(0)

    return _RE_EMOJI_NAME.sub(_sub, str(text))
