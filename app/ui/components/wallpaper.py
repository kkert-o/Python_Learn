from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QImage,
    QImageReader,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QSizePolicy, QWidget
import qtawesome as qta


def load_wallpaper_image(path: str | Path) -> QImage:
    if not path:
        return QImage()
    image_path = Path(path)
    if not image_path.is_file():
        return QImage()
    reader = QImageReader(str(image_path))
    reader.setAutoTransform(True)
    image = reader.read()
    return image if not image.isNull() else QImage()


def cover_source_rect(image: QImage, target_size: QSize) -> QRectF:
    if image.isNull() or target_size.width() <= 0 or target_size.height() <= 0:
        return QRectF()
    image_ratio = image.width() / image.height()
    target_ratio = target_size.width() / target_size.height()
    if image_ratio > target_ratio:
        source_width = image.height() * target_ratio
        return QRectF(
            (image.width() - source_width) / 2,
            0,
            source_width,
            image.height(),
        )
    source_height = image.width() / target_ratio
    return QRectF(
        0,
        (image.height() - source_height) / 2,
        image.width(),
        source_height,
    )


class WallpaperBackground(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = ""
        self._image = QImage()
        self._render_cache = QImage()
        self._render_size = QSize()
        self._transparency = 35
        self._dark = False
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

    @property
    def image(self) -> QImage:
        return self._image

    @property
    def wallpaper_path(self) -> str:
        return self._path

    def set_wallpaper(
        self,
        path: str,
        transparency: int = 35,
        *,
        dark: bool = False,
    ) -> None:
        next_path = str(path or "")
        if next_path != self._path:
            self._path = next_path
            self._image = load_wallpaper_image(self._path)
            self._render_cache = QImage()
            self._render_size = QSize()
        self._transparency = max(0, min(90, int(transparency)))
        self._dark = dark
        self.update()

    def set_theme(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        base = QColor("#0F172A" if self._dark else "#F8FAFC")
        painter.fillRect(self.rect(), base)
        if self._image.isNull():
            return

        if self._render_cache.size() != self.size():
            self._render_cache = self._build_render_cache()
            self._render_size = self.size()
        if self._render_cache.isNull():
            return
        visible = 1.0 - self._transparency / 100.0
        painter.setOpacity(max(0.08, min(0.95, visible)))
        painter.drawImage(QRectF(self.rect()), self._render_cache)
        painter.setOpacity(1.0)
        scrim = QColor(8, 15, 28, 132) if self._dark else QColor(248, 250, 252, 122)
        painter.fillRect(self.rect(), scrim)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self._render_cache = QImage()
        self._render_size = QSize()
        super().resizeEvent(event)

    def _build_render_cache(self) -> QImage:
        if self._image.isNull() or self.size().isEmpty():
            return QImage()
        rendered = QImage(
            self.size(),
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        rendered.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rendered)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawImage(
            QRectF(rendered.rect()),
            self._image,
            cover_source_rect(self._image, self.size()),
        )
        painter.end()
        return rendered


class WallpaperPreview(QWidget):
    clicked = Signal()
    fileDropped = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path = ""
        self._image = QImage()
        self._transparency = 35
        self._dark = False
        self._accent = QColor("#2563EB")
        self._hover_progress = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(160)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_hover_progress)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(330, 168)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

    def sizeHint(self) -> QSize:
        return QSize(430, 180)

    def set_wallpaper(
        self,
        path: str,
        transparency: int,
        *,
        dark: bool,
        accent: str,
    ) -> None:
        next_path = str(path or "")
        if next_path != self._path:
            self._path = next_path
            self._image = load_wallpaper_image(self._path)
        self._transparency = max(0, min(90, int(transparency)))
        self._dark = dark
        self._accent = QColor(accent)
        self.update()

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = QColor(accent)
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

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        for url in event.mimeData().urls():
            if url.isLocalFile():
                self.fileDropped.emit(url.toLocalFile())
                event.acceptProposedAction()
                return
        event.ignore()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)

        painter.save()
        painter.setClipPath(path)
        base = QColor("#111827" if self._dark else "#FFFFFF")
        painter.fillRect(rect, base)
        if not self._image.isNull():
            visible = 0.55 + (1.0 - self._transparency / 100.0) * 0.45
            painter.setOpacity(visible)
            painter.drawImage(
                rect,
                self._image,
                cover_source_rect(self._image, self.size()),
            )
            painter.setOpacity(1.0)
            overlay = (
                QColor(8, 15, 28, 118)
                if self._dark
                else QColor(255, 255, 255, 106)
            )
            painter.fillRect(rect, overlay)
        else:
            tint = QColor(self._accent)
            tint.setAlpha(24 if self._dark else 16)
            painter.fillRect(rect, tint)
        painter.restore()

        border = QColor(self._accent)
        border.setAlpha(
            round(
                120
                + 110 * self._hover_progress
                + (35 if not self._image.isNull() else 0)
            )
        )
        pen = QPen(border, 1.8, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 12, 12)

        text_color = QColor("#F8FAFC" if self._dark else "#0F172A")
        muted = QColor("#B7C3D2" if self._dark else "#52657A")
        icon_color = self._accent.name()
        icon = qta.icon(
            "fa5s.image" if self._image.isNull() else "fa5s.check-circle",
            color=icon_color,
        )
        icon.paint(
            painter,
            int(rect.center().x() - 18),
            int(rect.top() + 34),
            36,
            36,
        )

        if self._image.isNull():
            title = "点击或拖入壁纸"
            detail = "PNG、JPG、BMP、WEBP"
        else:
            title = Path(self._path).name or "当前壁纸"
            detail = f"{self._image.width()} x {self._image.height()}"

        title_font = painter.font()
        title_font.setPointSize(11)
        title_font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(title_font)
        painter.setPen(text_color)
        painter.drawText(
            QRectF(rect.left() + 22, rect.top() + 82, rect.width() - 44, 26),
            Qt.AlignmentFlag.AlignCenter,
            title,
        )
        detail_font = painter.font()
        detail_font.setPointSize(9.5)
        detail_font.setWeight(QFont.Weight.Normal)
        painter.setFont(detail_font)
        painter.setPen(muted)
        painter.drawText(
            QRectF(rect.left() + 22, rect.top() + 109, rect.width() - 44, 24),
            Qt.AlignmentFlag.AlignCenter,
            detail,
        )
