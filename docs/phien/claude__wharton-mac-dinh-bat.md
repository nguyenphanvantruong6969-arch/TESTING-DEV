# Branch handoff: claude/wharton-mac-dinh-bat

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
A13.13: school workspace default `rules.wharton = True` (commitment points on by default).
Truong approved breaking invariant 1 for this item (recorded in CHANGELOG + TIEN_DO). Invariants 2-8 hold.
Out of scope: "template header by vocabulary" (Direction A/B).

## Plan (Opus plan, ticked)
- [x] 1. Failing tests first (tests/test_wharton_mac_dinh_bat.py)
- [x] 2. Minimal fix: cau_hinh_ws (default True; auto-off in `_chuan_hoa` and `tron_len` when combo not allowed and `wharton` not explicit)
- [x] 3. Fix affected old tests (default -> new default, or explicit `wharton: false` via `tests/_wharton.py::tat_wharton`; no delete/skip)
- [x] 4. Scripts in du_lieu_test/ + soat-ma `kiem_nhanh.py` pass `wharton: false` explicitly
- [x] 5. Error text `wharton_ho_so_chua_hop_le` now names both fixes; docs wording
- [x] 6. ruff clean; soat-ma 7/7; CHANGELOG + TIEN_DO; commits pushed (no PR)
- [x] 7. Parent's acceptance suite: tests/test_a13_13_kiem_nhan.py (45) + tests/test_giao_dien_a13_13_kiem_nhan.py (2): all pass, no code change needed

## Current state
- Done and pushed. Related list (grep list + test_ws_* + stress + giao_dien): 1556 passed, 4 failed at last full run; 2 of those were then fixed (tests/test_ws_wharton_giao_dien.py, now 10 passed). Remaining 2 red = tests/test_a13_12_tai_lieu.py (map of code in CLAUDE.md moved to CLAUDE_CHI_TIET.md) — they ALSO fail on base cee2940, not caused by this item.
- test_a13_11_stress.py 33 errors were caused by the new default (run_pipeline blocked in fixtures), fixed with tat_wharton.
- F2 (scripts vs base cee2940, git worktree): do_anh_huong_seed.py --so-seed 5 output identical; bao_cao_phan_bo.py HTML identical.

## Decisions and gotchas
- `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"]` stays False: bare pipeline calls (rules=None, run_full_pipeline) keep old numbers; default ON lives only in cau_hinh_ws.
- Old stored config lacking the `wharton` key reads as ON (no migration, per Truong's original request).
- Data is blocked only when a fund has >=2 clubs and no points (single-club fund auto-fills 100, "cach A").
- soat-ma `kiem_trung_khit` would silently compare two "blocked" runs; fixed by writing wharton false in both.

## Next steps
1. Truong decides on the 2 pre-existing red tests in test_a13_12_tai_lieu.py (separate item).
2. CI runs the full suite.

## Files touched
- cau_hinh_ws.py, i18n_errors.py, i18n_loi.js, api_nhap.py (comment), rbda_priority_pipeline.py (comment), HUONG_DAN_SU_DUNG.md, mau_csv/HUONG_DAN_SO_NHAP.md, CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, .claude/skills/soat-ma/scripts/kiem_nhanh.py, du_lieu_test/** (explicit wharton false), ~35 test files, new tests above.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Branch + handoff created | |
| 2026-11-01 | Sonnet | Implemented A13.13, fixed tests/scripts, parent acceptance suite | see Current state |
