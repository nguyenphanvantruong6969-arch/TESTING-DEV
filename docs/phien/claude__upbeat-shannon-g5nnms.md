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
- [x] GĐ2 prep: printable interview sheet T4M_PHIEU_PHONG_VAN.md (plan §6 + results §4, blocking Qs first) (Sonnet)
- [ ] GĐ2: Truong interviews IT + ECA teacher (use T4M_PHIEU_PHONG_VAN.md), gets anonymised export sample
- [x] GĐ3 doc: prompt P3 (separate Sonnet SESSION, not a subagent; rule 10) -> T4M_HUONG_DAN_THU.md + fake Lists-export generator in du_lieu_test/ with test.
      Amended by Opus: wide store model (one row per student x day, NV1..NV3), SharePoint List only, two readers
      (Truong if sandbox; IT 1-page variant = fallback B), no row-by-row write-back in V1 (export_theo_lop instead).
- [ ] GĐ3 run: Truong (or IT) runs the sandbox checklist, only if NC-02 allows
- [x] Before GĐ4: P4 kiosk import contract -> §3 of T4M_KET_QUA_TAI_LIEU.md
- [x] Quiz path: prompt P5 (Opus, network) -> T4M_KET_QUA_TAI_LIEU.md §7 + NC-25/26 Qs in interview sheet (05/11)
- [x] T4M-Q1..Q3 (Sonnet, done 05/11/2026; Truong APPROVED 05/11/2026, separate session): quiz-only Forms converter keyed on lowercase Email; quiz-only mode
      in tao_mau_forms.py (≤200 questions, split by day); 1-page teacher note. Spec: results §7.5, §7.7
- [x] T4M-DEMO (Sonnet, done 06/11/2026; Truong APPROVED 06/11/2026): fake quiz-only Forms export generator + one-command demo
      (fake Lists CSV + fake quiz export -> Sổ nhập -> kiosk solve -> per-homeroom Excel) for the ECA meeting
- [ ] AUTO CHAIN (Truong approved 06/11; plan + prompts: docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md):
      [x] S1 T4M-VH (Sonnet, done 06/11)  [x] S2 T4M-GOI-TK (Opus, design only; done 06/11, awaiting Truong D1-D5)  [x] S3 T4M-GD4-V0 (Opus; v0 done 06/11, revisit after GĐ2)  [x] S4 T4M-DO (Sonnet, done 06/11)
      [x] T4M-Q1b (Sonnet, 06/11): --chi-thi converter writes Lớp from Lists into Sổ nhập; set_student_class workaround dropped from demo
      [ ] T4M-Q1b-b (Sonnet, NOT done; outside the Q1b task text): optional --co-so filter (S1 gap) + update T4M_VAN_HANH_MOT_DOT.md steps 4-5
- [ ] GĐ4: prompt P2 (Opus) -> T4M_MICROSOFT.md + proposed item codes; Truong approves

## Current state (overwrite each handoff)
- STATUS T4M-DO: DONE. `du_lieu_test/do_t4m_thi.py` + `tests/test_do_t4m_thi.py` (8 pass; related with test_demo_t4m 19 pass, ruff clean) + `docs/he_sinh_thai/T4M_DO_MO_PHONG.md` + `du_lieu_test/ket_qua_t4m/*.csv`. Full grid 3 sets (120/500/1500 hs) x 20 seeds x 2 conditions = 120 runs, 0 blocking pairs, runtime ~30 s (so `--nhanh` is only a small grid for tests, needs --ra and --tai-lieu). Condition A = same pipeline with scores dropped but applicant lists kept (checked byte-identical to run_pipeline on a DB without club_scores); B = with quiz scores (also byte-identical to run_pipeline). Tables only, no commentary. No product code changed. AI log: the project's AI log is an artifact outside the repo (BAN_GIAO.md §Nhật ký AI) - Truong must add the entry himself/herself.
- STATUS T4M-Q1b: DONE. Converter `doc_lists` reads `Lop`/`Lớp`, `ghi_tep_phan_mem` writes the Lớp column only when some student has one (no column in Lists -> old bytes). Demo workaround removed. Tests: test_t4m_chi_thi + test_demo_t4m + test_mau_forms_thi_clb 65 pass (3 new test_q1b_*), ruff clean, kiem_nhanh 7/7. No schema/CSV contract/core change.
- STATUS T4M-DEMO: DONE. Commit 4c7ad66. Tests: test_demo_t4m 11 pass, related group 69 pass, ruff clean, kiem_nhanh 7/7. No product code, schema or CSV contract changed.
- Done earlier: research plan + prompts; GĐ1 + P4 results; interview sheet; GĐ3 guide + fake Lists generator; P5 quiz path; T4M-Q1..Q3 (quiz-only converter/form generator/teacher note; reviewed by Opus 06/11).
- Done (Sonnet, 06/11/2026): T4M-DEMO, tests first (`tests/test_demo_t4m.py`, 11 tests; related 68 pass, ruff clean).
  `tao_mau_forms.ghi_mau_xuat_chi_thi` (fake quiz-only Forms export, plants: uppercase emails, 1 duplicate, 1 unknown email, 1 test for an unranked club);
  `sinh_xuat_lists_gia.sinh/ghi_csv(clb_theo_ngay=)` (default bytes unchanged); `du_lieu_test/demo_t4m.py --ra DIR [--so-hs 120] [--seed] [--he-so-cho]`; README section 0b.
- Demo facts to confirm with Truong: (1) pipeline needs rules.wharton=False in the TEMP db (default ON, data has no bids); (2) converter does not copy the class column, so demo calls `set_student_class` from the Lists CSV (possible follow-up item: converter writes `Lớp` into the Sổ nhập); (3) sample capacities (~42 seats/day) fit ~50 students, so demo multiplies capacity by an auto factor (~2.0 at 120 students; in-memory copy, `de_thi.json` untouched; `--he-so-cho 1` keeps it). Result at 120 students: ~65% of (student x day) slots get choice 1.
- Done (Opus, 06/11/2026): S2 T4M-GOI-TK -> `docs/he_sinh_thai/T4M_GOI_THIET_KE.md` (design only, no code). Two-phase orchestrator `run_rbda_co_goi` (new file goi_nhieu_buoi.py) above `run_rbda_nhieu_buoi`; bundle = pseudo-session `goi`; level = preference filter; commitments = quota only; phase-2 STB list excludes `goi` (one-day schools stay in short-circuit). Decisions pending Truong: D1 design, D2 CSV contract (optional `goi_buoi` column + optional `04_goi.csv`), D3 schema (`clubs.goi_buoi`, table `goi_dieu_kien`, `match_results` row `(sid, goi, G)`), D4 item codes A8-GOI-1..3, D5 phase-1 STB permutation. Wait for ECA answers Q1-Q3 before coding.
- STATUS T4M-GOI-TK: DONE, commit 34ccd56 (doc docs/he_sinh_thai/T4M_GOI_THIET_KE.md, design only). Truong must approve D1 two-phase design (+ V0 fallback), D2 CSV contract (optional goi_buoi + 04_goi.csv, reserved label goi), D3 schema (clubs.goi_buoi, goi_dieu_kien, match_results row (sid, goi, G)), D4 item codes A8-GOI-1..3 after ECA Q1-Q3, D5 phase-1 STB permutation.
- STATUS T4M-GD4-V0: DONE (commit: see git log "T4M-GD4-V0"). Doc docs/he_sinh_thai/T4M_MICROSOFT.md (v0, fallback A, 9 P2 items + §10 revisit list); docs only, no tests needed, kiem_nhanh run. Pending Truong: S2 D1-D5 (still unapproved, shown as pending in §5/§8), new item codes T4M-M1..M4 (§8), T4-K2 option K2-a/b/c/d (§9). Cites S1 T4M_VAN_HANH_MOT_DOT.md and S4 T4M_DO_MO_PHONG.md tables (both arrived on rebase; no interpretation). Revisit after GĐ2: NC-01 (branch L vs D), NC-02, NC-03, NC-08, NC-16, sample export, NC-10/17, ECA Q1-Q8, NC-25/26.
- Not done: nobody has run the chain against a real Forms or Lists export; push pending after soat-ma.
- Orchestration: root Opus session self-checks ~40 min (send_later), reviews each child, launches next (plan §4).
- Open problems: no sandbox likely (Developer Plan ends 15/11/2026) -> fallback B; PowerSchool->M365 path unknown; bundles (Japanese) need a new item code.

- STATUS T4M-VH: DONE. Doc docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md (99 lines, 8 steps, docs only, untested parts labelled TH/HỎI-IT). Step 5 describes Lớp flowing List -> Sổ nhập (depends on T4M-Q1b); converter does not filter by CoSo (documented as TH). Nothing for Truong to approve.

## Decisions and gotchas (keep short)
- Japanese club = multi-day bundle (e.g. 3A Mon+Wed+Thu), level assigned by school (eligibility, not priority),
  committed for the whole year. Bundles break day-independence (KE_HOACH_NHIEU_BUOI.md §2). Proposed: two phases
  (bundles first, max one bundle per student; then per-day), guarantees only within each phase; must be labelled
  "không bảo đảm ổn định toàn tuần khi có gói" (invariant 8). Year-committed seats reduce quota only (invariant 2 safe).
- DECISION 05/11/2026 (Truong): school changes its process to match RB-DA -> clubs with entrance quizzes use Tầng 1
  (-score then STB), others Tầng 2. Quizzes written by club teachers, built by OUR tooling (Microsoft version of
  tao-google-form-clb / xu-li-raw-forms). CSV contract unchanged (test_club_k, score_k). Plan: NC-23..26, prompt P5.
  Each campus is allocated separately (one workspace each).
- Never commit real school data, tenantId, app URL or names. Sandbox only; never touch the live app.
- GĐ1 findings that drive design (see T4M_KET_QUA_TAI_LIEU.md §0): store = SharePoint List, one row per (student, day)
  (CSV export cap 30,000 rows); Dataverse for Teams + Developer Plan stop new environments 15/11/2026 (ask IT for a
  sandbox/managed dev env); PowerSchool is NOT an SDS OneRoster provider (sync path = HỎI-IT); M365 Power Automate =
  Low profile, 6,000 requests/user/day -> V1 returns results as per-homeroom Excel (`export_theo_lop`), no row-by-row
  write-back; converter = Python on IT machine, lowercase emails (student_id is case-sensitive); Sổ nhập has one Buổi
  per club -> bundles need a new item code.
- Network was reachable on 05/11/2026 (learn.microsoft.com 302, support.powerschool.com 200), unlike the T4 session.

- Finding while writing P3: Power Automate Low profile caps paging at 5,000 items, so a 7,500-row export flow must filter per day (guide §7.1; verify by TH).

## Next steps (ordered)
1. Truong: GĐ0/GĐ2 (email + meet IT; print T4M_PHIEU_PHONG_VAN.md; ask for anonymised export sample).
2. If IT grants an environment: prompt P3 (GĐ3). Otherwise fallback B.
3. Prompt P2 (GĐ4) -> T4M_MICROSOFT.md.

## Files touched
- docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md: the plan
- docs/phien/claude__upbeat-shannon-g5nnms.md: this handoff
- du_lieu_test/demo_t4m.py, du_lieu_test/sinh_xuat_lists_gia.py, mau_forms_thi_clb/{tao_mau_forms.py,README.md}, tests/test_demo_t4m.py: T4M-DEMO
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: T4M-NC, Z-CLAUDE-GON, T4-K2 paused
- CLAUDE.md, docs/ke_hoach/CLAUDE_CHI_TIET.md: slimmed (Z-CLAUDE-GON)
- docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md: GĐ1 + P4 results
- docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md: GĐ2 interview sheet
- docs/he_sinh_thai/T4M_HUONG_DAN_THU.md, du_lieu_test/sinh_xuat_lists_gia.py, tests/test_sinh_xuat_lists_gia.py: GĐ3 doc
- mau_forms_thi_clb/{chuyen_forms_sang_phan_mem,bieu_mau,tao_mau_forms}.py, GHI_CHU_GIAO_VIEN.md, CAI_DAT_FORMS_CHI_THI.md, NHAP_FORMS_CHI_THI.docx, README.md; tests/test_t4m_chi_thi.py: T4M-Q1..Q3
- du_lieu_test/do_t4m_thi.py, du_lieu_test/ket_qua_t4m/, tests/test_do_t4m_thi.py, docs/he_sinh_thai/T4M_DO_MO_PHONG.md: T4M-DO

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-05 | Opus | Explained T4; gathered school profile via 28 questions; wrote T4M research plan + prompts P1..P4 | No code changed |
| 2026-11-05 | Opus | Slimmed prompts + CLAUDE.md; ran GĐ1 + P4 (web docs read, kiosk import contract) | Key: DVfT + Developer Plan end 15/11/2026; PowerSchool not an SDS OneRoster provider |
| 2026-11-05 | Opus | Handoff at ~400k context (Stop hook); no new work | Next: Truong GĐ2 with IT |
| 2026-11-05 | Opus+Sonnet | GĐ2 interview sheet written (by a subagent: rule 10 breach, Truong flagged it; reviewed by Opus); P3 subagent stopped, partial file deleted; P3 moved to a new Sonnet session | Never use Agent tool; open sessions |
| 2026-11-05 | Sonnet | GĐ3 doc (P3 amended): guide, fake Lists-export generator, test first (7 red -> green) | No subagent; ruff clean on new files |
| 2026-11-05 | Opus | Truong decided: school adopts RB-DA with entrance quizzes (Tầng 1); added NC-23..26 + prompt P5 | Sonnet P3 session told |
| 2026-11-05 | Opus | P5 research (Forms Quiz, Graph, Quick Import, Power Apps quiz); found mau_forms_thi_clb already covers Forms quiz; results §7; interview sheet +4 Qs | Proposed T4M-Q1..Q3 |
| 2026-11-05 | Opus | Truong approved T4M-Q1..Q3; opened Sonnet session for them | Order Q1 -> Q2 -> Q3 |
| 2026-11-05 | Sonnet | T4M-Q1..Q3 done: quiz-only converter, quiz-only form generator, teacher note; tests first (27), mutation check found missing 200-boundary case, fixed | No subagent; default mode unchanged; kiem_nhanh 7/7 |
| 2026-11-06 | Opus | Reviewed T4M-Q1..Q3 (58 related tests pass, ruff clean, default output identical except docx/xlsx core.xml timestamp); Truong approved T4M-DEMO, Sonnet session opened | |
| 2026-11-06 | Sonnet | T4M-DEMO done: fake quiz-only Forms generator, `demo_t4m.py` one-command chain, README 0b; tests first (11), mutation check found 1 weak test (uppercase emails), fixed | No subagent; no product code, schema or CSV contract changed |
| 2026-11-06 | Opus | Truong approved auto chain (bundle design only, GĐ4 v0, auto-run, simulation tables only); wrote T4M_KE_HOACH_TU_DONG.md | S2 launched |
| 2026-11-06 | Opus | S2 T4M-GOI-TK: bundle design doc (two-phase orchestrator, invariants 1/2/3/4/5/8, week-level counter-example, CSV/schema proposal, A8-GOI-1..3 kiem_nhan, ECA questions) | Design only; no code; 5 decisions for Truong |
| 2026-11-06 | Opus | Reviewed S0 T4M-DEMO (69 tests pass, demo runs, 3 seeded warnings) and S2 (OK); found Lớp gap -> T4M-Q1b; launched S1, S3, S4, Q1b | S2 D1-D5 await Truong |
| 2026-11-06 | Sonnet | S1 T4M-VH done: one-round operations guide for school IT (8 steps) | Docs only; no subagent; Lớp described as flowing into Sổ nhập (Q1b) |
| 2026-11-06 | Opus | Reviewed S1 T4M-VH (OK); added --co-so filter to Q1b scope | |
| 2026-11-06 | Sonnet | T4M-Q1b: tests first (1 red), converter carries Lớp from Lists into Sổ nhập, demo workaround removed; one old test's expectation updated (test Lists has class 9A1) | No subagent; default mode unchanged |
| 2026-11-06 | Sonnet | S4 T4M-DO: simulation grid script, tables, tests first; mutation check caught condition A dropping applicant lists (results no longer depended on seed) | No subagent; no product code changed; tables only |
| 2026-11-06 | Opus | S3 T4M-GD4-V0: draft v0 T4M_MICROSOFT.md (P2 under fallback A; two store branches; matrix filled; item codes T4M-M1..M4; T4-K2 options only) | Docs only; D1-D5 still pending Truong |
