#!/usr/bin/env python3
"""Hook Stop: khi ngữ cảnh vượt ngưỡng (mặc định 400k token), yêu cầu Claude
ghi bàn giao vào docs/phien/<nhánh>.md rồi dừng để mở phiên mới.

Kích thước lấy từ mục `usage` cuối cùng của transcript; không có thì ước bytes/4.
Chặn tối đa một lần mỗi lượt (stop_hook_active). Đổi ngưỡng: biến môi trường HANDOFF_TOKENS,
hoặc trường "nguong" trong `.claude/phien_vai.json` (vai coord/impl/tester, xem docs/phien/T3_GIAO_THUC.md).
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


def doc_vai(goc: str) -> dict:
    """Đọc vai của phiên từ `.claude/phien_vai.json` (không vào git, mỗi container một tệp).

    Dạng: {"vai": "coord" | "impl" | "tester", "coord_id": "session_...", "nguong": 400000}.
    Không có tệp hoặc tệp hỏng: {} (hành vi cũ).
    """
    try:
        with open(os.path.join(goc, ".claude", "phien_vai.json"), encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def nguong_cho(vai: dict) -> int:
    if os.environ.get("HANDOFF_TOKENS"):
        return NGUONG
    try:
        return int(vai.get("nguong") or NGUONG)
    except (TypeError, ValueError):
        return NGUONG


def loi_nhan(vai: dict, nhanh: str, nguong: int) -> str:
    goc = nhanh.replace("/", "__")
    ten_vai = str(vai.get("vai") or "")
    dau = f"Context is over ~{nguong // 1000}k tokens. Hand off now. "
    chung = (
        "rewrite 'Current state', 'Next steps', 'Decisions', 'Files touched', tick the Plan, append one row "
        "to 'Session log'. English, max 150 lines. Commit and push (git pull --rebase first). "
    )
    if ten_vai in ("impl", "tester"):
        tep = f"docs/phien/{goc}__{ten_vai}.md"
        coord = vai.get("coord_id") or "<coordinator id in docs/phien/" + goc + ".md>"
        return (
            dau + f"Update {tep} (create from docs/phien/_TEMPLATE.md if missing): " + chung
            + f"Then send_message to session {coord}: 'HANDOFF {ten_vai} {tep} <commit sha>'. "
            "Do not start new work."
        )
    tep = f"docs/phien/{goc}.md"
    if ten_vai == "coord":
        return (
            dau + f"Update {tep}: " + chung
            + "Then follow 'Coordinator handoff' in docs/phien/T3_GIAO_THUC.md: create_session for the new "
            "coordinator, send_message the new id to every live child, PushNotification to Truong. "
            "Do not start new work."
        )
    return (
        dau + f"Update {tep} (create from docs/phien/_TEMPLATE.md if missing): " + chung
        + "Then tell Truong to open a NEW session with the prompt: "
        f"'Read CLAUDE.md and {tep}, then continue.' Do not start new work."
    )


def main() -> int:
    try:
        du_lieu = json.load(sys.stdin)
    except ValueError:
        du_lieu = {}
    if du_lieu.get("stop_hook_active"):
        return 0
    goc = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    vai = doc_vai(goc)
    nguong = nguong_cho(vai)
    tp = du_lieu.get("transcript_path")
    if not tp or kich_thuoc_ngu_canh(tp) < nguong:
        return 0
    try:
        nhanh = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True, check=True, cwd=goc
        ).stdout.strip() or "unknown"
    except Exception:
        nhanh = "unknown"
    sys.stderr.write(loi_nhan(vai, nhanh, nguong))
    return 2


if __name__ == "__main__":
    sys.exit(main())
