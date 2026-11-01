# Branch handoff: claude/wharton-mac-dinh-bat

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
A13.13: make the school workspace default `rules.wharton = True` (commitment points on by default).
Truong explicitly approved breaking invariant 1 (default config no longer byte-identical to before) for this item.
Invariants 2-8 still hold. Not in scope: "template header by vocabulary" (Direction A/B).

## Plan (written by Opus; ticked by Sonnet)
- [ ] 1. Write failing tests (default True; new/migrated workspace has Wharton on; builtin template ticked; tier/per_person without explicit `wharton` stays valid; explicit `wharton: true` + bad combo still errors)
- [ ] 2. Minimal fix: `cau_hinh_ws.MAC_DINH_TRUONG_HOC`, `_chuan_hoa` (auto-off when not explicit), `tron_len` (auto-off on update)
- [ ] 3. grep affected tests, run them + files touched; fix by principle (default-off assertions -> new default; exact-match tests -> explicit `wharton: false`); no delete, no skip
- [ ] 4. Reference modes / du_lieu_test scripts: pass `wharton: false` explicitly
- [ ] 5. Docs/UI wording (so_nhap huong_dan, HUONG_DAN_SO_NHAP.md); `ruff check .`; skill soat-ma
- [ ] 6. CHANGELOG.md + TIEN_DO.md row A13.13 (record the invariant-1 exception); commit; push `claude/wharton-mac-dinh-bat`; no PR

## Current state (overwrite each handoff)
- Branch created from claude/sleepy-sagan-ly5fx0. Work starting.

## Decisions and gotchas
- Exception to invariant 1 approved by Truong; record in CHANGELOG + TIEN_DO.
- `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"]` stays False (pipeline-level fallback for rules without the key; workspace default comes from cau_hinh_ws).

## Next steps
1. See Plan.

## Files touched
- docs/phien/claude__wharton-mac-dinh-bat.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Branch + handoff created | |
