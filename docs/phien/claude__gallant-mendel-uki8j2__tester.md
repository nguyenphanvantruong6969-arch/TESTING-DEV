# Branch handoff: claude/gallant-mendel-uki8j2 (tester)

> Role: tester (Opus for L0, Sonnet for L1-L3). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S.
> Protocol: `docs/phien/T3_GIAO_THUC.md`. English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

## Plan
- [x] L0 review 7e90e14..661bccb -> 2 BUGS (see Current state)
- [x] L0 re-check fix1 9151962..e8944b2 -> NO BUGS  - [x] L1 reviewed (2 failing tests found)  - [ ] L2  - [ ] L3

## Current state (overwrite each handoff)
- L1 fix1 (74e4d26..4aa7ab4) re-checked: NO BUGS (170 passed in 14 files; th_ti_le_choi renders "Nhân viên trên mỗi chỗ"/"Employees per place" for company, "Học sinh/Students" for school; tab 05 placeholders = labels vi+en). Screenshot 06 replaced.
- L0 fixci1: assertions ALIGNED to B2/B3 (D1/E3/wharton_mac_dinh_bat keep "điền"/"điểm quyết tâm"/"phóng cho đủ 100", drop only "tắt";
  stress test_8 now asserts refusal code, no run_history, no stb lock). Not weakened.
- L1 related tests: 58 files, 1189 passed / 2 FAILED: tests/test_so_excel_de_dung.py (lines 166-167, 265) still pin the OLD Excel
  text ("Số em đã có câu lạc bộ", "mọi em đều") after T3-43 changed api_xuat.py. Pass at 2947617.
- Other L1 findings: th_ti_le_choi vi hardcodes "Học sinh" (not {person}); T3-27 partly applied (labels/admin_desc new, placeholders
  placeholder_capacity/_reserve_capacity/_reserve_group + th_tong_cho + admin_reserve_assign_title still old wording).
- Verified OK: excluded keys untouched; index.html fallback == catalog (test is leaf-wide); seed input in details#nangCao works vi+en
  (seed 7 locks, readOnly after lock, redraw sets open); history panel hidden at 1 run; Excel exports scanned: no em dash / "em" / "{".
- Screenshots: docs/nghien_cuu/anh_t3/sau_L1/ (01-06).

## Decisions and gotchas
- Test env (new container): `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python -r requirements-dev.txt
  playwright==1.63.0`, then `/root/.local/bin/pytest`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- `python3 tao_i18n_js.py` (any args) rewrites i18n_loi.js; `git status` clean afterwards = JS is in sync.
- Probe scripts live in the session scratchpad only (not committed).

## Next steps (ordered)
1. Wait for `FIX L1` re-check request or `REVIEW L2 ...` from coord.

## Files touched
- docs/nghien_cuu/anh_t3/sau_L0/*.png, sau_L1/*.png, this file.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Opus (tester) | L0 review, invariant 1 re-check, 3 screenshots | 2 bugs (reserve default 0; 'tab' in vi text) |
| 2026-11-04 | Opus (tester) | L0 fix1 re-check | NO BUGS |
| 2026-11-04 | Sonnet (tester) | L1 + L0fixci1 review, 6 screenshots | 2 failing tests outside impl's set; 2 minor notes |
| 2026-11-04 | Sonnet (tester) | L1 fix1 re-check | NO BUGS |
