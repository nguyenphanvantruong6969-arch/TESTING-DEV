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
- [ ] GĐ1: run prompt P1 (Opus, network) -> T4M_KET_QUA_TAI_LIEU.md
- [ ] GĐ2: Truong interviews IT + ECA teacher (plan §6), gets anonymised export sample
- [ ] GĐ3: prompt P3 (Sonnet) -> T4M_HUONG_DAN_THU.md; Truong runs sandbox tests (only if NC-02 allows)
- [ ] Before GĐ4: prompt P4 (Haiku, read-only) -> kiosk import contract summary in chat
- [ ] GĐ4: prompt P2 (Opus) -> T4M_MICROSOFT.md + proposed item codes; Truong approves

## Current state (overwrite each handoff)
- Done so far: research plan and prompts written; nothing researched yet.
- In progress: none.
- Tests: docs only; run `python .claude/skills/soat-ma/scripts/kiem_nhanh.py` before push.
- Open problems: T4-K2 (Google Apps Script) is NOT formally paused yet; Truong has not approved (a) writing
  T4M_MICROSOFT.md / pausing K2 in TIEN_DO, (b) a new item code for the "bundle" phase, (c) item code for the
  Power Apps -> Sổ nhập adapter. Ask before doing any of these beyond what the plan's prompts say.

## Decisions and gotchas (keep short)
- Japanese club = multi-day bundle (e.g. 3A Mon+Wed+Thu), level assigned by school (eligibility, not priority),
  committed for the whole year. Bundles break day-independence (KE_HOACH_NHIEU_BUOI.md §2). Proposed: two phases
  (bundles first, max one bundle per student; then per-day), guarantees only within each phase; must be labelled
  "không bảo đảm ổn định toàn tuần khi có gói" (invariant 8). Year-committed seats reduce quota only (invariant 2 safe).
- No scores at this school: everyone is Tầng 2 (STB only). Each campus is allocated separately (one workspace each).
- Never commit real school data, tenantId, app URL or names. Sandbox only; never touch the live app.
- Network was reachable on 05/11/2026 (learn.microsoft.com 302, support.powerschool.com 200), unlike the T4 session.

## Next steps (ordered)
1. Truong: GĐ0 (email IT with plan §6 questions; try make.powerapps.com).
2. Run prompt P1 in a new Opus session.

## Files touched
- docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md: the plan
- docs/phien/claude__upbeat-shannon-g5nnms.md: this handoff
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: T4M-NC entry

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-05 | Opus | Explained T4; gathered school profile via 28 questions; wrote T4M research plan + prompts P1..P4 | No code changed |
