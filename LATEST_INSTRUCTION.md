# LATEST INSTRUCTION — Sửa 7 lỗi nhỏ trước khi merge PR #14 (2026-11-10)

> Đây là tệp hướng dẫn **MỚI NHẤT**. Nếu tệp khác (kể cả `docs/phien/CHAY_DEM_FA_DAA.md`) nói khác, làm theo tệp này.
> **Next after this:** `INSTRUCTION_FILL_GAPS.md` (fill all remaining vision gaps, father/son sessions).
> Chỉ đọc nhãn "LATEST INSTRUCTION" ở dòng đầu là biết đây là bản đúng.

---

## PHẦN 1 — Cho người chạy (bạn của Truong). Đọc hết, mất 2 phút.

### Việc này là gì
Claude sẽ tự sửa **7 lỗi nhỏ** đã được soát ra trong phần mềm xếp CLB, mỗi lỗi một commit, rồi tự đẩy lên GitHub
và tự viết báo cáo. Bạn **không cần biết lập trình**. Bạn chỉ làm 5 bước dưới đây.

### 5 bước
1. Mở **https://claude.ai/code** và đăng nhập.
2. Chọn kho **`nguyenphanvantruong6969-arch/TESTING-DEV`**, chọn nhánh **`claude/keen-ride-72sa7t`**.
   (Không chọn `main`. Không tạo nhánh mới.)
3. Chọn model **Sonnet**. Chế độ quyền: **auto**.
4. Sao chép **nguyên văn** khung dưới đây, dán vào ô chat, bấm gửi:

```text
Read LATEST_INSTRUCTION.md in the repo root and follow PART 2 exactly, from top to bottom. Truong authorises commits and pushes to branch claude/keen-ride-72sa7t only. Do not open, close, approve or merge any pull request. Do not create any scheduled task. Do not use subagents. Work through the 7 items in the given order until each is DONE or BLOCKED, then write the report (step 6 of PART 2), push it, and print the report's GitHub link as the very last line of your final message.
```

5. Để Claude tự chạy (khoảng 1–3 giờ). **Không cần trả lời gì**, trừ khi Claude hỏi một câu có/không.

### Nếu có sự cố
| Thấy gì | Làm gì |
|---|---|
| Phiên dừng giữa chừng / hết lượt / báo lỗi mạng | Mở **phiên mới** (bước 1–3), dán **lại đúng khung trên**. Phiên mới tự làm tiếp phần còn lại. |
| Claude báo "another session is RUNNING" rồi dừng | Có phiên khác đang chạy. Đợi 3 giờ rồi thử lại, hoặc báo Truong. |
| Claude hỏi chọn giữa nhiều phương án | Trả lời: **"Choose the safest option that keeps default behaviour unchanged, and note it in the report."** |
| Claude xin merge PR hoặc đổi nhánh | Trả lời: **"No."** |

### Biết là xong khi nào
Dòng **cuối cùng** trong tin nhắn cuối của Claude là một đường link dạng
`https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/blob/claude/keen-ride-72sa7t/docs/phien/bao_cao_dem/2026-11-..._sua_nho.md`.
Gửi link đó cho Truong. Xong.

---

## PART 2 — For Claude (English). Follow in order. Do not skip steps.

### 0. Role and scope (read first)
- You are the **implementer** (Sonnet role, `CLAUDE.md` rule 11). The plan is fixed. Do not re-plan, do not reorder,
  do not add features.
- Branch: **`claude/keen-ride-72sa7t`** (PR #14 → `main`, open). Push ONLY to this branch. Never force-push.
  Never open, merge, close or approve a PR.
- Scope: EXACTLY the 7 items in section 4. Sources (read only the row of the item you are on):
  - `docs/phien/bao_cao_dem/2026-11-10_soat_dem5.md` (rows FA-P3 … FA-P7)
  - `docs/ke_hoach/BAO_CAO_SOAT_MA_FA_DEM5.md` (rows SM-1, SM-2, SM-3)
  - Note: **FA-P7 and SM-3 are the same bug** → one item, one commit, code `FA-P7/SM-3`.
- OUT of scope (do not touch): attendance, appeals, round 2, admin dashboard, D1 compensation, D8 (Power Apps vs
  Forms), real-Microsoft tests, the Windows build workflow, any new library, any schema/CSV-column change.
- FORBIDDEN files/functions: core of `rbda_priority_pipeline.py` (`run_rbda`, `run_rbda_nhieu_buoi`,
  `club_choice_function`, `compute_club_priority`, `verify_stability`). Importing `khoa_sap_buoi` from it is fine.
  If an item seems to need a forbidden change → mark it BLOCKED (section 5).
- `CLAUDE.md` is loaded automatically and wins over anything here on invariants. Key ones for this job:
  invariant 1 (default results byte-identical), invariant 6 (`{ok, data, errors}`; messages only from
  `i18n_errors.py` → `python tao_i18n_js.py`), rule 2 (test first), rule 10 (no subagents).

### 1. Setup (once per session; run exactly)
```bash
git fetch origin claude/keen-ride-72sa7t main
git checkout claude/keen-ride-72sa7t && git pull --rebase origin claude/keen-ride-72sa7t
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pip install -q playwright==1.63.0
git fetch --unshallow 2>/dev/null; git fetch origin main:refs/remotes/origin/main
```
- Shell variables do not persist between commands: prefix EVERY UI test command with
  `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- Browser check (once): `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q tests/test_giao_dien_wharton.py -x 2>&1 | tail -3`
  must show PASSED tests. If UI tests only **skip**, items needing a UI test (FA-P3 UI part, SM-2) are
  BLOCKED "no browser"; still do the others. **A skipped UI test is NOT a pass.**
- Quiet test command (never paste full pytest output):
```bash
.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files or -k> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed|skipped' | tail -25
```

### 2. Lock (prevents two sessions working at once)
1. Open `docs/phien/claude__keen-ride-72sa7t.md`, section "Current state".
2. If a line `RUNNING: <UTC time> <session>` exists and is **less than 3 hours old** → another session is working:
   print "another session is RUNNING" and STOP. Write nothing.
3. Otherwise add your own line `RUNNING: <UTC time now> sua-nho`, commit `FA-KH: lock small-fix run`, push.
4. Resuming? In the handoff Plan, section "Pre-merge small fixes", skip items already ticked `[x]` or `BLOCKED`.

### 3. Per-item loop (do a → h for EVERY item, one item at a time)
- **a. Red test first.** Write a test that REPRODUCES the bug exactly as the "repro" column of the source row
  describes. Run it: it must FAIL, and for the right reason (read the failure message).
- **b. Minimal fix.** Smallest change that makes the test pass. Default behaviour unchanged (FA off → identical).
- **c. Related tests.** The item's test file + every `tests/` file that greps a function or file you changed +
  always: `tests/test_nhieu_buoi.py -k TestTrungKhit`, `tests/test_wharton_pipeline.py`, all `tests/test_fa_*.py`.
  UI items also: `tests/test_giao_dien_fa_*.py`. Then `ruff check .` must be clean.
- **d. Mutation check.** Copy the fixed file aside, break one line of the fix, confirm a test goes RED, restore from
  your copy, `git status` shows only intended changes. (Never `git checkout -- <file>` on an uncommitted fix: it
  deletes the fix.)
- **e. Bookkeeping.** New test file → update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row
  `tests/`; checked by `tests/test_a13_12_tai_lieu.py`). Edited `i18n_errors.py` → run `python tao_i18n_js.py`.
  Add a `CHANGELOG.md` entry at the top (date, item code, files, new tests) and one row in `docs/ke_hoach/TIEN_DO.md`.
- **f. Quick self-check.** `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main`
  → fix only what it flags in YOUR change.
- **g. Handoff.** Tick the item in the handoff Plan ("Pre-merge small fixes") and append one Session-log row
  (`| date | Sonnet (small fixes) | <code>: what, test red first, related N passed, mutation caught | |`).
- **h. Commit + push.** Message `<code>: <short summary>` (+ the attribution lines your harness gives). Then
  `git pull --rebase origin claude/keen-ride-72sa7t && git push -u origin claude/keen-ride-72sa7t`.
  On network error retry after 2 s, 4 s, 8 s, 16 s.

### 4. The 7 items — IN THIS ORDER
Locate code by **function name** (`grep -n "def <name>" <file>`), never by line number.

**1) SM-1 — Excel lottery record crashes on forbidden characters** (`fa_bien_ban.py` → `ghi_xlsx`)
- Bug: a workspace name containing a control character (e.g. `"Kỳ\x01một"`) makes `export_bien_ban_boc_tham` fail
  with `error_exporting_csv` / `IllegalCharacterError`, and the HTML file is left behind.
- Fix: pass every text cell through `so_excel.lam_sach` before writing (the same cleaner `so_excel.Trang.o` uses).
- Test must show: export with that workspace name returns `ok: true`, writes both `.html` and `.xlsx`, and the xlsx
  opens with `openpyxl`. Keep the existing formula guard `_an_toan_cho_excel` (FA-P1) working.

**2) FA-P3 — Results screen silently hides days that have no reasons** (`api_xuat.py` → `get_ly_do_ket_qua`; `js/03_ket_qua.js` → `loadMatchResults`)
- Bug: `_doc_ly_do_moi_nhat` returns the missing days (`thieu`) but `get_ly_do_ket_qua` drops them; the "Lý do"
  column is just empty for that day, with no notice. (Repro in the source row: full FA run, re-run `thu_2` with FA
  off, turn FA back on.)
- Fix: return them as a new key `thieu_buoi` (list, day order). In the UI, when the list is not empty, show ONE
  short notice above the results table built from the EXISTING message code `fa_ly_do_thieu_buoi` (no new
  message text, unless a new i18n key is truly required; then add vi AND en in `i18n.js`).
- Tests: API test (red first) that `thieu_buoi == ["thu_2"]` for the repro; FA off → response unchanged
  (`thieu_buoi` absent or empty, existing keys identical). UI test (Chromium) that the notice appears in the repro
  and is hidden when nothing is missing.

**3) FA-P4 — Lottery record lists days alphabetically** (`fa_bien_ban.py` → `tao_ban_ghi`)
- Bug: `sorted(dem_theo_buoi.items())` puts `chu_nhat` before `thu_2` in the HTML and Excel record.
- Fix: sort with `khoa_sap_buoi` (from `rbda_priority_pipeline`), same as FA-O1.
- Test: clubs on `chu_nhat` and `thu_2` → `thu_2` row comes before `chu_nhat` in both the HTML and the xlsx.
  `sha256_stb` and all other values unchanged.

**4) FA-P6 — Missing-day warnings listed alphabetically** (`api_xuat.py` → `_doc_ly_do_moi_nhat`)
- Bug: `tat_ca_buoi = sorted(...)` → warnings `fa_ly_do_thieu_buoi` come out `chu_nhat` before `thu_2`.
- Fix: `sorted(..., key=khoa_sap_buoi)`.
- Test: two missing days `chu_nhat` and `thu_2` → `canh_bao` from `export_ly_do_csv` (and `thieu_buoi` from item 2)
  list `thu_2` first.

**5) FA-P5 — HTML and Excel record can get mismatched file names** (`api_xuat.py` → `_export_bien_ban_da_khoa`)
- Bug: names are chosen separately. Folder already has `bb.xlsx` (no `bb.html`) → output `bb.html` + `bb (2).xlsx`.
- Fix: choose ONE base name for the pair using the existing `kem_duoi` parameter of `_duong_xuat`
  (`kem_duoi=(".xlsx",)`), then derive the xlsx path from the html path.
- Test: the repro above → `bb (2).html` + `bb (2).xlsx` (same base), nothing overwritten; empty folder → `bb.html` +
  `bb.xlsx`.

**6) SM-2 — Flaky fixed wait in a UI test** (`tests/test_giao_dien_fa_n2_luu_mac_dinh.py` → `test_sang_em_khac_giua_luc_luu_van_luu_huy_chuong_em_truoc`)
- Problem: `page.wait_for_timeout(800)` instead of waiting for a condition.
- Fix: replace with a bounded wait on a real condition (poll the API / DB until the first student's medals are saved,
  max ~5 s), or wait for `#fbHuyChuongStep` of student 2 to be rendered. Test-only change; app code untouched.
- Exception to steps a and d: a timing flake cannot be reproduced on demand, so there is no red test and no mutation
  step. Instead run the changed test **5 times in a row**; all 5 must PASS. Write "5/5 passed" in the commit message.

**7) FA-P7/SM-3 — `kiem_nhanh --so-seed N` silently caps at 5** (`.claude/skills/soat-ma/scripts/kiem_nhanh.py` → `main`)
- Bug: `SEED_MAC_DINH[:N]` has only 5 seeds, so `--so-seed 20` prints "15 ca (3 bộ × 5 seed)".
- Fix: when N > 5, extend with deterministic extra seeds (e.g. `range(1, N+1)` minus duplicates, or a fixed rule
  you document in the help text). Never random. Default (no flag) must stay exactly the 5 current seeds.
- Test: a unit test on the seed-list builder: N=20 → 20 distinct seeds; N=5 / default → `(1, 7, 42, 99, 12345)`.
  Then run `--so-seed 20` once and confirm it prints 60 cases (3 × 20) all identical.

### 5. Stop rules (BLOCKED)
Mark `BLOCKED: <one line why>` next to the item in the handoff Plan, commit, push, continue with the next item, when:
an invariant would break; the baseline (`TestTrungKhit`) is red before you start; a new library is needed; a
schema or CSV-column change is needed; a forbidden function must change; the same test still fails after 3 honest
attempts; UI tests only skip (UI items only).
Context past ~400k tokens: finish the current step, update handoff "Current state", commit, push, stop.

### 6. Final report (when all 7 are DONE or BLOCKED)
1. **Invariant 1 full check:** 3 datasets × 20 seeds against `origin/main` must be **60/60 identical**.
   If item 7 is DONE: `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20`.
   If item 7 is BLOCKED: call `kiem_trung_khit(goc_moi, goc_cu, seeds=range(1, 21))` from that script directly (read
   its docstring for the two folder arguments). Record the result.
2. **Handoff:** overwrite "Current state" in `docs/phien/claude__keen-ride-72sa7t.md` (items done with commit
   hashes, BLOCKED with reason, test counts, open questions). Remove your RUNNING line. Append a session-log row.
   In "Next steps" write: "1. Watch PR #14 CI until green. 2. Truong merges."
3. **Report file:** `docs/phien/bao_cao_dem/<YYYY-MM-DD>_sua_nho.md` (Vietnam date when the run started). If it
   exists and starts with `# Báo cáo sửa lỗi nhỏ`, UPDATE it. Vietnamese, plain words, no jargon, ≤ 60 lines:
   - `# Báo cáo sửa lỗi nhỏ <ngày>` + one line: `xong X/7 mục, chặn Y mục`.
   - Table `| Mục | Việc (1 câu dễ hiểu) | Kết quả: xong / chặn | Commit |` — 7 rows in the order above.
   - `## Bị chặn` — each blocked item, why, what Truong must decide (write "Không có" if none).
   - `## Kiểm tra` — test files run, pass/fail/skip counts (UI: how many really ran in Chromium), ruff, kiem_nhanh,
     invariant 1 (60/60). Say clearly: **numbers are from SIMULATED data**.
   - `## Câu hỏi cho Truong` — anything left open (D8 stays open).
4. Commit `FA-BC: small-fix report <date>`, push as in 3h, then verify:
   `git fetch origin claude/keen-ride-72sa7t && git log -1 --format=%H origin/claude/keen-ride-72sa7t` equals
   `git rev-parse HEAD`.
5. Last line of your final message = the link:
   `https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/blob/claude/keen-ride-72sa7t/docs/phien/bao_cao_dem/<report file name>`
6. Stop.

### 7. Things that bite in this repo
- Day order: always `khoa_sap_buoi` / `THU_TU_BUOI` (`chu_nhat` after `thu_7`), never a plain string sort.
- Lottery record (HTML and Excel): never student names or ids; only the STB hash and counts.
- `kiem_nhanh` check `chu_cam`: no "Wharton" and no forbidden forms of address in visible text; `i18n_khoa`: every
  `i18n.js` key needs vi AND en.
- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` counts `tests/test_*.py` files.
- Never commit real school data, names, emails, tenant ids or app URLs. All data in tests is simulated.
- Never write commentary/interpretation for the student's project report (`CLAUDE.md`, academic integrity).
