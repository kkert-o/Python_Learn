from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


@dataclass(frozen=True, slots=True)
class RobotsAssessment:
    allowed: bool | None
    message: str
    robots_url: str


def assess_robots(
    url: str,
    user_agent: str,
    robots_text: str,
) -> RobotsAssessment:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return RobotsAssessment(None, "请输入完整的 http:// 或 https:// URL。", "")
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse((robots_text or "").splitlines())
    allowed = parser.can_fetch(user_agent or "*", url)
    message = (
        "根据当前 robots 内容，该路径允许这个 User-Agent 访问。"
        if allowed
        else "根据当前 robots 内容，该路径不允许这个 User-Agent 访问。"
    )
    return RobotsAssessment(allowed, message, robots_url)

