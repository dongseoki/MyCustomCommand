#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


# True: 같은 스레드의 알림 교체
# False: 매번 새로운 알림 생성
REPLACE_THREAD_NOTIFICATION = True


def send_thread_notification(command: list[str], thread_id: str) -> None:
    """스레드별 이전 알림을 교체하고 새 알림 ID를 저장합니다."""
    group = hashlib.sha256(thread_id.encode()).hexdigest()
    cache_root = Path(
        os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    )
    cache_dir = cache_root / "codex-notify"
    cache_dir.mkdir(parents=True, exist_ok=True)
    id_file = cache_dir / f"{group}.id"

    options = ["--print-id"]

    try:
        previous_id = id_file.read_text().strip()
        if previous_id.isdecimal():
            options.append(f"--replace-id={previous_id}")
    except FileNotFoundError:
        pass

    # 옵션은 제목·내용을 구분하는 "--" 앞에 넣습니다.
    notification_id = subprocess.check_output(
        [command[0], *options, *command[1:]],
        text=True,
    ).strip()

    if notification_id.isdecimal():
        id_file.write_text(notification_id)


def main() -> int:
    notification = json.loads(sys.argv[1])
    if notification.get("type") != "agent-turn-complete":
        return 0

    title = (
        f"Codex: "
        f"{notification.get('last-assistant-message') or 'Turn Complete!'}"
    )
    message = " ".join(notification.get("input-messages", []))
    inputs = notification.get("input-messages", [])
    if any(
        text.lstrip().startswith(
            "Generate a concise, single-line task title"
        )
        for text in inputs
    ):
        return 0
    command = [
        "notify-send",
        "--app-name=Codex",
        "--icon=dialog-information",
        "--expire-time=600000",  # 600초 10min
#        "--urgency=critical",
        "--",
        title,
        message or "작업이 완료되었습니다.",
    ]

    if REPLACE_THREAD_NOTIFICATION:
        thread_id = notification.get("thread-id") or "default"
        send_thread_notification(command, thread_id)
    else:
        subprocess.run(command, check=True)

    # 알림 소리 재생
    subprocess.Popen(
        [
            "canberra-gtk-play",
            "-i",
            "message-new-instant",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
