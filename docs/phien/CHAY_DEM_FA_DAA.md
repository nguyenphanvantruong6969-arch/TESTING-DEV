# Chạy đêm FA-DAA — tệp DUY NHẤT cần đưa cho Claude (ĐÊM 4: sửa lỗi soát đêm 3 + biên bản bốc thăm + mô phỏng)

> Đêm 1 (kiosk), đêm 2 (Microsoft), đêm 3 (sửa lỗi + giao diện) đã xong, Opus đã soát cả ba (GO). Báo cáo trong
> `docs/phien/bao_cao_dem/` (`*_soat_dem3.md` là bản soát mới nhất). Giao thức các đêm trước nằm trong lịch sử git của
> tệp này (commit a80e626, 3e7d8a7, c962bb8).

## Phần cho người cài (tiếng Việt, 1 phút)

1. Mở **claude.ai/code** → chọn kho `nguyenphanvantruong6969-arch/TESTING-DEV` → nhánh **`claude/keen-ride-72sa7t`**.
2. Chọn model **Sonnet** (quy tắc 11 của `CLAUDE.md`). Chế độ quyền: **auto**.
3. Dán đúng câu lệnh sau rồi để chạy:

```text
Start the night-4 job NOW in this session. Read docs/phien/CHAY_DEM_FA_DAA.md and follow it exactly. Truong authorises commits and pushes to branch claude/keen-ride-72sa7t. Write the RUNNING lock line first (section C.2). Do not create any scheduled task. Work through every night-4 item until each is done or BLOCKED. Then follow section E: write the report, commit, push, check the push reached GitHub, remove the RUNNING line, and print the report's GitHub link as your last line.
```

4. Phiên dừng giữa chừng thì mở phiên mới, dán lại đúng câu trên; phiên mới làm tiếp từ tệp bàn giao.
5. Sáng ra không cần gửi gì: Claude tự đẩy báo cáo lên GitHub (mục E.2; link ở dòng cuối tin nhắn cuối của Claude).

---

## Part for Claude (English)

### A. Who you are and what this is
- You are the **implementer** (Sonnet role). Plan by Opus; nights 1 and 2 reviewed by Opus (GO). Do not re-plan; do not
  reorder items.
- Tonight ("night 4"): **FA-N1 .. FA-N4** (fixes from the night-3 review), then **FA-9** (witnessed lottery record)
  and **FA-10** (simulation compare + D1 two-term behaviour), from `docs/ke_hoach/FA_DAA_KE_HOACH.md` §7 (FA-9 and
  FA-10 are specified in §2). Why each fix is needed: `docs/phien/bao_cao_dem/2026-11-09_soat_dem3.md`.
  Vision: `docs/ke_hoach/FA_DAA_VISION.md`.
- Kiosk code IS allowed tonight (`api*.py`, `fa_daa.py`, `fa_ly_do.py`, `so_nhap.py`, `index.html`, `js/*.js`,
  `i18n.js`, `style.css`), but NOT `rbda_priority_pipeline.py` core functions (`run_rbda`, `club_choice_function`,
  `compute_club_priority`, `verify_stability`): an item that needs them is BLOCKED.
- Microsoft parts stay **TH = untested on real Microsoft**. D8 (Power Apps or Forms) is still OPEN: never pick one.
- Not tonight: attendance, appeals, round 2, D1 itself (FA-10 only MEASURES it), real-Microsoft tests.
- `CLAUDE.md` is loaded automatically: invariants, working rules, no subagents (rule 10), tests first (rule 2),
  related tests only, simulated data only, never write report commentary.

### B. Setup (once per session)
```bash
git fetch origin claude/keen-ride-72sa7t main
git checkout claude/keen-ride-72sa7t && git pull --rebase origin claude/keen-ride-72sa7t
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pip install -q playwright==1.63.0
export PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
git fetch --unshallow 2>/dev/null; git fetch origin main:refs/remotes/origin/main
```
Shell variables do not survive between commands: prefix EVERY UI test command with `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
Check the browser once: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q tests/test_giao_dien_wharton.py -x 2>&1 | tail -3` must show
PASSED tests, not only "skipped". If UI tests only skip, FA-N2 and FA-N3 are BLOCKED ("no browser"); still do the other items.
If your environment forces a different branch name, create it from `origin/claude/keen-ride-72sa7t`, push there,
and write the branch name in the handoff Session log. Keep updating `docs/phien/claude__keen-ride-72sa7t.md` either way.

Quiet test command (never paste full pytest output):
```bash
.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files or -k> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed|skipped' | tail -25
```

### C. Protocol
1. Read: this file, then `docs/phien/claude__keen-ride-72sa7t.md` (handoff), then ONLY the §7 row (FA-9/FA-10: §2) of the item you start
   (and its line in the review report). Locate code by function name (`grep -n "def <name>" <file>`), never line numbers.
2. Lock: in the handoff "Current state", if a line `RUNNING: <UTC time> <session>` is less than 3 hours old, another
   session is working: stop immediately and write nothing. Otherwise write your own RUNNING line, commit, push.
   Remove it in your final report.
3. Take the first unticked night-4 item in the handoff Plan whose dependencies (C.5) are done. For each item:
   a. Failing test first that REPRODUCES the bug (FA-N) or checks the new feature (FA-9, FA-10); RED for the right reason.
   b. Minimal fix. Default behaviour unchanged: FA off / no `--fa-daa` -> byte-identical outputs (compare one sample
      run before/after for converter/generator items and say so in the commit).
   c. Run: the item's tests + every `tests/` file that greps a file or identifier you changed. Kiosk items also:
      `tests/test_nhieu_buoi.py -k TestTrungKhit`, `tests/test_wharton_pipeline.py`, all `tests/test_fa_*.py`.
      UI items also: `tests/test_giao_dien_wharton.py`, `tests/test_giao_dien_wharton_quan_ly.py`. Then `ruff check .`.
   d. Mutation check: break one line of the fix, confirm a test goes red, restore, `git status` clean. Do NOT use
      `git checkout -- <file>` to restore an uncommitted fix (it deletes the fix too): copy the file first, or commit first.
   e. New test file: update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row `tests/`).
      Edited `i18n_errors.py`: run `python tao_i18n_js.py`.
   f. `CHANGELOG.md` entry (item code, files, new tests) and one row in `docs/ke_hoach/TIEN_DO.md`.
   g. `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` (fix only what it flags in YOUR item).
   h. Tick the item in the handoff Plan, append one Session-log row, commit `<code>: <short summary>`, then
      `git pull --rebase origin claude/keen-ride-72sa7t && git push -u origin claude/keen-ride-72sa7t`
      (retry on network error: 2 s, 4 s, 8 s, 16 s). Never force-push. Never open or merge a PR.
4. Decisions D1..D12 (plan §1): use the Default column. D8 open. Never implement D1.
5. Order and dependencies:
   - Order: FA-N1, FA-N2, FA-N3, FA-N4, FA-9, FA-10. None depends on another, except FA-10 should run last
     (it uses the finished kiosk functions). FA-10 output is TABLES ONLY labelled "SỐ LIỆU MÔ PHỎNG", no
     interpretation or conclusion text (academic integrity in CLAUDE.md).
   Stop rules (plan §5): invariant would break, baseline red, new library needed, schema/CSV change beyond the
   item, same test fails after 3 honest attempts -> mark `BLOCKED: <one line why>` in the handoff Plan, commit,
   continue with the next item that does not depend on it.
6. Context: past ~400k tokens (the Stop hook reminds you), finish the current step, update the handoff "Current
   state" + "Next steps", commit, push, stop. The next session continues from the handoff.

### D. Things that bite in this repo
- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` counts `tests/test_*.py` files.
- `kiem_nhanh` check `chu_cam`: no "Wharton" and no forbidden forms of address in visible text; `i18n_khoa`: every
  `i18n.js` key needs vi AND en.
- UI tests skip silently without a browser: a skipped UI test is NOT a pass.
- `rules` keys that are False never appear in `run_history.luat_xep` or the fingerprint (`_luat_de_ghi_hoac_bam`).
- Variant choice `crc32(email) % n`: `zlib.crc32` on UTF-8, never `hash()`.
- `EMAIL_MA_HS.csv` is personal data: never commit a real one; tests use simulated emails.
- FA-9 record and FA-10 tables: no student names; STB numbers and ids only in simulated data.
- Never commit real school data, names, emails, tenant ids or app URLs.

### E. Final report (end of night or when nothing is left)
1. Overwrite "Current state" in the handoff: items done (commit hashes), BLOCKED (why), tests run and counts, open
   questions for Truong. Append a "Night 4 report <date>" Session-log row. Remove your RUNNING line.
2. Report file `docs/phien/bao_cao_dem/<YYYY-MM-DD>_dem4.md` (date the night started, Vietnam time). If it exists and
   its first line is `# Báo cáo đêm 4 ...`, an earlier session of tonight wrote it: UPDATE it; never touch other
   nights' files. Vietnamese, plain words, no jargon, at most 70 lines:
   - `# Báo cáo đêm 4 <ngày>` and one line: xong X/6 mục, chặn Y mục.
   - Table `| Mục | Việc (1 câu dễ hiểu) | Kết quả: xong / chặn / chưa làm | Commit |` with rows FA-N1 .. FA-N4,
     FA-9, FA-10.
   - `## Bị chặn` : each blocked item, why, what Truong must decide.
   - `## Kiểm tra` : test files run, pass/fail/skip counts (UI tests: how many really ran), ruff, kiem_nhanh.
     Numbers are SIMULATED data.
   - `## Câu hỏi cho Truong` (D8 stays here until decided) and `## Đêm sau nên làm` (Opus review of night 4).
3. Commit (`FA-BC: night 4 report <date>`) and push as in C.3 h. Verify:
   `git fetch origin claude/keen-ride-72sa7t && git log -1 --format=%H origin/claude/keen-ride-72sa7t` equals HEAD.
   Last line of your final message: the link
   `https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/blob/claude/keen-ride-72sa7t/docs/phien/bao_cao_dem/<report file name>`
4. Stop.
