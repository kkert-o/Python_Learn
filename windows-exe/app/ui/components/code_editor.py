from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QKeyEvent,
    QPainter,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from app.workspace.file_manager import FileManager


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.editor.line_number_area_paint_event(event)


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self.keyword_format = QTextCharFormat()
        self.builtin_format = QTextCharFormat()
        self.definition_format = QTextCharFormat()
        self.number_format = QTextCharFormat()
        self.string_format = QTextCharFormat()
        self.comment_format = QTextCharFormat()
        self.decorator_format = QTextCharFormat()
        self.keywords = (
            "False",
            "None",
            "True",
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "case",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "match",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
        )
        self.builtins = (
            "abs",
            "all",
            "any",
            "bool",
            "bytes",
            "callable",
            "chr",
            "dict",
            "dir",
            "enumerate",
            "eval",
            "exec",
            "filter",
            "float",
            "format",
            "frozenset",
            "getattr",
            "hasattr",
            "hash",
            "help",
            "hex",
            "id",
            "input",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "min",
            "next",
            "object",
            "oct",
            "open",
            "ord",
            "pow",
            "print",
            "property",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "setattr",
            "slice",
            "sorted",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "vars",
            "zip",
        )
        self._keyword_pattern = __import__("re").compile(
            r"\b(" + "|".join(self.keywords) + r")\b"
        )
        self._builtin_pattern = __import__("re").compile(
            r"\b(" + "|".join(self.builtins) + r")\b"
        )
        self._definition_pattern = __import__("re").compile(
            r"\b(?:def|class)\s+([A-Za-z_]\w*)"
        )
        self._number_pattern = __import__("re").compile(
            r"\b(?:0[xX][0-9A-Fa-f]+|0[bB][01]+|0[oO][0-7]+|"
            r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b"
        )
        self._string_pattern = __import__("re").compile(
            r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
        )
        self._comment_pattern = __import__("re").compile(r"#.*$")
        self._decorator_pattern = __import__("re").compile(r"^\s*@[\w.]+")
        self.set_theme(False)

    def set_theme(self, dark: bool) -> None:
        if dark:
            colors = {
                "keyword": "#C4B5FD",
                "builtin": "#7DD3FC",
                "definition": "#6EE7B7",
                "number": "#FCD34D",
                "string": "#FDA4AF",
                "comment": "#94A3B8",
                "decorator": "#67E8F9",
            }
        else:
            colors = {
                "keyword": "#7C3AED",
                "builtin": "#0369A1",
                "definition": "#047857",
                "number": "#B45309",
                "string": "#BE123C",
                "comment": "#64748B",
                "decorator": "#0891B2",
            }
        self.keyword_format = self._format(colors["keyword"], bold=True)
        self.builtin_format = self._format(colors["builtin"])
        self.definition_format = self._format(
            colors["definition"],
            bold=True,
        )
        self.number_format = self._format(colors["number"])
        self.string_format = self._format(colors["string"])
        self.comment_format = self._format(colors["comment"], italic=True)
        self.decorator_format = self._format(colors["decorator"])
        self.rehighlight()

    @staticmethod
    def _format(color: str, *, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        text_format.setFontWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        text_format.setFontItalic(italic)
        return text_format

    def highlightBlock(self, text: str) -> None:
        for match in self._keyword_pattern.finditer(text):
            self.setFormat(
                match.start(1),
                match.end(1) - match.start(1),
                self.keyword_format,
            )
        for match in self._builtin_pattern.finditer(text):
            self.setFormat(
                match.start(1),
                match.end(1) - match.start(1),
                self.builtin_format,
            )
        for match in self._definition_pattern.finditer(text):
            self.setFormat(
                match.start(1),
                match.end(1) - match.start(1),
                self.definition_format,
            )
        for match in self._number_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        for match in self._string_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
        for match in self._comment_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.comment_format)
        for match in self._decorator_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.decorator_format)

        self._highlight_multiline_string(text)

    def _highlight_multiline_string(self, text: str) -> None:
        state = self.previousBlockState()
        start = 0
        if state in (1, 2):
            marker = '"""' if state == 1 else "'''"
            end = text.find(marker)
            if end == -1:
                self.setFormat(0, len(text), self.string_format)
                self.setCurrentBlockState(state)
                return
            end += 3
            self.setFormat(0, end, self.string_format)
            start = end
            state = 0

        while start < len(text):
            triple_double = text.find('"""', start)
            triple_single = text.find("'''", start)
            candidates = [
                (triple_double, 1, '"""'),
                (triple_single, 2, "'''"),
            ]
            candidates = [item for item in candidates if item[0] != -1]
            if not candidates:
                self.setCurrentBlockState(0)
                return
            index, next_state, marker = min(candidates, key=lambda item: item[0])
            end = text.find(marker, index + 3)
            if end == -1:
                self.setFormat(index, len(text) - index, self.string_format)
                self.setCurrentBlockState(next_state)
                return
            end += 3
            self.setFormat(index, end - index, self.string_format)
            start = end
        self.setCurrentBlockState(0)


class CodeEditor(QPlainTextEdit):
    editor_focused = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.file_path: Path | None = None
        self.encoding = "utf-8"
        self.line_number_area = LineNumberArea(self)
        self.highlighter = PythonHighlighter(self.document())
        self._bracket_pairs = {"(": ")", "[": "]", "{": "}"}
        self._closing_brackets = {value: key for key, value in self._bracket_pairs.items()}
        self._dark = False

        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(11)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setCenterOnScroll(True)
        self.setStyleSheet("QPlainTextEdit { padding: 8px; }")

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._update_extra_selections)
        self._update_line_number_area_width(0)
        self._update_extra_selections()

    def set_theme(self, dark: bool, accent: str) -> None:
        self._dark = dark
        self._accent = QColor(accent)
        self.highlighter.set_theme(dark)
        self.line_number_area.update()
        self._update_extra_selections()

    def set_font_size(self, point_size: int) -> None:
        size = max(8, min(32, int(point_size)))
        font = QFont(self.font())
        font.setPointSize(size)
        self.setFont(font)
        self.document().setDefaultFont(font)
        self.setStyleSheet(
            f"QPlainTextEdit {{ padding: 8px; font-size: {size}pt; }}"
        )
        self.setTabStopDistance(
            self.fontMetrics().horizontalAdvance(" ") * 4
        )
        self._update_line_number_area_width(0)
        self.line_number_area.update()
        self.viewport().update()

    def set_file_content(
        self,
        text: str,
        path: str | Path,
        encoding: str = "utf-8",
    ) -> None:
        self.file_path = Path(path)
        self.encoding = encoding
        self.setPlainText(text)
        self.document().setModified(False)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.setTextCursor(cursor)

    def load_file(self, path: str | Path) -> None:
        data = FileManager.read_text(path)
        self.set_file_content(data.text, data.path, data.encoding)

    def goto_line(self, line_number: int) -> None:
        block = self.document().findBlockByNumber(max(0, line_number - 1))
        if not block.isValid():
            return
        cursor = self.textCursor()
        cursor.setPosition(block.position())
        cursor.movePosition(
            QTextCursor.MoveOperation.EndOfBlock,
            QTextCursor.MoveMode.KeepAnchor,
        )
        self.setTextCursor(cursor)
        self.centerCursor()
        self.setFocus()

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path is not None else self.file_path
        if target is None:
            raise ValueError("当前文件还没有保存路径")
        FileManager.write_text(target, self.toPlainText(), self.encoding)
        self.file_path = target
        self.document().setModified(False)
        return target

    def line_number_area_width(self) -> int:
        digits = max(3, len(str(max(1, self.blockCount()))))
        return 16 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def line_number_area_paint_event(self, event) -> None:  # type: ignore[no-untyped-def]
        painter = QPainter(self.line_number_area)
        painter.fillRect(
            event.rect(),
            QColor("#0B1220" if self._dark else "#F1F5F9"),
        )
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        current_block = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                color = (
                    QColor("#F8FAFC")
                    if self._dark and block_number == current_block
                    else QColor("#64748B")
                    if self._dark
                    else QColor("#0F172A")
                    if block_number == current_block
                    else QColor("#94A3B8")
                )
                painter.setPen(color)
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def _update_line_number_area_width(self, _count: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0,
                rect.y(),
                self.line_number_area.width(),
                rect.height(),
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        content_rect = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                content_rect.left(),
                content_rect.top(),
                self.line_number_area_width(),
                content_rect.height(),
            )
        )

    def focusInEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().focusInEvent(event)
        self.editor_focused.emit(self)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Tab:
            self._indent_selection()
            return
        if event.key() == Qt.Key.Key_Backtab:
            self._unindent_selection()
            return
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._insert_newline_with_indent()
            return
        if event.text() in self._bracket_pairs:
            opening = event.text()
            closing = self._bracket_pairs[opening]
            cursor = self.textCursor()
            cursor.insertText(opening + closing)
            cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
            self.setTextCursor(cursor)
            return
        if event.text() in self._closing_brackets:
            cursor = self.textCursor()
            next_char = self.document().characterAt(cursor.position())
            if next_char == event.text():
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
                self.setTextCursor(cursor)
                return
        super().keyPressEvent(event)

    def _insert_newline_with_indent(self) -> None:
        cursor = self.textCursor()
        line_text = cursor.block().text()
        before_cursor = line_text[: cursor.positionInBlock()]
        indentation = before_cursor[: len(before_cursor) - len(before_cursor.lstrip(" \t"))]
        stripped = before_cursor.rstrip()
        if stripped.endswith(":"):
            indentation += "    "
        cursor.insertText("\n" + indentation)
        self.setTextCursor(cursor)

    def _indent_selection(self) -> None:
        cursor = self.textCursor()
        if not cursor.hasSelection():
            spaces = 4 - (cursor.positionInBlock() % 4)
            cursor.insertText(" " * spaces)
            return
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        while True:
            cursor.insertText("    ")
            end += 4
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
            if cursor.position() > end:
                break
        cursor.setPosition(start + 4)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def _unindent_selection(self) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        while True:
            text = cursor.block().text()
            remove = 4 if text.startswith("    ") else (1 if text.startswith((" ", "\t")) else 0)
            if remove:
                for _ in range(remove):
                    cursor.deleteChar()
                end = max(start, end - remove)
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
            if cursor.position() >= end:
                break
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def _update_extra_selections(self) -> None:
        selections: list[QTextEdit.ExtraSelection] = []
        current_line = QTextEdit.ExtraSelection()
        current_line.format.setBackground(
            QColor("#152033" if self._dark else "#EFF6FF")
        )
        current_line.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        current_line.cursor = self.textCursor()
        current_line.cursor.clearSelection()
        selections.append(current_line)

        match = self._find_matching_bracket()
        if match is not None:
            first, second = match
            for position in (first, second):
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(
                    QColor("#854D0E" if self._dark else "#FDE68A")
                )
                selection.format.setForeground(
                    QColor("#FEF3C7" if self._dark else "#78350F")
                )
                cursor = self.textCursor()
                cursor.setPosition(position)
                cursor.movePosition(
                    QTextCursor.MoveOperation.NextCharacter,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                selection.cursor = cursor
                selections.append(selection)
        self.setExtraSelections(selections)

    def _find_matching_bracket(self) -> tuple[int, int] | None:
        text = self.toPlainText()
        position = self.textCursor().position()
        if position < len(text) and text[position] in self._bracket_pairs:
            return self._scan_forward(text, position)
        if position > 0 and text[position - 1] in self._closing_brackets:
            return self._scan_backward(text, position - 1)
        return None

    def _scan_forward(self, text: str, position: int) -> tuple[int, int] | None:
        opening = text[position]
        closing = self._bracket_pairs[opening]
        depth = 1
        for index in range(position + 1, len(text)):
            if text[index] == opening:
                depth += 1
            elif text[index] == closing:
                depth -= 1
                if depth == 0:
                    return position, index
        return None

    def _scan_backward(self, text: str, position: int) -> tuple[int, int] | None:
        closing = text[position]
        opening = self._closing_brackets[closing]
        depth = 1
        for index in range(position - 1, -1, -1):
            if text[index] == closing:
                depth += 1
            elif text[index] == opening:
                depth -= 1
                if depth == 0:
                    return index, position
        return None
