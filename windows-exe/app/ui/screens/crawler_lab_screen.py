from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QLayout,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.crawler import (
    AccessMode,
    ComplianceChecker,
    CrawlPlan,
    assess_robots,
)
from app.services.settings import SettingsService
from app.ui.components import AnimatedCheckBox, ModernComboBox
import qtawesome as qta


class CrawlerLabScreen(QWidget):
    workbench_requested = Signal(str, str)

    def __init__(
        self,
        settings: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._dark = False
        self._accent = "#2563EB"
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("https://example.com/api")
        self.purpose_input = QLineEdit()
        self.purpose_input.setPlaceholderText("例如：生成公开天气数据学习报告")
        self.access_mode = ModernComboBox()
        for mode in AccessMode:
            self.access_mode.addItem(mode.value, mode)
        self.authorized_check = AnimatedCheckBox("已确认服务条款、robots 规则或获得授权")
        self.personal_data_check = AnimatedCheckBox("包含个人信息")
        self.copyright_check = AnimatedCheckBox("包含可能受著作权保护的全文内容")
        self.commercial_check = AnimatedCheckBox("用于商业用途")
        self.bypass_check = AnimatedCheckBox("需要绕过登录、验证码或访问控制")
        self.rate_check = AnimatedCheckBox("请求频率合理，并设置超时与有限重试")
        self.rate_check.set_state(True)
        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(0, 3650)
        self.retention_spin.setValue(30)
        self.retention_spin.setSuffix(" 天")

        self.result_title = QLabel("填写信息后执行检查")
        self.result_title.setObjectName("sectionTitle")
        self.result_detail = QLabel()
        self.result_detail.setWordWrap(True)
        self.result_actions = QLabel()
        self.result_actions.setWordWrap(True)
        self.starter_view = self._code_view()
        send_button = QPushButton("发送安全起始代码到工作台")
        send_button.setObjectName("secondaryButton")
        send_button.setIcon(qta.icon("fa5s.share", color="#2563EB"))
        send_button.setIconSize(QSize(16, 16))
        send_button.clicked.connect(self._send_starter)

        check_button = QPushButton("执行合规检查")
        check_button.setObjectName("primaryButton")
        check_button.setIcon(qta.icon("fa5s.shield-alt", color="#FFFFFF"))
        check_button.setIconSize(QSize(17, 17))
        check_button.clicked.connect(self._assess)
        form_actions = QHBoxLayout()
        form_actions.addWidget(check_button)
        form_actions.addStretch(1)

        plan_card = QFrame()
        plan_card.setObjectName("lessonSection")
        plan_layout = QVBoxLayout(plan_card)
        plan_title = QLabel("采集计划")
        plan_title.setObjectName("sectionTitle")
        plan_help = QLabel(
            "先记录目标、用途、访问方式和保存期限；系统只做合规评估并生成安全起始代码，不会自动访问目标网站。"
        )
        plan_help.setObjectName("mutedText")
        plan_help.setWordWrap(True)
        plan_layout.addWidget(plan_title)
        plan_layout.addWidget(plan_help)
        plan_layout.addWidget(QLabel("目标 URL / API"))
        plan_layout.addWidget(self.target_input)
        plan_layout.addWidget(QLabel("数据用途"))
        plan_layout.addWidget(self.purpose_input)
        plan_layout.addWidget(QLabel("访问方式"))
        plan_layout.addWidget(self.access_mode)
        for checkbox in (
            self.authorized_check,
            self.personal_data_check,
            self.copyright_check,
            self.commercial_check,
            self.bypass_check,
            self.rate_check,
        ):
            plan_layout.addWidget(checkbox)
        retention_row = QHBoxLayout()
        retention_row.addWidget(QLabel("数据保存期限"))
        retention_row.addWidget(self.retention_spin)
        retention_row.addStretch(1)
        plan_layout.addLayout(retention_row)
        plan_layout.addLayout(form_actions)

        result_card = QFrame()
        result_card.setObjectName("lessonSection")
        result_layout = QVBoxLayout(result_card)
        result_layout.addWidget(self.result_title)
        result_layout.addWidget(self.result_detail)
        result_layout.addWidget(self.result_actions)
        result_layout.addWidget(self.starter_view)
        result_layout.addWidget(send_button, alignment=Qt.AlignmentFlag.AlignLeft)

        robots_card = QFrame()
        robots_card.setObjectName("lessonSection")
        robots_layout = QVBoxLayout(robots_card)
        robots_title = QLabel("robots.txt 规则检查")
        robots_title.setObjectName("sectionTitle")
        self.robots_url = QLineEdit()
        self.robots_url.setPlaceholderText("https://example.com/news")
        self.robots_agent = QLineEdit("PythonLearner")
        self.robots_text = QPlainTextEdit()
        self.robots_text.setPlaceholderText(
            "将 robots.txt 内容粘贴到这里；本工具不会自动请求目标网站。"
        )
        self.robots_text.setMaximumHeight(140)
        robots_button = QPushButton("检查规则")
        robots_button.clicked.connect(self._check_robots)
        self.robots_result = QLabel()
        self.robots_result.setWordWrap(True)
        robots_layout.addWidget(robots_title)
        robots_layout.addWidget(self.robots_url)
        robots_layout.addWidget(self.robots_agent)
        robots_layout.addWidget(self.robots_text)
        robots_layout.addWidget(robots_button, alignment=Qt.AlignmentFlag.AlignLeft)
        robots_layout.addWidget(self.robots_result)

        legal_card = QFrame()
        legal_card.setObjectName("lessonSection")
        legal_layout = QVBoxLayout(legal_card)
        legal_title = QLabel("法律地区")
        legal_title.setObjectName("sectionTitle")
        self.legal_region = ModernComboBox()
        self.legal_region.addItems(
            ("中国大陆", "日本", "美国", "欧盟", "其他")
        )
        current_region = str(settings.get("legal_region", "中国大陆"))
        index = self.legal_region.findText(current_region)
        self.legal_region.setCurrentIndex(max(0, index))
        self.legal_region.currentTextChanged.connect(
            lambda value: self.settings.set("legal_region", value)
        )
        disclaimer = QLabel(
            "合规检查只是学习性风险提示，不构成法律意见。"
            "不同地区的法律、服务条款和数据用途要求可能不同。"
        )
        disclaimer.setWordWrap(True)
        disclaimer.setObjectName("mutedText")
        legal_layout.addWidget(legal_title)
        legal_layout.addWidget(self.legal_region)
        legal_layout.addWidget(disclaimer)

        title = QLabel("爬虫与合规实验室")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "用于在编写爬虫前整理采集边界：确认授权、数据类型、频率、用途和保存期限，再生成合规起始骨架。"
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 26, 32, 30)
        layout.setSpacing(12)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(plan_card)
        layout.addWidget(result_card)
        layout.addWidget(robots_card)
        layout.addWidget(legal_card)
        layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)
        self.starter_view.setPlainText(
            ComplianceChecker.assess(self._build_plan()).starter_code
        )

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = accent
        for checkbox in (
            self.authorized_check,
            self.personal_data_check,
            self.copyright_check,
            self.commercial_check,
            self.bypass_check,
            self.rate_check,
        ):
            checkbox.set_theme(dark, accent)

    def _build_plan(self) -> CrawlPlan:
        access_value = self.access_mode.currentData() or AccessMode.UNKNOWN.value
        return CrawlPlan(
            target=self.target_input.text().strip(),
            purpose=self.purpose_input.text().strip(),
            access_mode=AccessMode(str(access_value)),
            has_authorization=self.authorized_check.isChecked(),
            personal_data=self.personal_data_check.isChecked(),
            copyrighted_content=self.copyright_check.isChecked(),
            commercial_use=self.commercial_check.isChecked(),
            bypass_access_control=self.bypass_check.isChecked(),
            reasonable_rate=self.rate_check.isChecked(),
            retention_days=self.retention_spin.value(),
        )

    def _assess(self) -> None:
        assessment = ComplianceChecker.assess(self._build_plan())
        self.result_title.setText(
            f"检查结果：{assessment.level} · 风险分 {assessment.score}/100"
        )
        self.result_detail.setText(
            "发现：\n" + "\n".join(f"• {item}" for item in assessment.findings)
        )
        self.result_actions.setText(
            "建议：\n"
            + "\n".join(f"• {item}" for item in assessment.required_actions)
        )
        self.starter_view.setPlainText(assessment.starter_code)
        self.result_title.setObjectName(
            "quizWrong" if assessment.score > 55 else "successText"
        )
        self.result_title.style().unpolish(self.result_title)
        self.result_title.style().polish(self.result_title)

    def _check_robots(self) -> None:
        result = assess_robots(
            self.robots_url.text().strip(),
            self.robots_agent.text().strip(),
            self.robots_text.toPlainText(),
        )
        suffix = f"\nrobots 地址：{result.robots_url}" if result.robots_url else ""
        self.robots_result.setText(result.message + suffix)

    def _send_starter(self) -> None:
        self.workbench_requested.emit(
            "合规采集起始骨架",
            self.starter_view.toPlainText(),
        )

    @staticmethod
    def _code_view() -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        view.setMaximumHeight(260)
        return view
