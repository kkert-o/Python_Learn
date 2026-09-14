from __future__ import annotations

import ctypes
import os
import sys
from ctypes import wintypes
from pathlib import Path

from PySide6.QtWidgets import QWidget


def set_windows_app_user_model_id(app_id: str) -> bool:
    if os.name != "nt":
        return False
    try:
        shell32 = ctypes.windll.shell32
        shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = [
            wintypes.LPCWSTR
        ]
        shell32.SetCurrentProcessExplicitAppUserModelID.restype = ctypes.c_long
        result = shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        return result == 0
    except (AttributeError, OSError, ValueError):
        return False


def set_windows_window_icon(
    widget: QWidget,
    icon_path: str | Path,
) -> int | None:
    if os.name != "nt" or not Path(icon_path).is_file():
        return None
    try:
        user32 = ctypes.windll.user32
        user32.LoadImageW.argtypes = [
            wintypes.HINSTANCE,
            wintypes.LPCWSTR,
            wintypes.UINT,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        user32.LoadImageW.restype = wintypes.HANDLE
        user32.SendMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        user32.SendMessageW.restype = ctypes.c_ssize_t
        user32.SetClassLongPtrW.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_ssize_t,
        ]
        user32.SetClassLongPtrW.restype = ctypes.c_ssize_t
        user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.UINT,
        ]
        user32.SetWindowPos.restype = wintypes.BOOL
        icon_handle = user32.LoadImageW(
            None,
            str(icon_path),
            1,
            0,
            0,
            0x00000010,
        )
        if not icon_handle:
            return None
        hwnd = wintypes.HWND(int(widget.winId()))
        user32.SendMessageW(hwnd, 0x0080, 0, icon_handle)
        user32.SendMessageW(hwnd, 0x0080, 1, icon_handle)
        user32.SendMessageW(hwnd, 0x0080, 2, icon_handle)
        user32.SetClassLongPtrW(hwnd, -14, icon_handle)
        user32.SetClassLongPtrW(hwnd, -34, icon_handle)
        user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0027)
        return int(icon_handle)
    except (AttributeError, OSError, TypeError, ValueError):
        return None


def destroy_windows_icon(icon_handle: int | None) -> None:
    if os.name != "nt" or not icon_handle:
        return
    try:
        ctypes.windll.user32.DestroyIcon(wintypes.HICON(icon_handle))
    except (AttributeError, OSError, TypeError, ValueError):
        return


def apply_windows_backdrop(
    widget: QWidget,
    *,
    dark: bool,
    enabled: bool,
) -> bool:
    if os.name != "nt" or not sys.getwindowsversion().major >= 10:
        return False
    try:
        hwnd = int(widget.winId())
        dwm = ctypes.windll.dwmapi
        dark_value = ctypes.c_int(1 if dark else 0)
        dwm.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(20),
            ctypes.byref(dark_value),
            ctypes.sizeof(dark_value),
        )
        backdrop_value = ctypes.c_int(3 if enabled else 1)
        result = dwm.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            wintypes.DWORD(38),
            ctypes.byref(backdrop_value),
            ctypes.sizeof(backdrop_value),
        )
        return int(result) == 0
    except (AttributeError, OSError, ValueError):
        return False
