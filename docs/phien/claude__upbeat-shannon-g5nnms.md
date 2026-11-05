# Branch handoff: claude/upbeat-shannon-g5nnms

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).

## Feature / goal
T4M-NC (outside the 33-item registry; Truong asked 05/11/2026): research plan for fitting RB-DA into the school's
EXISTING Microsoft ecosystem instead of the Google design of T4. The school runs a Power Apps canvas app
"ECA Registration HVT" (M365 A3/A5, students sign in with school email, PowerSchool auto-syncs, one pick per weekday,
no capacity cap, admin locks after deadline, manual allocation). T4's premise "Microsoft rejected because Power Apps is
paid" is wrong for this school. Plan: `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (22 research questions NC-01..22,
5 phases, 4 session prompts P1..P4, IT interview script, decision matrix template).

## Plan (written by Opus; ticked by Sonnet)
- [x] Write research plan + prompts (T4M_KE_HOACH_NGHIEN_CUU.md)
- [ ] GĐ0: Truong emails IT / ECA teacher, tries make.powerapps.com (NC-02)
- [x] GĐ1: run prompt P1 (Opus, network) -> T4M_KET_QUA_TAI_LIEU.md (05/11/2026, done in this session)
- [ ] GĐ2: Truong interviews IT + ECA teacher (plan §6), gets anonymised export sample
- [ ] GĐ3: prompt P3 (Sonnet) -> T4M_HUONG_DAN_THU.md; Truong runs sandbox tests (only if NC-02 allows)
- [x] Before GĐ4: P4 kiosk import contract -> §3 of T4M_KET_QUA_TAI_LIEU.md
- [ ] GĐ4: prompt P2 (Opus) -> T4M_MICROSOFT.md + proposed item codes; Truong approves

## Current state (overwrite each handoff)
- Done: plan + prompts; CLAUDE.md slimmed to English (Z-CLAUDE-GON, Truong approved); GĐ1 + P4 results in
  `docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md`; T4-K2 marked PAUSED in TIEN_DO (Truong decided 05/11/2026).
- In progress: none. Waiting on GĐ2 (Truong interviews IT; questions = plan §6 + results §4).
- Tests: docs only; kiem_nhanh.py before push.
- Open problems: no sandbox likely (Developer Plan ends 15/11/2026) -> plan fallback B; PowerSchool->M365 path unknown.

## Decisions and gotchas (keep short)
- Japanese club = multi-day bundle (e.g. 3A Mon+Wed+Thu), level assigned by school (eligibility, not priority),
  committed for the whole year. Bundles break day-independence (KE_HOACH_NHIEU_BUOI.md §2). Proposed: two phases
  (bundles first, max one bundle per student; then per-day), guarantees only within each phase; must be labelled
  "không bảo đảm ổn định toàn tuần khi có gói" (invariant 8). Year-committed seats reduce quota only (invariant 2 safe).
- No scores at this school: everyone is Tầng 2 (STB only). Each campus is allocated separately (one workspace each).
- Never commit real school data, tenantId, app URL or names. Sandbox only; never touch the live app.
- Network was reachable on 05/11/2026 (learn.microsoft.com 302, support.powerschool.com 200), unlike the T4 session.

## Next steps (ordered)
1. Truong: GĐ0/GĐ2 (email + meet IT with plan §6 and results §4 questions; ask for anonymised export sample).
2. If IT grants an environment: prompt P3 (GĐ3). Otherwise fallback B.
3. Prompt P2 (GĐ4) -> T4M_MICROSOFT.md.

## Files touched
- docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md: the plan
- docs/phien/claude__upbeat-shannon-g5nnms.md: this handoff
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: T4M-NC, Z-CLAUDE-GON, T4-K2 paused
- CLAUDE.md, docs/ke_hoach/CLAUDE_CHI_TIET.md: slimmed (Z-CLAUDE-GON)
- docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md: GĐ1 + P4 results

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-05 | Opus | Explained T4; gathered school profile via 28 questions; wrote T4M research plan + prompts P1..P4 | No code changed |
| 2026-11-05 | Opus | Slimmed prompts + CLAUDE.md; ran GĐ1 + P4 (web docs read, kiosk import contract) | Key: DVfT + Developer Plan end 15/11/2026; PowerSchool not an SDS OneRoster provider |
