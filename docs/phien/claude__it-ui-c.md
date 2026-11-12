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
- [ ] FA-M8 (Phase 2): `api_forms_bo.py` (`FormsBoMixin.tao_bo_bieu_mau_api`), step 3 UI in `js/13_chuan_bi_bo.js`,
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
- FA-M8-THUAN done (pure functions + tests). Next: lead review, then FA-M8 Phase 2 (api_forms_bo.py, js/13_chuan_bi_bo.js, cb_bo_* keys, fragment MANH_C.md).

## Decisions and gotchas (keep short)
- IT_UI_STATUS: A integrated alone into forms-gop (C was BLOCKED then). Truong re-ran PROMPT_C; C branches from the
  current forms-gop HEAD, which already contains G0 + FA-M7 → MERGE-G0 no-op; Phase 2 may start right after Phase 1.
- Worker B is running in parallel on `claude/it-ui-b` (same BASE). Stay inside C files + C marker blocks.
- Env: `LATEST_INSTRUCTION.md` PART 2 §1 on THIS branch. UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`;
  skipped != passed.

## Waiting for Truong
- (none)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-12 | opus lead | branch created from BASE 5196217, handoff written | |
| 2026-11-12 | sonnet coder | FA-M8-THUAN: `bm.TIEU_DE_PHIEU_CLB`/`cac_phan_phieu_clb`; in tao_mau_forms.py `sinh_phieu_clb`, `ghi_cai_dat_phieu_clb`, `dap_an_tren_forms` (default True) on ghi_cai_dat/_chi_thi/_moi_clb/_bien_the + sinh_chi_thi/moi_clb/bien_the, `ghi_xem_lai_dap_an`, `tao_bo_bieu_mau`, `ghi_zip_bo`; tests/test_fa_m8_bo_bieu_mau.py (28 passed) | snapshot from BASE 5196217 (8 modes; --bien-the with a 2-club variant de_thi built in scratch): `diff -r` differs ONLY in default-mode MAU_XUAT_TU_FORMS.xlsx + NHAP_FORMS_THI_CLB.docx = docProps/core.xml timestamp noise; content with core.xml excluded identical (24 files, 0 diffs). Mutation: tao_bo_bieu_mau passing dap_an_tren_forms=True -> `test_bo_khong_co_dap_an_tren_forms_o_moi_huong_dan` RED (1 failed, 27 passed), restored -> 28 passed. Related tests 228 passed; ruff clean; kiem_nhanh 7/7. KNOWN: `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` red (CLAUDE_CHI_TIET.md says 254 test files, now 255) -> A must bump count at integration (fragment, not my file). Path-A kit: HUONG_DAN_IT.md sentence patched by str.replace after tao_bo_dung (tao_bo_dung_t4m.py not owned by C). REQUEST A: none blocking. |
CODER session_01YVAytyhzs8uR54cjoTQrMS FA-M8-THUAN DONE c9550fa
