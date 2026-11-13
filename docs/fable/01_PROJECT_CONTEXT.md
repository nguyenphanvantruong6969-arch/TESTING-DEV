# Project context: RB-DA club allocation kiosk (for an AI reader)

> Written 2026-11-12 from the repository on branch `claude/forms-gop`. English on purpose (AI context file).
> Source of truth is always the code and the docs named here; this file is a map, not a spec.
> **All numbers in this file are SIMULATED data** (seeded random generators, no real students).
> This is a high-school student's science-research project (VISEF). Owner: Truong.

---

## 1. The problem in one paragraph

A Vietnamese high school must place ~800 students (design range 500–1000) into ~20 clubs (15–30) once per
semester. Clubs meet on fixed days ("buổi"); each day is a separate placement problem, and a student gets at
most one club per day. Students rank clubs (up to 10 per day), may sit an entry test at up to 5 clubs per day,
and clubs have limited seats. The school wants placements that are **fair, explainable, reproducible and
impossible to game**, run offline on a Windows PC by non-technical staff.

## 2. The algorithm (RB-DA core)

All in `rbda_priority_pipeline.py`. Find functions by name (`grep -n "^def <name>"`), never by line number.

| Piece | Function | What it does |
|---|---|---|
| Deferred Acceptance (Gale–Shapley), student-proposing | `run_rbda` | Each round, every unmatched student applies to their next choice; each club tentatively holds the best applicants by its choice function and rejects the rest. Ends when no one has a new proposal. Result is stable and strategy-proof for students (given substitutable choice functions). |
| Two-tier priority | `compute_club_priority` | Tier 1 = students with a test score at that club, sorted by −score then lottery number. Tier 2 = students who ranked the club but have no score, sorted by lottery only. Tier 1 is always above Tier 2. **Never receives preference rank** (anti-endogeneity; a test guards its signature). |
| Soft reserves, two passes (Kominers & Sönmez 2016) | `club_choice_function` | Pass 1 fills up to `reserve_capacity` seats with eligible students of the club's `reserve_group`; pass 2 fills the rest by priority. Unused reserve seats become ordinary seats. Recomputed on every call, not a static list. |
| Single tie-breaking (STB) lottery | `generate_stb_lottery`, `chen_stb_cho_hoc_sinh_moi` | One random number per student, shared by all clubs. Generated from a seed over the *sorted set* of student IDs (reproducible; crc32 where hashing is needed, never `hash()`). Locked after the first run; re-drawing needs a two-step confirmation and leaves a trace. Late students are inserted uniformly at random without changing existing students' relative order. |
| Multi-day | `run_rbda_nhieu_buoi` | Runs `run_rbda` independently per day label. Default lottery mode `stb_ngay` (re-permuted each day). `stb_tuan`, `stb_co_bu` kept only for measurement (`stb_co_bu` opened a manipulation channel: 113/300 simulated students found a profitable lie). |
| Stability check | `verify_stability`, `verify_stability_tuan` | For every (student, club the student prefers to their own), add the student to the club's held set and rerun the dynamic choice function; if accepted → blocking pair. The pipeline **rolls back the whole run** on any blocking pair or sanity failure. |
| Group priority (rules) | `xay_tier_rank`, `uu_tien_theo_nhom` | Optional ranked groups (e.g. grade 12 before 11) placed at the front of the priority key; read from workspace rules. |
| "Determination points" (code name `wharton`) | `uu_tien_wharton`, `khoa_uu_tien_wharton`, `diem_wharton_hieu_luc` | Bidding mode: each student splits 100 points per fund per day; points break ties inside Tier 1 and order Tier 2. Locked after first run. Now mainly the engine behind medals (below). |

**Pipeline** (`api.py`, `PipelineAPI._run_pipeline_da_khoa`, ~580 lines, one transaction):
backup (SQLite Backup API) → validate data → choose days → lock seed / extend STB for new students →
`run_rbda_nhieu_buoi` → sanity + `verify_stability` per day (rollback on failure) → snapshot previous result,
write `match_results`, `run_meta`, append `run_history` (never overwritten), SHA-256 fingerprint of inputs →
export CSV/Excel.

## 3. The FA-DAA layer (current mechanism for the school, default OFF)

Vision spec: `docs/ke_hoach/FA_DAA_VISION.md`. Decisions D1–D12: `docs/ke_hoach/FA_DAA_KE_HOACH.md`.
Code: `fa_daa.py` (`chay_fa_daa`), `fa_ly_do.py`, `fa_bien_ban.py`, `fa_sau_xep.py`, `fa_vong_doi_cho.py`.
It is a **wrapper**: it reshapes inputs in memory, calls the unchanged core, then post-processes.

- **Three club types.** FREE (`TU_DO`: never rejects; capacity = number of students; split into room groups
  after placement), LIMITED (`GIOI_HAN`: seats, no test; any test scores are ignored with a warning),
  SELECTIVE (`TUYEN_CHON`: seats + test with a pass mark; below the mark or not attempted → removed from the
  list before DA, reason `BELOW_PASS` / `NOT_ATTEMPTED`).
- **Priority key per club** (ascending): SELECTIVE `(−reserved, −score, −medal, lottery)`;
  LIMITED `(−reserved, −medal, lottery)`. Test score is an integer 0–10 (D7), so ties are common.
- **Medals** replace free point-splitting: 3 per student per day, gold/silver/bronze = 60/30/10 points, at most
  one per club, shared across club types. **Default** = first three non-FREE clubs in the student's rank order
  (approved exception to invariant 2, D2), but every student can override (path A swap UI; path B two optional
  Forms questions reaching all 6 placements). The priority key reads stored medals, never rank.
  Rationale: CADA-style separate signal (Abdulkadiroğlu, Che & Yasuda 2015).
- **Reserved seats** (club officers, returning members) = existing soft reserve (D6).
- **Fallback**: a student unplaced on a day is appended to the least-full FREE club and DA is rerun (FREE never
  rejects, so no one else moves).
- **Closing under-filled clubs** (D3): close the club with the largest shortfall, rerun with the same lottery,
  repeat; reason `CLUB_CLOSED`.
- **Reasons**: every rejection gets a reason (`SCORE`, `MEDAL`, `LOTTERY`, `RESERVED`, …) = first key element
  that separates the rejected student from the last admitted one (`ly_do_ket_qua`, templates in `fa_ly_do.py`).
- **Lottery trust**: no public-text seed (D5); instead a witnessed lottery record (FA-9, `fa_bien_ban.py`) with a
  SHA-256 of the sorted (student, number) list, fingerprint frozen before the seed is entered.
- **Demand review**: teachers see demand per club and may only **increase** seats (`bang_nhu_cau`,
  `kiem_chi_tang`); next-term capacity suggestions (`goi_y_chi_tieu`, GAP-7).
- **After placement** (`fa_sau_xep.py`, append-only adjustment log `fa_dieu_chinh`; `match_results` and
  `run_history` are never edited): attendance (2/3 unexcused absences frees the seat), waitlist invitations
  (D4: SELECTIVE score→medal→lottery; LIMITED medal→lottery), appeals for data errors only (3 days, rerun with
  same seed), round 2 for leftover seats, 3-question feedback, week-3 survey, admin dashboard (GAP-8).
- **Stable improvement cycles** (Erdil & Ergin 2008, `fa_vong_doi_cho.py`): **measurement mode only**, labelled
  "không bảo đảm ổn định", never writes results.
- **Open decision D1 (compensation credit)**: a student who loses the lottery at choice 1 gets priority next
  term. Not built: it reads a previous outcome (needs a new exception to invariant 2) and creates a cross-term
  manipulation incentive. Memo: `docs/ke_hoach/FA_GAPS_D1_MEMO.md` (small simulation: 1/30 sample students
  gain by lying with compensation, 0/30 without).

## 4. The program around the algorithm

| Layer | Files | Notes |
|---|---|---|
| Entry / hosting | `main.py`, `browser_host.py`, `recovery.py`, `chan_doan.py` | pywebview (WebView2) window; browser fallback on 127.0.0.1; recovery screen if `app.db` is broken |
| Backend API | `api.py` + `api_nhap.py`, `api_xuat.py`, `api_quan_ly.py`, `api_bao_cao.py`, `api_cham_diem.py`, `api_sau_xep.py`, `api_workspace.py`, `api_chung.py` | Contract `{ok, data, errors}`, `errors=[{code, params}]` |
| Errors / i18n | `i18n_errors.py` → `tao_i18n_js.py` → `i18n_loi.js`; `i18n.js` | One source for error messages; vi/en |
| UI | `index.html`, `js/*.js`, `style.css` | Tabs: run pipeline, results, on-site entry, management, blind grading, monitoring |
| Input | `so_nhap.py`, `so_excel.py` | "Sổ nhập CLB": ONE Excel workbook (clubs sheet + one row per student) replaces three CSVs |
| Workspaces | `cau_hinh_ws.py`, `nhan_ws.py`, `workspace.py` | Per-workspace vocabulary (6 nouns, vi/en) and allocation rules (`priority`, `tier_mode`, `score_scope`, `tiers`, limits) stored in `app.db`; the first step toward other sectors |
| Data collection ecosystem | `mau_forms_thi_clb/`, `.claude/skills/` | Google Forms generator (Apps Script skill), Microsoft Forms path B generator (`tao_mau_forms.py`), raw-export processing skill, Power Apps formulas (T4M docs in `docs/he_sinh_thai/`). Most Forms work is marked TH = not yet tried on real Forms |
| "Chuẩn bị đợt" tab (IT steps inside the kiosk, FA-M7…M10) | `forms_dot.py`, `api_forms.py`, `api_forms_bo.py`, `api_forms_nap.py`, `js/12_chuan_bi_nap.js`, `js/13_chuan_bi_bo.js` | Step 1 clubs once, step 2 exams in one Excel file, step 3 "create form bundle" (zip per path A/B), step 4 drop Forms/List exports (auto-detects file kind), step 5 after-allocation buttons. All TH. Pending fixes FG-1…FG-9 from a novice walkthrough: `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md` |
| Simulation | `du_lieu_test/` (`mo_phong_fa_daa.py`, `do_*.py`, datasets `bo_*`) | Old vs FA comparison, behaviour types (lazy / truthful / strategic), two-term D1 test |
| Build | `kiosk.spec`, `build_windows.bat`, GitHub Actions | PyInstaller single exe |
| Tests | `tests/` (~263 test files, several thousand cases incl. Chromium UI tests) | Full suite ~22 min; CI requires coverage ≥ 85 % and ruff |

**Data (`app.db`)**: `students`, `clubs` (capacity > 0, reserve_capacity in 0..capacity, reserve_group, buoi),
`club_test_selection`, `club_scores`, `preferences`, `match_results (PK student_id, buoi)`, `run_meta`,
`run_history`, `stb_lock`, `ket_qua_truoc`, `dau_van_tay_chay`, plus FA tables (`giu_cho`, `fa_nhom`, `fa_ly_do`,
`fa_gioi_han_gv`, `fa_dieu_chinh`, `fa_diem_danh`, …) and `workspace_settings`.

## 5. Invariants (never break; full text in `CLAUDE.md`)

1. Default config is **byte-identical** to before any change (all `match_results` rows, 3 datasets × 20 seeds).
2. Priority never reads preference rank or a previous session's outcome (only exception: default medals, D2).
3. STB lottery: locked, reproducible, crc32 not `hash()`, late arrivals inserted uniformly.
4. `run_history` is append-only.
5. Pipeline order fixed, one transaction, rollback on error.
6. UI↔backend contract `{ok, data, errors}`; messages from one source.
7. CSV column contract changes only when an item says so; schema migration idempotent with backup.
8. A new choice function must pass substitutability + law of aggregate demand, else it is labelled
   "không bảo đảm ổn định" and runs in measurement mode (item A12).

## 6. What is already measured (SIMULATED)

From `docs/ke_hoach/BOI_CANH_DU_AN.md` §5 and `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`:
- RB-DA is student-optimal among stable matchings (0 counterexamples / 2,088 exhaustive instances) and
  strategy-proof (0/1,400), but **not Pareto-efficient**: dataset `bo_sach` (140 students) has 85 mutually
  beneficial swaps involving 34 students (24.3 %). The set of placed students is invariant across stable matchings.
- Boston gives more first choices (92 vs 54) but 50 blocking pairs and 18.43 % of students can manipulate; TTC
  has 118 blocking pairs.
- **Stability check dominates run time**: 10,000 students → `run_rbda` 1.08 s vs `verify_stability` 22.4 s; a
  proposed bisect-based verify gives the same blocking pairs in 0.09 s (item Z4, not merged).
- Rounds: docstring says rounds = longest list; measured median 18, max 227 for 10-item lists; `max_rounds=1000`
  raises `RuntimeError` when hit (item Z5).
- **Late arrivals move earlier students** (2,000 students, capacity ratio 0.8, 20 late arrivals: 32.4 earlier
  students changed, 16.25 lost their seat, 0 improved). Resuming DA from the stored state gives identical
  results 1.8–3.9× faster (items G1–G3).
- FA mechanism vision sims: medals give the lowest lottery share (57 % vs 67 % for one star) and the highest
  top-2 rate (63 %); with equal seats data decides 52 % / lottery 48 %; matching seats to demand → 66 % / 34 %,
  first-choice rate ~48 % → ~79 %. **Capacity matched to demand is the largest lever.**

## 7. Owner's goals

1. Use FA-DAA for real this semester at the school (registration channel decided with IT; Forms paths built).
2. Find weak points and improve the algorithm, especially **changes over time** (late arrivals, withdrawals,
   capacity changes, protecting already-announced students).
3. Generalise to 12 sectors (codes DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC) via the 33-item registry
   (`docs/ke_hoach/SO_DANG_KY_33_MUC.md`, `ke_hoach_thay_doi.json`; shared order Z6 → … → G5). Most Z/A/B/G
   items are still "chưa" (not started); A13 (FA-DAA) and A14 (student class) are done or in progress.
4. Business model later.

## 8. Known weak points and open questions (starting list for research)

1. Not Pareto-efficient (24 % of students in a swap); improvement cycles exist only in measurement mode.
2. Integer 0–10 test scores create many ties, pushing decisions to medals and lottery.
3. Days are solved independently: no cross-day constraints or preferences over day combinations.
4. List-length cap (10, from Microsoft Forms) and 3 medals per day weaken full strategy-proofness
   (Dur & Morrill 2020 style argument); medal placement itself is a strategic choice.
5. Real-time changes: rerunning after late arrivals can demote announced students; no protection yet (G3);
   "removing constraints" events (withdrawal, capacity increase) have no proven incremental method.
6. Compensation credit D1: fairness vs cross-term manipulation, undecided.
7. Knapsack-like capacities, couples, hard minimums, many-to-many (other sectors) can break substitutability →
   no stable matching guaranteed (A3, A7, A8, A11, A12).
8. Performance at 10⁴–10⁵ applicants (TS sector): slow verify, round cap (Z4, Z5).
9. Fallback-and-rerun steps (FREE fallback, club closing loop D3) are argued correct informally; worth a proof
   or property test review.
10. Hard-coded vocabulary (144/191 SQL strings mention clubs/students) limits sector reuse (Z1).

## 9. Read order for a new session

0. `CLAUDE.md`, then `docs/phien/<branch>.md` if it exists.
1. `docs/ke_hoach/BOI_CANH_DU_AN.md` (full context, theory to keep, sectors).
2. `docs/ke_hoach/FA_DAA_VISION.md` + `docs/ke_hoach/FA_DAA_KE_HOACH.md` (current mechanism, decisions D1–D12).
3. `docs/ke_hoach/SO_DANG_KY_33_MUC.md` (33 items), `docs/ke_hoach/TIEN_DO.md` (progress).
4. `docs/CO_CHE_THUAT_TOAN.md`, `docs/NGHIEN_CUU_TOI_UU.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`.
5. Code: `rbda_priority_pipeline.py` (functions in §2), `fa_daa.py`, `fa_sau_xep.py`, `api.py`.

## 10. Glossary

| Term | Meaning |
|---|---|
| buổi | Day/time slot label; two clubs with the same `buoi` clash |
| NV1, NV2 | First / second choice (nguyện vọng) |
| Tầng 1 / Tầng 2 | Tier 1 (has a score at that club) / Tier 2 (ranked it, no score) |
| dự trữ mềm | Soft reserve seats |
| giữ chỗ | Reserved seat for a named student (FA) |
| huy chương | Medal (gold/silver/bronze) |
| điểm quyết tâm / wharton | Determination points (bidding engine) |
| cặp phá vỡ | Blocking pair |
| trùng khít | Byte-identical results (same data, same seed) |
| TH | Not yet tried on the real platform |
| R / O | Item required / optional for a sector |
