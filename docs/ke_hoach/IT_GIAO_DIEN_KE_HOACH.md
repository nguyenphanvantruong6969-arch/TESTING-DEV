# Đưa toàn bộ việc IT vào giao diện kiosk: FA-M7 → FA-M10 — kế hoạch cho Sonnet

> Soạn 2026-11-11 (Opus). Truong duyệt hội đồng "giảm việc IT, vòng 2": giữ HAI đường (A Power Apps + List, B chỉ
> Forms), IT tự chọn; **mọi việc phải làm được bằng giao diện, không kỹ thuật** (không Python, không dòng lệnh, không
> sửa JSON); không cần Post scores nhưng học sinh vẫn làm bài thi; đường Google chưa quyết → **không đụng**.
> Nhãn **TH** = chưa thử trên Microsoft thật. Mọi số liệu test là **MÔ PHỎNG**.
> Spec below is in English (implementer: Sonnet). Locate code by FUNCTION NAME (`grep -n "def <name>" <file>`).

## 0. Rules for the implementer (read first)
- `CLAUDE.md` wins on invariants 1–8 and rules 1–11. No Agent tool. Rule 2: failing test first, minimal code.
- **Branch:** `claude/forms-gop` (continue on it). Push only there. Never force-push. Do NOT open/merge/close a PR.
- **Scope = kiosk UI for FA-DAA mode (paths A and B).** Older T4M modes (`--chi-thi` without FA, default all-in-one
  form, `--moi-clb`) stay CLI-only and unchanged.
- **Defaults unchanged:** every existing CLI (`tao_mau_forms.py`, `chuyen_forms_sang_phan_mem.py`, `chuyen_phieu_clb.py`,
  …) keeps byte-identical output with its current flags. New behaviour goes behind NEW function parameters whose default
  is the old behaviour; the kiosk passes the new values. Prove with the step-1.0 snapshot of `FORMS_GOP_KE_HOACH.md`
  (`--fa-daa`, `--fa-daa --mot-bieu-mau`, `--bien-the`, `--chi-thi`, `--phan-hoi`, `--sau-ket-qua`, `--tuan-3`) → `diff -r`
  before/after = identical. Kiosk: `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7, 60/60 identical.
- Forbidden: DA core (`run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`,
  `verify_stability`), new libraries, CSV column contract, **schema changes** (personal data such as email stays in
  files inside the workspace folder, never in `app.db`). Need one → mark BLOCKED and stop.
- API contract `{ok, data, errors}`; new error codes only in `i18n_errors.py` (vi + en) → `python tao_i18n_js.py`;
  new codes into `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`). UI strings in `i18n.js` vi AND en. Converter
  warnings are Vietnamese raw strings today: show them as-is (raw strings are allowed by the contract); record
  "warnings not translated" as a known limit, do not translate the converter in these items.
- Files the kiosk writes go to `<workspace folder>/forms/` (folder of `app.db`, via the same resolution `_duong_xuat`
  uses) and, for things IT must hand out, also a `.zip` in `thu_muc_tai_ve()`. Reuse `mo_thu_muc` for "Mở thư mục".
- Every new UI flow gets a Chromium test (`tests/test_giao_dien_fa_m*_*.py`, pattern of
  `tests/test_giao_dien_fa_m6b_sau_ket_qua.py`); `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; a skipped UI test is not a pass.

## 1. Shared groundwork (inside FA-M7, first commit)
- New mixin `api_forms.py` → `class FormsMixin`, added to the API class the same way `SauXepMixin` is.
- Helper `_mau_forms()` puts `mau_forms_thi_clb/` on `sys.path` both from source and from PyInstaller
  (`sys._MEIPASS`), then imports the modules lazily. Check first that no module name in `mau_forms_thi_clb/` clashes
  with a root module (`ls *.py` vs `ls mau_forms_thi_clb/*.py`); a clash → BLOCKED.
- `kiosk.spec`: add `mau_forms_thi_clb` to `pathex` and its modules used by the kiosk to `hiddenimports`
  (`bieu_mau`, `tao_mau_forms`, `chuyen_forms_sang_phan_mem`, `chuyen_phieu_clb`, `phan_tich_cau_hoi`,
  `danh_sach_chua_dang_ky`, `doi_chieu_lists`, `ghep_ket_qua_email`, `tao_bo_dung_t4m`, plus any new module), and
  `mau_forms_thi_clb/bo_dung_t4m` to `datas` if `tao_bo_dung_t4m` reads files from it. No new library (docx is
  written with `zipfile`, xlsx with `openpyxl`). Test `tests/test_fa_m7_dong_goi.py`: parses `kiosk.spec` and asserts
  every module `api_forms.py` imports is listed; imports each through `_mau_forms()`.
- New nav tab **"Chuẩn bị đợt"** (`data-tab="chuan_bi"`, file `js/11_chuan_bi.js`, add to `js/_danh_sach.txt`) with
  a step list. First control: **path choice** A / B (radio), stored in `rules.fa_duong` (`"A"`/`"B"`, default absent →
  UI asks; no effect on allocation). Tab shown only when FA-DAA is on (`dung_fa_daa`); otherwise a one-line note how to
  turn it on. Check existing UI tests that count nav items and update only their expected count.

## 2. FA-M7 — one source for clubs and exams (R2 + R4)
Goal: clubs are entered ONCE (club setup form), exams in ONE Excel; nobody edits `de_thi.json`.
- **Step "1. CLB":** button "Nạp tệp xuất Phiếu thiết lập CLB" → API `nap_phieu_clb(file_base64, ky_truoc_base64="")`
  → writes the upload to `forms/` and calls `chuyen_phieu_clb.chuyen_phieu` → `forms/SO_NHAP_CLB_CLB.xlsx` +
  report. Returns `{n_clb, theo_loai, loi, canh_bao}`; UI shows the table of clubs (name, day, type, quota) and the report
  lines. Errors in the report → shown, step stays red. Does NOT write clubs into `app.db` (the final Sổ nhập does that
  in FA-M9).
- **Step "2. Đề thi":** button "Tải tệp đề mẫu" → API `tai_mau_de_thi()` writes `MAU_DE_THI_KIOSK.xlsx` to Downloads,
  pre-filled with the clubs of step 1 (sheet `CLB`: `club_id`, `ten_clb`, `buoi`, read-only meaning) and an empty
  `De_thi` sheet with columns `club_id, de, cau_hoi, lua_chon_a..d, dap_an` (`de` = A/B/C, empty = A) and `Cai_dat`
  (`tieu_de`, `diem_moi_cau`). Format follows the Google `MAU_DE_THI.xlsx` (sheets `Cai_dat`, `CLB`, `De_thi`) plus the
  `de` column; write a NEW module `mau_forms_thi_clb/so_de_thi.py` (`ghi_mau_kiosk`, `doc_so_de_thi`) — do not import
  from `.claude/skills/` (Google path untouched).
- Button "Nạp tệp đề" → API `nap_de_thi(file_base64)` → `so_de_thi.doc_so_de_thi` builds the SAME dict shape as
  `de_thi.json` (`buoi` from the clubs' days with labels, `cau_lac_bo` from step-1 clubs, `de_thi` / `de_thi_bien_the`
  from the sheet), runs `bm.soat_de_thi` and `phan_tich_cau_hoi.kiem_bien_the`; collects ALL errors (club in `De_thi`
  not in step 1, answer not a–d, empty option, variant rules) and writes nothing on error; on success writes
  `forms/de_thi.json` (for audit; same file the CLI could read). A club with no questions = no exam (allowed).
- Tests `tests/test_fa_m7_nguon_mot_lan.py`: template round-trip (write → read → equal); dict from Excel == the default
  `de_thi.json` for the same content (build an Excel from `de_thi.json`, read back, compare `cau_lac_bo` fields used by
  the generator and converter); every error kind listed at once; nothing written on error; club only in `De_thi` →
  error naming it; variant column → `de_thi_bien_the`. API tests for both buttons; UI test: step 1 then step 2 turn green.
Mutation: drop the club-cross-check → the "club not in step 1" test goes red.

## 3. FA-M9 — drop Forms / List exports into the kiosk (R1 + R5 + R6)
- **Step "4. Nạp kết quả đăng ký và bài thi":** one multi-file drop zone (xlsx/csv). API
  `nhan_dien_tep_forms(files)` (`files = [{ten, base64}]`) classifies each file WITHOUT writing:
  registration (has `[<buoi>-nv1]`), quiz (has `[<club_id>-<n>]`), List CSV (path A: `Email`, `Thu`, `NV1`), after-results
  (`[co_sai]` → message "dùng nút ở Theo dõi"), unknown → error. Path A rejects registration xlsx and path B rejects
  List CSV with a clear code.
- **Variant auto-detect (R5):** new pure function `doan_bien_the(de, tieu_de)` in `chuyen_forms_sang_phan_mem.py`:
  compare each quiz column's question text (after the `[...]` tag) with the texts of A/B/C for that club; return the
  single variant whose texts all match, else `None`. UI shows the guess per file with a dropdown to override;
  `None` → dropdown required. CLI `--bien-the-tep` unchanged (explicit wins).
- API `chuyen_tep_forms(files, bien_the, lua_chon)` → calls `chuyen_fa_daa(forms/nap/, de from forms/de_thi.json,
  forms/SO_NHAP_CLB_CLB.xlsx, dang_ky_xlsx | lists, quiz_xlsx, bien_the_tep=…, ap_dung_dieu_chinh / giu_diem_goc /
  bo_cau from lua_chon)`. Returns `{n_hoc_sinh, n_bai_thi, canh_bao, cho_xac_nhan?, cau_co_co?}`:
  - `LoiChoXacNhan` → `cho_xac_nhan = {clb: [...], bao_cao: path}`; UI shows two buttons "Dịch điểm về trung bình chung"
    / "Giữ điểm đã chấm" → re-call with that choice (R6). No file needed again (uploads kept in `forms/nap/tai_len/`).
  - flagged questions from `PHAN_TICH_CAU_HOI.xlsx` → checkbox list "Bỏ câu này" → re-call with `bo_cau`.
  - `LoiTepXuat` / `bm.LoiDeThi` → `_fail` with a new code `forms_khong_chuyen_duoc` (`detail`), nothing written.
- Then the UI shows the existing Sổ nhập preview (`xem_truoc_so_nhap` on `forms/nap/SO_NHAP_CLB.xlsx`) and the normal
  "Nhập sổ" button (`import_so_nhap`), so the import path is the SAME as today (no second import code). Remind to keep
  "Dùng điểm quyết tâm" ON (text from `GHI_CHU_FA_DAA`).
- Tests `tests/test_fa_m9_nap_tep_forms.py` (simulated files built with the existing test helpers / `demo_t4m.py`
  pieces): classification of each kind; wrong-path rejection; `doan_bien_the` A, B, mixed → None; converter output via
  API == CLI output for the same inputs (byte-compare `SO_NHAP_CLB.xlsx` cell values and `EMAIL_MA_HS.csv`); confirm
  flow (first call → `cho_xac_nhan`, second call with choice → Sổ written); `bo_cau` re-grade; error → nothing written.
  UI test: drop 1 registration + 2 quiz files → preview appears → import → students count matches.
Mutations: `doan_bien_the` always "A" → variant test red; ignore `lua_chon` → confirm-flow test red.

## 4. FA-M8 — "Tạo bộ biểu mẫu" button (R3 + R8 + R9)
- **Step "3. Tạo biểu mẫu":** options: path B → "Một biểu mẫu cho mọi buổi" (checked by default IN THE UI only),
  "Hai đề cho CLB Tuyển chọn" (enabled when FA-M7 found variants). Button → API `tao_bo_bieu_mau(tuy_chon)` writes
  `forms/bieu_mau/` and `Downloads/BO_BIEU_MAU_<date>.zip` containing, for the chosen path:
  - both paths: Phiếu thiết lập CLB `.docx` (NEW, R9: `sinh_phieu_clb` in `tao_mau_forms.py`, layout from
    `PHIEU_THIET_LAP_CLB.md` §1 via `ghi_docx_chi_thi`, guide states the two branchings by hand); quiz docx
    (`sinh_bien_the` or the FA quiz generator in use); "Sau khi xem kết quả" (`sinh_sau_ket_qua`); week-3 survey; one
    `00_DOC_TRUOC.md` listing the files in the order IT builds them;
  - path B: registration (`sinh_dang_ky(mot_bieu_mau=…)`, `--so-nhap-clb` behaviour from step 1);
  - path A: the build kit (`tao_bo_dung_t4m` with `--fa-daa` behaviour).
- **R3 (no answer key on Forms):** new parameter `dap_an_tren_forms=True` on the guide writers that tell IT to tick
  "Correct answer"/Points (`CAI_DAT_FORMS_CHI_THI.md` writer and the variant guide). The kiosk passes `False`: the guide
  says "do NOT tick answers; the kiosk grades from the exam file; keep Quiz mode only for Time limit; Show results OFF".
  Fallback line (TH): "if Forms refuses Time limit without answers, tick answers as before". CLI default (`True`) →
  byte-identical. Also write `XEM_LAI_DAP_AN.xlsx` (one row per question: club, đề, câu, đáp án đúng) for teachers to
  check before the link goes out — this replaces the old Forms-vs-regrade cross-check.
- Tests `tests/test_fa_m8_bo_bieu_mau.py`: file list per path (A vs B) exactly as above; zip == folder; Phiếu CLB docx
  has every question title of `PHIEU_THIET_LAP_CLB.md` §1 verbatim (the converter reads by title); `dap_an_tren_forms=
  False` text has no "Correct answer" instruction and has the fallback line; default text unchanged (snapshot diff);
  `XEM_LAI_DAP_AN.xlsx` rows == number of questions. UI test: choose B → button → toast with zip name.
Mutation: kiosk passes `True` → R3 test red.

## 5. FA-M10 — after-allocation buttons (R7 + leftover scripts)
- **Step "5. Sau khi xếp"** (also linked from the results tab):
  - "Xuất kết quả cho List KetQua" (path A, and B if the school uses a List): API `xuat_ket_qua_list()` = the rows of
    `export_ly_do_csv` joined by `ghep_ket_qua_email.ghep` with `forms/nap/EMAIL_MA_HS.csv` → `KETQUA_NHAP_LIST.csv`
    in Downloads; missing email file → code `forms_thieu_email` (run step 4 first).
  - "Ai chưa đăng ký": upload the class roster CSV; uses the last registration upload of step 4 →
    `danh_sach_chua_dang_ky` output in Downloads (one file per class if the script does so today).
  - "Đối chiếu hai lần xuất List" (path A): upload old + new List CSV → `doi_chieu_lists` report xlsx in Downloads.
- Tests `tests/test_fa_m10_sau_xep_nut.py`: API output == CLI output on the same files; missing inputs → codes; UI test
  for the first button.

## 6. Order, per-item loop, bookkeeping
Order: **FA-M7 → FA-M9 → FA-M8 → FA-M10** (M7 is the base; M9 removes the worst pain). Per item: `LATEST_INSTRUCTION.md`
PART 2 §3 steps a→h (red test first, minimal code, related tests, mutation, bookkeeping, `kiem_nhanh`, handoff, commit +
push). Related tests at least: `tests/test_fa_m*_*.py`, `tests/test_fa_gap*_*.py`, `tests/test_mau_forms*.py`,
`tests/test_tao_mau_forms*.py`, `tests/test_giao_dien_fa_*.py`, `tests/test_ws_nhan.py`, `tests/test_a13_12_tai_lieu.py`,
UI tests that count nav items, `tests/test_nhieu_buoi.py -k TestTrungKhit`, plus every test that greps a touched function.
- New test files → update the count in `CLAUDE_CHI_TIET.md` (code map row `tests/`); add `api_forms.py` and
  `so_de_thi.py` rows to the code map.
- `CHANGELOG.md` entry and one `TIEN_DO.md` row per item. User docs: new section "Chuẩn bị đợt" in
  `HUONG_DAN_SU_DUNG.md` (plain Vietnamese, no jargon); `T4M_VAN_HANH_MOT_DOT.md` gets a top note "làm bằng thẻ Chuẩn bị
  đợt; lệnh Python bên dưới chỉ dành cho người phát triển".
- After FA-M7: trigger the Windows build workflow once (or ask Truong) to prove the `.exe` still builds with
  `mau_forms_thi_clb` inside; record the result in the handoff.
- Stop rules = `LATEST_INSTRUCTION.md` §5. Past ~300k tokens: finish the step, update the handoff, push, stop with
  `CONTEXT LIMIT — restart with the same prompt`.

## 7. Finish
1. `soat-ma` on `git diff a8e8f32..HEAD` (report only; fix only cao/trung inside these items).
2. Generator snapshot `diff -r` (section 0) → identical; `kiem_nhanh` 60/60.
3. Report `docs/phien/bao_cao_dem/<YYYY-MM-DD>_it_giao_dien.md` (Vietnamese, plain, ≤ 50 lines): `xong X/4`; table
   `| Mục | Việc (1 câu dễ hiểu) | Kết quả | Commit |`; IT steps before → after (commands typed: before N, after 0;
   answer ticks on Forms: before ~50–100, after 0); what still must be done by hand on Forms (Quick Import, branching —
   Microsoft has no API); tests (UI really run), ruff, "TH", "MÔ PHỎNG"; questions for Truong.
4. Commit, push, verify remote HEAD = local HEAD. No PR.

## 8. Open points (Opus decisions, Truong may change)
- Kiosk UI covers FA-DAA only; legacy T4M modes stay CLI.
- Converter warnings stay Vietnamese in the English UI (known limit).
- `de_thi.json` is still written (audit + CLI reuse) but nobody edits it by hand.
- Email stays in `forms/nap/EMAIL_MA_HS.csv` (workspace folder), never in `app.db`; deletion policy after the cycle:
  HỎI-IT (unchanged).
