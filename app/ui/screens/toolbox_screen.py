from __future__ import annotations

import importlib.util

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.data.models import CourseContent
from app.projects import ProjectCatalog
from app.services.settings import SettingsService
from app.ui.components import ModernComboBox
from app.toolbox import (
    EngineeringCatalog,
    ErrorMuseumCatalog,
    GlobalSearchEngine,
    LibraryCatalog,
    LibraryCategory,
    SearchResultKind,
)
from app.training import TrainingCatalog
from app.ui.components.common import clear_layout


class ToolboxScreen(QWidget):
    lesson_requested = Signal(str)
    project_requested = Signal(str)
    training_requested = Signal(str)
    workbench_requested = Signal(str, str)

    def __init__(
        self,
        content: CourseContent,
        training_catalog: TrainingCatalog,
        project_catalog: ProjectCatalog,
        settings: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.content = content
        self.training_catalog = training_catalog
        self.project_catalog = project_catalog
        self.settings = settings
        self.library_query = QLineEdit()
        self.library_category = ModernComboBox()
        self.library_category.setMinimumWidth(160)
        self.library_results = QWidget()
        self.library_layout = QVBoxLayout(self.library_results)
        self.error_query = QLineEdit()
        self.error_results = QWidget()
        self.error_layout = QVBoxLayout(self.error_results)
        self.global_query = QLineEdit()
        self.global_results = QWidget()
        self.global_layout = QVBoxLayout(self.global_results)
        self.expanded_library_ids: set[str] = set()
        self.tabs = QTabWidget()
        self.tabs.addTab(self._library_tab(), "第三方库")
        self.tabs.addTab(self._error_tab(), "错误博物馆")
        self.tabs.addTab(self._engineering_tab(), "工程实践")
        self.tabs.addTab(self._search_tab(), "搜索与收藏")

        title = QLabel("资料库")
        title.setObjectName("pageTitle")
        subtitle = QLabel("查库、查错、查工程方法，也可以搜索全部学习内容。")
        subtitle.setObjectName("pageSubtitle")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 28)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.tabs, 1)
        self.refresh()

    @staticmethod
    def _scroll(container: QWidget, layout: QVBoxLayout) -> QScrollArea:
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(container)
        return scroll

    def _library_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        filters = QHBoxLayout()
        self.library_query.setPlaceholderText("搜索库名称、用途或分类")
        self.library_query.textChanged.connect(self._refresh_libraries)
        self.library_category.addItem("全部分类", None)
        for category in LibraryCategory:
            self.library_category.addItem(category.value, category)
        self.library_category.currentIndexChanged.connect(self._refresh_libraries)
        filters.addWidget(self.library_query, 1)
        filters.addWidget(self.library_category)
        layout.addLayout(filters)
        self.library_count = QLabel()
        self.library_count.setObjectName("mutedText")
        layout.addWidget(self.library_count)
        self.library_layout.setContentsMargins(0, 0, 0, 0)
        self.library_layout.setSpacing(10)
        layout.addWidget(self._scroll(self.library_results, self.library_layout), 1)
        return page

    def _error_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.error_query.setPlaceholderText("搜索 NameError、字典、文件等")
        self.error_query.textChanged.connect(self._refresh_errors)
        layout.addWidget(self.error_query)
        self.error_layout.setContentsMargins(0, 0, 0, 0)
        self.error_layout.setSpacing(10)
        layout.addWidget(self._scroll(self.error_results, self.error_layout), 1)
        return page

    def _engineering_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        for module in EngineeringCatalog.all:
            card = QFrame()
            card.setObjectName("stageCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 15, 18, 16)
            title = QLabel(module.title)
            title.setObjectName("projectTitle")
            category = QLabel(module.category.value)
            category.setObjectName("tagLabel")
            summary = QLabel(module.summary)
            summary.setObjectName("mutedText")
            summary.setWordWrap(True)
            checklist = QLabel(
                "检查清单：\n"
                + "\n".join(f"• {item}" for item in module.checklist)
            )
            checklist.setWordWrap(True)
            commands = self._code_view("\n".join(module.commands))
            commands.setMaximumHeight(110)
            card_layout.addWidget(category)
            card_layout.addWidget(title)
            card_layout.addWidget(summary)
            card_layout.addWidget(checklist)
            card_layout.addWidget(commands)
            container_layout.addWidget(card)
        container_layout.addStretch(1)
        layout.addWidget(self._scroll(container, container_layout), 1)
        return page

    def _search_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.global_query.setPlaceholderText("搜索课程、项目、训练、第三方库、错误和工程实践")
        self.global_query.textChanged.connect(self._refresh_global_search)
        layout.addWidget(self.global_query)
        self.global_layout.setContentsMargins(0, 0, 0, 0)
        self.global_layout.setSpacing(8)
        layout.addWidget(self._scroll(self.global_results, self.global_layout), 1)
        return page

    def refresh(self) -> None:
        self._refresh_libraries()
        self._refresh_errors()
        self._refresh_global_search()

    def _refresh_libraries(self) -> None:
        clear_layout(self.library_layout)
        category = self.library_category.currentData()
        entries = LibraryCatalog.search(self.library_query.text(), category)
        self.library_count.setText(f"{len(entries)} 个第三方库")
        for entry in entries:
            card = QFrame()
            card.setObjectName("libraryCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 13, 16, 14)
            top = QHBoxLayout()
            header = QToolButton()
            header.setObjectName("libraryHeader")
            header.setCheckable(True)
            header.setChecked(entry.library_id in self.expanded_library_ids)
            header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            header.setText(f"{entry.name}  ·  {entry.category.value}")
            header.setArrowType(
                Qt.ArrowType.DownArrow
                if header.isChecked()
                else Qt.ArrowType.RightArrow
            )
            available = self._module_available(entry.import_name)
            status = QLabel("当前环境可导入" if available else "需要安装")
            status.setObjectName("quizCorrect" if available else "mutedText")
            top.addWidget(header)
            top.addStretch(1)
            top.addWidget(status)
            summary = QLabel(entry.summary)
            summary.setWordWrap(True)
            card_layout.addLayout(top)
            card_layout.addWidget(summary)
            details = QWidget()
            details_layout = QVBoxLayout(details)
            details_layout.setContentsMargins(0, 4, 0, 0)
            details_layout.setSpacing(8)
            use_case = QLabel(f"适用场景：{entry.use_case}")
            use_case.setObjectName("mutedText")
            use_case.setWordWrap(True)
            details_layout.addWidget(use_case)
            install_label = QLabel(f"安装命令：{entry.install}")
            install_label.setObjectName("codeNote")
            install_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            details_layout.addWidget(install_label)
            example_label = QLabel("示例代码")
            example_label.setObjectName("sectionTitle")
            details_layout.addWidget(example_label)
            example = self._code_view(entry.example)
            example.setMaximumHeight(150)
            details_layout.addWidget(example)
            details.setVisible(header.isChecked())
            card_layout.addWidget(details)
            actions = QHBoxLayout()
            if entry.lesson_id:
                lesson = QPushButton("查看关联知识点")
                lesson.clicked.connect(
                    lambda _checked=False, lesson_id=entry.lesson_id: self.lesson_requested.emit(
                        lesson_id
                    )
                )
                actions.addWidget(lesson)
            send = QPushButton("发送示例到工作台")
            send.clicked.connect(
                lambda _checked=False, item=entry: self.workbench_requested.emit(
                    item.name,
                    item.example,
                )
            )
            actions.addStretch(1)
            actions.addWidget(send)
            card_layout.addLayout(actions)

            def toggle_details(
                checked: bool,
                button=header,
                detail_widget=details,
                library_id=entry.library_id,
            ) -> None:
                detail_widget.setVisible(checked)
                button.setArrowType(
                    Qt.ArrowType.DownArrow
                    if checked
                    else Qt.ArrowType.RightArrow
                )
                if checked:
                    self.expanded_library_ids.add(library_id)
                else:
                    self.expanded_library_ids.discard(library_id)

            header.toggled.connect(toggle_details)
            self.library_layout.addWidget(card)
        self.library_layout.addStretch(1)

    def _refresh_errors(self) -> None:
        clear_layout(self.error_layout)
        entries = ErrorMuseumCatalog.search(self.error_query.text())
        for entry in entries:
            card = QFrame()
            card.setObjectName("stageCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 13, 16, 14)
            header = QHBoxLayout()
            title = QLabel(entry.title)
            title.setObjectName("projectTitle")
            error_type = QLabel(entry.error_type)
            error_type.setObjectName("errorTitle")
            header.addWidget(title)
            header.addWidget(error_type)
            header.addStretch(1)
            card_layout.addLayout(header)
            symptom = QLabel(entry.symptom)
            symptom.setWordWrap(True)
            card_layout.addWidget(symptom)
            cause = QLabel(f"原因：{entry.cause}")
            cause.setObjectName("mutedText")
            cause.setWordWrap(True)
            card_layout.addWidget(cause)
            broken = self._code_view(entry.broken_code)
            fixed = self._code_view(entry.fixed_code)
            broken.setMaximumHeight(100)
            fixed.setMaximumHeight(120)
            card_layout.addWidget(QLabel("错误代码"))
            card_layout.addWidget(broken)
            card_layout.addWidget(QLabel("修复代码"))
            card_layout.addWidget(fixed)
            prevention = QLabel(f"避免方法：{entry.prevention}")
            prevention.setObjectName("mutedText")
            prevention.setWordWrap(True)
            card_layout.addWidget(prevention)
            actions = QHBoxLayout()
            send = QPushButton("运行修复代码")
            send.clicked.connect(
                lambda _checked=False, item=entry: self.workbench_requested.emit(
                    item.title,
                    item.fixed_code,
                )
            )
            actions.addWidget(send)
            if entry.lesson_id:
                lesson = QPushButton("学习对应知识点")
                lesson.clicked.connect(
                    lambda _checked=False, lesson_id=entry.lesson_id: self.lesson_requested.emit(
                        lesson_id
                    )
                )
                actions.addWidget(lesson)
            actions.addStretch(1)
            card_layout.addLayout(actions)
            self.error_layout.addWidget(card)
        self.error_layout.addStretch(1)

    def _refresh_global_search(self) -> None:
        clear_layout(self.global_layout)
        query = self.global_query.text().strip()
        if query:
            results = GlobalSearchEngine.search(
                query,
                self.content,
                self.training_catalog,
                self.project_catalog,
            )
            heading = QLabel(f"全局结果 · {len(results)} 项")
        else:
            favorites = list(self.settings.get("favorites", []))
            results = [
                resolved
                for key in favorites
                if (
                    resolved := GlobalSearchEngine.resolve(
                        str(key),
                        self.content,
                        self.training_catalog,
                        self.project_catalog,
                    )
                )
                is not None
            ]
            heading = QLabel(f"收藏 · {len(results)} 项")
        heading.setObjectName("sectionTitle")
        self.global_layout.addWidget(heading)
        if not results:
            message = (
                "没有找到匹配内容。"
                if query
                else "还没有收藏。搜索后点击“收藏”即可集中到这里。"
            )
            empty = QLabel(message)
            empty.setObjectName("mutedText")
            self.global_layout.addWidget(empty)
        for result in results:
            self.global_layout.addWidget(self._search_row(result))
        self.global_layout.addStretch(1)

    def _search_row(self, result) -> QFrame:  # type: ignore[no-untyped-def]
        card = QFrame()
        card.setObjectName("progressRow")
        layout = QHBoxLayout(card)
        text = QVBoxLayout()
        title = QLabel(result.title)
        title.setObjectName("progressRowTitle")
        subtitle = QLabel(f"{result.kind.value} · {result.subtitle}")
        subtitle.setObjectName("mutedText")
        text.addWidget(title)
        text.addWidget(subtitle)
        favorite = QPushButton(
            "已收藏" if self._is_favorite(result.favorite_key) else "收藏"
        )
        favorite.clicked.connect(
            lambda _checked=False, key=result.favorite_key: self._toggle_favorite(key)
        )
        open_button = QPushButton("打开")
        open_button.clicked.connect(
            lambda _checked=False, value=result: self._open_result(value)
        )
        layout.addLayout(text, 1)
        layout.addWidget(favorite)
        layout.addWidget(open_button)
        return card

    def _open_result(self, result) -> None:  # type: ignore[no-untyped-def]
        if result.kind is SearchResultKind.LESSON:
            self.lesson_requested.emit(result.route_id)
        elif result.kind is SearchResultKind.PROJECT:
            self.project_requested.emit(result.route_id)
        elif result.kind is SearchResultKind.TRAINING:
            self.training_requested.emit(result.route_id)
        elif result.kind is SearchResultKind.LIBRARY:
            entry = LibraryCatalog.by_id(result.route_id)
            if entry is not None:
                self.library_query.setText(entry.name)
                self.tabs.setCurrentIndex(0)
        elif result.kind is SearchResultKind.ERROR:
            entry = ErrorMuseumCatalog.by_id(result.route_id)
            if entry is not None:
                self.error_query.setText(entry.error_type)
                self.tabs.setCurrentIndex(1)
        elif result.kind is SearchResultKind.ENGINEERING:
            self.tabs.setCurrentIndex(2)

    def _toggle_favorite(self, key: str) -> None:
        favorites = set(self.settings.get("favorites", []))
        if key in favorites:
            favorites.remove(key)
        else:
            favorites.add(key)
        self.settings.set("favorites", sorted(favorites))
        self._refresh_global_search()

    def _is_favorite(self, key: str) -> bool:
        return key in set(self.settings.get("favorites", []))

    @staticmethod
    def _module_available(import_name: str) -> bool:
        try:
            return importlib.util.find_spec(import_name) is not None
        except (ImportError, ValueError):
            return False

    @staticmethod
    def _code_view(code: str) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setPlainText(code)
        view.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        return view
