# Chạy tự động FA-M7 → FA-M10, không cần người nhập thêm

> Soạn 2026-11-11 (Opus). Truong yêu cầu: "auto and solo mode without any further human input".
> Mọi số liệu MÔ PHỎNG; mọi việc trên Forms là TH.

## 1. Cho Truong (tiếng Việt)

Mở **MỘT** phiên Claude Code trên kho `testing-dev`, quyền **auto**, rồi dán **một** trong hai câu. Sau đó không cần làm
gì nữa. Phiên tự làm, tự soát, tự hẹn giờ quay lại khi phải chờ hoặc khi đầy ngữ cảnh. Chỉ khi phiên in `RESTART`
thì dán lại đúng câu cũ.

| Cách | Model | Nhanh/chậm | Rủi ro | Câu dán |
|---|---|---|---|---|
| **SOLO** (khuyên dùng) | Opus | Chậm hơn (một phiên làm lần lượt) | Thấp: một nhánh, không phải gộp | câu 1 |
| **ĐIỀU PHỐI** | Opus | Nhanh hơn (3 phiên con chạy song song) | Cao hơn: gộp 3 nhánh, cần quyền tạo phiên | câu 2 |

Câu 1 — SOLO:
```text
Read docs/ke_hoach/it_ui_song_song/TU_DONG.md and act as SOLO. Truong authorises commits and pushes to claude/forms-gop only, scheduling check-in reminders for this session, and triggering the Windows build workflow once; never open, merge or close a PR; never force-push; no Agent tool; never ask me anything, just continue until IT-UI DONE.
```

Câu 2 — ĐIỀU PHỐI:
```text
Read docs/ke_hoach/it_ui_song_song/TU_DONG.md and act as DIEU_PHOI. Truong authorises creating three worker sessions (Sonnet) for this job, sending them messages, scheduling check-in reminders for this session, commits and pushes to claude/forms-gop and claude/it-ui-a, claude/it-ui-b, claude/it-ui-c only, and triggering the Windows build workflow once; never open, merge or close a PR; never force-push; no Agent tool; never ask me anything, just continue until IT-UI DONE.
```

Kết thúc khi tệp `docs/phien/IT_UI_STATUS.md` trên `claude/forms-gop` ghi **`IT-UI DONE`** và có link báo cáo.
Câu hỏi Claude để lại cho Truong nằm ở mục "Waiting for Truong" của tệp đó (không chặn công việc).

## 2. For Claude (English)

### 2.1 Common rules (both roles)
- `CLAUDE.md` wins on invariants 1–8. Truong explicitly allows, for THIS job only: one session playing planner, coder
  and reviewer (overrides rule 11), and never asking (overrides rule 7 "stop and ask": write the question under
  "Waiting for Truong", mark the item `WAIT-TRUONG`, continue with items that do not depend on it).
- A choice between technical options → the safest one that keeps default behaviour byte-identical; record it under
  "Decisions" in the status file.
- **Status file** `docs/phien/IT_UI_STATUS.md` on `claude/forms-gop` (create at start, English, ≤ 150 lines):
  line 1 `Mode: SOLO|DIEU_PHOI`, line 2 lock `RUNNING <role> <session id> <UTC time>`, line 3 `STATUS: …`, then
  `Current step`, `Decisions`, `Waiting for Truong`, `Children` (DIEU_PHOI only), `Log` (append only).
  Re-read it before every step: work must never depend on chat memory.
- **Lock:** at start `git fetch origin claude/forms-gop`; if the status file has a lock from ANOTHER session younger
  than 3 h and STATUS is not DONE → print `IT-UI is RUNNING in another session` and stop. Otherwise write your lock.
- **Never end the turn early.** Commit + push after every item and every review. Long context is summarised
  automatically. If the turn must end (tool budget, error, waiting, context ~300k): commit, push, write the exact next
  step in the status file, then `send_later` (2 min when not waiting; 20 min when waiting for children) with message
  `continue as <ROLE> from docs/phien/IT_UI_STATUS.md`. If `send_later` is refused, print
  `RESTART: paste the same prompt again` and the status-file link.
- **Windows build:** once, after G0/FA-M7 are pushed, trigger the workflow *Build Windows executable (rbda-kiosk)* on
  the branch that holds G0 (GitHub MCP `actions_run_trigger`); record the run result. Not possible → record
  "not attempted: <reason>" and continue.
- Every message that stops ends with a GitHub link to the status file (or the final report).

### 2.2 Role SOLO — one session, sequential, branch `claude/forms-gop`
1. Read `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` and `PROMPT_A.md`, `PROMPT_B.md`, `PROMPT_C.md` in this folder. Use
   their "Your job" sections and plan §2–§5 for WHAT to build. **Ignore the parallel-only parts:** separate branches,
   file ownership, marker blocks, fragments `MANH_*.md`, the G0 merge, WAITING states. Work on `claude/forms-gop`;
   bookkeeping (CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET, user guides) directly after each item; handoff = the status file
   plus `docs/phien/claude__forms-gop.md` (tick the Phase 2 boxes).
2. Before any code: generator + converter snapshots (plan §0, PROMPT_B and PROMPT_C first steps) into the scratchpad;
   record the folder in the status file.
3. Order: **G0 → FA-M7 → FA-M9 → FA-M8 → FA-M10**. Per item: tests red first → minimal code → related tests (UI
   really run) → mutation → bookkeeping → `kiem_nhanh` 7/7 → commit + push.
4. **Switch hat after each item — review with fresh eyes:** re-read ONLY that item's spec and `git diff <item start>..HEAD`
   (not your memory), rerun its tests, `soat-ma` tiers on that diff. Finding cao/trung → fix round (max 2) → still
   failing → mark the item BLOCKED with the reason, continue with the next item that does not depend on it
   (FA-M9, FA-M8 depend on FA-M7; FA-M10 depends on FA-M9).
5. Finish = PROMPT_A Phase 3 minus the merges: all related tests, `kiem_nhanh --co-so origin/main --so-seed 20` 60/60,
   snapshot `diff -r` identical, `soat-ma` on `git diff d083aeb..HEAD`, report
   `docs/phien/bao_cao_dem/<date>_it_giao_dien.md` (plan §7), status `IT-UI DONE`, push, verify remote HEAD.

### 2.3 Role DIEU_PHOI — one Opus session runs three Sonnet workers
1. Lock + status file as in 2.1. Create three sessions with `create_session`: model = Sonnet (latest id), repo
   `https://github.com/nguyenphanvantruong6969-arch/testing-dev`, `source_revision` `claude/forms-gop`, same permission
   mode as yours, title `IT-UI worker A|B|C`, prompt = the text block at the top of `PROMPT_A|B|C.md` followed by
   ` Mode: AUTO.` Record the session ids under "Children". Creation refused → switch to Role SOLO (record it).
2. Check-in loop (`send_later` 20 min, never `sleep`): for each child read `get_session` (status_bucket) and line 2 of
   its handoff file on its branch (`git fetch`). Child `failed`, or idle without `STATUS: DONE`/`WAITING_*` → `send_message`
   `continue AUTO from your handoff file` (max 3 per child, then mark it BLOCKED and do its remaining items yourself
   on its branch, following its PROMPT file). Child pushed to another branch name → record it and tell worker A by
   `send_message` before Phase 3.
3. When B and C are DONE and A is `WAITING_B/C` or `DONE_M7` → `send_message` A: `Phase 3 now (B on <branch>, C on <branch>)`.
4. When A reports DONE → **review with fresh eyes** on `claude/forms-gop`: `git diff d083aeb..HEAD`, rerun the related
   tests yourself (Chromium must really run), `kiem_nhanh --so-seed 20` 60/60, snapshot diff, `soat-ma` 4 tiers.
   NEEDS-FIX → `send_message` the owning worker the list (max 2 rounds), then fix the rest yourself on `claude/forms-gop`.
5. GO → status `IT-UI DONE`, report link, push. Do not archive child sessions (Truong decides).
