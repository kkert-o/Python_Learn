from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AccessMode(StrEnum):
    PUBLIC_API = "公开 API"
    PUBLIC_PAGE = "公开页面"
    AUTHENTICATED = "自己的登录会话"
    UNKNOWN = "尚未确认"


@dataclass(frozen=True, slots=True)
class CrawlPlan:
    target: str
    purpose: str
    access_mode: AccessMode
    has_authorization: bool
    personal_data: bool
    copyrighted_content: bool
    commercial_use: bool
    bypass_access_control: bool
    reasonable_rate: bool
    retention_days: int


@dataclass(frozen=True, slots=True)
class ComplianceAssessment:
    score: int
    level: str
    findings: tuple[str, ...]
    required_actions: tuple[str, ...]
    starter_code: str


class ComplianceChecker:
    @classmethod
    def assess(cls, plan: CrawlPlan) -> ComplianceAssessment:
        score = 0
        findings: list[str] = []
        actions: list[str] = []
        if plan.bypass_access_control:
            score += 100
            findings.append("计划涉及绕过登录、验证码或访问控制。")
            actions.append("停止该方案，不得绕过访问控制。")
        if not plan.has_authorization:
            score += 40
            findings.append("尚未确认程序化访问权限。")
            actions.append("先阅读服务条款、robots 规则并取得必要授权。")
        if plan.access_mode is AccessMode.UNKNOWN:
            score += 20
            findings.append("访问方式尚未确认。")
            actions.append("改用官方 API，或明确允许程序化访问的页面。")
        if plan.personal_data:
            score += 25
            findings.append("数据可能包含个人信息。")
            actions.append("遵循最小必要原则，过滤无关个人信息并限制保存期限。")
        if not plan.reasonable_rate:
            score += 15
            findings.append("请求频率可能影响对方服务。")
            actions.append("设置延迟、超时、有限重试和最大请求数量。")
        if plan.copyrighted_content:
            score += 10
            findings.append("内容可能受著作权保护。")
            actions.append("只提取完成任务所需的最少信息，不复制和再发布全文。")
        if plan.commercial_use:
            score += 10
            findings.append("计划用于商业用途。")
            actions.append("单独确认商业使用授权和数据来源许可。")
        if plan.retention_days > 180:
            score += 10
            findings.append("数据保存期限较长。")
            actions.append("重新评估保存期限，并设置删除或匿名化策略。")
        score = min(score, 100)
        if score <= 20:
            level = "较低风险"
        elif score <= 55:
            level = "需要进一步确认"
        else:
            level = "高风险，先不要执行"
        if not findings:
            findings.append("目前没有发现明显高风险条件。")
        if not actions:
            actions.append("保留访问记录，按测试数据验证最小实现。")
        return ComplianceAssessment(
            score=score,
            level=level,
            findings=tuple(findings),
            required_actions=tuple(actions),
            starter_code=cls._starter_code(plan),
        )

    @staticmethod
    def _starter_code(plan: CrawlPlan) -> str:
        target = plan.target or "https://example.com/api"
        purpose = plan.purpose or "填写本次数据用途"
        return (
            "# 合规采集起始骨架\n"
            f"# 目标：{target}\n"
            f"# 用途：{purpose}\n"
            f"# 访问方式：{plan.access_mode.value}\n"
            f"# 保存期限：{plan.retention_days} 天\n"
            "import time\n"
            "import urllib.request\n\n"
            "MAX_REQUESTS = 5\n"
            "REQUEST_DELAY_SECONDS = 1.0\n\n"
            "def fetch(url, timeout=8):\n"
            "    request = urllib.request.Request(\n"
            "        url,\n"
            "        headers={\"User-Agent\": \"PythonLearner/1.0\"},\n"
            "    )\n"
            "    with urllib.request.urlopen(request, timeout=timeout) as response:\n"
            "        return response.status, response.read()\n\n"
            "# 先使用 1 到 5 条测试数据验证字段和清洗流程。\n"
            "for index in range(MAX_REQUESTS):\n"
            "    print(\"准备请求测试数据\", index + 1)\n"
            "    time.sleep(REQUEST_DELAY_SECONDS)\n"
        )

