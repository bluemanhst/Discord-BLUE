# utils/chat_markup.py
# Parse Markdown + emoji Discord thành segments để UI render preview chat.
# KHÔNG đổi nội dung gửi đi — chỉ dùng cho Xem trước.
# Author: bluemanhst

import re

# Emoji copy từ bản chat Discord: <:name:id> hoặc <a:name:id> (animated)
_RE_EMOJI_ID = re.compile(r"<a?:([A-Za-z0-9_]{2,32}):(\d{10,})>")
# Emoji chỉ có tên (nhập tay): :name: — không khớp số giờ "10:30", URL "https:"
# Lookbehind loai '<' de khong match :name: ben trong <:name:id> co san
_RE_EMOJI_NAME = re.compile(r"(?<![\w:<]):([A-Za-z0-9_]{2,32}):(?![\w:])")
_RE_CODE = re.compile(r"`([^`\n]+)`")
_RE_BOLD = re.compile(r"\*\*([^\*\n]+)\*\*")
_RE_STRIKE = re.compile(r"~~([^~\n]+)~~")
_RE_UNDER = re.compile(r"__([^_\n]+)__")
_RE_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")

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
        str: chuỗi đã convert; name không có trong map -> giữ nguyên.
    """
    if not emoji_map or not text:
        return str(text if text is not None else "")

    def _sub(m):
        name = m.group(1)
        info = emoji_map.get(name.lower())
        if not info or not info.get("id"):
            return m.group(0)
        prefix = "<a:" if info.get("animated") else "<:"
        return f"{prefix}{name}:{info['id']}>"

    return _RE_EMOJI_NAME.sub(_sub, str(text))
