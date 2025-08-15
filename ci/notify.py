import glob
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

import requests


def _env(*names: str, default: Optional[str] = None) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def parse_junit_report(path: str) -> dict:
    result = {"total": 0, "failed": 0, "skipped": 0, "time": 0.0}
    if not os.path.exists(path):
        return result

    tree = ET.parse(path)
    root = tree.getroot()

    # Support both <testsuite> and <testsuites>
    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall("testsuite")

    for suite in suites:
        result["total"] += int(suite.attrib.get("tests", 0))
        result["failed"] += int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
        result["skipped"] += int(suite.attrib.get("skipped", 0))
        try:
            result["time"] += float(suite.attrib.get("time", 0.0))
        except ValueError:
            pass

    return result


def build_message(summary: dict) -> str:
    project = _env("CI_PROJECT_NAME") or ""
    branch = _env("CI_COMMIT_BRANCH") or ""
    short_sha = _env("CI_COMMIT_SHORT_SHA") or ""
    pipeline_id = _env("CI_PIPELINE_ID") or ""
    job_url = _env("CI_JOB_URL") or ""

    total = summary["total"]
    failed = summary["failed"]
    skipped = summary["skipped"]
    passed = max(0, total - failed - skipped)
    duration = summary["time"]

    status_emoji = "🟢" if failed == 0 else "🔴"

    lines = [
        f"{status_emoji} <b>Тестирование завершено</b>",
    ]

    meta = []
    if project:
        meta.append(f"Проект: <code>{project}</code>")
    if branch:
        meta.append(f"Ветка: <code>{branch}</code>")
    if short_sha:
        meta.append(f"Коммит: <code>{short_sha}</code>")
    if pipeline_id:
        meta.append(f"Пайплайн: <code>#{pipeline_id}</code>")
    if job_url:
        meta.append(f"Ссылка на джоб: {job_url}")
    if meta:
        lines.append("\n".join(meta))

    lines.extend(
        [
            "",
            f"Всего тестов: <b>{total}</b>",
            f"Пройдено: <b>{passed}</b>",
            f"Провалено: <b>{failed}</b>",
            f"Пропущено: <b>{skipped}</b>",
            f"Длительность: <b>{duration:.2f}s</b>",
        ]
    )

    return "\n".join(lines)


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def send_telegram_document(token: str, chat_id: str, file_path: str, caption: Optional[str] = None) -> None:
    if not os.path.exists(file_path):
        return
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(file_path, "rb") as f:
        files = {"document": (os.path.basename(file_path), f)}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
            data["parse_mode"] = "HTML"
        resp = requests.post(url, data=data, files=files, timeout=60)
        resp.raise_for_status()


def main() -> int:
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured; skipping notification.")
        return 0

    junit_path = "report.xml"
    summary = parse_junit_report(junit_path)
    message = build_message(summary)

    try:
        send_telegram_message(token, chat_id, message)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to send Telegram message: {exc}")
        return 1

    # Attach latest text report if present
    txt_reports = sorted(glob.glob("Test report/test_results_*.txt"))
    latest_txt = txt_reports[-1] if txt_reports else None

    try:
        if latest_txt:
            send_telegram_document(token, chat_id, latest_txt, caption="Текстовый отчет")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to send text report: {exc}")

    try:
        if os.path.exists(junit_path):
            send_telegram_document(token, chat_id, junit_path, caption="JUnit XML")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to send JUnit report: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())