# language.py
# Quản lý đa ngôn ngữ cho ứng dụng
# Author: bluemanhst

import json
import os
from config import config_data
from utils.constants import LANGUAGES_DIR

# ===== CẤU HÌNH NGÔN NGỮ =====
DEFAULT_LANGUAGE = "vietnamese"

# ===== DANH SÁCH NGÔN NGỮ HỖ TRỢ =====
SUPPORTED_LANGUAGES = {
    "vietnamese": "Tiếng Việt",
    "english": "English"
}

# ===== BIẾN TOÀN CỤC =====
_current_language = None
_translations = {}


def load_language(language_code):
    """
    Load file ngôn ngữ từ JSON
    
    Args:
        language_code (str): Mã ngôn ngữ (vietnamese, english)
    
    Returns:
        dict: Dữ liệu dịch hoặc None nếu lỗi
    """
    global _translations
    
    file_path = os.path.join(LANGUAGES_DIR, f"{language_code}.json")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            _translations = json.load(f)
        return _translations
    except FileNotFoundError:
        print(f"Language file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing language file: {e}")
        return None


def get_current_language():
    """
    Lấy ngôn ngữ hiện tại từ config
    
    Returns:
        str: Mã ngôn ngữ hiện tại
    """
    global _current_language
    
    if _current_language is None:
        # Lấy từ config, nếu không có thì dùng mặc định
        _current_language = config_data.get("language", DEFAULT_LANGUAGE)

    # Code trong config không còn được hỗ trợ (vd: "chinese" đã bị gỡ) -> về mặc định
    if _current_language not in SUPPORTED_LANGUAGES:
        _current_language = DEFAULT_LANGUAGE

    return _current_language


def set_language(language_code):
    """
    Đặt ngôn ngữ hiện tại và load file dịch
    
    Args:
        language_code (str): Mã ngôn ngữ
    """
    global _current_language
    
    if language_code not in SUPPORTED_LANGUAGES:
        print(f"Unsupported language: {language_code}")
        return False
    
    _current_language = language_code
    load_language(language_code)
    
    # Lưu vào config
    config_data["language"] = language_code
    from config import save_config
    save_config(config_data)
    
    return True


def translate(key_path, *args):
    """
    Dịch một key theo đường dẫn dạng "section.key"
    
    Args:
        key_path (str): Đường dẫn key, ví dụ "main_page.tokens_label"
        *args: Các tham số để format vào chuỗi
    
    Returns:
        str: Chuỗi đã dịch hoặc key gốc nếu không tìm thấy
    """
    global _translations
    
    # Load ngôn ngữ nếu chưa load
    if not _translations:
        load_language(get_current_language())
    
    # Parse đường dẫn key
    keys = key_path.split('.')
    value = _translations

    try:
        for key in keys:
            value = value[key]

        if not isinstance(value, str):
            return key_path

        # Format với tham số nếu có
        if args:
            try:
                return value.format(*args)
            except (IndexError, KeyError, ValueError):
                # Thiếu/thừa tham số trong file dịch -> trả về chuỗi gốc
                # (tránh làm chết thread log của bot)
                return value
        return value
    except (KeyError, TypeError):
        # Trả về key gốc nếu không tìm thấy
        return key_path


def t(key_path, *args):
    """
    Shortcut cho translate()
    
    Args:
        key_path (str): Đường dẫn key
        *args: Các tham số để format
    
    Returns:
        str: Chuỗi đã dịch
    """
    return translate(key_path, *args)


def get_language_name(language_code):
    """
    Lấy tên hiển thị của ngôn ngữ
    
    Args:
        language_code (str): Mã ngôn ngữ
    
    Returns:
        str: Tên ngôn ngữ
    """
    return SUPPORTED_LANGUAGES.get(language_code, language_code)


def get_supported_languages():
    """
    Lấy danh sách ngôn ngữ được hỗ trợ
    
    Returns:
        dict: Dict {code: name}
    """
    return SUPPORTED_LANGUAGES.copy()


# Load ngôn ngữ mặc định khi import
load_language(get_current_language())