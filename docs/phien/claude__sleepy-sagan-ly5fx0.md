# Branch handoff: claude/sleepy-sagan-ly5fx0

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
Workflow tooling for Claude sessions on this repo (no algorithm change): session handoff files, token-saving rules in CLAUDE.md.

## Plan
- [x] Per-branch handoff file in `docs/phien/` (template: `_TEMPLATE.md`)
- [x] Stop hook triggers handoff when context > 400k tokens
- [x] Trim CLAUDE.md (details moved verbatim to `docs/ke_hoach/CLAUDE_CHI_TIET.md`)
- [x] Rules: run only related tests; NO SUBAGENT; model roles (Opus plans, Sonnet writes, Haiku reads)

## Current state
- All of the above is committed and pushed. No code in the algorithm was touched.
- Old `docs/ke_hoach/TRANG_THAI_PHIEN.md` and its per-turn hook were replaced by this per-branch scheme.

## Decisions and gotchas
- Context size is read from the last `usage` entry of the transcript (`transcript_path`), fallback bytes/4.
- Threshold 400000 tokens; override with env `HANDOFF_TOKENS`.
- Hook blocks at most once per turn (`stop_hook_active`).

## Next steps
1. Truong picks the next registry item (plan suggests Z6) and creates a new branch; copy `_TEMPLATE.md` to `docs/phien/<branch>.md`.

## Files touched
- CLAUDE.md, .claude/settings.json, .claude/hooks/handoff_khi_day_ngu_canh.py, docs/phien/*, docs/ke_hoach/CLAUDE_CHI_TIET.md, .claude/skills/soat-ma/SKILL.md

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Built handoff scheme, NO SUBAGENT rule, related-tests-only rule, CLAUDE.md trim | Opus advised via advisor tool |
