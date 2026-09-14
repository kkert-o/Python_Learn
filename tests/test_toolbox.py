from __future__ import annotations

from PySide6.QtWidgets import QApplication, QToolButton

from app.bootstrap import bootstrap
from app.services.settings import SettingsService
from app.toolbox import (
    EngineeringCatalog,
    ErrorMuseumCatalog,
    GlobalSearchEngine,
    LibraryCatalog,
    LibraryCategory,
    SearchResultKind,
)
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


def test_toolbox_catalogs_and_search(app_paths) -> None:
    context = bootstrap(app_paths)
    assert len(LibraryCatalog.all) == 15
    assert len(ErrorMuseumCatalog.all) == 8
    assert len(EngineeringCatalog.all) == 4

    library_results = LibraryCatalog.search("HTTP")
    assert {entry.library_id for entry in library_results} >= {
        "requests",
        "httpx",
    }
    assert len(LibraryCatalog.search("", LibraryCategory.NETWORK)) == 3
    assert ErrorMuseumCatalog.search("NameError")[0].error_id == "name-error"

    project_results = GlobalSearchEngine.search(
        "猜数字",
        context.content,
        context.training_catalog,
        context.project_catalog,
    )
    assert any(result.kind is SearchResultKind.PROJECT for result in project_results)
    library = GlobalSearchEngine.search(
        "pytest",
        context.content,
        context.training_catalog,
        context.project_catalog,
    )
    assert any(result.kind is SearchResultKind.LIBRARY for result in library)


def test_toolbox_ui_favorites_and_navigation(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_TOOLBOX)
    app.processEvents()
    assert window.toolbox_screen.tabs.count() == 4
    assert window.toolbox_screen.library_count.text() == "15 个第三方库"
    window.toolbox_screen.library_category.setCurrentIndex(1)
    app.processEvents()
    assert window.toolbox_screen.library_count.text() == "3 个第三方库"
    window.toolbox_screen.library_category.setCurrentIndex(0)
    app.processEvents()
    header = window.toolbox_screen.findChild(QToolButton, "libraryHeader")
    assert header is not None
    header.click()
    assert window.toolbox_screen.expanded_library_ids

    window.toolbox_screen._toggle_favorite("lesson:python")
    assert "lesson:python" in window.toolbox_screen.settings.get("favorites", [])
    reloaded_settings = SettingsService(app_paths.settings_path)
    assert "lesson:python" in reloaded_settings.get("favorites", [])

    result = next(
        result
        for result in GlobalSearchEngine.search(
            "猜数字",
            context.content,
            context.training_catalog,
            context.project_catalog,
        )
        if result.kind is SearchResultKind.PROJECT
    )
    window.toolbox_screen._open_result(result)
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_PROJECT_DETAIL
    window.close()
