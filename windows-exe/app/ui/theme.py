from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication


LIGHT_STYLE = """
QWidget {
    color: #172033;
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 11pt;
}
QMainWindow, QWidget#appRoot {
    background: #F8FAFC;
}
QWidget#contentPanel {
    background: #F8FAFC;
}
QScrollArea, QWidget#qt_scrollarea_viewport {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QWidget#sidebar {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
QListWidget#navigation {
    background: transparent;
    border: none;
    outline: none;
    padding: 8px;
}
QListWidget#navigation::item {
    height: 42px;
    border-radius: 7px;
    padding-left: 12px;
    margin: 2px 0;
}
QListWidget#navigation::item:selected {
    background: #E7F0FF;
    color: #1557B0;
    font-weight: 600;
}
QListWidget#navigation::item:hover:!selected {
    background: #F1F5F9;
}
QLabel#brandTitle {
    font-size: 18pt;
    font-weight: 700;
    color: #0F172A;
}
QLabel#brandMark {
    background: #EFF6FF;
    border: 1px solid #D8E1EC;
    border-radius: 10px;
}
QLabel#brandSubtitle, QLabel#pageSubtitle, QLabel#metricLabel {
    color: #475569;
}
QLabel#pageTitle {
    font-size: 25pt;
    font-weight: 700;
    color: #0F172A;
}
QLabel#sectionTitle {
    font-size: 13pt;
    font-weight: 600;
    color: #0F172A;
}
QLabel#metricValue {
    font-size: 22pt;
    font-weight: 700;
    color: #1557B0;
}
QFrame#metricCard {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-bottom: 2px solid #CED8E5;
    border-radius: 10px;
}
QPushButton, QToolButton {
    min-height: 36px;
    padding: 0 15px;
    color: #1E293B;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #F4F7FB
    );
    border: 1px solid #C8D2E0;
    border-bottom: 2px solid #AAB8CA;
    border-radius: 8px;
    font-weight: 500;
}
QPushButton:hover, QToolButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #EAF0F7
    );
    border-color: #9CACBF;
    border-bottom-color: #8294AA;
}
QPushButton:pressed, QToolButton:pressed {
    padding-top: 2px;
    background: #E3EAF2;
    border-top: 2px solid #AAB8CA;
    border-bottom: 1px solid #AAB8CA;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid #1557B0;
    border-bottom: 2px solid #124996;
}
QPushButton:disabled, QToolButton:disabled {
    color: #94A3B8;
    background: #F1F5F9;
    border-color: #D8E1EC;
    border-bottom-color: #D8E1EC;
}
QPushButton#primaryButton {
    color: #FFFFFF;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #2869C7,
        stop:1 #1557B0
    );
    border: 1px solid #1557B0;
    border-bottom: 3px solid #0E3F82;
    min-height: 40px;
    padding: 0 20px;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #3276D3,
        stop:1 #124996
    );
}
QPushButton#dangerButton {
    color: #B42318;
    background: #FFF7F7;
    border: 1px solid #F2B8B5;
    border-bottom: 2px solid #E98F8A;
    font-weight: 600;
}
QPushButton#dangerButton:hover {
    background: #FEECEB;
    border-color: #E98F8A;
}
QWidget#workbenchToolbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
}
QLabel#workbenchStatus {
    background: #F1F5F9;
    color: #475569;
    border-top: 1px solid #E2E8F0;
    padding: 5px 10px;
}
QPlainTextEdit, QLineEdit, QTreeWidget, QListWidget {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-top-color: #D4DEEA;
    border-bottom: 2px solid #D4DEEA;
    border-radius: 8px;
    padding: 5px 7px;
    selection-background-color: #BFDBFE;
}
QLineEdit {
    min-height: 38px;
    padding: 0 10px;
}
QLineEdit#fieldEditor {
    padding-left: 0;
    padding-right: 0;
}
QPlainTextEdit#terminalOutput {
    background: #0B1220;
    color: #D8E1EC;
    border: 1px solid #263244;
    border-radius: 9px;
    font-family: "Cascadia Mono", "Consolas";
    font-size: 10.5pt;
    padding: 10px;
}
QLineEdit#terminalInput {
    background: #0B1220;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 9px;
    font-family: "Cascadia Mono", "Consolas";
    min-height: 40px;
}
QLineEdit#terminalInput:focus {
    border: 2px solid #1557B0;
}
QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #1557B0;
    border-bottom: 2px solid #124996;
}
QComboBox {
    min-height: 38px;
    padding: 0 30px 0 10px;
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
}
QComboBox:hover {
    border-color: #94A3B8;
}
QComboBox::drop-down {
    width: 26px;
    border: none;
    background: transparent;
}
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #CBD5E1;
    selection-background-color: #E7F0FF;
    selection-color: #1557B0;
    outline: none;
}
QSpinBox {
    min-height: 34px;
    padding: 0 8px;
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #CBD5E1;
    border-radius: 7px;
}
QFrame#libraryCard {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C7D3E1;
    border-radius: 10px;
}
QToolButton#libraryHeader {
    min-height: 30px;
    padding: 3px 6px;
    background: transparent;
    border: none;
    color: #0F172A;
    font-size: 11pt;
    font-weight: 650;
    text-align: left;
}
QToolButton#libraryHeader:hover {
    background: #EFF6FF;
    border-radius: 5px;
}
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    background: #FFFFFF;
}
QTabBar::tab {
    background: #F1F5F9;
    padding: 8px 14px;
    border: 1px solid #E2E8F0;
    border-bottom: 2px solid #C8D2E0;
}
QTabBar::tab:selected {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #F4F7FB
    );
    color: #1557B0;
    border-bottom: 2px solid #1557B0;
    font-weight: 600;
}
QSplitter::handle {
    background: #E2E8F0;
}
QSplitter::handle:horizontal {
    width: 1px;
}
QSplitter::handle:vertical {
    height: 1px;
}
QToolTip {
    background: #0F172A;
    color: #FFFFFF;
    border: none;
    padding: 5px;
}
QScrollArea#settingsScroll, QWidget#settingsScrollContents {
    background: transparent;
    border: none;
}
QFrame#settingsPanel {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C7D3E1;
    border-radius: 10px;
}
QFrame#aiConfigPanel {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C7D3E1;
    border-radius: 10px;
}
QLabel#aiHeaderIcon {
    background: #EFF6FF;
    border: 1px solid #D8E1EC;
    border-radius: 12px;
}
QLabel#fieldLabel {
    color: #334155;
    font-weight: 600;
}
QLabel#configMessage {
    border-radius: 8px;
    padding: 8px 9px;
}
QLabel#configMessage[state="success"] {
    color: #065F46;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
}
QLabel#configMessage[state="error"] {
    color: #991B1B;
    background: #FEF2F2;
    border: 1px solid #FECACA;
}
QLabel#configMessage[state="info"] {
    color: #1E40AF;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
}
QSlider::groove:horizontal {
    height: 10px;
    border-radius: 5px;
    background: #E2E8F0;
}
QSlider::sub-page:horizontal {
    height: 10px;
    border-radius: 5px;
    background: #2563EB;
}
QSlider::handle:horizontal {
    width: 22px;
    height: 22px;
    margin: -6px 0;
    border-radius: 11px;
    background: #FFFFFF;
    border: 2px solid #2563EB;
}
QSlider::handle:horizontal:hover {
    background: #EFF6FF;
}
QSlider::handle:horizontal:pressed {
    background: #DBEAFE;
}
QMenuBar {
    background: rgba(255, 255, 255, 0.92);
    border-bottom: 1px solid #E2E8F0;
    padding: 2px 8px;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background: #EFF6FF;
}
QMenu {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid #D8E1EC;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 7px 28px 7px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #E7F0FF;
    color: #1557B0;
}
QPushButton[themeChoice="true"] {
    min-width: 92px;
}
QPushButton[themeChoice="true"]:checked {
    background: #E7F0FF;
    border-color: #1557B0;
    color: #1557B0;
    font-weight: 650;
}
QFrame#summaryCard, QFrame#practicePanel {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C7D3E1;
    border-radius: 10px;
}
QFrame#stageCard {
    background: #FFFFFF;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C7D3E1;
    border-radius: 10px;
}
QToolButton#stageHeader {
    min-height: 58px;
    padding: 8px 14px;
    text-align: left;
    background: transparent;
    border: none;
    border-radius: 7px;
    font-weight: 650;
}
QToolButton#stageHeader:hover {
    background: #F1F5F9;
}
QPushButton#lessonRow {
    min-height: 50px;
    padding: 7px 12px;
    text-align: left;
    background: #F8FAFC;
    border: 1px solid #D8E1EC;
    border-bottom: 2px solid #C4D0DE;
    border-radius: 8px;
}
QPushButton#lessonRow:hover:enabled {
    background: #EAF2FF;
    border-color: #93B4E8;
}
QPushButton#lessonRow:disabled {
    color: #94A3B8;
    background: #F8FAFC;
}
QFrame#lessonSection {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-bottom: 2px solid #CED8E5;
    border-radius: 10px;
}
QPlainTextEdit#lessonCode {
    background: #F8FAFC;
    border: 1px solid #D8E1EC;
    border-radius: 6px;
}
QLabel#codeNote {
    color: #1557B0;
    font-weight: 600;
}
QLabel#errorTitle {
    color: #B42318;
    font-weight: 650;
}
QLabel#quizQuestion {
    font-size: 12pt;
    font-weight: 650;
}
QPushButton#quizOption {
    text-align: left;
    min-height: 38px;
    padding: 6px 12px;
    border-bottom: 2px solid #C4D0DE;
}
QPushButton#lessonRow:pressed, QPushButton#quizOption:pressed {
    padding-top: 8px;
    border-bottom: 1px solid #C4D0DE;
}
QPushButton#quizOption[result="correct"] {
    color: #065F46;
    background: #D1FAE5;
    border-color: #34D399;
}
QPushButton#quizOption[result="wrong"] {
    color: #991B1B;
    background: #FEE2E2;
    border-color: #F87171;
}
QPushButton#quizOption[result="answer"] {
    color: #065F46;
    background: #ECFDF5;
    border-color: #6EE7B7;
}
QLabel#quizCorrect {
    color: #047857;
    font-weight: 650;
}
QLabel#quizWrong {
    color: #B42318;
    font-weight: 650;
}
QLabel#progressValue {
    color: #1557B0;
    font-size: 14pt;
    font-weight: 700;
}
QLabel#mutedText {
    color: #52657A;
}
QFrame#progressRow {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-bottom: 2px solid #CED8E5;
    border-radius: 8px;
}
QLabel#progressRowTitle {
    font-weight: 600;
}
QLabel#practiceResult {
    font-size: 16pt;
    font-weight: 650;
}
QLabel#tagLabel {
    color: #1557B0;
    background: #E7F0FF;
    border-radius: 5px;
    padding: 3px 9px;
    font-weight: 650;
}
QProgressBar {
    min-height: 8px;
    max-height: 8px;
    border: none;
    border-radius: 4px;
    background: #E2E8F0;
}
QProgressBar::chunk {
    border-radius: 4px;
    background: #2563EB;
}
QScrollBar:vertical {
    width: 11px;
    background: transparent;
    margin: 0;
}
QScrollBar::handle:vertical {
    min-height: 32px;
    background: #B8C4D4;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    height: 11px;
    background: transparent;
}
QScrollBar::handle:horizontal {
    min-width: 32px;
    background: #B8C4D4;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
"""


DARK_STYLE = """
QWidget {
    color: #E5E7EB;
    font-family: "Microsoft YaHei UI", "Segoe UI";
    font-size: 11pt;
}
QMainWindow, QWidget#appRoot {
    background: #0F172A;
}
QWidget#contentPanel {
    background: #0F172A;
}
QScrollArea, QWidget#qt_scrollarea_viewport {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QWidget#sidebar {
    background: #111C2E;
    border-right: 1px solid #263244;
}
QListWidget#navigation {
    background: transparent;
    border: none;
    outline: none;
    padding: 8px;
}
QListWidget#navigation::item {
    height: 42px;
    border-radius: 7px;
    padding-left: 12px;
    margin: 2px 0;
}
QListWidget#navigation::item:selected {
    background: #193A63;
    color: #BFDBFE;
    font-weight: 600;
}
QListWidget#navigation::item:hover:!selected {
    background: #1B2739;
}
QLabel#brandTitle, QLabel#pageTitle, QLabel#sectionTitle {
    color: #F8FAFC;
}
QLabel#brandMark {
    background: #193A63;
    border: 1px solid #2A3950;
    border-radius: 10px;
}
QLabel#brandSubtitle, QLabel#pageSubtitle, QLabel#metricLabel {
    color: #B7C3D2;
}
QLabel#metricValue {
    color: #93C5FD;
}
QFrame#metricCard {
    background: #152033;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
}
QPushButton, QToolButton {
    color: #E5E7EB;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1C2A41,
        stop:1 #142033
    );
    border: 1px solid #3B4C66;
    border-bottom: 2px solid #0B1220;
    border-radius: 8px;
    font-weight: 500;
}
QPushButton:hover, QToolButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #243650,
        stop:1 #1A2940
    );
    border-color: #5B7192;
    border-bottom-color: #0B1220;
}
QPushButton:pressed, QToolButton:pressed {
    padding-top: 2px;
    background: #101B2D;
    border-top: 2px solid #0B1220;
    border-bottom: 1px solid #3B4C66;
}
QPushButton:focus, QToolButton:focus {
    border: 1px solid #3B82F6;
    border-bottom: 2px solid #1D4ED8;
}
QPushButton:disabled, QToolButton:disabled {
    color: #64748B;
    background: #172033;
    border-color: #263244;
    border-bottom-color: #182235;
}
QPushButton#primaryButton {
    color: #FFFFFF;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #3B82F6,
        stop:1 #2563EB
    );
    border: 1px solid #3B82F6;
    border-bottom: 3px solid #1E40AF;
    min-height: 40px;
    padding: 0 20px;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #60A5FA,
        stop:1 #2563EB
    );
}
QPushButton#dangerButton {
    color: #FCA5A5;
    background: #3A1E24;
    border: 1px solid #7F3F47;
    border-bottom: 2px solid #5B2B33;
    font-weight: 600;
}
QPushButton#dangerButton:hover {
    background: #4A252C;
    border-color: #B85C66;
}
QWidget#workbenchToolbar {
    background: #111C2E;
    border-bottom: 1px solid #263244;
}
QLabel#workbenchStatus {
    background: #111C2E;
    color: #94A3B8;
    border-top: 1px solid #263244;
    padding: 5px 10px;
}
QPlainTextEdit, QLineEdit, QTreeWidget, QListWidget {
    background: #111827;
    color: #E5E7EB;
    border: 1px solid #2A3950;
    border-top-color: #35465F;
    border-bottom: 2px solid #0B1220;
    border-radius: 8px;
    padding: 5px 7px;
    selection-background-color: #1D4ED8;
}
QLineEdit {
    min-height: 38px;
    padding: 0 10px;
}
QLineEdit#fieldEditor {
    padding-left: 0;
    padding-right: 0;
}
QPlainTextEdit#terminalOutput {
    background: #0B1220;
    color: #D8E1EC;
    border: 1px solid #263244;
    border-radius: 9px;
    font-family: "Cascadia Mono", "Consolas";
    font-size: 10.5pt;
    padding: 10px;
}
QLineEdit#terminalInput {
    background: #0B1220;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 9px;
    font-family: "Cascadia Mono", "Consolas";
    min-height: 40px;
}
QLineEdit#terminalInput:focus {
    border: 2px solid #3B82F6;
}
QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #3B82F6;
    border-bottom: 2px solid #2563EB;
}
QComboBox {
    min-height: 38px;
    padding: 0 30px 0 10px;
    background: #111827;
    color: #E5E7EB;
    border: 1px solid #34445D;
    border-radius: 7px;
}
QComboBox::drop-down {
    width: 26px;
    border: none;
    background: transparent;
}
QComboBox QAbstractItemView {
    background: #111827;
    color: #E5E7EB;
    border: 1px solid #34445D;
    selection-background-color: #193A63;
    selection-color: #BFDBFE;
    outline: none;
}
QSpinBox {
    min-height: 34px;
    padding: 0 8px;
    background: #111827;
    color: #E5E7EB;
    border: 1px solid #34445D;
    border-radius: 7px;
}
QFrame#libraryCard {
    background: #152033;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
}
QToolButton#libraryHeader {
    min-height: 30px;
    padding: 3px 6px;
    background: transparent;
    border: none;
    color: #F8FAFC;
    font-size: 11pt;
    font-weight: 650;
    text-align: left;
}
QToolButton#libraryHeader:hover {
    background: #193A63;
    border-radius: 5px;
}
QTabWidget::pane {
    border: 1px solid #2A3950;
    background: #111827;
}
QTabBar::tab {
    background: #172338;
    padding: 8px 14px;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
}
QTabBar::tab:selected {
    background: #1A2940;
    color: #93C5FD;
    border-bottom: 2px solid #3B82F6;
    font-weight: 600;
}
QSplitter::handle {
    background: #2A3950;
}
QScrollArea#settingsScroll, QWidget#settingsScrollContents {
    background: transparent;
    border: none;
}
QFrame#settingsPanel {
    background: #152033;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
}
QFrame#aiConfigPanel {
    background: #152033;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
}
QLabel#aiHeaderIcon {
    background: #193A63;
    border: 1px solid #2A3950;
    border-radius: 12px;
}
QLabel#fieldLabel {
    color: #D8E1EC;
    font-weight: 600;
}
QLabel#configMessage {
    border-radius: 8px;
    padding: 8px 9px;
}
QLabel#configMessage[state="success"] {
    color: #A7F3D0;
    background: #10372F;
    border: 1px solid #176B55;
}
QLabel#configMessage[state="error"] {
    color: #FECACA;
    background: #3A1E24;
    border: 1px solid #7F3F47;
}
QLabel#configMessage[state="info"] {
    color: #BFDBFE;
    background: #193A63;
    border: 1px solid #315A88;
}
QSlider::groove:horizontal {
    height: 10px;
    border-radius: 5px;
    background: #2A3950;
}
QSlider::sub-page:horizontal {
    height: 10px;
    border-radius: 5px;
    background: #3B82F6;
}
QSlider::handle:horizontal {
    width: 22px;
    height: 22px;
    margin: -6px 0;
    border-radius: 11px;
    background: #F8FAFC;
    border: 2px solid #3B82F6;
}
QSlider::handle:horizontal:hover {
    background: #DBEAFE;
}
QSlider::handle:horizontal:pressed {
    background: #BFDBFE;
}
QFrame#summaryCard, QFrame#practicePanel, QFrame#stageCard,
QFrame#lessonSection, QFrame#progressRow {
    background: #152033;
    border: 1px solid #2A3950;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
}
QToolButton#stageHeader {
    min-height: 58px;
    padding: 8px 14px;
    text-align: left;
    background: transparent;
    border: none;
    font-weight: 650;
}
QToolButton#stageHeader:hover {
    background: #1B2739;
}
QPushButton#lessonRow {
    min-height: 50px;
    padding: 7px 12px;
    text-align: left;
    background: #111827;
    border: 1px solid #35465F;
    border-bottom: 2px solid #0B1220;
    border-radius: 8px;
}
QPushButton#lessonRow:hover:enabled {
    background: #193A63;
    border-color: #3B82F6;
}
QPushButton#lessonRow:disabled {
    color: #64748B;
}
QPlainTextEdit#lessonCode {
    background: #0B1220;
    border: 1px solid #2A3950;
}
QLabel#codeNote {
    color: #93C5FD;
    font-weight: 600;
}
QLabel#errorTitle {
    color: #FCA5A5;
    font-weight: 650;
}
QLabel#quizQuestion {
    font-size: 12pt;
    font-weight: 650;
}
QPushButton#quizOption {
    text-align: left;
    min-height: 38px;
    padding: 6px 12px;
    border-bottom: 2px solid #0B1220;
}
QPushButton#lessonRow:pressed, QPushButton#quizOption:pressed {
    padding-top: 8px;
    border-bottom: 1px solid #35465F;
}
QPushButton#quizOption[result="correct"] {
    color: #D1FAE5;
    background: #064E3B;
    border-color: #10B981;
}
QPushButton#quizOption[result="wrong"] {
    color: #FEE2E2;
    background: #641E1E;
    border-color: #EF4444;
}
QPushButton#quizOption[result="answer"] {
    color: #D1FAE5;
    background: #0F3D32;
    border-color: #34D399;
}
QLabel#quizCorrect {
    color: #6EE7B7;
    font-weight: 650;
}
QLabel#quizWrong {
    color: #FCA5A5;
    font-weight: 650;
}
QLabel#progressValue {
    color: #93C5FD;
    font-size: 14pt;
    font-weight: 700;
}
QLabel#mutedText {
    color: #A9B7C8;
}
QLabel#progressRowTitle {
    font-weight: 600;
}
QLabel#practiceResult {
    font-size: 16pt;
    font-weight: 650;
}
QLabel#tagLabel {
    color: #BFDBFE;
    background: #193A63;
    border-radius: 5px;
    padding: 3px 9px;
    font-weight: 650;
}
QProgressBar {
    min-height: 8px;
    max-height: 8px;
    border: none;
    border-radius: 4px;
    background: #2A3950;
}
QProgressBar::chunk {
    border-radius: 4px;
    background: #3B82F6;
}
QScrollBar:vertical {
    width: 11px;
    background: transparent;
}
QScrollBar::handle:vertical {
    min-height: 32px;
    background: #3F5068;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    height: 11px;
    background: transparent;
}
QScrollBar::handle:horizontal {
    min-width: 32px;
    background: #3F5068;
    border-radius: 5px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QMenuBar {
    background: rgba(15, 24, 40, 0.94);
    border-bottom: 1px solid #2A3950;
    padding: 2px 8px;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    border-radius: 6px;
}
QMenuBar::item:selected {
    background: #193A63;
}
QMenu {
    background: #111827;
    border: 1px solid #34445D;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 7px 28px 7px 12px;
    border-radius: 6px;
}
QMenu::item:selected {
    background: #193A63;
    color: #BFDBFE;
}
QPushButton[themeChoice="true"] {
    min-width: 92px;
}
QPushButton[themeChoice="true"]:checked {
    background: #193A63;
    border-color: #3B82F6;
    color: #BFDBFE;
    font-weight: 650;
}
"""


def is_dark_application() -> bool:
    hints = QApplication.styleHints()
    if hasattr(hints, "colorScheme"):
        return hints.colorScheme() == Qt.ColorScheme.Dark
    return QApplication.palette().color(QPalette.ColorRole.Window).lightness() < 128


def apply_theme(
    app: QApplication,
    preference: str = "system",
    accent: str = "#2563EB",
    glass: bool = True,
    *,
    wallpaper_active: bool = False,
    wallpaper_transparency: int = 35,
) -> bool:
    dark = preference == "dark" or (preference == "system" and is_dark_application())
    accent_color = QColor(accent)
    if not accent_color.isValid():
        accent_color = QColor("#2563EB")
    style = DARK_STYLE if dark else LIGHT_STYLE
    style = _apply_accent(style, accent_color)
    if glass:
        style += _glass_style(dark, accent_color)
    if wallpaper_active:
        style += _wallpaper_style(
            dark,
            accent_color,
            wallpaper_transparency,
        )
    style += _modern_controls_style(dark, accent_color)
    app.setStyle("Fusion")
    font = QFont("Microsoft YaHei UI")
    font.setPointSizeF(11.0)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)
    app.setStyleSheet(style)
    palette = QPalette()
    if dark:
        palette.setColor(QPalette.ColorRole.Window, QColor("#0F172A"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#E5E7EB"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#111827"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#E5E7EB"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#94A3B8"))
    else:
        palette.setColor(QPalette.ColorRole.Window, QColor("#F8FAFC"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#172033"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#172033"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#64748B"))
    app.setPalette(palette)
    return dark


def _apply_accent(style: str, accent: QColor) -> str:
    base = accent.name()
    hover = accent.darker(118).name()
    light_tint = accent.lighter(220).name()
    dark_tint = accent.darker(260).name()
    for source in ("#1557B0", "#2563EB", "#3B82F6"):
        style = style.replace(source, base)
    style = style.replace("#124996", hover)
    style = style.replace("#0E3F82", accent.darker(190).name())
    style = style.replace("#1E40AF", accent.darker(175).name())
    style = style.replace("#1D4ED8", accent.darker(150).name())
    style = style.replace("#2869C7", accent.lighter(108).name())
    style = style.replace("#3276D3", accent.lighter(118).name())
    style = style.replace("#E7F0FF", light_tint)
    style = style.replace("#193A63", dark_tint)
    style = style.replace("#93C5FD", accent.lighter(145).name())
    style = style.replace("#BFDBFE", accent.lighter(175).name())
    return style


def _glass_style(dark: bool, accent: QColor) -> str:
    if dark:
        return f"""
QMainWindow, QWidget#appRoot {{
    background: rgba(8, 15, 28, 0.78);
}}
QWidget#contentPanel {{
    background: rgba(10, 18, 32, 0.80);
}}
QWidget#sidebar {{
    background: rgba(15, 24, 40, 0.82);
    border-right: 1px solid rgba(148, 163, 184, 0.20);
}}
QFrame#summaryCard, QFrame#stageCard, QFrame#lessonSection,
QFrame#progressRow, QFrame#practicePanel, QFrame#libraryCard,
QFrame#settingsPanel, QFrame#aiConfigPanel {{
    background: rgba(21, 32, 51, 0.86);
    border: 1px solid rgba(148, 163, 184, 0.18);
}}
QMenuBar {{
    background: rgba(10, 18, 32, 0.86);
}}
"""
    return f"""
QMainWindow, QWidget#appRoot {{
    background: rgba(244, 248, 252, 0.78);
}}
QWidget#contentPanel {{
    background: rgba(255, 255, 255, 0.80);
}}
QWidget#sidebar {{
    background: rgba(255, 255, 255, 0.78);
    border-right: 1px solid rgba(148, 163, 184, 0.20);
}}
QFrame#summaryCard, QFrame#stageCard, QFrame#lessonSection,
QFrame#progressRow, QFrame#practicePanel, QFrame#libraryCard,
QFrame#settingsPanel, QFrame#aiConfigPanel {{
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid rgba(148, 163, 184, 0.18);
}}
QMenuBar {{
    background: rgba(255, 255, 255, 0.86);
}}
"""


def _wallpaper_style(
    dark: bool,
    accent: QColor,
    transparency: int,
) -> str:
    transparency = max(0, min(90, int(transparency)))
    content_alpha = 0.46 + (transparency / 100.0) * 0.06
    card_alpha = 0.94 + (transparency / 100.0) * 0.03
    sidebar_alpha = 0.90 + (transparency / 100.0) * 0.04
    if dark:
        return f"""
QMainWindow, QWidget#appRoot {{
    background: transparent;
}}
QWidget#contentPanel {{
    background: rgba(8, 15, 28, {content_alpha:.3f});
    border-left: 1px solid rgba(148, 163, 184, 0.15);
}}
QWidget#sidebar {{
    background: rgba(12, 20, 35, {sidebar_alpha:.3f});
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}}
QFrame#summaryCard, QFrame#stageCard, QFrame#lessonSection,
QFrame#progressRow, QFrame#practicePanel, QFrame#libraryCard,
QFrame#metricCard, QFrame#settingsPanel, QFrame#aiConfigPanel {{
    background: rgba(20, 31, 48, {card_alpha:.3f});
    border: 1px solid rgba(148, 163, 184, 0.23);
    border-bottom: 2px solid rgba(4, 9, 18, 0.68);
}}
QPlainTextEdit, QLineEdit, QTreeWidget, QListWidget, QComboBox {{
    background: rgba(10, 18, 32, 0.975);
}}
QMenuBar {{
    background: rgba(10, 18, 32, 0.90);
}}
"""
    return f"""
QMainWindow, QWidget#appRoot {{
    background: transparent;
}}
QWidget#contentPanel {{
    background: rgba(248, 250, 252, {content_alpha:.3f});
    border-left: 1px solid rgba(148, 163, 184, 0.15);
}}
QWidget#sidebar {{
    background: rgba(255, 255, 255, {sidebar_alpha:.3f});
    border-right: 1px solid rgba(148, 163, 184, 0.18);
}}
QFrame#summaryCard, QFrame#stageCard, QFrame#lessonSection,
QFrame#progressRow, QFrame#practicePanel, QFrame#libraryCard,
QFrame#metricCard, QFrame#settingsPanel, QFrame#aiConfigPanel {{
    background: rgba(255, 255, 255, {card_alpha:.3f});
    border: 1px solid rgba(148, 163, 184, 0.24);
    border-bottom: 2px solid rgba(148, 163, 184, 0.34);
}}
QPlainTextEdit, QLineEdit, QTreeWidget, QListWidget, QComboBox {{
    background: rgba(255, 255, 255, 0.975);
}}
QMenuBar {{
    background: rgba(255, 255, 255, 0.90);
}}
"""


def _modern_controls_style(dark: bool, accent: QColor) -> str:
    accent_name = accent.name()
    accent_hover = accent.lighter(118).name()
    accent_pressed = accent.darker(135).name()
    accent_border = accent.darker(112).name()
    if dark:
        return f"""
QPushButton {{
    min-height: 40px;
    padding: 0 16px;
    color: #E5E7EB;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1C2A41,
        stop:1 #142033
    );
    border: 1px solid #3B4C66;
    border-bottom: 2px solid #0B1220;
    border-radius: 10px;
    font-weight: 600;
}}
QPushButton:hover {{
    color: #BFDBFE;
    background: #1D304D;
    border-color: #5F7EA9;
}}
QPushButton:pressed {{
    padding-top: 2px;
    background: #101B2D;
    border-top: 1px solid #5F7EA9;
    border-bottom: 1px solid #3B4C66;
}}
QPushButton:focus {{
    border: 2px solid {accent_name};
}}
QPushButton:disabled {{
    color: #64748B;
    background: #172033;
    border-color: #263244;
}}
QToolButton#workbenchAction,
QToolButton#runActionButton,
QToolButton#stopActionButton {{
    min-height: 34px;
    padding: 0 12px;
    color: #D8E1EC;
    background: #172338;
    border: 1px solid #34445D;
    border-radius: 8px;
    font-weight: 600;
}}
QToolButton#workbenchAction:hover {{
    color: #BFDBFE;
    background: #1D304D;
    border-color: #5F7EA9;
}}
QToolButton#runActionButton {{
    color: #FFFFFF;
    background: {accent_name};
    border-color: {accent_name};
}}
QToolButton#runActionButton:hover {{
    background: {accent_hover};
}}
QToolButton#stopActionButton {{
    color: #FCA5A5;
    background: #3A1E24;
    border-color: #7F3F47;
}}
QPushButton#fileTreeAction {{
    min-height: 34px;
    padding: 0 8px;
    color: #D8E1EC;
    background: #172338;
    border: 1px solid #34445D;
    border-radius: 8px;
}}
QPushButton#iconButton {{
    min-height: 40px;
    padding: 0;
    background: #172338;
    border: 1px solid #34445D;
    border-radius: 9px;
}}
QListWidget#projectList {{
    background: transparent;
    border: none;
    padding: 0;
}}
QListWidget#projectList::item {{
    padding: 8px 9px;
    margin: 2px 0;
    border: 1px solid transparent;
    border-radius: 8px;
}}
QListWidget#projectList::item:hover {{
    background: #1A2940;
    border-color: #34445D;
}}
QListWidget#projectList::item:selected {{
    color: #BFDBFE;
    background: #193A63;
    border-color: {accent_name};
}}
QPushButton#primaryButton {{
    color: #FFFFFF;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {accent_hover},
        stop:1 {accent_name}
    );
    border: 1px solid {accent_name};
    border-bottom: 2px solid {accent_pressed};
    border-radius: 10px;
    min-height: 42px;
    padding: 0 20px;
    font-weight: 700;
}}
QPushButton#primaryButton:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {accent.lighter(132).name()},
        stop:1 {accent_name}
    );
}}
QPushButton#primaryButton:pressed {{
    background: {accent_pressed};
    border: 1px solid {accent.darker(150).name()};
}}
QPushButton#secondaryButton {{
    color: #D8E1EC;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #1B2A41,
        stop:1 #142033
    );
    border: 1px solid #3B4C66;
    border-bottom: 2px solid #0B1220;
}}
QPushButton#secondaryButton:hover {{
    color: #BFDBFE;
    background: #1D304D;
    border-color: #5F7EA9;
}}
QTabWidget::pane {{
    background: transparent;
    border: 1px solid #2A3950;
    border-radius: 10px;
    top: -1px;
}}
QTabBar::tab {{
    min-height: 38px;
    padding: 0 18px;
    margin-right: 4px;
    color: #B7C3D2;
    background: transparent;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
    border-radius: 9px 9px 0 0;
    font-weight: 600;
}}
QTabBar::tab:hover {{
    color: #BFDBFE;
    background: #1A2940;
}}
QTabBar::tab:selected {{
    color: #BFDBFE;
    background: #193A63;
    border-bottom: 2px solid {accent_name};
}}
QComboBox {{
    min-height: 40px;
    padding: 0 34px 0 12px;
    background: #111827;
    border: 1px solid #34445D;
    border-radius: 10px;
}}
QComboBox:hover {{
    border-color: #5F7EA9;
    background: #172338;
}}
QComboBox:focus {{
    border: 2px solid {accent_name};
}}
QComboBox::drop-down {{
    width: 32px;
    border: none;
    border-left: 1px solid #2A3950;
}}
QComboBox::down-arrow {{
    width: 0;
    height: 0;
    image: none;
}}
QComboBox QAbstractItemView {{
    background: #111827;
    color: #E5E7EB;
    border: 1px solid #34445D;
    border-radius: 10px;
    padding: 6px;
    outline: none;
    selection-background-color: #193A63;
    selection-color: #BFDBFE;
}}
QComboBox QAbstractItemView::item {{
    min-height: 36px;
    padding: 4px 10px;
    border-radius: 7px;
}}
QPushButton#quizOption {{
    min-height: 54px;
    padding: 10px 14px;
    color: #E5E7EB;
    background: #111827;
    border: 1px solid #35465F;
    border-left: 3px solid #52657A;
    border-bottom: 1px solid #35465F;
    border-radius: 9px;
    text-align: left;
    font-weight: 550;
}}
QPushButton#quizOption:hover {{
    color: #BFDBFE;
    background: #193A63;
    border-left-color: {accent_name};
}}
QPushButton#quizOption:checked {{
    background: #193A63;
    border-left-color: {accent_name};
}}
QPushButton#quizOption[result="correct"] {{
    color: #D1FAE5;
    background: #064E3B;
    border-color: #10B981;
    border-left-color: #34D399;
}}
QPushButton#quizOption[result="wrong"] {{
    color: #FEE2E2;
    background: #641E1E;
    border-color: #EF4444;
    border-left-color: #F87171;
}}
QPushButton#quizOption[result="answer"] {{
    color: #D1FAE5;
    background: #0F3D32;
    border-color: #34D399;
    border-left-color: #6EE7B7;
}}
"""
    return f"""
QPushButton {{
    min-height: 40px;
    padding: 0 16px;
    color: #172033;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #F8FAFC
    );
    border: 1px solid #D7E1ED;
    border-bottom: 2px solid #C7D2E0;
    border-radius: 10px;
    font-weight: 600;
}}
QPushButton:hover {{
    color: {accent_name};
    background: #F4F8FF;
    border-color: {accent.lighter(165).name()};
}}
QPushButton:pressed {{
    padding-top: 2px;
    background: {accent.lighter(220).name()};
    border-top: 1px solid {accent.lighter(165).name()};
    border-bottom: 1px solid {accent.lighter(165).name()};
}}
QPushButton:focus {{
    border: 2px solid {accent_name};
}}
QPushButton:disabled {{
    color: #94A3B8;
    background: #F1F5F9;
    border-color: #D8E1EC;
}}
QToolButton#workbenchAction,
QToolButton#runActionButton,
QToolButton#stopActionButton {{
    min-height: 34px;
    padding: 0 12px;
    color: #334155;
    background: #FFFFFF;
    border: 1px solid #D7E1ED;
    border-radius: 8px;
    font-weight: 600;
}}
QToolButton#workbenchAction:hover {{
    color: {accent_name};
    background: {accent.lighter(242).name()};
    border-color: {accent.lighter(160).name()};
}}
QToolButton#runActionButton {{
    color: #FFFFFF;
    background: {accent_name};
    border-color: {accent_name};
}}
QToolButton#runActionButton:hover {{
    background: {accent_hover};
}}
QToolButton#stopActionButton {{
    color: #B42318;
    background: #FFF7F7;
    border-color: #F2B8B5;
}}
QPushButton#fileTreeAction {{
    min-height: 34px;
    padding: 0 8px;
    color: #334155;
    background: #FFFFFF;
    border: 1px solid #D7E1ED;
    border-radius: 8px;
}}
QPushButton#iconButton {{
    min-height: 40px;
    padding: 0;
    background: #FFFFFF;
    border: 1px solid #D7E1ED;
    border-radius: 9px;
}}
QListWidget#projectList {{
    background: transparent;
    border: none;
    padding: 0;
}}
QListWidget#projectList::item {{
    padding: 8px 9px;
    margin: 2px 0;
    border: 1px solid transparent;
    border-radius: 8px;
}}
QListWidget#projectList::item:hover {{
    background: #F4F8FF;
    border-color: #D7E1ED;
}}
QListWidget#projectList::item:selected {{
    color: {accent_name};
    background: {accent.lighter(235).name()};
    border-color: {accent.lighter(160).name()};
}}
QPushButton#primaryButton {{
    color: #FFFFFF;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {accent_hover},
        stop:1 {accent_name}
    );
    border: 1px solid {accent_name};
    border-bottom: 2px solid {accent_border};
    border-radius: 10px;
    min-height: 42px;
    padding: 0 20px;
    font-weight: 700;
}}
QPushButton#primaryButton:hover {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 {accent.lighter(132).name()},
        stop:1 {accent_name}
    );
    border-color: {accent_name};
}}
QPushButton#primaryButton:pressed {{
    background: {accent_pressed};
    border: 1px solid {accent.darker(150).name()};
}}
QPushButton#secondaryButton {{
    color: #334155;
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FFFFFF,
        stop:1 #F5F8FC
    );
    border: 1px solid #D7E1ED;
    border-bottom: 2px solid #C7D2E0;
}}
QPushButton#secondaryButton:hover {{
    color: {accent_name};
    background: {accent.lighter(240).name()};
    border-color: {accent.lighter(160).name()};
}}
QTabWidget::pane {{
    background: transparent;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    top: -1px;
}}
QTabBar::tab {{
    min-height: 38px;
    padding: 0 18px;
    margin-right: 4px;
    color: #475569;
    background: transparent;
    border: 1px solid transparent;
    border-bottom: 2px solid transparent;
    border-radius: 9px 9px 0 0;
    font-weight: 600;
}}
QTabBar::tab:hover {{
    color: {accent_name};
    background: {accent.lighter(245).name()};
}}
QTabBar::tab:selected {{
    color: {accent_name};
    background: {accent.lighter(238).name()};
    border-bottom: 2px solid {accent_name};
}}
QComboBox {{
    min-height: 40px;
    padding: 0 34px 0 12px;
    background: #FFFFFF;
    border: 1px solid #D7E1ED;
    border-radius: 10px;
}}
QComboBox:hover {{
    border-color: {accent.lighter(155).name()};
    background: #FBFDFF;
}}
QComboBox:focus {{
    border: 2px solid {accent_name};
}}
QComboBox::drop-down {{
    width: 32px;
    border: none;
    border-left: 1px solid #E2E8F0;
}}
QComboBox::down-arrow {{
    width: 0;
    height: 0;
    image: none;
}}
QComboBox QAbstractItemView {{
    background: #FFFFFF;
    color: #172033;
    border: 1px solid #D7E1ED;
    border-radius: 10px;
    padding: 6px;
    outline: none;
    selection-background-color: {accent.lighter(230).name()};
    selection-color: {accent_name};
}}
QComboBox QAbstractItemView::item {{
    min-height: 36px;
    padding: 4px 10px;
    border-radius: 7px;
}}
QPushButton#quizOption {{
    min-height: 54px;
    padding: 10px 14px;
    color: #172033;
    background: #F8FAFC;
    border: 1px solid #D7E1ED;
    border-left: 3px solid #CBD5E1;
    border-bottom: 1px solid #D7E1ED;
    border-radius: 9px;
    text-align: left;
    font-weight: 550;
}}
QPushButton#quizOption:hover {{
    color: {accent_name};
    background: {accent.lighter(245).name()};
    border-left-color: {accent_name};
}}
QPushButton#quizOption:checked {{
    background: {accent.lighter(230).name()};
    border-left-color: {accent_name};
}}
QPushButton#quizOption[result="correct"] {{
    color: #065F46;
    background: #ECFDF5;
    border-color: #6EE7B7;
    border-left-color: #10B981;
}}
QPushButton#quizOption[result="wrong"] {{
    color: #991B1B;
    background: #FEF2F2;
    border-color: #FECACA;
    border-left-color: #EF4444;
}}
QPushButton#quizOption[result="answer"] {{
    color: #065F46;
    background: #F0FDF4;
    border-color: #A7F3D0;
    border-left-color: #34D399;
}}
"""
