# FA-SC crisis memo: human error in one allocation round (step 1, catalogue)

> Written 2026-11-14 by the Fable research session, branch `claude/fable-fa-sc`. English on purpose.
> Item: **FA-SC** (new, outside the registry, approved D-SC1). Brief: `docs/fable/05_CRISIS_BRIEF.md`.
> Status: steps 1–5 of brief §4 done (catalogue, drills, remedy tables, runbook draft). Decisions D-SC2…7 and every
> sub-item FA-SC-n still wait for Truong; nothing is implemented.
> No production code was changed. No real student data was used.
> **Every S / O / D score below is an ASSUMPTION made by the AI, not a measurement.** Drill numbers (§6) come from
> 120 fake students generated with a seed: **SỐ LIỆU MÔ PHỎNG** (simulated), never a real survey.
> Interpretation and conclusions for the project report are Truong's to write; this memo gives evidence and options.

## 1. Method

- FMEA-style scoring, one row per failure: severity **S** (1–5, harm to one real student this semester),
  occurrence **O** (1–5, how often per round at ~800 students; assumption), detectability **D** (1–5; 5 = nobody
  notices before the student is harmed). **RPN = S × O × D**; ties broken by S. A change of ±1 in any O reorders
  the top of the list, so the ranking is a reading aid, not a result.
- Sources of the method (checked against Crossref on 2026-11-14):
  DeRosier, Stalhandske, Bagian & Nudell (2002), "Using Health Care Failure Mode and Effect Analysis: The VA
  National Center for Patient Safety's Prospective Risk Analysis System", *Joint Commission Journal on Quality
  Improvement* 28(5), 248–267, doi:10.1016/S1070-3241(02)28025-6.
  Reason (2000), "Human error: models and management", *BMJ* 320(7237), 768–770, doi:10.1136/bmj.320.7237.768
  (layered defences, "Swiss cheese"). Used here as: prevent / detect / recover are three separate layers.
- Why students misreport even when truth-telling is safe (relevant to S9, S33): Chen & Sönmez (2006), "School
  choice: an experimental study", *J. Economic Theory* 127(1), doi:10.1016/j.jet.2004.10.006; Hassidim, Marciano,
  Romm & Shorrer (2017), "The Mechanism Is Truthful, Why Aren't You?", *AER P&P* 107(5), doi:10.1257/aer.p20171027.
- Evidence tags: **[code]** read in the code this session (function named); **[doc]** stated in a project doc;
  **[hyp]** not verified, to be tested by a drill in step 3.
- Two registration paths exist and fail differently: **path A** = Power Apps + SharePoint List (not in the repo, D8
  undecided); **path B** = Microsoft Forms registration (3 required choices per day, student **types** the student ID,
  resubmission allowed, last submission counts).

## 2. Facts verified in code that drive the scores

| # | Fact | Where |
|---|---|---|
| F1 | Test of a club the student did not rank: score kept in `BANG_DIEM.xlsx`, not loaded, one warning. Test of a ranked but unticked club (path A): same. | `phan_tich_chi_thi` |
| F2 | Ranked SELECTIVE club without a loaded test: warning `NOT_ATTEMPTED`, student is not considered there. F1 and F2 are two unrelated lines in a long list; nothing links them to "this student probably took the wrong test". | `chuyen_fa_daa` |
| F3 | Two test responses from one email in one file: FIRST kept. Registration (path B): LAST kept, per day. List (path A): last save kept, DRAFT rows dropped. | `phan_tich_chi_thi`, `doc_dang_ky_fa_forms`, `_loc_dong_fa` |
| F4 | Test email not in the registration data: whole response dropped, warning only. | `phan_tich_chi_thi` |
| F5 | Path B: the student ID is free text. Two emails typing the same ID give two workbook rows with one ID; the kiosk refuses the whole workbook (`so_nhap_hs_trung`). A typo matching nobody is accepted as a new identity. | `doc_dang_ky_fa_forms`, `so_nhap.py` |
| F6 | Path B: a duplicate club in choices 1–3 is dropped with a warning; an invalid medal answer falls back to the default with a warning. The student is never told. | `doc_dang_ky_fa_forms`, `dat_huy_chuong_duong_b` |
| F7 | FA pre-run check: every `fa_*` error except two reserved-seat warnings **blocks the whole run** (missing FREE club, SELECTIVE club with registrants and zero scores, any invalid medal value). | `kiem_truoc_fa`, `kiem_fa_tu_csdl`, `MA_CANH_BAO` |
| F8 | Attendance: changing ONE dropdown saves at once (no confirmation). The second unexcused absence writes `release` and immediately invites the next waitlisted student, in the same transaction. `KIND` has no kind that reverses a release or an accepted invitation. | `js/10_theo_doi.js`, `luu_diem_danh`, `moi_tiep`, `fa_sau_xep.KIND` |
| F9 | Invitation answers (`nhan` / `tu_choi` / `het_han`) are entered by the admin; no student channel, no stored deadline. Accepting frees the old seat and invites the next student for it at once. | `tra_loi_moi` |
| F10 | Complaint ID match: exact, else case/space-insensitive only if exactly one student matches; otherwise rejected. Window = `run_at` + 3 days, Forms completion time used. One pending complaint per (student, day). Accepting only logs `appeal_rerun`; data is fixed by hand, then a normal rerun. | `khop_ma_hoc_sinh`, `_them_khieu_nai`, `xu_ly_khieu_nai` |
| F11 | "Too fast" flag = under 1/3 of the club's median time. With ≥ 2 variants a retake **replaces** the first score whenever the first was flagged and the retake variant matches, whichever score is higher. | `co_nhanh_qua`, `chuyen_fa_daa` (FA-S1) |
| F12 | Result→email join is by student ID only; a missing ID gives an empty Email and a warning; a wrong but existing ID is not detectable. | `ghep_ket_qua_email.ghep` |
| F13 | Lottery redraw needs `force_redraw_stb=True` (two-step in the UI); workspace delete needs typing `XOA`, moves to a bin, and refuses the open workspace. | `_run_pipeline_da_khoa`, `delete_workspace` |
| F15 | Multi-day runs use `stb_ngay`: each day's order is `shuffle(range(n))` over the base order, seeded by (seed, day). When the number of students **n** changes (late arrival, deletion), every day's order among the EARLIER students is re-derived. The base lottery keeps their relative order (invariant 3 as tested), the per-day order that actually decides ties does not. Single-day runs are not affected. | `sinh_stb_theo_buoi`; drills d12, d16 |
| F14 | A student who never registers is not in the workbook, so not in the kiosk: no placement and no FREE fallback (drill d01). A student who registers some days but misses one IS in the data and is put into a FREE club on the missed day, with no warning (drill d02). `danh_sach_chua_dang_ky.py` lists them per class (TH, never tried on real Microsoft). | `chuyen_fa_daa`, `danh_sach_chua_dang_ky.py` |

## 3. Student-side catalogue (S1–S29 from the brief, S30–S48 added)

Columns follow brief §3, plus D and RPN. "B/A" = before / after results. "Manip." = can a student fake this case
to gain? "Inv." = invariant touched by the proposed fix ("–" = none). Owners: ST student, CT club teacher,
GV homeroom teacher (GVCN), ECA teacher, IT, SW software. Proposed items are listed in §8.

| id | stage | what happens | S | O | D | RPN | detected today by | prevent | detect | recover | owner | B/A | manip. | inv. | item |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | test | Takes the wrong club's test; intended club reads NOT_ATTEMPTED | 4 | 3 | 3 | 36 | two unlinked warnings (F1, F2) | app shows only ticked clubs; club name in large type on the first form page; no shared links | converter pairs "test without rank" + "NOT_ATTEMPTED" for one student into one line "likely wrong test" | before lock: club teacher reopens (D-SC2); after results: only with Forms timestamp evidence | CT, IT, SW | B | medium: a student who failed test X claims "wrong test" to get a second try; limit to cases where no response exists for the intended club | – | FA-SC-3, FA-SC-4 |
| S2 | registration | Ticks the wrong club, swaps NV1/NV2, wrong day | 4 | 3 | 5 | 60* | nothing (valid data) | confirmation screen / receipt before lock | per-student receipt read by the student (FA-SC-2) | free edit until lock; nothing after results (D-SC3) | ST, GV | B | high after results (regret looks the same); none before lock | – | FA-SC-2 |
| S3 | test | Submits early, timer ends, network drops, "Đã làm" late | 3 | 3 | 3 | 27 | low score only; `BaiThi` cross-check lists missing submissions (Q4c) | tell students the status can lag minutes; "Làm mới" button; timer stated before start | club teacher sees a very short or blank response | retake on a different variant only if the first was flagged too fast (F11); otherwise policy D-SC2 | CT, ECA | B | medium (blank submit to see the questions, then ask for a retake): require a different variant | – | FA-SC-3 |
| S4 | registration | Determination points do not sum to 100 (old two-fund mode) | 2 | 2 | 1 | 4 | converter warning, kiosk blocks the run | app validation | already loud | fix in the Management tab | IT | B | none | 5 | D-SC4 |
| S4b | registration | Any single invalid medal value (path A, if the app lets it through) blocks all ~800 (F7) | 2 | 2 | 1 | 4 | `fa_huy_chuong_*` error, run blocked | app validation; path B cannot produce it (F6) | already loud | fix the one student, rerun; or quarantine (D-SC4) | IT | B | none | 5 | D-SC4 |
| S5 | test | Uses a personal or other account; email not in the List; response dropped (F4) | 4 | 3 | 4 | 48 | IT-only warning; student learns at results | "Only people in my organization" (already); first test question shows "you are signed in as …" reminder | list of dropped emails sent to club teachers before lock | before lock: match by hand with teacher sign-off, logged; after: complaint type "mất bài thi" | ST, CT, IT | B | medium: claim a friend's better response as one's own; require the account owner to confirm | – | FA-SC-2, FA-SC-3 |
| S6 | after results | Claims "I misclicked" to get a better club | 3 | 3 | 2 | 18 | complaint form says data errors only | publish the rule before registration | – | accept only what a timestamped record proves (D-SC3) | ECA | A | this IS the manipulation case | – | FA-SC-8 |
| S7 | registration | Medal default vs override chosen by mistake | 3 | 3 | 5 | 45 | nothing (valid); invalid answer falls back silently (F6) | plain wording; show the resulting three medals back | receipt shows medals (FA-SC-2) | resubmit before lock (path B) / swap UI (path A) | ST | B | none before lock | 2 (unchanged: key reads stored medals) | FA-SC-1, FA-SC-2 |
| S8 | before | Misses the announcement, absent for the whole window; never registers (F14) | 4 | 4 | 3 | 48 | `danh_sach_chua_dang_ky.py` + reminder flows (all TH) | reminders at −2 days and −3 hours; GV reads names in class | not-registered list per class before lock, signed by GV | late-arrival path (G1): insert into the locked lottery, rerun; or default into a FREE club [P] | GV, IT | B | low: arriving late on purpose gains nothing (random insertion) but can move others (G3) | 3, 4 | FA-SC-6, G1/G3 |
| S9 | before | Misunderstands the mechanism (ranks a "safe" club first, thinks NV1 is wasted) | 3 | 4 | 5 | 60* | nothing | one-page explainer + 3 worked examples; GV script | week-3 feedback question "hardest part" (after the fact) | none after results | ECA, GV | B | n/a | – | FA-SC-1 |
| S10 | before | No device, weak connection, disability, language barrier | 4 | 2 | 4 | 32 | not-registered list (S8) | school computer room slot; paper form entered by GV with the student present | same as S8 | same as S8; extra test time by a separate form copy [P] | GV, ECA | B | low | – | FA-SC-6 |
| S11 | registration | Ranks 1–2 clubs; ends in a FREE club never chosen (FA fallback) or unplaced (old mode) | 3 | 3 | 4 | 36 | path B forces 3 choices; fallback places the student | require ≥ 1 FREE club in the list or say plainly what the fallback does | receipt line "if all your choices are full you go to the least-full free club" | round 2 for leftover seats | ST, SW | B | none | – | FA-SC-1 |
| S12 | registration | Same club on two days, or a club not offered that day | 2 | 2 | 2 | 8 | converter drops the cell with a warning | per-day choice lists (already) | receipt | resubmit before lock | SW | B | none | – | FA-SC-2 |
| S13 | registration | Edits on two devices, session times out, draft lost | 3 | 3 | 4 | 36 | DRAFT rows dropped with a warning (path A) | app autosave message "not submitted yet" | reminder flow to DRAFT students (TH) | resubmit before lock | ST, IT | B | none | – | FA-SC-2 |
| S14 | registration | Parent or friend fills it in; copies a friend's list | 3 | 3 | 5 | 45 | nothing | explain that copying cannot help (own priority) | – | resubmit before lock | ST, GV | B | n/a | – | FA-SC-1 |
| S15 | registration | Edits after lock and believes it saved | 3 | 2 | 4 | 24 | Forms end date / app lock (TH) | lock message "closed at …, your last saved answer counts" | receipt sent after lock | none; complaint only for data error | IT | B/A | medium (claims the edit was made in time): Forms timestamp decides | – | FA-SC-2 |
| S16 | test | Opens the test, closes the tab, never submits | 3 | 3 | 3 | 27 | NOT_ATTEMPTED warning; reminder list `CanNhac` (TH) | "you must press Submit" on the last page | NOT_ATTEMPTED reminder −2 days / −3 hours | take it before the end date | ST, IT | B | none | – | FA-SC-1 |
| S17 | test | Takes a test before ranking that club, or wrong day / campus | 3 | 2 | 3 | 18 | F1 warning; campus warning with `--co-so` | close tests after registration (already advised) | linked warning (FA-SC-4) | rank the club before lock, score then loads on re-export | ST, IT | B | none | – | FA-SC-4 |
| S18 | test | Impersonation, answers shared, answers leaked by "Show results" ON | 4 | 2 | 4 | 32 | too-fast flag (F11); item analysis flags odd items | supervised sitting for SELECTIVE clubs; variants; settings checklist | time flag + identical-answer check [hyp] | retake on another variant, admin decision | CT, ECA | B | this is cheating itself | – | FA-SC-7 |
| S19 | test | Misreads the time limit or the gate question (answers "Không" and skips) | 3 | 3 | 3 | 27 | NOT_ATTEMPTED | one form per club has no gate question (Q4a) | reminder list | take the test before the end date | CT | B | low | – | FA-SC-1 |
| S20 | test | Gets a harder variant | 3 | 2 | 2 | 12 | variant comparison stops the converter until the admin chooses (D11) | equated variants | `DIEU_CHINH_BAN_DE.xlsx` | admin flag `--ap-dung-dieu-chinh` | IT, CT | B | low | – | existing (FA-M4) |
| S21 | test | Takes more than 5 tests; extras dropped | 2 | 2 | 3 | 12 | converter warning (keeps first 5) | app caps ticks at 5 | receipt lists which tests count | none needed | SW | B | low | – | FA-SC-2 |
| S22 | after | Never reads the result or the invitation; seat lost | 4 | 3 | 4 | 48 | nothing; admin types `het_han` (F9) | fixed, published reply deadline; two contact attempts via GV | list of invitations older than N days | re-invite only if the seat is still free | GV, IT | A | low | – | FA-SC-5 |
| S23 | after | Sick in week 1; marked unexcused twice; seat released and offered on (F8) | 5 | 3 | 3 | 45 | nothing; release is automatic | GV forwards sick notes to the club teacher; default mark "excused" when unsure | "pending release" list reviewed by the admin before it takes effect | needs a reversal kind in the log (F8) | CT, GV, SW | A | low (a note is checkable) | 4 (append-only kept) | FA-SC-5 |
| S24 | after | Swaps clubs informally with a friend | 2 | 3 | 4 | 24 | attendance mismatch | state that swaps are not recognised | attendance list vs members | both marked absent → released (see S23) | CT | A | high if allowed: pairs trade priority; keep forbidden | – | FA-SC-1 |
| S25 | after | Complaint with a mistyped ID, or after the window | 3 | 2 | 2 | 12 | ambiguous ID rejected (F10); late complaint rejected | Forms pre-fills from Email where possible | rejected list shown to the admin | GV re-files by hand within the rule | IT | A | low: fuzzy match needs exactly one hit | – | existing (FA-M6) |
| S26 | after | Moves class or campus, or withdraws then wants back | 3 | 2 | 3 | 18 | `doi_chieu_lists.py` shows class/campus changes | – | list diff before any rerun | withdrawal = G2; return = late arrival G1 (random lottery slot, may lose the seat) | IT | A | medium: withdraw and re-enter to redraw one's lottery position; keep the original number for returners [P] | 3 | G1, G2 |
| S27 | registration | Two students with the same name; an ID typo merges two people | 4 | 2 | 3 | 24 | duplicate ID blocks the import (F5); same name is harmless (key = email / ID) | see S30 | see S30 | see S30 | IT | B | none | – | FA-SC-4 |
| S28 | after | Leaves a shared computer signed in; another student sees or edits | 4 | 2 | 5 | 40 | nothing | sign-out reminder on the thank-you page; lab policy | last-modified time vs class timetable [hyp] | before lock: resubmit; after: complaint with evidence | ST, IT | B/A | medium (blames a "friend" for own regret) | – | FA-SC-1 |
| S29 | after | Rejected everywhere, misreads the sentence, distress | 4 | 3 | 4 | 48 | week-3 survey (late) | GV script: what the reason codes mean, what to say | GV flags students placed by fallback or with no ranked club | round 2 seats; named adult follows up | GV, ECA | A | n/a | – | FA-SC-9 |
| **S30** | registration | Path B: mistypes own student ID (F5). Collision → whole workbook refused; no collision → placed under a wrong identity, no class, result reaches nobody | 4 | 4 | 3 | 48 | collision: loud error; no collision: nothing | do not ask for the ID: derive it from Email via the school roster; or validate against the roster in the converter | converter flags IDs not on the roster and IDs used by two emails, before writing the workbook | IT corrects from the roster, logged | SW, IT | B | none | 7 (no CSV change needed) | FA-SC-4 |
| **S31** | registration | Resubmits registration after taking tests (last counts, F3): tested club no longer ranked, new SELECTIVE club has no test | 4 | 3 | 3 | 36 | F1 + F2 warnings, unlinked | close registration before tests open, or warn on resubmit | converter line "choices changed after test date" from the two timestamps | before lock: take the missing test | ST, IT | B | low | – | FA-SC-4 |
| **S32** | registration | Path B: picks the same club in two of the three choices; list shrinks to 2, medals shift (F6) | 3 | 3 | 4 | 36 | IT-only warning | Forms cannot block it (TH); wording "three DIFFERENT clubs" | receipt | resubmit before lock | ST | B | none | – | FA-SC-2 |
| **S33** | registration | Ranks a FREE club above the clubs really wanted. FREE never rejects, so every choice below it and its medals are dead | 3 | 3 | 5 | 45 | nothing | one sentence in the form: "a free club always accepts you; put it last unless it is your favourite" | converter note "FREE club ranked above a SELECTIVE club the student tested for" | resubmit before lock | ST, SW | B | none | 2 (a note, not a priority input) | FA-SC-1, FA-SC-4 |
| **S34** | test | Honest fast finisher is flagged; a retake replaces the first score even if lower (F11). Mirror case: a weak student answers fast on purpose to earn a retake | 3 | 2 | 4 | 24 | flag in warnings | policy choice D-SC6: keep first / keep higher / replace (today's code) [P] | list of flagged students per club to the club teacher | admin decision logged | CT, ECA | B | medium (deliberate fast fail) | – | FA-SC-3 |
| **S35** | test | Takes a variant not assigned (link passed on by a friend) | 2 | 3 | 2 | 12 | warning "làm đề B nhưng đề giao A — admin quyết định" | app opens the assigned variant only | already flagged | rule needed: keep the score or void it [P] | CT | B | medium (choose the variant friends say is easier) | – | FA-SC-3 |
| **S36** | registration | Per-day forms (5 links): misses one day's form; silently placed in a FREE club that day (d02), no warning | 3 | 3 | 5 | 45 | "no choices on any day" only when ALL days are empty | one form for all days (option already built) | converter lists students missing a day that has clubs | before lock: submit that day; after: late-arrival path | SW, GV | B | low | – | FA-SC-4, FA-SC-6 |
| **S37** | test | Shared device still signed in as a schoolmate: the score is recorded under the OTHER student, used for them if they ranked the club, and their own attempt is blocked by "one response" | 4 | 2 | 5 | 40 | nothing (valid email in the List) | form's first question: "type your own class and name" as a cross-check field | converter compares the typed name with the roster name for that email | both students confirm with the club teacher; response reassigned by hand, logged | CT, IT | B | high: two friends agree to "swap" so the stronger one sits both tests; needs both to confirm AND supervised sitting for SELECTIVE clubs | – | FA-SC-4 |
| **S38** | after | Says yes to an invitation to the club teacher; nobody records `nhan`; later typed as expired (F9) | 4 | 2 | 4 | 32 | nothing | single reply channel (a 1-question Form with Record name) | admin screen lists pending invitations with age | re-invite only if the seat is still free | CT, IT | A | low | – | FA-SC-5 |
| **S39** | after | Accepts or declines an invitation by mistake; old seat is offered on at once; no reversal kind (F8, F9) | 4 | 2 | 3 | 24 | nothing | confirm step naming both clubs; 24 h cooling-off before the vacated seat is offered | – | reversal kind while the vacated seat is still unclaimed | SW, IT | A | medium (accept, regret, undo = free option); allow one undo, inside the cooling-off only | 4 | FA-SC-5 |
| **S40** | after | Goes to the wrong club or room in week 1 (similar names, FREE room groups); absent twice at the right one; released | 4 | 2 | 4 | 32 | nothing | class file states day, club, room group | club teacher reports "student not on my list" | same as S23 | GV, CT | A | low | – | FA-SC-5, FA-SC-1 |
| **S41** | after | Files the complaint for the wrong day, or uses it to say "unfair" | 2 | 3 | 2 | 12 | one pending per (student, day); form states data errors only | day shown as a choice list with club names | admin sees the result for that day beside the complaint | reject with a reason; re-file within the window | IT | A | low | – | existing (FA-M6) |
| **S42** | registration | Club officer with a reserved seat forgets to rank their own club; reservation silently unused | 4 | 2 | 4 | 32 | IT-only warning `fa_giu_cho_khong_xep_clb` (not blocking, F7) | club teacher tells officers to rank the club | this warning sent to the club teacher before lock | resubmit before lock | CT, IT | B | none | – | FA-SC-4 |
| **S43** | registration | Gold medal on a club that later closes for low demand (D3); medal wasted [hyp: are medals re-defaulted after closing?] | 3 | 2 | 4 | 24 | reason `CLUB_CLOSED` | publish minimum numbers; demand review before lock | – | [hyp] to drill | ECA, SW | B/A | low | 2 if medals were re-derived | to drill |
| **S44** | registration | Late arrival's choices are typed by IT from speech or paper; transcription slip | 4 | 2 | 4 | 32 | nothing | student sits beside IT and reads the screen | printed receipt signed by the student | fix + rerun, same lottery | IT | B/A | low | 3, 4 | FA-SC-7 |
| **S45** | after | No class on record: result lands in `_chua_co_lop.xlsx`, which no homeroom teacher receives. Path B sets class empty for every student [code: `doc_dang_ky_fa_forms`]; drill d14: 120 of 120 students without a class, the export writes only `_chua_co_lop.xlsx` | 4 | 4 | 3 | 48 | kiosk counts students without a class | roster with class loaded before export | non-empty `_chua_co_lop.xlsx` blocks "send" in the checklist | IT assigns the class, re-export | IT | A | none | – | FA-SC-7 |
| **S46** | after | Quietly stops attending; seat idle 2–3 weeks while others wait | 2 | 3 | 3 | 18 | attendance rule | one-click "I give up my seat" channel | attendance | waitlist invitation | ST, CT | A | low | – | G2 |
| **S47** | before | Misreads the deadline (dd/mm vs mm/dd, "end of day" vs 00:00) | 3 | 3 | 3 | 27 | reminder flows (TH) | write the deadline as weekday + date + hour | not-registered list at −3 h | late-arrival path | ECA | B | low | – | FA-SC-1 |
| **S48** | registration | Confuses two clubs with similar names, or the same club on two days | 3 | 2 | 4 | 24 | F1 + F2 if a test is involved | club names made distinct; day shown in every option | linked warning (FA-SC-4); receipt | resubmit before lock | CT, SW | B | low | – | FA-SC-2 |

\* S2 and S9 score highest by RPN but cannot be told apart from a deliberate choice, so no detection or recovery
exists by construction; they are handled as prevention only and kept out of the top 5 in §5.

## 4. Teacher and IT catalogue (scores only; remedies in step 4)

| id | actor | error | consequence for the student | detected today by | S | O | D | RPN |
|---|---|---|---|---|---|---|---|---|
| T1 | CT | Wrong key in Forms / in `de_thi.json` | Forms: none (rescoring). `de_thi.json`: whole club ranked on wrong scores | Forms vs rescoring mismatch warning; item analysis flags low-% items [code]; a wrong key that looks plausible: nothing | 4 | 2 | 4 | 32 |
| T2 | CT | Record name OFF / One response OFF / Show results ON / `[mã]` deleted / end date wrong | no email → all responses dropped; retakes; leaked answers | "phiếu không có Email" warning; first-response rule; "thiếu câu" error; Show results: nothing | 4 | 3 | 3 | 36 |
| T3 | CT / IT | Capacity typo (3 for 30), wrong pass mark | up to 27 students displaced, all with valid explanations | demand table (`bang_nhu_cau`) if someone reads it; after results only increases allowed (`kiem_chi_tang`) | 5 | 2 | 3 | 30 |
| T4 | CT | Attendance dropdown slip | seat released and offered on at once, no reversal (F8) | nothing | 5 | 3 | 3 | 45 |
| T5 | GV | Forwards the class file to the wrong class or to students | other students' placements exposed (no scores or lottery numbers in the file [doc]) | nothing | 3 | 2 | 5 | 30 |
| I1 | IT | Exports before lock, stale List, forgets one club's file | late edits lost; a whole club NOT_ATTEMPTED | forgotten club: blocking error `fa_clb_tuyen_chon_chua_co_diem` (F7) and converter warning; forgotten variant-B file or stale List: nothing | 4 | 2 | 4 | 32 |
| I2 | IT | Wrong `--co-so`, wrong workspace, same file twice | students of one campus placed in the other's clubs | summary line to compare by eye; import is additive [doc] | 5 | 2 | 3 | 30 |
| I3 | IT | Skips the warning list | every "warning only" row above becomes silent | nothing | 4 | 4 | 4 | 64 |
| I4 | IT | Announces, then reruns with changed data | announced students moved (SIMULATED, earlier project file: 20 late arrivals moved 32.4 earlier students on average, 16.25 lost their seat, at capacity ratio 0.8) | `thay_doi_ket_qua.csv` if exported; yellow band | 5 | 3 | 2 | 30 |
| I5 | IT | Changes seed / redraws mid-round | every result changes | two-step confirmation, trace kept (F13) | 5 | 1 | 2 | 10 |
| I6 | IT | Deletes workspace, laptop lost | results gone; personal data exposed | delete goes to a bin (F13); off-machine backup: none found [hyp] | 5 | 1 | 3 | 15 |
| I7 | IT | Sends results while the yellow band shows | published result ≠ data | yellow band (advisory) | 4 | 2 | 3 | 24 |
| I8 | IT | Email↔ID file from another round or campus | a student sees another's result | missing ID warned; wrong-but-existing ID: nothing (F12) | 5 | 1 | 5 | 25 |

I3 is not a failure of its own but the multiplier behind the student rows: most detection today is one line in
a list that the operations guide itself calls "the most skipped step".

## 5. Ranking (top 10 by RPN, ties by S; assumptions, not measurements)

| rank | rows | failure | S | O | D | RPN |
|---|---|---|---|---|---|---|
| 0 | I4, F15 | Added after the drills: rerun with a changed head-count re-draws the per-day lottery; announced students move without cause (d16) | 5 | 4 | 3 | 60 |
| 1 | S8, S10 | Student absent from the data (never registered) → no placement, no fallback (d01) | 4 | 4 | 3 | 48 |
| 2 | S30, S27 | Path B: typed student ID wrong → import blocked for all, or wrong identity | 4 | 4 | 3 | 48 |
| 3 | S5, S37 | Test sat under the wrong account → score dropped, or credited to another student | 4 | 3 | 4–5 | 48 / 40 |
| 4 | T4, S23, S40 | Attendance slip → automatic release + automatic invitation, no reversal | 5 | 3 | 3 | 45 |
| 5 | S33, S7, S36 | Valid but self-defeating registration (FREE club first, medals misplaced, a day missed) with zero feedback (d02, d07) | 3 | 3 | 5 | 45 |
| 6 | S1, S31 | Wrong test / choices changed after testing (Truong's example) | 4 | 3 | 3 | 36 |
| 7 | T2 | Wrong Forms settings | 4 | 3 | 3 | 36 |
| 8 | S45 | Path B: no class → every result lands in `_chua_co_lop.xlsx` (d14); raised to RPN 48 after the drill | 4 | 4 | 3 | 48 |
| 9 | T3, I2, I4 | Capacity typo, campus mix-up, rerun after announcing (S = 5, lower O) | 5 | 2–3 | 2–3 | 30 |
| 10 | S22, S29 | Missed invitation; distress after rejection | 4 | 3 | 4 | 48† |

Ranks were set in step 1 and are not re-sorted: after the drills S45 joins the RPN-48 group and S36 moved from rank 1 to rank 5.
† S22 and S29 have RPN 48 but depend on post-result parts marked TH/undecided (D8); listed last until the channel is fixed.
Cross-cutting: I3 (RPN 64) raises D for ranks 2, 3, 5, 6.

## 6. Drill results (step 3) — SỐ LIỆU MÔ PHỎNG

Setup: `du_lieu_test/su_co/` (one script per drill, `--seed`, deterministic; run all with `chay_tat_ca.py`). Fake round:
120 students, path B (one registration file per day, three choices per day), 5 days × 3 clubs (SELECTIVE 20 seats with
pass mark 5, LIMITED 30, FREE), real converter `chuyen_fa_daa` and real kiosk `PipelineAPI` on a scratch database,
seed 42. "Others moved" = students other than the one at fault whose club differs from the clean run with the same seed.
Limits: one small sample set, one seed shown (seed 7 also ran; see `du_lieu_test/su_co/README.md`), path A not drilled.

| drill | rows | error injected | run blocked? | warning that names the case | effect on the student at fault | others moved |
|---|---|---|---|---|---|---|
| d01 | S8 | one student never registers | no | 0 | not in the kiosk; placed on 0 of 5 days | 37 (the first-run lottery is drawn over a different ID set; not a harm before the first run) |
| d02 | S36 | misses one day's form | no | 0 | placed in a FREE club on that day | 0 |
| d03a | S30 | types a classmate's ID | **yes, import refused for all 120** (`so_nhap_hs_trung`) | converter: 0; kiosk: 1 error | — | all (no run) |
| d03b | S30 | types an ID that matches nobody | no | 0 | all 5 results stored under the wrong ID, 0 under the real one; own club differs on 1 day | 7 |
| d04 | S5 | sits all tests under an outside account | no | 1 "email not in the list" + 5 NOT_ATTEMPTED, unlinked | loses the SELECTIVE seat won in the clean run | 1 |
| d05 | S37 | A's test recorded under schoolmate B | no | 0 about B; 1 NOT_ATTEMPTED for A | A: SELECTIVE → FREE; B: FREE → SELECTIVE (B gains A's seat) | 0 |
| d06 | S1 | takes club Y's test instead of X's | no | 2 separate lines among 8 | SELECTIVE → FREE | 1 |
| d07 | S33 | FREE club ranked first | no | 0 | SELECTIVE → FREE although the test score was 5/5 | — |
| d08 | T4, S23 | second "unexcused" mark by mistake, corrected at once | no (saved without confirmation) | 0 | seat released; 1 invitation issued to another student; after both cells are corrected the student is still out and the invitation is still live; log = `release`, `invite_offer`; `match_results` and `run_history` unchanged | 1 invited |
| d09 | T3 | capacity 2 instead of 20 | no | 0 new (6 before, 6 after) | — | 18 lose that seat; nothing flags the change |
| d10 | S4b | one invalid medal value (50) for one student | **yes** (`fa_huy_chuong_gia_tri_sai`), 1 of 120 at fault | 1 error | — | nobody placed; old results intact, no `run_history` row |
| d11 | T2 | Record name OFF on the test form | **yes** at run (`fa_clb_tuyen_chon_chua_co_diem`) | 120 "no Email" + 600 NOT_ATTEMPTED | — | all (no run) |
| d12 | I4 | 5 late students added after announcing, rerun | no | — | — | 20 earlier students change club, 11 of those cells drop from a seat-limited club to a FREE club; lottery order among earlier students kept (inv. 3), `run_history` = 2 rows (inv. 4) |
| d16 | I4, F15 | ONE late student who ranks the FREE club first on every day (takes no contested seat), rerun | no | — | — | **18 earlier students change club** (19 student-days) at seed 42; 38 and 30 at seeds 7 and 11. Base lottery order among earlier students kept; per-day order kept on **0 of 5 days** |
| d13 | I2 | same workbook imported twice | no | — | — | 0 (result identical) |
| d14 | S45 | path B has no class column | no | — | 120 of 120 without a class | export writes one file: `_chua_co_lop.xlsx` |
| d15 | inv. 5 | failure injected at the stability check during a rerun | run fails | 2 error codes | — | `match_results` and `run_history` unchanged; next run succeeds |

**Main finding of the drills (F15, d16).** After results are announced, any rerun in which the number of students
has changed re-draws the per-day lottery for everyone, so already-announced students move even when the newcomer
competes for nothing. This is outside "human error" but every recovery path in this memo that says "fix the data and
rerun with the same lottery" depends on it: with the same students the rerun is safe (d13, d15); with one student
more or fewer it is not. It also bears on invariant 3 as worded ("keeping existing students' relative order") and on
the operations guide §8. Seed-7 figures for d12: 51 earlier students moved, 27 student-days dropped to a FREE club.
No fix is proposed here beyond the options in §7; changing the derivation would change default results (invariant 1)
and needs Truong's decision.

What the drills changed against step 1: S36 is milder than assumed (FREE fallback covers a missed day) but fully
silent; S45 is confirmed and applies to every path-B student; d08 confirms F8 end to end; d13 and d15 found no
problem (double import is idempotent, a failed run leaves no trace). Not drilled: S31, S34, S35, S43 (need a
richer sample: more clubs per day, variants, minimum numbers), I8, T1, and everything on path A.

## 7. Remedy options for the top failures (step 4)

Cost: S = wording or checklist only; M = converter or script, no kiosk change; L = kiosk code. "Manip." as in §3.

| failure | option | layer | cost | who acts | invariant | manip. |
|---|---|---|---|---|---|---|
| Absent from data (S8, S10) | A. not-registered list per class, signed by GVCN before lock | detect | S (tool exists, TH) | GV, IT | – | none |
| | B. roster reconciliation in the converter: roster in, "not registered" sheet out | detect | M | IT | 7 holds (extra output only) | none |
| | C. policy: unregistered students get a FREE club by default (D-SC5) | recover | S + small M | ECA | 3 (must enter before the first run, else late-arrival path) | low |
| Wrong ID (S30) | A. do not ask for the ID; map Email → ID from the roster | prevent | M | IT | 7 | none |
| | B. converter checks typed IDs against the roster and for reuse, before writing the workbook | detect | M | IT | – | none |
| | C. keep today's behaviour, add a runbook step | recover | S | IT | – | none |
| Wrong account (S5, S37) | A. first test question "your class and full name", compared with the roster | detect | M | CT, IT | – | lowers the swap risk, does not remove it |
| | B. dropped-email list sent to club teachers before lock | detect | S | IT, CT | – | medium (claiming someone's response): owner must confirm |
| | C. supervised sitting for SELECTIVE clubs | prevent | S (organisational) | ECA | – | lowest |
| Attendance slip (T4, S23, S40) | A. release becomes "pending" and takes effect only when the admin confirms | prevent | L | SW | 4 holds (append-only) | none |
| | B. a reversal kind in `fa_dieu_chinh`, allowed while the invitation is unanswered | recover | L | SW | 4 holds | low |
| | C. rule: never choose "unexcused" when unsure; admin reviews before any invitation is passed on | prevent | S | CT | – | none |
| Self-defeating registration (S33, S7, S36) | A. one sentence in the form and in the GVCN script | prevent | S | ECA, GV | – | none |
| | B. per-student confirmation sheet before lock (FA-SC-2) | detect | M | IT, GV | 2 holds (shows stored data; feeds nothing back) | none before lock |
| | C. converter note "FREE above a tested SELECTIVE club", "day missing" | detect | M | IT | 2 holds if the note never enters the key | none |
| Wrong test (S1, S31) | A. one linked line per student in the converter | detect | M | IT | – | none |
| | B. correction window before lock, different variant, club teacher approves (D-SC2) | recover | S | CT | – | medium: only when no response exists for the intended club |
| | C. after results: accept only with Forms timestamps (D-SC3) | recover | S | ECA | 3, 4 (rerun keeps lottery, appends history) | high if widened |
| No class (S45) | A. load class from the roster before export | prevent | S–M | IT | – | none |
| | B. checklist line: "`_chua_co_lop.xlsx` empty before sending" | detect | S | IT | – | none |
| Capacity typo (T3) | A. club teacher reads capacities back and signs before the run | detect | S | CT | – | none |
| | B. kiosk warning when capacity is far below demand or last term's figure | detect | L | SW | – | none |
| One student blocks all (S4b, D-SC4) | A. keep blocking (today) | – | – | IT | 5 holds | none |
| | B. set the student aside, run the rest, report | recover | L | SW | 5 (validation step changes meaning: needs Truong's decision) | low: a student could opt out of the run on purpose; treat as not registered |
| Rerun after announcing (I4, F15) | A. freeze the list before the first run; publish once; handle late students by round 2 / waitlist, not by rerun | prevent | S | ECA | – | none |
| | C. derive each day's order per student (independent of the head-count), behind a new parameter that defaults to today's behaviour | prevent | L | SW | 1 (default unchanged), 3 (wording to be confirmed by Truong) | none found; to be analysed |
| | B. protect announced students (registry item G3) | prevent | L | SW | 8 (new choice function must pass the two tests) | to be analysed under G3 |

## 8. Proposed sub-items (each needs Truong's approval; none started)

| code | what | type | covers | acceptance test (`kiem_nhan`) sketch |
|---|---|---|---|---|
| FA-SC-1 | Student one-pager, GV script, form wording (FREE club, medals, deadline, "press Submit") | communication | S9, S11, S14, S16, S19, S24, S33, S47 | none (document); Truong writes any text that goes into the project report |
| FA-SC-2 | Per-student "phiếu xác nhận" produced by the converter before lock, one file per class: choices per day, medals, which tests were received and count | software (converter only) | S2, S5, S7, S12, S13, S15, S21, S32, S48 | on `demo_t4m.py --day-du` data: one row per student per day; a dropped test appears as "not counted + reason"; no other student's data in a class file; default mode output byte-identical (inv. 1) |
| FA-SC-3 | Correction window and retest rules before lock (D-SC2), logged | policy + doc | S1, S3, S5, S34, S35 | – |
| FA-SC-4 | Linked warnings in the converter: wrong-test pair, choices changed after test, ID not on roster / used twice, missing day, FREE above tested club, typed name ≠ roster name, unused reservation to the club teacher | software (converter only) | S1, S17, S30, S31, S33, S36, S37, S42 | each injected case in a fake export gives exactly one line naming the student and the action; clean data gives none; workbook unchanged byte for byte |
| FA-SC-5 | Post-result safety: release becomes "pending" until the admin confirms; reversal kind in `fa_dieu_chinh` (append-only kept); invitation deadline and reply channel | software (`fa_sau_xep`) | S22, S23, S38, S39, S40, T4 | a slip then correction leaves the student in the seat and issues no invitation; log shows both rows; `match_results` and `run_history` untouched (inv. 4) |
| FA-SC-6 | Roster reconciliation: every student on the school roster is registered or on a signed not-registered list; policy for the rest | process + small tool | S8, S10, S36 | on fake roster + export: missing students and missing days listed per class; zero when complete |
| FA-SC-7 | IT checklists with second-person sign-off for steps that cannot be undone | checklist | I1, I2, I7, I8, S44, S45, T2, T5 | – |
| FA-SC-8 | Rule for post-result claims (D-SC3) | policy | S6, S15, S28 | – |
| FA-SC-9 | Welfare follow-up for students placed by fallback or rejected everywhere | process | S29 | – |
| existing | G1/G2/G3 (late, withdraw, protect announced), FA-M4, FA-M6 | – | S26, S46, I4, S20, S25, S41 | – |

Invariant check for the proposals: FA-SC-2 and FA-SC-4 only add outputs beside the workbook (inv. 1 and 7 hold if
the workbook is unchanged); FA-SC-4 notes must never feed the priority key (inv. 2); FA-SC-5 adds kinds to an
append-only log and never edits `match_results` / `run_history` (inv. 4); any rerun after a correction keeps the
locked lottery (inv. 3) and the fixed pipeline order (inv. 5).

## 9. Open decisions for Truong (options only)

- **D-SC2** retake after a wrong test: (a) never; (b) before lock, club teacher approves, different variant;
  (c) also after results with timestamp evidence.
- **D-SC3** post-result claims: (a) data errors only (today); (b) plus slips proven by a system record.
- **D-SC4** one invalid student: (a) block all (today, F7); (b) set aside and report, run the rest.
- **New, D-SC5** not-registered students: (a) no club; (b) late-arrival path; (c) default into a FREE club.
- **New, D-SC6** flagged-fast retake: keep first / keep higher / replace (today).
- **New, D-SC7** per-day lottery after a head-count change (F15): (a) accept and never rerun after announcing;
  (b) open an item to make the per-day order stable for earlier students (touches invariants 1 and 3 as noted in §7).

## 10. To try on real Microsoft Forms (TH)

1. Path B form: can "three different clubs" be enforced, and does "Allow respondents to edit" exist in the tenant?
2. Does the quiz export keep submission order (the converter keeps the FIRST response per email)?
3. What happens when a club teacher deletes a response: can the student submit again under "One response per person"?
4. Lag of the "Đã làm" status flow under load; the 6,000 requests/day ceiling on the peak day.
5. A shared computer left signed in: which account does Forms record?

## 11. Limits

- Scores S / O / D are assumptions. Drills: one fake data set of 120 students, 3 clubs per day; they show what the
  software does with an injected error, not how often people make that error.
- Path A (Power Apps) is not in the repository: its client-side validation is assumed, not read.
- Still [hyp]: S43 (medals after a club closes), I6 (off-machine backup), S18 (identical-answer check).

## 12. Note for the AI log (what the AI did)

On 2026-11-14 the AI (research role) read the operations docs and the converter / post-allocation code, wrote this
catalogue of 48 student-side and 13 staff-side failure cases with assumed FMEA scores, wrote 16 drill scripts on
fake data under `du_lieu_test/su_co/` and ran them, and drafted remedy tables and a Vietnamese incident handbook
(`06b_SO_TAY_SU_CO.md`). It changed no production code and wrote no conclusions for the project report.
