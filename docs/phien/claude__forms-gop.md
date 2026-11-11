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
- [x] Section 4: soat-ma, diff -r vs snapshot, report `docs/phien/bao_cao_dem/<date>_forms_gop.md`
- Phase 2 (Truong approved 2026-11-11, "giảm việc IT vòng 2"): every IT step in the kiosk UI, both paths A/B, no CLI.
  Spec: `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md`. Parallel mode (Truong, 2026-11-11): 3 independent Sonnet sessions
  with `docs/ke_hoach/it_ui_song_song/PROMPT_A|B|C.md` (A: G0 + FA-M7 + integration here; B: FA-M9 + FA-M10; C: FA-M8).
- [x] FA-M7 (+ G0): groundwork (`api_forms.py`, `kiosk.spec`, tab "Chuẩn bị đợt", path choice) + one source for clubs/exams
- [ ] FA-M9: drop Forms/List exports into the kiosk (auto-detect file kind + variant, confirm buttons, same import path) — NOT DONE — worker B/C BLOCKED (branch never pushed)
- [ ] FA-M8: "Tạo bộ biểu mẫu" button (zip per path, Phiếu CLB docx, no answer ticking on Forms, XEM_LAI_DAP_AN.xlsx) — NOT DONE — worker B/C BLOCKED (branch never pushed)
- [ ] FA-M10: after-allocation buttons (KetQua List CSV with email, who has not registered, List diff) — NOT DONE — worker B/C BLOCKED (branch never pushed)
- [ ] Phase 2 finish: soat-ma, snapshot diff, report `docs/phien/bao_cao_dem/<date>_it_giao_dien.md`

## Current state (overwrite each handoff)
- Merged `origin/claude/it-ui-a` (G0 + FA-M7, GREEN on its branch) into this branch (no conflicts); bookkeeping folded in
  (CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET, HUONG_DAN_SU_DUNG §16, T4M note); report `docs/phien/bao_cao_dem/2026-11-11_it_giao_dien.md`.
- NOT DONE: FA-M9, FA-M8, FA-M10 (workers B/C never pushed). Kiosk tab "Chuẩn bị đợt" has steps 1-2 only.
- Full-suite/CI numbers: see `docs/phien/IT_UI_STATUS.md` (the lead owns it).
- Open problems: none in the merged code.

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
- Phase 2 decisions (Truong): keep both paths, IT chooses; everything via UI (non-technical); no Post scores, students
  still take the quiz; Google path undecided -> untouched. Opus: kiosk UI covers FA-DAA only; email stays in files in
  the workspace folder (no schema change); converter warnings stay Vietnamese.

## Next steps (ordered)
0. Re-run PROMPT_B / PROMPT_C (they branch from this branch, now with G0 + FA-M7) or SOLO FA-M9 -> FA-M8 -> FA-M10.
1. Truong pastes the CHU_TRI prompt from `docs/ke_hoach/it_ui_song_song/TU_DONG.md` §1 into an Opus session (Opus
   delegates every task to Sonnet, then loops until all tests + CI are green; SOLO / DIEU_PHOI are fallbacks);
   manual alternative: 3 Sonnet sessions with the blocks at the top of PROMPT_A/B/C. Progress: `docs/phien/IT_UI_STATUS.md`.
2. Truong decides where `claude/forms-gop` merges (no PR opened).

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
| 2026-11-11 | Sonnet (forms-gop) | Section 4: soat-ma review (no high/medium findings), `diff -r` vs snapshot identical, Vietnamese report | TH |
| 2026-11-11 | Opus (forms-gop) | War room "giảm việc IT vòng 2": 9 redundancies (R1-R9) found; Truong approved FA-M7..FA-M10; wrote `IT_GIAO_DIEN_KE_HOACH.md` | docs only |
| 2026-11-11 | Opus (forms-gop) | Split phase 2 into 3 parallel prompts (file ownership, marker blocks, G0 sync, integration by A) | docs only |
| 2026-11-11 | Opus (forms-gop) | No-human-input runbook TU_DONG.md (SOLO / DIEU_PHOI) + AUTO mode in PROMPT_A/B/C | docs only |
| 2026-11-11 | Opus (forms-gop) | TU_DONG.md: role CHU_TRI (Opus delegates to Sonnet, reviews) + green loop until full suite, coverage, CI and Windows build pass | docs only |
| 2026-11-11 | Opus (forms-gop) | PROMPT_A/B/C rebuilt: each pasted into an Opus lead that delegates to Sonnet coders and runs its own green loop; A integrates + final green loop | docs only |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn8TcYiUVHyfRHBD82v INTEGRATE DONE 739736e | merged it-ui-a; 161 related passed (UI ran, 0 skipped); kiem_nhanh 7/7; ruff clean; B/C not merged |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn8TcYiUVHyfRHBD82v INTEGRATE-FIX1 DONE 9ac0998 | HUONG_DAN §16 path A/B meaning fixed; 92 doc tests passed; ruff clean; kiem_nhanh 7/7 |
