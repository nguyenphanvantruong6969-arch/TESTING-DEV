# Branch handoff: claude/forms-gop

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Cut IT work on path B (Microsoft Forms) for the club-allocation kiosk: FA-M2b = ONE registration form for all days
(`tao_mau_forms.py --fa-daa --mot-bieu-mau`); FA-M6b = ONE "after results" form (3 feedback questions + appeal
branch) with one kiosk import button. Spec: `docs/ke_hoach/FORMS_GOP_KE_HOACH.md` (follow exactly). Built on
`origin/claude/fa-gaps`. Push only to `claude/forms-gop`; no PR. All numbers SIMULATED; everything TH (not tried on real Forms).

## Plan (written by Opus; ticked by Sonnet)
- [x] FA-M2b: combined registration form (layout, generator, guide, tests, docs)
- [x] FA-M6b: combined "after results" form (layout, generator, reader, API, UI, tests, docs)
- [ ] Section 4: soat-ma, diff -r vs snapshot, report `docs/phien/bao_cao_dem/<date>_forms_gop.md`

## Current state (overwrite each handoff)
- Done: FA-M2b (commit 56fa911) and FA-M6b (code, API, UI, generator, tests, docs). Related tests: 2384 passed, 1 skipped
  (D1 deferral, not UI); Chromium UI tests really ran. `kiem_nhanh --co-so origin/main --so-seed 20` = 7/7, 60/60 identical.
  `diff -r` of `--fa-daa`, `--phan-hoi`, `--tuan-3` vs the step-1.0 snapshot: identical. ruff clean.
- In progress: plan section 4 (soat-ma review on `git diff origin/claude/fa-gaps..HEAD`, report in
  `docs/phien/bao_cao_dem/2026-11-11_forms_gop.md`, verify remote HEAD = local HEAD).
- Open problems: none.

## Decisions and gotchas (keep short)
- `tests/conftest.py` pre-creates a fake dir `TaiXuong_gia` in `tmp_path`: tests that list a folder must ignore it.
- Converter `doc_dang_ky_fa_forms` needed NO change for FA-M2b (tests prove one combined sheet == two per-day sheets).
- Combined docx name: `NHAP_FORMS_DANG_KY_TAT_CA.docx` (prefix `NHAP_FORMS_DANG_KY_`, so cleanup removes stale per-day files).
- Over the Forms question limit (`TRAN_CAU_MOI_BIEU_MAU`) -> `bm.LoiDeThi`, CLI prints `KHÔNG GHI TỆP NÀO — …`, exit 1.
- FA-M6b: `[kn_buoi]` is typed 'checkbox' in the layout only; the .docx writer prints lettered choices for any type, so the
  guide tells IT to switch on "Multiple answers" by hand (fallback allowed by the plan, recorded here).
- FA-M6b `khieu_nai_loi` items are exactly `{student_id, buoi, code}`; the UI fills `so_ngay` from the last loaded appeals panel.
- Unknown student in the file -> counted in `bo_qua` (not an appeal error); a known student with no result for that day ->
  `khieu_nai_khong_hop_le` in `khieu_nai_loi`. Day codes valid for the reader = distinct `match_results.buoi` + `clubs.buoi`.
- Old 3-question file (no `[co_sai]`) still loads through `nhap_sau_ket_qua_forms` when feedback is on (appeal part empty).
- No separate kiosk user guide documents the feedback panel; docs updated in `FA_SAU_XEP.md` (3.5, 4). The generated
  `CAI_DAT_FORMS_PHAN_HOI.md` was left untouched on purpose (`--phan-hoi` must stay byte-identical).
- The plan's step "lock" in LATEST_INSTRUCTION §2 refers to the keen-ride handoff; not used here.

## Next steps (ordered)
1. Plan section 4: soat-ma, snapshot diff, Vietnamese report, push, verify remote HEAD = local HEAD.

## Files touched
- mau_forms_thi_clb/bieu_mau.py, mau_forms_thi_clb/tao_mau_forms.py: FA-M2b layout + generator
- tests/test_fa_m2b_mot_bieu_mau.py: FA-M2b tests
- fa_sau_xep.py, api_sau_xep.py: `doc_tep_forms_khieu_nai`, `nhap_sau_ket_qua_forms`, shared `_chen_phan_hoi` / `_them_khieu_nai`
- i18n_errors.py, i18n_loi.js, i18n.js, index.html, js/10_theo_doi.js, tests/test_ws_nhan.py: new codes + button
- tests/test_fa_m6b_sau_ket_qua.py, tests/test_giao_dien_fa_m6b_sau_ket_qua.py: FA-M6b tests
- docs/he_sinh_thai/FA_SAU_XEP.md, docs/ke_hoach/FA_DAA_KE_HOACH.md, CLAUDE_CHI_TIET.md, CHANGELOG.md, TIEN_DO.md: docs and bookkeeping

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-11 | Sonnet (forms-gop) | FA-M2b: tests red first (13), `cac_phan_fa_gop`, `sinh_dang_ky(mot_bieu_mau)`, `--mot-bieu-mau`; mutation (drop a day) caught by 5 tests; `diff -r` vs snapshot identical | TH |
| 2026-11-11 | Sonnet (forms-gop) | FA-M6b: tests red first (22 + 2 UI), reader, API refactor + `nhap_sau_ket_qua_forms`, generator, UI button; mutations (Forms time -> import time; ignore co_sai) caught | TH |
