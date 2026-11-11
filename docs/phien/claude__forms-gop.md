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
- [ ] FA-M6b: combined "after results" form (layout, generator, reader, API, UI, tests, docs)
- [ ] Section 4: soat-ma, diff -r vs snapshot, report `docs/phien/bao_cao_dem/<date>_forms_gop.md`

## Current state (overwrite each handoff)
- Done so far: FA-M2b code + tests (13 green, red first, mutation caught), snapshot `diff -r` identical, ruff clean.
- In progress: related tests + `kiem_nhanh` for FA-M2b, then commit/push.
- Snapshot of old generator output (step 1.0) is in the session scratchpad `snap/` (regenerate from
  `origin/claude/fa-gaps` with the three modes if the scratchpad is gone).
- Open problems: none.

## Decisions and gotchas (keep short)
- `tests/conftest.py` pre-creates a fake dir `TaiXuong_gia` in `tmp_path`: tests that list a folder must ignore it.
- Converter `doc_dang_ky_fa_forms` needed NO change for FA-M2b (tests prove one combined sheet == two per-day sheets).
- Combined docx name: `NHAP_FORMS_DANG_KY_TAT_CA.docx` (prefix `NHAP_FORMS_DANG_KY_`, so cleanup removes stale per-day files).
- Over the Forms question limit (`TRAN_CAU_MOI_BIEU_MAU`) -> `bm.LoiDeThi`, CLI prints `KHÔNG GHI TỆP NÀO — …`, exit 1.
- The plan's step "lock" in LATEST_INSTRUCTION §2 refers to the keen-ride handoff; not used here.

## Next steps (ordered)
1. Commit FA-M2b, `git pull --rebase origin claude/forms-gop` (branch may not exist yet), `git push -u origin claude/forms-gop`.
2. FA-M6b per plan §2 (tests first).
3. Plan §4 finish.

## Files touched
- mau_forms_thi_clb/bieu_mau.py, mau_forms_thi_clb/tao_mau_forms.py: FA-M2b layout + generator
- tests/test_fa_m2b_mot_bieu_mau.py: FA-M2b tests
- docs/ke_hoach/FA_DAA_KE_HOACH.md, CLAUDE_CHI_TIET.md, CHANGELOG.md, TIEN_DO.md: bookkeeping

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-11 | Sonnet (forms-gop) | FA-M2b: tests red first (13), `cac_phan_fa_gop`, `sinh_dang_ky(mot_bieu_mau)`, `--mot-bieu-mau`; mutation (drop a day) caught by 5 tests; `diff -r` vs snapshot identical | TH |
