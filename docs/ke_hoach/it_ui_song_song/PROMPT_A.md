# PROMPT A — Nền (G0) + FA-M7 + tích hợp — gửi cho một cộng tác viên

> **Cho cộng tác viên (tiếng Việt):** mở MỘT phiên Claude Code trên kho `testing-dev`, **chọn model Opus**, quyền
> **auto**, dán đúng khối dưới, gửi. Không cần nhập gì thêm: Opus tự giao việc code cho Sonnet, tự soát, tự hẹn giờ
> quay lại, rồi lặp tới khi mọi test xanh. Chạy ĐỒNG THỜI với hai người kia (B và C). Chỉ khi phiên in `RESTART` thì
> dán lại đúng khối cũ. Xong khi dòng 2 của `docs/phien/claude__it-ui-a.md` trên nhánh `claude/it-ui-a` ghi `STATUS: GREEN`
> (người A: `docs/phien/IT_UI_STATUS.md` trên `claude/forms-gop` ghi `IT-UI GREEN`).
> Soạn 2026-11-11 (Opus). Truong duyệt. TH = chưa thử trên Microsoft thật; số liệu MÔ PHỎNG.

```text
Read CLAUDE.md, then docs/ke_hoach/it_ui_song_song/PROMPT_A.md and act as CHU_TRI for worker A. Truong authorises, for this job only: creating Sonnet worker sessions and sending them messages (if that is refused: the Agent tool with model sonnet), scheduling check-in reminders for this session, commits and pushes to claude/it-ui-a and, in Phase 3, claude/forms-gop, running the full test suite, and triggering the Windows build workflow; never open, merge or close a PR; never force-push; never touch main; never ask anyone anything. Mode: AUTO. Loop until STATUS: GREEN.
```

## How this file runs (CHU_TRI for worker A)
You are the Opus lead for worker A. Follow "Roles: Opus lead + Sonnet coder" in the shared contract below.
Your task list, in order (WHAT each task builds = "Your job" below + the plan sections it names):
`G0` (job 1) → `FA-M7` (job 2) → green loop on `claude/it-ui-a` → wait for B and C → `INTEGRATE` (job 3: merges, marker conflicts, `tao_i18n_js.py`, fold `MANH_*.md`) → green loop on `claude/forms-gop` → `FINISH` (plan §7 report).

## Your job (worker A)
1. **G0 groundwork — FIRST, push before anything else.** Create branch `claude/it-ui-a` from `origin/claude/forms-gop`.
   Build exactly the "Code contract" below: `forms_dot.py`; `api_forms.py` with `FormsMixin` (`get_fa_duong`,
   `dat_fa_duong`); empty stubs `api_forms_nap.py` (`class FormsNapMixin: pass` + module docstring "owner: worker B")
   and `api_forms_bo.py` (`FormsBoMixin`, "owner: worker C"); register all three in `PipelineAPI`; `kiosk.spec`
   (pathex + hiddenimports for every `mau_forms_thi_clb` module the three workers use: `bieu_mau`, `so_de_thi`,
   `tao_mau_forms`, `chuyen_forms_sang_phan_mem`, `chuyen_phieu_clb`, `phan_tich_cau_hoi`, `danh_sach_chua_dang_ky`,
   `doi_chieu_lists`, `ghep_ket_qua_email`, `tao_bo_dung_t4m`; `bo_dung_t4m/` in datas if read at run time); check no
   module-name clash with root modules; tab "Chuẩn bị đợt" + `#cb-buoc-1..5` + path radio A/B; `js/11_chuan_bi.js`
   with `window.ChuanBi`; empty stubs `js/12_chuan_bi_nap.js`, `js/13_chuan_bi_bo.js` (one comment line "owner: worker
   B/C"); all three JS files in `js/_danh_sach.txt`; all error codes listed in the contract (vi + en) and marker pairs
   in every shared file; `MA_MOI_SAU_ANH_CHUP` updated; `python tao_i18n_js.py`.
   Tests first: `tests/test_fa_m7_dong_goi.py` (spec lists every module imported by the three `api_forms*.py` files and
   `forms_dot.py`; each imports through `nap_mau_forms()`; `forms_dot` paths under the db folder),
   `tests/test_fa_m7_duong.py` (`dat_fa_duong` "A"/"B" ok, other value → error; stored in rules; allocation results
   unchanged), `tests/test_giao_dien_fa_m7_the.py` (tab visible only with FA-DAA on; path radio saves). Update only the
   expected counts in existing nav-count UI tests. `kiem_nhanh` 7/7. Commit message starts `FA-M7 G0:`. Push.
2. **FA-M7** = plan §2 (steps "1. CLB" and "2. Đề thi"), using `forms_dot` paths. APIs `nap_phieu_clb`,
   `tai_mau_de_thi`, `nap_de_thi` in `api_forms.py`; new module `mau_forms_thi_clb/so_de_thi.py`. Tests and mutation
   as in plan §2. Bookkeeping into your own fragment `MANH_A.md` (folded in Phase 3). Push. Handoff `STATUS: DONE_M7`; then the green loop on `claude/it-ui-a` before Phase 3.
3. **Phase 3 integration** (see "Sync points"). Check B and C: `git fetch origin claude/it-ui-b claude/it-ui-c`, read
   line 2 of their handoff files on those branches. Both `STATUS: GREEN` (or `RED`/`BLOCKED` after waiting per AUTO) → integrate. Otherwise handoff
   `STATUS: WAITING_B/C` and wait with `send_later` check-ins per the AUTO rules (no human restarts you).
   The Windows build of the green loop (step b) proves the `.exe` builds with `mau_forms_thi_clb` inside.
   Then the green loop on `claude/forms-gop`, final report per plan §7, `IT-UI GREEN` in `docs/phien/IT_UI_STATUS.md`.

## Not yours
Steps 3–5 of the tab, generator changes (C), converter / import / after-allocation buttons (B). Requests from B or C
arrive as lines "REQUEST A:" in their handoff files — read them at Phase 3 (or at G0 time if already pushed).

## Shared contract (IDENTICAL in PROMPT_A, PROMPT_B, PROMPT_C — do not change it alone)

### Workers, branches, base
| Worker | Items | Branch (push only here) |
|---|---|---|
| A | G0 groundwork, FA-M7, then integration (Phase 3) | `claude/it-ui-a` |
| B | FA-M9, FA-M10 | `claude/it-ui-b` |
| C | FA-M8 | `claude/it-ui-c` |
All three branch from `origin/claude/forms-gop` (current HEAD when you start; record it as `BASE`). If your environment forces a
different branch name, use it and write it on line 1 of your handoff file. Never force-push. Never push to another
worker's branch or to `main`. No PR. No subagents (CLAUDE.md rule 10). All numbers SIMULATED; all Forms work TH.
Item details: `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` (§2 FA-M7, §3 FA-M9, §4 FA-M8, §5 FA-M10). Where this file and
that plan differ, THIS file wins (it adds the parallel split; §1 of the plan is now G0 of worker A).

### File ownership (only the owner edits a file; anything else → write it in your handoff as a request)
| Owner | Files |
|---|---|
| A | `forms_dot.py` (new), `api_forms.py` (new), `api.py` (mixin line), `kiosk.spec`, `index.html`, `js/11_chuan_bi.js` (new), `js/_danh_sach.txt`, `mau_forms_thi_clb/so_de_thi.py` (new), `mau_forms_thi_clb/chuyen_phieu_clb.py`, nav-count UI tests, `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, `docs/ke_hoach/CLAUDE_CHI_TIET.md`, `HUONG_DAN_SU_DUNG.md`, `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md`, `i18n_loi.js` (regenerated only at integration) |
| B | `api_forms_nap.py` (stub by A in G0, then B), `js/12_chuan_bi_nap.js` (stub by A, then B), `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`, `mau_forms_thi_clb/ghep_ket_qua_email.py`, `mau_forms_thi_clb/danh_sach_chua_dang_ky.py`, `mau_forms_thi_clb/doi_chieu_lists.py` |
| C | `api_forms_bo.py` (stub by A, then C), `js/13_chuan_bi_bo.js` (stub by A, then C), `mau_forms_thi_clb/tao_mau_forms.py`, `mau_forms_thi_clb/bieu_mau.py`, `mau_forms_thi_clb/phan_tich_cau_hoi.py` (read-only unless needed for FA-M8) |
| Shared, marker blocks only | `i18n_errors.py`, `i18n.js` (vi AND en), `tests/test_ws_nhan.py` (`MA_MOI_SAU_ANH_CHUP`), `style.css` |
Shared files: A creates, in G0, one marker pair per worker in each shared file, separated by at least one unchanged
line, e.g. `# === B: FA-M9/M10 — add below ===` … `# === end B ===` (JS/CSS: `/* … */`). Each worker inserts ONLY
between its own pair. After editing `i18n_errors.py` run `python tao_i18n_js.py` and commit `i18n_loi.js` (kiem_nhanh
checks it); conflicts in that generated file are resolved at integration by regenerating, never by hand.
New test files: each worker's own `tests/test_fa_m7_*.py` (A), `test_fa_m9_*`/`test_fa_m10_*` (B), `test_fa_m8_*` (C),
and `tests/test_giao_dien_fa_m<same>_*.py`. Never edit another worker's test file.
Bookkeeping: B and C do NOT edit CHANGELOG/TIEN_DO/CLAUDE_CHI_TIET/user guides. Each writes a fragment
`docs/ke_hoach/it_ui_song_song/MANH_<A|B|C>.md` (CHANGELOG entry text, TIEN_DO row, code-map rows, test-file count,
user-guide paragraph in plain Vietnamese). A folds all fragments in at integration.

### Code contract (A builds it in G0; B and C code against it)
`forms_dot.py` (root module, pure, no UI):
- `nap_mau_forms() -> str`: put `mau_forms_thi_clb/` on `sys.path` (from source or from `sys._MEIPASS`), idempotent.
- `thu_muc_forms(db_path)` = `<dir of app.db>/forms/` (created). Sub-paths, all created on demand:
  `duong_de_dot(db_path)` → `forms/de_thi.json`; `duong_so_nhap_clb_dot(db_path)` → `forms/SO_NHAP_CLB_CLB.xlsx`;
  `thu_muc_nap(db_path)` → `forms/nap/`; `thu_muc_tai_len(db_path)` → `forms/nap/tai_len/`;
  `duong_email_ma_hs(db_path)` → `forms/nap/EMAIL_MA_HS.csv`; `thu_muc_bieu_mau(db_path)` → `forms/bieu_mau/`.
- `doc_de_dot(db_path) -> dict`: `bieu_mau.doc_de_thi(duong_de_dot(db_path))`; missing file → `FileNotFoundError`
  (APIs map it to `forms_chua_co_de`; missing club file → `forms_chua_co_clb`).
Mixins registered by A in `PipelineAPI`: `FormsMixin` (`api_forms.py`, A), `FormsNapMixin` (`api_forms_nap.py`, B),
`FormsBoMixin` (`api_forms_bo.py`, C). Path choice: `rules.fa_duong` ∈ {"A","B"}; API `get_fa_duong()` /
`dat_fa_duong(duong)` (A); B and C read it via `self._luat_nghiem().get("fa_duong")` and fail with
`forms_duong_chua_chon` when absent.
UI: tab `data-tab="chuan_bi"` (A) with containers `#cb-buoc-1` … `#cb-buoc-5` in `index.html`. `js/11_chuan_bi.js`
exposes `window.ChuanBi = { duong(), dangKyBuoc(so, veFn), lamMoi() }`; step 3 is drawn by C's `js/13_chuan_bi_bo.js`,
steps 4–5 by B's `js/12_chuan_bi_nap.js`, each calling `ChuanBi.dangKyBuoc(...)` once.
Error codes A adds in G0 (vi + en, also into `MA_MOI_SAU_ANH_CHUP`): `forms_duong_chua_chon`, `forms_chua_co_clb`,
`forms_chua_co_de`, `phieu_clb_tep_sai`(detail), `de_thi_tep_sai`(detail), `forms_khong_chuyen_duoc`(detail),
`forms_tep_khong_nhan_ra`(ten), `forms_tep_sai_duong`(ten, duong), `forms_tep_sau_ket_qua`(ten),
`forms_can_chon_de`(ten), `forms_thieu_email`, `forms_thieu_danh_sach_lop`(detail), `forms_tao_bo_loi`(detail).
More codes → your own marker block. UI string key prefixes: A `cb_`, B `cb_nap_`, C `cb_bo_`.

### Sync points
- **G0** (A, first commit, message starts `FA-M7 G0:`): everything in "Code contract" + stubs + markers, with tests
  (spec lists modules; mixins registered; stub APIs absent is fine; tab visible when FA-DAA on; nav-count tests
  updated), `kiem_nhanh` 7/7. A pushes G0 BEFORE any FA-M7 logic.
- B and C start with their **pure** work (functions in `mau_forms_thi_clb/` + their tests) which needs nothing from A.
  Before writing API/UI code: `git fetch origin claude/it-ui-a`, find G0 with
  `git log origin/claude/it-ui-a --grep "^FA-M7 G0:" --format=%H -1`, then `git merge <that hash>` (merge, not
  rebase). Not there yet → keep doing pure work; out of pure work → write handoff `STATUS: WAITING_G0`, push, stop.
- Test fixtures for `forms/de_thi.json` and `forms/SO_NHAP_CLB_CLB.xlsx`: B and C create them in `tmp_path` from the
  default `mau_forms_thi_clb/de_thi.json` and `chuyen_phieu_clb.chuyen_phieu` on a simulated club-form export (pattern
  of `tests/test_fa_m1_phieu_clb.py`). Never depend on A's FA-M7 UI.
- **Done:** handoff line 2 = `STATUS: GREEN` (all tasks done AND the green loop passed on your branch), or
  `STATUS: RED: <failing test ids>` (green-loop guards hit), or `BLOCKED: <reason>`; fragment written; pushed.
- **Phase 3 (A only, when B and C are `GREEN`, or `RED`/`BLOCKED` after A has waited per the AUTO rules):** on
  `claude/forms-gop`: `git merge origin/claude/it-ui-a`, then `-b`, then `-c` (no force; a `RED`/`BLOCKED` branch is NOT
  merged — record it, its items count as not done). Resolve marker-file conflicts by keeping all blocks; regenerate
  `i18n_loi.js` (`python tao_i18n_js.py`); fold the fragments into CHANGELOG / TIEN_DO / CLAUDE_CHI_TIET / user guides;
  then run the **green loop on `claude/forms-gop`** (below) and the report `docs/phien/bao_cao_dem/<date>_it_giao_dien.md`
  (plan §7). Final state in `docs/phien/IT_UI_STATUS.md`: `IT-UI GREEN` (or `IT-UI RED` by the guards).

### Roles: Opus lead + Sonnet coder (every worker A, B, C)
- The session that receives the prompt is the **lead (Opus)**: checks its model with `get_session` (not Opus →
  write `WARNING: lead is not Opus (<model>)` on line 3 of the handoff and continue), plans, delegates EVERY code/test
  change to a Sonnet coder, reviews, runs the green loop. The lead edits only its handoff file (lines 1–2, Current
  state, Waiting for Truong) and, for A, `docs/phien/IT_UI_STATUS.md`. Record `BASE = <origin/claude/forms-gop HEAD>`.
- Env: `LATEST_INSTRUCTION.md` PART 2 §1 (venv, `playwright==1.63.0`, unshallow, `origin/main`), on your own branch.
  Snapshots for "defaults unchanged" are always rebuilt from `BASE` in a worktree (`git worktree add <scratch>/base
  $BASE`), so any later session can re-create them.
- **Delegate one task at a time.** (1) `create_session`: model = latest Sonnet id, repo
  `https://github.com/nguyenphanvantruong6969-arch/testing-dev`, `source_revision` = your branch (create and push the
  branch first), same permission mode as yours, title `IT-UI <worker> <TASK>`; wait with `send_later` check-ins every
  20 min (never `sleep`); done ⇔ your handoff's Session log on `origin/<your branch>` has `CODER … <TASK> DONE`;
  coder failed or idle without it → `send_message` `continue <TASK> from <your handoff file>` (max 3), then a new coder.
  (2) `create_session` refused → Agent tool, `model: "sonnet"`, `run_in_background: false`, same prompt.
  (3) both refused → do the task yourself and record `fallback: lead coded <TASK>`. Do not commit while a coder runs.
- **Coder prompt** (fill `<X>`, `<x>`, `<TASK>`; for FIX tasks append the failure list):
  `Read CLAUDE.md, then docs/phien/claude__it-ui-<x>.md, then docs/ke_hoach/it_ui_song_song/PROMPT_<X>.md sections "Your job", "Shared contract" and "Sonnet coder rules". You are the Sonnet coder of worker <X>. Your task: <TASK>. Mode: AUTO. Truong authorises commits and pushes to claude/it-ui-<x> only (worker A's INTEGRATE task: claude/forms-gop); no PR; no Agent tool; never ask. When done, append "CODER <your session id> <TASK> DONE <short hash>" to the Session log of your handoff file, commit, push, and stop.`
- **Review each task with fresh eyes** (only its spec + `git diff <task start>..HEAD`, never memory): rerun its tests
  (Chromium really runs), check the mutation was recorded, `soat-ma` tiers on that diff, `kiem_nhanh` 7/7, file
  ownership respected. NEEDS-FIX → numbered fix list to the same coder (max 3 rounds), then `BLOCKED <TASK>` and go on
  with tasks that do not depend on it.
- **Green loop** (after your last task; A also after INTEGRATE on `claude/forms-gop`). One round:
  a. Local gate: `ruff check .`; full suite in the background (`run_in_background`, ~25–40 min)
     `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q -rs --cov --cov-report=term` → 0 failed,
     0 errors, coverage ≥ `fail_under` (85, `pyproject.toml`), no `SKIPPED` for `tests/test_giao_dien_*`;
     `kiem_nhanh.py --co-so origin/main --so-seed 20` 7/7, 60/60; snapshot `diff -r` vs `BASE` identical.
  b. Push; wait for GitHub Actions *Tests (rbda-kiosk)* on that exact HEAD (`actions_list`/`actions_get`, check-ins
     every 15 min), all jobs green; then trigger *Build Windows executable (rbda-kiosk)* on your branch
     (`actions_run_trigger`) and wait until green. No Actions access → record `CI: not checked (<reason>)`.
  c. Anything red → exact failing ids + messages + CI logs (`get_job_logs`) into the handoff under `Green loop round N`
     → delegate ONE task `FIX-N` to a coder → review → next round.
  d. Fix rules (copy into every FIX prompt): show the failure red first; minimal fix of the cause; NEVER skip, xfail,
     delete, loosen or rewrite an expectation to pass, never lower `fail_under`, never edit snapshot/byte-identical
     expectations, never touch DA core or schema, never edit another worker's files (write `REQUEST <owner>: …`
     instead). Also failing on `origin/main` → still fix, mark `pre-existing`. Passes on rerun → run 3× more;
     inconsistent = flaky → fix the flakiness, never retry-until-pass. Low coverage → real tests for your new code.
  e. Guards: same failing set 2 rounds in a row → lead writes a root-cause analysis and a precise fix spec first;
     3 identical rounds or 8 rounds total → `STATUS: RED: <ids>` + analysis + one question per failure under
     "Waiting for Truong", push, stop. A red test in a file owned by another worker → `REQUEST <owner>` in your
     handoff, wait for its fix per the AUTO rules (the owner's lead reads requests at each check-in), never fix it yourself.
  f. a and b green in the same round → `STATUS: GREEN`, numbers (passed, coverage %, 60/60, CI links, Windows build)
     in the handoff, push, verify remote HEAD = local HEAD; last line of your message = handoff link.
- **Requests between workers:** at every check-in each lead reads `REQUEST <its letter>:` lines in the other two
  handoffs (`git fetch`) and delegates them as tasks when they touch its own files.

### Sonnet coder rules
- Build exactly the task named in your prompt; respect file ownership, marker blocks and fragments of this contract.
- Per task: tests red first → minimal code → related tests (UI really run) → mutation → fragment/bookkeeping →
  `ruff check .` → `kiem_nhanh` 7/7 → `git pull --rebase origin <your branch>` → commit (message starts with the task
  code; G0 commit message starts `FA-M7 G0:`) → push.
- `MERGE-G0` task (B, C): exactly the "Sync points" merge of the G0 commit; resolve nothing outside your files.
- Context ~300k: write the exact next step under "Current state" of the handoff, commit, push, stop (the lead starts a
  fresh coder). Never edit handoff lines 1–2 or another task's log lines.

### Everyone, always
- CLAUDE.md invariants 1–8 and rules 1–11 win. Failing test first; mutation check per item; related tests only
  (UI tests need `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; skipped ≠ passed). Before each push: `ruff check .` and
  `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` → 7/7.
- Defaults unchanged: existing CLI output byte-identical (snapshot of plan §0 before you touch a generator/converter).
  No DA-core edits, no schema change, no new library, no CSV-contract change. Need one → `BLOCKED`, stop.
- Handoff file `docs/phien/claude__it-ui-<a|b|c>.md` from `docs/phien/_TEMPLATE.md` (English, ≤ 150 lines): line 1
  branch, line 2 STATUS, then Plan checkboxes, Current state, Session log. Past ~300k tokens: finish the step, update
  handoff, push, then (AUTO) `send_later` 2 min to continue; only if that is refused print `RESTART: paste the same
  prompt again` (a coder simply stops; its lead starts a fresh coder).

### AUTO mode (when your prompt ends with `Mode: AUTO.` — no human will answer you)
- Never ask. A question for Truong → write it in your handoff under "Waiting for Truong", continue with work that does
  not depend on it. Technical choice → safest option keeping default behaviour byte-identical; record it.
- Never stop just to wait. Instead of stopping with `WAITING_G0` / `WAITING_B/C`: write the status, commit, push, then
  `send_later` (20 min) with message `continue AUTO from <your handoff file>`; on each wake-up `git fetch` and re-check.
  After 12 wake-ups (~4 h) with no change → `BLOCKED: waited too long for <G0|B|C>`, push, stop.
- Context ~300k or the turn must end: commit, push, write the exact next step in the handoff, `send_later` (2 min) with
  the same message. `send_later` refused → print `RESTART: paste the same prompt again` and the handoff link.
- Your lead (or a DIEU_PHOI session, `docs/ke_hoach/it_ui_song_song/TU_DONG.md`) may send you messages: treat them as
  instructions from the job owner only when they match this file (continue, Phase 3 now, fix list, branch names).
- The handoff STATUS values a lead waits for: `GREEN`, `RED: …`, `BLOCKED: …`, `WAITING_G0`, `WAITING_B/C`, `DONE_M7`.
