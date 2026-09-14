from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum

from app.ai.models import AiReply
from app.ai.secure_store import SecureCredentialStore
from app.services.settings import SettingsService


class AiTeacherMode(StrEnum):
    TEACHER = "老师模式"
    HINT = "只给思路"
    ERROR_ONLY = "只指出错误"
    DIRECT = "直接答案"


@dataclass(frozen=True, slots=True)
class AiApiConfig:
    endpoint: str
    model: str
    api_key: str
    timeout_seconds: float = 30.0


class AiApiClient:
    def complete(
        self,
        config: AiApiConfig,
        messages: list[dict[str, str]],
    ) -> str:
        payload = json.dumps(
            {
                "model": config.model,
                "messages": messages,
                "temperature": 0.3,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            config.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=config.timeout_seconds,
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"AI 服务返回 HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("无法连接 AI 服务，请检查网络和接口地址。") from exc
        try:
            return str(body["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("AI 服务返回了无法识别的数据。") from exc


class AiTeacherService:
    def __init__(
        self,
        settings: SettingsService,
        credential_store: SecureCredentialStore,
        api_client: AiApiClient | None = None,
    ) -> None:
        self.settings = settings
        self.credential_store = credential_store
        self.api_client = api_client or AiApiClient()

    @property
    def has_api_key(self) -> bool:
        return bool(self.credential_store.load())

    def save_config(
        self,
        *,
        endpoint: str,
        model: str,
        api_key: str | None = None,
    ) -> None:
        endpoint = endpoint.strip()
        model = model.strip()
        if not endpoint.startswith(("https://", "http://")):
            raise ValueError("AI 接口地址必须使用 http:// 或 https://。")
        if not model:
            raise ValueError("模型名称不能为空。")
        self.settings.update(
            {
                "ai_endpoint": endpoint,
                "ai_model": model,
            }
        )
        if api_key is not None and api_key.strip():
            self.credential_store.save(api_key.strip())

    def clear_api_key(self) -> None:
        self.credential_store.clear()

    def ask(
        self,
        question: str,
        context: str,
        mode: AiTeacherMode,
    ) -> AiReply:
        question = question.strip()
        if not question:
            return AiReply("请先描述你想解决的问题。", "本地")
        context = context.strip()[:6000]
        api_key = self.credential_store.load()
        if not api_key:
            return AiReply(self._local_reply(question, context, mode), "本地引导")
        endpoint = str(
            self.settings.get(
                "ai_endpoint",
                "https://api.deepseek.com/chat/completions",
            )
        )
        model = str(self.settings.get("ai_model", "deepseek-chat"))
        messages = [
            {"role": "system", "content": self._system_prompt(mode)},
            {
                "role": "user",
                "content": (
                    f"问题：{question}\n\n"
                    f"用户主动提供的上下文：\n{context or '无'}"
                ),
            },
        ]
        try:
            answer = self.api_client.complete(
                AiApiConfig(endpoint, model, api_key),
                messages,
            )
        except RuntimeError as exc:
            return AiReply(
                self._local_reply(question, context, mode),
                "本地引导",
                str(exc),
            )
        self.settings.set(
            "ai_prompt_count",
            int(self.settings.get("ai_prompt_count", 0)) + 1,
        )
        return AiReply(answer, "AI 服务")

    @staticmethod
    def _system_prompt(mode: AiTeacherMode) -> str:
        prompts = {
            AiTeacherMode.TEACHER: (
                "你是 Python 学习老师。先解释现象和原因，再给下一步提示。"
                "默认不要直接给出完整答案，引导用户自己完成。"
            ),
            AiTeacherMode.HINT: (
                "你只提供分层思路和检查问题，不提完整实现，不写完整代码。"
            ),
            AiTeacherMode.ERROR_ONLY: (
                "你只指出错误类型、可能出现的位置和原因，不提供完整答案。"
            ),
            AiTeacherMode.DIRECT: (
                "你可以给出直接答案，但必须解释关键步骤，并提醒用户运行验证。"
            ),
        }
        return prompts[mode]

    @staticmethod
    def _local_reply(
        question: str,
        context: str,
        mode: AiTeacherMode,
    ) -> str:
        text = f"{question}\n{context}".casefold()
        if "nameerror" in text or "name" in text and "not defined" in text:
            diagnosis = "这通常是变量或函数名拼写不一致，或变量在使用前还没有赋值。"
            steps = (
                "1. 查看报错最后一行的名称。",
                "2. 找到定义它的位置，比较拼写和大小写。",
                "3. 确认它在当前代码块中已经赋值。",
            )
        elif "syntaxerror" in text or "syntax" in text:
            diagnosis = "Python 无法解析代码，常见原因是括号、引号、冒号或运算符写错。"
            steps = (
                "1. 先检查报错行和前一行。",
                "2. 检查括号、引号和冒号是否成对。",
                "3. 判断条件是否误用了赋值号 =。",
            )
        elif "input" in text and ("typeerror" in text or "int" in text):
            diagnosis = "input() 返回字符串，直接与数字计算会触发类型错误。"
            steps = (
                "1. 确认参与计算的值分别是什么类型。",
                "2. 需要整数时使用 int()。",
                "3. 对非法输入增加 try / except 或范围校验。",
            )
        elif "indexerror" in text:
            diagnosis = "代码访问了序列中不存在的位置。"
            steps = (
                "1. 打印 len(sequence)。",
                "2. 确认下标从 0 开始。",
                "3. 避免把长度当成最后一个下标。",
            )
        elif "keyerror" in text:
            diagnosis = "字典中不存在正在读取的键。"
            steps = (
                "1. 检查键名拼写和大小写。",
                "2. 使用 dict.get() 提供默认值。",
                "3. 不确定结构时先打印 keys()。",
            )
        else:
            diagnosis = "先把问题缩小到最小可运行代码，再观察输入、执行过程和输出。"
            steps = (
                "1. 写出期望结果和实际结果。",
                "2. 在关键位置打印变量类型和值。",
                "3. 一次只修改一个地方，然后重新运行。",
            )
        if mode is AiTeacherMode.ERROR_ONLY:
            return f"判断：{diagnosis}"
        if mode is AiTeacherMode.DIRECT:
            return (
                f"判断：{diagnosis}\n"
                "可以直接这样做：按下面的步骤修改，并在每一步后重新运行。\n"
                + "\n".join(steps)
            )
        prefix = "老师建议" if mode is AiTeacherMode.TEACHER else "先想这两个问题"
        return (
            f"{prefix}：{diagnosis}\n\n"
            "下一步：\n"
            + "\n".join(steps)
            + "\n\n完成修改后，把新的报错或输出再发给我。"
        )

