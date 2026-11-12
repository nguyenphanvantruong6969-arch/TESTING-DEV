# Sửa sau thử nghiệm người dùng: FG-1 … FG-9 (nhánh forms-gop) — kế hoạch cho Sonnet

> Soạn 2026-11-12 (Opus) từ báo cáo thử nghiệm người dùng mới + soát mã của nhánh `claude/forms-gop` (commit `a8e8f32`,
> 18 phát hiện). Mọi số liệu test là **MÔ PHỎNG**; mọi việc Forms là **TH** (chưa thử trên Microsoft Forms thật).
> **Truong đã duyệt D1–D4 ngày 2026-11-12: cả bốn theo cột "Recommended"** (D1 = C, D2 = khớp mềm khi duy nhất,
> D3 = "Huy chương (60/30/10)", D4 = giữ thẻ 03 + tiêu đề nhóm). Spec below is in English (implementer: Sonnet). Locate code by
> FUNCTION NAME (`grep -n "def <name>" <file>`), never line numbers.

## 0. Rules for the implementer (read first)
- `CLAUDE.md` wins on invariants 1–8 and rules 1–11. No Agent tool. Rule 2: failing test first, minimal code, then
  related tests only. One commit per item code (`FG-n: …`).
- **Branch:** `claude/forms-gop` for manual runs; the autonomous run (`docs/ke_hoach/FG_TU_DONG.md`) uses
  `claude/fg-sua` and its own merge rule. Never force-push. Do NOT open, merge or close any PR.
- **Default unchanged (invariant 1):** after each wave run `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7,
  60/60 identical. No item touches `run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`,
  `compute_club_priority`, `verify_stability`, the STB lottery or `run_history`.
- **Generator byte-identity:** `tao_mau_forms.py` modes `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--phan-hoi`,
  `--tuan-3` must stay byte-identical (`diff -r` vs a snapshot taken BEFORE FG-7). Only `--sau-ket-qua` output changes.
- **No schema change, no new library, no CSV contract change** (with D1 = C). If an item needs one → mark BLOCKED, ask.
- Messages: new error codes only in `i18n_errors.py` (vi + en) → `python tao_i18n_js.py`; new codes also into
  `MA_MOI_SAU_ANH_CHUP` in `tests/test_ws_nhan.py`. UI strings in `i18n.js`, vi AND en. No internal codes (FA-M6b, GAP-n,
  TH, "đường B") in any string a user, IT or student reads.
- After each item: `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, tick the Plan in `docs/phien/claude__forms-gop.md`.
- Before push: skill `soat-ma` (`kiem_nhanh.py` + four tiers), report only.

## 1. Decisions (answered 2026-11-12: the "Recommended" column, all four)
| # | Question | Options | Recommended |
|---|---|---|---|
| D1 | How to stop duplicate rows when the same Forms export is loaded twice? | **A** new column `forms_id` in `fa_phan_hoi` + unique index (schema change, `di_tru_schema`, backup) · **B** delete earlier `nguon='forms'` rows of the same student/type, then insert · **C** skip a row identical to one already stored (same student, source, type, all answers) | **C**: no schema, no deletes; "One response per person" is ON in the guide, so an identical row is a re-load |
| D2 | How to match a typed student ID that differs only in case/spaces? | exact only (today) · **exact, then strip + casefold if exactly one student matches** · map by email (needs a new table: schema) | **middle**: never changes stored IDs; ambiguous → still skipped and listed |
| D3 | In an FA workspace, what does the workbook column for medals say? | keep "Điểm quyết tâm" · **template says "Huy chương"; reader accepts both** | **Huy chương** (FA mode only; default template byte-identical) |
| D4 | Where do the after-results panels live? | new tab · **stay in "Chi tiết và xuất tệp", grouped under a heading "Sau khi công bố kết quả" with one line per button** | **stay + heading** (smallest UI change) |

## 1b. Step 0 — re-check findings on current HEAD (do this first)
The walkthrough ran on `a8e8f32`. The branch then received FA-M7..FA-M10 (tab "Chuẩn bị đợt", Forms import steps,
after-allocation buttons; `index.html`, `i18n.js`, `cau_hinh_ws.py` changed). Files at the core of FG-1..FG-8
(`api_sau_xep.py`, `fa_sau_xep.py`, `js/10_theo_doi.js`, `js/075_workspace.js`, `api_nhap.py`) did not change.
For each FG item, write its failing test first (rule 2): if the test is already green on HEAD, the finding is gone —
record "đã hết trên HEAD" in the handoff and skip the item. FG-9 (sidebar numbers) and FG-8 (tab 03 grouping) must be
re-read against the new tab layout before coding. If FA-M9's new import step already covers the after-results file,
FG-6/FG-8 apply to that step too: ask Truong before touching FA-M9 code.

## 2. Waves and order
| Wave | Items | Why first | Size |
|---|---|---|---|
| 1 | FG-1, FG-3, FG-4 | Feature unreachable; silent duplicate data | S, M, S |
| 2 | FG-5, FG-6, FG-2 | Lost student answers; wrong counts; "Xong" then 686 errors | S, M, L |
| 3 | FG-7, FG-8, FG-9 | Student-facing form, wording, small UX | M, M, S |

## 3. Items

### FG-1 — Turn after-results features on/off for the open workspace (finding: Nghiêm trọng #1)
- UI: in the workspace list row menu (built in `wsVeDanhSach`, `js/075_workspace.js`) add "Tính năng sau khi xếp…".
  It opens a small dialog with the five `CO_SAU_XEP` checkboxes (`cau_hinh_ws.py`) + `fa_khieu_nai_so_ngay` (1–14).
  Save → `update_workspace_config({rules: {...only these keys...}}, slug)`.
- Not in scope: `fa_daa`, `wharton`, priority, score scope (they change results). If `fa_daa` is off, the checkboxes
  are disabled and one line says FA must be chosen when the workspace is created.
- Server already rejects a flag without FA (`FaTinhNangCanFa`) → show its i18n message, keep the dialog open.
- After save, the open workspace re-applies config (panels in tab 03 appear/disappear without restart).
- Tests first: `tests/test_fg1_bat_tinh_nang.py` (API: partial cfg keeps other keys; FA off → error code; so_ngay out of
  range → error) + `tests/test_giao_dien_fg1_bat_tinh_nang.py` (Chromium: tick "Phản hồi" → `#phanHoiTongPanel`
  visible; FA-off workspace → boxes disabled).
- Docs: `CAI_DAT_FORMS_SAU_KET_QUA.md` step 4 names the menu path, not config keys (generator text, see FG-7).

### FG-3 — Loading the same file again adds nothing (Cao #1 + appeal re-open bug)
- Feedback (`_chen_phan_hoi`, `api_sau_xep.py`; shared by both import buttons): with D1 = C, skip a row when a row with
  the same `(student_id, nguon, loai, hai_long, hieu_ly_do, kho_nhat, con_di, muon_doi)` exists. Return the count of
  skipped duplicates.
- Appeals (`_them_khieu_nai` called from `nhap_sau_ket_qua_forms`): **verify first** with a test: an appeal already
  ACCEPTED or REJECTED, then the same file loaded again, today inserts a NEW pending appeal (the duplicate check only looks
  at `trang_thai = 'CHO'`). Fix for the Forms path only: same `(student_id, buoi, created_at = Forms completion time)`
  in any state → count as "already loaded", not as an error. Manual appeals from the kiosk form keep today's rule.
- Tests first: `tests/test_fg3_nap_lai.py` — load twice → row counts unchanged; second result reports duplicates, no
  `khieu_nai_loi`; accepted appeal + reload → still one appeal, still accepted; changed answer → one new row, summary
  uses the latest.

### FG-4 — Import buttons: busy state, error path, one helper (Cao #4, code review)
- `js/10_theo_doi.js`: replace the two copied `FileReader → callApi → reset` handlers with one helper
  `napTepForms(nut, input, tenApi, khiXong)`: disable the button + label "Đang nạp…" while running; `.catch` shows a
  generic error toast; always reset the input and re-enable in `finally`.
- Tests first: Chromium test — during the call the button is disabled; a second click does not start a second call
  (count API calls via a wrapped `callApi`); a rejected call re-enables the button.

### FG-5 — Student ID typed with other case or spaces (Cao #2)
- One pure helper in `fa_sau_xep.py`: `khop_ma_hoc_sinh(ma_go, tat_ca_ma) -> ma | None`: exact match, else
  `strip().casefold()` match if exactly one student matches, else None. Use it in both feedback and appeal paths of
  `nhap_sau_ket_qua_forms` and in `nhap_phan_hoi_forms`. Stored IDs never change.
- Unmatched IDs are returned as a list (first 20) for FG-6 to show.
- Tests first: `"S4 "` → `s4`; `"hs001"` with `HS001` → match; two students `ab`/`AB` + typed `Ab` → None (listed);
  exact match always wins.

### FG-6 — One unit per number, a list instead of a wall (Trung bình #1, #6)
- API result of `nhap_sau_ket_qua_forms` (and `nhap_phan_hoi_forms`): `{hoc_sinh, dong_moi, dong_trung,
  ma_khong_khop: [...], dong_bo_qua: [{dong, ly_do}], khieu_nai_moi, khieu_nai_trung, khieu_nai_loi, canh_bao}`.
  Keep the old keys for one release only if a test or UI still reads them; otherwise replace.
- UI: toast = one sentence ("Đã nạp phản hồi của 3 học sinh, 1 khiếu nại mới."); the panel line under the buttons shows
  a `<ul>` grouped by reason with counts, unmatched IDs listed. Same for the run step "Kiểm tra dữ liệu" (group
  `errors` by `code`, count, show the first 5 of each; "và N lỗi nữa").
- Empty file → its own code `phan_hoi_tep_rong` (today it says "not a feedback export").
- Tests: API keys and counts on the FG-3/FG-5 fixtures; Chromium: list items present, toast one sentence.

### FG-2 — FA workspace: warn at preview, give a sample (Nghiêm trọng #2)
- `xem_truoc_so_nhap` (`api_nhap.py`): when `dung_fa_daa(luat)`, append to `canh_bao` the result of
  `fa_daa.kiem_truoc_fa` and `fa_daa.kiem_ho_so_huy_chuong` on the parsed data, **grouped by code with counts**
  (e.g. "9 CLB chưa có Loại", "677 ô huy chương không phải 60/30/10"). Import stays allowed (the user may fix clubs in
  Quản lý), but the preview line says the run will fail until these are fixed.
- D3: FA-mode template ("Tải sổ nhập mẫu") labels the bid column "Huy chương (60/30/10)" and has the "Loại" column for
  clubs (check `so_nhap` template code; add only what is missing). Reader accepts "huy chuong" as an alias of the
  bid column header. Default (non-FA) template: byte-identical — test it.
- Sample: `du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx` generated by a script in `du_lieu_test/` (fixed seed,
  `random.Random(seed)`), valid for FA (each day has a TU_DO club). Use skill `sinh-du-lieu-clb` if it fits. Mark as
  SIMULATED in the sheet "Hướng dẫn".
- Tests first: `tests/test_fg2_xem_truoc_fa.py` — non-FA workbook into FA workspace → preview warnings grouped, counts
  right; sample workbook → preview clean and `run_pipeline` ok; default template bytes unchanged.

### FG-7 — The "after results" form itself (Cao #3, Trung bình #5, Thấp: CLI)
- `tao_mau_forms.py --sau-ket-qua`: accept `--so-nhap-clb` (today only with `--fa-daa`); when given, `[kn_buoi]` lists
  only the days that have clubs in that workbook. Without it: today's output.
- Title: the docx title for this mode becomes "Phản hồi và báo lỗi sau khi xem kết quả" (not
  `de["tieu_de"] + hau_to`). Other modes unchanged (byte-identity rule in §0).
- Guide step 4: "Kiosk → Không gian làm việc → ⋯ → Tính năng sau khi xếp…" (FG-1) instead of config keys.
- `--help`: remove internal codes from every option text (help text is not part of the byte-identity rule; say so in the
  commit). Print the absolute output folder at the end.
- Keep `[tag]` and `(code)` in questions: the importer reads them. Add one line to the guide telling IT why.
- Tests: `tests/test_fg7_bieu_mau_sau_ket_qua.py` — with a 3-day workbook only those 3 days; title text; `diff -r`
  snapshot for the other modes.

### FG-8 — Wording and wizard (Trung bình #2, #3, #4; Thấp)
- `health_panel_hint` (vi + en): say that items marked NGHIÊM TRỌNG stop the run. Summary line red only when
  serious > 0; otherwise neutral.
- Wizard step 3 (`js/075_workspace.js`): the four "Cần bật xếp theo loại CLB" checkboxes are disabled (and unticked)
  while `wzFaDaa` is off; checkbox sits on the same line as its label (CSS on `.ws-truong` for checkbox inputs only).
- D4: in tab 03, put the appeals + feedback panels under one heading "Sau khi công bố kết quả"; one hint line:
  "Nạp từ Forms (Excel)" = old 3-question form; "Nạp biểu mẫu Sau khi xem kết quả" = new combined form.
- Hide the session label "Chưa chia buổi" (`BUOI_MAC_DINH`) in the appeals list and dropdown when the workspace has one
  session only.
- Tests: Chromium for disabled checkboxes and the heading; unit test for the hint key in both languages.

### FG-9 — Small UX (Thấp)
- "Tải sổ nhập mẫu": success toast gets a "Mở thư mục" button using `mo_thu_muc` (`api_xuat.py`); the full path moves
  into the tooltip.
- Sidebar: drop the 01–06 numbers (they suggest an order the tabs do not follow). Visual-only; update screenshots
  tests if any assert the numbers.
- "32 học sinh chưa có chỗ nào · Cần xử lý" becomes a link that opens and scrolls to "Học sinh chưa có CLB nào".
- Tests: Chromium for the toast button and the link.

## 4. Out of scope (recorded, not fixed here)
- Medals sharing the `wharton_bids` table with commitment points: a design change with schema impact. FG-2 removes the
  trap for users; a separate item is needed to split storage.
- Repo root clutter (78 entries incl. .pptx/.docx), very long modules (`rbda_priority_pipeline.py` 3,174 lines,
  `api_*.py` 1.6–2.1k), Vietnamese/English identifier mix, generic `except Exception` in `api_sau_xep.py`: tech-debt item.
- Student-visible choice codes like "(thu_2)": needed by the importer; changing them needs a new reader contract.

## 5. Done when
- All FG tests green; related old tests green (`-k "fa_m6b or fa_m2b or phan_hoi or khieu_nai or workspace"`).
- `kiem_nhanh` 7/7, 60/60; generator `diff -r` clean for unchanged modes; `ruff check .` clean.
- Re-run the novice walkthrough (fresh workspace dir, browser mode): a new IT person turns the feature on from the menu,
  loads the FA sample, runs, loads the after-results file twice, and sees the same counts both times.
