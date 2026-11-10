# Branch handoff: claude/fa-gaps

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
Fill every remaining FA-DAA vision gap (GAP-0 … GAP-14) per `INSTRUCTION_FILL_GAPS.md`: post-allocation changes
(adjustment table + replay, attendance, waitlist invites, appeals, round 2), feedback/surveys, next-term capacity,
admin dashboard, two-grader deviation, reminders, Power Apps kit, simulation, improvement cycles (measurement mode),
D1 memo. Every behaviour behind a new `rules` key defaulting to False; default output byte-identical (invariant 1).
Status: `docs/phien/FA_GAPS_STATUS.md`; specs: `docs/ke_hoach/FA_GAPS_KE_HOACH.md`. Run mode: SOLO (START_HERE §2.2b).

## Plan (written by Opus; ticked by Sonnet)
- [x] GAP-0 fa_dieu_chinh + vi_tri_hien_tai (w1)  - [x] GAP-1 attendance (w1)  - [x] GAP-2 waitlist invites (w1)
- [x] GAP-3 appeals (w2)  - [x] GAP-4 round 2 (w2)  - [x] GAP-5 feedback (w2)  - [x] GAP-6 week-3 survey (w2)
- [x] GAP-7 next-term capacity (w3)  - [x] GAP-8 admin dashboard (w3)  - [x] GAP-9 two-grader deviation (w3)
- [x] GAP-10 reminders (w3)  - [x] GAP-11 Power Apps kit (w4)  - [x] GAP-12 simulation (w4)
- [x] GAP-13 improvement cycles (w4)  - [x] GAP-14 D1 memo (WAIT-TRUONG) (w4)

## Current state (overwrite each handoff)
- Phase 1 DONE (bao_cao_dem/2026-11-10_sua_nho.md). Waves 1 and 2 reviewed GO (bao_cao_dem/..._wave1.md, _wave2.md).
- Wave 3 (GAP-7, 8, 9, 10) and wave 4 (GAP-11, 12, 13; GAP-14 memo WAIT-TRUONG) coded, own tests + mutations green,
  kiem_nhanh 7/7 60/60 after GAP-13. Broad suites running: wave-3 snapshot b0d832e, final HEAD 8069c08.
- Remaining: confirm suites, write wave 3/4 review reports, F7 final report, ALL WAVES DONE, one draft PR.
- Tests: new files up to tests/test_fa_gap13_vong_doi_cho.py; count in CLAUDE_CHI_TIET.md = 246 test files.

## Decisions and gotchas (keep short)
- SOLO mode (START_HERE §2.2b). Post-allocation flags only in cau_hinh_ws.MAC_DINH_TRUONG_HOC["rules"] +
  CO_SAU_XEP (needs fa_daa → FaTinhNangCanFa / `fa_tinh_nang_can_fa`); never in LUAT_XEP → never in fingerprint.
- New tables appended to DEFAULT_SCHEMA (init_db runs it, then di_tru_schema): fa_dieu_chinh (append-only, guarded by
  kiem_nhanh BANG_NHAT_KY), fa_diem_danh, fa_khieu_nai, fa_phan_hoi.
- Current seat = match_results of the day's base run + fa_dieu_chinh replay (fa_sau_xep.vi_tri_hien_tai).
- Waitlist = fa_ly_do.waitlist_pos (D4 already computed). Round 2 = serial dictatorship in day lottery order.
- New error codes must be added to MA_MOI_SAU_ANH_CHUP in tests/test_ws_nhan.py; code-map backticks must be Python
  names (tests/test_a13_12_tai_lieu.py).
- Broad suite ≈ 20–25 min: run it in a `git worktree` snapshot so coding can continue.

## Next steps (ordered)
1. See "Next step" in docs/phien/FA_GAPS_STATUS.md (confirm wave-2 suites, bookkeeping, mark DONE, review wave 2).
2. Finalise wave-3 spec, then waves 3–4, F7 final report, ONE draft PR claude/fa-gaps → main.

## Files touched
- fa_sau_xep.py, api_sau_xep.py (new); api.py (mixin), api_workspace.py, cau_hinh_ws.py, rbda_priority_pipeline.py
  (DEFAULT_SCHEMA only), i18n_errors.py/i18n_loi.js, i18n.js, index.html, js/01_khung.js, js/03_ket_qua.js,
  js/075_workspace.js, js/10_theo_doi.js (new), js/_danh_sach.txt, mau_forms_thi_clb/bieu_mau.py, tao_mau_forms.py,
  .claude/skills/soat-ma/scripts/kiem_nhanh.py, docs (status, spec, CLAUDE_CHI_TIET, CHANGELOG, TIEN_DO).

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-10 | Opus (SOLO) | F1 setup: branch claude/fa-gaps from keen-ride 60f75a5 | phase 1 done 7/7 |
| 2026-11-10 | Opus (SOLO, son hat) | GAP-0 done: fa_dieu_chinh + vi_tri_hien_tai; 16 tests red first; related 2456 passed/1 skipped; 2 mutations caught; 60/60 | |
| 2026-11-10 | Opus (SOLO, son hat) | GAP-1 done: attendance + release; 13 tests red first (3 Chromium); related 4768 passed/4 skipped (D1 marker, numpy, POSIX user); 2 mutations caught; 60/60 | |
| 2026-11-10 | Opus (SOLO, son hat) | GAP-2 done: waitlist invites; 10 tests red first (1 Chromium); related 4636 passed/4 skipped; 3 mutations caught; 60/60 | |
| 2026-11-10 | Opus (SOLO) | Phase 1 7/7; wave 1 done + GO; wave 2 coded (suites unconfirmed); wave-3 spec draft | context limit stop |
| 2026-11-10 | Opus (SOLO) | Wave 2 suites + GO; waves 3–4 coded (GAP-7..14); GAP-13 spec edge rule corrected | suites running |
