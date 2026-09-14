from __future__ import annotations

from PySide6.QtCore import (
    QByteArray,
    QTimer,
    Qt,
)
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.bootstrap import AppContext
from app.ui.screens import (
    AiTeacherScreen,
    CourseScreen,
    CrawlerLabScreen,
    FreeProjectScreen,
    GraduationProjectScreen,
    HomeScreen,
    LearningHubScreen,
    LessonScreen,
    PracticeScreen,
    ProjectDetailScreen,
    ProjectListScreen,
    PythonWorkbench,
    SettingsScreen,
    TrainingCenterScreen,
    TrainingSessionScreen,
    ToolboxScreen,
)
from app.training import TrainingExercise, TrainingType
from app.ui.components import SidebarNavigation, WallpaperBackground
from app.ui.smooth_scroll import SmoothScrollFilter
from app.ui.theme import apply_theme, is_dark_application
from app.ui.window_effects import (
    apply_windows_backdrop,
    destroy_windows_icon,
    set_windows_window_icon,
)


class MainWindow(QMainWindow):
    PAGE_HOME = 0
    PAGE_COURSE = 1
    PAGE_PRACTICE = 2
    PAGE_TRAINING = 3
    PAGE_PROJECTS = 4
    PAGE_TOOLBOX = 5
    PAGE_AI_TEACHER = 6
    PAGE_CRAWLER_LAB = 7
    PAGE_FREE_PROJECTS = 8
    PAGE_GRADUATION = 9
    PAGE_WORKBENCH = 10
    PAGE_LEARNING_HUB = 11
    PAGE_LESSON = 12
    PAGE_TRAINING_SESSION = 13
    PAGE_PROJECT_DETAIL = 14
    PAGE_SETTINGS = 15

    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self._native_icon_handles: list[int] = []
        self.setWindowTitle("Python 学习器")
        icon_path = context.paths.resource_root / "assets" / "app-icon.png"
        ico_path = context.paths.resource_root / "assets" / "app-icon.ico"
        if ico_path.exists():
            icon_path = ico_path
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            png_path = context.paths.resource_root / "assets" / "app-icon.png"
            if png_path.exists():
                icon.addFile(str(png_path))
            self.setWindowIcon(icon)
        self.setMinimumSize(1100, 700)
        self.resize(1440, 900)

        self.home_screen = HomeScreen(
            context.content,
            context.course_catalog,
            context.progress_repository,
            context.workspace_repository,
        )
        self.course_screen = CourseScreen(
            context.course_catalog,
            context.progress_repository,
        )
        self.practice_screen = PracticeScreen(
            context.course_catalog,
            context.progress_repository,
        )
        self.training_center_screen = TrainingCenterScreen(
            context.training_catalog,
            context.progress_repository,
        )
        self.project_list_screen = ProjectListScreen(
            context.project_catalog,
            context.progress_repository,
        )
        self.toolbox_screen = ToolboxScreen(
            context.content,
            context.training_catalog,
            context.project_catalog,
            context.settings,
        )
        self.ai_teacher_screen = AiTeacherScreen(
            context.paths,
            context.settings,
        )
        self.crawler_lab_screen = CrawlerLabScreen(context.settings)
        self.free_project_screen = FreeProjectScreen(
            context.paths,
            context.workspace_repository,
        )
        self.graduation_project_screen = GraduationProjectScreen(context)
        self.settings_screen = SettingsScreen(context.settings)
        self.workbench = PythonWorkbench(
            context.paths,
            context.content,
            context.workspace_repository,
            context.settings,
        )
        self.learning_hub_screen = LearningHubScreen(
            context.course_catalog,
            context.progress_repository,
        )
        self.lesson_screen = LessonScreen(
            context.course_catalog,
            context.progress_repository,
        )
        self.training_session_screen = TrainingSessionScreen(
            context.paths,
            context.progress_repository,
        )
        self.project_detail_screen = ProjectDetailScreen(
            context.project_catalog,
            context.progress_repository,
        )
        self.home_screen.open_workbench_requested.connect(
            self._open_workbench
        )
        self.home_screen.open_project_requested.connect(self._open_project)
        self.home_screen.continue_learning_requested.connect(self._open_lesson)
        self.course_screen.lesson_requested.connect(self._open_lesson)
        self.course_screen.practice_requested.connect(
            lambda: self.navigate(self.PAGE_PRACTICE)
        )
        self.course_screen.learning_hub_requested.connect(
            lambda: self.navigate(self.PAGE_LEARNING_HUB)
        )
        self.practice_screen.back_requested.connect(
            lambda: self.navigate(self.PAGE_COURSE)
        )
        self.practice_screen.lesson_requested.connect(self._open_lesson)
        self.practice_screen.progress_changed.connect(self._refresh_learning_views)
        self.learning_hub_screen.back_requested.connect(
            lambda: self.navigate(self.PAGE_COURSE)
        )
        self.learning_hub_screen.lesson_requested.connect(self._open_lesson)
        self.lesson_screen.back_requested.connect(
            lambda: self.navigate(self.PAGE_COURSE)
        )
        self.lesson_screen.lesson_requested.connect(self._open_lesson)
        self.lesson_screen.workbench_requested.connect(self._open_snippet)
        self.lesson_screen.progress_changed.connect(self._refresh_learning_views)
        self.training_center_screen.start_type_requested.connect(
            self._start_training_type
        )
        self.training_center_screen.review_requested.connect(
            self._start_training_review
        )
        self.training_session_screen.back_requested.connect(
            lambda: self.navigate(self.PAGE_TRAINING)
        )
        self.training_session_screen.workbench_requested.connect(
            self._open_snippet
        )
        self.training_session_screen.progress_changed.connect(
            self._refresh_training_views
        )
        self.project_list_screen.project_requested.connect(
            self._open_project_detail
        )
        self.project_detail_screen.back_requested.connect(
            lambda: self.navigate(self.PAGE_PROJECTS)
        )
        self.project_detail_screen.workbench_requested.connect(
            self._open_project_workspace
        )
        self.project_detail_screen.progress_changed.connect(
            self._refresh_project_views
        )
        self.toolbox_screen.lesson_requested.connect(self._open_lesson)
        self.toolbox_screen.project_requested.connect(self._open_project_detail)
        self.toolbox_screen.training_requested.connect(
            self._open_training_by_id
        )
        self.toolbox_screen.workbench_requested.connect(self._open_snippet)
        self.crawler_lab_screen.workbench_requested.connect(self._open_snippet)
        self.free_project_screen.open_workbench_requested.connect(
            self._open_workbench_project
        )
        self.graduation_project_screen.workbench_requested.connect(
            self._open_workbench_project
        )
        self.graduation_project_screen.progress_changed.connect(
            self._refresh_project_views
        )
        self.settings_screen.appearance_changed.connect(
            self._apply_appearance
        )
        self.settings_screen.wallpaper_changed.connect(
            self._apply_wallpaper
        )
        self.settings_screen.wallpaper_preview_changed.connect(
            self._preview_wallpaper
        )
        self.settings_screen.about_requested.connect(self._show_about)
        self.workbench.status_message.connect(self._show_status)

        self.navigation = SidebarNavigation()
        self.navigation.setObjectName("navigation")
        self.navigation.setFixedWidth(228)
        nav_entries = (
            ("首页", "fa5s.home", self.PAGE_HOME),
            ("课程", "fa5s.book-open", self.PAGE_COURSE),
            ("练习", "fa5s.edit", self.PAGE_PRACTICE),
            ("专项训练", "fa5s.dumbbell", self.PAGE_TRAINING),
            ("项目", "fa5s.folder-open", self.PAGE_PROJECTS),
            ("资料库", "fa5s.database", self.PAGE_TOOLBOX),
            ("AI 老师", "fa5s.robot", self.PAGE_AI_TEACHER),
            ("爬虫实验室", "fa5s.spider", self.PAGE_CRAWLER_LAB),
            ("自由项目", "fa5s.folder-plus", self.PAGE_FREE_PROJECTS),
            ("毕业项目", "fa5s.graduation-cap", self.PAGE_GRADUATION),
            ("Python 工作台", "fa5s.terminal", self.PAGE_WORKBENCH),
            ("学习中心", "fa5s.chart-line", self.PAGE_LEARNING_HUB),
            ("设置", "fa5s.cog", self.PAGE_SETTINGS),
        )
        self._navigation_pages = [page for _label, _icon, page in nav_entries]
        for label, icon_name, _page in nav_entries:
            self.navigation.addItem(label, icon_name)
        navigation_height = self.navigation.count() * 42 + 4
        self.navigation.setFixedHeight(navigation_height)
        self.navigation.currentRowChanged.connect(self._navigation_changed)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.home_screen)
        self.pages.addWidget(self.course_screen)
        self.pages.addWidget(self.practice_screen)
        self.pages.addWidget(self.training_center_screen)
        self.pages.addWidget(self.project_list_screen)
        self.pages.addWidget(self.toolbox_screen)
        self.pages.addWidget(self.ai_teacher_screen)
        self.pages.addWidget(self.crawler_lab_screen)
        self.pages.addWidget(self.free_project_screen)
        self.pages.addWidget(self.graduation_project_screen)
        self.pages.addWidget(self.workbench)
        self.pages.addWidget(self.learning_hub_screen)
        self.pages.addWidget(self.lesson_screen)
        self.pages.addWidget(self.training_session_screen)
        self.pages.addWidget(self.project_detail_screen)
        self.pages.addWidget(self.settings_screen)

        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 22, 18, 18)
        sidebar_layout.setSpacing(6)
        brand = QLabel("Python 学习器")
        brand.setObjectName("brandTitle")
        brand_subtitle = QLabel("Windows EXE · V1.1")
        brand_subtitle.setObjectName("brandSubtitle")
        brand_icon = QLabel()
        brand_icon.setObjectName("brandMark")
        brand_icon.setFixedSize(42, 42)
        brand_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_icon_path = context.paths.resource_root / "assets" / "app-icon.ico"
        if not brand_icon_path.exists():
            brand_icon_path = context.paths.resource_root / "assets" / "app-icon.png"
        brand_icon.setPixmap(QIcon(str(brand_icon_path)).pixmap(38, 38))
        brand_copy = QVBoxLayout()
        brand_copy.setSpacing(0)
        brand_copy.addWidget(brand)
        brand_copy.addWidget(brand_subtitle)
        brand_row = QHBoxLayout()
        brand_row.setSpacing(9)
        brand_row.addWidget(brand_icon)
        brand_row.addLayout(brand_copy, 1)
        sidebar_layout.addLayout(brand_row)
        sidebar_layout.addSpacing(18)
        sidebar_layout.addWidget(self.navigation)
        sidebar_layout.addStretch(1)

        root = WallpaperBackground()
        root.setObjectName("appRoot")
        self.root_surface = root
        self.content_panel = QWidget()
        self.content_panel.setObjectName("contentPanel")
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.pages)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.content_panel, 1)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        app = QApplication.instance()
        self.smooth_scroll_filter = SmoothScrollFilter(self)
        if app is not None:
            app.installEventFilter(self.smooth_scroll_filter)
        self._apply_current_appearance()
        self._restore_window_state()
        self.navigation.setCurrentRow(0)

    def _show_about(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle("关于 Python 学习器")
        box.setIcon(QMessageBox.Icon.Information)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(self._about_html())
        box.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        box.exec()

    @staticmethod
    def _about_html() -> str:
        return (
            "<h3>Python 学习器 V1.1</h3>"
            "<p>课程、训练、项目、AI 老师与独立 Python 工作台。</p>"
            "<p><b>抖音号：</b>62868461635<br>"
            "<b>主页：</b><a href=\"https://v.douyin.com/wA4Df70HOgE/\">"
            "https://v.douyin.com/wA4Df70HOgE/</a></p>"
        )

    def navigate(self, page_index: int) -> None:
        if page_index < 0 or page_index >= self.pages.count():
            return
        self.pages.setCurrentIndex(page_index)
        if page_index in self._navigation_pages:
            row = self._navigation_pages.index(page_index)
            if self.navigation.currentRow() != row:
                self.navigation.setCurrentRow(row)
        if page_index == self.PAGE_HOME:
            self.home_screen.refresh()
        elif page_index == self.PAGE_COURSE:
            self.course_screen.refresh()
        elif page_index == self.PAGE_PRACTICE:
            self.practice_screen.start()
        elif page_index == self.PAGE_TRAINING:
            self.training_center_screen.refresh()
        elif page_index == self.PAGE_PROJECTS:
            self.project_list_screen.refresh()
        elif page_index == self.PAGE_TOOLBOX:
            self.toolbox_screen.refresh()
        elif page_index == self.PAGE_LEARNING_HUB:
            self.learning_hub_screen.refresh()
        elif page_index == self.PAGE_FREE_PROJECTS:
            self.free_project_screen.refresh()
        elif page_index == self.PAGE_GRADUATION:
            self.graduation_project_screen.refresh()

    def _navigation_changed(self, row: int) -> None:
        if 0 <= row < len(self._navigation_pages):
            page = self._navigation_pages[row]
            if page == self.PAGE_WORKBENCH:
                self.workbench.ensure_ready()
            self.navigate(page)

    def _open_workbench(self) -> None:
        self.workbench.ensure_ready()
        self.navigate(self.PAGE_WORKBENCH)

    def _open_project(self, path: str) -> None:
        self.navigate(self.PAGE_WORKBENCH)
        self.workbench.open_project(path)

    def _open_lesson(self, lesson_id: str) -> None:
        self.lesson_screen.show_lesson(lesson_id)
        self.pages.setCurrentIndex(self.PAGE_LESSON)

    def _open_snippet(self, title: str, code: str) -> None:
        self.navigate(self.PAGE_WORKBENCH)
        self.workbench.open_code_snippet(title, code)

    def _open_project_detail(self, project_id: str) -> None:
        self.project_detail_screen.show_project(project_id)
        self.pages.setCurrentIndex(self.PAGE_PROJECT_DETAIL)

    def _open_project_workspace(self, project_id: str) -> None:
        project = self.context.project_catalog.by_id(project_id)
        if project is None:
            return
        project_root = self.context.project_workspace.ensure(project)
        self.navigate(self.PAGE_WORKBENCH)
        self.workbench.open_project(project_root)

    def _open_workbench_project(self, path: str) -> None:
        self.navigate(self.PAGE_WORKBENCH)
        self.workbench.open_project(path)

    def _start_training_type(self, training_type: TrainingType) -> None:
        exercises = self.context.training_catalog.by_type(training_type)
        self._start_training_session(exercises, training_type.label)

    def _start_training_review(self) -> None:
        exercise_ids = self.context.progress_repository.training_needs_review_ids()
        exercises = self.context.training_catalog.by_ids(exercise_ids)
        self._start_training_session(exercises, "错题复习")

    def _open_training_by_id(self, exercise_id: str) -> None:
        exercise = self.context.training_catalog.by_id(exercise_id)
        if exercise is None:
            return
        self._start_training_session([exercise], exercise.type.label)

    def _start_training_session(
        self,
        exercises: list[TrainingExercise],
        title: str,
    ) -> None:
        self.training_session_screen.start_session(exercises, title)
        self.pages.setCurrentIndex(self.PAGE_TRAINING_SESSION)

    def _refresh_learning_views(self) -> None:
        self.home_screen.refresh()
        self.course_screen.refresh()
        self.learning_hub_screen.refresh()

    def _refresh_training_views(self) -> None:
        self.training_center_screen.refresh()
        self.learning_hub_screen.refresh()

    def _refresh_project_views(self) -> None:
        self.project_list_screen.refresh()
        self.home_screen.refresh()
        self.learning_hub_screen.refresh()

    def _show_status(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)

    def _apply_current_appearance(self) -> None:
        wallpaper_path = str(
            self.context.settings.get("wallpaper_path", "")
        )
        wallpaper_transparency = int(
            self.context.settings.get("wallpaper_transparency", 35)
        )
        self._apply_appearance(
            str(self.context.settings.get("theme_preference", "light")),
            str(self.context.settings.get("accent_value", "#2563EB")),
            bool(self.context.settings.get("glass_effect", True)),
        )
        self._apply_wallpaper(
            wallpaper_path,
            wallpaper_transparency,
        )

    def _apply_appearance(
        self,
        preference: str,
        accent: str,
        glass: bool,
    ) -> None:
        app = QApplication.instance()
        if app is None:
            return
        wallpaper_path = str(
            self.context.settings.get("wallpaper_path", "")
        )
        wallpaper_transparency = int(
            self.context.settings.get("wallpaper_transparency", 35)
        )
        dark = apply_theme(
            app,
            preference,
            accent,
            glass,
            wallpaper_active=bool(wallpaper_path),
            wallpaper_transparency=wallpaper_transparency,
        )
        self.navigation.set_theme(dark, accent)
        self.settings_screen.set_theme(dark, accent)
        self.ai_teacher_screen.set_theme(dark, accent)
        self.crawler_lab_screen.set_theme(dark, accent)
        self.workbench.set_theme(dark, accent)
        self.root_surface.set_wallpaper(
            wallpaper_path,
            wallpaper_transparency,
            dark=dark,
        )
        self.graduation_project_screen.set_theme(dark, accent)
        apply_windows_backdrop(self, dark=dark, enabled=glass)
        self.update()

    def _apply_wallpaper(
        self,
        path: str,
        transparency: int,
    ) -> None:
        self.context.settings.set("wallpaper_path", str(path or ""))
        self.context.settings.set(
            "wallpaper_transparency",
            max(0, min(90, int(transparency))),
        )
        self._apply_appearance(
            str(self.context.settings.get("theme_preference", "light")),
            str(self.context.settings.get("accent_value", "#2563EB")),
            bool(self.context.settings.get("glass_effect", True)),
        )

    def _preview_wallpaper(
        self,
        path: str,
        transparency: int,
    ) -> None:
        dark = is_dark_application()
        self.root_surface.set_wallpaper(
            path,
            transparency,
            dark=dark,
        )

    def showEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().showEvent(event)
        if not self._native_icon_handles:
            QTimer.singleShot(80, self._apply_native_window_icon)
        dark = str(
            self.context.settings.get("theme_preference", "light")
        ) == "dark"
        apply_windows_backdrop(
            self,
            dark=dark,
            enabled=bool(self.context.settings.get("glass_effect", True)),
        )

    def _apply_native_window_icon(self) -> None:
        if self._native_icon_handles or not self.isVisible():
            return
        icon_path = self.context.paths.resource_root / "assets" / "app-icon.ico"
        native_icon = set_windows_window_icon(self, icon_path)
        if native_icon is not None:
            self._native_icon_handles.append(native_icon)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.training_session_screen.runner.stop()
        if not self.workbench.can_close():
            event.ignore()
            return
        self.workbench.stop_terminal()
        self._save_window_state()
        super().closeEvent(event)
        for icon_handle in self._native_icon_handles:
            destroy_windows_icon(icon_handle)
        self._native_icon_handles.clear()
        app = QApplication.instance()
        if app is not None:
            app.quit()

    def _save_window_state(self) -> None:
        geometry_hex = bytes(self.saveGeometry().toHex()).decode("ascii")
        self.context.settings.set("window_geometry_hex", geometry_hex)

    def _restore_window_state(self) -> None:
        geometry_hex = self.context.settings.get("window_geometry_hex", "")
        if not geometry_hex:
            return
        try:
            geometry = QByteArray.fromHex(geometry_hex.encode("ascii"))
            self.restoreGeometry(geometry)
        except (ValueError, TypeError):
            return
