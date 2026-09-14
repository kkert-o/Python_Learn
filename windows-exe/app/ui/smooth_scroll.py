from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QVariantAnimation
from PySide6.QtWidgets import QAbstractScrollArea, QScrollArea, QWidget


class SmoothScrollFilter(QObject):
    """Adds short inertial easing to wheel scrolling without delaying input."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._animations: dict[QAbstractScrollArea, QVariantAnimation] = {}
        self._touch_ready: set[QScrollArea] = set()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.Wheel:
            return False
        area = self._find_scroll_area(watched)
        if area is None:
            return False
        bar = area.verticalScrollBar()
        if bar.maximum() <= bar.minimum():
            return False

        delta = event.pixelDelta().y()
        if delta == 0:
            delta = event.angleDelta().y()
        if delta == 0:
            return False

        target = bar.value() - round(delta * 0.82)
        target = max(bar.minimum(), min(bar.maximum(), target))
        if target == bar.value():
            return False

        previous = self._animations.pop(area, None)
        if previous is not None:
            previous.stop()
            previous.deleteLater()
        animation = QVariantAnimation(self)
        animation.setStartValue(bar.value())
        animation.setEndValue(target)
        animation.setDuration(190)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.valueChanged.connect(
            lambda value, scroll_bar=bar: scroll_bar.setValue(round(value))
        )
        animation.finished.connect(
            lambda target_area=area, target_animation=animation: (
                self._animations.pop(target_area, None),
                target_animation.deleteLater(),
            )
        )
        self._animations[area] = animation
        self._enable_touch_scrolling(area)
        animation.start()
        event.accept()
        return True

    def _enable_touch_scrolling(self, area: QScrollArea) -> None:
        if area in self._touch_ready:
            return
        try:
            from PySide6.QtWidgets import QScroller

            QScroller.grabGesture(
                area.viewport(),
                QScroller.ScrollerGestureType.TouchGesture,
            )
        except (AttributeError, RuntimeError):
            return
        self._touch_ready.add(area)

    @staticmethod
    def _find_scroll_area(watched: QObject) -> QScrollArea | None:
        current = watched if isinstance(watched, QWidget) else None
        while current is not None:
            if isinstance(current, QScrollArea):
                return current
            current = current.parentWidget()
        return None
