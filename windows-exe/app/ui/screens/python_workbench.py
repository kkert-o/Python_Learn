from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from app.config import AppPaths
from app.data.models import CourseContent
from app.data.repositories import WorkspaceRepository
from app.runtime import (
    PythonErrorExplainer,
    PythonRunner,
    RunResult,
    RunState,
)
from app.services.settings import SettingsService
from app.ui.components import CodeEditor, OutputPanel, TerminalPanel
from app.ui.components.file_tree import FileTreePanel
from app.workspace import FileManager, ProjectManager


class PythonWorkbench(QWidget):
    status_message = Signal(str)

    def __init__(
        self,
        paths: AppPaths,
        content: CourseContent,
        workspace_repository: WorkspaceRepository,
        settings: SettingsService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.paths = paths
        self.content = content
        self.workspace_repository = workspace_repository
        self.settings = settings
        self._dark = False
        self._accent = "#2563EB"
        self._font_size = (
            int(settings.get("workbench_font_size", 11))
            if settings is not None
            else 11
        )
        self.project_manager = ProjectManager()
        self.error_explainer = PythonErrorExplainer()
        self.runner = PythonRunner(paths, self)
        self.current_project: Path | None = None
        self._running_script: Path | None = None
        self._closing_allowed = False

        self.file_tree = FileTreePanel()
        self.file_tree.file_activated.connect(self.open_file)
        self.file_tree.open_project_requested.connect(self.choose_project)
        self.file_tree.new_project_requested.connect(self.create_project)
        self.file_tree.status_message.connect(self.status_message.emit)

        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.setMinimumHeight(260)
        self.editor_tabs.tabCloseRequested.connect(self._close_editor_tab)
        self.editor_tabs.currentChanged.connect(self._current_tab_changed)

        self.output_panel = OutputPanel()
        self.output_panel.setMinimumHeight(150)
        self.output_panel.input_submitted.connect(self.runner.submit_input)
        self.output_panel.input_finished.connect(self.runner.end_input)
        self.terminal = TerminalPanel(
            paths.projects_dir,
            packages_dir=paths.packages_dir,
        )
        self.terminal.status_message.connect(self.status_message.emit)
        self.bottom_tabs = QTabWidget()
        self.bottom_tabs.setDocumentMode(True)
        self.bottom_tabs.addTab(self.output_panel, "运行结果")
        self.bottom_tabs.addTab(self.terminal, "终端")

        self.toolbar = self._build_toolbar()
        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("workbenchStatus")

        editor_splitter = QSplitter(Qt.Orientation.Vertical)
        editor_splitter.addWidget(self.editor_tabs)
        editor_splitter.addWidget(self.bottom_tabs)
        editor_splitter.setChildrenCollapsible(False)
        editor_splitter.setStretchFactor(0, 4)
        editor_splitter.setStretchFactor(1, 2)
        editor_splitter.setSizes([540, 250])

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.file_tree)
        main_splitter.addWidget(editor_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([245, 900])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(main_splitter, 1)
        layout.addWidget(self.status_label)

        self.runner.started.connect(self._run_started)
        self.runner.stdout_ready.connect(self.output_panel.append_stdout)
        self.runner.stderr_ready.connect(self.output_panel.append_stderr)
        self.runner.input_requested.connect(self.output_panel.request_input)
        self.runner.result_ready.connect(self._run_finished)
        self.runner.failed.connect(self._run_failed)
        self.runner.truncated.connect(self._run_truncated)
        self.runner.state_changed.connect(self._run_state_changed)
        self._setup_shortcuts()

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("workbenchToolbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        self.new_action = self._action(
            "新建文件",
            "fa5s.file",
            self.new_file,
        )
        self.open_action = self._action(
            "打开文件",
            "fa5s.folder-open",
            self.choose_file,
        )
        self.save_action = self._action(
            "保存",
            "fa5s.save",
            self.save_current,
        )
        self.save_as_action = self._action(
            "另存为",
            "fa5s.file-export",
            self.save_current_as,
        )
        self.run_action = self._action(
            "运行",
            "fa5s.play",
            self.run_current,
        )
        self.stop_action = self._action(
            "停止",
            "fa5s.stop",
            self.runner.stop,
        )
        self.stop_action.setEnabled(False)

        for action in (
            self.new_action,
            self.open_action,
            self.save_action,
            self.save_as_action,
            self.run_action,
            self.stop_action,
        ):
            button = QToolButton()
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            if action is self.run_action:
                button.setObjectName("runActionButton")
            elif action is self.stop_action:
                button.setObjectName("stopActionButton")
            else:
                button.setObjectName("workbenchAction")
            layout.addWidget(button)

        font_label = QLabel("代码字号")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.font_size_spin.setValue(self._font_size)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setFixedWidth(88)
        self.font_size_spin.valueChanged.connect(self.set_font_size)
        layout.addSpacing(8)
        layout.addWidget(font_label)
        layout.addWidget(self.font_size_spin)
        layout.addStretch(1)
        interpreter = QLabel(
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        interpreter.setToolTip(sys.executable)
        layout.addWidget(interpreter)
        return bar

    def _action(
        self,
        text: str,
        icon_name: str,
        callback,
    ) -> QAction:  # type: ignore[no-untyped-def]
        action = QAction(qta.icon(icon_name), text, self)
        action.setProperty("iconName", icon_name)
        action.triggered.connect(callback)
        return action

    def _refresh_action_icons(self) -> None:
        neutral = "#CBD5E1" if self._dark else "#475569"
        for action in (
            self.new_action,
            self.open_action,
            self.save_action,
            self.save_as_action,
        ):
            action.setIcon(
                qta.icon(str(action.property("iconName")), color=neutral)
            )
        self.run_action.setIcon(
            qta.icon("fa5s.play", color=self._accent)
        )
        self.stop_action.setIcon(
            qta.icon("fa5s.stop", color="#EF4444")
        )

    def _setup_shortcuts(self) -> None:
        shortcuts = (
            (QKeySequence.StandardKey.New, self.new_file),
            (QKeySequence.StandardKey.Open, self.choose_file),
            (QKeySequence.StandardKey.Save, self.save_current),
            (QKeySequence.StandardKey.SaveAs, self.save_current_as),
            (QKeySequence("Ctrl+Return"), self.run_current),
            (QKeySequence("Ctrl+Enter"), self.run_current),
        )
        self._shortcut_objects: list[QShortcut] = []
        for sequence, callback in shortcuts:
            shortcut = QShortcut(sequence, self)
            shortcut.activated.connect(callback)
            self._shortcut_objects.append(shortcut)
        stop_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        stop_shortcut.activated.connect(self._stop_if_running)
        self._shortcut_objects.append(stop_shortcut)

    def new_file(self) -> None:
        if self.current_project is not None:
            name, accepted = QInputDialog.getText(self, "新建 Python 文件", "文件名：")
            if not accepted or not name.strip():
                return
            file_name = name.strip()
            if not Path(file_name).suffix:
                file_name += ".py"
            path = self.current_project / file_name
            try:
                FileManager.create_file(path, "")
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "无法新建文件", str(exc))
                return
            self.file_tree.refresh()
            self.open_file(path)
            return

        path_text, _ = QFileDialog.getSaveFileName(
            self,
            "新建 Python 文件",
            str(self.paths.projects_dir / "main.py"),
            "Python 文件 (*.py);;所有文件 (*)",
        )
        if not path_text:
            return
        try:
            path = FileManager.create_file(path_text, "")
        except OSError as exc:
            QMessageBox.warning(self, "无法新建文件", str(exc))
            return
        self.open_file(path)

    def ensure_ready(self) -> None:
        if self.editor_tabs.count() > 0:
            editor = self.current_editor()
            if editor is not None:
                editor.setFocus()
            return
        project_root = self.current_project or (
            self.paths.projects_dir / "scratch"
        )
        project_root.mkdir(parents=True, exist_ok=True)
        path = project_root / "main.py"
        if not path.exists():
            FileManager.write_text(
                path,
                '# 在这里输入 Python 代码，按 Ctrl+Enter 运行\n'
                'print("你好，Python！")\n',
            )
        self.current_project = project_root
        self.terminal.set_working_directory(project_root)
        self.file_tree.set_project_root(project_root)
        self.workspace_repository.upsert_project(project_root)
        self.open_file(path)

    def choose_file(self) -> None:
        path_text, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            str(self.current_project or self.paths.projects_dir),
            "Python 文件 (*.py);;文本文件 (*.txt *.json *.csv *.md);;所有文件 (*)",
        )
        if path_text:
            self.open_file(path_text)

    def open_file(self, path: str | Path) -> None:
        file_path = Path(path).resolve()
        if not file_path.exists():
            QMessageBox.warning(self, "无法打开文件", f"文件不存在：{file_path}")
            return
        existing_index = self._find_tab(file_path)
        if existing_index is not None:
            self.editor_tabs.setCurrentIndex(existing_index)
            return
        editor = CodeEditor()
        editor.set_font_size(self._font_size)
        editor.set_theme(self._dark, self._accent)
        try:
            editor.load_file(file_path)
        except (OSError, UnicodeError) as exc:
            QMessageBox.warning(self, "无法打开文件", str(exc))
            return
        editor.document().modificationChanged.connect(
            lambda _modified, target=editor: self._update_tab_title(target)
        )
        editor.editor_focused.connect(lambda _target: self.status_message.emit(str(file_path)))
        self._restore_editor_state(editor)
        index = self.editor_tabs.addTab(editor, file_path.name)
        self.editor_tabs.setTabToolTip(index, str(file_path))
        self.editor_tabs.setCurrentIndex(index)
        self.workspace_repository.record_recent_file(
            file_path,
            self.current_project,
        )
        self.status_message.emit(f"已打开 {file_path}")

    def choose_project(self) -> None:
        path_text = QFileDialog.getExistingDirectory(
            self,
            "打开 Python 项目",
            str(self.current_project or self.paths.projects_dir),
        )
        if path_text:
            self.open_project(path_text)

    def open_code_snippet(self, title: str, code: str) -> None:
        safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip() or "lesson"
        digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
        project_root = self.paths.projects_dir / "lesson_workspace"
        project_root.mkdir(parents=True, exist_ok=True)
        path = project_root / f"{safe_title[:40]}_{digest}.py"
        FileManager.write_text(path, code.rstrip() + "\n")
        self.current_project = project_root
        self.terminal.set_working_directory(project_root)
        self.file_tree.set_project_root(project_root)
        self.workspace_repository.upsert_project(project_root)
        self.open_file(path)
        self.status_message.emit(f"已从课程发送到工作台：{title}")

    def set_font_size(self, point_size: int) -> None:
        self._font_size = max(8, min(32, int(point_size)))
        if self.font_size_spin.value() != self._font_size:
            self.font_size_spin.blockSignals(True)
            self.font_size_spin.setValue(self._font_size)
            self.font_size_spin.blockSignals(False)
        for index in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(index)
            if isinstance(editor, CodeEditor):
                editor.set_font_size(self._font_size)
        if self.settings is not None:
            self.settings.set("workbench_font_size", self._font_size)

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = accent
        self._refresh_action_icons()
        for index in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(index)
            if isinstance(editor, CodeEditor):
                editor.set_theme(dark, accent)

    def open_project(self, path: str | Path) -> None:
        project_root = Path(path).resolve()
        if not project_root.is_dir():
            QMessageBox.warning(self, "无法打开项目", f"目录不存在：{project_root}")
            return
        self.current_project = project_root
        self.terminal.set_working_directory(project_root)
        self.file_tree.set_project_root(project_root)
        self.workspace_repository.upsert_project(project_root)
        entry = self.project_manager.detect_entry_file(project_root)
        if entry is not None:
            self.open_file(entry)
        self.status_message.emit(f"已打开项目 {project_root}")

    def create_project(self) -> None:
        parent_text = QFileDialog.getExistingDirectory(
            self,
            "选择项目保存位置",
            str(self.paths.projects_dir),
        )
        if not parent_text:
            return
        name, accepted = QInputDialog.getText(self, "新建项目", "项目名称：")
        if not accepted or not name.strip():
            return
        try:
            project_root = self.project_manager.create_project(parent_text, name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "无法新建项目", str(exc))
            return
        self.open_project(project_root)

    def save_current(self) -> bool:
        editor = self.current_editor()
        if editor is None:
            return False
        if editor.file_path is None:
            return self.save_current_as()
        try:
            path = editor.save()
        except OSError as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False
        self._after_save(editor, path)
        return True

    def save_current_as(self) -> bool:
        editor = self.current_editor()
        if editor is None:
            return False
        initial = (
            str(editor.file_path)
            if editor.file_path is not None
            else str(self.current_project or self.paths.projects_dir) + "/untitled.py"
        )
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Python 文件",
            initial,
            "Python 文件 (*.py);;所有文件 (*)",
        )
        if not path_text:
            return False
        try:
            path = editor.save(path_text)
        except OSError as exc:
            QMessageBox.warning(self, "保存失败", str(exc))
            return False
        self._after_save(editor, path)
        return True

    def _after_save(self, editor: CodeEditor, path: Path) -> None:
        index = self.editor_tabs.indexOf(editor)
        if index >= 0:
            self.editor_tabs.setTabText(index, path.name)
            self.editor_tabs.setTabToolTip(index, str(path))
        self.workspace_repository.record_recent_file(path, self.current_project)
        self.status_message.emit(f"已保存 {path}")

    def run_current(self) -> None:
        if self.runner.is_running:
            return
        editor = self.current_editor()
        if editor is None:
            QMessageBox.information(self, "没有可运行文件", "请先新建或打开一个 Python 文件。")
            return
        if editor.document().isModified() or editor.file_path is None:
            if not self.save_current():
                return
        path = editor.file_path
        if path is None:
            return
        if path.suffix.lower() != ".py":
            QMessageBox.warning(self, "无法运行", "当前文件不是 .py 文件。")
            return
        self.output_panel.clear_output()
        self.bottom_tabs.setCurrentIndex(0)
        self.output_panel.append_info(
            f"运行文件：{path}\n工作目录：{self.current_project or path.parent}"
        )
        try:
            self._running_script = path
            self.runner.start(
                code=editor.toPlainText(),
                script_path=path,
                working_directory=self.current_project or path.parent,
            )
        except (OSError, RuntimeError) as exc:
            self._running_script = None
            QMessageBox.warning(self, "无法运行", str(exc))

    def _stop_if_running(self) -> None:
        if self.runner.is_running:
            self.runner.stop()

    def current_editor(self) -> CodeEditor | None:
        widget = self.editor_tabs.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None

    def _find_tab(self, path: Path) -> int | None:
        for index in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(index)
            if isinstance(widget, CodeEditor):
                if widget.file_path is not None and widget.file_path.resolve() == path:
                    return index
        return None

    def _update_tab_title(self, editor: CodeEditor) -> None:
        index = self.editor_tabs.indexOf(editor)
        if index < 0:
            return
        base = editor.file_path.name if editor.file_path is not None else "未命名"
        self.editor_tabs.setTabText(index, f"{base} *" if editor.document().isModified() else base)

    def _current_tab_changed(self, _index: int) -> None:
        editor = self.current_editor()
        if editor is not None:
            editor.setFocus()

    def _close_editor_tab(self, index: int) -> None:
        editor = self.editor_tabs.widget(index)
        if not isinstance(editor, CodeEditor):
            return
        if editor.document().isModified():
            result = QMessageBox.question(
                self,
                "保存修改",
                f"“{editor.file_path.name if editor.file_path else '未命名'}”尚未保存，是否保存？",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if result == QMessageBox.StandardButton.Cancel:
                return
            if result == QMessageBox.StandardButton.Save:
                self.editor_tabs.setCurrentIndex(index)
                if not self.save_current():
                    return
        self._save_editor_state(editor)
        self.editor_tabs.removeTab(index)
        editor.deleteLater()

    def _run_started(self, run_id: str) -> None:
        self.output_panel.append_info(f"运行编号：{run_id}")
        self.status_message.emit("程序正在运行")

    def _run_finished(self, result: RunResult) -> None:
        status = "已停止" if result.cancelled else "超时" if result.timed_out else "已完成"
        self.output_panel.append_info(
            f"{status}，退出码：{result.exit_code}，运行时间：{result.duration_ms / 1000:.3f}s"
        )
        explanation = self.error_explainer.explain(result.stderr)
        if explanation is not None:
            self.output_panel.append_info(
                f"\n错误解释：{explanation.title}\n{explanation.message}\n"
                + "\n".join(f"- {item}" for item in explanation.suggestions)
            )
            if explanation.line_number is not None:
                editor = self.current_editor()
                if editor is not None:
                    editor.goto_line(explanation.line_number)
        self.workspace_repository.record_run(
            run_id=result.run_id,
            script_path=str(self._running_script or ""),
            started_at=result.started_at,
            duration_ms=result.duration_ms,
            exit_code=result.exit_code,
            success=result.exit_code == 0 and not result.cancelled and not result.timed_out,
            cancelled=result.cancelled,
            project_root=self.current_project,
        )
        self._running_script = None
        self.status_message.emit(status)

    def _run_failed(self, message: str) -> None:
        self.output_panel.append_stderr(message + "\n")
        self.output_panel.append_info(message)
        self.status_message.emit("运行失败")

    def _run_truncated(self, stream: str) -> None:
        self.output_panel.append_info(f"{stream} 输出已达到 1 MB 上限，后续内容已截断。")

    def _run_state_changed(self, state: RunState) -> None:
        running = state in {
            RunState.STARTING,
            RunState.RUNNING,
            RunState.WAITING_INPUT,
            RunState.CANCELLING,
        }
        self.run_action.setEnabled(not running)
        self.stop_action.setEnabled(running)
        self.output_panel.set_running(running)
        labels = {
            RunState.STARTING: "正在启动",
            RunState.RUNNING: "正在运行",
            RunState.WAITING_INPUT: "等待输入",
            RunState.CANCELLING: "正在停止",
        }
        if state in labels:
            self.status_message.emit(labels[state])

    def _restore_editor_state(self, editor: CodeEditor) -> None:
        if editor.file_path is None:
            return
        state = self.workspace_repository.get_editor_state(editor.file_path)
        if state is None:
            return
        cursor = editor.textCursor()
        cursor.setPosition(min(state.cursor_position, len(editor.toPlainText())))
        editor.setTextCursor(cursor)
        editor.verticalScrollBar().setValue(state.scroll_position)

    def _save_editor_state(self, editor: CodeEditor) -> None:
        if editor.file_path is None:
            return
        self.workspace_repository.save_editor_state(
            editor.file_path,
            editor.textCursor().position(),
            editor.verticalScrollBar().value(),
        )

    def can_close(self) -> bool:
        for index in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor) or not editor.document().isModified():
                continue
            result = QMessageBox.question(
                self,
                "保存修改",
                f"“{editor.file_path.name if editor.file_path else '未命名'}”尚未保存，是否保存？",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if result == QMessageBox.StandardButton.Cancel:
                return False
            if result == QMessageBox.StandardButton.Save:
                self.editor_tabs.setCurrentIndex(index)
                if not self.save_current():
                    return False
        for index in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(index)
            if isinstance(editor, CodeEditor):
                self._save_editor_state(editor)
        return True

    def stop_terminal(self) -> None:
        self.terminal.stop()
