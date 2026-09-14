from __future__ import annotations

from pathlib import Path
import qtawesome as qta

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.workspace.file_manager import FileManager


class FileTreePanel(QWidget):
    file_activated = Signal(str)
    open_project_requested = Signal()
    new_project_requested = Signal()
    status_message = Signal(str)

    IGNORED_DIRECTORIES = {
        ".git",
        ".idea",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.project_root: Path | None = None
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.itemExpanded.connect(self._load_children)
        self.tree.itemActivated.connect(self._activate_item)
        self.tree.itemDoubleClicked.connect(self._activate_item)

        open_button = QPushButton("打开")
        new_button = QPushButton("新建")
        refresh_button = QPushButton("刷新")
        for button in (open_button, new_button, refresh_button):
            button.setObjectName("fileTreeAction")
        open_button.setIcon(qta.icon("fa5s.folder-open", color="#64748B"))
        new_button.setIcon(qta.icon("fa5s.folder-plus", color="#64748B"))
        refresh_button.setIcon(qta.icon("fa5s.sync-alt", color="#64748B"))
        open_button.clicked.connect(self.open_project_requested.emit)
        new_button.clicked.connect(self.new_project_requested.emit)
        refresh_button.clicked.connect(self.refresh)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.tree, 1)
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(open_button)
        actions.addWidget(new_button)
        actions.addWidget(refresh_button)
        layout.addLayout(actions)

    def set_project_root(self, root: str | Path) -> None:
        self.project_root = Path(root).resolve()
        self.refresh()

    def refresh(self) -> None:
        self.tree.clear()
        if self.project_root is None or not self.project_root.exists():
            return
        root_item = self._make_item(self.project_root, is_directory=True)
        self.tree.addTopLevelItem(root_item)
        root_item.setExpanded(True)

    def _make_item(self, path: Path, *, is_directory: bool) -> QTreeWidgetItem:
        item = QTreeWidgetItem([path.name or str(path)])
        item.setData(0, Qt.ItemDataRole.UserRole, str(path))
        item.setData(0, Qt.ItemDataRole.UserRole + 1, is_directory)
        if is_directory:
            placeholder = QTreeWidgetItem(["正在读取..."])
            placeholder.setData(0, Qt.ItemDataRole.UserRole, "")
            item.addChild(placeholder)
        return item

    def _load_children(self, item: QTreeWidgetItem) -> None:
        if item.data(0, Qt.ItemDataRole.UserRole + 1) is not True:
            return
        if item.childCount() != 1 or item.child(0).data(0, Qt.ItemDataRole.UserRole):
            return
        item.takeChildren()
        path = Path(str(item.data(0, Qt.ItemDataRole.UserRole)))
        try:
            children = sorted(
                path.iterdir(),
                key=lambda child: (not child.is_dir(), child.name.casefold()),
            )
        except OSError as exc:
            self.status_message.emit(f"无法读取目录：{exc}")
            return
        for child in children:
            if child.name.startswith(".") and child.name not in {".gitignore"}:
                continue
            if child.is_dir() and child.name in self.IGNORED_DIRECTORIES:
                continue
            if child.is_file() or child.is_dir():
                item.addChild(self._make_item(child, is_directory=child.is_dir()))

    def _activate_item(self, item: QTreeWidgetItem, _column: int = 0) -> None:
        path_text = str(item.data(0, Qt.ItemDataRole.UserRole))
        if not path_text:
            return
        path = Path(path_text)
        if path.is_file():
            self.file_activated.emit(str(path))
        elif path.is_dir():
            item.setExpanded(not item.isExpanded())

    def _show_context_menu(self, point) -> None:  # type: ignore[no-untyped-def]
        item = self.tree.itemAt(point)
        if item is None:
            return
        path_text = str(item.data(0, Qt.ItemDataRole.UserRole))
        if not path_text:
            return
        path = Path(path_text)
        menu = QMenu(self)
        if path.is_dir():
            menu.addAction("新建文件", lambda: self._create_file(path))
            menu.addAction("新建文件夹", lambda: self._create_directory(path))
        menu.addAction("重命名", lambda: self._rename(path))
        menu.addAction("删除", lambda: self._delete(path))
        menu.addSeparator()
        menu.addAction("刷新", self.refresh)
        menu.exec(self.tree.viewport().mapToGlobal(point))

    def _create_file(self, directory: Path) -> None:
        name, accepted = QInputDialog.getText(self, "新建文件", "文件名：")
        if not accepted or not name.strip():
            return
        try:
            path = FileManager.create_file(directory / name.strip())
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法新建文件", str(exc))
            return
        self.refresh()
        self.file_activated.emit(str(path))

    def _create_directory(self, directory: Path) -> None:
        name, accepted = QInputDialog.getText(self, "新建文件夹", "文件夹名称：")
        if not accepted or not name.strip():
            return
        target = directory / name.strip()
        try:
            FileManager.create_directory(target)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法新建文件夹", str(exc))
            return
        self.refresh()

    def _rename(self, path: Path) -> None:
        name, accepted = QInputDialog.getText(
            self,
            "重命名",
            "新名称：",
            text=path.name,
        )
        if not accepted or not name.strip() or name == path.name:
            return
        try:
            FileManager.rename(path, name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法重命名", str(exc))
            return
        self.refresh()

    def _delete(self, path: Path) -> None:
        result = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除“{path.name}”吗？此操作无法撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        try:
            FileManager.delete(path)
        except OSError as exc:
            QMessageBox.warning(self, "无法删除", str(exc))
            return
        self.refresh()
