Branch: claude/it-ui-b
STATUS: IN_PROGRESS
WARNING: lead is not Opus (claude-sonnet-5-5)
Lead: CHU_TRI session_01VfPzNuCMVqq71ep3pTUA9K. BASE = 51962176a71456ca0417a3ce97da360227f8a7a7 (origin/claude/forms-gop HEAD, already holds G0 + FA-M7, so MERGE-G0 is a no-op)

# Branch handoff: claude/it-ui-b

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Worker B of the IT-UI job. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_B.md` ("Your job", "Shared contract",
> "Sonnet coder rules") + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` §3, §5. PROMPT_B wins where they differ.

## Feature / goal
FA-M9 (load Forms/List files in the "Chuẩn bị đợt" tab, step 4) and FA-M10 (buttons after allocation, step 5).
All numbers SIMULATED; all Forms work TH (not tried on real Microsoft).

## Plan (written by lead; ticked by Sonnet)
- [x] SNAPSHOT: converter CLI outputs from BASE worktree (demo_t4m --day-du + an FA-DAA set) into scratch
- [x] FA-M9-THUAN: `nhan_dien_tep`, `doan_bien_the`, data-returning wrapper; `tests/test_fa_m9_thuan.py`; mutation
- [x] FA-M10-THUAN: callable functions in ghep_ket_qua_email / danh_sach_chua_dang_ky / doi_chieu_lists; `tests/test_fa_m10_thuan.py`
- [x] MERGE-G0 (no-op: BASE already contains G0)
- [x] FA-M9: `api_forms_nap.py` + step 4 UI in `js/12_chuan_bi_nap.js`; 3 test files; mutation (ignore lua_chon)
- [x] FA-M10: `api_forms_nap.py` + step 5 UI; test files; fragment `docs/ke_hoach/it_ui_song_song/MANH_B.md`
- [ ] Green loop on claude/it-ui-b

## Current state (overwrite each handoff)
- Phase 1 (pure) done: FA-M9-THUAN + FA-M10-THUAN committed. FA-M9 Phase 2 done (API + step 4 UI + tests + fragment MANH_B.md). FA-M10 Phase 2 done (API + step 5 UI + 13 tests + fragment). Next: green loop.
- REQUEST A: `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` fails until the code-map test-file count in CLAUDE_CHI_TIET.md is updated (says 254); fold in at integration.
- API building blocks for Phase 2 (all in mau_forms_thi_clb/): `chuyen_forms_sang_phan_mem.nhan_dien_tep(ten, tieu_de)`, `doan_bien_the(de, tieu_de)`,
  `chuyen_fa_daa_du_lieu(thu_muc_ra, de, so_nhap_clb, dang_ky_xlsx, lists, quiz_xlsx, bien_the_tep, lua_chon)` -> trang_thai xong|cho_xac_nhan|loi
  (`lua_chon` = {dieu_chinh: ap_dung|giu, bo_cau: [(clb, de, so)]}); `kq['cau_co_co']` lists flagged questions;
  `danh_sach_chua_dang_ky.chua_dang_ky(ds, dk, ra)`; `ghep_ket_qua_email.ghep`; `doi_chieu_lists.doi_chieu` + `ghi_bao_cao`.
- Snapshot recipe (scratch, rebuilt from BASE worktree): demo_t4m --day-du + `--fa-daa` path A and B on inputs built with helpers of tests/test_fa_m3_chuyen.py;
  compare xlsx by cell values (timestamps differ), others by bytes. Result after M9+M10: 53 files, 0 diffs.

## Decisions and gotchas (keep short)
- IT_UI_STATUS says A integrated alone and paused; Truong now authorised running B. B's branch is created from the
  current forms-gop HEAD (includes G0 + FA-M7 + integration), so no G0 wait.
- Env setup: `LATEST_INSTRUCTION.md` PART 2 §1. UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; skipped != passed.

## Waiting for Truong
- (none)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-12 | sonnet-5-5 lead | branch created, handoff written | |
| 2026-11-12 | sonnet-5-5 coder | SNAPSHOT (53 files) + FA-M9-THUAN (22 tests) + FA-M10-THUAN (7 tests); mutations red | kiem_nhanh 7/7, ruff clean |
CODER session_01VfPzNtVpSjz7Hctw7iV7Z7 FA-M9-THUAN DONE 568bd20
CODER session_01VfPzNtVpSjz7Hctw7iV7Z7 FA-M10-THUAN DONE 194d5de
| 2026-11-12 | sonnet-5-5 coder | FA-M9: api_forms_nap.py (nhan_dien_tep_forms, chuyen_tep_forms, get_forms_nap, lay_so_nhap_nap) + step 4 UI; 19 API + 4 Chromium tests green; mutation ignore lua_chon -> 3 red | kiem_nhanh 7/7, ruff clean |
CODER session_01VfPzNs495e7jDUEqWPy8jf FA-M9 DONE 934d031
| 2026-11-12 | sonnet-5-5 coder | FA-M10: xuat_ket_qua_list, ai_chua_dang_ky, doi_chieu_hai_lan + step 5 UI; 8 API + 5 Chromium tests green; 2 mutations red | ruff clean |
CODER session_01VfPzNtKmTt9VD3XNUQbYRG FA-M10 DONE b43953c
CODER session_01VfPzNveb6btV2ocn7yNVEo FIX-1 DONE e7c5a1f
