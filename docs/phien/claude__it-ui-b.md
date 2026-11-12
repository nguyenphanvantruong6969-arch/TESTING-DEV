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
- [ ] SNAPSHOT: converter CLI outputs from BASE worktree (demo_t4m --day-du + an FA-DAA set) into scratch
- [ ] FA-M9-THUAN: `nhan_dien_tep`, `doan_bien_the`, data-returning wrapper; `tests/test_fa_m9_thuan.py`; mutation
- [ ] FA-M10-THUAN: callable functions in ghep_ket_qua_email / danh_sach_chua_dang_ky / doi_chieu_lists; `tests/test_fa_m10_thuan.py`
- [ ] MERGE-G0 (no-op: BASE already contains G0)
- [ ] FA-M9: `api_forms_nap.py` + step 4 UI in `js/12_chuan_bi_nap.js`; 3 test files; mutation (ignore lua_chon)
- [ ] FA-M10: `api_forms_nap.py` + step 5 UI; test files; fragment `docs/ke_hoach/it_ui_song_song/MANH_B.md`
- [ ] Green loop on claude/it-ui-b

## Current state (overwrite each handoff)
- Branch created from BASE, handoff written. No code yet.

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
