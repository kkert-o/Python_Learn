from __future__ import annotations

from PySide6.QtWidgets import QApplication

from app.bootstrap import bootstrap
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme
from app.workspace import FileManager, ProjectManager


def test_project_templates(tmp_path) -> None:
    manager = ProjectManager()
    blank = manager.create_project(tmp_path, "blank", template="blank")
    basic = manager.create_project(tmp_path, "basic", template="basic")
    quality = manager.create_project(tmp_path, "quality", template="quality")
    assert FileManager.read_text(blank / "main.py").text == ""
    assert "Hello Python" in FileManager.read_text(basic / "main.py").text
    assert (quality / "tests" / "test_main.py").exists()
    assert (quality / "requirements-dev.txt").exists()


def test_free_project_ui_refreshes_recent(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_FREE_PROJECTS)
    app.processEvents()
    window.free_project_screen.name_input.setText("我的自由项目")
    window.free_project_screen.parent_input.setText(str(app_paths.projects_dir))
    window.free_project_screen._create_project()
    app.processEvents()
    assert window.pages.currentIndex() == window.PAGE_WORKBENCH
    assert window.workbench.current_project is not None
    assert window.workbench.current_project.name == "我的自由项目"
    window.close()


def test_graduation_milestones_workspace_and_completion(app_paths) -> None:
    context = bootstrap(app_paths)
    project = context.project_catalog.by_id("graduation-project")
    assert project is not None
    repository = context.progress_repository
    keys = (
        "requirements",
        "design",
        "mvp",
        "testing",
        "security",
        "documentation",
        "release",
    )
    for key in keys:
        repository.set_graduation_milestone(
            project.project_id,
            key,
            True,
        )
    states = repository.graduation_milestones(project.project_id)
    assert all(states[key] for key in keys)

    root = context.project_workspace.ensure(project)
    (root / "src").mkdir(exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)


def test_graduation_ui_checks_milestones(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_GRADUATION)
    app.processEvents()
    assert len(window.graduation_project_screen.checkboxes) == 7
    for checkbox in window.graduation_project_screen.checkboxes.values():
        checkbox.setChecked(True)
    app.processEvents()
    states = context.progress_repository.graduation_milestones(
        "graduation-project"
    )
    assert len(states) == 7
    assert all(states.values())
    assert (
        "graduation-project"
        in context.progress_repository.completed_project_ids()
    )
    window.close()

