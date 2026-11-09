# Chạy đêm FA-DAA — tệp DUY NHẤT cần đưa cho Claude (ĐÊM 2: Microsoft)

> Đêm 1 (FA-0..FA-8, kiosk) đã xong và Opus đã soát (GO): báo cáo `docs/phien/bao_cao_dem/2026-11-09.md` và
> `docs/phien/bao_cao_dem/2026-11-09_soat_dem1.md`; giao thức đêm 1 nằm trong lịch sử git của tệp này (commit a80e626).

## Phần cho người cài (tiếng Việt, 1 phút)

1. Mở **claude.ai/code** → chọn kho `nguyenphanvantruong6969-arch/TESTING-DEV` → nhánh **`claude/keen-ride-72sa7t`**.
2. Chọn model **Sonnet** (quy tắc 11 của `CLAUDE.md`). Chế độ quyền: **auto**.
3. Dán đúng câu lệnh sau rồi để chạy qua đêm:

```text
Read docs/phien/CHAY_DEM_FA_DAA.md and follow it exactly. Truong authorises commits and pushes to the branch named there. Work until every night-2 item is done or blocked, then write the final report.
```

4. (Tuỳ chọn, tự động cả đêm) Thay bước 3 bằng: mở một phiên claude.ai/code bất kỳ trên kho này, dán **prompt cài tự
   động** dưới đây (tác vụ 00:23, 02:23, 04:23 giờ Việt Nam; khoá chống hai phiên ở mục C.2; phiên tự tắt tác vụ ở mục E).
   Nếu tác vụ đêm 1 "FA-DAA chay dem" còn bật, tắt nó trước.

```text
Create a scheduled task for me. Name: "FA-DAA chay dem 2". Mode: create a NEW session on each firing, in this
environment, repo nguyenphanvantruong6969-arch/TESTING-DEV, branch claude/keen-ride-72sa7t, model Sonnet
(latest Sonnet id). Schedule: CRON_TZ=Asia/Ho_Chi_Minh 23 0,2,4 * * *. Push notifications on, email off.
Prompt for each firing, verbatim:
"Read docs/phien/CHAY_DEM_FA_DAA.md and follow it exactly. Truong authorises commits and pushes to the branch named
there. Work until every night-2 item is done or blocked, then write the final report. If the handoff Plan already
shows every night-2 item ticked or BLOCKED, disable the scheduled task named 'FA-DAA chay dem 2' (update_trigger,
enabled=false), write nothing else, and stop."
Do not fire it now. Show me the task id, next run time and stored prompt when done.
```
5. Sáng ra: Claude tự đẩy báo cáo lên GitHub (đường dẫn ở mục E.2; link nằm ở dòng cuối tin nhắn cuối của Claude).

---

## Part for Claude (English)

### A. Who you are and what this is
- You are the **implementer** (Sonnet role). Plan by Opus (2026-11-08), night 1 reviewed by Opus (2026-11-09, GO).
  Do not re-plan; do not reorder items.
- Tonight ("night 2"): Microsoft items **FA-M1 .. FA-M6** from `docs/ke_hoach/FA_DAA_KE_HOACH.md` §3 (the spec; read
  the row of the item you start, plus the §1 decisions it cites). Vision: `docs/ke_hoach/FA_DAA_VISION.md` (V§n).
- Every FA-M output is labelled **TH = untested on real Microsoft** (in docstrings, doc headings, report). Never
  claim something works in Forms / Power Apps / SharePoint / Power Automate.
- **D8 (Power Apps or Forms) is still OPEN** (GĐ2 meeting). Build exactly what §3 specifies for BOTH paths; never
  pick one, never write "recommended path" text beyond plan §4.
- Kiosk code is NOT tonight: do not edit `api*.py`, `rbda_priority_pipeline.py`, `fa_daa.py`, `fa_ly_do.py`,
  `so_nhap.py`, `index.html`, `*.js` (importing their functions is fine). If an item needs a change there: BLOCKED.
- `CLAUDE.md` is loaded automatically: invariants, working rules, no subagents (rule 10), tests first (rule 2),
  related tests only, simulated data only, never write report commentary.

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

### C. Protocol
1. Read: this file, then `docs/phien/claude__keen-ride-72sa7t.md` (handoff), then ONLY the §3 row (and cited §1
   decisions) of the item you start. Locate code by function name (`grep -n "^def <name>" <file>`), never line numbers.
2. Lock: in the handoff "Current state", if a line `RUNNING: <UTC time> <session>` is less than 3 hours old, another
   session is working: stop immediately and write nothing. Otherwise write your own RUNNING line, commit, push.
   Remove it in your final report.
3. Take the first unticked night-2 item in the handoff Plan whose dependencies (C.5) are done. For each item:
   a. Failing tests first, from the §3 row (file names as listed there); run them; RED for the right reason.
   b. Minimal code / docs to make them green. FA paths only behind `--fa-daa` (converter, generator): without the
      flag, output must be byte-identical to before (compare one sample run before/after and say so in the commit).
   c. Run: the item's tests + `tests/test_fa_m3_huy_chuong_b.py` + `tests/test_mau_forms_thi_clb.py` + every `tests/`
      file that greps a file or identifier you changed (e.g. `grep -l chuyen_forms_sang_phan_mem tests/*.py`;
      `tests/test_t4m_*.py` for `bo_dung_t4m`). Then `ruff check .`.
   d. Mutation check: break one line of the new code, confirm a test goes red, restore, `git status` clean.
   e. New test file: update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row `tests/`).
   f. `CHANGELOG.md` entry (item code, files, new tests) and one row in `docs/ke_hoach/TIEN_DO.md`.
   g. `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` (fix only what it flags in YOUR item).
   h. Tick the item in the handoff Plan, append one Session-log row, commit `FA-M<n>: <short summary>`, then
      `git pull --rebase origin claude/keen-ride-72sa7t && git push -u origin claude/keen-ride-72sa7t`
      (retry on network error: 2 s, 4 s, 8 s, 16 s). Never force-push. Never open or merge a PR.
4. Decisions D1..D12 (plan §1): use the Default column. D8 stays open (A above). Never implement D1.
5. Order and dependencies (keep the order FA-M1 .. FA-M6):
   - FA-M1 club setup form + converter: none (uses night-1 `so_nhap` FA columns and `fa_daa.kiem_truoc_fa`).
   - FA-M2 path B registration Forms (`--fa-daa` in `tao_mau_forms.py` / `bieu_mau.py`): none.
   - FA-M3 converter FA mode: needs FA-M1 (Loại from the club sheet) and FA-M2 (path B column names); wires the
     existing `dat_huy_chuong_duong_b` (do not change its behaviour; its 19 tests must stay green).
   - FA-M4 quiz variants + item analysis + D11 equating: needs FA-M3 (the converter's `--ap-dung-dieu-chinh` /
     `--giu-diem-goc` gate).
   - FA-M5 Power Apps spec v2 (path A) + `bo_dung_t4m` columns: needs FA-M3 (column names `WP1..WP7`, `HC_TuChinh`,
     `TrangThai` read by the converter).
   - FA-M6 after-allocation docs (docs only): needs FA-M5 (app result screen); uses night-1 `ket_qua_ly_do.csv`.
   Stop rules (plan §5): invariant would break, baseline red, new library needed, schema/CSV change beyond the
   item, same test fails after 3 honest attempts -> mark `BLOCKED: <one line why>` in the handoff Plan, commit,
   continue with the next item that does not depend on it.
6. Context: past ~400k tokens (the Stop hook reminds you), finish the current step, update the handoff "Current
   state" + "Next steps", commit, push, stop. The next session continues from the handoff.

### D. Things that bite in this repo
- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` counts `tests/test_*.py` files.
- Variant choice `crc32(email) % n` (FA-M4): `zlib.crc32` on UTF-8, never `hash()`.
- Never commit real school data, names, emails, tenant ids or app URLs; sample data is SIMULATED.
- Forms has no creation API: FA-M1/FA-M2 output is a generator + build guide, not a live form.
- Power Automate limit 6,000 requests/user/day (FA-M6): state the arithmetic in the doc, do not assume more.

### E. Final report (end of night or when nothing is left)
1. Overwrite "Current state" in the handoff: items done (commit hashes), BLOCKED (why), tests run and counts, open
   questions for Truong. Append a "Night 2 report <date>" Session-log row. Remove your RUNNING line.
2. Report file `docs/phien/bao_cao_dem/<YYYY-MM-DD>.md` (date the night started, Vietnam time). If it exists and its
   first line is `# Báo cáo đêm 2 ...`, an earlier session of tonight wrote it: UPDATE it. If it exists but belongs to
   another night (e.g. `2026-11-09.md` is night 1), never touch it: use `<YYYY-MM-DD>_dem2.md` instead. Vietnamese,
   plain words, no jargon, at most 60 lines:
   - `# Báo cáo đêm 2 <ngày>` and one line: xong X/6 mục, chặn Y mục. All Microsoft parts are TH (chưa thử thật).
   - Table `| Mục | Việc (1 câu dễ hiểu) | Kết quả: xong / chặn / chưa làm | Commit |` with rows FA-M1 .. FA-M6.
   - `## Bị chặn` : each blocked item, why, what Truong must decide.
   - `## Kiểm tra` : test files run, pass/fail counts, ruff, kiem_nhanh. Numbers are SIMULATED data.
   - `## Câu hỏi cho Truong` (D8 stays here until decided) and `## Đêm sau nên làm` (Opus review of night 2, then FA-UI).
3. Commit (`FA-BC: night 2 report <date>`) and push as in C.3 h. Verify:
   `git fetch origin claude/keen-ride-72sa7t && git log -1 --format=%H origin/claude/keen-ride-72sa7t` equals HEAD.
   Last line of your final message: the link
   `https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/blob/claude/keen-ride-72sa7t/docs/phien/bao_cao_dem/<report file name>`
4. If you were started by the scheduled task "FA-DAA chay dem 2" and no night-2 item is left unticked (all done or
   BLOCKED), disable that task (`list_triggers`, then `update_trigger` with `enabled=false`; never delete it). Stop.
