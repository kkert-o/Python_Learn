from __future__ import annotations

from functools import lru_cache
from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta


@lru_cache(maxsize=128)
def _cached_icon(icon_name: str, color: str):
    return qta.icon(icon_name, color=color)


class NavButton(QAbstractButton):
    def __init__(
        self,
        text: str,
        icon_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.icon_name = icon_name
        self.selected = False
        self.dark = False
        self.accent = QColor("#2563EB")
        self._hover_progress = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setMinimumHeight(40)
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_hover_progress)

    def sizeHint(self) -> QSize:
        return QSize(210, 40)

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        self.setChecked(selected)
        self.update()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_to(0.0)
        super().leaveEvent(event)

    def _animate_to(self, value: float) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._hover_progress)
        self._animation.setEndValue(value)
        self._animation.start()

    def _set_hover_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._hover_progress = float(value)
        self.update()

    def get_hover_progress(self) -> float:
        return self._hover_progress

    def set_hover_progress(self, value: float) -> None:
        self._hover_progress = value
        self.update()

    hoverProgress = Property(
        float,
        get_hover_progress,
        set_hover_progress,
    )

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        if self.selected:
            selected_color = QColor(self.accent)
            selected_color.setAlpha(52 if self.dark else 36)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(selected_color)
            painter.drawRoundedRect(rect, 10, 10)
        if self._hover_progress > 0:
            hover_color = QColor("#FFFFFF" if self.dark else "#0F172A")
            hover_color.setAlpha(round(18 * self._hover_progress))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover_color)
            painter.drawRoundedRect(rect, 10, 10)

        if self.selected:
            painter.setBrush(self.accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRectF(rect.left() + 1, rect.center().y() - 10, 3, 20),
                1.5,
                1.5,
            )

        icon_color = (
            self.accent.name()
            if self.selected
            else "#E5E7EB"
            if self.dark
            else "#475569"
        )
        icon = _cached_icon(self.icon_name, icon_color)
        icon_size = 20 + round(2 * self._hover_progress)
        icon_x = 15 + round(1.5 * self._hover_progress)
        icon.paint(
            painter,
            int(rect.left() + icon_x),
            int(rect.center().y() - icon_size / 2),
            icon_size,
            icon_size,
        )

        painter.setPen(
            QColor(
                "#F8FAFC"
                if self.dark and (self.selected or self._hover_progress > 0.35)
                else "#0F172A"
                if self.selected or self._hover_progress > 0.35
                else "#334155"
                if not self.dark
                else "#CBD5E1"
            )
        )
        font = QFont(self.font())
        font.setPointSize(10.5)
        font.setWeight(QFont.Weight.DemiBold if self.selected else QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(
            QRectF(
                rect.left() + 48 + 1.5 * self._hover_progress,
                rect.top(),
                rect.width() - 58,
                rect.height(),
            ),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class SidebarNavigation(QWidget):
    currentRowChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._buttons: list[NavButton] = []
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self.setCurrentRow)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._current_row = -1
        self.dark = False
        self.accent = "#2563EB"

    def addItem(self, text: str, icon_name: str) -> None:
        row = len(self._buttons)
        button = NavButton(text, icon_name, self)
        button.set_theme(self.dark, self.accent)
        self._group.addButton(button, row)
        self._buttons.append(button)
        self._layout.addWidget(button)

    def count(self) -> int:
        return len(self._buttons)

    def currentRow(self) -> int:
        return self._current_row

    def setCurrentRow(self, row: int) -> None:
        if row < 0 or row >= len(self._buttons):
            return
        if self._current_row == row:
            return
        self._current_row = row
        for index, button in enumerate(self._buttons):
            button.set_selected(index == row)
        self.currentRowChanged.emit(row)

    def itemText(self, row: int) -> str:
        return self._buttons[row].text()

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = accent
        for button in self._buttons:
            button.set_theme(dark, accent)
