from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme
from app.workspace import FileManager


def test_project_catalog_contains_all_levels(app_paths) -> None:
    context = bootstrap(app_paths)
    catalog = context.project_catalog
    assert len(catalog.all) == 13
    assert len(catalog.levels) == 6
    graduation = catalog.by_id("graduation-project")
    assert graduation is not None
    assert len(graduation.requirements) == 7
    assert len(graduation.hints) >= 3
    assert graduation.starter.strip()


def test_project_workspace_keeps_user_code(app_paths) -> None:
    context = bootstrap(app_paths)
    project = context.project_catalog.by_id("guess")
    assert project is not None
    root = context.project_workspace.ensure(project)
    main_path = root / "main.py"
    assert main_path.exists()
    user_code = 'print("my working code")\n'
    FileManager.write_text(main_path, user_code)
    context.project_workspace.ensure(project)
    assert FileManager.read_text(main_path).text == user_code
    assert "验收要求" in FileManager.read_text(root / "README.md").text


def test_project_completion_persists(app_paths) -> None:
    context = bootstrap(app_paths)
    repository = context.progress_repository
    repository.complete_project("guess")
    assert "guess" in repository.completed_project_ids()
    reloaded = bootstrap(app_paths)
    assert "guess" in reloaded.progress_repository.completed_project_ids()


def test_project_ui_and_workbench_flow(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_PROJECTS)
    app.processEvents()
    assert len(window.project_list_screen.catalog.all) == 13
    window._open_project_detail("guess")
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_PROJECT_DETAIL
    assert window.project_detail_screen.project is not None

    window.project_detail_screen._complete_project()
    assert "guess" in context.progress_repository.completed_project_ids()

    window._open_project_workspace("guess")
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_WORKBENCH
    assert window.workbench.current_project is not None
    editor = window.workbench.current_editor()
    assert editor is not None
    assert editor.file_path is not None
    assert editor.file_path.name == "main.py"
    window.close()
