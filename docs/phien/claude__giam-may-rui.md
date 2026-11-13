# Branch handoff: claude/giam-may-rui

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Reduce the role of luck without touching the DA core (Truong 2026-11-13, "implement 1 + 2" of Fable G-H):
FA-CT1 split a day's seats by demand (report-only suggestion), FA-CT2 "where to add X seats" + teacher export/UI,
FA-D7L optional 0.1-step test scores with the pass/fail set exactly unchanged. Registry: A13 sub-items, goal G-D.
Spec: `docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md` (follow exactly). Branch from `origin/claude/forms-gop`; push only to
`claude/giam-may-rui`; no PR. All numbers SIMULATED.

## Plan (written by Opus; ticked by Sonnet)
- [x] FA-CT1: `chia_cho_theo_nhu_cau` (pure) + tests `tests/test_fa_ct1_chia_cho.py`
- [x] FA-CT2: `goi_y_tang_them` (pure) + `export_chia_cho` API + UI button + tests
- [x] FA-D7L: `quy_diem_10_le`, `diem_dieu_chinh_le`, `--diem-le`, `rules.fa_diem_le`, kiosk `dat_diem_san` + tests
- [x] Finish: soat-ma, `kiem_nhanh --co-so origin/main --so-seed 20` 7/7 (60/60), report
      `docs/phien/bao_cao_dem/<date>_giam_may_rui.md`, Vietnamese summary to Truong

## Current state (overwrite each handoff)
- Done: FA-CT1 (`bc2e670`), FA-CT2 (`e2885eb`), FA-D7L (`7254539`), soat-ma four tiers (report only). All pushed.
- kiem_nhanh `--co-so origin/main --so-seed 20`: 7/7, 60/60 after each item. Chromium UI tests really ran (5/5 repeats).
- SIMULATED (FA-D7L test 3, 20 seeds, 200 students, 6 clubs/day): LOTTERY share of rejections at SELECTIVE clubs
  6.6 % (201/3065) integer -> 0.4 % (13/3068) decimal; BELOW_PASS set identical on all 20 seeds.
- Report: `docs/phien/bao_cao_dem/2026-11-13_giam_may_rui.md` (findings P-1..P-6, none blocking; decision D-1).
- Open: Truong decides D-1 and whether to merge into `claude/forms-gop`. No PR opened.

## Decisions and gotchas (keep short)
- FA-CT1/CT2 never write `clubs.capacity`; teachers enter seats as usual (only-increase rule unchanged).
- First real term has no last-term demand: optional teacher file `club_id, nhu_cau` (e.g. last year's members).
- FA-D7L: store TRUNCATED one-decimal score; pass check = round-half-up of the stored value (`dat_diem_san`).
  Proven equal to today's integer pass check (checked by Opus on 200,000 random cases, 0 mismatches). Rounding to
  0.1 half-up would break it (4.45 → 4.5 → 5 vs today 4).
- `export_chia_cho(tep_nhu_cau)` accepts a path OR `{ten, base64}` (UI sends base64; spec said str). P-1 suggests base64 only.
- `rules.fa_diem_le` read via separate `get_fa_diem_le` (kept `get_forms_nap` keys unchanged for an existing exact test).
- `dat_diem_san` applies to ALL scores when FA is on (spec); hand-entered decimals now pass if they round up (D-1).
- Medal default D1, minimum members, group priority, block-rotated lottery: still Truong's open decisions; out of scope.

## Next steps (ordered)
1. Truong: decide D-1 and merge / no merge.
2. If asked: fix P-1..P-6 (new item code), then kiem_nhanh again.

## Files touched
- fa_daa.py, fa_ly_do.py, fa_vong_doi_cho.py, cau_hinh_ws.py, api_xuat.py, api_forms.py, api_forms_nap.py
- mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py, mau_forms_thi_clb/phan_tich_cau_hoi.py
- index.html, js/03_ket_qua.js, js/12_chuan_bi_nap.js, i18n.js, i18n_errors.py, i18n_loi.js
- tests: test_fa_ct1_chia_cho.py, test_fa_ct2_tang_them.py, test_giao_dien_fa_ct2.py, test_fa_d7l_diem_le.py,
  test_giao_dien_fa_d7l.py, test_ws_nhan.py
- docs (Opus plan): docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md, docs/ke_hoach/giam_may_rui/PROMPT_SONNET.md
- docs: CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md, docs/phien/bao_cao_dem/2026-11-13_giam_may_rui.md
## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Opus | Plan FA-CT1, FA-CT2, FA-D7L from Fable G-H; rounding proof checked | report-only seats; option default off |
| 2026-11-13 | Sonnet-role (coder) | FA-CT1, FA-CT2, FA-D7L + soat-ma report | 7/7, 60/60; P-1..P-6, D-1 open |
