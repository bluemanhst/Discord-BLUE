# utils/paths.py
# Xác định đường dẫn chuẩn cho cả 2 chế độ: chạy source và chạy EXE (PyInstaller)
# Author: bluemanhst

import os
import sys


def is_frozen():
    """True nếu app đang chạy trong file EXE đã build bằng PyInstaller"""
    return bool(getattr(sys, "frozen", False))


# Thư mục gốc project (chỉ có ý nghĩa khi chạy source)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Thư mục làm việc: cạnh file EXE (khi build) hoặc gốc project (khi chạy source)
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable)) if is_frozen() else PROJECT_DIR


def _build_resource_roots():
    """
    Các thư mục có thể chứa dữ liệu bundle (assets/, languages/), theo thứ tự dò:
    - onefile : dữ liệu giải nén vào sys._MEIPASS
    - onedir  : dữ liệu nằm trong <cạnh exe>/_internal
    - source  : gốc project
    """
    roots = []
    if is_frozen():
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            roots.append(meipass)
            roots.append(os.path.join(meipass, "_internal"))
        roots.append(os.path.join(BASE_DIR, "_internal"))
        roots.append(BASE_DIR)
    else:
        roots.append(PROJECT_DIR)
    return roots


RESOURCE_ROOTS = _build_resource_roots()


def resource_path(*parts):
    """
    Đường dẫn tuyệt đối tới file/thư mục dữ liệu đi kèm app (assets, languages...).
    Tự dò lần lượt: _MEIPASS -> _MEIPASS/_internal -> cạnh EXE -> gốc project.

    Args:
        *parts: Các thành phần đường dẫn, ví dụ resource_path("assets", "logo.ico")

    Returns:
        str: Đường dẫn tuyệt đối (trả về ứng viên đầu tiên nếu file không tồn tại)
    """
    relative = os.path.join(*parts)
    for root in RESOURCE_ROOTS:
        candidate = os.path.join(root, relative)
        if os.path.exists(candidate):
            return candidate
    return os.path.join(RESOURCE_ROOTS[0], relative)


def user_path(*parts):
    """
    Đường dẫn file do người dùng tạo (config.json, log...).
    Luôn nằm cạnh file EXE khi build, hoặc ở gốc project khi chạy source.
    """
    return os.path.join(BASE_DIR, *parts)
