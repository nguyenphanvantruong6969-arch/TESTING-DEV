# G-H. Reducing the role of luck (first pass: top 3 methods, 2026-11-13)

> Continuation of `docs/fable/03_RESEARCH_MEMO.md` (kept in a separate file because that memo is at its 400-line
> cap). Research role only (CLAUDE.md rule 11); no production code changed.
> **Every number here is SIMULATED (SỐ LIỆU MÔ PHỎNG)**. Evidence and options only; conclusions are Truong's.
> Truong's four G-A.2 decisions are still open, so every scenario is shown for both medal defaults D0 and D1.
> Constraint: students enter only what they enter today.

Script: `du_lieu_test/fable_gh_giam_may_rui.py` (`kiem`, `bang`, `doi_cho`). It carries a small research DA so
that per-club lotteries and non-integer scores can be measured; `kiem` shows it reproduces `chay_fa_daa` exactly
under production settings (7,200 student-days, 0 differences). Model = `sinh_truong` of G-A.2: 800 students, 3
days, 7 clubs/day (1 FREE, 2 LIMITED, 4 SELECTIVE, pass mark 5), lists of 6, non-FREE seats = 70 % of students.
Profile: `luoi` and `that_tha` keep default medals, the 20 % `chien_luoc` use the informed rule `gan_toi_uu`.
"Lottery loss" = the student was rejected somewhere and the lottery number was the first thing that separated
them from the last admitted student.

## H.1 Main table (10 data seeds × 3 days) — SỐ LIỆU MÔ PHỎNG

| scenario | medals | rejections per 100 student-days | decided by SCORE / MEDAL / LOTTERY % | % student-days with a lottery loss | % students with a lottery loss on 2–3 days | % true NV1 | mean utility | utility luoi / that_tha / chien_luoc | bottom 10 %: 3-day utility |
|---|---|---|---|---|---|---|---|---|---|
| S0 baseline (equal seats, integer score, one lottery per day) | D0 | 120.5 | 31 / 44 / 25 | 28.0 | 21.4 | 28.6 | 0.5452 | 0.467 / 0.564 / 0.613 | 0.883 |
| S0 | D1 | 126.0 | 34 / 31 / 35 | 38.5 | 33.5 | 25.3 | 0.5399 | 0.481 / 0.561 / 0.576 | 0.928 |
| S1 same total seats, split by THIS term's first-choice demand | D0 | 69.6 | 27 / 38 / 35 | 20.7 | 14.9 | 47.3 | 0.6108 | 0.543 / 0.625 / 0.675 | 1.024 |
| S1 | D1 | 78.7 | 35 / 39 / 26 | 19.5 | 10.9 | 42.9 | 0.6018 | 0.558 / 0.614 / 0.636 | 1.055 |
| S2 same total, split by demand of another cohort ("last term") | D0 | 69.6 | 30 / 38 / 33 | 20.0 | 14.6 | 47.1 | 0.6108 | 0.543 / 0.625 / 0.675 | 1.023 |
| S2 | D1 | 78.8 | 35 / 39 / 26 | 19.7 | 11.2 | 42.9 | 0.6020 | 0.558 / 0.615 / 0.636 | 1.060 |
| S3 only increases: +15 % seats, given to over-demanded clubs | D0 | 88.5 | 25 / 44 / 31 | 24.2 | 15.1 | 37.0 | 0.5805 | 0.495 / 0.605 / 0.647 | 0.942 |
| S3 | D1 | 93.5 | 28 / 34 / 39 | 32.0 | 25.3 | 32.7 | 0.5745 | 0.514 / 0.597 / 0.609 | 1.011 |
| S4 score reported in steps of 0.5 | D0 | 121.0 | 37 / 41 / 22 | 24.9 | 17.8 | 28.0 | 0.5440 | 0.469 / 0.562 / 0.610 | 0.881 |
| S4 | D1 | 126.4 | 39 / 28 / 33 | 36.2 | 30.1 | 24.8 | 0.5387 | 0.481 / 0.559 / 0.574 | 0.923 |
| S5 score in steps of 0.1 | D0 | 121.7 | 41 / 39 / 20 | 23.7 | 16.9 | 27.5 | 0.5432 | 0.471 / 0.560 / 0.608 | 0.881 |
| S5 | D1 | 126.9 | 43 / 26 / 31 | 34.5 | 28.6 | 24.3 | 0.5380 | 0.482 / 0.558 / 0.572 | 0.924 |
| S6 one lottery number PER CLUB (multiple tie-breaking) | D0 | 120.4 | 31 / 43 / 25 | 28.1 | 21.1 | 28.5 | 0.5452 | 0.466 / 0.565 / 0.613 | 0.885 |
| S6 | D1 | 126.1 | 33 / 32 / 35 | 38.4 | 34.2 | 25.2 | 0.5394 | 0.480 / 0.560 / 0.577 | 0.919 |
| S7 = S2 + S5 | D0 | 70.2 | 41 / 32 / 27 | 17.8 | 12.7 | 46.1 | 0.6093 | 0.542 / 0.623 / 0.675 | 1.015 |
| S7 | D1 | 80.5 | 47 / 33 / 21 | 16.5 | 8.4 | 41.5 | 0.5995 | 0.556 / 0.612 / 0.633 | 1.050 |

In S4/S5/S7 the pass/fail filter still uses the integer score, so the same students are eligible in every row.

**Improvement cycles after DA (Erdil & Ergin 2008), measurement mode, label "không bảo đảm ổn định" — SỐ LIỆU MÔ PHỎNG.**

| seats | % student-days that move to a higher-ranked club | % true NV1 before → after | mean utility before → after |
|---|---|---|---|
| equal (C0) | 0.2 | 28.6 → 28.6 | 0.5452 → 0.5454 |
| by last term's demand (C2) | 0.3 | 47.1 → 47.2 | 0.6108 → 0.6110 |

From G-A.2 (same model, D0, all default): block-rotated lottery across days changes "% students with a lottery
loss on all 3 days" 2.9 → 2.0 and "% in the worst lottery third on all 3 days" 3.6 → 0.0, mean utility unchanged.

## H.2 Ranked methods

| # | Method | Lottery-loss student-days (D0 / D1) | True NV1 (D0) | Stable | Truthful ranking | Invariant touched | Cost | Evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | Seats split by demand, same total (S1/S2) | 28.0 → 20.0 / 38.5 → 19.7 | 28.6 → 47.1 | yes (capacity is an input of DA) | S2: yes. S1: seats depend on this term's reports (see H.3) | none on priority (inv. 2 covers the priority key); inv. 1 untouched (capacity is data) | S (report + teacher step) | table H.1 |
| 1b | Only-increase variant, +15 % seats (S3) | 28.0 → 24.2 / 38.5 → 32.0 | 28.6 → 37.0 | yes | as S1 | none | S; needs rooms/teachers | table H.1 |
| 2 | Finer score from answers already collected (S5) | 28.0 → 23.7 / 38.5 → 34.5 | 28.6 → 27.5 | yes | yes (score is not a report) | D7 (integer 0–10) is a project decision, not an invariant; CSV contract unchanged if `score_k` already holds decimals (to confirm) | M (grading rule, D11 check) | table H.1 |
| 3 | Block-rotated lottery across days | all-3-days losers 2.9 → 2.0 % | unchanged | yes | yes (uses no report, no outcome) | inv. 3: new derivation of per-day numbers → new option, default off | M | G-A.2 table |
| – | Lottery per club (S6) | 28.0 → 28.1 | unchanged | yes | yes | inv. 3 | M | no measurable effect |
| – | Improvement cycles after DA | not a lottery-share lever | +0.0 to +0.1 pt | constrained-stable only | **no** (see H.3) | inv. 8 label | exists (measurement) | 0.2–0.3 % of student-days move |
| – | D1 vs D0 medals | D1 is higher at equal seats (38.5 vs 28.0), about equal once seats follow demand (19.7 vs 20.0) | lower under D1 | yes | yes | see G-A.2 | – | table H.1 |

Combination S7 (seats by last term's demand + score step 0.1): lottery-loss student-days 28.0 → 17.8 (D0) and
38.5 → 16.5 (D1); students with a lottery loss on 2–3 days 21.4 → 12.7 % (D0) and 33.5 → 8.4 % (D1).

## H.3 Proof sketches, counter-arguments and limits

- **Seats (method 1).** DA takes capacities as given, so stability and truthful ranking hold for any capacities
  fixed before the run. With S2 (last term's registrations) nothing a student reports this term moves a seat.
  With S1 a student's first choice moves a fraction of a seat (1 of ~130 first choices per club in this model):
  a channel exists in principle; it was not searched for profitable cases here. The model's "last term" is a
  different cohort facing the SAME club popularity, which is optimistic; drift between terms was not simulated.
  Teachers may only increase seats after registration opens (`kiem_chi_tang`); S1/S2 lower some clubs, so they
  are planning rules for BEFORE opening; S3 is the only-increase form and gives about half of the effect.
- **Finer scores (method 2).** Fewer ties at SELECTIVE clubs: the score's share of decisions goes 31 → 41 %,
  the lottery's 25 → 20 %. It does nothing at LIMITED clubs (no test). Welfare does not move; what changes is
  which students win. Limits: in this model the test has noise of ±1 point, so a 0.1 difference is mostly
  noise: luck moves from a visible lottery to an invisible one. Finer steps also magnify any difficulty gap
  between quiz variants (D11). Whether the Forms export keeps per-question data and completion time
  (`_thoi_gian_lam_bai` exists in the converter) was not checked; using time as a tie-break would reward speed
  and device quality and is not proposed.
- **Tie-breaking design (families 2 and 3).** One lottery per club was expected to spread bad luck
  (Ashlagi & Nikzad 2020; Arnosti 2023 compare the two designs); in this model medals already break most ties
  club by club and no difference appears. Improvement cycles recover almost nothing here for the same reason
  (0.2 % of student-days), and no strategy-proof mechanism can improve on DA with tie-breaking for everyone
  (Abdulkadiroğlu, Pathak & Roth 2009), so they stay in measurement mode. Efficiency-adjusted DA (Kesten 2010)
  and TTC-style exchanges give up stability or need consent; not simulated in this pass.
- **Compensation across terms / `stb_co_bu`.** Any rule that improves a student's lottery after a loss reads an
  outcome the student can cause on purpose (rank an over-demanded club first, lose, collect the credit); that is
  the measured failure of `stb_co_bu`. Block rotation avoids it because the rotation is fixed before any report.
- **Luck that cannot be removed.** At a LIMITED club the only data are medals and the lottery. Two students with
  the same medal are, for the school, equally entitled; any non-random order needs a criterion someone must
  justify (attendance last term would read a previous outcome → invariant-2 exception). In the best scenario
  measured (S7) the lottery still decides 21–27 % of rejections.

## H.4 Recommendation (operational; items and acceptance tests)

- **This semester, no algorithm change:** before opening registration, set seats from last term's first-choice
  demand where rooms allow (existing `bang_nhu_cau` / `goi_y_chi_tieu`, item G-D / GAP-7), and after
  registration closes use the only-increase step for over-demanded clubs. `kiem_nhan`: the demand table shows,
  per club, seats, first-choice demand and the gap; a run with changed seats passes `kiem_chi_tang`; default
  results byte-identical when seats are unchanged (invariant 1).
- **Later (needs Truong's decision on D7):** finer score reporting for SELECTIVE clubs, only together with the
  D11 variant-fairness check. `kiem_nhan`: same pass/fail set as the integer score; share of LOTTERY reasons at
  SELECTIVE clubs reported before/after on simulated data; priority key unchanged in form.
- **Later, low priority (new item, invariant 3):** block-rotated per-day lottery as an option, default off.
  `kiem_nhan`: derived only from the locked lottery and the seed; same seed → same numbers; no student in the
  worst third on every day; single-day data byte-identical to today.
- **Not recommended:** per-club lottery; improvement cycles in the placement path; compensation credit that
  reads outcomes.

Not done in this pass (ask before continuing): term-to-term drift of demand; search for profitable misreports
under S1; EADA / TTC measurement; signal rules other than D0–D3; pass-rate and seat-ratio sensitivity.

## References (checked on Crossref, 2026-11-13)

- Abdulkadiroğlu, A., Pathak, P. A. & Roth, A. E. (2009). Strategy-proofness versus Efficiency in Matching with
  Indifferences: Redesigning the NYC High School Match. *American Economic Review* 99(5). doi:10.1257/aer.99.5.1954
- Erdil, A. & Ergin, H. (2008). What's the Matter with Tie-Breaking? Improving Efficiency in School Choice.
  *American Economic Review* 98(3). doi:10.1257/aer.98.3.669
- Ashlagi, I. & Nikzad, A. (2020). What matters in school choice tie-breaking? How competition guides design.
  *Journal of Economic Theory* 190. doi:10.1016/j.jet.2020.105120
- Arnosti, N. (2023). Lottery Design for School Choice. *Management Science* 69(1). doi:10.1287/mnsc.2022.4338
- Kesten, O. (2010). School Choice with Consent. *Quarterly Journal of Economics* 125(3).
  doi:10.1162/qjec.2010.125.3.1297

AI log note (for Truong to copy if he wishes): 2026-11-13, Claude (research role): wrote
`du_lieu_test/fable_gh_giam_may_rui.py`, measured eight luck-reduction scenarios and improvement cycles on
simulated school-size data, wrote this file. No production code changed; no report text written.
