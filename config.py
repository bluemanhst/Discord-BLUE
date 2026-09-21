# config.py
# Quản lý cấu hình của tool - Load/Save/Export/Import
# Author: bluemanhst

import copy
import json
import os
from tkinter import filedialog, messagebox
from utils.constants import CONFIG_FILE


# ===== CẤU HÌNH MẶC ĐỊNH =====
DEFAULT_CONFIG = {
    "language": "vietnamese",
    "current_theme": "Dragon Ball (Mặc định)",
    "tokens": [""],
    "channel_ids": [""],
    "cooldown_min": 60,
    "cooldown_max": 90,
    "custom_message": ["Hello"],
    "features": {
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
        "startup_enabled": False
    }
}

# Các key tính năng của những phiên bản trước đã bị gỡ bỏ (tự động dọn khi load/save)
REMOVED_FEATURE_KEYS = (
    "status_simulation",
    "activity_simulation",
    "activity_change_interval",
    "default_activity_type",
    "default_game_name",
    "dashboard_enabled",
    "auto_export_stats",
    "stats_export_interval"
)


def _show_error(title, message):
    """Hiện hộp thoại lỗi nếu UI sẵn sàng, nếu không thì in ra console"""
    try:
        messagebox.showerror(title, message)
    except Exception:
        print(f"[{title}] {message}")


def _clean_str_list(values):
    """Chuyển dữ liệu bất kỳ thành list[str] đã bỏ khoảng trắng và phần tử rỗng"""
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, (list, tuple)):
        return []
    result = []
    for value in values:
        text = str(value).strip()
        if text:
            result.append(text)
    return result


def _to_non_negative_int(value, default=0):
    """Ép giá trị về số nguyên không âm, sai định dạng thì trả về giá trị mặc định"""
    try:
        number = int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default
    return max(number, 0)


# ===== HÀM LOAD CẤU HÌNH =====
def load_config():
    """
    Đọc cấu hình từ file config.json
    Nếu file không tồn tại hoặc lỗi, trả về cấu hình mặc định

    Returns:
        dict: Cấu hình tool
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception:
        return copy.deepcopy(DEFAULT_CONFIG)

    if not isinstance(data, dict):
        return copy.deepcopy(DEFAULT_CONFIG)

    # Tương thích ngược với config cũ (chỉ có 1 channel_id dạng chuỗi)
    if "channel_ids" not in data and "channel_id" in data:
        data["channel_ids"] = [data["channel_id"]] if data["channel_id"] else [""]
        data.pop("channel_id", None)

    # Bổ sung các key tính năng mới + dọn các key tính năng đã gỡ bỏ
    features = data.get("features")
    if not isinstance(features, dict):
        features = {}
    for key in REMOVED_FEATURE_KEYS:
        features.pop(key, None)
    for key, value in DEFAULT_CONFIG["features"].items():
        features.setdefault(key, value)
    data["features"] = features

    # Bổ sung các key cấu hình còn thiếu ở cấp cao nhất
    for key, value in DEFAULT_CONFIG.items():
        if key != "features":
            data.setdefault(key, value)

    return data


# ===== HÀM CHUẨN HOÁ / KIỂM TRA CẤU HÌNH =====
def validate_config(raw_config):
    """
    Chuẩn hoá cấu hình: dọn key đã gỡ bỏ, đảm bảo đúng kiểu dữ liệu và tự sửa
    các giá trị nguy hiểm (cooldown min > max, số âm, danh sách rỗng...).

    Args:
        raw_config (dict): Cấu hình thô (thường là từ file import)

    Returns:
        tuple: (cấu_hình_đã_chuẩn_hoá hoặc None, danh sách cảnh báo)
    """
    warnings = []

    if not isinstance(raw_config, dict):
        return None, ["File cấu hình không phải JSON object!"]

    data = copy.deepcopy(DEFAULT_CONFIG)
    for key, value in raw_config.items():
        if key != "features":
            data[key] = value

    # ----- features -----
    raw_features = raw_config.get("features")
    if not isinstance(raw_features, dict):
        raw_features = {}
        warnings.append("Thiếu mục 'features' -> đã dùng giá trị mặc định")
    for key in REMOVED_FEATURE_KEYS:
        raw_features.pop(key, None)
    features = copy.deepcopy(DEFAULT_CONFIG["features"])
    for key in DEFAULT_CONFIG["features"]:
        if key in raw_features:
            features[key] = raw_features[key]
    data["features"] = features

    # ----- danh sách tokens / channels / messages -----
    data["tokens"] = _clean_str_list(data.get("tokens"))
    data["channel_ids"] = _clean_str_list(data.get("channel_ids"))
    if not data["tokens"]:
        warnings.append("Không có token hợp lệ trong file cấu hình")
    if not data["channel_ids"]:
        warnings.append("Không có Channel ID hợp lệ trong file cấu hình")
    data["custom_message"] = _clean_str_list(data.get("custom_message"))
    if not data["custom_message"]:
        data["custom_message"] = list(DEFAULT_CONFIG["custom_message"])
        warnings.append("Danh sách câu chat rỗng -> đã dùng giá trị mặc định")

    # ----- cooldown -----
    data["cooldown_min"] = _to_non_negative_int(data.get("cooldown_min"), DEFAULT_CONFIG["cooldown_min"])
    data["cooldown_max"] = _to_non_negative_int(data.get("cooldown_max"), DEFAULT_CONFIG["cooldown_max"])
    if data["cooldown_min"] > data["cooldown_max"]:
        data["cooldown_min"], data["cooldown_max"] = data["cooldown_max"], data["cooldown_min"]
        warnings.append("Cooldown Min lớn hơn Cooldown Max -> đã tự đổi lại")

    # ----- các ô số trong features -----
    for key in ("delete_delay_ms", "typing_min_sec", "typing_max_sec", "break_after_min",
                "break_after_max", "break_duration_min", "break_duration_max"):
        data["features"][key] = _to_non_negative_int(
            data["features"].get(key), DEFAULT_CONFIG["features"][key])

    for low_key, high_key in (("typing_min_sec", "typing_max_sec"),
                              ("break_after_min", "break_after_max"),
                              ("break_duration_min", "break_duration_max")):
        if data["features"][low_key] > data["features"][high_key]:
            data["features"][low_key], data["features"][high_key] = \
                data["features"][high_key], data["features"][low_key]
            warnings.append(f"{low_key} lớn hơn {high_key} -> đã tự đổi lại")

    return data, warnings



# ===== HÀM SAVE CẤU HÌNH =====
def save_config(config_data):
    """
    Lưu cấu hình vào file config.json

    Args:
        config_data (dict): Cấu hình cần lưu

    Returns:
        bool: True nếu lưu thành công
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        _show_error("Lỗi", f"Không thể lưu cấu hình:\n{CONFIG_FILE}\n\n{e}")
        return False


# ===== HÀM EXPORT CẤU HÌNH =====
def export_config(config=None):
    """
    Export cấu hình ra file JSON khác (backup)

    Args:
        config (dict|None): Cấu hình cần export. Bỏ trống = cấu hình hiện tại.
                            (Tham số có mặc định để nút Export có thể gọi trực tiếp)
    """
    if config is None:
        config = config_data

    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile="discord-blue-config.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        if not file_path:
            return False

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Thành công", f"Đã export cấu hình thành công!\n\nFile: {file_path}")
        return True
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể export cấu hình:\n{e}")
        return False


# ===== HÀM IMPORT CẤU HÌNH =====
def import_config(file_path=None):
    """
    Đọc cấu hình từ file JSON (chưa áp dụng gì cả)

    Args:
        file_path (str|None): Đường dẫn file; bỏ trống sẽ mở hộp thoại chọn file

    Returns:
        dict: Cấu hình đã import, hoặc None nếu lỗi
    """
    try:
        if not file_path:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import Configuration"
            )
        if not file_path:
            return None

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            imported_config = json.load(f)

        if not isinstance(imported_config, dict):
            messagebox.showerror("Lỗi", "File cấu hình không hợp lệ!")
            return None

        return imported_config
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể import cấu hình:\n{e}")
        return None


def import_and_apply_config():
    """
    Import cấu hình từ file JSON, kiểm tra hợp lệ rồi ghi đè config.json.
    Dùng cho nút "Import Cấu Hình" ở trang Cấu hình.

    Returns:
        bool: True nếu đã áp dụng thành công
    """
    imported = import_config()
    if imported is None:
        return False

    validated, warnings = validate_config(imported)
    if validated is None:
        messagebox.showerror("Lỗi", "File cấu hình không hợp lệ!")
        return False

    # Cập nhật trực tiếp dict dùng chung để mọi module thấy cấu hình mới
    config_data.clear()
    config_data.update(validated)

    if not save_config(config_data):
        return False

    message = "Đã import và lưu cấu hình thành công!"
    if warnings:
        message += "\n\nLưu ý:\n- " + "\n- ".join(warnings)
    message += "\n\nVui lòng khởi động lại tool để áp dụng đầy đủ."

    messagebox.showinfo("Thành công", message)
    return True


# Load cấu hình ban đầu
config_data = load_config()

