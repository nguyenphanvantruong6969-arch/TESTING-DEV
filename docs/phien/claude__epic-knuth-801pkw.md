# Branch handoff: claude/epic-knuth-801pkw

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
Follow-up to A14 (student class). Branch starts from `claude/a14-giao-dien` (fast-forwarded, includes
A14 part A + B). Truong's task file (2026-11-03), explicitly overriding the registry rule (rule 1):
- T1a: static sample `mau_csv/SO_NHAP_CLB.xlsx` has no "Lớp" column (software-generated sample has it).
  Add it and make that file the main sample.
- T1b: an old workspace whose saved config already has two nouns with the same label opens fine, but
  ANY later save (rename workspace, change a rule) is rejected with `nhan_trung_danh_tu` until labels
  are fixed. Fix that. No over-engineering.
- T2: merge sidebar tabs 02 (Kết quả), 06 (Thành viên CLB), 07 (Theo lớp) into TWO tabs:
  "Kết quả" (per-student timetable, members per club, members per class) and "Dữ liệu khác"
  (everything else that was in 02). Kết quả has two tiers (see Plan T2).
- T3 (later loop): UI debloat research, output one .md. T4 (later loop): data-collection ecosystem
  model (flowcharts/architecture images) for Truong to approve BEFORE any implementation.
Algorithm, match_results, run_history, CSV column contract: untouched.

## Plan (written by Opus; ticked by Sonnet)
- [x] T1a sample Sổ with Lớp column, main sample (CON-1)
- [x] T1b old duplicate labels do not block unrelated saves (CON-1)
- [x] T2 tabs 02/06/07 merged into Kết quả (two tiers) + Dữ liệu khác (CON-1); full suite green at cebfa2c (3299 passed)
- [x] T3 debloat study docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md (CON-3, tester NO BUGS at 0d28de0)
- [x] T4-K3 skill reads multi-part CSV folder (7e64cc4, done by another session)
- [x] T4-K1 optional `lop` column (CON-5, fff0f41 + fix 85d22ce, tester NO BUGS)
- [ ] T4 design review round 5 (gate for K2): tester CON-6 reviewing commit 00372e0
- [ ] T4-K2 Apps Script (xuLyLo, caiLaiTrigger, 15 menus, export in parts) by CON-5 after "GO K2"
- [x] Merge main (aac38df), recount 181 files / 3.360 cases, PR opened: nguyenphanvantruong6969-arch/TESTING-DEV#8
- [ ] Full suite after merge (was running in Opus session) + CI green on PR #8; then T4-K2 as a follow-up

## Current state (overwrite each handoff)
- Coordinator = Opus session session_01VfPzNvdGizkwxJ8cd64rmp (handing off now, context > 400k).
- Child sessions (claude-code-remote, send_message to talk):
  - CON-5 implementer session_01VfPzNtNTCRyPE34MDFqofZ: K1 done; WAITING for "GO K2" (its first prompt holds Truong's K2 spec).
  - CON-6 tester session_01VfPzNsx2G7ePNkQy3Eg5A5: running JOB E = T4 design round 5 review of 00372e0; will report
    "TESTER REPORT T4 round 5" to the OLD coordinator id. New coordinator: read it with list_events on that session.
  - CON-7 design writer session_01VfPzNskNGxNkQtb4CTcC1X: did design round 4 (00372e0); use it for design fixes.
  - CON-4, CON-2, CON-1, CON-3: retired (context full or done).
- Design status (00372e0): §7.7 holds implementation conventions M1..M26 + N1..N15 decisions. Simulation: at c=100 ms per
  response both targets FAIL (backlog drain 140 min > 2 h; peak day 64.3 min > 45); both hold when c <= ~64 ms; the doc says so
  and gives the pilot decision rule (<=64 keep A; 64-200 mitigations §9.4; >200 option B).
- ROUND 5 RESULT (arrived after handoff, 07:19): CON-6 verified N1..N15 and reproduced the simulation (matches; peak-day
  totals off by 0.1-0.3 min rounding). NOT passed only because of 5 blocking ambiguities, one line each needed in §7.7:
  B1 Từ chối: which states it applies to, ban_giu after, which rows are candidates for re-rank (suggest: any state; ban_giu 0;
  candidates = valid ma_hs rows not tu_choi). B2 normal-batch red alert (suggest: red if RAW < valid phieu, or RAW > phieu after a
  batch that ended "no more responses"). B3 runtime c for the stop rule (suggest: measured from the previous block, default
  100 ms stored in cau_hinh). B4 Gán lại mã: new code must exist in hoc_sinh (refuse otherwise); M9 normalisation on both sides.
  B5 swap-kept-row write order (suggest: demote old row first, then promote; batch start repairs groups with 0 or >1 ban_giu=1
  by M11). Non-blocking: §7.7 intro says round 3; §9.3 totals rounding; ketThucLo re-arms forever if RAW has hand-typed rows
  (say so); API < phieu has no exit (say "Từ chối that row" or V1 unsupported); no cau_hinh key for last API count.

- PR #8 (claude/epic-knuth-801pkw -> main) opened 2026-11-04 WITHOUT T4-K2. Merge resolution: kept branch T1b
  (all pairs, per language) + main's C1 rule (changing a duplicate pair to another shared label = new pair, key includes
  label casefold); tests/test_a14_sua_sau_soat.py taken from main; mau_csv/tao_so_nhap.py = main's + cfg=chuan_hoa({});
  SO_NHAP_CLB.xlsx regenerated. 241 related tests green after merge; full suite result not yet read.

## Decisions and gotchas (keep short)
- Truong approved T4-K1/K2 (TIEN_DO 3e9b0bc). K2 starts only after the design review passes (Truong's order).
- Deviations from Truong's original K2 wording, to report to him: Từ chối sets ban_giu=0 and re-ranks (M5); a second full export
  the same day is allowed if phieu changed (phieu_phien_ban, M20); Chốt đợt does not auto-export; 15 menus incl. "Huỷ xuất";
  no ma_hs format check (membership only, N13); chốt requires API count = valid phieu, RAW mismatch only warns (N4).
- Product bugs found by T3 (NOT fixed, ask Truong): B1 saving a club with blank optional fields wipes reserve seats, priority
  group and session (js/05_quan_ly.js sends all 6 fields); B2 Run on an empty workspace locks seed 42; B3 no way to turn off
  Điểm quyết tâm after creation.
- Network blocks Google/Microsoft/Supabase docs and the teacher's netlify page: quotas stay TT-CXM; doc §16 lists what to verify.
- Local test env: python3 -m venv .venv; pip install -r requirements-dev.txt; pip install playwright==1.63.0 (matches
  /opt/pw-browsers); run with PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; full suite ~23 min.

## Next steps (ordered)
0. Check PR #8 CI (subscribe_pr_activity in the new session) and fix failures; run full suite locally if needed.
1. Decide B1-B5 (see Current state), send to CON-7 to write into §7.7 (+ non-blocking items), then CON-6 quick re-check.
2. When it passes: send "GO K2" to CON-5 with: follow §7.7 + N decisions at the latest design commit; list deviations.
3. CON-5 reports "CON-5 K2 DONE" -> CON-6 reviews code -> loop until NO BUGS. Report to Truong: files, new tests (cases),
   soat-ma, uncertain points.
4. (DONE except CI) PR: merge origin/main into the branch; conflicts in workspace.py, cau_hinh_ws.py, docs/ke_hoach/CLAUDE_CHI_TIET.md (T1/T2);
   tests/test_a14_sua_sau_soat.py::test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien take main's version (B9, no DROP
   COLUMN); recount test files and cases (collect-only; K1 wrote 3.319 uncounted). Full suite, soat-ma, push, open PR to main,
   subscribe_pr_activity, fix CI until green.
5. Ask Truong whether to fix product bugs B1-B3.

## Files touched
- T1/T2: cau_hinh_ws.py, workspace.py, api_workspace.py, so_nhap.py, mau_csv/*, index.html, style.css, i18n.js, i18n_errors.py,
  i18n_loi.js, js/01,03,04,05,06,075,07,08,09, README/HUONG_DAN_*, tests (see CHANGELOG T1a/T1b/T2 and rounds).
- T3: docs/nghien_cuu/. T4 design: docs/he_sinh_thai/. K1: lop_hoc_sinh.py (new), rbda_priority_pipeline.py (re-import),
  .claude/skills/xu-li-raw-forms/*, mau_forms_thi_clb/{tao_google_forms.py,TAO_GOOGLE_FORM.gs,DINH_DANG_RAW.md,dong_goi_skill.py},
  tests/test_t4_k1_lop.py, tests/test_a14_lop_backend.py, tests/test_a14_tu_vung_cohort.py.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-03 | Opus | ff to a14-giao-dien, wrote plan for T1/T2 | coordinator session |
| 2026-11-03 | Sonnet | T1a, T1b, T2 implemented, tests green, pushed | static sample is a blank template (only Lớp column added); day sort = earliest session with a club |
| 2026-11-03 | Sonnet | Fix round 1 (F1-F8) from Opus plan | see CHANGELOG "T1/T2 sửa vòng 1" |
| 2026-11-03 | Sonnet | Fix round 2 (G1-G3) from Opus plan | see CHANGELOG "T2 sửa vòng 2" |
| 2026-11-03 | Sonnet | Fix round 3 (snapshot of Sổ guide text) | only Hướng dẫn A1,A16,A18,A23,A33 differed |
| 2026-11-03 | Sonnet | Handoff at context limit, round 3 committed | tests still pending, report to Opus not sent |
| 2026-11-03 | Sonnet | Final handoff: rounds 1-3 done and reported | nothing pending on this side |
| 2026-11-04 | Sonnet | CON-4: T4 design doc and 5 diagrams, rounds 1, 2, 3b pushed (ca9e161); handoff at context limit | design only; quotas unverified (network blocked); waiting for Opus review |
| 2026-11-04 | Opus | Coordinated T3 (closed), T4 design rounds 1-4, T4-K1 (closed); handoff at context limit | K2 waits on design round 5 (CON-6) |
| 2026-11-04 | Opus | Merged main, resolved 7 conflicts, opened PR #8 (no K2) | full suite + CI pending at handoff |
