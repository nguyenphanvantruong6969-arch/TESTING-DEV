# Research memo: RB-DA / FA-DAA

> Research output (CLAUDE.md rule 11, "Fable researches"). No production code was changed.
> **Every number in this file is SIMULATED (SỐ LIỆU MÔ PHỎNG)**: seeded random generators, no real students.
> This memo gives evidence, options and test designs only. Interpretation and report conclusions are Truong's.

## G-A. Audit of the current mechanism (first pass: top 3 findings, 2026-11-12)

Scope: `chay_fa_daa` and `ly_do_ket_qua` in `fa_daa.py`, the call in `PipelineAPI._run_pipeline_da_khoa`
(`api.py`), `uu_tien_wharton` / `tham_so_luat` in `rbda_priority_pipeline.py`.
Reproduce everything below with `du_lieu_test/fable_ga_kiem.py` (new, research-only script):

    python du_lieu_test/fable_ga_kiem.py phan_vi_du    # CE1–CE3
    python du_lieu_test/fable_ga_kiem.py tim_lech      # table A1 (~20 s)
    python du_lieu_test/fable_ga_kiem.py huy_chuong    # tables A2, A3 (~3 min)
    python du_lieu_test/fable_ga_kiem.py quan_the      # table A4

### A.0 Wrapper steps at a glance

"Stable" = no blocking pair on the prepared inputs (what `verify_stability` checks). "Truthful" = no student
gains by changing the ORDER or LENGTH of the rank list, medals held fixed.

| Step in `chay_fa_daa` | Stable | Truthful (ranks, medals fixed) | Evidence |
|---|---|---|---|
| (1) FREE capacity = number of students | yes | yes | Capacity never binds; the club accepts every applicant. |
| (2) SELECTIVE filter (`NOT_ATTEMPTED`, `BELOW_PASS`) | yes | yes | Sketch S1. Caveat: medals on filtered clubs are dead (finding 2). |
| (3) LIMITED: scores dropped | yes | yes | Only changes a priority input that does not depend on the student's report. |
| (4) Reserved seats as soft reserve (D6) | yes | yes | Sketch S2. **Fails silently when strict group priority is on (finding 3).** |
| FA-5 closing loop (D3, `so_toi_thieu`) | only on the reduced lists | **no** | **Finding 1: CE1, CE2, table A1.** |
| (5) FREE fallback + rerun | yes | yes | Sketch S3. |
| (6) Room groups | n/a | n/a | Post-processing; does not change who is in which club. |
| Medal placement (D2) | yes | not a truthful choice by design | Finding 2: tables A2–A4, CE4. |
| Reasons (`ly_do_ket_qua`) | n/a | n/a | **Finding 3: CE3 (wrong reason code or ValueError with `tier_rank`).** |

Proof sketches (assume no minimum quota and no `tier_rank`):
- **S1 (filter).** Removing (student, club) pairs where the student is below the pass mark or has no score is
  the same as the club declaring that student unacceptable. Acceptability depends on the score only, not on
  the student's report, so the market is a standard one with responsive priorities: student-proposing DA is
  stable and strategy-proof (Dubins & Freedman 1981).
- **S2 (reserve).** `reserve_capacity` = number of usable reservations of the club, eligibility = being in
  `giu_cho`. Pass 1 of `club_choice_function` therefore always admits every reserved applicant, so the choice
  function equals "sort by `(−reserved, base key)` and take the top `capacity`": responsive, hence
  substitutable and satisfying the law of aggregate demand (special case of Kominers & Sönmez 2016).
- **S3 (fallback).** The FREE club is appended at the END of the list of a student who was rejected by every
  listed club, and it never rejects. By order-independence of DA, every proposal made before that point is
  unchanged, so no other student moves. Listing that FREE club truthfully is weakly better than relying on the
  fallback (same club or a preferred FREE club), so the fallback creates no gain from shortening the list.

### Finding 1 (severity HIGH, if any club has `so_toi_thieu` this term): the closing loop D3 breaks truthful ranking and depends on closing order

**Evidence.**
- **CE1 (2 students, runs on the real code).** A = SELECTIVE, 1 seat, pass 5; C = LIMITED, 2 seats, minimum 2;
  F = FREE. True lists: s: A > C > F (score 8 at A), t: C > A > F (score 9 at A).
  Truthful: C has 1 member, closes; t moves to A and beats s; result s → F, t → A.
  s reports C > A > F (same medals): C has 2 members and stays open; result s → C, t → C.
  s moves from the 3rd to the 2nd true choice by misreporting; t is also better off.
- **CE2 (3 students).** X and Y = LIMITED, 3 seats, minimum 3; F = FREE. a: X > F; b, c: Y > X > F.
  The code closes X first (largest shortfall: 2), then Y (shortfall 1): all three → F.
  Closing Y first sends b and c to X, X reaches 3 and stays open: all three → X. "Largest shortfall first" is
  not neutral; a club that would be viable is closed and three students prefer the other order.
- **Table A1 — random search for a profitable rank misreport (SỐ LIỆU MÔ PHỎNG).** Generator
  `tests/test_fa_tinh_chat._bo`, 200 instances per row, every permutation and sub-list of each true list (≤ 4
  clubs), medals fixed.

| minimum quota | instances | instances with a profitable misreport | students tried | students who gain | blocking pairs on prepared inputs |
|---|---|---|---|---|---|
| off | 200 | 0 | 1298 | 0 | 0 |
| on (1–3 per club) | 200 | 2 | 1289 | 2 | 0 |

  First hit: seed 72, student `s02`, true list `[C12, C11]`, report `[C11]`: true rank 3 (fallback) → 1.
- **Why the existing checks do not see it.** `test_13_1_khai_that_thu_tu_la_toi_uu` builds data with
  `_bo(seed)` (`toi_thieu=False`), so the loop never runs there. `verify_stability` runs on `kq_fa.preferences`,
  from which the closed club has already been removed, so a group of students who all prefer the closed club is
  invisible to it (it is not a blocking PAIR).
- **Theory.** With minimum quotas no mechanism is both strategy-proof and free of this kind of waste in
  general (Fragiadakis, Iwasaki, Troyan, Ueda & Yokoo 2016). "Accept the group only if it reaches the minimum"
  is not a substitutable choice rule, so by invariant 8 this step belongs under the label
  "không bảo đảm ổn định" unless redesigned.

**Options (decision for Truong, item A13 / FA-5; a replacement rule would be item A7/A12 territory).**

| Option | What changes | Cost |
|---|---|---|
| 1a. Leave `so_toi_thieu` empty this term; teachers decide viability BEFORE registration opens, or handle an under-filled club by hand after results | no code change | under-filled clubs possible |
| 1b. Keep D3, state in the student guide that the "truthful ranking is optimal" promise excludes clubs with a minimum; label the run per invariant 8 | wording + label | weaker promise |
| 1c. Later: study a quota-reduction rule from Fragiadakis et al. (ESDA / MSDA) in measurement mode | research, new item | not for this term |

**Property tests that would catch it (`kiem_nhan` style).**
- T1: `test_13_1` parametrised with `_bo(seed, toi_thieu=True)`, seeds 0–199, including sub-lists (dropping
  clubs), expecting no strictly better report. Fails today at seed 72 → documents the limit, or guards a redesign.
- T2: order-neutrality: for every instance where two clubs are under the minimum, closing either first must give
  the same final set of open clubs. Fails today on CE2.
- T3: CE1 and CE2 as fixed regression cases.

### Finding 2 (severity MEDIUM–HIGH): default medals are often not the best placement, and a deviation mostly costs default users

Model: `mo_phong_fa_daa.sinh_du_lieu` (n = 100, 2 days, 5 clubs/day: 1 FREE, 2 LIMITED, 2 SELECTIVE with pass
mark 5; list ≤ 4; 30 % `luoi`, 50 % `that_tha`, 20 % `chien_luoc`), 5 data seeds. One student at a time
changes medals for one day; everyone else as generated. "Best response" = the placement (any of up to 24) with
the highest mean true liking on 4 lottery draws, then **evaluated on 4 other draws** (out-of-sample).
"Hindsight" = share of draws where some placement beats the default after seeing the lottery (upper bound).

**Table A2 — unilateral medal deviation by behaviour type (SỐ LIỆU MÔ PHỎNG).** Utility = true liking, 0–1.

| type | student-days | default: utility | default: % true NV1 | default: mean true rank | best response: utility | BR: % true NV1 | BR: mean true rank | % student-days BR ≠ default | hindsight % draws | % default gold on a filtered club |
|---|---|---|---|---|---|---|---|---|---|---|
| luoi | 246 | 0.4263 | 31.6 | 2.590 | 0.4734 | 33.8 | 2.240 | 32.5 | 24.1 | 2.0 |
| that_tha | 544 | 0.4716 | 50.1 | 2.077 | 0.4967 | 46.4 | 1.893 | 28.9 | 19.4 | 12.3 |
| chien_luoc | 210 | 0.5017 | 51.5 | 2.035 | 0.5213 | 47.6 | 1.879 | 26.2 | 17.7 | 11.4 |

Same run, fixed rules a student could follow without knowing others' choices (mean utility):

| type | default | skip clubs where own score < pass mark | LIMITED clubs first | least-hot first (the script's `chien_luoc`) | best response |
|---|---|---|---|---|---|
| luoi | 0.4263 | 0.4283 | 0.4305 | 0.3968 | 0.4734 |
| that_tha | 0.4716 | 0.4765 | 0.4798 | 0.4303 | 0.4967 |
| chien_luoc | 0.5017 | 0.5053 | 0.5100 | 0.4529 | 0.5213 |

**Table A3 — effect of one student's best response on the others (SỐ LIỆU MÔ PHỎNG).** 1,168 deviation-draws.

| others made worse per deviation-draw | others made better | harmed who are `luoi` | `that_tha` | `chien_luoc` |
|---|---|---|---|---|
| 0.786 | 0.253 | 104 | 686 | 128 |

**Table A4 — population view (SỐ LIỆU MÔ PHỎNG).** 10 data seeds × 4 lottery draws, same data per profile.

| medal profile | type | mean utility | % true NV1 | % student-days with a lottery loss |
|---|---|---|---|---|
| all default | luoi | 0.4256 | 26.8 | 57.7 |
| all default | that_tha | 0.4684 | 37.8 | 43.6 |
| all default | chien_luoc | 0.4778 | 39.9 | 41.4 |
| `chien_luoc` use LIMITED-first | luoi | 0.4236 | 26.3 | 53.5 |
| `chien_luoc` use LIMITED-first | that_tha | 0.4660 | 37.3 | 43.0 |
| `chien_luoc` use LIMITED-first | chien_luoc | 0.4836 | 38.0 | 44.1 |
| all use LIMITED-first | luoi | 0.4241 | 25.9 | 62.5 |
| all use LIMITED-first | that_tha | 0.4651 | 35.3 | 51.1 |
| all use LIMITED-first | chien_luoc | 0.4765 | 37.3 | 46.9 |

Facts read directly from the tables (no interpretation):
- The best response differs from the default in 26–33 % of student-days; out-of-sample utility is higher by
  0.047 (`luoi`), 0.025 (`that_tha`), 0.020 (`chien_luoc`). Its % true NV1 is LOWER for `that_tha` and
  `chien_luoc`: the gain comes from securing a 2nd/3rd choice, not from winning the 1st.
- The `chien_luoc` rule coded in `mo_phong_fa_daa.py` (gold on the least hot of the top three) scores BELOW the
  default in this model, so existing tables "by behaviour type" do not measure the gain of a good strategy.
- 12.3 % of `that_tha` student-days have the default gold on a SELECTIVE club where the student is below the
  pass mark; that medal has no effect anywhere. Skipping such clubs recovers 0.005 of the 0.025 gap.
- **CE4 (default couples medals to rank).** A = SELECTIVE 1 seat, B = LIMITED 1 seat, F = FREE. s truly
  A > B > F, score 6 at A; u has 10 at A; t lists B with gold. Default medals: s loses A on score and B on medal
  (gold vs silver) → F. Reporting B > A moves s's default gold to B → s gets B. Keeping the true order and
  overriding medals gives the same B. So "truthful ranking is optimal" holds only for a student who places
  medals deliberately; a student who keeps the default has a reason to reorder. This is inside the D2 exception
  (every student can override) but matters for what the student guide may promise.

Limits of this evidence: 5 clubs per day and lists of 4 are smaller than the school (≈ 20 clubs, lists up to
10); the best responder knows everyone else's registration, which a real student does not; the liking model is
an assumption of the script. A rerun with the school's club counts and capacities is the natural next step.

**Options (decision for Truong; item A13 / FA-3, D2).**

| Option | Invariant impact |
|---|---|
| 2a. Keep the rule; the student guide says medals are a choice with trade-offs, and never says the default is "safe" or "best" | none |
| 2b. Dead medals: let students see their scores before confirming medals (path A), or warn at registration when a medal sits on a club with a pass mark | none (registration layer) |
| 2c. Dead medals: after the pass-mark filter, slide medals down to the next eligible club in rank order | **needs new exception text for invariant 2**: the D2 exception allows rank-derived defaults "at the registration layer only"; this would read rank at run time |
| 2d. Replace `chien_luoc` in `mo_phong_fa_daa.py` by a best-response type before quoting "by behaviour" numbers | script only |

**Property / measurement tests.**
- T4: the `huy_chuong` routine as a monitored number: "% student-days where best response ≠ default" and
  "% default gold on a filtered club", on the school-sized simulated data set, recorded in
  `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` with the SIMULATED label.
- T5: CE4 as a fixed case asserting that override (true order + moved medals) reaches the same club as the
  rank misreport, i.e. the override path is never worse than reordering.
- T6: after the run, count medals whose club is in `loai_bo` for that student (dead medals) and show it in the
  data-health report.

### Finding 3 (severity MEDIUM; HIGH if the school turns on strict group priority together with FA-DAA): reserved seats are dropped and reasons are wrong or crash when `tier_rank` is set

`tham_so_luat` returns `tier_rank` and `bo_qua_du_tru=True` when the workspace uses strict group priority, and
the pipeline passes both into `chay_fa_daa`. No guard against this combination was found in `dung_fa_daa`
or `tham_so_luat`.

**Evidence (CE3, runs on the real code).**
- A = LIMITED, 1 seat; r has a reserved seat at A (`giu_cho`) and lottery 2; o has lottery 1.
  Without tiers: r → A. With `tier_rank` (both in the same group) and `bo_qua_du_tru=True`: **o → A, r → F**.
  The reservation is ignored without a warning, and `ly_do_ket_qua` raises
  `ValueError: FA-6: khoa cua r tot hon nguoi nhan cuoi` (its key still counts the reservation).
- A = LIMITED, 1 seat; k12 (group 0, lottery 2) and k11 (group 1, lottery 1), both gold: k12 → A (correct by
  group), then `ly_do_ket_qua` raises the same ValueError because its key `(−reserved, −score, −medal, lottery)`
  has no group element. If k11 holds silver instead, no error is raised and the reason shown is `MEDAL`,
  although the group decided.
- In the pipeline the ValueError is raised after the stability check and before the write, inside the
  transaction, so the run rolls back: no wrong result is stored, but the run cannot finish on the day.

**Options (item A13 / FA-4, FA-6; rule group `tiers` of the workspace).**

| Option | Cost |
|---|---|
| 3a. This term: FA-DAA runs only with `tier_mode` ≠ strict; add a precheck error for the combination | small code change (Sonnet session), new error code |
| 3b. Support it: add the group to the reason key (new reason code, e.g. `GROUP`) and define whether a reservation outranks the group | code + decision on precedence + i18n |

**Property tests.**
- T7: for random instances with `tier_rank`, `ly_do_ket_qua` must not raise, and every `REJECTED` reason must
  equal the first element that differs in the key actually used by `uu_tien_wharton`.
- T8: every usable reservation (student ranks the club, passes the mark) ends with that student at the club or
  at a club they rank higher, for every rule combination the workspace accepts.

### Not yet examined (waiting for Truong's go-ahead)

Integer 0–10 scores and tie share (brief G-A question 3); reserved students below the pass mark (reservation
lapses with reason `BELOW_PASS`, no separate warning); medals on a club closed by D3; school-sized rerun of
tables A2–A4; waitlist order versus the run-time key.

### References (checked against Crossref on 2026-11-12)

- Dubins, L. E. & Freedman, D. A. (1981). Machiavelli and the Gale-Shapley Algorithm. *The American
  Mathematical Monthly* 88(7). doi:10.1080/00029890.1981.11995301
- Kominers, S. D. & Sönmez, T. (2016). Matching with slot-specific priorities: Theory. *Theoretical Economics*
  11(2). doi:10.3982/te1839
- Abdulkadiroğlu, A., Che, Y.-K. & Yasuda, Y. (2015). Expanding "Choice" in School Choice. *American Economic
  Journal: Microeconomics* 7(1), 1–42. doi:10.1257/mic.20120027
- Fragiadakis, D., Iwasaki, A., Troyan, P., Ueda, S. & Yokoo, M. (2016). Strategyproof Matching with Minimum
  Quotas. *ACM Transactions on Economics and Computation* 4(1). doi:10.1145/2841226

### Note for the project's AI log (for Truong to copy if he wishes)

2026-11-12, Claude (research role, branch `claude/fable-ga-audit`): read `fa_daa.py` and the pipeline call,
wrote the research script `du_lieu_test/fable_ga_kiem.py`, built four small counterexamples (CE1–CE4) and four
simulated tables (A1–A4), and wrote section G-A of this memo. No production code changed; no report text written.
