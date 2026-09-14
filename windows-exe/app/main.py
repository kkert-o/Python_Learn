from __future__ import annotations

import sys
import traceback

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.bootstrap import bootstrap
from app.config import APP_DISPLAY_NAME, APP_VERSION, ORGANIZATION_NAME
from app.runtime.worker import main as worker_main
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme
from app.ui.window_effects import set_windows_app_user_model_id


def _run_worker_if_requested() -> int | None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--run-worker":
        return worker_main([sys.argv[2]])
    return None


def main() -> int:
    worker_exit = _run_worker_if_requested()
    if worker_exit is not None:
        return worker_exit

    set_windows_app_user_model_id("PythonLearner.Desktop.1.1.0.16")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_DISPLAY_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setDesktopFileName("PythonLearner")
    try:
        context = bootstrap()
        icon_path = context.paths.resource_root / "assets" / "app-icon.ico"
        png_icon_path = context.paths.resource_root / "assets" / "app-icon.png"
        if not icon_path.exists():
            icon_path = png_icon_path
        icon = QIcon(str(icon_path))
        if png_icon_path.exists():
            icon.addFile(str(png_icon_path))
        app.setWindowIcon(icon)
        apply_theme(
            app,
            str(context.settings.get("theme_preference", "light")),
            str(context.settings.get("accent_value", "#2563EB")),
            bool(context.settings.get("glass_effect", True)),
        )
        window = MainWindow(context)
        window.show()
        return app.exec()
    except BaseException as exc:
        traceback.print_exc()
        QMessageBox.critical(
            None,
            "Python 学习器启动失败",
            f"程序无法启动：\n{exc}",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
