from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QAction, QPainter, QTextCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta

from app.ai import AiTeacherMode, AiTeacherService, SecureCredentialStore
from app.config import AppPaths
from app.services.settings import SettingsService
from app.ui.components import ModernComboBox, PulseDots, StatusBadge


class _AiWorkerSignals(QObject):
    finished = Signal(object)


class _AiWorker(QRunnable):
    def __init__(
        self,
        service: AiTeacherService,
        question: str,
        context: str,
        mode: AiTeacherMode,
    ) -> None:
        super().__init__()
        self.service = service
        self.question = question
        self.context = context
        self.mode = mode
        self.signals = _AiWorkerSignals()

    @Slot()
    def run(self) -> None:
        self.signals.finished.emit(
            self.service.ask(self.question, self.context, self.mode)
        )


class _IconLineEdit(QLineEdit):
    def __init__(
        self,
        icon_name: str,
        right_margin: int = 30,
        *,
        clearable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.icon_name = icon_name
        self.icon_color = "#64748B"
        self._action_color = "#64748B"
        self.setObjectName("fieldEditor")
        self.setTextMargins(38, 0, right_margin, 0)
        self.clear_action: QAction | None = None
        if clearable:
            self.clear_action = QAction("", self)
            self.clear_action.setVisible(False)
            self.clear_action.triggered.connect(self.clear)
            self.addAction(
                self.clear_action,
                QLineEdit.ActionPosition.TrailingPosition,
            )
            self.textChanged.connect(self._sync_clear_action)

    def set_icon_color(self, color: str) -> None:
        self.icon_color = color
        self._action_color = color
        if self.clear_action is not None:
            self.clear_action.setIcon(
                qta.icon("fa5s.times", color=color).pixmap(13, 13)
            )
        self.update()

    def _sync_clear_action(self, text: str) -> None:
        if self.clear_action is not None:
            self.clear_action.setVisible(bool(text))

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        qta.icon(self.icon_name, color=self.icon_color).paint(
            painter,
            12,
            round((self.height() - 16) / 2),
            16,
            16,
        )


class AiTeacherScreen(QWidget):
    def __init__(
        self,
        paths: AppPaths,
        settings: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._dark = False
        self._accent = "#2563EB"
        self.service = AiTeacherService(
            settings,
            SecureCredentialStore(paths.cache_dir / "ai_key.bin"),
        )
        self.thread_pool = QThreadPool.globalInstance()

        self.header_icon = QLabel()
        self.header_icon.setObjectName("aiHeaderIcon")
        self.header_icon.setFixedSize(52, 52)
        self.header_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("AI Python 老师")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "默认使用老师模式。只发送你主动填写的问题，不会自动上传整个项目。"
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        header_copy = QVBoxLayout()
        header_copy.setSpacing(2)
        header_copy.addWidget(title)
        header_copy.addWidget(subtitle)
        header = QHBoxLayout()
        header.setSpacing(14)
        header.addWidget(self.header_icon)
        header.addLayout(header_copy, 1)

        mode_label = QLabel("教学策略")
        mode_label.setObjectName("fieldLabel")
        self.mode_combo = ModernComboBox()
        self.mode_combo.setMinimumWidth(150)
        for mode in AiTeacherMode:
            self.mode_combo.addItem(mode.value, mode)
        self.request_status = StatusBadge("正在思考", "busy")
        self.request_status.hide()
        mode_row = QHBoxLayout()
        mode_row.setSpacing(10)
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.mode_combo)
        mode_row.addWidget(self.request_status)
        mode_row.addStretch(1)

        self.chat = QPlainTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setPlaceholderText("AI 老师的回答会显示在这里")
        self.chat.setMinimumHeight(210)

        context_label = QLabel("可选上下文")
        context_label.setObjectName("sectionTitle")
        self.context_input = QPlainTextEdit()
        self.context_input.setPlaceholderText("粘贴错误信息或一小段代码")
        self.context_input.setMinimumHeight(96)
        self.context_input.setMaximumHeight(124)

        question_label = QLabel("你的问题")
        question_label.setObjectName("sectionTitle")
        self.question_input = QPlainTextEdit()
        self.question_input.setPlaceholderText("例如：为什么会出现 NameError？")
        self.question_input.setMinimumHeight(96)
        self.question_input.setMaximumHeight(124)

        context_column = QVBoxLayout()
        context_column.setSpacing(6)
        context_column.addWidget(context_label)
        context_column.addWidget(self.context_input)
        question_column = QVBoxLayout()
        question_column.setSpacing(6)
        question_column.addWidget(question_label)
        question_column.addWidget(self.question_input)
        input_row = QHBoxLayout()
        input_row.setSpacing(12)
        input_row.addLayout(context_column, 1)
        input_row.addLayout(question_column, 1)

        self.ask_button = QPushButton("询问老师")
        self.ask_button.setObjectName("primaryButton")
        self.ask_button.setIconSize(QSize(18, 18))
        self.ask_button.clicked.connect(self.ask)
        self.request_dots = PulseDots()
        self.request_dots.set_active(False)
        clear_button = QPushButton("清空对话")
        clear_button.setIconSize(QSize(17, 17))
        clear_button.clicked.connect(self._clear_chat)
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        action_row.addWidget(self.ask_button)
        action_row.addWidget(self.request_dots)
        action_row.addWidget(clear_button)
        action_row.addStretch(1)

        left = QVBoxLayout()
        left.setSpacing(10)
        left.addLayout(mode_row)
        left.addWidget(self.chat, 1)
        left.addLayout(input_row)
        left.addLayout(action_row)

        config = QFrame()
        config.setObjectName("aiConfigPanel")
        config.setMinimumWidth(326)
        config.setMaximumWidth(370)
        config_layout = QVBoxLayout(config)
        config_layout.setContentsMargins(18, 18, 18, 18)
        config_layout.setSpacing(9)
        config_header = QHBoxLayout()
        config_title = QLabel("AI 接口配置")
        config_title.setObjectName("sectionTitle")
        self.key_status = StatusBadge("", "local")
        config_header.addWidget(config_title)
        config_header.addStretch(1)
        config_header.addWidget(self.key_status)
        config_layout.addLayout(config_header)

        self.config_message = QLabel()
        self.config_message.setObjectName("configMessage")
        self.config_message.setWordWrap(True)
        self.config_message.setMinimumHeight(38)
        self.config_message.hide()
        config_layout.addWidget(self.config_message)

        endpoint_label = QLabel("接口地址")
        endpoint_label.setObjectName("fieldLabel")
        self.endpoint_input = _IconLineEdit("fa5s.link", clearable=True)
        self.endpoint_input.setText(
            str(
                settings.get(
                    "ai_endpoint",
                    "https://api.deepseek.com/chat/completions",
                )
            )
        )
        model_label = QLabel("模型")
        model_label.setObjectName("fieldLabel")
        self.model_input = _IconLineEdit("fa5s.microchip", clearable=True)
        self.model_input.setText(str(settings.get("ai_model", "deepseek-chat")))

        key_label = QLabel("API Key")
        key_label.setObjectName("fieldLabel")
        self.api_key_input = _IconLineEdit("fa5s.key", right_margin=36)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入新 Key，留空则保持原配置")
        self.reveal_action = QAction("", self.api_key_input)
        self.reveal_action.setCheckable(True)
        self.reveal_action.triggered.connect(self._toggle_key_visibility)
        self.api_key_input.addAction(
            self.reveal_action,
            QLineEdit.ActionPosition.TrailingPosition,
        )

        field_help = QLabel("Key 使用 Windows DPAPI 加密，只保存在本机。")
        field_help.setObjectName("mutedText")
        field_help.setWordWrap(True)

        save_button = QPushButton("保存配置")
        save_button.setObjectName("primaryButton")
        save_button.setIconSize(QSize(17, 17))
        save_button.clicked.connect(self._save_config)
        clear_key_button = QPushButton("清除 Key")
        clear_key_button.setObjectName("dangerButton")
        clear_key_button.setIconSize(QSize(17, 17))
        clear_key_button.clicked.connect(self._clear_key)
        key_actions = QHBoxLayout()
        key_actions.setSpacing(8)
        key_actions.addWidget(save_button)
        key_actions.addWidget(clear_key_button)
        key_actions.addStretch(1)

        config_layout.addWidget(endpoint_label)
        config_layout.addWidget(self.endpoint_input)
        config_layout.addWidget(model_label)
        config_layout.addWidget(self.model_input)
        config_layout.addWidget(key_label)
        config_layout.addWidget(self.api_key_input)
        config_layout.addWidget(field_help)
        config_layout.addStretch(1)
        config_layout.addLayout(key_actions)

        body = QHBoxLayout()
        body.setSpacing(14)
        body.addLayout(left, 1)
        body.addWidget(config)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 26, 32, 30)
        layout.setSpacing(14)
        layout.addLayout(header)
        layout.addLayout(body, 1)
        self._save_button = save_button
        self._clear_key_button = clear_key_button
        self._clear_chat_button = clear_button
        self._set_icons()
        self._refresh_key_status()

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = accent
        self.key_status.set_theme(dark, accent)
        self.request_status.set_theme(dark, accent)
        self.request_dots.set_accent(accent)
        self._set_icons()

    def _set_icons(self) -> None:
        self.header_icon.setPixmap(
            qta.icon("fa5s.robot", color=self._accent).pixmap(32, 32)
        )
        subtle = "#CBD5E1" if self._dark else "#64748B"
        self.endpoint_input.set_icon_color(subtle)
        self.model_input.set_icon_color(subtle)
        self.api_key_input.set_icon_color(subtle)
        reveal_icon = (
            "fa5s.eye-slash" if self.reveal_action.isChecked() else "fa5s.eye"
        )
        self.reveal_action.setIcon(qta.icon(reveal_icon, color=subtle))
        self.ask_button.setIcon(qta.icon("fa5s.paper-plane", color="#FFFFFF"))
        self._clear_chat_button.setIcon(
            qta.icon("fa5s.broom", color=subtle)
        )
        self._save_button.setIcon(
            qta.icon("fa5s.save", color="#FFFFFF")
        )
        self._clear_key_button.setIcon(
            qta.icon("fa5s.trash-alt", color="#DC2626")
        )

    def ask(self) -> None:
        question = self.question_input.toPlainText().strip()
        if not question:
            self._append("\n请先输入问题。\n")
            self.question_input.setFocus()
            return
        mode_value = self.mode_combo.currentData() or AiTeacherMode.TEACHER.value
        mode = AiTeacherMode(str(mode_value))
        self._append(f"\n你：{question}\n")
        self.question_input.clear()
        self._set_busy(True)
        worker = _AiWorker(
            self.service,
            question,
            self.context_input.toPlainText(),
            mode,
        )
        worker.signals.finished.connect(self._reply_ready)
        self._active_worker = worker
        if self.service.has_api_key:
            self.thread_pool.start(worker)
        else:
            worker.run()

    def _reply_ready(self, reply) -> None:  # type: ignore[no-untyped-def]
        self._set_busy(False)
        source = f"{reply.source}"
        if reply.error:
            source += f" · 联网失败：{reply.error}"
            self._show_config_message(f"联网失败：{reply.error}", "error")
            self.key_status.set_status("本地引导 · 联网失败", "error")
        else:
            self._refresh_key_status()
        self._append(f"\nAI 老师（{source}）：\n{reply.content}\n")

    def _set_busy(self, busy: bool) -> None:
        self.ask_button.setEnabled(not busy)
        self.ask_button.setText("正在思考" if busy else "询问老师")
        self.request_status.setVisible(busy)
        self.request_dots.set_active(busy)
        if busy:
            self.ask_button.setIcon(
                qta.icon(
                    "fa5s.spinner",
                    color="#FFFFFF",
                    animation=qta.Spin(self.ask_button),
                )
            )
        else:
            self.ask_button.setIcon(
                qta.icon("fa5s.paper-plane", color="#FFFFFF")
            )

    def _append(self, text: str) -> None:
        self.chat.moveCursor(QTextCursor.MoveOperation.End)
        self.chat.insertPlainText(text)
        self.chat.ensureCursorVisible()

    def _clear_chat(self) -> None:
        self.chat.clear()

    def _save_config(self) -> None:
        try:
            self.service.save_config(
                endpoint=self.endpoint_input.text(),
                model=self.model_input.text(),
                api_key=self.api_key_input.text(),
            )
        except (OSError, RuntimeError, ValueError) as exc:
            self._show_config_message(str(exc), "error")
            return
        had_key = self.service.has_api_key
        self.api_key_input.clear()
        self._refresh_key_status()
        if had_key:
            self._show_config_message("配置已保存，API Key 已加密保存。", "success")
        else:
            self._show_config_message(
                "接口和模型已保存，当前仍使用本地引导模式。",
                "success",
            )

    def _clear_key(self) -> None:
        self.service.clear_api_key()
        self.api_key_input.clear()
        self.reveal_action.setChecked(False)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._refresh_key_status()
        self._show_config_message("API Key 已清除，当前使用本地引导模式。", "success")

    def _refresh_key_status(self) -> None:
        if self.service.has_api_key:
            self.key_status.set_status("API Key 已加密保存", "online")
        else:
            self.key_status.set_status("本地引导 · 未配置", "local")

    def _show_config_message(self, text: str, state: str) -> None:
        self.config_message.setText(text)
        self.config_message.setProperty("state", state)
        self.config_message.style().unpolish(self.config_message)
        self.config_message.style().polish(self.config_message)
        self.config_message.show()

    def _toggle_key_visibility(self, visible: bool) -> None:
        self.api_key_input.setEchoMode(
            QLineEdit.EchoMode.Normal
            if visible
            else QLineEdit.EchoMode.Password
        )
        subtle = "#CBD5E1" if self._dark else "#64748B"
        self.reveal_action.setIcon(
            qta.icon(
                "fa5s.eye-slash" if visible else "fa5s.eye",
                color=subtle,
            )
        )
