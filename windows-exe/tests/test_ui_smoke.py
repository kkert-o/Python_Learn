from __future__ import annotations

import os

import pytest
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication, QLabel

from app.bootstrap import bootstrap
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme
from app.ui.window_effects import set_windows_app_user_model_id


def test_main_window_smoke_test(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    assert window.pages.count() == 16
    assert window.home_screen.content.lesson_count == 56
    assert window.navigation.count() == 13
    assert window.navigation.minimumHeight() == 13 * 42 + 4
    sidebar_text = "\n".join(
        label.text() for label in window.findChildren(QLabel)
    )
    assert "数据目录" not in sidebar_text
    assert window.workbench.runner.state.value == "IDLE"
    assert not window.windowIcon().isNull()
    assert window.smooth_scroll_filter is not None
    window._open_workbench()
    app.processEvents()
    editor = window.workbench.current_editor()
    assert editor is not None
    assert editor.file_path is not None
    assert editor.file_path.name == "main.py"
    assert editor.highlighter is not None
    window.workbench.font_size_spin.setValue(14)
    assert editor.font().pointSize() == 14
    assert context.settings.get("workbench_font_size") == 14
    window.close()


@pytest.mark.skipif(os.name != "nt", reason="Windows taskbar only")
def test_windows_app_user_model_id_is_set() -> None:
    assert set_windows_app_user_model_id("PythonLearner.Desktop.Test")


def test_navigation_does_not_show_transient_top_level_widgets(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()
    unexpected: list[str] = []

    class Watcher(QObject):
        def eventFilter(self, watched, event) -> bool:  # type: ignore[no-untyped-def]
            if (
                event.type() == QEvent.Type.Show
                and hasattr(watched, "isWindow")
                and watched.isWindow()
                and watched is not window
                and type(watched).__name__ == "QWidget"
            ):
                unexpected.append(watched.objectName())
            return False

    watcher = Watcher()
    app.installEventFilter(watcher)
    try:
        for page in (
            window.PAGE_COURSE,
            window.PAGE_PRACTICE,
            window.PAGE_TRAINING,
            window.PAGE_PROJECTS,
            window.PAGE_TOOLBOX,
            window.PAGE_AI_TEACHER,
            window.PAGE_CRAWLER_LAB,
            window.PAGE_FREE_PROJECTS,
            window.PAGE_GRADUATION,
            window.PAGE_LEARNING_HUB,
            window.PAGE_SETTINGS,
        ):
            window.navigate(page)
            app.processEvents()
            app.sendPostedEvents()
            app.processEvents()
    finally:
        app.removeEventFilter(watcher)
        window.close()
    assert unexpected == []


def test_navigation_has_icons_and_settings_applies_theme(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    assert window.navigation.itemText(0) == "首页"
    assert window.navigation.itemText(window.navigation.count() - 1) == "设置"
    window.navigate(window.PAGE_SETTINGS)
    app.processEvents()
    window.settings_screen.theme_switch.button("dark").click()
    window.settings_screen.accent_group.button(1).click()
    app.processEvents()
    assert context.settings.get("theme_preference") == "dark"
    assert context.settings.get("accent_value") == "#0F9F8F"
    assert "#0f9f8f" in app.styleSheet().casefold()
    window.settings_screen.glass_check.setChecked(False)
    assert context.settings.get("glass_effect") is False
    wallpaper = app_paths.local_data_root / "wallpaper.png"
    image = QImage(32, 20, QImage.Format.Format_ARGB32)
    image.fill(QColor("#0F9F8F"))
    assert image.save(str(wallpaper))
    window.settings_screen.set_wallpaper(str(wallpaper))
    window.settings_screen.transparency_slider.setValue(48)
    assert context.settings.get("wallpaper_transparency") == 35
    window.settings_screen._persist_transparency()
    app.processEvents()
    assert context.settings.get("wallpaper_path") == str(wallpaper.resolve())
    assert context.settings.get("wallpaper_transparency") == 48
    assert not window.root_surface.image.isNull()
    assert "rgba(8, 15, 28" in app.styleSheet()
    window.settings_screen.clear_wallpaper()
    assert context.settings.get("wallpaper_path") == ""
    about = window._about_html()
    assert "62868461635" in about
    assert "https://v.douyin.com/wA4Df70HOgE/" in about
    assert "3@7.com" not in about
    window.close()
