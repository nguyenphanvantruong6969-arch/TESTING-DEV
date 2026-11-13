# Research memo: RB-DA / FA-DAA

> Research output (CLAUDE.md rule 11, "Fable researches"). No production code was changed.
> **Every number in this file is SIMULATED (SỐ LIỆU MÔ PHỎNG)**: seeded random generators, no real students.
> This memo gives evidence, options and test designs only. Interpretation and report conclusions are Truong's.

## G-A. Audit of the current mechanism (first pass: top 3 findings, 2026-11-12)

Scope: `chay_fa_daa` and `ly_do_ket_qua` in `fa_daa.py`, the call in `PipelineAPI._run_pipeline_da_khoa`
(`api.py`), `uu_tien_wharton` / `tham_so_luat` in `rbda_priority_pipeline.py`.
Reproduce everything below with `du_lieu_test/fable_ga_kiem.py` (new, research-only script):

    python du_lieu_test/fable_ga_kiem.py phan_vi_du | tim_lech | huy_chuong | quan_the

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
2026-11-13, same role: compared solutions for the three findings at simulated school size (scripts
`fable_ga2_*.py`), wrote section G-A.2. No production code changed; no report text written.

## G-A.2 Solutions for findings 1–3, and other improvements (2026-11-13)

Asked by Truong (via the Opus planning session, confirmed by Truong): challenge Opus's proposals, find the best
option per finding. Constraint from Truong: **students enter only what they enter today** (rank list, test
ticks/answers, optional medal questions); no new student input. Scripts (research only, SIMULATED data):
`du_lieu_test/fable_ga2_giai_phap.py` (`f1`, `f3`, `f2`, `f2_br`, `boc_tham`) and `fable_ga2_huy_chuong.py`.
School-size model `sinh_truong`: 800 students, 3 days, 7 clubs/day (1 FREE, 2 LIMITED, 4 SELECTIVE, pass mark 5),
lists of 6, non-FREE seats = 70 % of students split equally. These are assumptions; pass rate (~50 %) and equal
seats drive several numbers below.

### F1. Minimum members (D3)

Rules compared: **D3** (current loop); **E** = close before the lottery, in one pass, only clubs that cannot reach
the minimum (eligible students who list the club above every FREE club < minimum); **none** = Opus's proposal
(minimum not used in the run; teachers fix the club list before registration).

**Table F1-a — misreport search on 200 small instances, incl. ADDING unlisted clubs (SỐ LIỆU MÔ PHỎNG).**

| rule | instances with a profitable misreport | student-days tried | student-days that gain | clubs closed | open clubs below minimum |
|---|---|---|---|---|---|
| D3 | 4 | 2236 | 4 | 317 | 0 |
| E | 2 | 2236 | 2 | 178 | 132 |
| none | 0 | 2236 | 0 | 0 | 240 |

**Table F1-b — school size, minimum 25 per non-FREE club, 20 data seeds = 360 club-days (SỐ LIỆU MÔ PHỎNG).**

| rule | club-days closed | open club-days below minimum | students in a club below minimum | mean utility | % true NV1 | club-days within ±1 of the minimum |
|---|---|---|---|---|---|---|
| D3 | 20 | 0 | 0 | 0.5444 | 27.9 | 2 |
| E | 0 | 20 | 292 | 0.5453 | 27.9 | 2 |
| none | 0 | 20 | 292 | 0.5453 | 27.9 | 2 |

| Option | Promise "rank honestly" | Stable | Clubs below minimum | Teacher burden | Cost | Invariant risk | Evidence |
|---|---|---|---|---|---|---|---|
| Opus: no minimum in the run, list fixed before registration | kept | yes | possible (20/360) | decide early, without demand data | none | none | F1-a row "none": 0 gains |
| D3 as is | broken in rare pivot cases | on reduced lists | none | none | none | needs label (inv. 8) | CE1, CE2; 4 gains / 2236 |
| E (hopeless clubs only) | broken (padding: list a club you do not want to keep it open) | on reduced lists | same as "none" at school size | none | S | needs label | 2 gains / 2236; fires 0/360 |
| Cancel by hand after results, members take leftover seats | broken (avoid a club likely to be cancelled) | no (members lose priority) | none | manual | none | none | sketch below |
| Fixed, announced closing order | broken (CE1 does not depend on order) | on reduced lists | none | none | S | needs label | CE1 |

- Where Opus is right: fixing the club list before registration is the only option here with zero misreport
  gains, and it needs no code.
- Where the alternatives fail. **E** gives nothing at school size: with 800 students listing 6 of 7 clubs no club
  is ever "hopeless" (0 of 360 closed), and it is still manipulable by padding (seed 163: adding an unwanted club
  keeps it open and keeps a rival there). **Manual cancel after results** removes CE1 but creates a new gain:
  a student who expects club C to be cancelled skips C and takes the next club with full priority, while honest
  members of C fall to leftover seats. **Any closing rule that reads this term's registrations has a pivotal
  student**; only the size of the pivot zone differs (2 of 360 club-days within ±1 of the minimum under D3).
- Correction to option 1c of section G-A: Fragiadakis et al. (2016) treat minimums that MUST be filled, with
  every student acceptable at every school. Here clubs may close and SELECTIVE clubs reject below the pass mark;
  that is the "lower quotas with closure" model, where a stable matching may not exist and deciding existence is
  NP-complete (Biró, Fleiner, Irving & Manlove 2010). No off-the-shelf rule fits; 1c is withdrawn as stated.

**Recommendation.** This semester (A13 / FA-5): agree with Opus — leave `so_toi_thieu` empty; teachers fix the
list before registration; an under-filled club is a teaching decision (run small or merge), not an algorithm
step. If teachers require a hard minimum, D3 as it stands is the least-bad rule (closed members rerun with full
priority; pivot zone small) but the run must carry the label of invariant 8 and the guide must not promise
truthfulness for clubs with a minimum. Later (new item, with G-D): treat the minimum as a PLANNING input —
flag clubs whose last-term or current demand is near the minimum in `bang_nhu_cau` / `goi_y_chi_tieu` — and
make the closing order neutral (T2) if D3 stays as a labelled mode.
`kiem_nhan`: (a) with every `so_toi_thieu` empty, `chay_fa_daa(...).dong_cua == []` and T1 passes on seeds
0–199 with added clubs; (b) if D3 is used, the run record and the result screen show "không bảo đảm ổn định".

### F3. Group priority (`tier_rank`) with FA-DAA

Candidate fix tested read-only: call the core with `bo_qua_du_tru=False` when FA-DAA is on (FA reservations are
named seats from `giu_cho`, not the old group reserve, so the "same group twice" reason for skipping does not
apply). Resulting key order: reserved > group > score > medal > lottery.

**Table F3 — 300 random small instances with random groups (SỐ LIỆU MÔ PHỎNG).**

| call | instances with blocking pairs | usable reservations | NOT honoured | rejections contradicting the key above | `ly_do_ket_qua` raises (instances) | wrong reason codes |
|---|---|---|---|---|---|---|
| current (`bo_qua_du_tru=True`) | 0 | 266 | 47 | 47 of 723 | 144 | 62 |
| candidate (`bo_qua_du_tru=False`) | 0 | 266 | 0 | 0 of 725 | 123 | 71 |

| Option | Stable | Reservations kept | Reasons correct | Cost | Invariant 1 risk |
|---|---|---|---|---|---|
| Opus: block FA + strict groups in the pre-run check | n/a | n/a | n/a | S (1 check, 1 error code, i18n) | none |
| Candidate fix: (1) FA never passes `bo_qua_du_tru=True`; (2) `ly_do_ket_qua` and the waitlist sort take `tier_rank`, key `(−reserved, group, −score, −medal, lottery)`, new reason `GROUP`; (3) `verify_stability` gets the same flag | yes (0/300) | yes (266/266) | after step 2 | M | none: default path has FA off; FA without groups already passes `False` |
| Group above reservation | would need a new two-pass rule | only inside the group | — | L | new choice function → inv. 8 check |

- Agree with Opus for this semester IF the school does not need grade priority: blocking is the smallest safe
  change. The second row shows that step 1 alone is not enough: reasons still fail until step 2.
- Also found: `tier_mode = reserve` with FA-DAA drops the group soft reserve silently (`chay_fa_daa` sets
  `reserve_capacity = 0` by decision D6). The pre-run check should say so.
`kiem_nhan` (A13 / FA-4, FA-6): block → `kiem_truoc_fa` returns a blocking code when rules are FA + strict
groups, pipeline does not start. Fix → T7 and T8 of section G-A pass on 300 seeds; FA-off results byte-identical
(invariant 1 suite); FA-on-without-groups reasons unchanged row by row on the existing FA test data.

### F2. Medals

Designs, same registration data: **D0** current; **D1** same values, default skips SELECTIVE clubs the student
cannot enter (no score or below the pass mark) and moves to the next club in rank order; **D2** three equal
medals; **D3** one medal; **D4** no medals. `gan_toi_uu` = a strategic rule added in the research script (medals
first where they can change the result, using one earlier draw as "last term"); in the sample it reaches the
utility of the enumerated best response, unlike `chien_luoc` of `mo_phong_fa_daa.py`.

**Table F2-a — school size, 5 data seeds, by type (SỐ LIỆU MÔ PHỎNG).** Utility = true liking; "strategic" = the
20 % `chien_luoc` students use `gan_toi_uu`, everyone else default.

| design | profile | luoi utility | that_tha utility | chien_luoc utility | that_tha % true NV1 | that_tha % lottery loss | % default medals on a club the student cannot enter |
|---|---|---|---|---|---|---|---|
| D0 | all default | 0.4554 | 0.5837 | 0.5834 | 40.3 | 20.3 | 28.6–31.3 |
| D0 | strategic | 0.4532 | 0.5662 | 0.6144 | 37.6 | 21.7 | (strategic: 0) |
| D1 | all default | 0.4722 | 0.5653 | 0.5626 | 31.9 | 35.0 | 0 |
| D1 | strategic | 0.4697 | 0.5616 | 0.5734 | 31.4 | 35.4 | 0 |
| D2 | all default | 0.4849 | 0.5521 | 0.5516 | 27.0 | 51.0 | 0 |
| D2 | strategic | 0.4845 | 0.5513 | 0.5531 | 27.0 | 51.1 | 0 |
| D3 | all default | 0.4727 | 0.5628 | 0.5604 | 31.9 | 38.1 | 0 |
| D3 | strategic | 0.4710 | 0.5596 | 0.5698 | 31.4 | 37.4 | 0 |
| D4 | all default | 0.4848 | 0.5502 | 0.5498 | 26.9 | 52.0 | – |

**Table F2-c — sampled unilateral best response, 90 student-days per design (small sample) (SỐ LIỆU MÔ PHỎNG).**

| design | gain: luoi | gain: that_tha | gain: chien_luoc | % BR ≠ default (that_tha) | others worse per deviation-draw (that_tha) |
|---|---|---|---|---|---|
| D0 | +0.1125 | +0.0389 | +0.0288 | 28.6 | 0.97 |
| D1 | +0.0669 | +0.0123 | −0.0041 | 14.3 | 0.67 |
| D2 | +0.0254 | +0.0000 | +0.0000 | 2.4 | 0.00 |
| D3 | +0.0438 | +0.0127 | +0.0073 | 14.3 | 0.78 |

Facts read from the tables:
- Under D0 about 29–31 % of default medals sit on clubs the student cannot enter (model pass rate ~50 %).
  The strategic rule's edge over an honest default-keeper is 0.6144 − 0.5662 = 0.048 under D0, 0.012 under D1,
  0.010 under D3, 0.002 under D2. Most of the D0 edge is "do not leave medals on clubs you cannot enter".
- D1 is not a free gain: with everyone on default, `that_tha` true NV1 falls 40.3 → 31.9 % and lottery share
  rises 21.1 → 35.3 % of rejections, while `luoi` utility rises. Mechanism: in D0 a dead gold removes that student from the
  medal contest elsewhere, so gold at a LIMITED club mostly means "true first choice". That D0 advantage exists
  only while students leave medals dead; informed students already move them (profile "strategic").
- Equal medals (D2) remove the strategy almost entirely but also the function of medals (lottery 64 % vs 69 %
  with none).

Reply to Opus's F2 proposal:
- "Keeping the default is fine" is not supported: under D0 the sampled best response gains +0.039 (`that_tha`)
  and +0.11 (`luoi`), and one deviation makes about one other student worse.
- A warning for "not tested" clubs is correct but weaker than making the default skip them: same information,
  no action needed from the student, covers below-pass cases too if the Forms converter already holds the scores
  when it derives defaults (`dat_huy_chuong_duong_b` in `chuyen_forms_sang_phan_mem.py`; to be confirmed by the
  coder). Done there, it stays at the registration layer; Truong should confirm the D2 exception wording covers
  "default may also read test eligibility".
- Opus's concern that sliding widens the default-keeper channel is not what the tables show for the size of the
  strategic edge (0.048 → 0.012); the real cost of D1 is the NV1 / lottery trade-off above.

| Option | Promise | Fairness to default keepers | Lottery share | Teacher burden | Cost | Invariant risk |
|---|---|---|---|---|---|---|
| D0 + guide wording (Opus) | unchanged | strategic edge 0.048 | 21 % | none | S | none |
| D0 + warning on untested clubs (Opus) | unchanged | helps only students who read it | ~21 % | none | S | none |
| **D1 default at the converter** | unchanged | strategic edge 0.012 | 35 % | none | S–M | confirm D2 exception wording |
| D1 for explicit placements too (slide after filter) | unchanged | as D1 or better | ~35 % | none | M | new exception if done at run time |
| D3 one medal / D2 equal medals | unchanged | edge 0.010 / 0.002 | 42 % / 64 % | re-explain rules | M | medal validation rules change |

**Recommendation.** This semester (A13 / FA-3, registration layer): D1 as the default rule, if Truong accepts
the measured trade-off (fewer true first choices for honest students, smaller edge for informed ones); otherwise
D0 with a guide that states the rule openly to everyone ("a medal on a club you cannot enter is wasted"), which
moves outcomes toward D1 anyway. Later: decide on sliding explicit placements; replace `chien_luoc` by
`gan_toi_uu` in the simulation before quoting numbers by type (script-only change, keep the old type as a control
mode per rule 4). `kiem_nhan`: for every student with untouched defaults, no medal is on a club in `loai_bo` for
that student; override answers still reach all 6 placements (`tests/test_fa_m3_huy_chuong_b.py`); priority key
unchanged (reads stored medals only).

### Other improvements that need no new student input

| # | Idea | Evidence so far | Item | Status |
|---|---|---|---|---|
| 1 | Seats matched to demand (teacher side) | earlier project sims: first choice ~48 % → ~79 % | G-D | largest known lever; next research goal after G-C |
| 2 | D1 default medals | tables F2-a…c | A13 / FA-3 | recommended above |
| 3 | Block-rotated lottery across days: split the locked order into 3 blocks, rotate blocks each day, reshuffle inside | table below; uses no report and no outcome, so per-day truthfulness is untouched (unlike `stb_co_bu`) | new item; touches invariant 3 → new option, default off | small gain, low priority |
| 4 | Reasons layer: `GROUP` reason, dead-medal count, "what would have changed your result" line | CE3, T6 | A13 / FA-6 | cheap, raises explainability |
| 5 | Finer score from the answers already collected (fewer ties) | not yet measured | G-A question 3 | pending |
| 6 | Stable improvement cycles | measurement mode exists | G-B | keep off until G-B |

**Table — cross-day lottery variants, D0, all default, 10 data seeds (SỐ LIỆU MÔ PHỎNG).**

| lottery | mean utility per day | SD of 3-day utility | bottom 10 %: mean 3-day utility | % students with a lottery loss on 0 / 1 / 2 / 3 days | % in the worst lottery third on all 3 days |
|---|---|---|---|---|---|
| independent per day (current `stb_ngay`) | 0.5472 | 0.4387 | 0.8875 | 39.7 / 40.2 / 17.2 / 2.9 | 3.6 |
| same order every day (`stb_tuan`) | 0.5475 | 0.4458 | 0.8765 | 43.8 / 33.5 / 18.2 / 4.5 | 33.4 |
| block-rotated | 0.5475 | 0.4348 | 0.8909 | 37.4 / 43.8 / 16.7 / 2.0 | 0.0 |

Rejected after testing: rule E, post-result manual cancel as a mechanism, equal medals.
Additional reference (Crossref, 2026-11-13): Biró, P., Fleiner, T., Irving, R. W. & Manlove, D. F. (2010). The
College Admissions problem with lower and common quotas. *Theoretical Computer Science* 411(34–36).
doi:10.1016/j.tcs.2010.05.005

## G-H. Reducing luck

See `docs/fable/04_GH_REDUCING_LUCK.md` (separate file: this memo is at its length cap).
