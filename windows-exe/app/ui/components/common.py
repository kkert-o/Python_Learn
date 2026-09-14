from __future__ import annotations

from PySide6.QtWidgets import QLayout


def clear_layout(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.hide()
            widget.deleteLater()
        child_layout = item.layout()
        if child_layout is not None:
            clear_layout(child_layout)
