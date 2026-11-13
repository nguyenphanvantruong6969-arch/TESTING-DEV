# Giảm may rủi: chia chỗ theo nhu cầu (FA-CT1, FA-CT2) và điểm lẻ (FA-D7L) — kế hoạch cho Sonnet

> Soạn 2026-11-13 (Opus) theo yêu cầu của Truong ("implement 1 + 2"), từ nghiên cứu của Fable
> (`docs/fable/04_GH_REDUCING_LUCK.md` trên nhánh `claude/fable-ga-audit`, methods 1 and 2). Mọi số liệu là **MÔ PHỎNG**.
> Registry: A13 (FA-DAA) sub-items, research goal G-D. Spec below is in English (implementer: Sonnet). Locate code by
> FUNCTION NAME (`grep -n "def <name>" <file>`), never line numbers.

## 0. Rules for the implementer (read first)
- `CLAUDE.md` wins on invariants 1–8 and rules 1–11. No Agent tool. Rule 2: failing test first, minimal code, then
  related tests only. One commit per item code (`FA-CT1: …`).
- **Branch:** `claude/giam-may-rui`, created from `origin/claude/forms-gop`. Never force-push. Do NOT open/merge PRs.
- **Default unchanged (invariant 1):** after each item run
  `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7, 60/60 identical. No item touches `run_rbda`,
  `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`, `verify_stability`, the STB lottery or
  `run_history`. FA-CT1/CT2 are **report-only** (they never write `clubs.capacity`).
- **No schema change, no new library, no CSV column change.** If an item turns out to need one → mark BLOCKED, ask Truong.
- Messages: new error codes only in `i18n_errors.py` (vi + en) → `python tao_i18n_js.py`; add new codes to
  `MA_MOI_SAU_ANH_CHUP` in `tests/test_ws_nhan.py`. UI strings in `i18n.js`, vi AND en. No internal codes
  (FA-CT1, D7, GAP-n) in text a user reads. Plain Vietnamese for teachers.
- Integer/rounding maths with `fractions.Fraction` (from `str(x)`), never raw float comparisons.
- After each item: `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, tick the Plan in `docs/phien/claude__giam-may-rui.md`.
- Before push: skill `soat-ma` (`kiem_nhanh.py` + four tiers), report only.

## 1. Why (one paragraph, for context)
Simulated school (800 students, 3 days, 7 clubs/day): splitting the SAME total seats by first-choice demand cuts
student-days with a lottery loss 28 % → 20 % and raises true first choice 29 % → 47 %; the only-increase form
(+15 % seats to over-demanded clubs) gives about half. Finer scores (0.1 steps) cut lottery decisions at SELECTIVE
clubs (25 % → 20 % of rejections) and do nothing at LIMITED clubs. Capacities and scores are DATA for DA, so
stability and truthful ranking are untouched as long as seats are fixed before the run.

## 2. FA-CT1 — split a day's seats by demand (pure function + tests)

New pure function in `fa_daa.py` (next to `goi_y_chi_tieu`):

```
chia_cho_theo_nhu_cau(rows, tong: int, gioi_han: dict, nhu_cau: dict | None = None) -> list
```
- `rows` = output of `bang_nhu_cau(...)` for ONE day (caller filters by `buoi`). Only LIMITED and SELECTIVE
  clubs take part; FREE rows are returned unchanged with `goi_y = None` (FREE has no seat limit).
- Demand per club `d_c` = `nhu_cau[club_id]` if given (teacher-supplied reference, e.g. last year's members),
  else `nv1`. For SELECTIVE with no `nhu_cau`: `min(nv1, so_dat_san)` when `so_dat_san` is not None.
- Floor per club `f_c` = `max(1, so_giu_cho)` (capacity > 0 is a schema rule; reserved students must fit).
  Ceiling `g_c` = `gioi_han.get(club_id)` (teacher limit from `fa_gioi_han_gv`) or no ceiling.
- `tong` = total seats to split for that day (default chosen by the caller = sum of current `capacity` of the
  day's non-FREE clubs). If `sum(f_c) > tong` → error code `chia_cho_tong_qua_nho` (params: buoi, tong, can).
- Method (deterministic, floors and ceilings are BOUNDS, not additions): quota `q_c = T·d_c/Σd` over the free clubs
  with `T` = seats not yet fixed. Any club with `q_c < f_c` is fixed at `f_c`, any with `q_c > g_c` at `g_c`; remove
  fixed clubs, recompute quotas on the rest; repeat until no bound binds. Then round the free clubs by largest
  remainder (Hamilton): integer parts first, leftover seats to the largest fractional parts (ties → larger `d_c`,
  then `club_id`). If rounding pushes a club outside its bounds, fix it and repeat. All demand 0 → equal split by
  the same rule. Seats nobody can take (all clubs at ceiling) → reported in `du` on every row of that day.
- Output rows = input row + `goi_y` (int), `chenh` (`goi_y − capacity`), `ghi_chu` ∈
  {`""`, `cham_gioi_han`, `san_giu_cho`, `khong_nhu_cau`}, `du`.
- Never reads student IDs, ranks of individual students, or outcomes (it reads only the aggregate counts that
  `bang_nhu_cau` already publishes to teachers). Not part of any priority key (invariant 2 untouched).

`kiem_nhan` (tests first, `tests/test_fa_ct1_chia_cho.py`):
1. Sum of `goi_y` over a day's non-FREE clubs == `tong − du`; every `goi_y` within `[f_c, g_c]`.
2. Proportionality: with no caps/floors binding, `|goi_y_c − tong·d_c/Σd| < 1` for every club.
3. Determinism: same input in a different dict order → identical output.
4. Reserved seats: `goi_y ≥ so_giu_cho` always; floor too large → `chia_cho_tong_qua_nho`.
5. FREE rows untouched; `nhu_cau` overrides `nv1`; SELECTIVE uses `min(nv1, so_dat_san)`.
6. Hand examples in the test docstring, checked number by number: 3 clubs, 30 seats, demand 20/8/2 → 20/8/2;
   same with a ceiling of 15 on the first → 15/12/3 (re-split 15 seats 8:2); demand 29/1/0, floors 1 → 28/1/1.

## 3. FA-CT2 — "we can add X seats: where?" + teacher export and UI

New pure function in `fa_daa.py`:
```
goi_y_tang_them(rows, them: int, gioi_han: dict) -> list
```
- For ONE day. Excess `e_c = d_c − capacity` (same `d_c` as FA-CT1, without `nhu_cau`), only `e_c > 0` clubs.
- Give seats one at a time to the club with the largest remaining excess (ties: larger `nv1`, then `club_id`),
  never above `g_c`. Output rows + `them_vao` (int ≥ 0), `capacity_moi`. Leftover seats reported in `du`.
- Always only increases → passes `kiem_chi_tang` by construction (test it).

API (`api_xuat.py`, next to `export_goi_y_chi_tieu`, same locking and `fa_chua_bat` guard):
```
export_chia_cho(output_path: str = "", buoi: str = "", tong: int | None = None,
                them: int | None = None, tep_nhu_cau: str = "")
```
- Writes `chia_cho_theo_nhu_cau.xlsx` (use `so_excel.py` formatting like the other teacher exports) with one sheet per
  day: club name, type, current seats, first-choice demand, students above the pass mark, reserved, teacher limit,
  **suggested seats (FA-CT1)**, difference, and when `them` is given **seats to add (FA-CT2)**. No student data.
- `tep_nhu_cau` (optional): a small CSV/XLSX `club_id, nhu_cau` the teacher fills (e.g. last year's members) for the
  first real term; unknown club IDs → warning code `chia_cho_ma_clb_la` (list), not a failure. The file is read
  only for this export; nothing is stored.
- Read-only on `app.db`. Returns `{ok, data: {path, n_rows, du_theo_buoi}, errors}`.

UI (`js/03_ket_qua.js`, `index.html`, `i18n.js`): one new button in the same group as "xuat_muc_nhu_cau" /
"xuat_muc_goi_y": "Gợi ý chia lại chỗ theo nhu cầu", with two optional inputs ("Tổng số chỗ mỗi buổi" — default
current total; "Được thêm bao nhiêu chỗ" — empty = skip) and an optional file picker for the reference demand. One
help line: "Số chỗ chỉ là gợi ý; thầy cô tự quyết và nhập chỉ tiêu như thường lệ."

`kiem_nhan` (`tests/test_fa_ct2_tang_them.py`, `tests/test_giao_dien_fa_ct2.py` for the button):
1. `them_vao` sums to `them − du`; no club above `g_c`; only clubs with excess receive seats.
2. `kiem_chi_tang(before, after)` returns no violation for every random case (50 seeds).
3. Export: file exists, one sheet per day, no student ID or name anywhere in the workbook (scan all cells against
   the students table), FA off → `fa_chua_bat`.
4. `app.db` byte-identical before/after the export (read-only).
5. UI test: button calls the API and shows the path; inputs left empty → defaults.

## 4. FA-D7L — finer test scores (0.1 steps), OPTION, default OFF

Goal: fewer ties at SELECTIVE clubs, with the **pass/fail set exactly unchanged**.

Key fact (keep this proof in the code docstring): for a score `x ≥ 0`, let `t = floor(10x)/10` (truncate to one
decimal). Then `floor(t + 1/2) == floor(x + 1/2)`, because every half-integer `n − 1/2` is a multiple of 1/10, so
`x ≥ n − 1/2 ⇔ t ≥ n − 1/2`. Therefore: **store the truncated decimal, and compare with the pass mark after
round-half-up** → the same students pass as with today's integer score. Do NOT round to 0.1 half-up (double
rounding breaks this: x = 4.45 → 4.5 → 5, but today 4.45 → 4).

Converter (`mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`, `mau_forms_thi_clb/phan_tich_cau_hoi.py`):
- New `quy_diem_10_le(diem, toi_da)` = truncate `diem/toi_da·10` to one decimal (Fraction), clip 0–10.
  New `diem_dieu_chinh_le(diem_tho, dich)` = truncate `(diem_tho + dich)` to one decimal, clip 0–10 (D11 path).
- Switch: CLI flag `--diem-le` (only with `--fa-daa`), and the kiosk import step (FA-M9, `api_forms_nap.py`) reads a
  workspace flag `rules.fa_diem_le` (bool, default False, stored like `rules.fa_duong`; NOT an allocation rule,
  not in `luat_xep`). Off → today's functions, byte-identical Sổ nhập.
- The D11 variant check (`phan_tich_cau_hoi`) keeps computing on unrounded scores (unchanged); only the value
  written changes.
- Guide text for IT/teachers (where the flag is shown): "Điểm lẻ đến 0,1 giúp ít bằng điểm hơn. Đạt hay không đạt
  điểm sàn vẫn xét như điểm làm tròn."

Kiosk (`fa_daa.py` and every place that compares a score with `diem_san`):
- New helper `dat_diem_san(diem, san) -> bool` = `floor(Fraction(str(diem)) + 1/2) >= san`. Use it in
  `chay_fa_daa` (SELECTIVE filter), `bang_nhu_cau` (`so_dat_san`), `ly_do_ket_qua` / waitlist / round 2 wherever a
  pass check happens (grep `diem_san` in `fa_daa.py`, `fa_sau_xep.py`, `fa_ly_do.py`, `api_*.py`). For integer scores
  the helper equals today's `diem >= san`, so default results stay byte-identical.
- Priority ordering already uses `-score`; decimals need no change there. Check that Sổ nhập import
  (`so_nhap.py`) and the data checks accept a decimal score for FA clubs; if anything rejects or rounds it, that is
  the one place to fix (no column change). If a CSV/schema change appears necessary → BLOCKED, ask.
- Result screen and reasons (`fa_ly_do.py`): show the score with one decimal when it is not an integer
  ("điểm chuẩn 7,3, em 7,1"); the pass-mark sentence shows the pass mark as an integer.

`kiem_nhan` (`tests/test_fa_d7l_diem_le.py`):
1. Property: for 10,000 random `(diem, toi_da)` incl. edge cases x.x5, x.45, 4.5, 0, max →
   `floor(quy_diem_10_le + 1/2) == quy_diem_10` (pass set identical). Same for `diem_dieu_chinh_le` vs
   `diem_dieu_chinh`.
2. Flag off → Sổ nhập byte-identical to today on the converter's existing test fixtures.
3. Kiosk: with integer scores, `chay_fa_daa` results identical on the FA test data (row by row); `kiem_nhanh`
   60/60. With decimal scores: the set of `BELOW_PASS` rows equals the set produced from the integer-rounded
   scores; share of `LOTTERY` reasons at SELECTIVE clubs ≤ the integer run on 20 simulated seeds (report the numbers
   in the commit message, labelled MÔ PHỎNG).
4. `dat_diem_san(4.4, 5) is False`, `dat_diem_san(4.5, 5) is True`, `dat_diem_san(5, 5) is True`,
   float noise (`4.4999999999` stored as REAL) handled via `str` → test it.

## 5. Order and done
1. FA-CT1 → 2. FA-CT2 → 3. FA-D7L. After all three: soat-ma report in `docs/phien/bao_cao_dem/<date>_giam_may_rui.md`
   (Vietnamese, short), `kiem_nhanh` 7/7 with 60/60, related tests green, Chromium UI tests really ran.
2. Stop and report to Truong (Vietnamese, plain): what the teacher now clicks, what the two new options do, and the
   simulated before/after numbers from FA-D7L test 3. Do not merge into `claude/forms-gop`; Truong decides.

## 6. Out of scope (do not do)
- Writing `clubs.capacity` automatically, changing `kiem_chi_tang`, or any capacity change after the run.
- Block-rotated lottery, per-club lottery, improvement cycles, medal default D1 (separate decisions, still open).
- Using answer time as a tie-break (rewards fast devices; rejected by Fable G-H).
