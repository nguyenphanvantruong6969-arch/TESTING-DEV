# FA-SC fix plan: ideas and order of work for every failure in the crisis memo

> Written 2026-11-14 by the Fable research session, branch `claude/fable-fa-sc`. English on purpose.
> Input: `docs/fable/06_CRISIS_MEMO.md` (catalogue S1–S48, T1–T5, I1–I8, facts F1–F15, drills d01–d16).
> This is a **proposal**. Nothing here is approved or built. Per `CLAUDE.md` rule 11, Opus turns the approved parts
> into a coding plan and Sonnet writes the code; Fable does not edit production code.
> Every number is **SỐ LIỆU MÔ PHỎNG** (120 fake students, seeded). "Recommended" marks the AI's suggestion for a
> decision that belongs to Truong and the school; it is not a decision.

## 1. Design principles (why the plan has this shape)

1. **Three layers per failure** (Reason 2000): prevent, detect, recover. Most failures today have at most one layer,
   and it is usually a line in a warning list that IT is known to skip (memo I3).
2. **Give the student the feedback, not IT.** One per-student confirmation sheet before lock turns about a third of the
   student rows from "nobody notices" into "the student notices while it is still free to fix".
3. **Corrections are free before lock and evidence-only after results.** This keeps truthful ranking safe: a
   post-result "I misclicked" channel would be a free second try (memo S6).
4. **Never rerun with a changed head-count after announcing** until the per-day lottery is fixed (F15).
5. **Cheapest layer first.** Wording and checklists cost nothing and cover the largest number of rows.
6. **Each software fix is "done" when a named drill flips**, and the default configuration stays byte-identical
   (invariant 1).

## 2. Work packages

Cost: S = documents only; M = converter / scripts under `mau_forms_thi_clb/`, no kiosk change; L = kiosk code.
"Flips" = the drill result that must change. Proposed test files are names only.

### Phase 0 — before the real round, no code (S)

| WP | What | Covers | Needs |
|---|---|---|---|
| P0-1 (FA-SC-1) | Student one-pager + the 7 GVCN sentences (runbook §8) + three wording changes in the forms: "a free club always accepts you; put it first only if it is your favourite", "three DIFFERENT clubs", deadline as weekday + date + hour. Truong writes the final text | S2, S7, S9, S11, S14, S16, S19, S24, S32, S33, S47 | — |
| P0-2 (FA-SC-7) | Adopt the pre-announcement checklist (runbook §4) with two signatures; club teachers read capacities back; Forms settings checklist per form | T2, T3, T5, I1, I2, I3, I7, I8, S45 | — |
| P0-3 | Operating rule: after announcing, late students go to leftover seats (round 2) or the waitlist; no rerun with a changed student list | I4, F15, S8, S26 | D-SC7 (a) |
| P0-4 | Attendance rule: never mark "unexcused" when unsure; the admin reviews every release before passing an invitation on | T4, S23, S40 | — |
| P0-5 (FA-SC-9) | Welfare: GVCN gets the list of students placed by fallback or outside their list, and the script | S29 | — |
| P0-6 | Decide D-SC2…D-SC7 (§4) and write the answers into the runbook | S1, S3, S5, S6 … | Truong, school |
| P0-7 | Try the five items of memo §10 on real Microsoft Forms (TH) | F3, S3, S37 | a test tenant |

### Phase 1 — converter and scripts only (M); kiosk untouched, workbook bytes unchanged

**P1-1 Roster input (FA-SC-6, part of FA-SC-4).** The converter accepts the school roster that
`danh_sach_chua_dang_ky.py` already reads (`student_id`, `class_id`, optional `email`).
- ID check: an ID not on the roster, or one ID used by two emails, is listed **before** the workbook is written, with
  both emails (S30, S27). With an `email` column, the typed ID is replaced by the roster ID and the difference reported.
- Class: `class_id` from the roster fills the workbook's class column (S45).
- Not registered: a sheet "Chưa đăng ký" per class, and "missing day" per student (S8, S36).
- `kiem_nhan`: fake roster + export with one collision, one unknown ID, one unregistered student, one missing day →
  exactly one line each; clean data → none; without the roster option the output is byte-identical to today.
- Flips: d03a (import no longer refused; the collision is reported and resolved from the roster), d03b (unknown ID
  reported), d14 (0 of 120 without a class), d01 and d02 (student named in a report).
- Invariants: 7 (workbook columns unchanged; class column already exists), 1.

**P1-2 Linked warnings (FA-SC-4).** A new sheet "Cần xử lý" in `BANG_DIEM.xlsx`, one row per student, built from
warnings that already exist: wrong-test pair (test without rank + NOT_ATTEMPTED), response dropped for an unknown
email, choices changed after the test time, FREE club ranked above a tested SELECTIVE club, typed name ≠ roster name
for the test email, unused reservation (addressed to the club teacher). Each row: who acts, what to do.
- `kiem_nhan`: each injected case gives one row; the existing warning list is unchanged.
- Flips: d06 (two lines → one actionable row), d04, d05 (a row for B when names differ), d07.
- Invariants: 2 (rows are reports; nothing feeds the priority key), 1.
- Limit: the name cross-check for S37 needs a "class and full name" question in the test form (form generator change).

**P1-3 Confirmation sheet (FA-SC-2).** One file per class before lock: per student and day, the choices as stored,
the three medals, which tests were received and count, and what is not counted with the reason. Delivered through GVCN.
- `kiem_nhan`: one block per student; a dropped test appears as "not counted + reason"; no other student's data in a
  class file; no scores of other students, no lottery numbers.
- Covers: S2, S5, S7, S12, S13, S15, S21, S32, S33, S36, S48.
- Depends on P1-1 for the class. Privacy: same handling as the result-by-class files.

**P1-4 Dropped-response report for club teachers.** From P1-2, one small file per club: emails whose response was
dropped and students who ranked the club but have no test. Sent before lock (S5, S16, S42).

### Phase 2 — kiosk code (L); each needs its own approval and tests first

**P2-1 Per-day lottery lock (new, FA-SC-10; D-SC7 option b).**
- Problem: F15. Prototype evidence (`du_lieu_test/su_co/thu_p1_khoa_so_theo_ngay.py`, in-process, no file changed):

  | drill | earlier students moved today | with the prototype |
  |---|---|---|
  | d12, 5 late students, seed 42 / 7 | 20 / 51 | 1 / 1 |
  | d16, 1 late student taking no contested seat, seed 42 / 7 | 18 / 38 | 0 / 0 |

- Idea: at the first run, store each day's order (new table, e.g. `stb_buoi(buoi, student_id, so)`). On later runs,
  earlier students keep their order on every day and new students are inserted uniformly per day with the existing
  `chen_stb_cho_hoc_sinh_moi`, seeded by `_seed_cua_buoi(seed, buoi)`. The first run calls today's function, so
  first-run results stay byte-identical. All three callers must read the stored order: the run, the lottery report
  (`get_so_boc_tham_theo_buoi`) and round 2 (`_du_lieu_vong_2`).
- Alternative considered: per-student hash `crc32(seed|day|student_id)`. No storage, but it changes first-run results
  (invariant 1) and is no longer a function of the witnessed base lottery (FA-9). Not recommended.
- `kiem_nhan`: (1) 3 data sets × 20 seeds first run byte-identical; (2) property test: after adding k students, the
  relative order of earlier students is unchanged on every day; (3) each newcomer's per-day position is uniform
  (chi-square over seeds); (4) deletion leaves the others' order unchanged; (5) redraw (`force_redraw_stb`) clears the
  table and leaves a trace; (6) migration idempotent with backup; (7) the lottery record fingerprint (FA-9) covers the
  per-day orders or states that it does not.
- Invariants: 1 (first run), 3 (extends the promise to per-day order; wording for Truong to confirm), 4, 5, 7 (schema).
- Open questions: old workspaces already run (no stored order → store on the next run, which reshuffles once, or
  rebuild from the recorded head-count); interaction with G1 (resume DA) and G3.

**P2-2 Attendance and invitations (FA-SC-5).**
- Release becomes two steps: the second unexcused mark creates "pending release"; the seat is released and the next
  student invited only when the admin confirms. A reversal kind in `fa_dieu_chinh` undoes a release or an accepted
  invitation while the freed seat is unclaimed. Invitations get a stored deadline and an age column.
- `kiem_nhan`: slip then correction → student still in the seat, no invitation; log shows both rows; `match_results`
  and `run_history` untouched; reversal refused once the seat is taken.
- Flips: d08. Invariants: 4 (append-only kept), 6 (new error codes through `i18n_errors.py`).
- Manipulation: one undo per invitation, inside a cooling-off window only (S39).

**P2-3 Capacity sanity warning.** Import and pre-run warning (not blocking) when a club's capacity is under a set
fraction of its first-choice demand or of the previous run's capacity. Flips: d09 (0 warnings → 1). Covers T3.

**P2-4 One invalid student (D-SC4 option b).** Set the student aside, run the rest, report. Changes what the
validation step means (invariant 5), so it needs Truong's decision first. Cheaper today: the error already names the
student and nothing is lost (d10), and path B cannot produce the case. Recommended: keep blocking; do not build.

**P2-5 Protect announced students (registry G3).** Unchanged from the registry; P2-1 is a precondition, because
without it G3 would be measuring lottery noise.

## 3. Coverage: every catalogue row has a home

| rows | handled by |
|---|---|
| S2, S7, S9, S11, S14, S16, S19, S24, S32, S33, S47, S48 | P0-1 wording; P1-3 confirmation sheet |
| S1, S17, S31 | P1-2 linked row; D-SC2 window; P0-1 |
| S5, S37, S18 | P1-2, P1-4; supervised sitting for SELECTIVE clubs (D-SC2) |
| S8, S10, S36 | P1-1 not-registered / missing-day lists; D-SC5 |
| S30, S27 | P1-1 ID check |
| S45 | P1-1 class from roster; P0-2 checklist |
| S3, S34, S35 | D-SC2, D-SC6 rules; runbook |
| S6, S15, S28 | D-SC3 rule; P1-3 sheet as the record of what was stored |
| S22, S23, S38, S39, S40, T4 | P0-4 now; P2-2 |
| S25, S41 | existing complaint flow (FA-M6); runbook |
| S26, S46, I4 | P0-3 now; P2-1; registry G1–G3 |
| S29 | P0-5 |
| S42 | P1-4 |
| S43 | not yet understood: drill first (needs a sample with minimum numbers) |
| S44 | P0-2 (student reads the screen, signed print) |
| S4, S4b | keep blocking (P2-4 not recommended) |
| S12, S13, S20, S21 | already handled by existing warnings; shown to the student by P1-3 |
| T1 | existing rescoring + item analysis; add "second person checks the key" to P0-2 |
| T2 | P0-2 settings checklist; existing blocking error (d11) |
| T3 | P0-2 read-back; P2-3 |
| T5, I8 | P0-2 |
| I1, I2, I3, I7 | P0-2; P1-2 makes the list short enough to read |
| I5, I6 | existing guards (F13); off-machine backup line in P0-2 |

## 4. Decisions, with a recommendation each (Truong and the school decide)

| id | question | recommended | why | what it costs |
|---|---|---|---|---|
| D-SC2 | retake after a wrong test | before lock only, club teacher approves, different variant, only if no response exists for the intended club | closes the "second try" channel | clubs need a second variant |
| D-SC3 | post-result claims | data errors only, proven by a system record | keeps truthful ranking safe | some genuine slips stay uncorrected; P1-3 reduces how many |
| D-SC4 | one invalid student | keep blocking | loud, loses nothing, rare | IT fixes one row |
| D-SC5 | not registered at lock | GVCN-signed list; students who register later use leftover seats, no rerun | avoids F15 and moving announced students | late students get fewer options |
| D-SC6 | flagged-fast retake | keep the first score unless the admin records a reason | an honest fast student is not punished; a deliberate fast fail gains nothing | admin judgment needed |
| D-SC7 | per-day lottery | (a) now: no rerun with a changed list; (b) then build P2-1 | (a) is free and immediate; (b) removes the cause | (b) schema change, full test pass |

## 5. Suggested order and effort (rough, to be re-estimated by Opus)

| order | package | effort | blocks the real round? |
|---|---|---|---|
| 1 | P0-1 … P0-6 | days, no code | yes: do before registration opens |
| 2 | P1-1 roster | small | yes for path B (IDs, class) |
| 3 | P1-2, P1-4 linked rows | small | strongly advised |
| 4 | P1-3 confirmation sheet | medium | strongly advised |
| 5 | P2-2 attendance | medium | only if attendance / waitlist is switched on this term; otherwise keep `fa_diem_danh` off |
| 6 | P2-1 per-day lottery lock | medium–large | no, if rule P0-3 is followed |
| 7 | P2-3 capacity warning | small | no |
| — | P2-4, P2-5 | — | not now |

If time is short: Phase 0 plus P1-1 removes or exposes the three highest-ranked failures (absent student, wrong ID,
no class) and the rerun risk, without touching the kiosk.

## 6. Risks of the plan itself

- More reports can mean more unread lists. P1-2 must replace reading the raw warning list, not add to it.
- The confirmation sheet shows a student their medals and choices; it must never show a lottery number or a score of
  another student, and it must go out before lock or it becomes a source of post-result claims.
- P2-1 changes results of reruns compared with today's reruns. That is the intended effect, but it must be stated in
  `CHANGELOG.md` and checked against invariant 1 exactly as worded ("same data, same seed").
- Everything on Microsoft's side is still TH; path A (Power Apps) is not in the repository.
- All effect sizes come from one small fake data set (120 students, 3 clubs per day).
