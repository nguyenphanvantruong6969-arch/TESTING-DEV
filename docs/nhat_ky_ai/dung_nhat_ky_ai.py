"""Dựng docs/nhat_ky_ai/NHAT_KY_AI.md CHỈ từ dữ liệu trong repo (tệp bàn giao, CHANGELOG, git).

Chạy: python docs/nhat_ky_ai/dung_nhat_ky_ai.py   (từ thư mục gốc repo; nên `git fetch origin` trước
để đọc được tệp bàn giao chỉ có trên nhánh khác). Không đọc lịch sử chat, không nhập tay số liệu.
"""
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

REPO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
OUT = REPO / "docs/nhat_ky_ai/NHAT_KY_AI.md"


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout


def cut(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def dmy(iso):
    y, m, d = iso[:10].split("-")
    return f"{d}/{m}/{y}"


TRUONG_RE = re.compile(r"Truong", re.I)
DECIDE_RE = re.compile(r"Truong[^|]{0,25}?(yêu cầu|duyệt|chọn|quyết định|nói|asked|approved|decided|decision|choice|instruction|'s|xác nhận)", re.I)
QUOTE_RE = re.compile(r"Truong[^\n]{0,80}?[\"“«]([^\"”»\n]{3,300})[\"”»]")

# ---------- 1. verbatim quotes kept in the repo (curated; each checked against the file) ----------
CURATED = [
    ("BAN_GIAO.md", "Yêu cầu của Truong", "Suggest other name for “nguyen vong may thi duoc suat” and include any info that can be added and display using a pie chart"),
    ("BAN_GIAO.md", "Nhật ký AI: toàn bộ mã trên do AI (Claude) viết theo yêu cầu của Truong", "use this skill to redesign charts and information in the Result sector to be more friendly and helpful for the adminstrator. Define done as Renovate and help display data better"),
    ("BAN_GIAO.md", "Triệu chứng học sinh báo (lỗi 24, 01/09)", "mới cài, mở lần đầu thì thường bị lỗi backend không kết nối được"),
    ("BAN_GIAO.md", "Học sinh hỏi (lỗi 19, 01/09)", "chạy trên máy khác có ra cùng kết quả không?"),
    ("CHANGELOG.md", "Theo yêu cầu của Truong (28/10/2026, đợt soát A13)", "làm bước cuối"),
    ("docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md", "Bước cuối — skill soat-ma (28/10/2026)", "tiếp"),
    ("docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md", "Soạn 05/11/2026 theo yêu cầu của Truong", "viết prompt và lên kế hoạch nghiên cứu cụ thể các app để bổ sung cho architecture hiện có"),
]
quotes = []
for rel, ctx, q in CURATED:
    txt = re.sub(r"\s+", " ", (REPO / rel).read_text(encoding="utf-8"))
    assert q in txt, (rel, q)  # verbatim check: the quote must exist in the file
    quotes.append((rel, ctx, q))

# ---------- 2. CHANGELOG headings ----------
cl = (REPO / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
heads = []  # (date, title, truong_flag, first_bullet)
for i, line in enumerate(cl):
    m = re.match(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", line)
    if not m:
        continue
    body = []
    for nxt in cl[i + 1: i + 12]:
        if nxt.startswith("## "):
            break
        body.append(nxt)
    text = " ".join(body)
    flag = bool(DECIDE_RE.search(m.group(2)))
    heads.append((m.group(1), m.group(2), flag, text))

# ---------- 3. handoff threads ----------
def parse_handoff(path, branch_hint):
    t = path.read_text(encoding="utf-8")
    goal = ""
    g = re.search(r"^## (Feature / goal|Goal|Mục tiêu)[^\n]*\n(.+?)(?=^## )", t, re.S | re.M)
    if g:
        goal = cut(g.group(2), 420)
    rows = []
    for line in t.splitlines():
        if not re.match(r"^\| 20\d\d-", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        date, model, what = cells[0], cells[1], cells[2]
        note = cells[3] if len(cells) > 3 else ""
        rows.append((date, model, what, note))
    return branch_hint, goal, rows


class _Blob:
    """Tệp bàn giao chỉ có trên nhánh khác (đọc bằng git show)."""

    def __init__(self, name, text):
        self.name, self.stem, self._t = name, name[:-3], text

    def read_text(self, encoding="utf-8"):
        return self._t


local = sorted((REPO / "docs/phien").glob("claude__*.md"))
have = {p.name for p in local}
others = []
for ref in git("for-each-ref", "--format=%(refname:short)", "refs/remotes").split():
    try:
        names = git("ls-tree", "--name-only", ref, "docs/phien/").split()
    except subprocess.CalledProcessError:
        continue
    for n in names:
        base = n.rsplit("/", 1)[-1]
        if base.startswith("claude__") and base.endswith(".md") and base not in have:
            have.add(base)
            others.append(_Blob(base, git("show", f"{ref}:{n}")))

threads = []
for p in local + others:
    name = p.stem.replace("claude__", "")
    branch = "claude/" + name.split("__")[0]
    sub = name.split("__")[1] if "__" in name else ""
    b, goal, rows = parse_handoff(p, branch)
    if rows:
        threads.append((rows[0][0], branch, sub, p.name, goal, rows))
threads.sort(key=lambda x: (x[0], x[1], x[2]))


def is_father(model, what):
    """Cha = Opus lập kế hoạch / điều phối / soát. Con = phiên làm theo kế hoạch (Sonnet, hoặc Opus chạy đêm / impl / tester)."""
    m = model.lower()
    if "opus" not in m and "coord" not in m:
        return False
    return not any(k in m for k in ("night", "impl", "tester"))


# ---------- 4. git sessions ----------
log = git("log", "--all", "--format=%H%x1f%cI%x1f%s%x1f%(trailers:key=Claude-Session,valueonly,separator=%x20)%x1e")
sessions = OrderedDict()
for rec in log.split("\x1e"):
    rec = rec.strip()
    if not rec:
        continue
    h, iso, subj, tr = (rec.split("\x1f") + ["", "", "", ""])[:4]
    m = re.search(r"session_([A-Za-z0-9]+)", tr)
    if not m:
        continue
    sid = m.group(1)[-8:]
    s = sessions.setdefault(sid, {"first": iso, "last": iso, "n": 0, "codes": OrderedDict(), "hash": []})
    s["first"] = min(s["first"], iso)
    s["last"] = max(s["last"], iso)
    s["n"] += 1
    code = re.match(r"^([A-Za-z0-9][A-Za-z0-9.\-+/ ,]{0,30}?):", subj)
    if code:
        for c in re.split(r"[,+ ]+", code.group(1)):
            if c and re.search(r"\d|[A-Z]{2,}", c):
                s["codes"][c] = 1
    if len(s["hash"]) < 3:
        s["hash"].append(h[:7])

n_commits = int(git("rev-list", "--all", "--count").strip())
first_commit = git("log", "--all", "--reverse", "--format=%cI").splitlines()[0]

# ---------- write ----------
L = []
w = L.append
w("# Nhật ký AI của dự án (Phụ lục 1: trích dẫn trợ giúp của AI)")
w("")
w("- **Mục đích:** ghi lại các lần dùng AI (Claude Code) trong dự án, theo `CLAUDE.md` mục *Academic integrity*.")
w("- **Nguồn: CHỈ dữ liệu có trong repo này** — bảng *Session log* của các tệp bàn giao `docs/phien/claude__*.md`,"
  " `CHANGELOG.md`, lịch sử git (nội dung commit và dòng `Claude-Session`), các báo cáo trong `docs/phien/bao_cao_dem/`"
  " và `docs/ke_hoach/`. Không đọc lịch sử chat. Repo chứa việc của cả tài khoản Truong và tài khoản bạn cộng tác.")
w("- **Phiên cha** = phiên lập kế hoạch / điều phối / soát (Opus), nơi Truong giao việc và chốt quyết định."
  " **Phiên con** = phiên làm theo kế hoạch (Sonnet), chỉ tóm tắt một dòng, không chép lời nhắn.")
w("- **Nguyên văn:** chỉ những chữ repo lưu đúng lời Truong (mục 1). Mọi chỗ khác là *theo ghi chép trong repo*"
  " (chép lại dòng ghi chép, có dẫn tệp), không phải lời nhắn nguyên văn. Không đoán, không viết thay.")
w(f"- **Phạm vi:** `CHANGELOG.md` từ {dmy(heads[-1][0])}; lịch sử git từ {dmy(first_commit)} ({n_commits} commit,"
  f" {len(sessions)} phiên có dòng `Claude-Session`). Việc trước đó (08–09/2026) chỉ có trong `BAN_GIAO.md` và"
  " `KE_HOACH_SUA_THIET_KE.md` (mục 5).")
w("- Chỉ nêu sự việc; không có bình luận hay kết luận nghiên cứu (phần đó học sinh tự viết). Mọi số liệu kiểm thử là dữ liệu MÔ PHỎNG.")
w("- Dựng lại: `python docs/nhat_ky_ai/dung_nhat_ky_ai.py` (nên `git fetch origin` trước). Không có số liệu nào nhập tay.")
w("")
w("## 1. Lời Truong được lưu nguyên văn trong repo")
w("")
w("- `docs/ke_hoach/FA_DAA_VISION.md`: bản vision FA-DAA của Truong (08/11/2026), chép nguyên văn vào repo (ghi trong"
  " tệp bàn giao `claude__keen-ride-72sa7t.md`, mục *Files touched*). Không chép lại ở đây; xem tệp gốc.")
for rel, ctx, q in quotes:
    w(f"- `{rel}` — {ctx}: “{q}”")
w("")
w("## 2. Chỉ thị và quyết định của Truong (theo `CHANGELOG.md`)")
w("")
w("Các mục `CHANGELOG.md` có tiêu đề ghi Truong yêu cầu / duyệt / chọn / quyết định. Chép nguyên tiêu đề (ghi chép"
  " của AI trong repo, không phải lời nhắn nguyên văn).")
w("")
for d, title, flag, _ in reversed(heads):
    if flag:
        w(f"- {dmy(d)} — {title}")
w("")
w("## 3. Các luồng việc: phiên cha và phiên con")
w("")
w("Mỗi luồng là một tệp bàn giao (một nhánh). Dòng của phiên cha chép nguyên ô *What was done* của bảng Session log;"
  " phiên con lồng dưới phiên cha gần nhất trước nó, mỗi phiên một dòng tóm tắt.")
w("")
for first, branch, sub, fname, goal, rows in threads:
    tag = f" ({sub})" if sub else ""
    w(f"### {dmy(first)} — `{branch}`{tag}")
    w(f"Nguồn: `docs/phien/{fname}`" if (REPO / "docs/phien" / fname).exists()
      else f"Nguồn: `docs/phien/{fname}` (chỉ có trên nhánh `{branch}`)")
    if goal:
        w(f"Mục tiêu (theo tệp bàn giao): {goal}")
    w("")
    open_father = False
    for date, model, what, note in rows:
        if is_father(model, what):
            w(f"- **{dmy(date)} · Phiên cha · {model}** — theo ghi chép trong repo: {cut(what, 420)}"
              + (f" *({cut(note, 160)})*" if note else ""))
            open_father = True
        else:
            if not open_father:
                w("- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*")
                open_father = True
            w(f"  - Phiên con · {dmy(date)} · {model}: {cut(what, 170)}")
    w("")
w("## 4. Phiên có commit trong git (dòng `Claude-Session`)")
w("")
w("Để đối chiếu: mỗi phiên Claude có commit, mã 8 ký tự cuối, ngày, số commit, mã mục trong tiêu đề commit."
  " Repo không ghi phiên nào là cha hay con.")
w("")
w("| Mã phiên | Từ | Đến | Số commit | Mã mục (theo tiêu đề commit) | Commit ví dụ |")
w("|---|---|---|---|---|---|")
for sid, s in sorted(sessions.items(), key=lambda kv: kv[1]["first"]):
    codes = ", ".join(list(s["codes"])[:8]) or "—"
    w(f"| {sid} | {dmy(s['first'])} | {dmy(s['last'])} | {s['n']} | {codes} | {' '.join(s['hash'])} |")
w("")
w(f"## 5. Trước lịch sử git (trước {dmy(first_commit)}, theo `CHANGELOG.md`)")
w("")
w("Repo không giữ phiên hay commit của giai đoạn này. Nhật ký AI đã có sẵn từ trước:")
w("")
w("- `KE_HOACH_SUA_THIET_KE.md` §11 *AI-log entries for the executed tasks* (27–28/09/2026): bảng việc, tệp AI viết mới,"
  " mã học sinh viết bị sửa. Mẫu ghi nhật ký: cùng tệp §7.")
w("- `BAN_GIAO.md` §2 *Trạng thái hiện tại*: các đoạn \"Nhật ký AI\" theo từng việc (08–09/2026); §6 quy định dùng AI của Sở GD&ĐT.")
w("")
w("Tiêu đề mục `CHANGELOG.md` trước lịch sử git:")
w("")
for d, title, flag, _ in reversed(heads):
    if d < first_commit[:10]:
        w(f"- {dmy(d)} — {title}")
w("")
w("---")
w("Dựng bằng `docs/nhat_ky_ai/dung_nhat_ky_ai.py` (tệp bàn giao, `CHANGELOG.md`, `git log --all`).")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(OUT, len(L), "lines;", len(quotes), "quotes;", sum(h[2] for h in heads), "decisions;",
      len(threads), "threads;", sum(is_father(r[1], r[2]) for t in threads for r in t[5]), "father rows;",
      sum(not is_father(r[1], r[2]) for t in threads for r in t[5]), "son rows;", len(sessions), "git sessions")
