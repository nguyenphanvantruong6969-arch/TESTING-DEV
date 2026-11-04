# Branch handoff: claude/gallant-mendel-uki8j2 (tester)

> Role: tester (Opus for L0, Sonnet for L1-L3). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S.
> Protocol: `docs/phien/T3_GIAO_THUC.md`. English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

## Plan
- [x] L0 review 7e90e14..661bccb -> 1 BUG (see Current state)
- [ ] L0 re-check fix  - [ ] L1  - [ ] L2  - [ ] L3

## Current state (overwrite each handoff)
- L0 reviewed. Verdict: 1 BUG.
  1. js/05_quan_ly.js `initAdminHandlers` (btnSaveClub handler, `reserveCapacity` line) + index.html `clubFormReserveCapacity value="0"`
     + `datLaiFormClb` resets it to "0": in hand-typed mode the reserve field is never blank, so retyping an existing club id,
     name and capacity sends explicit 0 and wipes reserve_capacity (4 -> 0). Group and session are kept. The impl UI test
     `test_go_tay_lai_ma_cu_...` hides it by clearing the field first (`page.fill(..., "")`).
- Everything else OK: B1 backend (None keeps, ""/0 clears, capacity vs stored reserve checked, Sổ nhập path untouched,
  round-trip of imported reserve_group/buoi unchanged), B2 (0 students / 0 clubs / both: no run_history row, stb_lock unchanged,
  no .bak file, steps=[]; normal data still runs; UI disables Run with reason and re-enables after data + tab reload),
  B3 text, i18n_loi.js regenerates byte-identical, no unrelated file changes.
- Invariant 1 re-checked independently: own script, 3 datasets x seeds 1..20, wharton off AND default-on, 2 runs each,
  compared match_results + stb numbers + run_history count + stb_lock vs `git archive origin/main`: 60/60 identical both modes.
- Screenshots: docs/nghien_cuu/anh_t3/sau_L0/ (01 empty workspace tab 01, 03 tab 05 form labels, 04 row-click prefill).

## Decisions and gotchas
- Test env (new container): `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python -r requirements-dev.txt
  playwright==1.63.0`, then `/root/.local/bin/pytest`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
- `python3 tao_i18n_js.py` (any args) rewrites i18n_loi.js; `git status` clean afterwards = JS is in sync.
- Probe scripts live in the session scratchpad only (not committed).

## Next steps (ordered)
1. Wait for `REVIEW L0 fix<k>` or `REVIEW L1 ...` from coord.

## Files touched
- docs/nghien_cuu/anh_t3/sau_L0/*.png, this file.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Opus (tester) | L0 review, invariant 1 re-check, 3 screenshots | 1 bug (reserve field default 0) |
