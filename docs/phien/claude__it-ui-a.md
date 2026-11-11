Branch: claude/it-ui-a
STATUS: RUNNING (G0)
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
- [ ] FA-M7: plan §2 (`nap_phieu_clb`, `tai_mau_de_thi`, `nap_de_thi` in `api_forms.py`; `mau_forms_thi_clb/so_de_thi.py`
      with `ghi_mau_kiosk`, `doc_so_de_thi`; tests `tests/test_fa_m7_nguon_mot_lan.py` + API + UI; mutation recorded);
      bookkeeping only into `docs/ke_hoach/it_ui_song_song/MANH_A.md`
- [ ] Green loop on `claude/it-ui-a` (lead)
- [ ] INTEGRATE (Phase 3, on `claude/forms-gop`)
- [ ] Green loop on `claude/forms-gop` + FINISH (plan §7 report, `docs/phien/IT_UI_STATUS.md` = `IT-UI GREEN`)

## Current state (overwrite each handoff)
- G0 done and pushed (commit `FA-M7 G0: ...`). Next: FA-M7 (plan §2). `so_de_thi.py` is a docstring-only placeholder.
- `rules.fa_duong` default None added to `cau_hinh_ws.MAC_DINH_TRUONG_HOC`; not in luat_xep. FA tab hook wraps `wsApDungCauHinh` from `js/11_chuan_bi.js` (no edit to other workers' JS).

## Decisions and gotchas (keep short)
- Env setup: `LATEST_INSTRUCTION.md` PART 2 §1 on this branch (venv, `playwright==1.63.0`, unshallow, `origin/main`).
- UI tests: prefix `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; skipped != passed.

## Waiting for Truong
- (none)

## Requests (REQUEST B: / REQUEST C: lines from worker A go here)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-11 | Opus lead | Branch + handoff created, BASE recorded | |
