# Branch handoff: claude/gallant-mendel-uki8j2 (tester)

> Role: tester (Opus for L0, Sonnet for L1-L3). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S.
> Protocol: `docs/phien/T3_GIAO_THUC.md`. English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

## Plan
- [x] L0 review 7e90e14..661bccb -> 2 BUGS (see Current state)
- [x] L0 re-check fix1 9151962..e8944b2 -> NO BUGS  - [x] L1 reviewed + fix1 re-check NO BUGS  - [x] L2 reviewed (1 bug + 5 notes reported)  - [ ] L3

## Current state (overwrite each handoff)
- L2 fix1 (a8b4407..a1258c3) re-checked. Reported to coord ("TESTER REPORT L2 fix1"): 1 BUG, rest OK.
  BUG: tests/test_giao_dien_bang_loi.py::test_trang_dich_dung_ma_loi_ca_hai_ngon_ngu[index.html|recovery.html] fail (2):
  page now shows "Thứ 2" via nhanHoaBuoi but test compares with i18n_errors.format_message (raw `thu_2`). Impl did not run it.
- OK: btn_reset_entry vi/en school ("học sinh") + company ("nhân viên"/"employee"), matches confirm text; tab-01 warnings map thu_2->Thứ 2/Mon,
  list buoi too, unknown "Buổi tối" kept, caller params not mutated; tab 03 "Lần chạy gần nhất: 04/11/2026 16:12" (en "Latest run:"), no seed;
  parity test present; ws chooser last th is sr-only (no visible header). Related tests 94 run: 92 pass, the 2 above fail.
- T3-32 collapse skipped: acceptable as note (scroll-to-entry exists; old UI tests click other cards after select).
- Screenshots replaced: docs/nghien_cuu/anh_t3/sau_L2/01, 04, 07.

## Decisions and gotchas
- Test env (new container): `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python -r requirements-dev.txt
  playwright==1.63.0`, then `/root/.local/bin/pytest`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- `python3 tao_i18n_js.py` (any args) rewrites i18n_loi.js; `git status` clean afterwards = JS is in sync.
- Probe scripts live in the session scratchpad only (not committed).
- Browser probes: standalone scripts in scratchpad using `browser_host.serve(api, GOC, 'index.html', open_browser=False)` + Playwright; company workspace via `workspace.tao(dir, name, cfg)` + `PipelineAPI(..., thu_muc_goc_ws=, ws_da_chon=True)`.
- Related-test selection: grep tests/ for changed i18n keys, element ids, function names AND changed visible texts; run in background, wait with `until ! pgrep -f bin/pytest`.
- Quiet runs: `pytest -q -p no:cacheprovider --no-header -rN --tb=line <files> | tail -3`.

## Next steps (ordered)
1. Wait for fix2 re-check (test_giao_dien_bang_loi) or `REVIEW L3` from coord. Screenshots go to docs/nghien_cuu/anh_t3/sau_L<n>/ (<=6).

## Files touched
- docs/nghien_cuu/anh_t3/sau_L0/*.png, sau_L1/*.png, this file.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Opus (tester) | L0 review, invariant 1 re-check, 3 screenshots | 2 bugs (reserve default 0; 'tab' in vi text) |
| 2026-11-04 | Opus (tester) | L0 fix1 re-check | NO BUGS |
| 2026-11-04 | Sonnet (tester) | L1 + L0fixci1 review, 6 screenshots | 2 failing tests outside impl's set; 2 minor notes |
| 2026-11-04 | Sonnet (tester) | L1 fix1 re-check | NO BUGS |
| 2026-11-04 | Sonnet (tester) | L1 fix1 re-check NO BUGS; L2 review | L2: 1 bug + notes |
| 2026-11-04 | Sonnet (tester) | Handoff at 200k | state above is current |
| 2026-11-04 | Sonnet (tester) | L2 fix1 re-check, screenshots 01/04/07 | 1 bug: test_giao_dien_bang_loi x2 |
