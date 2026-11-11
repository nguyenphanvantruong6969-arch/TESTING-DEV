Branch: claude/it-ui-a
STATUS: RUNNING (green loop round 2: waiting for CI Linux job)
Lead: Opus CHU_TRI session_01TGThn5vxmXkqyACZzBpJCq (model claude-opus-5-5). BASE = fe373493223aeadf9e0b20cb88260d80eaad74a0

# Branch handoff: claude/it-ui-a

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Worker A of the parallel IT-UI job. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_A.md` ("Your job", "Shared
> contract", "Sonnet coder rules") + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` §1–§2. PROMPT_A wins where they differ.

## Feature / goal
Worker A: G0 groundwork (code contract shared by workers B and C: `forms_dot.py`, `api_forms.py` FormsMixin, stubs
`api_forms_nap.py`/`api_forms_bo.py`, `kiosk.spec`, tab "Chuẩn bị đợt", marker blocks, error codes), then FA-M7 (one
source for clubs and exams), then green loop, then Phase 3 integration of `claude/it-ui-b|c` into `claude/forms-gop`.
All numbers SIMULATED; all Forms work TH.

## Plan (written by Opus; ticked by Sonnet)
- [x] G0: PROMPT_A "Your job" 1 exactly (tests first: `tests/test_fa_m7_dong_goi.py`, `tests/test_fa_m7_duong.py`,
      `tests/test_giao_dien_fa_m7_the.py`; nav-count UI tests updated; `kiem_nhanh` 7/7; commit message `FA-M7 G0: ...`)
- [x] FA-M7: plan §2 (`nap_phieu_clb`, `tai_mau_de_thi`, `nap_de_thi` in `api_forms.py`; `mau_forms_thi_clb/so_de_thi.py`
      with `ghi_mau_kiosk`, `doc_so_de_thi`; tests `tests/test_fa_m7_nguon_mot_lan.py` + API + UI; mutation recorded);
      bookkeeping only into `docs/ke_hoach/it_ui_song_song/MANH_A.md`
- [ ] Green loop on `claude/it-ui-a` (lead)
- [ ] INTEGRATE (Phase 3, on `claude/forms-gop`)
- [ ] Green loop on `claude/forms-gop` + FINISH (plan §7 report, `docs/phien/IT_UI_STATUS.md` = `IT-UI GREEN`)

## Current state (overwrite each handoff)
- G0 (c7b5d1d) and FA-M7 (d5a303e + FA-M7-FIX1 414a94c: `loai` carried into forms/de_thi.json) done, lead review PASS:
  166 related tests passed (Chromium really ran), ruff clean, `kiem_nhanh` 7/7, mutation recorded in MANH_A.md.
- Now: green loop round 1 on `claude/it-ui-a` (lead). B and C branches not on origin yet (13:05 UTC).

## Decisions and gotchas (keep short)
- Env setup: `LATEST_INSTRUCTION.md` PART 2 §1 on this branch (venv, `playwright==1.63.0`, unshallow, `origin/main`).
- G0 review notes: `fa_duong` lives in `MAC_DINH_TRUONG_HOC.rules` (not in `LUAT_XEP_MAC_DINH`, so not in
  `run_history.luat_xep`); tab wraps `window.wsApDungCauHinh` to follow `FA_BAT`.
- UI tests: prefix `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; skipped != passed.

## Green loop round 1 (claude/it-ui-a @ 80aa188)
- Local full suite: 1 failed, 5860 passed, 4 skipped (none UI: D1 deferral, 2x numpy missing locally, POSIX user),
  coverage 93.35 % (>= 85). ruff clean. `kiem_nhanh --so-seed 20` 7/7, 60/60. Generator snapshot vs BASE: identical
  (only `docProps/core.xml` timestamp of the default-mode xlsx differs; unzipped content otherwise equal).
- FAILED `tests/test_van_phong_tu_nhien.py::test_moi_cau_hien_thi_deu_viet_tu_nhien`:
  `i18n_errors.forms_thieu_email [vi] gạch ngang nối câu: 'Thiếu danh sách email - mã học sinh. Hãy nạp tệp này trước.'`
- CI run 43025992926: cancelled by the next push (round already red locally); FIX-1 delegated.

## Green loop round 2 (claude/it-ui-a @ 5ead67e, after FIX-1 db76ea9)
- Local: 5861 passed, 0 failed, 4 skipped (none UI), coverage 93.35 %, ruff clean, `kiem_nhanh --so-seed 20` 7/7, 60/60.
- Windows build run 43035758322: SUCCESS (exe builds with `mau_forms_thi_clb` inside; NOTE: this workflow also uploads
  to the shared release `ban-moi-nhat`, so that release now holds this branch's build).
- CI Tests run 43035270644: lint SUCCESS, "Bo test (Windows)" SUCCESS; Linux job failed twice (attempts 1 and 2) in
  step "Cai Chromium cho Playwright": runner apt `Temporary failure resolving 'azure.archive.ubuntu.com'` (GitHub
  infra, no test ran). Not a code failure; retried on the next HEAD (this handoff commit, code unchanged).

## Waiting for Truong
- (none)

## Requests (REQUEST B: / REQUEST C: lines from worker A go here)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-11 | Opus lead | Branch + handoff created, BASE recorded | |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn85Pq2YHSsR4JaidNW G0 DONE c7b5d1d | tests: m7_dong_goi, m7_duong, giao_dien_fa_m7_the red→green; kiem_nhanh 7/7 (60/60); ruff clean |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn8yVQTjim3hxvfMDWv FA-M7 DONE d5a303e | tests: m7_nguon_mot_lan 18 + giao_dien_fa_m7_nguon 3 red→green; mutation (drop club cross-check) 3 red; kiem_nhanh 7/7; ruff clean |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn8yVQTjim3hxvfMDWv FA-M7-FIX1 DONE 414a94c | loai carried into de_thi.json; 2 tests red→green; related 99 passed; kiem_nhanh 7/7 |
| 2026-11-11 | Sonnet coder | CODER session_01TGThn6pDja9nUgPuhpnPyu FIX-1 DONE db76ea9 | test_van_phong_tu_nhien red→green (not pre-existing: G0 text); 101 related passed; ruff clean; kiem_nhanh 7/7 |
