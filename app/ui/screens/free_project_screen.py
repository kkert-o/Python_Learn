from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from app.config import AppPaths
from app.data.repositories import WorkspaceRepository
from app.ui.components import ModernComboBox
from app.workspace import ProjectManager


class FreeProjectScreen(QWidget):
    open_workbench_requested = Signal(str)

    def __init__(
        self,
        paths: AppPaths,
        workspace_repository: WorkspaceRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.paths = paths
        self.workspace_repository = workspace_repository
        self.project_manager = ProjectManager()

        title = QLabel("自由项目")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "用于练习、作业和自己的 Python 想法：创建独立文件夹项目，"
            "不锁格式，可随时回到工作台继续编辑。"
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        create_card = self._create_card()
        recent_card = self._recent_card()
        top = QHBoxLayout()
        top.setSpacing(14)
        top.addWidget(create_card, 2)
        top.addWidget(recent_card, 3)

        history_card = self._history_card()
        history_card.setMinimumHeight(150)

        create_card.setMinimumHeight(360)
        recent_card.setMinimumHeight(360)
        history_card.setMinimumHeight(230)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 26, 32, 30)
        layout.setSpacing(14)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top, 5)
        layout.addWidget(history_card, 2)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)
        self.refresh()

    def _create_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsPanel")
        card.setMinimumWidth(350)
        card.setMaximumWidth(440)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel("新建自由项目")
        title.setObjectName("sectionTitle")
        description = QLabel("创建后会加入最近项目，并直接在工作台中打开。")
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(description)

        name_label = QLabel("项目名称")
        name_label.setObjectName("fieldLabel")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：天气数据分析")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        parent_label = QLabel("保存位置")
        parent_label.setObjectName("fieldLabel")
        self.parent_input = QLineEdit(str(self.paths.projects_dir))
        browse_button = QPushButton()
        browse_button.setObjectName("iconButton")
        browse_button.setToolTip("选择保存位置")
        browse_button.setIcon(qta.icon("fa5s.folder-open", color="#64748B"))
        browse_button.setIconSize(QSize(17, 17))
        browse_button.setFixedWidth(44)
        browse_button.clicked.connect(self._browse_parent)
        location_row = QHBoxLayout()
        location_row.setSpacing(8)
        location_row.addWidget(self.parent_input, 1)
        location_row.addWidget(browse_button)
        layout.addWidget(parent_label)
        layout.addLayout(location_row)

        template_label = QLabel("项目模板")
        template_label.setObjectName("fieldLabel")
        self.template_combo = ModernComboBox()
        self.template_combo.addItem("空白 Python 项目", "blank")
        self.template_combo.addItem("基础 Python 项目", "basic")
        self.template_combo.addItem("带测试项目结构", "quality")
        layout.addWidget(template_label)
        layout.addWidget(self.template_combo)

        create_button = QPushButton("创建项目")
        create_button.setObjectName("primaryButton")
        create_button.setIcon(qta.icon("fa5s.folder-plus", color="#FFFFFF"))
        create_button.setIconSize(QSize(17, 17))
        create_button.clicked.connect(self._create_project)
        layout.addSpacing(4)
        layout.addWidget(create_button)
        layout.addStretch(1)
        return card

    def _recent_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel("最近项目")
        title.setObjectName("sectionTitle")
        description = QLabel("双击项目，或选中后在工作台打开。")
        description.setObjectName("mutedText")
        layout.addWidget(title)
        layout.addWidget(description)

        self.recent = QListWidget()
        self.recent.setObjectName("projectList")
        self.recent.itemDoubleClicked.connect(self._open_recent)
        layout.addWidget(self.recent, 1)

        open_button = QPushButton("在工作台打开")
        open_button.setObjectName("secondaryButton")
        open_button.setIcon(qta.icon("fa5s.external-link-alt", color="#2563EB"))
        open_button.setIconSize(QSize(16, 16))
        open_button.clicked.connect(self._open_selected_recent)
        refresh_button = QPushButton("刷新")
        refresh_button.setObjectName("secondaryButton")
        refresh_button.setIcon(qta.icon("fa5s.sync-alt", color="#64748B"))
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.clicked.connect(self.refresh)
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(open_button)
        actions.addWidget(refresh_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        return card

    def _history_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("settingsPanel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel("最近运行")
        title.setObjectName("sectionTitle")
        description = QLabel("记录脚本是否运行成功、耗时和所属项目。")
        description.setObjectName("mutedText")
        layout.addWidget(title)
        layout.addWidget(description)

        self.history = QListWidget()
        self.history.setObjectName("projectList")
        self.history.itemDoubleClicked.connect(self._open_history)
        layout.addWidget(self.history, 1)

        open_button = QPushButton("打开对应项目")
        open_button.setObjectName("secondaryButton")
        open_button.setIcon(qta.icon("fa5s.folder-open", color="#2563EB"))
        open_button.setIconSize(QSize(16, 16))
        open_button.clicked.connect(self._open_selected_history)
        layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignLeft)
        return card

    def refresh(self) -> None:
        self.recent.clear()
        for project in self.workspace_repository.list_projects(limit=20):
            item = QListWidgetItem(
                f"{project.name}\n{Path(project.root_path)}"
            )
            item.setData(Qt.ItemDataRole.UserRole, project.root_path)
            item.setSizeHint(QSize(0, 48))
            self.recent.addItem(item)
        if self.recent.count() == 0:
            self.recent.addItem("还没有项目，先在左侧创建一个。")

        self.history.clear()
        for run in self.workspace_repository.list_run_history(limit=20):
            status = "成功" if run.success else "失败"
            item = QListWidgetItem(
                f"{Path(run.script_path).name} · {status} · {run.duration_ms} ms\n"
                f"{Path(run.script_path).parent}"
            )
            item.setData(Qt.ItemDataRole.UserRole, run.script_path)
            item.setSizeHint(QSize(0, 48))
            self.history.addItem(item)
        if self.history.count() == 0:
            self.history.addItem("还没有运行记录。")

    def _browse_parent(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "选择项目保存位置",
            self.parent_input.text() or str(self.paths.projects_dir),
        )
        if path:
            self.parent_input.setText(path)

    def _create_project(self) -> None:
        name = self.name_input.text().strip()
        parent = self.parent_input.text().strip()
        if not name or not parent:
            QMessageBox.warning(self, "无法创建", "请填写项目名称和保存位置。")
            return
        try:
            root = self.project_manager.create_project(
                parent,
                name,
                template=str(self.template_combo.currentData()),
            )
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法创建", str(exc))
            return
        self.name_input.clear()
        self.workspace_repository.upsert_project(root)
        self.refresh()
        self.open_workbench_requested.emit(str(root))

    def _open_recent(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.open_workbench_requested.emit(str(path))

    def _open_selected_recent(self) -> None:
        item = self.recent.currentItem()
        if item is not None:
            self._open_recent(item)

    def _open_history(self, item: QListWidgetItem) -> None:
        script = item.data(Qt.ItemDataRole.UserRole)
        if script:
            self.open_workbench_requested.emit(str(Path(script).parent))

    def _open_selected_history(self) -> None:
        item = self.history.currentItem()
        if item is not None:
            self._open_history(item)
