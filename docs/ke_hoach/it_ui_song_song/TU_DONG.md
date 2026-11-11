# Chạy tự động FA-M7 → FA-M10, không cần người nhập thêm

> Soạn 2026-11-11 (Opus). Truong yêu cầu: "auto and solo mode without any further human input".
> Mọi số liệu MÔ PHỎNG; mọi việc trên Forms là TH.

## 1. Cho Truong (tiếng Việt)

**Cách chính (Truong chốt 2026-11-11): Opus chủ trì, giao việc cho Sonnet, xong thì lặp tới khi mọi test xanh.**
Mở **MỘT** phiên Claude Code trên kho `testing-dev`, **chọn model Opus**, quyền **auto**, dán đúng câu dưới, gửi. Không
cần nhập gì nữa. Phiên Opus tự tạo phiên Sonnet cho từng mục, tự soát, tự sửa, tự hẹn giờ quay lại, rồi chạy vòng
"xanh": toàn bộ test + độ phủ ≥ 85 % + CI trên GitHub + bản build Windows, lặp sửa tới khi tất cả đạt.

```text
Read docs/ke_hoach/it_ui_song_song/TU_DONG.md and act as CHU_TRI. Truong authorises, for this job only: creating Sonnet worker sessions and sending them messages (if that is refused: the Agent tool with model sonnet), scheduling check-in reminders for this session, commits and pushes to claude/forms-gop only, running the full test suite, and triggering the Windows build workflow; never open, merge or close a PR; never force-push; never touch main; never ask me anything; loop until IT-UI GREEN.
```

Kết thúc khi `docs/phien/IT_UI_STATUS.md` trên `claude/forms-gop` ghi **`IT-UI GREEN`** kèm link báo cáo. Chỉ khi phiên
in `RESTART` mới dán lại đúng câu cũ. Câu hỏi để lại cho Truong (không chặn việc): mục "Waiting for Truong".

Cách dự phòng (vẫn tự động): `act as SOLO` (một phiên tự làm hết) hoặc `act as DIEU_PHOI` (ba phiên con song song) —
xem §2.2, §2.3; câu dán giống câu trên, thay `CHU_TRI` và bỏ phần "creating Sonnet worker sessions".

## 2. For Claude (English)

### 2.1 Common rules (every role)
- `CLAUDE.md` wins on invariants 1–8. Truong explicitly allows, for THIS job only: (SOLO only) one session playing planner,
  coder and reviewer (overrides rule 11; CHU_TRI and DIEU_PHOI keep it: Opus plans/reviews, Sonnet codes), and never asking (overrides rule 7 "stop and ask": write the question under
  "Waiting for Truong", mark the item `WAIT-TRUONG`, continue with items that do not depend on it).
- A choice between technical options → the safest one that keeps default behaviour byte-identical; record it under
  "Decisions" in the status file.
- **Status file** `docs/phien/IT_UI_STATUS.md` on `claude/forms-gop` (create at start, English, ≤ 150 lines):
  line 1 `Mode: CHU_TRI|SOLO|DIEU_PHOI`, line 2 lock `RUNNING <role> <session id> <UTC time>`, line 3 `STATUS: …`, then
  `Current step`, `Decisions`, `Waiting for Truong`, `Children` (DIEU_PHOI only), `Log` (append only).
  Re-read it before every step: work must never depend on chat memory.
- **Lock:** at start `git fetch origin claude/forms-gop`; if the status file has a lock from ANOTHER session younger
  than 3 h and STATUS is not `IT-UI GREEN` / `IT-UI RED` → print `IT-UI is RUNNING in another session` and stop. Otherwise write your lock.
- **Never end the turn early.** Commit + push after every item and every review (CHU_TRI: only while no worker runs). Long context is summarised
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
   `docs/phien/bao_cao_dem/<date>_it_giao_dien.md` (plan §7), push.
6. Then run the green loop of §2.4 T3 yourself (you are the fixer; fix rules T3 d and guards T3 e apply) until
   `IT-UI GREEN` (or `IT-UI RED` by the guards).

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
5. GO → run the green loop of §2.4 T3 (delegate `FIX-N` to worker A via `send_message`, or a new Sonnet session)
   until `IT-UI GREEN` (or `IT-UI RED` by the guards); report link, push. Do not archive child sessions.

### 2.4 Role CHU_TRI — Opus plans, delegates EVERY code change to Sonnet, reviews, then loops until green
Opus never edits code or tests itself (rule 11), except as the last fallback below. Opus writes only the status file.
**T0 Setup.** `get_session` (no id): `session_context.model` must be an Opus model; if not, write
`WARNING: chủ trì không phải Opus (<model>)` at the top of the status file and continue. Lock + status file (§2.1),
`Mode: CHU_TRI`. Record `BASE = <current HEAD of origin/claude/forms-gop>`. Env setup exactly as
`LATEST_INSTRUCTION.md` PART 2 §1 (venv, `playwright==1.63.0`, unshallow, `origin/main`), branch `claude/forms-gop`.
**Snapshots** are always rebuilt from `BASE` in a worktree (`git worktree add <scratch>/base $BASE`) by running the
generator modes of plan §0 and the converter commands of PROMPT_B there, so every session can re-create them.
**T1 Delegate, one task at a time** (sequential, one branch, no merges). Tasks in order:
`G0` (PROMPT_A job 1) → `FA-M7` (plan §2 + PROMPT_A job 2) → `FA-M9` (plan §3 + PROMPT_B FA-M9 parts) →
`FA-M8` (plan §4 + PROMPT_C) → `FA-M10` (plan §5 + PROMPT_B FA-M10 parts) → `FINISH` (plan §7 report).
For each task send the worker prompt (§2.5) with `<TASK>` filled in:
1. `create_session`: model = latest Sonnet id, repo `https://github.com/nguyenphanvantruong6969-arch/testing-dev`,
   `source_revision` `claude/forms-gop`, same permission mode as yours, title `IT-UI <TASK>`. Record the id.
   Wait with `send_later` check-ins every 20 min (never `sleep`): done ⇔ the status-file Log on `origin/claude/forms-gop`
   has `WORKER … <TASK> DONE`. `get_session` failed / idle without that line → `send_message`
   `continue <TASK> from docs/phien/IT_UI_STATUS.md` (max 3), then a NEW worker session for the same task.
2. `create_session` refused → Agent tool, `model: "sonnet"`, `run_in_background: false`, same prompt.
3. Both refused → do the task yourself under SOLO rules (§2.2) and record `fallback: SOLO for <TASK>`.
While a worker runs, do not commit or push (avoid races); keep notes in your scratchpad.
**T2 Review each task with fresh eyes** (only spec + `git diff <task start>..HEAD`, never memory): rerun its tests
(Chromium really runs), check its mutation was recorded, `soat-ma` tiers on that diff, `kiem_nhanh` 7/7.
NEEDS-FIX → send the numbered fix list to the same worker (`send_message`, or a new Agent call), max 3 rounds, then
`BLOCKED <TASK>: <reason>` and continue with tasks that do not depend on it (M8, M9 need M7; M10 needs M9).
**T3 Green loop ("VÒNG XANH")** — starts after `FINISH` (or after every non-blocked task is done). One round:
a. `git pull --rebase`. Local gate, all must pass:
   - `ruff check .`
   - full suite with coverage, in the background (`run_in_background`, ~25–40 min):
     `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q -rs --cov --cov-report=term` → 0 failed,
     0 errors, total coverage ≥ `fail_under` in `pyproject.toml` (85), and NO `SKIPPED` line for `tests/test_giao_dien_*`;
   - `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7, 60/60;
   - snapshot `diff -r` vs `BASE` for every existing generator/converter mode → identical.
b. Gate green → push, then wait for GitHub Actions *Tests (rbda-kiosk)* on that exact HEAD (`actions_list` /
   `actions_get`, check-ins every 15 min): every job green (Linux full + UI, ruff, Windows tests). Then trigger
   *Build Windows executable (rbda-kiosk)* (`actions_run_trigger`, ref `claude/forms-gop`) and wait until it is green.
   No GitHub Actions access → record `CI: not checked (<reason>)` and treat the local gate as final.
c. Anything red → collect the exact failing test ids, messages and CI logs (`get_job_logs`), write them under
   `Green loop round N` in the status file, delegate ONE task `FIX-N` to Sonnet (T1 mechanics) with that list. Then
   review it (T2) and start the next round.
d. Fix rules for every worker (put them in the `FIX-N` prompt): reproduce the failure first and show it red; minimal
   fix of the cause; **never** skip, xfail, delete, loosen or rewrite the expectation of a test to make it pass, never
   lower `fail_under`, never edit snapshot/byte-identical expectations, never touch DA core or schema. Low coverage →
   add real tests for the new code. A failure that also fails on `origin/main` is still fixed (Truong: every test
   green); record it as `pre-existing`. A test that passes on rerun → run it 3× more; inconsistent = flaky → fix the
   flakiness (waits, ordering), never retry-until-pass.
e. Guards so the loop always ends: same failing set in 2 consecutive rounds → Opus writes a root-cause analysis and a
   precise fix spec before the next `FIX`; 3 identical rounds or 8 rounds in total → stop with
   `IT-UI RED: <failing ids>` + the analysis + one question per failure under "Waiting for Truong", push, last line the
   status link.
f. All of a and b green in the same round → update the report (`docs/phien/bao_cao_dem/<date>_it_giao_dien.md`): passed
   count, coverage %, 60/60, CI run links, Windows build result; status `IT-UI GREEN`; push; verify remote HEAD =
   local HEAD; last line = report link.

### 2.5 Worker prompt (Sonnet; CHU_TRI fills `<TASK>` and, for FIX tasks, appends the failure list)
```text
Read CLAUDE.md, then docs/phien/IT_UI_STATUS.md, then docs/ke_hoach/it_ui_song_song/TU_DONG.md section 2.6. You are a Sonnet worker. Your task: <TASK>. Mode: AUTO. Truong authorises commits and pushes to claude/forms-gop only; no PR; no Agent tool; never ask. When done, append "WORKER <your session id> <TASK> DONE <short hash>" to the Log of docs/phien/IT_UI_STATUS.md, commit, push, and stop.
```

### 2.6 Worker rules
- WHAT to build: the task's sources named in §2.4 T1 (plan section + the PROMPT_A/B/C "Your job" part). Ignore the
  parallel-only parts (separate branches, file ownership, marker blocks, `MANH_*.md`, G0 merge, WAITING states):
  everything is on `claude/forms-gop`; bookkeeping (CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET, user guides) directly.
- Env: `LATEST_INSTRUCTION.md` PART 2 §1 (venv, playwright 1.63.0, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).
- Per task: tests red first → minimal code → related tests (UI really run) → mutation → bookkeeping → `ruff check .`
  → `kiem_nhanh` 7/7 → `git pull --rebase origin claude/forms-gop` → commit (message starts with the task code) → push.
- AUTO rules of PROMPT_A/B/C apply (never ask; questions under "Waiting for Truong"; safest technical choice).
- Context ~300k: write the exact next step under "Current step" in the status file, commit, push, stop; CHU_TRI starts a
  fresh worker. Never edit the lock line or another task's log lines.

