# Fixes after the whole-kiosk UI audit: SG-1 … SG-12 — plan for Sonnet

> Written 2026-11-13 by Opus. Source: Fable report "Soát giao diện kiosk RB-DA"
> (https://claude.ai/artifact/QENDTqZFHhePzKsEDh8S6C, audited `origin/main` 58d868b against `claude/fg-sua` 2e0e06a).
> Opus re-checked C1, C2, C3 and H1 in code before writing this. English for the implementer; reply to Truong in Vietnamese.
> Locate code by FUNCTION NAME (`grep -n "^def <name>"`), never line numbers.

## 0. Rules for the implementer (read first)
- **Base (Step 0, done by the manager):** `claude/sg-sua` = `origin/claude/fg-sua` + merge of `origin/claude/forms-gop`
  (which is `main` + these docs). So FG-1…FG-9 are included without waiting for a merge into `main`; the final PR
  `claude/sg-sua` → `main` carries FG and SG together.
  Several items reuse FG patterns (FG-1 menu dialog, FG-2 preview warning, FG-4 busy helper, FG-6 grouped list).
- **How the work runs:** three sessions in a loop (manager / coder / checker), mechanics in `docs/ke_hoach/SG_VONG_LAP.md`.
- One commit per item, message `SG-n: …`. Test first (rule 2): write the acceptance test, see it red, then fix.
- Invariant 1: default config byte-identical. Run `kiem_nhanh --co-so origin/main --so-seed 20` after every item that
  touches Python. SG-3 touches only the FA branch; prove it with `kiem_nhanh` + the FA tests.
- Invariant 6: every new user-visible string goes through `i18n.js` / `i18n_errors.py` (vi AND en); run
  `python tao_i18n_js.py` after editing `i18n_errors.py`; new codes go into `MA_MOI_SAU_ANH_CHUP` in `tests/test_ws_nhan.py`.
- No internal codes (SG-n, FG-n, FA-M…, GAP-n, TH) in any user-visible string. Each UI-string review also runs
  `tests/test_van_phong_tu_nhien.py` and `tests/test_ws_nhan.py`.
- **Stop and ask Truong** (rule 7) before: any schema or CSV-contract change not approved in §1, a new library, or
  any change to the default `Trường học` template values.
- Generated-form modes not touched by an item must stay byte-identical (`diff -r` against a snapshot of `main`,
  as in `FORMS_GOP_SUA_KE_HOACH.md` / FG_STATUS "Snapshots"; compare .xlsx/.docx without `docProps/core.xml`).
- After each item: `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, tick the handoff `docs/phien/claude__sg-sua.md`.

## 1. Decisions — APPROVED by Truong 2026-11-13 ("duyệt tất cả"): D1 = A, D2 = b, D3 = NULL
These approvals cover the schema change of SG-6 (nullable columns, `di_tru_schema`, backup first), the optional
CLB-sheet columns "Giờ" / "Địa điểm" (invariant 7: this item says so), and the reader-contract change of SG-12
(old files with codes must still load). Anything BEYOND these still follows rule 7 (stop and ask).
SG-5 wording: the coder drafts it, the checker checks it against the real rule; it ships, and the exact text is copied
under "For Truong" in the status file so Truong can amend it later.

| # | Question | Options | Recommended (= approved) |
|---|---|---|---|
| D1 | H1: keep club time and room the teacher typed? | **A** add nullable `gio`, `dia_diem` to `clubs` (`di_tru_schema`, idempotent, backup first) + two OPTIONAL columns "Giờ", "Địa điểm" on the CLB sheet of the Sổ nhập (reader accepts their absence), shown in club table, results, rosters, student notice · **B** no schema: warn at load "Giờ và Địa điểm chưa được lưu" | **A** (additive, nullable, results unaffected; same pattern as `COT_FA`). Blocks SG-6 only. |
| D2 | H2: student-visible codes like `[thu_2-nv1]`, `(clb_bong_ro)` in every form | **a** keep (FG-7 decision) · **b** generator also writes a mapping file (title → code); the reader matches by exact plain title via that file, codes disappear from the form · **c** IT strips codes by hand after building | **b**, but as the LAST item (SG-12): it changes the reader contract, so it needs its own approval and a full converter snapshot. Keep **a** for this semester's real run if time is short. |
| D3 | C2: what rank to store for a student placed by FA fallback into a club they never listed? | `NULL` (shown as "—", counted as "not in list") · `0` | `NULL`, if the `match_results` column allows it; otherwise stop and ask. |

## 2. Order (most severe first) and why it differs from Fable's
Fable ranks C1 first (first thing a new user hits). Opus ranks **C3 first**: the project priority rule (`docs/fable/02_FABLE_BRIEF.md` §2) is "harm to
real students", and C3 silently removes every applicant of a club (56 students, 27 with it as first choice), while C1
is loud (the run is blocked, nobody is placed wrongly). C2 corrupts published numbers, including the science report.
Within a severity, smaller items go first.

| Order | Item | Finding(s) | Size | Touches | Needs |
|---|---|---|---|---|---|
| 0 | Step 0 | create `claude/sg-sua` = fg-sua + forms-gop; verify L2, L3 fixed (FG-9) | S | — | — |
| 1 | SG-1 | C3 selective club with no scores at all | S | `fa_daa.kiem_truoc_fa`, health report | — |
| 2 | SG-2 | C1 default workspace blocks itself | S | FG-1 dialog, preview, sample guide text | — |
| 3 | SG-3 | C2 FA rank from trimmed list | M | `fa_daa.chay_fa_daa`, report/dashboard | D3 |
| 4 | SG-4 | M3 two ID-matching rules (appeal typed in kiosk) | S | `api_sau_xep.gui_khieu_nai` | — |
| 5 | SG-5 | H3 medal questions | M | `bieu_mau.cau_vang_fa`, `cau_doi_fa` | — |
| 6 | SG-6 | H1 time and room dropped | S (B) / L (A) | `chuyen_phieu_clb`, `so_nhap`, `clubs` | D1 |
| 7 | SG-7 | H4 + M1 warning walls | S | `js/12_chuan_bi_nap.js`, `js/02_van_hanh.js` | — |
| 8 | SG-8 | M5 `NOI_DUNG` outside i18n (invariant 6) | S | `chuyen_phieu_clb.NOI_DUNG`, `api_forms.nap_phieu_clb` | — |
| 9 | SG-9 | busy state + `.catch` in new JS files | M | `js/05,10,11,12,13_*.js` | — |
| 10 | SG-10 | M2 "150%" for free clubs | S | `js/03_ket_qua.js`, `api_bao_cao.py` | — |
| 11 | SG-11 | UI hygiene: M4, M6, M7, L1, L4, L5 + consistency table | M | CSS, small JS | — |
| 12 | SG-12 | H2 codes in student forms | L | generator + reader | D2 = b |

## 2b. All 19 findings → items (nothing left out)
| Finding | Item | Finding | Item | Finding | Item |
|---|---|---|---|---|---|
| C1 | SG-2 | H3 | SG-5 | M5 | SG-8 |
| C2 | SG-3 | H4 | SG-7 | M6 | SG-11 |
| C3 | SG-1 | M1 | SG-7 | M7 | SG-11 |
| H1 | SG-6 | M2 | SG-10 | L1, L4, L5 | SG-11 |
| H2 | SG-12 | M3 | SG-4 | L2, L3 | Step 0 (verify FG-9) |
| — | — | M4 | SG-11 | review: 68 bare `.then()` | SG-9 |

## 3. Items
### Step 0 — build the base branch (manager)
`git switch -c claude/sg-sua origin/claude/fg-sua && git merge --no-edit origin/claude/forms-gop`. Conflicts are
expected only in bookkeeping files (CHANGELOG, TIEN_DO, handoffs, status files): keep both sides. A conflict in code →
STATUS `SG RED: step 0 conflict in <file>`, stop. Then `ruff`, `kiem_nhanh` 7/7 and the FG tests on the merged tree.
Verify L2 (sidebar numbers) and L3 (absolute path in toast) no longer reproduce (FG-9); record in the item table.

### SG-1 — Selective club that nobody can pass (C3)
- In `fa_daa.kiem_truoc_fa` (or the FA part of `get_data_health_report`): for each TUYEN_CHON club with ≥ 1 applicant
  and **0 students with a score**, add a SEVERE error `fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1}
  that blocks the run, like an invalid commitment profile. Text: club name, how many applicants would all be removed,
  and the fix ("nhập điểm cho CLB này ở thẻ Nhập điểm, hoặc đổi CLB sang loại Giới hạn").
- Acceptance: `tests/test_sg1_tuyen_chon_khong_diem.py`: Guitar-like club (Video challenge, no scores) → run blocked
  with that code and correct counts; same club with one score → not blocked; non-FA default → no new error.

### SG-2 — The default workspace must not trap a new user (C1)
- Do NOT change the default `wharton: true` of the `Trường học` template (invariant 1). Instead:
  1. FG-1 menu dialog "Tính năng sau khi xếp…" gets a row "Dùng điểm quyết tâm" (on/off) for the open workspace;
     disabled with a reason when `fa_daa` is on (FA needs it, see FA-N3 in `cau_hinh_ws.py`).
  2. Preview of a workbook in a workspace with `wharton` on: if a student has ≥ 2 choices in a day and all bids are
     empty/0, warn at PREVIEW (FG-2 pattern, grouped by code with a count) and name the fix (turn off, or fill points).
  3. Fix the Hướng dẫn sheet sentence "ô trống tính là 0": true only when the fund has one club; say so.
  4. The blocked-run message links to the dialog in (1).
- Acceptance: Fable's repro (4 clubs, 10 students, 2 choices/day, empty bids) → preview warns; turning the rule off
  from the menu → run succeeds. UI test for the new row + disabled state under FA.

### SG-3 — One source for preference rank in FA mode (C2)
- In FA mode store in `match_results.rank_in_student_pref` the rank in the student's ORIGINAL list (same value as
  `rank_in_list` in the reason rows); fallback placements into an unlisted club → D3 value. Default mode untouched.
- Dashboard "Vào NV1" and panel "Mức đáp ứng nguyện vọng" then read the corrected value; label fallback separately.
- **Academic check (required):** grep `docs/` and `du_lieu_test/` outputs for FA first-choice percentages produced
  before this fix; list each file and number in the item log so Truong can re-measure. Do not rewrite Truong's
  interpretation or conclusions; only flag.
- Acceptance: `tests/test_sg3_hang_fa.py`: Fable's HS001/HS002 cases (trimmed list; unlisted fallback); dashboard
  NV1 % equals a direct count on `preferences`; `kiem_nhanh` 60/60 identical.

### SG-4 — One matching rule for student IDs (M3)
- `api_sau_xep.gui_khieu_nai` uses `fa_sau_xep.khop_ma_hoc_sinh` like the Forms path. Split the error into two codes:
  unknown student vs. no result on that day.
- Acceptance: "hs010 " typed by hand is accepted when unique; two distinct messages for the two causes.

### SG-5 — Medal questions a student can understand (H3)
- One description line under the medal part (vi; plain words, no jargon): default gold = choice 1, silver = 2,
  bronze = 3; medals only break ties after the test score; leaving it as default never hurts. Text must match the
  real rule (check `fa_daa` / invariant-2 exception); Truong approves the wording.
- Emit "đổi bạc và đồng?" only for a day with ≥ 3 medal-eligible (non-free) clubs.
- Acceptance: generated form for a day with 2 eligible clubs has no swap question; the 110 false warnings at step 4
  disappear on Fable's data; other generator modes byte-identical.

### SG-6 — Club time and room (H1) — D1 = A approved
- D1 = A: nullable columns, `di_tru_schema` idempotent with backup; reader fills them from `C_GIO`, `C_DIA_DIEM`;
  show in step-1 table, Quản lý, "Theo từng câu lạc bộ", Excel "Theo CLB"/"Theo lớp", rosters, student notice.
  Default run output (`match_results`) unchanged.
- D1 = B: one warning at load listing that time and room are not stored.
- Acceptance: a club form export with "15:30-17:00" / "Sân A" → visible in each listed place (A) or warning (B).

### SG-7 — No more walls of warnings (H4, M1)
- Step 4 (`js/12_chuan_bi_nap.js`) and the import panel (`js/02_van_hanh.js`, `canh_bao_gom`) use the FG-6 rule:
  group by code, count, 5 examples, "và N trường hợp nữa". One shared JS helper, no third style.

### SG-8 — Step-1 messages into i18n (M5, invariant 6)
- Move `chuyen_phieu_clb.NOI_DUNG` and `so_nhap.NHAN_LOAI_HIEN_THI` strings to `i18n_errors.py`; API returns codes.
- Acceptance: English UI shows step 1 fully in English (UI test); `kiem_nhanh` `i18n_*` checks pass.

### SG-9 — Busy state and error path for every new button
- Reuse/extend FG-4 `napTepForms` into one wrapper (disable, "Đang…", `.catch`, `.finally`) for the 68 bare `.then()`
  calls in `js/05_quan_ly.js`, `10_theo_doi.js`, `11_chuan_bi.js`, `12_chuan_bi_nap.js`, `13_chuan_bi_bo.js`.
- Acceptance: UI test with an API that rejects → button re-enabled and an error toast shown; double click → one call.

### SG-10 — Free clubs have no fill percentage (M2)
- Free club shows "60 em · không giới hạn chỗ"; summary "chỗ còn trống" excludes free clubs from the denominator.

### SG-11 — UI hygiene in one pass
M4 dialog focus trap + Esc + initial focus (`wsMoManChon`); M6 `color-scheme: light` on `:root`; M7 tab 03 at 1024 px;
L1 `.hs-buoi-nhan` uses `--gold-text`; L4 Nhập điểm uses the shared content width; L5 one hint line where FA-only
export buttons are hidden. Apply the consistency table of the report only where it is a one-line rule (severity labels
and colours, file-location messages); wording glossary goes to `docs/` as a list for Truong to approve.

### SG-12 — Plain titles in student forms (H2) — D2 = b approved
Generator writes `MAP_*.json` (title → code) beside each form; readers match by exact title through it; old files
with codes still load. Full converter snapshot (all modes, path A and B) before and after.

## 4. Out of scope (recorded)
Long functions (`_run_pipeline_da_khoa` 708 lines, `get_data_health_report`, `ghi_so_nhap`) and 143 `except Exception`
in the API layer: separate tech-debt item. Dark theme: not planned (light kiosk; SG-11 only declares `color-scheme`).

## 5. Done when
All SG tests green, related old tests green, `kiem_nhanh` 7/7 with 20 seeds, generator snapshots clean, `ruff` clean,
`soat-ma` four tiers, then re-run Fable's four walkthroughs (Appendix B of the report) and confirm C1–C3 no longer reproduce.
