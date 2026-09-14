from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from app.crawler import (
    AccessMode,
    ComplianceChecker,
    CrawlPlan,
    assess_robots,
)
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def _plan(**overrides) -> CrawlPlan:  # type: ignore[no-untyped-def]
    values = {
        "target": "https://example.com/api",
        "purpose": "学习数据处理",
        "access_mode": AccessMode.PUBLIC_API,
        "has_authorization": True,
        "personal_data": False,
        "copyrighted_content": False,
        "commercial_use": False,
        "bypass_access_control": False,
        "reasonable_rate": True,
        "retention_days": 30,
    }
    values.update(overrides)
    return CrawlPlan(**values)


def test_compliance_checker_blocks_access_control_bypass() -> None:
    assessment = ComplianceChecker.assess(
        _plan(bypass_access_control=True)
    )
    assert assessment.score >= 100
    assert "高风险" in assessment.level
    assert any("访问控制" in item for item in assessment.required_actions)


def test_compliance_checker_accepts_well_defined_plan() -> None:
    assessment = ComplianceChecker.assess(_plan())
    assert assessment.score <= 20
    assert assessment.level == "较低风险"
    assert "MAX_REQUESTS" in assessment.starter_code


def test_robots_assessment() -> None:
    robots = "User-agent: PythonLearner\nDisallow: /private\nAllow: /"
    blocked = assess_robots(
        "https://example.com/private/data",
        "PythonLearner",
        robots,
    )
    allowed = assess_robots(
        "https://example.com/public",
        "PythonLearner",
        robots,
    )
    assert blocked.allowed is False
    assert allowed.allowed is True
    assert blocked.robots_url.endswith("/robots.txt")


def test_crawler_lab_ui_and_workbench(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_CRAWLER_LAB)
    app.processEvents()
    window.crawler_lab_screen.target_input.setText("https://example.com/api")
    window.crawler_lab_screen.purpose_input.setText("学习公开 API")
    window.crawler_lab_screen._assess()
    assert "风险分" in window.crawler_lab_screen.result_title.text()
    assert "MAX_REQUESTS" in window.crawler_lab_screen.starter_view.toPlainText()

    window.crawler_lab_screen._send_starter()
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_WORKBENCH
    editor = window.workbench.current_editor()
    assert editor is not None
    assert "MAX_REQUESTS" in editor.toPlainText()
    window.close()
