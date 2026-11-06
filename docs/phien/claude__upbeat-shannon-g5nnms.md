# Branch handoff: claude/upbeat-shannon-g5nnms

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).

## Feature / goal
T4M-NC (outside the 33-item registry; Truong asked 05/11/2026): fit RB-DA into the school's EXISTING Microsoft
ecosystem (Power Apps "ECA Registration HVT", M365 A3/A5, PowerSchool sync, IT runs the kiosk). Truong decided the
school adopts RB-DA incl. entrance quizzes (Tầng 1) built by our tooling on Microsoft Forms.
Plans: `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (research, NC-01..27, prompts P1..P5),
`docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md` (auto chain: §5 round 1, §6 round 2, §7 round 3, with prompts and rules).

## Plan (written by Opus; ticked by Sonnet)
- [x] Research plan; GĐ1 docs (P1); P4 kiosk contract; P5 quiz path; GĐ2 interview sheet; GĐ3 sandbox guide
- [x] T4M-Q1..Q3, Q1b, Q1b-b (quiz-only Forms, Email key, Lớp, --co-so); T4M-DEMO; Round 1 S1-S4; Round 2 R1-R3
- [x] ROUND 3 quiz portal (plan §7; Truong approved 06/11; score level 5a; Opus reviewed 06/11):
      [x] C1 T4M-Q4a/b/c (Sonnet, session_01YVAyu2ANfZCsBcACp7Az4F, DONE 06/11)
      [x] C2 T4M-M5 (Sonnet, session_01YVAytz83xzruFD2dhwkPzs, DONE 06/11)
- [x] ROUND 4 (plan §8; Truong decided 06/11: up to 7 NV/day, tick to sit tests max 5/day, determination
      points collected in app = option b; no core change):
      [x] D1 T4M-Q5a/b/c converter THIk/WPk + fake data + demo --day-du (Sonnet) DONE 7e274d4; Opus reviewed OK (fixed HDT note that broke an old test)
      [x] D2 T4M-M6 docs: app spec Top 7, tick, determination-point screen; interview sheet (Sonnet) DONE 7e31127; Opus reviewed OK (fixed R37 wording)
      [x] Opus: review D1/D2, then update the simulation artifact https://claude.ai/artifact/B9jnsdzuN57KNuhPUBMUCd
- [ ] GĐ0/GĐ2: Truong meets IT + ECA teacher (before 15/11/2026), gets anonymised export sample
- [ ] GĐ3 run: sandbox checklist (only if NC-02 allows)
- [ ] GĐ4 final: update T4M_MICROSOFT.md v0 -> v1 after GĐ2 (its §10 lists what to revisit)
- [ ] A8-GOI-1..3 (bundle code): D1-D5 approved in principle; code ONLY after ECA answers Q1-Q3
- [ ] T4M-M2 (column-mapping file): waits for a real anonymised export
- [ ] Proposed, not approved: PR to main for full CI + Windows build; skill T4M-SK; registry chain Z6 (new branch)

## Current state (overwrite each handoff)
- Rounds 1-4 DONE and reviewed by Opus 06/11/2026. Nothing is running; no child sessions; check-in trigger deleted.
- Round 4 (plan §8): Truong decided up to 7 NV/day, tick to sit tests (max 5/day), determination points collected in
  the app (option b). Origin: Opus's earlier Top 3 recommendation silently cut core limits (10 NV, 5 tests) and the
  T4M path had no determination points (demo turned wharton OFF silently). No core/schema/CSV change was needed.
  D1 T4M-Q5a/b/c (7e274d4): converter reads THIk/WPk, fake Lists --so-nv/--tick/--wp, demo --day-du (wharton ON,
  planted bad fund blocked by kiosk then fixed); tests/test_t4m_day_du.py 34 tests. D2 T4M-M6 (7e31127): app spec
  R25..R38, HDT §14 rows 14.x, interview ECA-6/9/12, IT-19. Opus review: demo default and --moi-clb outputs
  identical before/after D1; fixed R37 wording (legit "vắng thi" warnings) and HDT note (dropped `NV3` broke
  test_sinh_xuat_lists_gia). Related tests 173 pass, ruff clean, kiem_nhanh 7/7.
- Simulation artifact (interactive, 7 stages, fake data; shared "Anyone with the link" by Truong):
  https://claude.ai/artifact/B9jnsdzuN57KNuhPUBMUCd (v4). Source is NOT in the repo (scratchpad only); it adds
  invented clubs marked "*" so 7 slots and the cap of 5 are visible (sample de_thi.json has 3 clubs/day).
- Minor notes, not fixed: tao_mau_forms.py default mode ignores --ra (pre-existing); --bai-thi ClubId compare is
  case-sensitive; converter warnings over many files give row number but not file name (pre-existing).
- kiem_nhanh needs `git fetch origin main:refs/remotes/origin/main` first, else trung_khit fails.
- Container: pip install pytest openpyxl python-docx if missing (ruff is present).
- Still for Truong: AI-log entry for T4M-DO (log is outside the repo).

## Decisions and gotchas (keep short)
- Never commit real school data, tenantId, app URL or names. Sandbox/copy only; never touch the live app.
- No subagents (rule 10): every step is a SEPARATE session (create_session), reporting DONE/BLOCKED (plan §3).
- Store = SharePoint List, wide model (one row per student x day, NV1..NV7 + THI1..THI7 + WP1..WP7, round 4); CSV export cap 30,000 rows.
  Dataverse for Teams + Developer Plan stop creating environments 15/11/2026. PowerSchool is not an SDS OneRoster
  provider (sync path HỎI-IT). Power Automate Low profile: 6,000 requests/user/day; no row-by-row write-back in V1.
- Quiz: Microsoft Forms Quiz (no supported API creates forms; Quick Import does not carry answers; Forms connector is
  read-only, not in Power Apps, and per community does not return quiz points). Official scores = converter
  re-grades from de_thi.json. Score level 5a: teachers "Post scores" in Forms; app shows no score.
- Quiz portal (T4M_CONG_THI.md): app = portal, one Form per club, list CLB(FormUrl) + BaiThi(status), one small
  standard flow per form writes "Đã làm"; request estimate ~9,000 per round vs 6,000/day (peak-day risk).
- Bundles (T4M_GOI_THIET_KE.md): two-phase orchestrator above the pipeline, label "bảo đảm trong từng pha, không bảo
  đảm ổn định toàn tuần khi có gói" (inv. 8); no bundles => byte-identical (inv. 1); D2/D3 add OPTIONAL CSV/schema.
- Round 4 rules: tick only on clubs with de_thi; ticked+no submission -> "thi" (absent); submission without tick ->
  dropped+warned; >5 ticks keep first 5 by NV order; fund 1 = ticked clubs, fund 2 = rest, each non-empty = 100
  (converter warns, kiosk blocks); single-club blank fund auto-filled 100 by kiosk (tu_dien_wharton_mot_clb).
- T4-K2 (Google) = K2-b, stays paused (Truong 06/11/2026).
- Review lessons: children once committed conflict markers into this file; S4 miscounted quiz clubs (15 vs 10);
  R2 diff tool had a false "no change" with unknown club codes (fixed: raw compare + warning headline).

## Next steps (ordered)
1. Ask Truong: open a PR to main for full CI + Windows build (recommended next; Truong has not answered yet).
2. Truong said "I want to recreate something like that" (the simulation page). Opus asked, unanswered: (a) learn to
   build it himself (tutor mode, hints first), (b) a similar page for another sector, or (c) use it in the project
   report (Truong writes all commentary). Also asked whether to copy the page source into the repo: it exists only in
   the old session scratchpad; if lost, read it back with the Artifact tool (action read) from the URL above.
3. After Truong's GĐ2 meeting (before 15/11): paste anonymised summary -> GĐ4 v1, decide M2, start A8-GOI if ECA
   answered Q1-Q3; ECA-6 (clubs per day) decides whether 7 slots matter.

## Files touched (T4M, this branch)
- mau_forms_thi_clb/{bieu_mau,tao_mau_forms,chuyen_forms_sang_phan_mem}.py, README.md, tests/test_t4m_cong_thi.py, T4M_VAN_HANH_MOT_DOT.md: T4M-Q4a/b/c
- docs/he_sinh_thai/: T4M_KE_HOACH_NGHIEN_CUU, T4M_KET_QUA_TAI_LIEU, T4M_PHIEU_PHONG_VAN, T4M_HUONG_DAN_THU,
  T4M_KE_HOACH_TU_DONG, T4M_GOI_THIET_KE, T4M_MICROSOFT (v0), T4M_VAN_HANH_MOT_DOT, T4M_DO_MO_PHONG,
  T4M_DAC_TA_SUA_APP (+§10 M5), T4M_HUONG_DAN_THU (+§13), T4M_FLOW_GUI_GVCN, T4M_CONG_THI, T4M_FLOW_DA_LAM (.md)
- mau_forms_thi_clb/: chuyen_forms_sang_phan_mem.py, bieu_mau.py, tao_mau_forms.py, doi_chieu_lists.py, README.md,
  GHI_CHU_GIAO_VIEN.md, CAI_DAT_FORMS_CHI_THI.md, NHAP_FORMS_CHI_THI.docx
- du_lieu_test/: sinh_xuat_lists_gia.py (+--so-nv/--tick/--wp), demo_t4m.py (+--moi-clb, --day-du), do_t4m_thi.py, ket_qua_t4m/
- tests/: test_t4m_day_du (round 4), test_sinh_xuat_lists_gia, test_t4m_chi_thi, test_demo_t4m, test_do_t4m_thi, test_doi_chieu_lists (.py)
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, CLAUDE.md + docs/ke_hoach/CLAUDE_CHI_TIET.md (Z-CLAUDE-GON)

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
| 2026-11-06 | Sonnet | T4M-Q1b-b (orchestrator addition): --co-so filter, tests first (4 red -> green), ops guide steps 4-5 | No subagent; default unchanged |
| 2026-11-06 | Opus | Reviewed Q1b (OK, test expectation change justified), S3 (OK, cites DO sections not numbers); S4 sent back: table 2 says 15 clubs with tests, de_thi.json has 10 | Waiting S4 fix, Q1b-b |
| 2026-11-06 | Sonnet | T4M-DO review fix: table 2 exam-club count 15 -> 10, method wording, test that B is Tier 1 for exactly the clubs with de_thi, grid rerun | Numbers in tables 3+ unchanged except seconds |
| 2026-11-06 | Opus | Reviewed S4 fix (OK) and Q1b-b (OK); chain finished; cancelled check-in; asked Truong pending decisions | |
| 2026-11-06 | Opus | Truong decided D1-D5 (principle), M1/M3/M4, K2-b, round 2; wrote plan §6; launched R1-R3 | |
| 2026-11-06 | Sonnet | T4M-M1 (R1): app-edit spec for Top 3 per day, 14 requirements with pass/fail checks | Docs only; no subagent; no product code |
| 2026-11-06 | Sonnet | T4M-M4 (R3): flow guide for sending per-homeroom Excel to homeroom teachers; docs only | No subagent; no code changed |
| 2026-11-06 | Opus | Reviewed R1 T4M-M1 (OK); added HDT §9 rows 5.5 (bilingual) and 5.6 (restore) for R10/R12 | |
| 2026-11-06 | Opus | Reviewed R3 T4M-M4 (OK; fixed DLP reference NC-16 -> NC-14) | Waiting R2 |
| 2026-11-06 | Sonnet | T4M-M3 (R2): `doi_chieu_lists.py` list-export diff tool, tests first (17), ops guide step 8 | No subagent; kiosk untouched |
| 2026-11-06 | Sonnet | T4M-M3 review fix: raw NV comparison + unknown-code warning headline, tests first (6 red -> green) | Orchestrator false negative reproduced and fixed |
| 2026-11-06 | Opus | Reviewed R2 fix (raw NV compare, warning headline; my false-negative scenario now caught); round 2 finished; 109 related tests pass, ruff clean, kiem_nhanh 7/7 | Next needs Truong: GĐ2 interviews |
| 2026-11-06 | Opus | Truong asked for a quiz portal loop; designed T4M_CONG_THI.md (app as portal, one Form per club, BaiThi status list via standard flow, score via converter); proposed Q4a-c, M5 | Awaiting Truong approval |
| 2026-11-06 | Opus | Truong approved Q4a-c + M5, score level 5a; wrote plan §7; launched C1, C2 | |
| 2026-11-06 | Opus | Handoff at ~400k context: rewrote state/next/decisions; round 3 C1, C2 still running; fallback trigger deleted | New root must poll C1/C2 (they message the old session) |
| 2026-11-06 | Sonnet | T4M-M5 (C2): Thi tuyển screen spec (§10, R15..R24) + "Đã làm" flow guide; docs only | No subagent; C1 files untouched |
| 2026-11-06 | Opus | Second handoff note: C2 reported DONE (unreviewed); C1 running | No new work started |
| 2026-11-06 | Sonnet | T4M-Q4a/b/c (C1): `--moi-clb` generator, one-club-per-export converter, `--bai-thi` report; tests first (24) | No subagent; default and --chi-thi unchanged |
| 2026-11-06 | Opus | Third handoff note: C1 also reported DONE (unreviewed) | Round 3 needs Opus review only |
| 2026-11-06 | Opus | Reviewed round 3 (C1, C2): 134 tests, kiem_nhanh 7/7, outputs identical; added 1 test (mutation survivor), HDT §13 rows 13.1-13.4 (C2 numbering clash); round 3 ticked | Next: Truong decides PR to main |
| 2026-11-06 | Opus | Truong chose cách B; T4M-DEMO-B: demo --moi-clb (tests first, 4 red -> green, 2 mutations caught), interview sheet B3 IT-15..18 | Next: PR to main? |
| 2026-11-06 | Opus | Built simulation artifact (cách B); Truong flagged 10 NV / 5 tests / determination points missing; decided 7 NV, tick max 5, points in app (b); wrote plan §8 round 4 | Launching D1, D2 |
| 2026-11-06 | Sonnet | T4M-M6 (D2): app spec Top 7, tick max 5, determination-point screen; R25..R38, HDT rows 14.x + section 14; CONG_THI, MICROSOFT, interview sheet | Docs only; no subagent; no code touched; grep shows no stale "Top 3" in the five files |
| 2026-11-06 | Opus | Updated simulation artifact v2 (Top 7, tick, two funds); reviewed D2 T4M-M6 (OK; R37 no longer counts legit "vắng thi" warnings) | Waiting D1 |
| 2026-11-06 | Sonnet | T4M-Q5a/b/c (D1): converter THIk/WPk, fake Lists/Forms with ticks and funds, demo --day-du; tests first (29 red on first run -> all 34 green), 5 mutations caught | No subagent; no core/schema/CSV change; default outputs byte-identical |
| 2026-11-06 | Opus | Reviewed D1 T4M-Q5a/b/c: tests green after fixing D2/D1 clash (HDT no longer named `NV3`), demo default and --moi-clb outputs identical to before, --day-du runs; kiosk auto-fills single-club fund (confirmed); round 4 done | Artifact v3 next |
| 2026-11-06 | Opus | Artifact v4 (demo --day-du numbers); handoff at ~400k context (Stop hook); no new work | Next: ask Truong about PR to main |
| 2026-11-06 | Opus | Truong asked to recreate the simulation page; asked clarifying questions only (no new work, context full) | New session: get answers first |
