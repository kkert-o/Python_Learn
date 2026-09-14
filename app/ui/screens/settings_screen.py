from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.settings import SettingsService
from app.ui.components import (
    AccentSwatch,
    ModernSlider,
    ThemeModeSwitch,
    ThemePreview,
    ToggleSwitch,
    WallpaperPreview,
)
from app.ui.components.wallpaper import load_wallpaper_image


class SettingsScreen(QWidget):
    appearance_changed = Signal(str, str, bool)
    wallpaper_changed = Signal(str, int)
    wallpaper_preview_changed = Signal(str, int)
    about_requested = Signal()

    ACCENTS = (
        ("蓝色", "#2563EB"),
        ("青绿色", "#0F9F8F"),
        ("橙色", "#EA580C"),
        ("紫色", "#7C3AED"),
        ("玫红", "#DB2777"),
    )

    def __init__(
        self,
        settings: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._dark = False
        self._accent = "#2563EB"

        self.theme_switch = ThemeModeSwitch()
        self.theme_switch.modeChanged.connect(self._theme_changed)
        self.accent_group = QButtonGroup(self)
        self.accent_group.setExclusive(True)
        self.accent_group.idClicked.connect(self._accent_clicked)

        title = QLabel("设置")
        title.setObjectName("pageTitle")
        subtitle = QLabel("主题、壁纸与界面效果会立即应用并保存。")
        subtitle.setObjectName("pageSubtitle")

        theme_panel = QFrame()
        theme_panel.setObjectName("settingsPanel")
        theme_layout = QVBoxLayout(theme_panel)
        theme_layout.setContentsMargins(20, 18, 20, 18)
        theme_layout.setSpacing(12)
        theme_title = QLabel("主题模式")
        theme_title.setObjectName("sectionTitle")
        theme_description = QLabel("浅色、深色或跟随 Windows 外观")
        theme_description.setObjectName("mutedText")
        theme_layout.addWidget(theme_title)
        theme_layout.addWidget(theme_description)
        theme_layout.addWidget(self.theme_switch)

        accent_title = QLabel("强调色")
        accent_title.setObjectName("sectionTitle")
        theme_layout.addSpacing(4)
        theme_layout.addWidget(accent_title)
        accent_row = QHBoxLayout()
        accent_row.setSpacing(8)
        for row, (label, value) in enumerate(self.ACCENTS):
            button = AccentSwatch(value)
            button.setToolTip(label)
            button.setCheckable(True)
            button.setProperty("accentValue", value)
            self.accent_group.addButton(button, row)
            accent_row.addWidget(button)
        accent_row.addStretch(1)
        theme_layout.addLayout(accent_row)

        self.glass_check = ToggleSwitch()
        self.glass_check.toggled.connect(self._emit_appearance)
        glass_row = QHBoxLayout()
        glass_copy = QVBoxLayout()
        glass_title = QLabel("毛玻璃背景")
        glass_title.setObjectName("progressRowTitle")
        glass_description = QLabel("侧边栏与卡片使用 Windows Acrylic")
        glass_description.setObjectName("mutedText")
        glass_copy.addWidget(glass_title)
        glass_copy.addWidget(glass_description)
        glass_row.addLayout(glass_copy, 1)
        glass_row.addWidget(self.glass_check)
        theme_layout.addSpacing(4)
        theme_layout.addLayout(glass_row)

        preview_panel = QFrame()
        preview_panel.setObjectName("settingsPanel")
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(18, 16, 18, 18)
        preview_layout.setSpacing(10)
        preview_title = QLabel("实时预览")
        preview_title.setObjectName("sectionTitle")
        self.theme_preview = ThemePreview()
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self.theme_preview, 1)

        top_row = QHBoxLayout()
        top_row.setSpacing(14)
        top_row.addWidget(theme_panel, 3)
        top_row.addWidget(preview_panel, 2)

        wallpaper_panel = QFrame()
        wallpaper_panel.setObjectName("settingsPanel")
        wallpaper_layout = QVBoxLayout(wallpaper_panel)
        wallpaper_layout.setContentsMargins(20, 18, 20, 18)
        wallpaper_layout.setSpacing(12)
        wallpaper_title = QLabel("壁纸")
        wallpaper_title.setObjectName("sectionTitle")
        wallpaper_description = QLabel("支持本地图片与拖放")
        wallpaper_description.setObjectName("mutedText")
        wallpaper_layout.addWidget(wallpaper_title)
        wallpaper_layout.addWidget(wallpaper_description)

        wallpaper_content = QHBoxLayout()
        wallpaper_content.setSpacing(18)
        self.wallpaper_preview = WallpaperPreview()
        self.wallpaper_preview.clicked.connect(self._choose_wallpaper)
        self.wallpaper_preview.fileDropped.connect(self.set_wallpaper)
        wallpaper_content.addWidget(self.wallpaper_preview, 3)

        wallpaper_controls = QVBoxLayout()
        wallpaper_controls.setSpacing(10)
        self.wallpaper_name = QLabel("未选择壁纸")
        self.wallpaper_name.setObjectName("progressRowTitle")
        self.wallpaper_name.setWordWrap(True)
        wallpaper_controls.addWidget(self.wallpaper_name)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        upload_button = QPushButton("选择图片")
        upload_button.setObjectName("primaryButton")
        upload_button.clicked.connect(self._choose_wallpaper)
        self.clear_wallpaper_button = QPushButton("移除")
        self.clear_wallpaper_button.clicked.connect(self.clear_wallpaper)
        button_row.addWidget(upload_button)
        button_row.addWidget(self.clear_wallpaper_button)
        button_row.addStretch(1)
        wallpaper_controls.addLayout(button_row)

        transparency_row = QHBoxLayout()
        transparency_label = QLabel("透明度")
        transparency_label.setObjectName("progressRowTitle")
        self.transparency_value = QLabel("35%")
        self.transparency_value.setObjectName("progressValue")
        self.transparency_value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.transparency_value.setFixedWidth(58)
        transparency_row.addWidget(transparency_label)
        transparency_row.addStretch(1)
        transparency_row.addWidget(self.transparency_value)
        wallpaper_controls.addLayout(transparency_row)

        self.transparency_slider = ModernSlider()
        self.transparency_slider.setRange(0, 90)
        self.transparency_slider.setValue(35)
        self.transparency_slider.setSingleStep(1)
        self.transparency_slider.setPageStep(5)
        self.transparency_slider.valueChanged.connect(
            self._transparency_changed
        )
        self.transparency_slider.sliderReleased.connect(
            self._persist_transparency
        )
        self._transparency_save_timer = QTimer(self)
        self._transparency_save_timer.setSingleShot(True)
        self._transparency_save_timer.setInterval(180)
        self._transparency_save_timer.timeout.connect(
            self._persist_transparency
        )
        wallpaper_controls.addWidget(self.transparency_slider)
        wallpaper_hint = QLabel("越大越透明，文字遮罩会自动适配")
        wallpaper_hint.setObjectName("mutedText")
        wallpaper_controls.addWidget(wallpaper_hint)
        wallpaper_controls.addStretch(1)
        wallpaper_content.addLayout(wallpaper_controls, 2)
        wallpaper_layout.addLayout(wallpaper_content)

        about = QFrame()
        about.setObjectName("settingsPanel")
        about_layout = QHBoxLayout(about)
        about_layout.setContentsMargins(20, 16, 20, 16)
        about_copy = QVBoxLayout()
        about_title = QLabel("关于与联系")
        about_title.setObjectName("progressRowTitle")
        about_text = QLabel("版本信息、抖音号和主页链接")
        about_text.setObjectName("mutedText")
        about_copy.addWidget(about_title)
        about_copy.addWidget(about_text)
        about_button = QPushButton("查看")
        about_button.clicked.connect(self.about_requested.emit)
        about_layout.addLayout(about_copy, 1)
        about_layout.addWidget(about_button)

        contents = QWidget()
        contents.setObjectName("settingsScrollContents")
        layout = QVBoxLayout(contents)
        layout.setContentsMargins(34, 28, 34, 32)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top_row)
        layout.addWidget(wallpaper_panel)
        layout.addWidget(about)
        layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(contents)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll)
        self.refresh()

    def refresh(self) -> None:
        theme = str(self.settings.get("theme_preference", "light"))
        accent = str(self.settings.get("accent_value", "#2563EB"))
        glass = bool(self.settings.get("glass_effect", True))
        wallpaper_path = str(self.settings.get("wallpaper_path", ""))
        transparency = int(self.settings.get("wallpaper_transparency", 35))

        self.theme_switch.set_mode(theme)
        selected_accent = next(
            (
                index
                for index, (_label, value) in enumerate(self.ACCENTS)
                if value.casefold() == accent.casefold()
            ),
            0,
        )
        self.accent_group.button(selected_accent).setChecked(True)
        self.glass_check.set_state(glass)
        self.transparency_slider.blockSignals(True)
        self.transparency_slider.setValue(transparency)
        self.transparency_slider.blockSignals(False)
        self.transparency_value.setText(f"{transparency}%")
        self._update_wallpaper_copy(wallpaper_path, transparency)
        self.theme_preview.set_theme(
            self._dark,
            accent,
            wallpaper_path,
            transparency,
        )

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = accent
        self.theme_switch.set_theme(dark, accent)
        self.glass_check.set_theme(dark, accent)
        for button in self.accent_group.buttons():
            if isinstance(button, AccentSwatch):
                button.set_theme(dark)
        self.wallpaper_preview.set_theme(dark, accent)
        self.transparency_slider.set_theme(dark, accent)
        self.theme_preview.set_theme(
            dark,
            accent,
            str(self.settings.get("wallpaper_path", "")),
            int(self.settings.get("wallpaper_transparency", 35)),
        )

    def set_wallpaper(self, path: str) -> None:
        candidate = str(path or "").strip()
        if candidate:
            image = load_wallpaper_image(candidate)
            if image.isNull():
                return
            candidate = str(Path(candidate).resolve())
        self.settings.set("wallpaper_path", candidate)
        transparency = self.transparency_slider.value()
        self._update_wallpaper_copy(candidate, transparency)
        self.wallpaper_changed.emit(candidate, transparency)

    def clear_wallpaper(self) -> None:
        self.settings.set("wallpaper_path", "")
        self._update_wallpaper_copy("", self.transparency_slider.value())
        self.wallpaper_changed.emit("", self.transparency_slider.value())

    def _choose_wallpaper(self) -> None:
        current = str(self.settings.get("wallpaper_path", ""))
        directory = str(Path(current).parent) if current else str(Path.home())
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择壁纸",
            directory,
            "图片 (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if path:
            self.set_wallpaper(path)

    def _theme_changed(self, mode: str) -> None:
        self.settings.set("theme_preference", mode)
        self._emit_appearance()

    def _accent_clicked(self, button_id: int) -> None:
        button = self.accent_group.button(button_id)
        if button is None:
            return
        self.settings.set(
            "accent_value",
            str(button.property("accentValue")),
        )
        self._emit_appearance()

    def _transparency_changed(self, value: int) -> None:
        transparency = max(0, min(90, int(value)))
        self.transparency_value.setText(f"{transparency}%")
        self._update_wallpaper_copy(
            str(self.settings.get("wallpaper_path", "")),
            transparency,
            update_theme_preview=False,
        )
        self.wallpaper_preview_changed.emit(
            str(self.settings.get("wallpaper_path", "")),
            transparency,
        )
        self._transparency_save_timer.start()

    def _persist_transparency(self) -> None:
        self._transparency_save_timer.stop()
        transparency = max(0, min(90, self.transparency_slider.value()))
        path = str(self.settings.get("wallpaper_path", ""))
        if int(self.settings.get("wallpaper_transparency", 35)) != transparency:
            self.settings.set("wallpaper_transparency", transparency)
        self._update_wallpaper_copy(path, transparency)
        self.wallpaper_changed.emit(path, transparency)

    def _update_wallpaper_copy(
        self,
        path: str,
        transparency: int,
        *,
        update_theme_preview: bool = True,
    ) -> None:
        wallpaper = Path(path) if path else None
        name = wallpaper.name if wallpaper is not None else "未选择壁纸"
        self.wallpaper_name.setText(name)
        self.wallpaper_name.setToolTip(path)
        self.clear_wallpaper_button.setEnabled(bool(path))
        accent = str(self.settings.get("accent_value", "#2563EB"))
        self.wallpaper_preview.set_wallpaper(
            path,
            transparency,
            dark=self._dark,
            accent=accent,
        )
        if update_theme_preview:
            self.theme_preview.set_theme(
                self._dark,
                accent,
                path,
                transparency,
            )

    def _emit_appearance(self) -> None:
        glass = self.glass_check.isChecked()
        self.settings.set("glass_effect", glass)
        self.appearance_changed.emit(
            str(self.settings.get("theme_preference", "light")),
            str(self.settings.get("accent_value", "#2563EB")),
            glass,
        )
