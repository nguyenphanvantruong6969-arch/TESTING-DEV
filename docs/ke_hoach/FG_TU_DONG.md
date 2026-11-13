# Chạy tự động FG-1 → FG-9, không cần người nhập thêm

> Soạn 2026-11-12 (Opus). Truong yêu cầu: cộng tác viên dán một khối, Claude tự làm hết. Đặc tả việc cần làm:
> `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md` (D1–D4 Truong đã duyệt). Cơ chế chạy dùng lại `it_ui_song_song/TU_DONG.md`.
> Mọi số liệu MÔ PHỎNG; mọi việc trên Forms là TH.

## 1. Cho cộng tác viên (tiếng Việt)

1. Mở **MỘT** phiên Claude Code trên kho `nguyenphanvantruong6969-arch/TESTING-DEV` (tài khoản phải có quyền push).
2. **Chọn model Opus**, chế độ quyền **auto**.
3. Dán đúng khối dưới, gửi. Không cần nhập gì thêm.

```text
Read CLAUDE.md, then docs/ke_hoach/FG_TU_DONG.md and act as CHU_TRI_FG. Truong authorises, for this job only: creating Sonnet worker sessions and sending them messages (if that is refused: the Agent tool with model sonnet), scheduling check-in reminders for this session, creating branch claude/fg-sua and pushing to it, merging claude/fg-sua into claude/forms-gop only under the conditions of section 2.6, running the full test suite, and triggering GitHub Actions workflows on claude/fg-sua; never open, merge or close a PR; never force-push; never touch main; never ask anyone anything. Mode: AUTO. Loop until FG GREEN or FG RED.
```

**Biết là xong khi nào:** dòng 3 của `docs/phien/FG_STATUS.md` trên nhánh `claude/fg-sua` ghi `STATUS: FG GREEN`
(hoặc `FG RED` kèm câu hỏi cho Truong), và dòng cuối tin nhắn cuối của Claude là link tới báo cáo. Gửi link cho Truong.

| Thấy gì | Làm gì |
|---|---|
| Claude in `RESTART` hoặc phiên chết giữa chừng | Mở phiên mới (bước 1–2), dán **lại đúng khối trên**. Phiên mới đọc tệp trạng thái và làm tiếp. |
| Claude báo `FG is RUNNING in another session` | Đã có phiên khác chạy. Đợi 3 giờ rồi dán lại, hoặc báo Truong. |
| Claude vẫn hỏi gì đó | Trả lời: **"Choose the safest option that keeps default behaviour unchanged, record it in FG_STATUS.md, continue."** |
| Claude xin merge PR, đổi nhánh `main` | Trả lời: **"No."** |

## 2. For Claude (English)

### 2.1 What and where
- **WHAT:** items FG-1…FG-9 of `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md`, exactly as specified (§0 rules, §1 decisions
  D1–D4 are FINAL, §1b step 0, §3 items, §5 done-when). Do not re-plan, reorder or add features.
- **Branch:** `claude/fg-sua`, created from `origin/claude/forms-gop` (if it already exists on origin: check it out and
  continue). All FG work goes here. This overrides the spec's line "Branch: claude/forms-gop only": the IT-UI job on
  `claude/forms-gop` is paused mid green loop (`docs/phien/IT_UI_STATUS.md`) and must not be raced.
- Record `BASE = <origin/claude/forms-gop HEAD at start>` in the status file.

### 2.2 Common rules — same as `it_ui_song_song/TU_DONG.md` §2.1, with these substitutions
- Status file **`docs/phien/FG_STATUS.md`** on `claude/fg-sua` (create at start, English, ≤ 150 lines): line 1
  `Mode: CHU_TRI_FG|SOLO_FG`, line 2 lock `RUNNING <role> <session id> <UTC time>`, line 3 `STATUS: …`, then
  `BASE`, `Current step`, `Item table` (FG-n · DONE | GONE-ON-HEAD | BLOCKED | WAIT-TRUONG · commit · tests),
  `Decisions`, `Waiting for Truong`, `Workers`, `Log` (append only). Re-read it before every step; never rely on chat memory.
- **Lock:** same rule (another session's lock younger than 3 h and STATUS not `FG GREEN`/`FG RED` → print
  `FG is RUNNING in another session` + status link, stop).
- **Never ask (overrides CLAUDE.md rule 7 for this job):** a "stop and ask" case → write the question under
  "Waiting for Truong", mark the item `WAIT-TRUONG`, continue with items that do not depend on it. Spec §0 "mark
  BLOCKED, ask" cases (schema change, new library, CSV contract, DA core, FA-M9/FA-M10 code) → `WAIT-TRUONG`, never do them.
- Technical choice not covered by the spec → the safest one that keeps default behaviour byte-identical; record it
  under "Decisions".
- **Never end the turn early.** Commit + push after every item and review (lead: only while no worker runs). If the
  turn must end: commit, push, write the exact next step, then `send_later` (2 min, or 20 min while waiting for a
  worker) with `continue as CHU_TRI_FG from docs/phien/FG_STATUS.md`. `send_later` refused → print
  `RESTART: paste the same prompt again` + status link.
- Env: `LATEST_INSTRUCTION.md` PART 2 §1 (venv, `playwright==1.63.0`, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`,
  unshallow, fetch `origin/main`). Any browser walkthrough uses a workspace folder OUTSIDE the repo.
- Every stopping message ends with a GitHub link to the status file or the final report.

### 2.3 Role CHU_TRI_FG — Opus plans and reviews, Sonnet codes (CLAUDE.md rule 11)
Mechanics exactly as `TU_DONG.md` §2.4 T0–T2 (session creation, check-ins, fallbacks Agent → SOLO_FG, fresh-eyes
review, max 3 fix rounds then BLOCKED), with:
- `get_session`: if the model is not Opus, write `WARNING: lead is not Opus` at the top of the status file, continue.
- Snapshots: before any code, in a worktree of `BASE`, run the generator modes `--fa-daa`, `--fa-daa --mot-bieu-mau`,
  `--phan-hoi`, `--tuan-3` of `mau_forms_thi_clb/tao_mau_forms.py` into the scratchpad; record the folder. Any session
  can rebuild them from `BASE`.
- Worker repo `https://github.com/nguyenphanvantruong6969-arch/testing-dev`, `source_revision` `claude/fg-sua`, latest
  Sonnet model, title `FG <TASK>`.
- **Task order:** `STEP0` (spec §1b: write the failing test of every FG item; green on HEAD → `GONE-ON-HEAD`, delete
  nothing, keep the test only if it adds coverage) → `FG-1` → `FG-3` → `FG-4` → (wave gate 2.4) → `FG-5` → `FG-6` →
  `FG-2` → (wave gate) → `FG-7` → `FG-8` → `FG-9` → (wave gate) → `FINISH`.
  Skip items marked `GONE-ON-HEAD`. Dependencies: FG-6 needs FG-3 and FG-5 (result keys); FG-7 step 4 text needs FG-1;
  everything else independent.
- Review per task: spec section of that item + `git diff <task start>..HEAD` only; rerun its tests (Chromium really
  runs, no `SKIPPED` for `tests/test_giao_dien_*`), confirm the worker's mutation check is in the Log, `soat-ma` tiers
  on that diff, `kiem_nhanh` 7/7.

### 2.4 Wave gate (after each wave)
`git merge origin/claude/forms-gop` into `claude/fg-sua` first (stay current; conflict in a file an FG item owns →
resolve keeping both behaviours; conflict elsewhere → `WAIT-TRUONG`, abort the merge, continue without it). Then:
`ruff check .`; related tests of the wave; `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7, 60/60; snapshot
`diff -r` (after FG-7 only `--sau-ket-qua` may differ); push.

### 2.5 FINISH and green loop — `TU_DONG.md` §2.4 T3, with these substitutions
- Report `docs/phien/bao_cao_dem/<date>_fg_sua.md` (Vietnamese): item table, tests added, decisions, what was
  `GONE-ON-HEAD`, "Waiting for Truong", and the novice walkthrough re-run of spec §5 (steps and result, screenshots
  NOT committed). Update `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, and the FG lines of `docs/phien/claude__forms-gop.md`.
- Green loop gate: full suite with coverage ≥ `fail_under`; GitHub Actions *Tests (rbda-kiosk)* on `claude/fg-sua`
  HEAD; *Build Windows executable (rbda-kiosk)* on `claude/fg-sua`. No Actions access → `CI: not checked (<reason>)`,
  local gate is final.
- **Ownership rule (differs from TU_DONG):** a failure that also fails on `BASE` and lives in FA-M7…FA-M10 files or
  their tests belongs to the paused IT-UI job → record it as `pre-existing (IT-UI)` under "Waiting for Truong" and do NOT
  fix it. The FG gate is: no failure that is new compared with `BASE`, plus every FG test green.
- Fix rules T3 d (never skip/xfail/loosen a test, never lower coverage, never touch snapshots, DA core or schema) and
  guards T3 e apply; end states `FG GREEN` / `FG RED: <failing ids>`.

### 2.6 Hand back to `claude/forms-gop` (only after `FG GREEN`)
Merge `claude/fg-sua` into `claude/forms-gop` and push ONLY if all hold: `docs/phien/IT_UI_STATUS.md` on
`origin/claude/forms-gop` has no lock younger than 3 h; the merge has no conflicts; after the merge `ruff`, the FG tests
and `kiem_nhanh` 7/7 pass on the merged tree. Otherwise leave everything on `claude/fg-sua` and write under "Waiting for
Truong": `merge claude/fg-sua into claude/forms-gop: <reason it was not done>`. Never open a PR.

### 2.7 Worker prompt (Sonnet; lead fills `<TASK>`, appends the fix list for fix rounds)
```text
Read CLAUDE.md, then docs/phien/FG_STATUS.md, then docs/ke_hoach/FG_TU_DONG.md section 2.8. You are a Sonnet worker. Your task: <TASK> from docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md. Mode: AUTO. Truong authorises commits and pushes to claude/fg-sua only; no PR; no Agent tool; never ask. When done, append "WORKER <your session id> <TASK> DONE <short hash>" to the Log of docs/phien/FG_STATUS.md, commit, push, and stop.
```

### 2.8 Worker rules
- Exactly the spec section of `<TASK>`; spec §0 rules apply. Env as 2.2.
- Tests red first (show the red run in the Log line) → minimal code → related tests (UI really run) → mutation check
  (break the fix, see red, restore, `git status` clean) → bookkeeping (CHANGELOG, TIEN_DO) → `ruff check .` →
  `kiem_nhanh` 7/7 → `git pull --rebase origin claude/fg-sua` → commit `FG-n: <what>` → push.
- A case the spec says to ask about → do not do it; write it under "Waiting for Truong", mark `WAIT-TRUONG`, finish the
  rest of the task.
- Context ~300k: write the exact next step under "Current step", commit, push, stop. Never edit the lock line or other
  tasks' log lines.
