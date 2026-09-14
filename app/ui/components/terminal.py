from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import qtawesome as qta


class TerminalPanel(QWidget):
    status_message = Signal(str)

    _MARKER = "__PYLEARNER_COMMAND_DONE__"

    def __init__(
        self,
        working_directory: Path,
        packages_dir: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.working_directory = Path(working_directory)
        self.packages_dir = (
            Path(packages_dir) if packages_dir is not None else None
        )
        self._process: QProcess | None = None
        self._install_process: QProcess | None = None
        self._buffer = ""
        self._busy = False
        self._queued_command: str | None = None
        self._started = False
        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.setInterval(300_000)
        self._timeout.timeout.connect(self._command_timeout)

        header = QHBoxLayout()
        terminal_title = QLabel("PowerShell 终端")
        terminal_title.setObjectName("sectionTitle")
        self.shell_status = QLabel("等待首个命令")
        self.shell_status.setObjectName("mutedText")
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self._clear_output)
        install_button = QPushButton("安装库")
        install_button.clicked.connect(self._prompt_install)
        restart_button = QPushButton("重启")
        restart_button.clicked.connect(self.restart_shell)
        clear_button.setIcon(qta.icon("fa5s.eraser", color="#64748B"))
        install_button.setIcon(qta.icon("fa5s.box-open", color="#2563EB"))
        restart_button.setIcon(qta.icon("fa5s.redo", color="#64748B"))
        header.addWidget(terminal_title)
        header.addWidget(self.shell_status)
        header.addStretch(1)
        header.addWidget(install_button)
        header.addWidget(clear_button)
        header.addWidget(restart_button)

        self.output = QPlainTextEdit()
        self.output.setObjectName("terminalOutput")
        self.output.setReadOnly(True)
        self.output.setPlaceholderText(
            "可执行 pip install requests、py -m pip install 包名、目录切换和普通 PowerShell 命令。"
        )

        self.input = QLineEdit()
        self.input.setObjectName("terminalInput")
        self.input.setPlaceholderText("输入 PowerShell 命令，按 Enter 执行")
        self.input.returnPressed.connect(self.submit_command)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(header)
        layout.addWidget(self.output, 1)
        layout.addWidget(self.input)
        self._write_info(
            "终端尚未启动。输入命令后会自动创建 PowerShell 会话。"
        )

    @property
    def is_running(self) -> bool:
        return (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    def set_working_directory(self, path: str | Path) -> None:
        directory = Path(path).resolve()
        if not directory.is_dir():
            return
        self.working_directory = directory
        if self.is_running:
            self.restart_shell()
        self._write_info(f"终端工作目录：{directory}")

    def submit_command(self) -> None:
        command = self.input.text().strip()
        if not command or self._busy:
            return
        self.input.clear()
        self.output.appendPlainText(f"PS {self.working_directory}> {command}")
        self.status_message.emit(f"终端执行：{command}")
        install_args = self._pip_install_args(command)
        if install_args is not None:
            self._run_package_install(install_args)
            return
        if not self.is_running:
            self._queued_command = command
            self._start_shell()
            return
        self._send_command(command)

    def restart_shell(self) -> None:
        self._cancel_current_command()
        if self._process is not None:
            self._process.kill()
            self._process.waitForFinished(1500)
            self._process.deleteLater()
            self._process = None
        self._busy = False
        self._buffer = ""
        self._started = False
        self.shell_status.setText("等待首个命令")
        self.input.setEnabled(True)
        self._write_info("PowerShell 会话已重启。")

    def stop(self) -> None:
        self._timeout.stop()
        if self._install_process is not None:
            self._install_process.kill()
            self._install_process.waitForFinished(1500)
        if self._process is not None:
            self._process.kill()
            self._process.waitForFinished(1500)

    def _start_shell(self) -> None:
        if os.name != "nt":
            self._write_info("当前系统不支持 PowerShell 终端。")
            self._queued_command = None
            return
        self.shell_status.setText("正在启动")
        process = QProcess(self)
        process.setProgram("powershell.exe")
        process.setArguments(
            ["-NoLogo", "-NoProfile", "-NoExit", "-Command", "-"]
        )
        process.setWorkingDirectory(str(self.working_directory))
        process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )
        process.readyReadStandardOutput.connect(self._read_output)
        process.started.connect(self._shell_started)
        process.finished.connect(self._shell_finished)
        process.errorOccurred.connect(self._shell_error)
        self._process = process
        process.start()

    def _shell_started(self) -> None:
        self._started = True
        self.shell_status.setText("运行中")
        self._write_info("PowerShell 会话已就绪。")
        if self._process is not None:
            self._process.write(
                (
                    "[Console]::OutputEncoding = "
                    "[System.Text.Encoding]::UTF8\n"
                    "$OutputEncoding = [Console]::OutputEncoding\n"
                ).encode("utf-8")
            )
        if self._queued_command:
            command = self._queued_command
            self._queued_command = None
            QTimer.singleShot(80, lambda: self._send_command(command))

    def _send_command(self, command: str) -> None:
        if self._process is None:
            return
        self._busy = True
        self.input.setEnabled(False)
        self.shell_status.setText("执行中")
        self._timeout.start()
        marker_command = (
            f"{command}\n"
            "Write-Output ("
            f'"{self._MARKER}" + '
            "[Convert]::ToBase64String("
            "[Text.Encoding]::UTF8.GetBytes((Get-Location).Path)))\n"
        )
        self._process.write(marker_command.encode("utf-8"))

    def _read_output(self) -> None:
        if self._process is None:
            return
        chunk = bytes(self._process.readAllStandardOutput()).decode(
            "utf-8",
            errors="replace",
        )
        self._buffer += chunk
        while self._MARKER in self._buffer:
            marker_index = self._buffer.index(self._MARKER)
            visible = self._buffer[:marker_index]
            if visible:
                self.output.appendPlainText(visible.rstrip("\n"))
            marker_line_end = self._buffer.find("\n", marker_index)
            if marker_line_end < 0:
                self._buffer = self._buffer[marker_index:]
                return
            marker_line = self._buffer[
                marker_index + len(self._MARKER) : marker_line_end
            ].strip()
            self._buffer = self._buffer[marker_line_end + 1 :]
            self._update_working_directory(marker_line)
            self._finish_command()
        if self._buffer and self._MARKER not in self._buffer:
            self.output.appendPlainText(self._buffer.rstrip("\n"))
            self._buffer = ""

    def _update_working_directory(self, encoded: str) -> None:
        if not encoded:
            return
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return
        path = Path(decoded)
        if path.is_dir():
            self.working_directory = path

    def _finish_command(self) -> None:
        self._timeout.stop()
        self._busy = False
        self.input.setEnabled(True)
        self.shell_status.setText("运行中")
        self.input.setFocus()
        self.status_message.emit("终端命令已完成")

    def _command_timeout(self) -> None:
        self._write_info("命令执行超过 5 分钟，已终止 PowerShell 会话。")
        self.restart_shell()

    def _cancel_current_command(self) -> None:
        self._timeout.stop()
        self._queued_command = None
        self._busy = False
        self.input.setEnabled(True)

    def _shell_finished(self, exit_code: int) -> None:
        self._cancel_current_command()
        self._started = False
        self.shell_status.setText("已停止")
        self._write_info(f"PowerShell 已退出，代码：{exit_code}")

    def _shell_error(self, error) -> None:  # type: ignore[no-untyped-def]
        self._cancel_current_command()
        self.shell_status.setText("启动失败")
        self._write_info(f"PowerShell 启动失败：{error}")

    def _clear_output(self) -> None:
        self.output.clear()

    def _prompt_install(self) -> None:
        package, accepted = QInputDialog.getText(
            self,
            "安装 Python 库",
            "包名（可包含版本，例如 requests 或 pandas==2.2.3）：",
        )
        if accepted and package.strip():
            self._run_package_install([package.strip()])

    @staticmethod
    def _pip_install_args(command: str) -> list[str] | None:
        lowered = command.casefold().strip()
        prefixes = (
            "pip install ",
            "python -m pip install ",
            "py -m pip install ",
        )
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return command[len(prefix) :].strip().split()
        return None

    def _run_package_install(self, packages: list[str]) -> None:
        if not packages:
            return
        if self.packages_dir is None:
            self._write_info("未配置库安装目录。")
            return
        if self._busy:
            self._write_info("当前命令尚未完成。")
            return
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self._busy = True
        self.input.setEnabled(False)
        self.shell_status.setText("安装库中")
        install_process = QProcess(self)
        install_process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )
        install_process.setWorkingDirectory(str(self.working_directory))
        if getattr(sys, "frozen", False):
            worker = Path(sys.executable).with_name("PythonWorker.exe")
            program = str(worker)
            arguments = [
                "--pip-install",
                "--target",
                str(self.packages_dir),
                *packages,
            ]
        else:
            program = sys.executable
            arguments = [
                "-m",
                "app.runtime.worker",
                "--pip-install",
                "--target",
                str(self.packages_dir),
                *packages,
            ]
        install_process.setProgram(program)
        install_process.setArguments(arguments)
        install_process.readyReadStandardOutput.connect(
            self._read_install_output
        )
        install_process.finished.connect(self._install_finished)
        install_process.errorOccurred.connect(self._install_error)
        self._install_process = install_process
        install_process.start()

    def _read_install_output(self) -> None:
        if self._install_process is None:
            return
        text = bytes(
            self._install_process.readAllStandardOutput()
        ).decode("utf-8", errors="replace")
        if text:
            self.output.appendPlainText(text.rstrip("\n"))
            self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _install_finished(
        self,
        exit_code: int,
        _status,
    ) -> None:
        process = self._install_process
        self._install_process = None
        if process is not None:
            process.deleteLater()
        self._busy = False
        self.input.setEnabled(True)
        self.shell_status.setText("运行中")
        if exit_code == 0:
            self._write_info("库安装完成，工作台运行时可以直接导入。")
            self.status_message.emit("Python 库安装完成")
        else:
            self._write_info(f"库安装失败，退出代码：{exit_code}")
            self.status_message.emit("Python 库安装失败")
        self.input.setFocus()

    def _install_error(self, error) -> None:  # type: ignore[no-untyped-def]
        self._write_info(f"无法启动库安装程序：{error}")
        self._busy = False
        self.input.setEnabled(True)
        self.shell_status.setText("安装失败")

    def _write_info(self, text: str) -> None:
        self.output.appendPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)
