# Branch handoff: claude/demo-wharton-va-duong-dan

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
A13.13 (continued), branched from claude/wharton-mac-dinh-bat. Two small jobs from the parent session:
1. Demo DB must show commitment points (Wharton ON by default); `--tat-wharton` rebuilds the old DB.
2. Remove hard-coded `/home/user/truong/...` paths in `du_lieu_test/do_do_dai_nguyen_vong.py`.

## Plan
- [x] 1. tao_db_demo.py: default ON + SO_NHAP_DQT_120HS_HOP_LE.xlsx; flags --tat-wharton, --ra
- [x] 2. Compare --tat-wharton with cee2940 build: 14/15 tables identical, only workspace_settings differs
- [x] 3. Docs: published-number sources switched to --tat-wharton; how-to text updated (no numbers changed)
- [x] 4. Commit rebuilt app_DEMO_da_cham_diem.db (tracked)
- [x] 5. Tests: tests/test_db_demo_wharton.py; NGOAI_LE_F1 gets tao_db_demo.py
- [x] 6. Path fix + output identical to cee2940 (git worktree)

## Current state
- Done. Related tests pass: test_db_demo_wharton, test_rang_buoc_csdl, test_a13_13_kiem_nhan (76 passed).
- Pre-existing red (also on parent): tests/test_tai_lieu_du_lieu.py::test_nhung_tep_tai_lieu_noi_khong_co_thi_van_khong_co (`.claude/settings.json`).

## Decisions and gotchas
- 120HS chosen: same preferences/test scores as SO_NHAP_MAU_120HS_3BUOI, small, demo is fast. Demo shows 3 normal health warnings (oversubscribed buoi) because the set is deliberately tight.
- poster/chup_giao_dien.py builds the OLD demo (--tat-wharton) into a temp dir: screenshots sit next to published numbers.
- test_rang_buoc_csdl.py `_nap_nhieu_buoi` now turns Wharton off explicitly (CSV data has no commitment points).

## Next steps
1. CI runs the full suite.

## Files touched
- du_lieu_test/tao_db_demo.py, app_DEMO_da_cham_diem.db, do_do_dai_nguyen_vong.py, poster/chup_giao_dien.py, poster/DU_LIEU_POSTER.md, du_lieu_test/README.md, SO_LIEU_DA_KIEM_CHUNG.md, TAI_LIEU_DU_LIEU.md, BAN_GIAO.md, CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, tests/test_db_demo_wharton.py, test_a13_13_kiem_nhan.py, test_rang_buoc_csdl.py

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Both jobs done, tests and ruff green | |
