# Gộp biểu mẫu Forms: FA-M2b (1 form đăng ký) + FA-M6b (1 form "Sau khi xem kết quả") — kế hoạch cho Sonnet

> Soạn 2026-11-11 (Opus, Truong duyệt S1 + S2 của hội đồng "giảm việc IT"). Chỉ hai mục này. Nhãn **TH** = chưa thử
> trên Microsoft Forms thật. Mọi số liệu test là **MÔ PHỎNG**.
> Spec below is in English (implementer: Sonnet). Locate code by FUNCTION NAME (`grep -n "def <name>" <file>`).

## 0. Rules for the implementer (read first)
- `CLAUDE.md` wins on invariants 1–8 and rules 1–11. No Agent tool. Rule 2: failing test first, minimal code.
- **Branch:** create `claude/forms-gop` from `origin/claude/fa-gaps` (this work builds on GAP-3/GAP-5 there). Bring this
  file in with `git checkout origin/claude/keen-ride-72sa7t -- docs/ke_hoach/FORMS_GOP_KE_HOACH.md`. Push only to
  `claude/forms-gop`. Never touch `main`, `claude/fa-gaps`, `claude/keen-ride-72sa7t`. Never force-push. Do NOT open,
  merge or close any PR.
- **Default unchanged:** without the new CLI flags / new API, every output is byte-identical to before. Prove it for
  the generator: BEFORE coding, run the old generator modes into a scratch folder (step 1.0); AFTER coding, run again
  and `diff -r` → no difference. Kiosk: `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7, 60/60 identical.
- Forbidden: DA core functions (`run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`,
  `verify_stability`), new libraries, CSV column contract changes, schema changes (none are needed: reuse
  `fa_phan_hoi` and `fa_khieu_nai`). Need one → mark BLOCKED.
- Messages: new error codes only in `i18n_errors.py` (vi + en) → `python tao_i18n_js.py`; new codes also go into
  `MA_MOI_SAU_ANH_CHUP` in `tests/test_ws_nhan.py`. Visible UI strings in `i18n.js` with vi AND en; no "Wharton", no
  forbidden forms of address (`kiem_nhanh` `chu_cam`).
- Keep every question tag `[...]` and choice code `(...)` exactly as specified: the importers read by these codes.

## 1. FA-M2b — one registration form for all days (path B, TH)

### 1.0 Snapshot before coding
```bash
D=$(mktemp -d); for m in "--fa-daa" "--phan-hoi" "--tuan-3"; do
  .venv/bin/python mau_forms_thi_clb/tao_mau_forms.py $m --ra "$D/truoc_${m#--}" >/dev/null; done; echo "$D"
```
(read `tao_mau_forms.py main` first for the exact argument names; use the default `de_thi.json`). Keep `$D`.

### 1.1 Layout — `mau_forms_thi_clb/bieu_mau.py`
- New `cac_phan_fa_gop(de)` → `[("Thông tin học sinh", [student_id, name])]` + for each day in `de["buoi"]` order
  (same order `sinh_dang_ky` uses today): the NV section and the medal section of `cac_phan_fa(de, ma_buoi)`
  (i.e. `cac_phan_fa(de, b)[1:]`). Question titles, types, choices, required flags: **identical strings** to the
  per-day form (tags `[<buoi>-nvK]`, `[<buoi>-vang]`, `[<buoi>-doi]` unchanged). The info section appears once.
- Question limit: `dem_cau`-style count of the combined form must be ≤ `TRAN_CAU_MOI_BIEU_MAU`; if not, raise a clear
  error (the CLI prints `KHÔNG GHI TỆP NÀO — …` and writes nothing, like other generator errors).

### 1.2 Generator — `mau_forms_thi_clb/tao_mau_forms.py`
- `sinh_dang_ky(de, thu_muc, mot_bieu_mau=False)`. False → exactly today's behaviour. True → guide + ONE docx
  `NHAP_FORMS_DANG_KY_TAT_CA.docx` (prefix `TIEN_TO_DOCX_DANG_KY`, so the existing cleanup also removes stale per-day
  files; and per-day mode must remove a stale `..._TAT_CA.docx`), written with `ghi_docx_chi_thi(..., phan=cac_phan_fa_gop(de),
  hau_to=" — đăng ký tất cả các buổi")`.
- `ghi_cai_dat_dang_ky(de, mot_bieu_mau=False)`: False → identical text. True → same guide plus a section
  "Một biểu mẫu cho mọi buổi": one link for students; every day's 3 NV questions are required; resubmitting replaces
  the whole earlier answer for every day (converter keeps the LAST submission per day); turn ON "Allow respondents to
  edit their responses" if the tenant offers it (TH); export ONE Excel file and pass it to `--dang-ky`.
- CLI: `--mot-bieu-mau`, valid only with `--fa-daa` (else `ap.error`). Message: `… 1 biểu mẫu (…)`.

### 1.3 Converter — no change expected
`chuyen_forms_sang_phan_mem.doc_dang_ky_fa_forms` already reads several days from one file. Prove it with tests; change
code only if a test shows a real gap (then say so in the commit).

### 1.4 Tests first — `tests/test_fa_m2b_mot_bieu_mau.py`
1. `cac_phan_fa_gop`: 1 + 2×D sections; info section once; each day's `nv1..nvK`, `vang`, `doi` tags exactly once.
2. Every combined question title equals the per-day title from `cac_phan_fa` (string equality).
3. `sinh_dang_ky(mot_bieu_mau=True)` writes guide + exactly one docx; a stale per-day docx in the folder is removed;
   the reverse switch removes a stale `_TAT_CA.docx`.
4. `sinh_dang_ky()` default: same file list as before (N per-day docx + guide).
5. **Converter equivalence:** simulated data, 3 students × 2 days. Build (a) one combined export sheet (header =
   combined titles + `Email`) and (b) two per-day export sheets with the same answers. `doc_dang_ky_fa_forms` on (a)
   once vs (b) twice with the same `danh_sach` → identical `nguyen_vong` and `wp` for every student.
6. Combined resubmission: same email twice → the LAST row wins for every day; one "nộp lần nữa" warning per day.
7. Over the question limit → error, no file written.
8. CLI: `--mot-bieu-mau` without `--fa-daa` → exit code 2 (argparse error).
Mutation: drop one day from `cac_phan_fa_gop` → tests 1 and 5 go red.

### 1.5 Docs
- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §4 (D8 table, path B column): add "one form for all days available
  (`--mot-bieu-mau`, FA-M2b)". Do not change the D8 recommendation or decide D8.

## 2. FA-M6b — one "after results" form: 3 feedback questions + appeal branch (TH)

### 2.1 Layout — `mau_forms_thi_clb/bieu_mau.py`
- New constants:
  - `CAU_CO_SAI = "[co_sai] Em có thấy thông tin của em trong kết quả bị sai không? (ví dụ sai mã, sai điểm, thiếu nguyện vọng)"`
  - `LUA_CHON_CO_SAI = ["Không (0)", "Có (1)"]`
  - `CAU_KN_BUOI = "[kn_buoi] Buổi nào có thông tin bị sai?"` (checkbox, choices `"<tên buổi> (<ma_buoi>)"` for every
    day, in `de["buoi"]` order)
  - `CAU_KN_GHI_CHU = "[kn_ghi_chu] Em mô tả ngắn chỗ sai"` (text)
- New `cac_phan_sau_ket_qua(de)` → two sections:
  1. "Phản hồi sau khi xem kết quả": `cau_ma_hoc_sinh()`, `CAU_HAI_LONG`, `CAU_HIEU_LY_DO`, `CAU_KHO_NHAT` (same
     choices as `cac_phan_phan_hoi`), then `CAU_CO_SAI` — all required.
  2. "Báo lỗi dữ liệu (khiếu nại, chỉ lỗi dữ liệu)": `CAU_KN_BUOI` (checkbox, required), `CAU_KN_GHI_CHU` (required).
  If the docx writer has no checkbox type, add the minimal support `ghi_docx_chi_thi` needs, or fall back to a
  "choice" question and say so in the guide (record the choice in the handoff).
- `cac_phan_phan_hoi()` stays byte-identical.

### 2.2 Generator — `mau_forms_thi_clb/tao_mau_forms.py`
- New `sinh_sau_ket_qua(de, thu_muc)` → `NHAP_FORMS_SAU_KET_QUA.docx` + `CAI_DAT_FORMS_SAU_KET_QUA.md` (use
  `_ghi_khao_sat` or a sibling). Guide must state, step by step (Quick Import cannot set branching):
  - Branching on `[co_sai]`: "Không (0)" → **End of form**; "Có (1)" → section 2. Section 1 last question → leave.
  - Settings: Record name ON; **one response per person ON** (an appeal covering several days uses the checkbox);
    start/end date = 3 days from publication (matches `fa_khieu_nai_so_ngay`, default 3); late or second requests
    go to the homeroom teacher, and the admin enters them on the kiosk (existing appeal entry).
  - Export: Responses → Open in Excel → kiosk "Phản hồi" panel → new button (2.4). Keep `[…]`/`(…)` codes.
- CLI `--sau-ket-qua`, mutually exclusive with `--phan-hoi`, `--tuan-3`, `--fa-daa`, `--chi-thi`, `--moi-clb`,
  `--bien-the` (same pattern as the existing exclusivity checks). `--phan-hoi` keeps working unchanged.

### 2.3 Pure readers — `fa_sau_xep.py`
- `doc_tep_forms_phan_hoi` must read the combined file unchanged (extra columns ignored). Test it; change nothing
  unless a test fails.
- New `doc_tep_forms_khieu_nai(hang, ma_buoi_hop_le) -> (yeu_cau, bo_qua)`:
  - columns by `[mã]` (`_MA_CAU`); value codes by `(mã)` (`_MA_LUA_CHON`), checkbox cell = codes separated by `;`;
  - only rows with `co_sai == 1`; one request per (student_id, day) → `{"student_id", "buoi", "ghi_chu", "luc"}`;
  - `luc` = the Forms completion time if a column named `Completion time` / `Thời gian hoàn thành` (case-insensitive,
    also accept `Start time` as fallback only if completion is missing) parses, else `None`;
  - unknown day code / empty day list / missing student id → into `bo_qua` as `(row_no, student_id, reason_code)`;
  - no `[co_sai]` column → `ValueError` (not this form).

### 2.4 API + UI — `api_sau_xep.py`, `js/` (the panel that calls `nhap_phan_hoi_forms`)
- Refactor without behaviour change: move the insert loop of `nhap_phan_hoi_forms` into a helper used by both APIs,
  and move the validation of `gui_khieu_nai` (row exists, base run, window, duplicate pending) into a helper
  `_them_khieu_nai(cur, student_id, buoi, ghi_chu, luc)` that returns an id or an error code. `gui_khieu_nai` and
  `nhap_phan_hoi_forms` outputs must stay identical (their existing tests must pass untouched).
- New `nhap_sau_ket_qua_forms(file_base64)`:
  - read the workbook once; feedback rows via `doc_tep_forms_phan_hoi` (only if `fa_phan_hoi` is on), appeals via
    `doc_tep_forms_khieu_nai` (only if `fa_khieu_nai` is on);
  - both flags off → `_fail(err("fa_sau_ket_qua_chua_bat"))` (new code, vi + en);
  - appeal window uses `luc` from Forms (the student submitted in time even if IT imports later); `luc` missing →
    use import time and add warning code `khieu_nai_khong_co_gio_forms`;
  - per-appeal failures (`khieu_nai_qua_han`, `khieu_nai_trung`, `khieu_nai_khong_hop_le`) are REPORTED, not fatal;
  - one write transaction; any unexpected error → rollback, `loi_luu_sau_xep`;
  - returns `{"n_ket_qua", "n_khieu_nai", "bo_qua", "khieu_nai_loi": [{student_id, buoi, code}], "canh_bao": [...]}`.
- UI: next to the existing "Nạp từ Forms" feedback button add "Nạp biểu mẫu Sau khi xem kết quả"; on success show one
  toast with the counts and, if any, a short list of appeal errors via `trErr`. Shown under the same conditions as the
  feedback panel. i18n keys vi + en.

### 2.5 Tests first
- `tests/test_fa_m6b_sau_ket_qua.py`:
  1. layout: 2 sections; section 1 = id + 3 feedback + `co_sai` (all required); section 2 = `kn_buoi` (every day,
     codes) + `kn_ghi_chu`.
  2. `cac_phan_phan_hoi()` unchanged (compare with a literal copy of today's structure).
  3. `doc_tep_forms_phan_hoi` on a combined sheet → same rows as on the 3-question sheet with the same answers.
  4. `doc_tep_forms_khieu_nai`: `co_sai` 0 → no request; 1 with `thu_2;thu_4` → two requests; unknown code → `bo_qua`;
     completion time parsed; no `[co_sai]` column → `ValueError`.
  5. API: in-window by Forms time but imported after the deadline → accepted; Forms time after deadline →
     `khieu_nai_qua_han` reported; duplicate pending → `khieu_nai_trung` reported; appeals flag off → feedback
     imported, appeals skipped with a warning; both flags off → `fa_sau_ket_qua_chua_bat`; unknown student → `bo_qua`.
  6. Regression: existing tests of `nhap_phan_hoi_forms`, `gui_khieu_nai`, GAP-3, GAP-5 pass untouched.
  7. Generator: `--sau-ket-qua` writes the 2 files; exclusive with `--phan-hoi`; `--phan-hoi` output identical to 1.0.
- `tests/test_giao_dien_fa_m6b_sau_ket_qua.py` (Chromium, pattern of `tests/test_giao_dien_fa_gap5_*.py`): button visible
  with flags on; importing a small simulated xlsx shows the counts; one appeal appears in the appeals list.
Mutations: (a) use import time instead of Forms time → test 5 first case red; (b) ignore `co_sai` → test 4 red.

### 2.6 Docs
- `docs/he_sinh_thai/FA_SAU_XEP.md`: in the feedback and appeals sections, add the combined form as the recommended
  path B option (one form instead of two), TH. Update the kiosk user guide section that documents the feedback panel
  (grep the existing button label) with the new button.

## 3. Order, per-item loop, bookkeeping
Order: FA-M2b, then FA-M6b. For each item do `LATEST_INSTRUCTION.md` PART 2 §3 steps a→h (red test first, minimal
code, related tests, mutation, bookkeeping, `kiem_nhanh`, handoff, commit + push), with these related tests at least:
`tests/test_fa_m2_*.py`, `tests/test_fa_m3_*.py`, `tests/test_mau_forms*.py`, `tests/test_tao_mau_forms*.py`
(whatever exists), `tests/test_fa_gap3_*.py`, `tests/test_fa_gap5_*.py`, `tests/test_fa_gap6_*.py`,
`tests/test_giao_dien_fa_gap*_*.py`, `tests/test_ws_nhan.py`, `tests/test_a13_12_tai_lieu.py`,
`tests/test_nhieu_buoi.py -k TestTrungKhit`, plus every test file that greps a function you changed. UI tests need
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; a skipped UI test is not a pass.
- New test files → update the count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row `tests/`).
- `CHANGELOG.md` entry per item; one row per item in `docs/ke_hoach/TIEN_DO.md`.
- Handoff `docs/phien/claude__forms-gop.md` from `docs/phien/_TEMPLATE.md` (English, ≤ 150 lines): Goal, Plan (two
  checkboxes), Current state, Session log.
- Stop rules = `LATEST_INSTRUCTION.md` §5. Context: past ~300k tokens finish the step, update the handoff, push, stop
  with `CONTEXT LIMIT — restart with the same prompt`.

## 4. Finish
1. Skill `soat-ma` (`kiem_nhanh.py`, then the four tiers in its `SKILL.md`) on `git diff origin/claude/fa-gaps..HEAD`:
   report only; fix only cao/trung findings inside these two items.
2. Generator `diff -r` against the 1.0 snapshot for `--fa-daa`, `--phan-hoi`, `--tuan-3` → identical (write the result).
3. Report `docs/phien/bao_cao_dem/<YYYY-MM-DD>_forms_gop.md` (Vietnamese, plain, ≤ 50 lines): `xong X/2`; table
   `| Mục | Việc (1 câu dễ hiểu) | Kết quả | Commit |`; what IT now does (form count before → after); tests (UI really
   run), 60/60, ruff, diff -r; "TH — chưa thử trên Forms thật"; "số liệu MÔ PHỎNG"; questions for Truong.
4. Commit, push, verify remote HEAD = local HEAD. Last line of the final message: link to the report on
   `claude/forms-gop`. Do not open a PR (Truong decides where it merges).
