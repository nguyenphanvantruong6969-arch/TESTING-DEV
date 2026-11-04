# Branch handoff: claude/gallant-mendel-uki8j2 (tester)

> Role: tester (Opus for L0, Sonnet for L1-L3). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S.
> Protocol: `docs/phien/T3_GIAO_THUC.md`. English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

## Plan
- [x] L0 review 7e90e14..661bccb -> 2 BUGS (see Current state)
- [x] L0 re-check fix1 9151962..e8944b2 -> NO BUGS  - [x] L1 reviewed (2 failing tests found)  - [ ] L2  - [ ] L3

## Current state (overwrite each handoff)
- L2 reviewed (ad1481d..a8b4407): related tests 35 + 11 files = 548 passed, 0 failed. Findings sent to coord ("TESTER REPORT L2"):
  1 bug: btn_reset_entry vi hardcodes "học sinh" (company workspace shows "Xoá nguyện vọng của học sinh này"); en still "Start over".
  Notes: raw `thu_2` still in tab-01 warning texts (vi+en); tab 03 "Lần chạy gần nhất: 2026-11-04T15:58:33 · số khởi tạo 42" unformatted;
  MA_BUOI_CO_NHAN set not parity-tested vs NHAN_BUOI; reserve segment of fill bar not asserted; ws chooser "THAO TÁC" header over empty column;
  T3-32 collapse not done (known).
- Verified OK: T3-24 numbers moved (#nvTieuDiem "66,7% ... 100% nằm trong 3 nguyện vọng đầu", #duTruTieuDiem "0/9"); T3-14 vi labels, unknown codes keep text;
  T3-06 stepper visible on failed run, hidden after success, Chi tiết toggles; T3-23 details#xuatNangCao + red warning kept; T3-28 Lịch tuần gone;
  T3-34 menu keeps "Xuất CSV nhân viên này"; company workspace renders (title, KPI, run line).
- Screenshots: docs/nghien_cuu/anh_t3/sau_L2/ (01,03,04,05,06,07).

## Decisions and gotchas
- Test env (new container): `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python -r requirements-dev.txt
  playwright==1.63.0`, then `/root/.local/bin/pytest`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- `python3 tao_i18n_js.py` (any args) rewrites i18n_loi.js; `git status` clean afterwards = JS is in sync.
- Probe scripts live in the session scratchpad only (not committed).

## Next steps (ordered)
1. Wait for `FIX L2` re-check or `REVIEW L3 ...` from coord.

## Files touched
- docs/nghien_cuu/anh_t3/sau_L0/*.png, sau_L1/*.png, this file.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Opus (tester) | L0 review, invariant 1 re-check, 3 screenshots | 2 bugs (reserve default 0; 'tab' in vi text) |
| 2026-11-04 | Opus (tester) | L0 fix1 re-check | NO BUGS |
| 2026-11-04 | Sonnet (tester) | L1 + L0fixci1 review, 6 screenshots | 2 failing tests outside impl's set; 2 minor notes |
| 2026-11-04 | Sonnet (tester) | L1 fix1 re-check | NO BUGS |
| 2026-11-04 | Sonnet (tester) | L1 fix1 re-check NO BUGS; L2 review | L2: 1 bug + notes |
