from __future__ import annotations

import math

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QListView,
    QSizePolicy,
    QSlider,
    QWidget,
)
import qtawesome as qta

from app.ui.components.wallpaper import cover_source_rect, load_wallpaper_image


class ToggleSwitch(QAbstractButton):
    def __init__(self, accent: str = "#2563EB", parent=None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(46, 26)
        self.accent = QColor(accent)
        self.dark = False
        self.progress = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(140)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_progress)
        self.toggled.connect(self._animate)

    def sizeHint(self) -> QSize:
        return QSize(46, 26)

    def set_accent(self, accent: str) -> None:
        self.accent = QColor(accent)
        self.update()

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def set_state(self, checked: bool, *, animate: bool = False) -> None:
        if animate:
            self.setChecked(checked)
            return
        self._animation.stop()
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self.progress = 1.0 if checked else 0.0
        self.update()

    def _animate(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self.progress)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    def _set_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self.progress = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(1, 3, self.width() - 2, self.height() - 6)
        track_color = QColor("#CBD5E1")
        track_color = self._blend(track_color, self.accent, self.progress)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, track.height() / 2, track.height() / 2)
        diameter = track.height() - 4
        x = track.left() + 2 + (track.width() - diameter - 4) * self.progress
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QRectF(x, track.top() + 2, diameter, diameter))

    @staticmethod
    def _blend(first: QColor, second: QColor, amount: float) -> QColor:
        amount = max(0.0, min(1.0, amount))
        return QColor(
            round(first.red() + (second.red() - first.red()) * amount),
            round(first.green() + (second.green() - first.green()) * amount),
            round(first.blue() + (second.blue() - first.blue()) * amount),
        )


class StatusBadge(QWidget):
    def __init__(
        self,
        text: str = "",
        status: str = "local",
        accent: str = "#2563EB",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.text = text
        self.status = status
        self.accent = QColor(accent)
        self.dark = False
        self._phase = 0.0
        self.setMinimumHeight(34)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self._timer = QTimer(self)
        self._timer.setInterval(32)
        self._timer.timeout.connect(self._advance)
        self._update_timer()

    def sizeHint(self) -> QSize:
        return QSize(
            self.fontMetrics().horizontalAdvance(self.text) + 50,
            34,
        )

    def set_status(self, text: str, status: str) -> None:
        self.text = text
        self.status = status
        self._update_timer()
        self.updateGeometry()
        self.update()

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def _update_timer(self) -> None:
        if self.status in {"online", "busy"}:
            self._timer.start()
        else:
            self._timer.stop()
            self._phase = 0.0

    def _advance(self) -> None:
        self._phase = (self._phase + 0.045) % 1.0
        self.update()

    def _status_color(self) -> QColor:
        if self.status == "error":
            return QColor("#EF4444")
        if self.status == "busy":
            return QColor("#F59E0B")
        if self.status == "online":
            return QColor(self.accent)
        return QColor("#94A3B8" if self.dark else "#64748B")

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        color = self._status_color()
        fill = QColor(color)
        fill.setAlpha(28 if self.dark else 20)
        border = QColor(color)
        border.setAlpha(95)
        painter.setPen(QPen(border, 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect, 9, 9)

        center_x = rect.left() + 16
        center_y = rect.center().y()
        if self.status in {"online", "busy"}:
            ring = QColor(color)
            ring.setAlpha(round(95 * (1.0 - self._phase)))
            painter.setPen(QPen(ring, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            radius = 5 + 4 * self._phase
            painter.drawEllipse(
                QRectF(
                    center_x - radius,
                    center_y - radius,
                    radius * 2,
                    radius * 2,
                )
            )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(QRectF(center_x - 4, center_y - 4, 8, 8))

        painter.setPen(QColor("#F8FAFC" if self.dark else "#0F172A"))
        font = QFont(self.font())
        font.setPointSize(9.5)
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(
            QRectF(rect.left() + 28, rect.top(), rect.width() - 37, rect.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text,
        )


class PulseDots(QWidget):
    def __init__(
        self,
        accent: str = "#2563EB",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.accent = QColor(accent)
        self._phase = 0.0
        self._active = False
        self.setFixedSize(46, 20)
        self._timer = QTimer(self)
        self._timer.setInterval(36)
        self._timer.timeout.connect(self._advance)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setVisible(active)
        if active:
            self._timer.start()
        else:
            self._timer.stop()
            self._phase = 0.0
        self.update()

    def set_accent(self, accent: str) -> None:
        self.accent = QColor(accent)
        self.update()

    def _advance(self) -> None:
        self._phase = (self._phase + 0.14) % 1.0
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self._active:
            return
        center_y = self.height() / 2
        for index in range(3):
            phase = (self._phase + index / 3.0) % 1.0
            wave = (math.sin(phase * math.tau) + 1.0) / 2.0
            radius = 3.0 + 2.2 * wave
            color = QColor(self.accent)
            color.setAlpha(round(100 + 155 * wave))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            center_x = 11 + index * 12
            painter.drawEllipse(
                QRectF(
                    center_x - radius,
                    center_y - radius,
                    radius * 2,
                    radius * 2,
                )
            )


class AnimatedCheckBox(QAbstractButton):
    def __init__(
        self,
        text: str,
        accent: str = "#2563EB",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.accent = QColor(accent)
        self.dark = False
        self._hover_progress = 0.0
        self._selection_progress = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(140)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_hover_progress)
        self._selection_animation = QVariantAnimation(self)
        self._selection_animation.setDuration(170)
        self._selection_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._selection_animation.valueChanged.connect(
            self._set_selection_progress
        )
        self.toggled.connect(self._animate_selection)

    def sizeHint(self) -> QSize:
        return QSize(
            self.fontMetrics().horizontalAdvance(self.text()) + 42,
            max(34, self.fontMetrics().height() + 12),
        )

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def set_state(self, checked: bool, *, animate: bool = False) -> None:
        if animate:
            self.setChecked(checked)
            return
        self._selection_animation.stop()
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self._selection_progress = 1.0 if checked else 0.0
        self.update()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, value: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(value)
        self._hover_animation.start()

    def _animate_selection(self, checked: bool) -> None:
        self._selection_animation.stop()
        self._selection_animation.setStartValue(self._selection_progress)
        self._selection_animation.setEndValue(1.0 if checked else 0.0)
        self._selection_animation.start()

    def _set_hover_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._hover_progress = float(value)
        self.update()

    def _set_selection_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._selection_progress = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(
            1,
            (self.height() - 20) / 2,
            20,
            20,
        )
        border = QColor("#52657A" if not self.dark else "#A9B7C8")
        if self._hover_progress > 0:
            border = self.accent
        painter.setPen(QPen(border, 1.5))
        fill = QColor(self.accent)
        fill.setAlpha(round(235 * self._selection_progress))
        painter.setBrush(fill)
        painter.drawRoundedRect(box, 6, 6)

        if self._selection_progress > 0:
            check = QColor("#FFFFFF")
            check_pen = QPen(check, 2.2)
            check_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(check_pen)
            left = box.left() + 4
            middle = box.left() + 8.5
            right = box.right() - 4
            center = box.center().y()
            painter.drawLine(
                QPointF(left, center),
                QPointF(middle, center + 4),
            )
            painter.drawLine(
                QPointF(middle, center + 4),
                QPointF(right, center - 4),
            )

        painter.setPen(QColor("#F8FAFC" if self.dark else "#0F172A"))
        font = QFont(self.font())
        font.setPointSize(10)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)
        painter.drawText(
            QRectF(32, 0, self.width() - 36, self.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class ModernComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        view = QListView(self)
        view.setObjectName("modernComboPopup")
        view.setSpacing(3)
        view.setUniformItemSizes(True)
        self.setView(view)
        self.setMaxVisibleItems(10)

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = self.palette().color(self.foregroundRole())
        color.setAlpha(190)
        pen = QPen(color, 1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        center_x = self.width() - 19
        center_y = self.height() / 2 - 1
        painter.drawLine(
            QPointF(center_x - 4, center_y - 2),
            QPointF(center_x, center_y + 2),
        )
        painter.drawLine(
            QPointF(center_x, center_y + 2),
            QPointF(center_x + 4, center_y - 2),
        )


class ModernSlider(QSlider):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.accent = QColor("#2563EB")
        self.dark = False
        self._hover_progress = 0.0
        self._pressed = False
        self.setMinimumHeight(34)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(140)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_hover_progress)

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, value: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(value)
        self._hover_animation.start()

    def _set_hover_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._hover_progress = float(value)
        self.update()

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.setSliderDown(True)
            self._set_value_from_x(event.position().x())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if self._pressed:
            self._set_value_from_x(event.position().x())
            self.sliderMoved.emit(self.value())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._set_value_from_x(event.position().x())
            self._pressed = False
            self.setSliderDown(False)
            self.update()
            self.sliderReleased.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _set_value_from_x(self, x_position: float) -> None:
        if self.maximum() <= self.minimum():
            return
        usable = max(1.0, self.width() - 24)
        ratio = min(1.0, max(0.0, (x_position - 12) / usable))
        value = self.minimum() + round(ratio * (self.maximum() - self.minimum()))
        self.setValue(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(12, self.height() / 2 - 5, self.width() - 24, 10)
        track_color = QColor("#334155" if self.dark else "#DDE5EF")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track, 5, 5)

        ratio = (self.value() - self.minimum()) / max(
            1,
            self.maximum() - self.minimum(),
        )
        fill_width = track.width() * ratio
        if fill_width > 0:
            fill = QRectF(track.left(), track.top(), fill_width, track.height())
            painter.setBrush(self.accent)
            painter.drawRoundedRect(fill, 5, 5)

        handle_x = track.left() + fill_width
        handle_radius = 10 + 1.5 * self._hover_progress + (2 if self._pressed else 0)
        halo = QColor(self.accent)
        halo.setAlpha(round(34 + 34 * self._hover_progress))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo)
        painter.drawEllipse(
            QRectF(
                handle_x - handle_radius - 4,
                self.height() / 2 - handle_radius - 4,
                (handle_radius + 4) * 2,
                (handle_radius + 4) * 2,
            )
        )
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(QPen(self.accent, 2))
        painter.drawEllipse(
            QRectF(
                handle_x - handle_radius,
                self.height() / 2 - handle_radius,
                handle_radius * 2,
                handle_radius * 2,
            )
        )


class ThemeSegmentButton(QAbstractButton):
    def __init__(
        self,
        text: str,
        icon_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.icon_name = icon_name
        self.dark = False
        self.accent = QColor("#2563EB")
        self._hover_progress = 0.0
        self._selection_progress = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(102, 42)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_hover_progress)
        self._selection_animation = QVariantAnimation(self)
        self._selection_animation.setDuration(190)
        self._selection_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._selection_animation.valueChanged.connect(
            self._set_selection_progress
        )
        self.toggled.connect(self._animate_selection)

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def set_selected(self, selected: bool, *, animate: bool = False) -> None:
        if animate:
            self.setChecked(selected)
            return
        self._selection_animation.stop()
        self.blockSignals(True)
        self.setChecked(selected)
        self.blockSignals(False)
        self._selection_progress = 1.0 if selected else 0.0
        self.update()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, value: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(value)
        self._hover_animation.start()

    def _animate_selection(self, checked: bool) -> None:
        self._selection_animation.stop()
        self._selection_animation.setStartValue(self._selection_progress)
        self._selection_animation.setEndValue(1.0 if checked else 0.0)
        self._selection_animation.start()

    def _set_hover_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._hover_progress = float(value)
        self.update()

    def _set_selection_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._selection_progress = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)

        hover = QColor("#FFFFFF" if self.dark else "#0F172A")
        hover.setAlpha(round(13 * self._hover_progress))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hover)
        painter.drawRoundedRect(rect, 9, 9)

        if self._selection_progress > 0:
            fill = QColor(self.accent)
            fill.setAlpha(
                round((34 if self.dark else 26) * self._selection_progress)
            )
            border = QColor(self.accent)
            border.setAlpha(round(205 * self._selection_progress))
            painter.setBrush(fill)
            painter.setPen(QPen(border, 1.2))
            painter.drawRoundedRect(rect, 9, 9)

        icon_color = (
            self.accent.name()
            if self.isChecked()
            else "#CBD5E1"
            if self.dark
            else "#475569"
        )
        icon = qta.icon(self.icon_name, color=icon_color)
        icon.paint(
            painter,
            int(rect.left() + 13),
            int(rect.center().y() - 8),
            16,
            16,
        )
        painter.setPen(
            QColor(
                "#F8FAFC"
                if self.dark and self.isChecked()
                else "#0F172A"
                if self.isChecked()
                else "#CBD5E1"
                if self.dark
                else "#334155"
            )
        )
        font = QFont(self.font())
        font.setPointSize(10)
        font.setWeight(
            QFont.Weight.DemiBold if self.isChecked() else QFont.Weight.Medium
        )
        painter.setFont(font)
        painter.drawText(
            QRectF(rect.left() + 36, rect.top(), rect.width() - 44, rect.height()),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class ThemeModeSwitch(QWidget):
    modeChanged = Signal(str)

    MODES = (
        ("light", "浅色", "fa5s.sun"),
        ("dark", "深色", "fa5s.moon"),
        ("system", "跟随系统", "fa5s.desktop"),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("themeModeSwitch")
        self.dark = False
        self.accent = "#2563EB"
        self._buttons: dict[str, ThemeSegmentButton] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.idClicked.connect(self._mode_clicked)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        for index, (mode, text, icon_name) in enumerate(self.MODES):
            button = ThemeSegmentButton(text, icon_name, self)
            button.setProperty("themeMode", mode)
            button.set_theme(self.dark, self.accent)
            self._group.addButton(button, index)
            self._buttons[mode] = button
            layout.addWidget(button)
        self._buttons["light"].set_selected(True)

    @property
    def group(self) -> QButtonGroup:
        return self._group

    def button(self, mode: str) -> ThemeSegmentButton | None:
        return self._buttons.get(mode)

    def current_mode(self) -> str:
        for mode, button in self._buttons.items():
            if button.isChecked():
                return mode
        return "light"

    def set_mode(self, mode: str, *, emit: bool = False) -> None:
        button = self._buttons.get(mode)
        if button is None:
            button = self._buttons["light"]
        if button.isChecked():
            return
        for item in self._buttons.values():
            item.set_selected(item is button)
        if emit:
            self.modeChanged.emit(mode)

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = accent
        for button in self._buttons.values():
            button.set_theme(dark, accent)

    def _mode_clicked(self, button_id: int) -> None:
        button = self._group.button(button_id)
        if button is None:
            return
        mode = str(button.property("themeMode"))
        self.set_mode(mode)
        self.modeChanged.emit(mode)


class AccentSwatch(QAbstractButton):
    def __init__(self, color: str, parent=None) -> None:
        super().__init__(parent)
        self.color = QColor(color)
        self.dark = False
        self._hover_progress = 0.0
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(40, 40)
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_hover_progress)

    def sizeHint(self) -> QSize:
        return QSize(40, 40)

    def set_theme(self, dark: bool) -> None:
        self.dark = dark
        self.update()

    def _set_hover_progress(self, value) -> None:  # type: ignore[no-untyped-def]
        self._hover_progress = float(value)
        self.update()

    def _animate_hover(self, value: float) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._hover_progress)
        self._animation.setEndValue(value)
        self._animation.start()

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isChecked() or self._hover_progress > 0:
            ring = QColor(self.color)
            ring.setAlpha(
                round(
                    (92 if self.isChecked() else 38)
                    + (42 * self._hover_progress)
                )
            )
            painter.setPen(QPen(ring, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(2, 2, 36, 36))
        radius = 15.5 - (1.5 * self._hover_progress) - (1.5 if self.isChecked() else 0)
        if self.isChecked():
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(self.color)
            painter.drawEllipse(
                QRectF(
                    self.rect().center().x() - radius,
                    self.rect().center().y() - radius,
                    radius * 2,
                    radius * 2,
                )
            )
            painter.setPen(QPen(QColor("#FFFFFF"), 2.3))
            painter.drawLine(13, 20, 18, 25)
            painter.drawLine(18, 25, 28, 15)
        else:
            border = QColor("#94A3B8" if self.dark else "#CBD5E1")
            border.setAlpha(round(190 + 65 * self._hover_progress))
            painter.setPen(QPen(border, 1))
            painter.setBrush(self.color)
            painter.drawEllipse(
                QRectF(
                    self.rect().center().x() - radius,
                    self.rect().center().y() - radius,
                    radius * 2,
                    radius * 2,
                )
            )


class ThemePreview(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.dark = False
        self.accent = QColor("#2563EB")
        self.wallpaper_path = ""
        self.wallpaper_transparency = 35
        self._wallpaper_image = QImage()
        self.setMinimumSize(260, 218)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def set_theme(
        self,
        dark: bool,
        accent: str,
        wallpaper_path: str = "",
        transparency: int = 35,
    ) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        next_path = str(wallpaper_path or "")
        if next_path != self.wallpaper_path:
            self.wallpaper_path = next_path
            self._wallpaper_image = load_wallpaper_image(next_path)
        self.wallpaper_transparency = max(0, min(90, int(transparency)))
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        outer = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        clip = QPainterPath()
        clip.addRoundedRect(outer, 10, 10)
        painter.setClipPath(clip)

        base = QColor("#0B1220" if self.dark else "#F8FAFC")
        painter.fillRect(outer, base)
        if not self._wallpaper_image.isNull():
            visible = 1.0 - self.wallpaper_transparency / 100.0
            painter.setOpacity(max(0.12, visible))
            painter.drawImage(
                outer,
                self._wallpaper_image,
                cover_source_rect(self._wallpaper_image, self.size()),
            )
            painter.setOpacity(1.0)

        surface = QColor(12, 20, 35, 210) if self.dark else QColor(255, 255, 255, 204)
        sidebar = QRectF(outer.left(), outer.top(), 60, outer.height())
        painter.fillRect(sidebar, QColor(8, 15, 28, 225) if self.dark else QColor(255, 255, 255, 232))
        content = QRectF(sidebar.right(), outer.top(), outer.width() - 60, outer.height())
        painter.fillRect(content, surface)

        accent = self.accent
        selected = QColor(accent)
        selected.setAlpha(46 if self.dark else 34)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(selected)
        painter.drawRoundedRect(QRectF(12, 42, 38, 22), 7, 7)

        line_color = QColor("#B7C3D2" if self.dark else "#CBD5E1")
        for y, width in ((42, 36), (70, 29), (98, 33), (126, 24)):
            line = QColor(line_color)
            line.setAlpha(120)
            painter.setBrush(line)
            painter.drawRoundedRect(QRectF(14, y, width, 5), 2.5, 2.5)

        title = QColor("#F8FAFC" if self.dark else "#0F172A")
        painter.setBrush(title)
        painter.drawRoundedRect(QRectF(76, 28, 92, 9), 4.5, 4.5)
        muted = QColor("#94A3B8" if self.dark else "#64748B")
        muted.setAlpha(150)
        painter.setBrush(muted)
        painter.drawRoundedRect(QRectF(76, 45, 128, 6), 3, 3)

        card = QColor(20, 31, 48, 235) if self.dark else QColor(255, 255, 255, 238)
        painter.setBrush(card)
        painter.drawRoundedRect(QRectF(74, 68, outer.width() - 90, 66), 8, 8)
        painter.setBrush(accent)
        painter.drawRoundedRect(QRectF(86, 82, 64, 20), 6, 6)
        detail = QColor("#D8E1EC" if self.dark else "#D8E1EC")
        painter.setBrush(detail)
        painter.drawRoundedRect(QRectF(86, 112, 112, 7), 3.5, 3.5)

        lower = QColor(20, 31, 48, 220) if self.dark else QColor(255, 255, 255, 230)
        painter.setBrush(lower)
        painter.drawRoundedRect(QRectF(74, 145, outer.width() - 90, 56), 8, 8)
        painter.setBrush(muted)
        painter.drawRoundedRect(QRectF(87, 159, 72, 7), 3.5, 3.5)
        painter.setBrush(detail)
        painter.drawRoundedRect(QRectF(87, 174, 138, 7), 3.5, 3.5)


class MilestoneRow(QAbstractButton):
    def __init__(
        self,
        number: int,
        title: str,
        description: str,
        accent: str = "#2563EB",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.number = number
        self.title = title
        self.description = description
        self.accent = QColor(accent)
        self.dark = False
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(68)

    def sizeHint(self) -> QSize:
        return QSize(720, 68)

    def set_accent(self, accent: str) -> None:
        self.accent = QColor(accent)
        self.update()

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        if self.isChecked():
            fill = QColor(self.accent)
            fill.setAlpha(22)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(rect, 12, 12)
        if self.underMouse():
            hover = QColor("#FFFFFF" if self.dark else "#0F172A")
            hover.setAlpha(12)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(hover)
            painter.drawRoundedRect(rect, 12, 12)

        circle = QRectF(16, rect.center().y() - 15, 30, 30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.accent if self.isChecked() else QColor("#E2E8F0"))
        painter.drawEllipse(circle)
        painter.setPen(
            QColor("#FFFFFF")
            if self.isChecked()
            else QColor("#94A3B8" if self.dark else "#64748B")
        )
        font = QFont(self.font())
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(
            circle,
            Qt.AlignmentFlag.AlignCenter,
            "✓" if self.isChecked() else str(self.number),
        )

        text_rect = QRectF(60, rect.top() + 8, rect.width() - 72, 24)
        font.setPointSize(10.5)
        painter.setFont(font)
        painter.setPen(
            QColor("#F8FAFC" if self.dark and not self.isChecked() else self.accent.name())
            if self.isChecked()
            else QColor("#F8FAFC" if self.dark else "#0F172A")
        )
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.title,
        )
        detail_font = QFont(self.font())
        detail_font.setPointSize(9.5)
        painter.setFont(detail_font)
        painter.setPen(QColor("#94A3B8" if self.dark else "#64748B"))
        painter.drawText(
            QRectF(60, rect.top() + 32, rect.width() - 72, 24),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.description,
        )


class CircularProgress(QWidget):
    def __init__(self, accent: str = "#2563EB", parent=None) -> None:
        super().__init__(parent)
        self.value = 0
        self.maximum = 1
        self.accent = QColor(accent)
        self.dark = False
        self.setFixedSize(132, 132)

    def setValue(self, value: int) -> None:
        self.value = value
        self.update()

    def setMaximum(self, maximum: int) -> None:
        self.maximum = max(1, maximum)
        self.update()

    def set_accent(self, accent: str) -> None:
        self.accent = QColor(accent)
        self.update()

    def set_theme(self, dark: bool, accent: str) -> None:
        self.dark = dark
        self.accent = QColor(accent)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        ring = QRectF(12, 12, 108, 108)
        painter.setPen(
            QPen(
                QColor("#334155" if self.dark else "#E2E8F0"),
                10,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawArc(ring, 0, 360 * 16)
        ratio = self.value / self.maximum
        painter.setPen(QPen(self.accent, 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(ring, 90 * 16, -round(360 * 16 * ratio))
        painter.setPen(QColor("#F8FAFC" if self.dark else "#0F172A"))
        font = QFont(self.font())
        font.setPointSize(17)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            f"{round(ratio * 100)}%",
        )
