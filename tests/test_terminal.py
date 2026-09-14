from __future__ import annotations

import os

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.ui.components.terminal import TerminalPanel


@pytest.mark.skipif(os.name != "nt", reason="PowerShell terminal is Windows-only")
def test_terminal_runs_powershell_command(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    panel = TerminalPanel(tmp_path)
    panel.input.setText('Write-Output "terminal-ok"')
    panel.submit_command()

    for _ in range(100):
        app.processEvents()
        if "terminal-ok" in panel.output.toPlainText() and not panel._busy:
            break
        QTest.qWait(50)

    assert "terminal-ok" in panel.output.toPlainText()
    assert panel.working_directory == tmp_path.resolve()
    panel.stop()
    panel.deleteLater()


def test_terminal_recognizes_pip_install_commands() -> None:
    assert TerminalPanel._pip_install_args("pip install requests") == [
        "requests"
    ]
    assert TerminalPanel._pip_install_args(
        "py -m pip install pandas==2.2.3"
    ) == ["pandas==2.2.3"]
    assert TerminalPanel._pip_install_args("Get-ChildItem") is None
