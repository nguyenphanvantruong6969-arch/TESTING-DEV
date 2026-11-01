#!/usr/bin/env python3
"""Hook Stop: khi ngữ cảnh vượt ngưỡng (mặc định 400k token), yêu cầu Claude
ghi bàn giao vào docs/phien/<nhánh>.md rồi dừng để mở phiên mới.

Kích thước lấy từ mục `usage` cuối cùng của transcript; không có thì ước bytes/4.
Chặn tối đa một lần mỗi lượt (stop_hook_active). Đổi ngưỡng: biến môi trường HANDOFF_TOKENS.
"""
import json
import os
import subprocess
import sys

NGUONG = int(os.environ.get("HANDOFF_TOKENS", "400000"))


def kich_thuoc_ngu_canh(duong_dan: str) -> int:
    try:
        with open(duong_dan, "rb") as f:
            bytes_tong = f.seek(0, 2)
            f.seek(max(0, bytes_tong - 400_000))
            cuoi = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return 0
    for dong in reversed(cuoi):
        try:
            d = json.loads(dong)
        except ValueError:
            continue
        u = (d.get("message") or {}).get("usage") if isinstance(d, dict) else None
        if isinstance(u, dict) and "input_tokens" in u:
            return (
                int(u.get("input_tokens") or 0)
                + int(u.get("cache_read_input_tokens") or 0)
                + int(u.get("cache_creation_input_tokens") or 0)
            )
    return bytes_tong // 4


def main() -> int:
    try:
        du_lieu = json.load(sys.stdin)
    except ValueError:
        du_lieu = {}
    if du_lieu.get("stop_hook_active"):
        return 0
    tp = du_lieu.get("transcript_path")
    if not tp or kich_thuoc_ngu_canh(tp) < NGUONG:
        return 0
    try:
        nhanh = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        nhanh = "unknown"
    tep = f"docs/phien/{nhanh.replace('/', '__')}.md"
    sys.stderr.write(
        f"Context is over ~{NGUONG // 1000}k tokens. Hand off now: update {tep} "
        "(create from docs/phien/_TEMPLATE.md if missing): rewrite 'Current state', 'Next steps', "
        "'Decisions', 'Files touched', tick the Plan, append one row to 'Session log'. English, max 150 lines. "
        "Commit and push. Then tell Truong to open a NEW session with the prompt: "
        f"'Read CLAUDE.md and {tep}, then continue.' Do not start new work."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
