Branch: claude/it-ui-c
STATUS: IN_PROGRESS
Lead: CHU_TRI session_01YVAytz6NWHWLMW8oSuiyFi (Opus). BASE = 51962176a71456ca0417a3ce97da360227f8a7a7 (origin/claude/forms-gop HEAD; already holds G0 + FA-M7, so MERGE-G0 is a no-op)

# Branch handoff: claude/it-ui-c

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Worker C of the IT-UI job. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_C.md` ("Your job", "Shared contract",
> "Sonnet coder rules") + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` §0, §4. PROMPT_C wins where they differ.

## Feature / goal
FA-M8: "Tạo bộ biểu mẫu" button (step 3 of the kiosk tab "Chuẩn bị đợt"): R3 (no answer key on Forms,
`dap_an_tren_forms`), R8 (one zip with every form file for the chosen path), R9 (club setup form `sinh_phieu_clb`).
All numbers SIMULATED; all Forms work TH (not tried on real Microsoft).

## Plan (written by lead; ticked by Sonnet)
- [x] FA-M8-THUAN (Phase 1, pure): `sinh_phieu_clb`, `dap_an_tren_forms=True` on guide writers, `ghi_xem_lai_dap_an`,
      `tao_bo_bieu_mau`, `ghi_zip_bo` in `mau_forms_thi_clb/tao_mau_forms.py` / `bieu_mau.py`;
      `tests/test_fa_m8_bo_bieu_mau.py`; mutation (R3); snapshot diff identical
- [x] MERGE-G0: no-op (BASE already contains G0 c7b5d1d/d731a3d via INTEGRATE 47ab08b)
- [x] FA-M8 (Phase 2): `api_forms_bo.py` (`FormsBoMixin.tao_bo_bieu_mau_api`), step 3 UI in `js/13_chuan_bi_bo.js`,
      `cb_bo_*` keys in C marker blocks; `tests/test_fa_m8_api.py`, `tests/test_giao_dien_fa_m8_bo.py`; mutation;
      fragment `docs/ke_hoach/it_ui_song_song/MANH_C.md` (incl. snapshot `diff -r` result)
- [ ] Green loop on claude/it-ui-c

## Snapshot (defaults unchanged)
Rebuild from BASE in a worktree, never from the working branch:
```bash
S=<scratch>; git worktree add $S/base 51962176a71456ca0417a3ce97da360227f8a7a7
for m in "" "--fa-daa" "--fa-daa --mot-bieu-mau" "--bien-the" "--chi-thi" "--phan-hoi" "--sau-ket-qua" "--tuan-3"; do
  n=$(echo "mac_dinh$m" | tr ' ' '_'); (cd $S/base && ../../<repo>/.venv/bin/python mau_forms_thi_clb/tao_mau_forms.py $m --ra "$S/truoc/$n" >/dev/null); done
```
Then the same loop from the branch into `$S/sau/`, and `diff -r $S/truoc $S/sau`. Known noise: `.xlsx`
`docProps/core.xml` timestamp (compare xlsx by unzipped content except core.xml), `.docx` likewise.

## Current state (overwrite each handoff)
- FA-M8-THUAN and FA-M8 done and reviewed (PASS). Green loop round 1 RED (2 tests) -> FIX-1 done (b641d89), reviewed PASS. Green loop round 2 running.

## Green loop round 1 (HEAD 5f3de9b)
- Local: 2 failed, 5905 passed, 4 skipped (none `test_giao_dien_*`), coverage 93.44 %; ruff clean;
  kiem_nhanh --so-seed 20 7/7, 60/60; snapshot 8 modes identical.
- CI Tests run 43157769145: lint green; Linux 2 failed / 5906 passed (cov 93.43 %); Windows 2 failed / 5403 passed.
  Same two failures everywhere:
  1. `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` — AssertionError ('254', 257):
     `CLAUDE_CHI_TIET.md` "Bản đồ mã" row `tests/` says 254 files, branch has 257 (3 new C test files).
  2. `tests/test_giao_dien_tieng_viet_sach.py::test_khong_con_chu_zip_trong_chu_hien_thi[i18n.js]` — vi key
     `cb_bo_ghi` contains the word "zip"; Vietnamese UI must say "tệp nén" (see `ws_btn_xuat` etc.).
- Fix spec FIX-1: (1) in `docs/ke_hoach/CLAUDE_CHI_TIET.md` change ONLY the number 254 -> 257 in the `tests/` row
  (deliberate ownership deviation, see Decisions; note it in MANH_C.md "Phase 3: recount"); (2) reword vi `cb_bo_ghi`
  (C marker block of `i18n.js`) with "tệp nén" instead of "zip"; check every other vi `cb_bo_*` string and the
  user-guide paragraph of `MANH_C.md` for the same word. No test change.

## Decisions and gotchas (keep short)
- IT_UI_STATUS: A integrated alone into forms-gop (C was BLOCKED then). Truong re-ran PROMPT_C; C branches from the
  current forms-gop HEAD, which already contains G0 + FA-M7 → MERGE-G0 no-op; Phase 2 may start right after Phase 1.
- Worker B is running in parallel on `claude/it-ui-b` (same BASE). Stay inside C files + C marker blocks.
- Env: `LATEST_INSTRUCTION.md` PART 2 §1 on THIS branch. UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`;
  skipped != passed.

- Test-file count (`CLAUDE_CHI_TIET.md` "Bản đồ mã" row `tests/`): A's lead is PAUSED (IT_UI_STATUS), so a
  `REQUEST A` cannot be served before integration. Lead decision (AUTO, safest): in the green loop, bump ONLY that
  number on this branch, recorded as a deliberate ownership deviation; at Phase 3 A must recount after merging B and C
  (expected one-line conflict, resolve by recounting `tests/test_*.py`).
- Path B quizzes use `sinh_moi_clb` (one form per club, no gate), same as the path-A kit's `04_forms/`.

## Waiting for Truong
- (none)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-12 | opus lead | branch created from BASE 5196217, handoff written | |
| 2026-11-12 | sonnet coder | FA-M8-THUAN: `bm.TIEU_DE_PHIEU_CLB`/`cac_phan_phieu_clb`; in tao_mau_forms.py `sinh_phieu_clb`, `ghi_cai_dat_phieu_clb`, `dap_an_tren_forms` (default True) on ghi_cai_dat/_chi_thi/_moi_clb/_bien_the + sinh_chi_thi/moi_clb/bien_the, `ghi_xem_lai_dap_an`, `tao_bo_bieu_mau`, `ghi_zip_bo`; tests/test_fa_m8_bo_bieu_mau.py (28 passed) | snapshot from BASE 5196217 (8 modes; --bien-the with a 2-club variant de_thi built in scratch): `diff -r` differs ONLY in default-mode MAU_XUAT_TU_FORMS.xlsx + NHAP_FORMS_THI_CLB.docx = docProps/core.xml timestamp noise; content with core.xml excluded identical (24 files, 0 diffs). Mutation: tao_bo_bieu_mau passing dap_an_tren_forms=True -> `test_bo_khong_co_dap_an_tren_forms_o_moi_huong_dan` RED (1 failed, 27 passed), restored -> 28 passed. Related tests 228 passed; ruff clean; kiem_nhanh 7/7. KNOWN: `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` red (CLAUDE_CHI_TIET.md says 254 test files, now 255) -> A must bump count at integration (fragment, not my file). Path-A kit: HUONG_DAN_IT.md sentence patched by str.replace after tao_bo_dung (tao_bo_dung_t4m.py not owned by C). REQUEST A: none blocking. |
CODER session_01YVAytyhzs8uR54cjoTQrMS FA-M8-THUAN DONE c9550fa
| 2026-11-12 | opus lead | review FA-M8-THUAN c9550fa: PASS | 278 related passed; ruff clean; snapshot 8 modes vs BASE identical (xlsx/docx compared without core.xml); mutation re-done by lead -> R3 test red; kiem_nhanh 7/7; ownership OK |
| 2026-11-12 | sonnet coder | FA-M8 Phase 2: `api_forms_bo.py` (`get_bo_bieu_mau`, `tao_bo_bieu_mau_api`), `js/13_chuan_bi_bo.js` (bước 3), `cb_bo_*` (i18n.js vi+en, khối C), CSS khối C; tests/test_fa_m8_api.py (12), tests/test_giao_dien_fa_m8_bo.py (6 Chromium, chạy 3 lần xanh); MANH_C.md | Mutation: (1) tao_bo_bieu_mau dap_an_tren_forms=True -> API `test_r3_so_voi_dap_an_tren_forms_true` RED (1 failed, 11 passed); (2) API bỏ qua mot_bieu_mau -> `test_mot_bieu_mau_theo_tuy_chon` RED; (3) UI luôn gửi mot_bieu_mau true -> `test_bo_tich_mot_bieu_mau_doi_bo` RED; restored. Snapshot 8 chế độ BASE 5196217 vs nhánh: `diff -rq` rỗng, 23 tệp. Related: 130 passed (ws_nhan, fa_m8, fa_m7, i18n) + UI m7 6 passed + m8 6 passed; ruff sạch; kiem_nhanh 7/7. Không mã lỗi mới nên i18n_loi.js không đổi. Test-file count trên nhánh = 257 (C +3). test_a13_12 đỏ đã biết, để lead. Ghi chú: API đường A bỏ qua mot_bieu_mau (UI tắt ô); REQUEST A: none. |
CODER session_01YVAyu3iuHSR5HxZvebVahw FA-M8 DONE 57f4631
| 2026-11-12 | opus lead | review FA-M8 57f4631..959eca9: PASS | 143 related passed (Chromium ran, 0 skipped); ruff clean; snapshot 8 modes identical; UI mutation (always mot_bieu_mau:true) re-done by lead -> red; kiem_nhanh --so-seed 20 7/7, 60/60; ownership OK (no edits outside C files/markers) |
| 2026-11-12 | opus lead | green loop round 1 started | |
| 2026-11-12 | opus lead | green loop round 1: RED (2 ids, same local/CI Linux/CI Windows) | FIX-1 delegated |
| 2026-11-12 | sonnet coder | FIX-1: (1) CLAUDE_CHI_TIET.md hàng `tests/` 254→257 (lệch quyền sở hữu có chủ đích, ghi ở MANH_C.md); (2) vi `cb_bo_ghi` "tệp zip"→"tệp nén" (i18n.js), đoạn hướng dẫn MANH_C.md cùng sửa | Đỏ trước (2 failed), sau: 2 test + 3 lần chạy lại = 4/4 xanh; test_giao_dien_fa_m8_bo + tieng_viet_sach + a13_12 + fa_m8 api/thuan = 62 passed; ruff sạch; kiem_nhanh --co-so BASE --so-seed 20 7/7, 60/60. Lưu ý: venv mới phải cài requirements-dev.txt (pillow, python-docx) mới có test xanh. |
CODER session_01YVAytyhzs8uR54cjoTQrMS FIX-1 DONE 9e16ba0
| 2026-11-12 | opus lead | review FIX-1 b641d89: PASS (coder log line above has wrong session id/hash; real: session_01YVAytyWT5up1scxVFbRakd, b641d89) | 2 ids now pass + test_giao_dien_fa_m8_bo (22 passed); ruff clean; kiem_nhanh 7/7; CLAUDE_CHI_TIET diff = one number only. Green loop round 2 started |
