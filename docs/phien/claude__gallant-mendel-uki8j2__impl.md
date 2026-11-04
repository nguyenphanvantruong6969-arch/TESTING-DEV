# Branch handoff: claude/gallant-mendel-uki8j2 (impl)

> Role: impl (Sonnet). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S. Protocol: `docs/phien/T3_GIAO_THUC.md`.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Implement T3 lots L0..L3 on this branch (spec = "Lot L<n>" in `docs/phien/claude__gallant-mendel-uki8j2.md`).

## Plan
- [x] L0: B1/T3-26, B2/T3-01, B3/T3-42 (tests first, related tests, invariant 1, soat-ma, CHANGELOG + TIEN_DO, commit, push)
- [ ] L1  - [ ] L2  - [ ] L3 (wait for `GO L<n>`)

## Current state (overwrite each handoff)
- L0 implemented and pushed (see commit `T3-L0: ...`); `IMPL DONE L0` sent to coord. Idle, waiting for next message.
- Tests for L0: `tests/test_t3_l0_backend.py` (11), `tests/test_giao_dien_t3_l0.py` (6, Chromium).
- Test env: system `pytest` (uv tool, /root/.local/bin/pytest) with playwright+openpyxl installed via
  `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python ...`. `python3 -m venv` + pip hung on the proxy; do not retry it.
  UI tests need `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.

## Decisions and gotchas
- B1 backend: `None` = not sent = keep stored value; `""`/`0` = explicit clear. UI: editing mode (row click) sends explicit values,
  typing by hand sends `null` for blank optional fields.
- B2: guard sits before backup in `_run_pipeline_da_khoa`; error `chua_co_du_lieu_de_chay`, returned via `_fail_co_buoc([], ...)`.
- `stb_lock` always has one seeded row; assert on `is_locked`, not row count.
- Invariant 1 harness: `kiem_nhanh.kiem_trung_khit(new, old, seeds, 3)` with `old` = `git archive origin/main`; 20 seeds via direct call.

## Next steps (ordered)
1. Wait for `GO L1` / `FIX L0`.

## Files touched
- api.py, api_quan_ly.py, i18n_errors.py, i18n_loi.js, i18n.js, index.html, style.css, js/02_van_hanh.js, js/05_quan_ly.js
- tests/test_t3_l0_backend.py, tests/test_giao_dien_t3_l0.py, CHANGELOG.md, docs/ke_hoach/TIEN_DO.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Sonnet (impl) | L0 implemented | |
