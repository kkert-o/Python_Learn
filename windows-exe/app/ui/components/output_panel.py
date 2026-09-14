from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFontDatabase, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class OutputPanel(QWidget):
    input_submitted = Signal(str)
    input_finished = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.tabs = QTabWidget()
        self.stdout_view = self._text_view()
        self.stderr_view = self._text_view()
        self.info_view = self._text_view()
        self.input_prompt = QLabel("程序尚未等待输入")
        self.input_prompt.setWordWrap(True)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入一行内容并按 Enter")
        self.input_field.setEnabled(False)
        self.send_button = QPushButton("发送输入")
        self.end_button = QPushButton("结束输入")
        self.send_button.setEnabled(False)
        self.end_button.setEnabled(False)

        self.tabs.addTab(self._wrap_readonly(self.stdout_view), "输出")
        self.tabs.addTab(self._wrap_readonly(self.stderr_view), "错误")
        self.tabs.addTab(self._wrap_readonly(self.info_view), "运行信息")
        self.tabs.addTab(self._build_input_tab(), "输入")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabs)

        self.send_button.clicked.connect(self._submit_input)
        self.input_field.returnPressed.connect(self._submit_input)
        self.end_button.clicked.connect(self._finish_input)

    @staticmethod
    def _text_view() -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        view.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        return view

    @staticmethod
    def _wrap_readonly(view: QPlainTextEdit) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(view)
        return wrapper

    def _build_input_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.input_prompt)
        row = QHBoxLayout()
        row.addWidget(self.input_field, 1)
        row.addWidget(self.send_button)
        row.addWidget(self.end_button)
        layout.addLayout(row)
        layout.addStretch(1)
        return widget

    def clear_output(self) -> None:
        self.stdout_view.clear()
        self.stderr_view.clear()
        self.info_view.clear()
        self.tabs.setCurrentIndex(0)

    def append_stdout(self, text: str) -> None:
        self.stdout_view.moveCursor(QTextCursor.MoveOperation.End)
        self.stdout_view.insertPlainText(text)
        self.stdout_view.ensureCursorVisible()

    def append_stderr(self, text: str) -> None:
        self.stderr_view.moveCursor(QTextCursor.MoveOperation.End)
        self.stderr_view.insertPlainText(text)
        self.stderr_view.ensureCursorVisible()
        self.tabs.setCurrentIndex(1)

    def append_info(self, text: str) -> None:
        self.info_view.moveCursor(QTextCursor.MoveOperation.End)
        self.info_view.insertPlainText(text + ("" if text.endswith("\n") else "\n"))
        self.info_view.ensureCursorVisible()

    def request_input(self, prompt: str) -> None:
        self.input_prompt.setText(f"程序正在等待输入：{prompt or '请提供输入内容'}")
        self.input_field.clear()
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.end_button.setEnabled(True)
        self.tabs.setCurrentWidget(self.input_field.parentWidget())
        self.input_field.setFocus()

    def set_running(self, running: bool) -> None:
        self.send_button.setEnabled(running and self.input_prompt.text().startswith("程序正在等待输入"))
        self.end_button.setEnabled(running and self.input_prompt.text().startswith("程序正在等待输入"))
        if not running:
            self.input_prompt.setText("程序尚未等待输入")
            self.input_field.setEnabled(False)

    def _submit_input(self) -> None:
        if not self.send_button.isEnabled():
            return
        text = self.input_field.text()
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.end_button.setEnabled(False)
        self.input_submitted.emit(text)

    def _finish_input(self) -> None:
        if not self.end_button.isEnabled():
            return
        self.send_button.setEnabled(False)
        self.end_button.setEnabled(False)
        self.input_finished.emit()
