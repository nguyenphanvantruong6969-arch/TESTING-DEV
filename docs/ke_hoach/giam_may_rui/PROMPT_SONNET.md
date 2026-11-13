# Start prompt for the Sonnet coding session (paste as the first message)

```
You are the coder (CLAUDE.md rule 11: Sonnet codes and ticks the Plan). Work in this repository.

1. Create branch claude/giam-may-rui from origin/claude/forms-gop (git fetch origin claude/forms-gop first).
   Push only to claude/giam-may-rui. Never force-push. Do not open, merge or close any PR.
2. Read, in order: CLAUDE.md, docs/phien/claude__giam-may-rui.md, docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md.
   Follow the spec exactly. Locate code by function name, never line numbers.
3. Do the items in order: FA-CT1 → FA-CT2 → FA-D7L. For each item:
   - write the failing tests from its kiem_nhan first, then the minimal code, then run only the related tests
     (./.venv/bin/python -m pytest -q <files>);
   - one commit per item ("FA-CT1: …"), update CHANGELOG.md, docs/ke_hoach/TIEN_DO.md and tick the Plan in the
     handoff file;
   - run .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20 → must be 7/7 with 60/60
     identical; then push.
4. Never touch run_rbda, run_rbda_nhieu_buoi, club_choice_function, compute_club_priority, verify_stability,
   the STB lottery or run_history. FA-CT1/CT2 are read-only on app.db. FA-D7L is an option, default OFF, and must
   keep today's output byte-identical when off.
5. Stop and ask Truong (do not guess) if: an invariant conflicts with the spec, a schema/CSV column change or a new
   library seems necessary, or the code differs clearly from what the spec assumes. Mark the item BLOCKED in the
   handoff file with the reason.
6. No Agent tool / subagents. All numbers are SIMULATED (label "MÔ PHỎNG"). No report conclusions.
7. When all three items are done: run the soat-ma skill (four tiers, report only), write
   docs/phien/bao_cao_dem/<date>_giam_may_rui.md (Vietnamese, short), update the handoff "Current state", push,
   and reply to Truong in Vietnamese, plain language: what teachers can now click, what the score option does,
   the simulated before/after numbers from FA-D7L test 3, and what he must decide (merge or not).
```

Suggested session settings: model Sonnet 5.5 (`claude-sonnet-5-5`), repository branch `claude/forms-gop` as the
starting point, outcome branch `claude/giam-may-rui`.
