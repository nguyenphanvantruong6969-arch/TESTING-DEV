# FA-DAA implementation plan (kiosk first, then Microsoft)

> Written by Opus, 2026-11-08 (revised after the council review the same day: D1, D3, D4, D5, D9, D11, D12, FA-9),
> branch `claude/keen-ride-72sa7t`. Source: `docs/ke_hoach/FA_DAA_VISION.md` (Truong's
> vision, cited as **V§n**). English (cheap). Night-run entry point: `docs/phien/CHAY_DEM_FA_DAA.md`.
> Every item below has a code `FA-*`, its parent registry item (A5, A6, A13, C3, Z6, A2) or T4M-NC (Microsoft
> track, outside the registry, already approved), its files, and its acceptance tests (`kiem_nhan`).
> All numbers produced by this plan are SIMULATED data. Never draft report commentary (academic integrity).

## 0. What already exists (do not rebuild)

| Vision piece | Already in repo | Gap |
|---|---|---|
| Student-proposing DA per day (V§8.1) | `run_rbda`, `run_rbda_nhieu_buoi`, mode `stb_ngay` = one STB permutation per day shared by all clubs (V§8.3) | none |
| Determination points (V§6.2) | A13 `wharton_bids(student_id, club_id, tier, points)`, `uu_tien_wharton`, key tier 1 `(0,-score,(),-w,stb,sid)`, tier 2 `(1,-w,stb,sid)` | two funds -> one fund of fixed medals 60/30/10 |
| Reserved seats (V§2 `reserved_student_ids`) | two-pass soft reserve, `is_reserve_eligible_fn(student, club)` is a callable | per-club reserved list |
| Pass mark filter (V§7.4) | registry A5 (hard filter before DA), not built | build, FA mode only |
| Min members (V§8.5) | registry A6, not built | build, FA mode only |
| Result reasons (V§9.1) | registry C3, not built; `get_diem_chuan`, `tinh_diem_chuan` give cut-offs | build |
| Reproducible lottery (V§8.3) | crc32 STB stored in `students.stb_number`, locked seed (`stb_lock`), `_seed_cua_buoi` | witnessed lottery record (D5, FA-9) |
| Microsoft path | T4M-NC: Power Apps "ECA" + SharePoint List (wide, NV1..NV7, THI1..7, WP1..7), Forms Quiz per club, converter `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`, IT build kit `tao_bo_dung_t4m.py` | medals, club types, setup form, results/feedback |

Key design choice: **no change to the DA core**. FA-DAA is a wrapper (new module `fa_daa.py`) that prepares the
inputs `run_rbda_nhieu_buoi` already accepts (clubs, preferences, tested_scores, `diem_wharton`,
`is_reserve_eligible_fn`) and post-processes the result. `verify_stability` and `sanity_check_result` then run on
the same prepared inputs, so the existing safety net still applies.

## 1. Decisions (night run uses the DEFAULT; Truong may edit this table before the run)

| # | Question | Default (recommended) | Why |
|---|---|---|---|
| D1 | Compensation credit (V§8.4) | **Not built this term** (deferred, not rejected). Has no effect before term 2 anyway. Before term 2: measure the incentive with FA-10 | **Stability is NOT the problem**: within a term the credit is a fixed part of the priority key, so DA stays stable and truthful ranking stays optimal inside that term. **The real problem is the incentive across terms**: a student can rank a crowded club NV1 on purpose, lose the lottery, and gain priority next term. That is the concern invariant 2 guards ("no previous outcome in the priority key"; `stb_co_bu` precedent: 113/300 found a profitable lie, TN7d), so turning it on needs Truong's explicit exception to invariant 2 AND a simulation showing the abuse is small |
| D2 | Default medals come from rank order (V§6.1) | **Approved exception to invariant 2 (Truong 08/11, recorded in `CLAUDE.md`)**: defaults = gold/silver/bronze on the first three non-FREE clubs in rank order, derived at the registration layer (Power Apps, converter, kiosk on-site entry screen), and ONLY where the student can override (path A: swap UI; path B: gold question, D12). Stored as student data; the priority key reads stored medals only, never rank | CADA-style separate signal (Abdulkadiroğlu, Che & Yasuda 2015): truthful ranking stays optimal given the medals the student keeps (V§13.1). Without an override the default would tie medals to rank and the exception does not apply |
| D3 | Closing under-filled clubs (V§8.5) | Close **one club per iteration**: the one with the **largest shortfall** (`so_toi_thieu - members`; tie: fewer members, then `club_id`), rerun with the same STB, repeat until no club is short (council 08/11) | Closing all at once can close a club that would have reached its minimum after another closed. Bounded by number of clubs |
| D4 | Waitlist order (V§9.3 said LotteryOrder; corrected by the council 08/11) | SELECTIVE: score -> medal -> lottery. LIMITED: medal -> lottery. Only students who rank that club ABOVE their current club are on the list and invited | Pure lottery can refill a SELECTIVE seat with a lower score ahead of a higher one (breaks V§13.7 at refill) |
| D5 | Public seed (V§8.3) | **Not built** (Truong's 24/10 decision stands, council 08/11). Instead FA-9 = a witnessed lottery record. Re-running stays exact because STB numbers are already stored (`students.stb_number`) and locked (`stb_lock`, seed kept) | Students must be able to trust the draw without a public-text seed: a teacher witnesses the run, and the data fingerprint is frozen BEFORE the seed is entered |
| D6 | Reserved seats | Use the existing soft reserve: `reserve_capacity` = number of reserved students of the club, eligibility = in `giu_cho`. FA workspaces may not also use `reserve_group` | Gives exactly the key "-is_reserved first" when reserved <= capacity (precheck) and reuses verified machinery |
| D7 | Challenge score | Integer 0-10 = round-half-up(points / max * 10), done in the converter | V§7.4 |
| D8 | Registration channel this term | Truong + IT decide at the GĐ2 meeting (before 15/11). Build both converters | See §4 table |
| D9 | Anti-rush on Forms (V§7.2) | Turn ON the Forms quiz **time limit** (auto-submits at the end, no edits after) instead of a per-question limit. Flag = total time (completion - start) **< 1/3 of the median** of that club's takers -> one retake offer | Forms records start/completion only, not per question (`T4M_KET_QUA_TAI_LIEU.md`); time-limit feature: support.microsoft.com/office/f255a4ba-e03c-4e12-b880-f7e8b62e0665 (TH: check it is on in the school tenant) |
| D11 | Fairness between quiz variants (Truong 08/11: never block) | Per SELECTIVE club, on the unrounded 0-10 scale: for each variant v, compare its mean with the mean of the other takers; threshold from sample sizes = `z * sqrt(s_v²/n_v + s_o²/n_o)` with z = 1.96 (2 variants) or 2.39 (3 variants, Bonferroni for 3 comparisons); variants with n < 5 are reported, never adjusted. Beyond the threshold: adjusted = raw + (pooled mean - mean_v), then round half up and clip 0-10 (D7); pass mark uses the adjusted score. Admin confirms: the converter writes the Sổ nhập only after `--ap-dung-dieu-chinh` or `--giu-diem-goc` when any gap is found (report `DIEU_CHINH_BAN_DE.xlsx`); no gap -> no flag needed. Prefer **2 variants** | Otherwise the easier variant becomes luck. With ~20 takers per variant and SD ≈ 2 (assumption), a gap > 1 point appears by chance ≈ 11 % of the time (SE of the difference ≈ 0.63); with ~40 per variant ≈ 2.5 %, so fewer variants = fewer false alarms |
| D12 | Path B registration questions | No Forms **Ranking** question. Per day: 3 separate required choice questions "Nguyện vọng 1 / 2 / 3"; converter drops duplicates (warning). Path B medals: default by order (D2) plus TWO optional questions per day: "Đặt huy chương vàng vào CLB khác NV1? (để trống = giữ mặc định)" (choices = that day's non-FREE clubs) and "Đổi chỗ huy chương bạc và đồng? (để trống = giữ mặc định)" (Có / blank). Converter `dat_huy_chuong_duong_b` (DONE 08/11): gold on the chosen club, silver then bronze on the remaining non-FREE clubs in rank order, swapped if "Có"; all 6 placements reachable, so the invariant-2 exception is fully met. Unusable answers keep the default + warning. Full swap UI on path A | Ranking allows at most 10 options, and partial-save bugs are reported when the respondent does not reorder: lazy students (main users) are hit (learn.microsoft.com/answers 5417196, 5779229) |
| D10 | Which students need a club each day (V§8.6) | Every student in the student list, every day that has clubs | Vision: unregistered -> FREE club of that day |

## 2. Kiosk items (night 1, in this order)

Common rules for every item: tests first (red, then green); FA code paths run only when `rules.fa_daa` is true;
default config must stay byte-identical (invariant 1: `tests/test_nhieu_buoi.py::TestTrungKhit`,
`tests/test_wharton_pipeline.py`, plus every test file that greps a changed identifier). New error codes go to
`i18n_errors.py`, then `python tao_i18n_js.py`. Each new `tests/test_*.py` file changes the test-file count in
`docs/ke_hoach/CLAUDE_CHI_TIET.md` (guarded by `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that`):
update the number in the same commit.

### FA-0 Baseline (no code)
- Create venv, run the invariant-1 tests and `ruff check .`; record pass counts in the handoff file.
- If the baseline is red, STOP (do not fix unrelated tests).

### FA-1 Data model (parent A13; this item states the invariant-7 change)
- `rules.fa_daa` (bool, default False) in `cau_hinh_ws.py` and `LUAT_XEP_MAC_DINH` handling: same pattern as
  `wharton` (`dung_wharton`, `_luat_de_ghi_hoac_bam`: key omitted from history/fingerprint when False). Allowed only
  with `wharton` true, `priority` score, `score_scope` per_slot (FA reuses `wharton_bids`).
- `clubs`: nullable columns `loai` (`TU_DO` | `GIOI_HAN` | `TUYEN_CHON`), `diem_san` (int 0-10), `so_toi_thieu`
  (int >= 0), `suc_chua_phong` (int > 0). NULL = old behaviour. Add through `di_tru_schema` (idempotent, backup
  first; copy the pattern of the latest ADD COLUMN there). Validation in code, not new CHECKs, unless the existing
  pattern requires `_BANG_RANG_BUOC`.
- New table `giu_cho(club_id, student_id, PRIMARY KEY(club_id, student_id))`, FKs like `wharton_bids`; every delete
  path that cleans `wharton_bids` also cleans `giu_cho` (grep `DELETE FROM wharton_bids`).
- Sổ nhập (`so_nhap.py`, `so_excel.py`) and CSV import (`api_nhap.py`): OPTIONAL club columns "Loại", "Điểm sàn",
  "Tối thiểu", "Sức chứa phòng"; OPTIONAL sheet "Giữ chỗ" (Mã CLB, Mã học sinh). Labels accepted for Loại: `Tự do`,
  `Giới hạn`, `Tuyển chọn` (normalised with `chuan_hoa_tim_kiem`). Files without these columns load exactly as now.
  When `fa_daa` is off and the columns are present: ignore with a warning (pattern `csv_wp_bo_qua`).
- Medal cell: the existing "Điểm W k" / `wp_k` column, values 60/30/10 or text `Vàng`/`Bạc`/`Đồng`.
- kiem_nhan: `tests/test_fa_du_lieu.py`: migration twice = same schema; old Sổ nhập loads byte-identical
  (`tests/_so_nhap_dump.py`); new columns round-trip; bad Loại / Điểm sàn rejected with a code; delete cleans `giu_cho`.

### FA-2 Precheck (parent A5; V§4.2)
- Function `kiem_truoc_fa(clubs, giu_cho, students) -> list[err]` in `fa_daa.py`, called in the "kiểm dữ liệu" step
  of `_run_pipeline_da_khoa` and in `get_data_health_report` when `fa_daa` is on. Blocking errors:
  each day has >= 1 `TU_DO` club; every club has `loai`; `GIOI_HAN`/`TUYEN_CHON` have `capacity`; `TUYEN_CHON` has
  `diem_san`; reserved per club <= capacity; reserved student exists and lists that club (else warning, not counted).
- kiem_nhan: `tests/test_fa_kiem_truoc.py` one test per rule; pipeline refuses to run and rolls back nothing.

### FA-3 Medals, one fund (parent A13; V§6)
- `kiem_ho_so_huy_chuong(preferences_by_day, bids, clubs) -> list[err]`: per student per day, values in
  {60, 30, 10}, each value at most once, at most one medal per club (PK already), club must be in that day's list and
  not `TU_DO`. Fewer than 3 medals is valid (V§6.1).
- `diem_huy_chuong_hieu_luc(preferences, bids) -> {club_id: {student_id: points}}`: one fund, ignores `tier`.
  Passed as `diem_wharton` to `run_rbda_nhieu_buoi`; for a `TUYEN_CHON` club the student is tier 1 (has a score) so
  the key is `(0, -score, (), -medal, stb, sid)`; for `GIOI_HAN` the key is `(1, -medal, stb, sid)`. This is exactly
  V§8.2 without compensation (D1).
- `submit_wharton` / on-site entry: when `fa_daa` is on, accept the medal form (server-side check). UI is FA-UI.
- kiem_nhan: `tests/test_fa_huy_chuong.py`: V§13.8; permuting the rank list with medals fixed does not change any
  club's order (invariant 2); medal 60 on a SELECTIVE club never beats a higher score.

### FA-4 FA wrapper `chay_fa_daa(...)` (parent A13 + A5; V§8.2, V§8.6, V§8.7)
Per day, before DA:
1. `TU_DO` club: in-memory capacity = number of students of the day; `reserve_capacity` = 0. Stored capacity untouched.
2. `TUYEN_CHON`: remove the club from the in-memory list of each student with no score (`NOT_ATTEMPTED`) or score <
   `diem_san` (`BELOW_PASS`); record each removal.
3. `GIOI_HAN`: drop any score for that club from `tested_scores` (warning `fa_diem_bo_qua`).
4. Reserved (D6): `reserve_capacity` = count of reserved applicants; eligibility fn = membership in `giu_cho`.
After DA (first pass):
5. Fallback (D10, V§8.6/8.7): students with no list that day, and students unassigned, are processed in STB order;
   each goes to the `TU_DO` club with fewest members (tie `club_id`). Implement by APPENDING that club to the END of
   the student's in-memory list and running DA again: `TU_DO` never rejects, so nobody else moves, and
   `sanity_check_result` / `verify_stability` pass on the augmented lists. Never write the augmented list to
   `preferences`.
6. Groups: for `TU_DO` with `suc_chua_phong` and members > it: `n = ceil(m / suc_chua_phong)`, members sorted by STB,
   `group_no = i % n + 1`. Store in new table `fa_nhom(run_id, buoi, student_id, club_id, group_no)` (append-only,
   like `run_history`) and in exports.
- Hook: `_run_pipeline_da_khoa` calls `chay_fa_daa` instead of `run_rbda_nhieu_buoi` when `fa_daa` is on; same
  transaction, same rollback (invariant 5).
- kiem_nhan: `tests/test_fa_chay.py`: V§13.3, 13.4, 13.6, 13.7; fallback count = students without a club; others'
  assignments identical with and without step 5; `fa_daa` off -> byte-identical.

### FA-5 Minimum members (parent A6; V§8.5, D3)
- Loop in `chay_fa_daa`: while some open `GIOI_HAN`/`TUYEN_CHON` club has members < `so_toi_thieu`, close the one
  with the largest shortfall `so_toi_thieu - members` (tie: fewer members, then `club_id`; D3), remove it from that day's lists, rerun with the SAME STB. Max iterations =
  number of clubs of the day (assert). Record `CLUB_CLOSED` for its applicants. Label in the report: "đóng CLB thiếu
  người là xấp xỉ, không bảo đảm khai thật tối ưu" (A6 risk).
- kiem_nhan: `tests/test_fa_toi_thieu.py`: V§13.11; every open club meets its minimum or is closed; same STB rerun
  identical; closing order independent of input order; with two short clubs, the larger shortfall closes first.

### FA-6 Reasons, cut-offs, waitlist (parent C3; V§8.2 reasons, V§9.1, D4)
- `ly_do_ket_qua(run, prepared_inputs) -> rows`: for each student and each club ranked ABOVE the final assignment in
  the ORIGINAL list: `BELOW_PASS` / `NOT_ATTEMPTED` (from FA-4 step 2), `CLUB_CLOSED` (FA-5), else compare the
  student's key with the last admitted member's key (component order: reserved, score, medal, lottery) and take the
  first differing component -> `RESERVED` / `SCORE` / `MEDAL` / `LOTTERY`. If the student's key is better, raise
  (stability bug). Snapshot: cut-off score, medal, STB of the last admitted. Waitlist (D4): only students who rank
  the club ABOVE their final club; order SELECTIVE = score, medal, STB; LIMITED = medal, STB; position = rank in it. Plus one row for the accepted club
  (`ACCEPTED`, rank in list) and fallback rows (`KHONG_DANG_KY`, `HET_NGUYEN_VONG`).
- Table `fa_ly_do(run_id, buoi, student_id, club_id, rank_in_list, outcome, reason, cut_score, cut_medal, cut_stb,
  waitlist_pos)`, append-only. Export `ket_qua_ly_do.csv` (email/student_id, day, club, group, reason code, Vietnamese
  sentence from V§9.1 templates, own STB number, waitlist position). Templates live in ONE module (`fa_ly_do.py`);
  never include another student's id or name (C3 risk).
- `LOTTERY` sentence needs n (tied applicants on all non-lottery criteria) and k (seats among them): compute from the
  applicants who proposed to the club (club at or above their final position).
- kiem_nhan: `tests/test_fa_ly_do.py`: V§13.9 (every rejection has a valid reason); no foreign id in any sentence;
  reason matches a hand-built 6-student case for each code; waitlist excludes students whose current club is ranked
  above the waitlisted one; SELECTIVE waitlist never puts a lower score ahead of a higher one.

### FA-7 Demand table (outside registry, vision V§4.3)
- `bang_nhu_cau(data, buoi) -> rows`: per club NV1 count, listed count, passed `diem_san` count (`TUYEN_CHON`),
  capacity, reserved count. Export xlsx/CSV via `api_xuat.py` (`_duong_xuat`). No student ids or names.
- `kiem_chi_tang(so_nhap_truoc, so_nhap_sau)`: script `mau_forms_thi_clb/so_sanh_suc_chua.py` that refuses any
  capacity decrease and any type change (V§4.1: type locked at OPEN).
- kiem_nhan: `tests/test_fa_nhu_cau.py`: counts on a hand case; output contains no id; decrease detected.

### FA-8 Acceptance property tests (parent Z6; V§13)
- `tests/test_fa_tinh_chat.py`, stdlib `random` only (no Hypothesis: no new library, rule 7), ~200 small instances
  (6-12 students, 3-5 clubs, 1-2 days, all three types, medals): V§13.1 (exhaustive permutations of each student's
  list, medals fixed, `so_toi_thieu` off), 13.2 (`verify_stability` = 0 pairs), 13.3-13.9, 13.11; 13.5 rerun same
  seed identical. 13.10 belongs to FA-7, 13.12 is D1 (skip with reason).

### FA-9 Witnessed lottery record (parent A2/A13; D5)
- No public-text seed. Kiosk export `bien_ban_boc_tham` (xlsx/pdf-ready html, Vietnamese): date-time, term, data
  fingerprint (`dau_van_tay_du_lieu`), seed, SHA-256 of the sorted (student_id, stb_number) list, counts per day,
  signature lines for the admin and a witness teacher. Ceremony order printed on it: (1) freeze data and print the
  fingerprint, (2) the witness chooses the seed (e.g. rolls a die six times) and types it, (3) run, (4) sign.
  Students can look up their own STB number after publication (existing STB is stored and locked; nothing new).
- kiem_nhan: `tests/test_fa_bien_ban.py`: same data + seed -> identical record except the timestamp; the STB hash
  changes if any number changes; no student name in the record.

### FA-10 Simulation compare (parent A13 "mô phỏng VISEF"; V§12)
- `du_lieu_test/mo_phong_fa_daa.py`: synthetic N students, K clubs/day, D days; liking = common hotness + own taste;
  score = ability + noise ±1; behaviour mix lazy / truthful / strategic (configurable). Same data, old mode
  (score + two funds) vs FA. Output TABLES ONLY (% NV1, % top 2, % no club, % decisions per reason, % lottery losers
  by behaviour type), each labelled "SỐ LIỆU MÔ PHỎNG". No interpretation text.
- Extension for D1 (before term 2): two-term simulation with a "rank a crowded club NV1 on purpose" behaviour;
  output: share of students for whom it pays off, with and without the credit. Tables only.
- kiem_nhan: `tests/test_mo_phong_fa_daa.py`: deterministic per seed; columns present.

### FA-UI Kiosk screens (night 3, Chromium tests)
- Workspace toggle "Xếp kiểu FA-DAA"; club table shows Loại / Điểm sàn / Tối thiểu / Sức chứa phòng; on-site entry
  step "Huy chương" (3 slots, one per club; prefilled with the D2 defaults, student can move any medal); result view shows the reason sentence;
  demand table button. Vietnamese, no jargon (V§0). Follow `js/04_nhap_tai_cho.js` `renderWhartonStep` pattern.

## 3. Microsoft items (night 2; T4M-NC track, all labelled TH = untested on real Microsoft)

| Code | What | Files |
|---|---|---|
| FA-M1 | Club setup form (V§4.1, 5 questions with branching) on Microsoft Forms: build guide (Forms has no creation API) + converter Forms Excel -> Sổ nhập club sheet with automatic Loại classification and FA-2 precheck report | `mau_forms_thi_clb/chuyen_phieu_clb.py`, `mau_forms_thi_clb/PHIEU_THIET_LAP_CLB.md`, `tests/test_fa_m1_phieu_clb.py` |
| FA-M2 | Path B registration on Microsoft Forms (one form per day): description = the one guidance line (V§5.1); 3 separate required choice questions "Nguyện vọng 1 / 2 / 3", no Ranking question, plus the two optional medal questions (D12); shuffle options ON where Forms offers it (TH). Extend the existing Forms generator (`tao_mau_forms.py`, `bieu_mau.py`) behind `--fa-daa` | as listed, `tests/test_fa_m2_forms_dang_ky.py` |
| FA-M3 | Converter FA mode `--fa-daa` (Lists export OR Path B Forms export -> Sổ nhập): medals one fund; path A: default medals when all medal cells are empty and `HC_TuChinh` is not set; path B: call `dat_huy_chuong_duong_b` (already built + 19 tests in `tests/test_fa_m3_huy_chuong_b.py`, incl. all 6 placements; FA-M3 only wires it to the Forms columns); drop duplicate choices with a warning; Loại from club sheet; integer score (D7); `NOT_ATTEMPTED`; rush flag < 1/3 median (D9); duplicate/last-save rule (V§5.1) | `chuyen_forms_sang_phan_mem.py`, `tests/test_fa_m3_chuyen.py` |
| FA-M4 | Quiz on Forms: 2 variant Forms per SELECTIVE club (3 only if many takers) with the same difficulty mix; variant = crc32(email) % n; time limit ON (D9); shuffle questions + options ON; retake = other variant when flagged; item analysis script (% correct, discrimination top third - bottom third, flag < 0, > 90 %, < 20 %; V§7.5) regraded from `de_thi.json`; variant mean comparison with sample-size threshold and mean equating confirmed by the admin, never blocking (D11; kiem_nhan: no adjustment when the gap is within chance, exact shift when beyond, n < 5 never adjusted) | `mau_forms_thi_clb/phan_tich_cau_hoi.py`, `tests/test_fa_m4_phan_tich.py`, doc section in `CAI_DAT_FORMS_CHI_THI.md` |
| FA-M5 | Path A Power Apps spec v2: registration screen (V§5.1: random order with `Shuffle()`, ▲▼ buttons, autosave `Patch` with `TrangThai` DRAFT/SUBMITTED, min 3, FREE warning, card labels) and medal widget (V§6.1) replacing the two-fund screen R25..R38; SharePoint columns: reuse `WP1..WP7` (60/30/10) + `HC_TuChinh` + `TrangThai`; update build kit column module `bo_dung_t4m` | `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md`, `mau_forms_thi_clb/bo_dung_t4m/`, related tests |
| FA-M6 | After allocation: `ket_qua_ly_do.csv` -> SharePoint List "KetQua" (CSV way C) -> app result screen + 3 one-tap feedback buttons (List "PhanHoi"); Forms for week-3 survey and appeals (3-day window); Power Automate reminders (open, -2 days, -3 hours; SELECTIVE not attempted x2; < 50 % after 3 days -> homeroom lists via `T4M_FLOW_GUI_GVCN.md`); attendance List "DiemDanh" + waitlist export. Watch the 6,000 requests/user/day limit (≈3 reminders x 1,000 students) | `docs/he_sinh_thai/FA_SAU_XEP.md` (docs only) |

## 4. Registration channel this term (decision D8, for the GĐ2 meeting)

| | Path A: Power Apps "ECA" (existing app) | Path B: Microsoft Forms only |
|---|---|---|
| IT work | Edit app + list columns (build kit exists) | Create 1 form per day from a guide; no app edits |
| Autosave, random order per student, ▲▼, live medal defaults | Yes; students can swap medals | No autosave; 3 choice questions (no Ranking, D12); medals by order + gold and silver/bronze-swap questions (all 6 placements) |
| Validation (min 3, distinct, medal rules) | In app, before submit | Required questions + converter warnings after |
| Risk for "dùng thật học kỳ này" | Needs an Environment Maker and time (NC-02) | Lowest; works with M365 A3/A5 today |
| Recommendation | If IT confirms edit rights by 15/11 | Otherwise; also the fallback if the app slips |

## 5. Stop rules (also in the night-run file)
Stop the current item and mark it BLOCKED in the handoff file when: an invariant would break; the baseline is red;
a new library is needed; the schema or CSV contract must change beyond what the item says; the same test fails after
3 honest attempts. Then continue with the next item that does not depend on it.

## 6. Night 3: fix list, then kiosk screens (Opus, 2026-11-09, after the night-2 review)

Source of the fix list: `docs/phien/bao_cao_dem/2026-11-09_soat_dem2.md` (and `..._soat_dem1.md` #1-#4). Truong asked
that the review only LIST bugs; night 3 fixes them. Each fix: failing test first that reproduces the bug, minimal
fix, related tests. Default (non-FA) behaviour and outputs stay byte-identical (invariant 1; converter/generator
without `--fa-daa` byte-identical).

### 6.1 Kiosk fixes (first)
| Code | Fix | kiem_nhan |
|---|---|---|
| FA-S7 | `api_xuat.py` `_export_ly_do_da_khoa`: export the reasons of the LATEST run only. If the latest `run_history` row is not an FA run (no `fa_ly_do` rows for it), return `_fail` with a code saying the latest run has no reasons (reuse `fa_chua_co_ly_do` or add one in `i18n_errors.py` + `tao_i18n_js.py`) | `tests/test_fa_ly_do.py` (or new): run FA (run 2), turn FA off, run (run 3) -> export fails with the code; run FA again -> exports run 4 |
| FA-S8 | `api_nhap.py` club CSV import: when FA is OFF, ignore FA columns entirely (one `fa_cot_bo_qua` warning) and KEEP the row; when FA is ON, keep today's behaviour | CSV `club_id,name,capacity,loai` with `C1,...,abc`, FA off -> C1 and C2 created + warning; FA on -> unchanged |
| FA-S9 | Test only: rollback of `fa_nhom` and `fa_ly_do` | inject a failure after the last FA write in `_run_pipeline_da_khoa`; both tables and `match_results` unchanged; `run_history` unchanged |

### 6.2 Converter / generator fixes (`mau_forms_thi_clb/`, all TH)
| Code | Fix | kiem_nhan |
|---|---|---|
| FA-S1 | Retake (V§7.2): in `--fa-daa`, a second attempt for the same club counts ONLY if the first attempt was flagged "too fast" (D9) AND the second file is the student's retake variant (`chon_bien_the_thi_lai`); then it REPLACES attempt 1. Any other second attempt: keep attempt 1, warn. "First attempt" = the file whose variant is `chon_bien_the(email)`, never the CLI file order. D9 median uses first attempts only. Default modes keep "giữ bài đầu" | flagged + retake variant -> score from attempt 2; unflagged second attempt -> ignored + warning; swapping the order of quiz files on the command line gives identical output |
| FA-S2 | `--bo-cau` keys `(club, variant, item)`; CLI `CLB-DE-SO` (e.g. `C3-B-4`). `CLB-SO` accepted only when the club has one variant (else error naming the variants) | dropping item 4 of variant B leaves variant A scores unchanged; old form errors for a 2-variant club |
| FA-S3 | `so_sanh_bien_the`: `N_NHO` (report, no shift) when EITHER side has n < `N_TOI_THIEU` | `{A: 10 scores, B: 3}` -> no `dich` for A or B, `co_lech` False |
| FA-S4 | `_thoi_gian_lam_bai`: accept `datetime` cells and ISO text; when the time columns exist but some rows cannot be read, add ONE warning per file with the count (no guessing of day/month order) | `11/9/26 08:00:00` rows -> warning with count; ISO and datetime rows -> seconds |
| FA-S5 | Warn when a quiz file's variant differs from the variant assigned to that email (`chon_bien_the`, or `chon_bien_the_thi_lai` for an allowed retake). Keep the score (admin decides) | wrong-variant submission -> one warning naming email, club, variant given/expected |
| FA-S6 | `tao_mau_forms.py --fa-daa --so-nhap-clb <FA-M1 sổ>`: read Loại with `chuyen_forms_sang_phan_mem.doc_clb_fa`; FREE clubs are left out of the gold question. Without `--so-nhap-clb`: today's behaviour + its note | with the sổ: no FREE club among gold options; without: output byte-identical to now |
| FA-S11 | Converter `--fa-daa` also writes `EMAIL_MA_HS.csv` (email, student_id; IT machine only, personal data) and a script `mau_forms_thi_clb/ghep_ket_qua_email.py` that joins `ket_qua_ly_do.csv` + that file into `KETQUA_NHAP_LIST.csv` with the `KetQua` columns of `FA_SAU_XEP.md` §2; update §2 "Lấy từ" of `Email` | join test: every row gets its email; a student missing from the mapping -> warning, row kept with empty Email |

### 6.3 Docs fix
- FA-S10: plan §4 D8 table, path B row: "medals by order + gold and silver/bronze-swap questions (all 6 placements)".

### 6.4 Kiosk screens FA-UI (after 6.1-6.3; Chromium tests `tests/test_giao_dien_fa_*.py`, pattern of
`tests/test_giao_dien_wharton.py`; texts in `i18n.js` vi + en; no jargon, never "Wharton", avoid "FA-DAA" on screen)
| Code | Screen | kiem_nhan |
|---|---|---|
| FA-UI-1 | Workspace settings (`js/075_workspace.js`): switch "Xếp theo loại CLB và huy chương" (`rules.fa_daa`); refused with the existing error when `wharton` is off | toggle round-trips; refusal shown |
| FA-UI-2 | Club table (`js/05_quan_ly.js`): columns Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, Giữ chỗ (count) only when FA is on | columns hidden when FA off (page identical to now) |
| FA-UI-3 | On-site entry (`js/04_nhap_tai_cho.js`): when FA is on, a "Huy chương" step replaces `renderWhartonStep`: 3 slots prefilled with the D2 defaults; the student can move any medal (all 6 placements reachable); no medal on FREE clubs; V§6.1 note when gold is on a SELECTIVE club; saves through `submit_huy_chuong` | Chromium: default prefill; reach all 6 placements; FREE club cannot take a medal; server error shown |
| FA-UI-4 | Results (`js/03_ket_qua.js` / `js/09_the_xem.js`): show the reason sentence per student; admin buttons for `export_ly_do_csv` and `export_bang_nhu_cau` | sentence visible; both exports produce files; nothing shown when FA off |
| FA-UI-5 | `HUONG_DAN_SU_DUNG.md`: one FA section (turn on, import Sổ nhập with types, medals, read reasons, demand table) | doc test if one exists for the guide |

Not in night 3 (Truong did not select): attendance, appeals, round 2 in the kiosk; FA-9; FA-10.

## 7. Night 4: night-3 review fixes, lottery record, simulation (Opus, 2026-11-09, after the night-3 review)

Source: `docs/phien/bao_cao_dem/2026-11-09_soat_dem3.md`. Same rules as §6: failing test that reproduces first,
minimal fix, FA off byte-identical.

| Code | Fix / build | kiem_nhan |
|---|---|---|
| FA-N1 | Reasons after a PARTIAL run (`chi_buoi`): `_doc_ly_do_moi_nhat` (api_xuat.py) takes, for EACH day, the rows of the latest run that included that day, and only when that run is the one that wrote the day's current `match_results`. A day whose latest run was not FA has no reasons: leave it out and return a warning (fail only when no day has reasons). Same for `get_ly_do_ket_qua` and the `fa_nhom` join | 2 days, FA full run (6 rows), then `run_pipeline(chi_buoi=[day 1])` -> export still has both days (day 1 from run 2, day 2 from run 1). Repro script in the review report |
| FA-N2 | On-site entry lazy path (V§6.1, D2): when step 2 is saved with FA on and the day has NO saved medals, the screen saves the D2 defaults at once through `submit_huy_chuong`. When the student re-ranks and the saved medals still equal the defaults of the OLD ranking (never moved by hand), save the defaults of the new ranking; if they were moved by hand, keep them and show the gentle reminder (V§6.1). No schema change, no server-side derivation | Chromium: save step 2 only -> `wharton_bids` has 60/30/10 on the first 3 non-FREE clubs; re-rank -> medals follow; move gold then re-rank -> kept + reminder |
| FA-N3 | Clear message when the FA switch is on while determination points are off (night-3 question 1): new code in `i18n_errors.py` (+ `tao_i18n_js.py`), shown at the rules step | Chromium/API: the new code, not the generic one |
| FA-N4 | Retake needs a second variant: when a flagged student's club has ONE variant, the converter warns "không có đề thi lại" and the guide `CAI_DAT_FORMS_BIEN_THE.md` says so | flagged + single-variant club -> warning; nothing else changes |
| FA-9 | Witnessed lottery record, as specified in §2 FA-9 (export `bien_ban_boc_tham`, ceremony order, signature lines, STB hash, data fingerprint) + one admin button | `tests/test_fa_bien_ban.py` as in §2 |
| FA-10 | Simulation compare, as specified in §2 FA-10, including the D1 two-term "lose NV1 on purpose" behaviour. TABLES ONLY, labelled "SỐ LIỆU MÔ PHỎNG", no interpretation text | `tests/test_mo_phong_fa_daa.py` as in §2 |

Defaults for the other night-3 questions (Truong may change before the run): medals are NOT forced to 3 (V§6.1
allows fewer); the result column keeps every sentence of the day in list order; `fa_ly_do.py` wording keeps V§9.1.
Not in night 4: attendance, appeals, round 2, D1 itself, any real-Microsoft test (needs IT, GĐ3).
