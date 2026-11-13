Branch: claude/it-ui-b
STATUS: IN_PROGRESS (green loop round 2, after merging origin/claude/forms-gop)
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

## Green loop round 1 (claude/it-ui-b @ fbbb823)
- Local full suite: 1 failed, 5925 passed, 4 skipped (none UI: D1 deferral, 2x numpy missing, POSIX user), coverage 93 %.
  ruff clean. `kiem_nhanh --so-seed 20` 7/7, 60/60. Snapshot vs BASE: identical per coder (53 files, 0 diffs; only i18n strings changed since).
- CI Tests run 43159448923 on fbbb823: lint SUCCESS; Windows 1 failed/5420 passed; Linux 1 failed/5926 passed, coverage 93.42 %.
- The ONLY failure everywhere: `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` ('254', 260): the code-map
  row for `tests/` in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (owner A) says 254 files; B added 6 (test_fa_m9_thuan, test_fa_m10_thuan,
  test_fa_m9_nap_tep_forms, test_giao_dien_fa_m9_nap, test_fa_m10_sau_xep_nut, test_giao_dien_fa_m10_nut) -> 260.
  Not a code bug; an artifact of the file-ownership split (the contract says A folds the count at integration).
- Windows build NOT triggered (step b: only after CI Tests green on this HEAD).
- Waiting for A (AUTO rule): REQUEST A already above. Not fixing it myself (fix rules: never edit another worker's files).

## Green loop round 2 (claude/it-ui-b, lead session_01VfPzNsjEZdwCpR5bXRdhgG, 2026-11-13)
- Cause of round-1 failure gone: `origin/claude/forms-gop` already merged B (f809e2b) and A folded the code-map count (263). Merged
  forms-gop into it-ui-b (clean merge, no code change). `tests/test_a13_12_tai_lieu.py` 8 passed; ruff clean; kiem_nhanh 7/7, 60/60.
- Converter files: only B's own commit (568bd20) differs from BASE, snapshot identical earlier (53 files, 0 diffs).
- Full local suite running in background; then push, CI Tests, Windows build.

## Waiting for Truong
- (Answered by events: A integrated B on forms-gop and fixed the count; no action needed.) Old text: worker A is PAUSED (IT_UI_STATUS), so nobody will update the 254 in CLAUDE_CHI_TIET.md. Allow worker B to change that one number to 260 (one-line edit, will be re-folded by A at integration)? Until answered B stays at line 2 STATUS IN_PROGRESS, waiting per AUTO rules.

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
| 2026-11-12 | sonnet-5-5 lead | 12 wake-ups (07:00-10:57 UTC) waiting for A; forms-gop/it-ui-a unchanged (254) -> BLOCKED | Windows build not triggered (CI not green). All other checks green: 5926 passed on Linux CI, cov 93.42 %, kiem_nhanh 7/7 60/60 |
