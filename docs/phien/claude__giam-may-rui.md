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
- [ ] FA-CT2: `goi_y_tang_them` (pure) + `export_chia_cho` API + UI button + tests
- [ ] FA-D7L: `quy_diem_10_le`, `diem_dieu_chinh_le`, `--diem-le`, `rules.fa_diem_le`, kiosk `dat_diem_san` + tests
- [ ] Finish: soat-ma, `kiem_nhanh --co-so origin/main --so-seed 20` 7/7 (60/60), report
      `docs/phien/bao_cao_dem/<date>_giam_may_rui.md`, Vietnamese summary to Truong

## Current state (overwrite each handoff)
- Done so far: plan written (Opus, 2026-11-13). No code yet.
- Tests: none yet.
- Open problems: none.

## Decisions and gotchas (keep short)
- FA-CT1/CT2 never write `clubs.capacity`; teachers enter seats as usual (only-increase rule unchanged).
- First real term has no last-term demand: optional teacher file `club_id, nhu_cau` (e.g. last year's members).
- FA-D7L: store TRUNCATED one-decimal score; pass check = round-half-up of the stored value (`dat_diem_san`).
  Proven equal to today's integer pass check (checked by Opus on 200,000 random cases, 0 mismatches). Rounding to
  0.1 half-up would break it (4.45 → 4.5 → 5 vs today 4).
- Medal default D1, minimum members, group priority, block-rotated lottery: still Truong's open decisions; out of scope.

## Next steps (ordered)
1. Sonnet: FA-CT1 (tests first).

## Files touched
- docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md: spec
- docs/ke_hoach/giam_may_rui/PROMPT_SONNET.md: start prompt

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Opus | Plan FA-CT1, FA-CT2, FA-D7L from Fable G-H; rounding proof checked | report-only seats; option default off |
