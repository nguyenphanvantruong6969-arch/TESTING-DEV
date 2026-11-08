# Chạy đêm FA-DAA — tệp DUY NHẤT cần đưa cho Claude

## Phần cho người cài (tiếng Việt, 1 phút)

1. Mở **claude.ai/code** → chọn kho `nguyenphanvantruong6969-arch/TESTING-DEV` → nhánh **`claude/keen-ride-72sa7t`**.
2. Chọn model **Sonnet** (quy tắc 11 của `CLAUDE.md`: Sonnet viết mã, Opus lập kế hoạch). Chế độ quyền: **auto**.
3. Dán đúng câu lệnh sau rồi để chạy qua đêm:

```text
Read docs/phien/CHAY_DEM_FA_DAA.md and follow it exactly. Truong authorises commits and pushes to the branch named there. Work until every night-1 item is done or blocked, then write the final report.
```

4. (Tuỳ chọn, tự động cả đêm) Thay bước 3 bằng: mở một phiên claude.ai/code bất kỳ trên kho này, dán **prompt cài tự
   động** dưới đây. Nó tạo tác vụ định kỳ 00:23, 02:23, 04:23 (giờ Việt Nam), mỗi lần mở phiên Sonnet mới; tệp này có
   khoá chống hai phiên chạy cùng lúc (mục C.2) và phiên tự tắt tác vụ khi xong (mục E).

```text
Create a scheduled task for me. Name: "FA-DAA chay dem". Mode: create a NEW session on each firing, in this
environment, repo nguyenphanvantruong6969-arch/TESTING-DEV, branch claude/keen-ride-72sa7t, model Sonnet
(latest Sonnet id). Schedule: CRON_TZ=Asia/Ho_Chi_Minh 23 0,2,4 * * *. Push notifications on, email off.
Prompt for each firing, verbatim:
"Read docs/phien/CHAY_DEM_FA_DAA.md and follow it exactly. Truong authorises commits and pushes to the branch named
there. Work until every night-1 item is done or blocked, then write the final report. If the handoff Plan already
shows every night-1 item ticked or BLOCKED, disable the scheduled task named 'FA-DAA chay dem' (update_trigger,
enabled=false), write nothing else, and stop."
Do not fire it now. Show me the task id, next run time and stored prompt when done.
```
5. Sáng ra: đọc mục "Night report" trong `docs/phien/claude__keen-ride-72sa7t.md`, gửi Truong.

Chạy bằng máy cá nhân thay vì web: clone kho, `git checkout claude/keen-ride-72sa7t`, chạy `claude --model sonnet`,
dán câu lệnh trên.

---

## Part for Claude (English)

### A. Who you are and what this is
- You are the **implementer** (Sonnet role). The plan was written by Opus on 2026-11-08 and approved by Truong (the
  student who owns this project) when he asked for this night run. Do not re-plan; do not reorder items.
- Goal: build FA-DAA in the kiosk (Python), items FA-0 .. FA-8 tonight ("night 1"), following
  `docs/ke_hoach/FA_DAA_KE_HOACH.md` (the spec; section numbers below refer to it) and the vision
  `docs/ke_hoach/FA_DAA_VISION.md` (cited V§n). Microsoft items (FA-M*) and UI (FA-UI) are NOT tonight.
- `CLAUDE.md` is loaded automatically: obey its invariants and working rules. In particular: no subagents / Agent
  tool (rule 10), tests first (rule 2), related tests only (full suite is CI's job), never present simulated numbers
  as real, never write report commentary.

### B. Setup (once per session)
```bash
git fetch origin claude/keen-ride-72sa7t main
git checkout claude/keen-ride-72sa7t && git pull --rebase origin claude/keen-ride-72sa7t
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
git fetch --unshallow 2>/dev/null; git fetch origin main:refs/remotes/origin/main
```
If your environment forces a different branch name, create it from `origin/claude/keen-ride-72sa7t`, push there,
and write the branch name in the handoff Session log. Keep updating `docs/phien/claude__keen-ride-72sa7t.md` either way.

Quiet test command (never paste full pytest output):
```bash
.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files or -k> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | tail -25
```
Re-run only failing node ids with `--tb=short | tail -40`.

### C. Protocol
1. Read, in this order: this file, `docs/phien/claude__keen-ride-72sa7t.md` (handoff: plan ticks, state, decisions),
   then ONLY the section of `FA_DAA_KE_HOACH.md` for the item you start. Locate code by function name
   (`grep -n "^def <name>" <file>`), never by line number.
2. Lock: in the handoff "Current state", if a line `RUNNING: <UTC time> <session>` is less than 3 hours old, another
   session is working: stop immediately and write nothing. Otherwise write your own RUNNING line, commit, push.
   Remove it in your final report.
3. Take the first unticked night-1 item in the handoff Plan whose dependencies are done. For each item:
   a. Write the failing tests from its `kiem_nhan` first; run them; confirm RED for the right reason.
   b. Minimal code to make them green. FA paths run only when `rules.fa_daa` is true.
   c. Run: the item's tests + `tests/test_nhieu_buoi.py -k TestTrungKhit` + `tests/test_wharton_pipeline.py` +
      every `tests/` file that greps an identifier you changed. Then `ruff check .`.
   d. Mutation check: break one line of the new code on purpose, confirm a test goes red, restore, `git status` clean.
   e. If you added a test file: update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row
      `tests/`). If you edited `i18n_errors.py`: `python tao_i18n_js.py`.
   f. `CHANGELOG.md` entry (item code, files, new tests) and one row in `docs/ke_hoach/TIEN_DO.md`.
   g. `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` (report only; fix only what it flags
      in YOUR item).
   h. Tick the item in the handoff Plan, append one Session-log row, commit `FA-<n>: <short summary>`, then
      `git pull --rebase origin claude/keen-ride-72sa7t && git push -u origin claude/keen-ride-72sa7t`
      (retry on network error: 2 s, 4 s, 8 s, 16 s). Never force-push. Never open or merge a PR.
4. Decisions D1..D10 in §1 of the plan are settled: use the Default column. Never implement D1 (compensation).
5. Stop rules (plan §5): invariant would break, baseline red, new library needed, schema/CSV change beyond the item,
   same test fails after 3 honest attempts -> mark the item `BLOCKED: <one line why>` in the handoff Plan, commit,
   continue with the next item that does not depend on it. FA-4 depends on FA-1 and FA-3; FA-5 and FA-6 depend on
   FA-4; FA-8 depends on FA-4..FA-6; FA-2, FA-3, FA-7 depend on FA-1 only.
6. Context: past ~400k tokens (the Stop hook reminds you), finish the current step, update the handoff "Current
   state" + "Next steps", commit, push, stop. The next session continues from the handoff.

### D. Things that bite in this repo
- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` counts `tests/test_*.py` files.
- `rules` keys that are False must not appear in `run_history.luat_xep` or the fingerprint (`_luat_de_ghi_hoac_bam`):
  copy the `wharton` pattern for `fa_daa`, or every old result reports "stale".
- `wharton` defaults ON at workspace level (A13.13); `fa_daa` must default OFF everywhere.
- `sanity_check_result` requires each assignment to be in the student's list: pass it the in-memory augmented lists
  of FA-4 step 5, never write them to `preferences`.
- STB: crc32 only, never `hash()`. `run_history` append-only. New result tables (`fa_nhom`, `fa_ly_do`) append-only.
- Never commit real school data, names, tenant ids or app URLs.

### E. Final report (end of night or when nothing is left)
Overwrite "Current state" in the handoff with: items done (commit hashes), items BLOCKED (why), tests run and
counts, open questions for Truong. Append a "Night report <date>" Session-log row. Remove your RUNNING line. Commit,
push. If you were started by the scheduled task "FA-DAA chay dem" and no night-1 item is left unticked (all done or
BLOCKED), disable that task (`list_triggers` to find it, then `update_trigger` with `enabled=false`; never delete it).
Stop.
