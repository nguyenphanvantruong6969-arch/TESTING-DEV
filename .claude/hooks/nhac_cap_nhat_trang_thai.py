#!/usr/bin/env python3
"""Hook Stop: nhắc Claude cập nhật docs/ke_hoach/TRANG_THAI_PHIEN.md.

Chỉ chặn khi cây làm việc có thay đổi (ngoài chính tệp trạng thái) mà tệp
trạng thái chưa được sửa. Chặn tối đa một lần mỗi lượt (stop_hook_active).
"""
import json
import subprocess
import sys

TEP = "docs/ke_hoach/TRANG_THAI_PHIEN.md"


def main() -> int:
    try:
        du_lieu = json.load(sys.stdin)
    except Exception:
        du_lieu = {}
    if du_lieu.get("stop_hook_active"):
        return 0
    try:
        ra = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout
    except Exception:
        return 0
    tep_doi = [d[3:].strip().strip('"') for d in ra.splitlines() if d.strip()]
    if not tep_doi or TEP in tep_doi:
        return 0
    sys.stderr.write(
        f"Cuối lượt: cây làm việc có thay đổi nhưng {TEP} chưa được cập nhật. "
        "Hãy cập nhật tệp đó theo mẫu trong tệp (Việc vừa làm, Trạng thái, "
        "Việc tiếp theo, Quyết định / lưu ý, Lệnh kiểm), rồi kết thúc."
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
