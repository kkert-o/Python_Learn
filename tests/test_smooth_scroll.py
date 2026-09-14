from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QScrollArea, QVBoxLayout, QWidget

from app.ui.smooth_scroll import SmoothScrollFilter


def test_smooth_scroll_animates_wheel_input() -> None:
    app = QApplication.instance() or QApplication([])
    area = QScrollArea()
    content = QWidget()
    QVBoxLayout(content)
    content.setMinimumHeight(1200)
    area.setWidget(content)
    area.resize(400, 300)
    area.show()
    app.processEvents()

    scroll_filter = SmoothScrollFilter()
    wheel = QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        QPoint(),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )
    assert scroll_filter.eventFilter(area.viewport(), wheel)
    QTest.qWait(240)
    assert area.verticalScrollBar().value() > 0
    area.close()
