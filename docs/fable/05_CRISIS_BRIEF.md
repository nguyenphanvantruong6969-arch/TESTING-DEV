# Brief for a Fable research session: human error and crisis scenarios (FA-SC)

> Written 2026-11-14 (Opus, branch `claude/dreamy-johnson-cgw652`). English on purpose.
> Read first: `CLAUDE.md`, `docs/fable/01_PROJECT_CONTEXT.md`, `docs/fable/02_FABLE_BRIEF.md` §1 (ground rules apply
> unchanged), then this file. Role: research partner. **Never edit production code** (`CLAUDE.md` rule 11).
> Registry: no item covers operational human error yet. Item code **FA-SC** ("sự cố") = new item, outside the
> registry, approved by Truong 2026-11-14 (D-SC1). Map each proposal to FA-SC-n, or to an existing item if it fits
> better (G1–G5 changes over time, A13 FA-DAA sub-items, FA-M6 post-allocation).

## 1. Goal
Find what can go wrong when real people (students, club teachers, homeroom teachers, IT) run one allocation round,
when the software itself works as designed. Example from Truong: a student misclicks and takes the wrong club's
test, or a test they did not select. For each failure: how likely, how much harm to a real student, whether the
current system detects it, and the cheapest fix (prevent / detect / recover) that keeps the 8 invariants.

Priority rule (same as `02_FABLE_BRIEF.md`): rank by **harm to real students this semester**. Highest: a student
placed wrongly, unfairly or unexplainably, a student's data shown to another person, or one person's slip blocking
the whole school's run. Lowest: cosmetic, other sectors.

## 2. Sources of truth for the workflow (read only what you need)
| Stage | Doc | Code to read (by function name) |
|---|---|---|
| Teachers build tests, Forms settings | `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` §1, `mau_forms_thi_clb/GHI_CHU_GIAO_VIEN.md` | `mau_forms_thi_clb/tao_mau_forms.py` |
| Students register, tick tests, take tests | `docs/he_sinh_thai/T4M_CONG_THI.md`, `T4M_DAC_TA_SUA_APP.md` §2, §11 | — (Power Apps, not in repo) |
| Lock, export, convert | `T4M_VAN_HANH_MOT_DOT.md` §3–5 | `chuyen_forms_sang_phan_mem.py`, `api_forms_nap.py`, `so_nhap.py` |
| Import, run, export by class | `T4M_VAN_HANH_MOT_DOT.md` §6–7, `HUONG_DAN_SU_DUNG.md` §8, §10 | `api_nhap.py`, `run_pipeline`, `api_xuat.py`, `recovery.py` |
| After results: complaints, attendance, waitlist | `docs/he_sinh_thai/FA_SAU_XEP.md`, `T4M_FLOW_GUI_GVCN.md` | `fa_sau_xep.py` (`ghi_dieu_chinh`, `moi_tiep`, `trong_han_khieu_nai`, `anh_huong_sau_chay_lai`, `khop_ma_hoc_sinh`) |
| Late arrivals, withdrawals, reruns | `T4M_VAN_HANH_MOT_DOT.md` §8 | `mau_forms_thi_clb/doi_chieu_lists.py` |
| Earlier robustness work (do not repeat) | `docs/ke_hoach/VAN_DE_STRESS_TEST.md`, `BAO_CAO_STRESS_TEST.md` | `du_lieu_test/stress/` |

## 3. Seed list of hypotheses (verify each; add your own; drop what is wrong)
Labels: **[V]** verify in code or with a drill, **[P]** policy question for Truong.

**Students**
- S1 [V] Takes the wrong club's test (misclick, shared link, wrong tab). "One response per person" blocks a retake;
  the intended club then reads NOT_ATTEMPTED. What does the converter do with the wrong test (dropped if not ticked)?
  Can a teacher delete the response to reopen it, and does the converter then see two responses?
- S2 [V] Ticks the wrong club for testing, or ranks clubs in the wrong order (NV1/NV2 swapped), or wrong day.
- S3 [V] Submits early by accident, timer runs out, network drops mid-test, "Đã làm" status arrives late (flow delay)
  and the student panics or tries again.
- S4 [V] Determination points (quỹ 1/quỹ 2) do not sum to 100. Doc says the kiosk blocks the run: does ONE student's
  slip block all ~800? Same question for every validation that blocks the whole run.
- S5 [V] Uses a personal or a sibling's account → email not in List → submission silently dropped (warning only).
- S6 [P] After results, claims "I misclicked" to get a better club. Genuine slip vs regret cannot be told apart from
  the claim alone; accepting it opens manipulation (link to strategy-proofness, `02_FABLE_BRIEF.md` G-A).
- S7 [V] Medal placement: default from rank (invariant 2 exception, D2) vs student override done by mistake.

**Students: extended list by stage of the student journey (Truong, 2026-11-14: "more from the student side").**
Treat these as seeds too; walk the journey yourself and add what is missing (target: ≥ 15 new rows of your own).
- *Before registration:* S8 misses the announcement or is absent/sick for the whole window; S9 misunderstands the
  mechanism (ranks a "safe" club first, thinks NV1 is wasted if rejected, misreads medals) — truthful ranking is
  only useful if students believe it; S10 no device, weak connection, disability or language barrier.
- *Registration:* S11 ranks only 1–2 clubs and ends unassigned without knowing the risk; S12 same club on two days
  or a club not offered that day; S13 edits on two devices or the app session times out → draft lost or last write
  wins; S14 a parent or friend fills it in, or the student copies a friend's list (peer pressure); S15 tries to edit
  after lock and believes the edit was saved.
- *Test:* S16 opens the test, closes the tab, never submits (counts as absent?); S17 takes a test before ranking that
  club, or on the wrong day/campus; S18 someone else takes the test (impersonation), answers shared in a group chat,
  or answers leaked by a wrong Forms setting; S19 misunderstands the time limit or the gate question; S20 gets a
  harder quiz variant (fairness between variants, D11); S21 takes more than 5 tests and the extra ones are dropped
  silently from the student's point of view.
- *After results:* S22 never reads the result or misses a waitlist invitation deadline (`moi_tiep`) → seat lost;
  S23 sick for the first sessions → seat released by attendance (`can_giai_phong`); S24 swaps clubs informally with
  a friend, records no longer match reality; S25 complaint with a mistyped student ID → fuzzy match picks the wrong
  student (`khop_ma_hoc_sinh`); complaint after the window (`trong_han_khieu_nai`); S26 moves class or campus
  mid-round, or withdraws then wants back in; S27 two students with the same name, or an ID typo merges two people;
  S28 leaves a shared school computer logged in → another student sees or changes their result; S29 rejected from
  every choice, misreads the explanation sentence, distress (welfare: what does the GVCN say, who follows up).

**Required for every student-side row (S1–S29 and your own):** assign a solution, not only a risk. Columns:
`id | stage | what happens | harm to the student (S 1–5) | likelihood (O, assumption) | detected today by
(warning code / nothing) | solution: prevent | solution: detect | solution: recover | owner (student, club teacher,
GVCN, ECA teacher, IT, software) | before or after results | manipulation risk (can a student fake this case to
gain?) | invariant touched | proposed item FA-SC-n or existing item`. Where the fix is pure communication (wording,
instructions, a reminder), say so; that is a valid, cheap solution. Where the fix needs software, give a
`kiem_nhan` acceptance test.

**Club teachers and homeroom teachers (GVCN)**
- T1 [V] Wrong answer key in Forms (caught: converter rescoring) vs wrong key in `de_thi.json` itself (caught by whom?).
- T2 [V] Wrong Forms settings: Record name OFF (no email), One response OFF (retakes), Show results ON (answers leak),
  `[mã]` prefix deleted, end date wrong.
- T3 [V] Capacity typo (3 instead of 30), wrong pass mark, capacity changed after results were announced.
- T4 [V] Attendance marked wrongly → seat released (`can_giai_phong`) → student loses a seat they still use.
- T5 [V] GVCN forwards a class file to the wrong class or to students (other students' results leak).

**IT**
- I1 [V] Exports before lock, exports a stale List, forgets one club's Forms file (whole club NOT_ATTEMPTED).
- I2 [V] Wrong `--co-so`; imports campus 1 into campus 2's workspace; imports the same file twice (additive import).
- I3 [V] Ignores import warnings (the doc calls this "the most skipped step").
- I4 [V] Announces, then reruns with changed data → announced students moved (G3); forgets `thay_doi_ket_qua.csv`.
- I5 [V] Changes seed or redraws the lottery mid-round (invariant 3: is it blocked, or only discouraged?).
- I6 [V] Deletes `app.db`/workspace, laptop dies or is lost (recovery? off-machine backup? personal data exposure).
- I7 [V] Sends results while the yellow "data changed since last run" band is showing.
- I8 [V] Email↔student_id join wrong (`EMAIL_MA_HS.csv`, `ghep_ket_qua_email.py`) → a student sees another's result.

**Non-human events around people** (only where people must react): Forms/M365 outage on test day, power cut during
`run_pipeline` (invariant 5 says rollback: confirm with a drill), disk full, flow throttling (6,000 requests/day).

## 4. Method (do in order; stop points marked STOP)
1. **Catalogue.** One row per failure: stage, actor, error, consequence for the student, current detection
   (which warning / error code / nothing), severity S (1–5), likelihood O (1–5, state the assumption), detectability
   D (1–5, 5 = nobody notices). Rank by S × O × D (FMEA-style). Name the method's source and verify the citation
   (e.g. FMEA / healthcare HFMEA, Reason's "Swiss cheese" model) before citing it.
2. **STOP:** send Truong the top 5 by rank with one line of evidence each, and ask before step 3.
3. **Drills.** For the top ~10, inject the error into fake data and run the real pipeline read-only:
   `python du_lieu_test/demo_t4m.py --ra <scratch> --day-du` (120 fake students), edit the fake Forms/List files to
   inject the error, then run the converter and kiosk API on a scratch workspace. Record: does a warning fire, is the
   run blocked, how many students change club vs the clean run (same seed), who is harmed. Scripts go under
   `du_lieu_test/su_co/` (one script per drill, `--seed`, deterministic). Never touch a real `app.db`.
4. **Remedies.** For each top failure give 2–3 options in a table: prevent / detect / recover, cost, who acts,
   which invariant it touches, and the manipulation risk (S6). Typical shapes to evaluate, not to assume:
   - correction window before lock (free) vs after results (evidence-based only, e.g. Forms timestamp shows a test of
     a club the student never ticked);
   - per-student quarantine instead of whole-run block (S4), if it keeps invariant 5;
   - checklists / two-person sign-off for IT steps that cannot be undone (I2, I5, I6, I8);
   - an incident log entry for every manual correction (does `fa_dieu_chinh` append-only log already fit?).
   A remedy that reruns after a correction must keep the locked STB (invariant 3) and append to `run_history` (4).
5. **Runbook draft.** A plain-Vietnamese incident handbook for IT and teachers ("Sổ tay sự cố"): symptom → check →
   action → who decides → what to tell the student. Operational docs are allowed (academic integrity only bars the
   project report's commentary and conclusions).

## 5. Open decisions to put to Truong (present options; do not decide)
- D-SC1: item code FA-SC — APPROVED 2026-11-14. Sub-items FA-SC-n still need approval one by one.
- D-SC2: may a student who took the wrong test retake it? Until when? Who approves (club teacher, ECA teacher)?
- D-SC3: after results, which "I made a mistake" claims are accepted (data errors only, as the complaint form says now,
  or also proven misclicks)?
- D-SC4: should one invalid student block the whole run, or be set aside and reported?

## 6. Deliverables
1. `docs/fable/06_CRISIS_MEMO.md` (English, ≤ 400 lines): catalogue table, drill results labelled
   **SỐ LIỆU MÔ PHỎNG**, remedy tables, proposals FA-SC-n with an acceptance test (`kiem_nhan`) in the registry's
   style, risk to each invariant.
2. `docs/fable/06b_SO_TAY_SU_CO.md` (Vietnamese, plain words, ≤ 200 lines): the runbook draft.
3. Drill scripts under `du_lieu_test/su_co/`, read-only use of production code.
4. Short Vietnamese summary to Truong: top 3 risks, decisions D-SC1…4 with options, what to try on real Forms (TH).
5. A 3–5 line note of what the AI did, for Truong's AI log.

## 7. Do not
- Edit production code, change defaults, `run_history`/`match_results` semantics, or the CSV contract.
- Repeat the stress test (concurrency, HTTP, zip) unless a human action triggers it.
- Use real student data; present simulated numbers as real; draft the project report's conclusions.

## 8. Ready-to-paste prompt
```
Read CLAUDE.md, docs/fable/01_PROJECT_CONTEXT.md, docs/fable/02_FABLE_BRIEF.md §1, then
docs/fable/05_CRISIS_BRIEF.md. Work on FA-SC only. Do step 1 (catalogue) of §4. Walk the whole student journey and add at least
15 student-side scenarios of your own to S1–S29; give EVERY student row a solution (prevent / detect / recover,
owner, manipulation risk) in the §3 column format. Then STOP and give me the top 5 human-error risks ranked by
harm to real students, with one line of evidence and the proposed solution each, in Vietnamese.
Do not change production code. Label all numbers as simulated.
```
