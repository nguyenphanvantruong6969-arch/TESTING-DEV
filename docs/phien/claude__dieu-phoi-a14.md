# Branch handoff: claude/dieu-phoi-a14

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> This branch holds ONLY this handoff file. It is the coordinator (Opus) session for item A14; it wrote no product code.

## Feature / goal
A14 "class per student" (Lớp): each student has `students.class_id` used ONLY for display / sort / filter / export to homeroom teachers (GVCN); the allocation never reads it. Opus coordinated two parallel Sonnet sessions (A = base + import + API, B = export + UI + view tabs 06/07), cross-review, fix rounds and final verification.

## Plan (all done)
- [x] Clarify spec with Truong (decisions below) and write prompts for sessions A and B
- [x] A: schema/migration, `chuan_hoa_lop`, vocabulary noun `cohort`, Sổ/CSV import, admin/kiosk/results APIs
- [x] B: "Theo lớp" sheet, `export_theo_lop`, Lớp column in exports, UI (Quản lý, Kết quả, kiosk, workspace), tabs 06 "Thành viên CLB" + 07 "Theo lớp"
- [x] Cross-review (A reviews B, B reviews A) with soat-ma; fix rounds A1–A6, B1–B9, C1–C2
- [x] Coordinator ran the FULL suite on the final commit: 3314 passed, 1 skipped (root-only env skip)
- [x] PR #6 (claude/a14-giao-dien -> main) CI green on 353d1c4; merged by Truong as b044c4c (2026-11-03)
- [x] PR #7 (claude/a14-chot-tai-lieu -> main): docs-only closing (TIEN_DO A14 = xong, handoff files, CHANGELOG); CI green on 804d205

## Current state (overwrite each handoff)
- Done: A14 code is on main (b044c4c). PR #7 is OPEN, CI green (ruff, Linux full + real UI, Windows), mergeable clean, no reviews. Waiting only for Truong to review/merge.
- In progress: nothing. Sessions A (session_01VfPzNra1AUNjuEtEybZqXm) and B (session_01VfPzNuqgL1PDRUBydGUj7d) are idle; no pending work for them.
- Watching: the old coordinator session was subscribed to PR #7 and had a one-shot check-in scheduled (trigger trig_01JSWreCPpEtJc4XUNckceGb, ~05:49Z 2026-11-04). A new session should re-subscribe to PR #7 if Truong wants it watched (subscribe_pr_activity owner nguyenphanvantruong6969-arch repo testing-dev pullNumber 7).
- Tests: nothing to run for this branch (docs only).

## Decisions and gotchas (keep short)
- Truong-approved exceptions: optional input CSV column `class_id` (invariant 7, 2026-11-02); "Theo lớp" sheet + Lớp column ALWAYS present in result exports even with no classes (2026-11-02); static sample Sổ files in mau_csv/ carry SIMULATED classes (2026-11-03, script du_lieu_test/them_lop_vao_mau.py, bo_sach untouched).
- Class normalisation: NFC, drop Cf/Cc, trim, collapse spaces, UPPERCASE, max 50 chars (import truncates + warns, API rejects).
- Two nouns with the same label are rejected on save; an already-stored duplicate config can be re-saved unchanged (C1).
- Kiosk class dropdown = classes already in DB; hidden when none; required when any exist.
- Grep-chosen test lists missed files twice: always run the FULL suite before a PR (rule 2 asks Truong first; he asked for it here).
- SQLite on CI is older: `ALTER TABLE ... DROP COLUMN` on tables with `--` comments failed there (fixed in test A5 by CREATE TABLE).
- Never force-push: the permission classifier blocks it; use a new branch instead.
- Do not push handoff/coordination files directly to main; this file lives on its own branch (no PR needed).

## Next steps (ordered)
1. Truong reviews/merges PR #7. If CI or a review needs work, fix within docs scope.
2. Later items (not started, need registry codes): Google Form asks for class; skill xu-li-raw-forms carries Lớp to Sổ; skill sinh-du-lieu-clb simulated class option.
3. Small risk: tests/test_a14_sua_sau_soat.py (`_csdl_cu_co_du_lieu`) and tests/test_a14_tu_vung_cohort.py still build old DBs with DROP COLUMN; green on CI now, may break on an older SQLite.
4. Wrong `Claude-Session:` trailer in some of B's old commits: left as is (already on main).

## Files touched
- docs/phien/claude__dieu-phoi-a14.md: this handoff (coordinator wrote no other files)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-02..04 | Opus | Coordinated A14: spec Q&A, prompts, parallel sessions A/B, cross-review, fix rounds, full-suite verification, PR #6 merged, PR #7 opened and green | handoff at ~400k tokens |
