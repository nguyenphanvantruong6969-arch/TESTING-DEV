# Branch handoff: claude/fable-ga-audit

## Feature / goal
Research only (CLAUDE.md rule 11, Fable): audit FA-DAA (goal G-A of `docs/fable/02_FABLE_BRIEF.md`) for
stability, truthfulness and fairness risks before real use. Related item: A13 (FA-3/4/5/6). No production code edits.

## Plan
- [x] Top 3 findings for G-A with evidence, written to `docs/fable/03_RESEARCH_MEMO.md`
- [x] G-A.2: solutions per finding, school-size simulations, other improvements (no new student input)
- [x] G-H first pass (reducing luck): `docs/fable/04_GH_REDUCING_LUCK.md`, top 3 methods, stopped to ask
- [ ] Wait for Truong's decisions (below)

## Current state (overwrite each handoff)
- Done so far: memo section G-A (findings 1–3, CE1–CE4, tables A1–A4, all SIMULATED);
  script `du_lieu_test/fable_ga_kiem.py` (subcommands phan_vi_du, tim_lech, huy_chuong, quan_the).
- In progress: nothing.
- Tests: none added (research role). Script needs `pytest` importable for `tim_lech` (imports the test generator).
- Open problems: decisions pending from Truong.

## Decisions and gotchas (keep short)
- Constraint (Truong, 2026-11-13): students enter only today's inputs; no new student input in any proposal.
- G-A.2 recommendations: F1 leave `so_toi_thieu` empty this term; F3 block FA + strict groups unless the school
  needs grade priority (then fix: `bo_qua_du_tru=False` + `GROUP` reason); F2 default medals skip clubs the
  student cannot enter (D1), trade-off: fewer true NV1 for honest students, smaller edge for informed ones.
- Pending (Truong): (1) use `so_toi_thieu` this term or not (memo options 1a/1b/1c); (2) medal guidance and
  dead-medal handling (2a–2d; 2c needs new invariant-2 exception text); (3) FA-DAA with strict group priority:
  block (3a) or support (3b).
- Medal tables use 5 clubs/day, lists of 4: smaller than the school; rerun at school size before quoting.

## Next steps (ordered)
1. Get Truong's answers; 2. school-sized rerun of tables A2–A4; 3. G-A question 3 (integer-score ties);
4. remaining "Not yet examined" list in the memo.

## Files touched
- docs/fable/03_RESEARCH_MEMO.md: G-A section
- du_lieu_test/fable_ga_kiem.py: research script (read-only use of production code)
- du_lieu_test/fable_ga2_giai_phap.py, fable_ga2_huy_chuong.py: G-A.2 simulations (f1, f3, f2, f2_br, boc_tham)

## Session log (append only, newest last)
- 2026-11-12: first G-A pass, top 3 findings, stopped to ask Truong.
- 2026-11-13: G-A.2 written after Truong confirmed the Opus request; stopped for decisions.
- 2026-11-13: G-H first pass after Truong's OK; script `du_lieu_test/fable_gh_giam_may_rui.py`. Top lever: seats by demand.
