from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TextFileData:
    path: Path
    text: str
    encoding: str


class FileManager:
    @staticmethod
    def read_text(path: str | Path) -> TextFileData:
        file_path = Path(path)
        for encoding in ("utf-8-sig", "utf-8", "gb18030"):
            try:
                text = file_path.read_text(encoding=encoding)
                return TextFileData(file_path, text, encoding)
            except UnicodeDecodeError:
                continue
        raise UnicodeError(f"无法识别文件编码：{file_path}")

    @staticmethod
    def write_text(
        path: str | Path,
        text: str,
        encoding: str = "utf-8",
    ) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = file_path.with_name(f".{file_path.name}.tmp")
        with temp_path.open("w", encoding=encoding, newline="\n") as handle:
            handle.write(text)
            handle.flush()
        temp_path.replace(file_path)
        return file_path

    @staticmethod
    def create_file(path: str | Path, text: str = "") -> Path:
        file_path = Path(path)
        if file_path.exists():
            raise FileExistsError(f"文件已存在：{file_path}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8", newline="\n")
        return file_path

    @staticmethod
    def create_directory(path: str | Path) -> Path:
        directory = Path(path)
        directory.mkdir(parents=True, exist_ok=False)
        return directory

    @staticmethod
    def rename(path: str | Path, new_name: str) -> Path:
        source = Path(path)
        if not source.exists():
            raise FileNotFoundError(f"路径不存在：{source}")
        clean_name = new_name.strip()
        if not clean_name or any(separator in clean_name for separator in ("/", "\\")):
            raise ValueError("新名称不能为空，也不能包含路径分隔符")
        target = source.with_name(clean_name)
        if target.exists():
            raise FileExistsError(f"目标已存在：{target}")
        source.rename(target)
        return target

    @staticmethod
    def delete(path: str | Path) -> None:
        target = Path(path)
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        else:
            raise FileNotFoundError(f"路径不存在：{target}")

