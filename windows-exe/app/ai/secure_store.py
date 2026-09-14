from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


class SecureCredentialStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def available(self) -> bool:
        return os.name == "nt"

    def save(self, secret: str) -> None:
        if not secret:
            self.clear()
            return
        if not self.available:
            raise RuntimeError("当前系统不支持 Windows DPAPI。")
        encrypted = self._protect(secret.encode("utf-8"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_bytes(encrypted)
        temp.replace(self.path)

    def load(self) -> str | None:
        if not self.available or not self.path.exists():
            return None
        try:
            return self._unprotect(self.path.read_bytes()).decode("utf-8")
        except (OSError, ValueError):
            return None

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            return

    @staticmethod
    def _protect(data: bytes) -> bytes:
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        crypt32.CryptProtectData.argtypes = [
            ctypes.POINTER(_DataBlob),
            wintypes.LPCWSTR,
            ctypes.POINTER(_DataBlob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DataBlob),
        ]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
        kernel32.LocalFree.restype = wintypes.HLOCAL
        in_buffer = ctypes.create_string_buffer(data)
        in_blob = _DataBlob(
            len(data),
            ctypes.cast(in_buffer, ctypes.POINTER(ctypes.c_byte)),
        )
        out_blob = _DataBlob()
        result = crypt32.CryptProtectData(
            ctypes.byref(in_blob),
            "PythonLearner AI Key",
            None,
            None,
            None,
            0x01,
            ctypes.byref(out_blob),
        )
        if not result:
            raise ValueError("DPAPI 加密失败。")
        try:
            return ctypes.string_at(out_blob.pbData, out_blob.cbData)
        finally:
            kernel32.LocalFree(out_blob.pbData)

    @staticmethod
    def _unprotect(data: bytes) -> bytes:
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(_DataBlob),
            ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(_DataBlob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DataBlob),
        ]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
        kernel32.LocalFree.restype = wintypes.HLOCAL
        in_buffer = ctypes.create_string_buffer(data)
        in_blob = _DataBlob(
            len(data),
            ctypes.cast(in_buffer, ctypes.POINTER(ctypes.c_byte)),
        )
        out_blob = _DataBlob()
        result = crypt32.CryptUnprotectData(
            ctypes.byref(in_blob),
            None,
            None,
            None,
            None,
            0x01,
            ctypes.byref(out_blob),
        )
        if not result:
            raise ValueError("DPAPI 解密失败。")
        try:
            return ctypes.string_at(out_blob.pbData, out_blob.cbData)
        finally:
            kernel32.LocalFree(out_blob.pbData)
