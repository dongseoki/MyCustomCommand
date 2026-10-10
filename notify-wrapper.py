#!/usr/bin/env python3
import subprocess
import sys

def main() -> int:
    payload = sys.argv[1]

    commands = [
        [
            "/home/dslee/.nvm/versions/node/v24.21.0/bin/node",
            "/home/dslee/.nvm/versions/node/v24.21.0/lib/node_modules/"
            "oh-my-codex/dist/scripts/notify-hook.js",
            payload,
        ],
        [
            sys.executable,
            "/home/dslee/utils/MyCustomCommand/notify.py",
            payload,
        ],
    ]

    failed = False
    for command in commands:
        try:
            subprocess.run(command, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"알림 실행 실패: {error}", file=sys.stderr)
            failed = True

    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
