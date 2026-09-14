from __future__ import annotations

import json
import os

import pytest
from PySide6.QtWidgets import QApplication

from app.ai import AiTeacherMode, AiTeacherService, SecureCredentialStore
from app.bootstrap import bootstrap
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme


class FakeAiClient:
    def complete(self, config, messages) -> str:  # type: ignore[no-untyped-def]
        assert "teacher" not in config.api_key
        assert messages
        return "这是来自测试服务端的回答。"


def test_local_teacher_works_without_key(app_paths) -> None:
    context = bootstrap(app_paths)
    service = AiTeacherService(
        context.settings,
        SecureCredentialStore(app_paths.cache_dir / "ai_key.bin"),
    )
    reply = service.ask(
        "为什么出现 NameError？",
        'print(name)',
        AiTeacherMode.TEACHER,
    )
    assert reply.source == "本地引导"
    assert "名称" in reply.content or "变量" in reply.content
    assert "下一步" in reply.content
    assert reply.content.startswith("老师建议")


@pytest.mark.skipif(os.name != "nt", reason="Windows DPAPI only")
def test_dpapi_round_trip_does_not_store_plaintext(tmp_path) -> None:
    store = SecureCredentialStore(tmp_path / "ai_key.bin")
    secret = "sk-test-secret-value"
    store.save(secret)
    assert secret.encode("utf-8") not in store.path.read_bytes()
    assert store.load() == secret
    store.clear()
    assert store.load() is None


def test_remote_client_and_key_are_not_in_settings(app_paths) -> None:
    context = bootstrap(app_paths)
    store = SecureCredentialStore(app_paths.cache_dir / "ai_key.bin")
    service = AiTeacherService(
        context.settings,
        store,
        api_client=FakeAiClient(),
    )
    service.save_config(
        endpoint="https://example.com/chat/completions",
        model="test-model",
        api_key="sk-secret",
    )
    reply = service.ask(
        "解释这个错误",
        "NameError",
        AiTeacherMode.TEACHER,
    )
    assert reply.source == "AI 服务"
    assert "测试服务端" in reply.content
    saved = json.loads(app_paths.settings_path.read_text(encoding="utf-8"))
    assert "sk-secret" not in json.dumps(saved, ensure_ascii=False)
    assert saved["ai_prompt_count"] == 1


def test_ai_teacher_ui_local_mode(app_paths) -> None:
    app = QApplication.instance() or QApplication([])
    context = bootstrap(app_paths)
    apply_theme(app, "light")
    window = MainWindow(context)
    window.show()
    app.processEvents()

    window.navigate(window.PAGE_AI_TEACHER)
    app.processEvents()
    assert window.ai_teacher_screen.mode_combo.count() == 4
    assert window.ai_teacher_screen.endpoint_input.height() >= 38
    assert window.ai_teacher_screen.model_input.height() >= 38
    assert window.ai_teacher_screen.api_key_input.height() >= 38
    window.ai_teacher_screen.endpoint_input.setText("deepseek.com/chat")
    window.ai_teacher_screen._save_config()
    assert window.ai_teacher_screen.config_message.isVisible()
    assert window.ai_teacher_screen.config_message.property("state") == "error"
    window.ai_teacher_screen.endpoint_input.setText(
        "https://api.deepseek.com/chat/completions"
    )
    window.ai_teacher_screen.question_input.setPlainText("NameError 怎么办")
    window.ai_teacher_screen.ask()
    app.processEvents()
    assert "本地引导" in window.ai_teacher_screen.chat.toPlainText()
    assert window.navigation.count() == 13
    window.close()
