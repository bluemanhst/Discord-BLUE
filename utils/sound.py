# utils/sound.py
# Phát âm thanh thông báo - trạng thái bật/tắt được chia sẻ giữa UI và các thread
# Author: bluemanhst

import threading

# ===== TRẠNG THÁI BẬT/TẮT TỪNG LOẠI ÂM THANH =====
_enabled = {
    "error": False,
    "stop": False,
    "success": False
}

# ===== ÂM THANH TƯƠNG ỨNG (tần số Hz, thời lượng ms) =====
_TONES = {
    "error": (500, 200),
    "stop": (300, 300),
    "success": (800, 100)
}

_lock = threading.Lock()


def set_enabled(sound_type, value):
    """
    Bật/tắt 1 loại âm thanh

    Args:
        sound_type (str): "error", "stop" hoặc "success"
        value (bool): Trạng thái mới
    """
    with _lock:
        if sound_type in _enabled:
            _enabled[sound_type] = bool(value)


def set_all(values):
    """
    Cập nhật nhiều loại âm thanh cùng lúc

    Args:
        values (dict): Ví dụ {"error": True, "stop": False, "success": True}
    """
    with _lock:
        for sound_type, value in values.items():
            if sound_type in _enabled:
                _enabled[sound_type] = bool(value)


def is_enabled(sound_type):
    """Kiểm tra 1 loại âm thanh có đang bật không"""
    with _lock:
        return bool(_enabled.get(sound_type, False))


def notify(sound_type):
    """
    Phát âm thanh nếu loại đó đang bật.
    An toàn khi gọi từ thread phụ (thread-safe, tự bỏ qua mọi lỗi).

    Args:
        sound_type (str): "error", "stop" hoặc "success"
    """
    if not is_enabled(sound_type):
        return

    try:
        import winsound
        frequency, duration = _TONES.get(sound_type, (600, 150))
        winsound.Beep(frequency, duration)
    except Exception:
        pass  # Không phát được âm thanh thì bỏ qua, không ảnh hưởng tool
