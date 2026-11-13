# Branch handoff: claude/sg-c

> Fresh session: read CLAUDE.md, then this file, then docs/phien/sg_song_song/STATUS_C.md. Continue SG-12 only.

## Feature / goal
SG-12 (H2, D2 = b, approved): student forms carry PLAIN titles (no `[thu_2-nv1]`, no `(clb_x)`); mapping lives in
`MAP_<form>.json`; readers match by exact plain title via a map rebuilt from `de`; old coded exports still load.
Flag `--giu-ma` keeps coded titles byte-identical to pre-SG-12 HEAD e729ff1. Coder role (Sonnet), branch claude/sg-c,
no PR, no subagents. Spec: docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md SG-12 + lead notes in STATUS_C.md.

## Plan
- [x] Shared map in bieu_mau.py (TieuDe/LuaChon str subclasses, che_do_giu_ma contextvar, xay_ban_do, ban_do_chung, ban_do_bieu_mau, doc_ban_do, gop_ban_do)
- [x] Generator: MAP_*.json beside each form, `--giu-ma`, main wrapped in che_do_giu_ma (no leak), md wording conditional
- [x] Readers: chuyen_forms_sang_phan_mem, fa_sau_xep (ThieuBanDo, ban_do_tinh), danh_sach_chua_dang_ky, api_sau_xep, api_forms_nap; i18n codes forms_cot_la / forms_thieu_ban_do / forms_tieu_de_trung (SG-C block, vi+en, i18n_loi.js regenerated)
- [x] Tests: tests/test_sg12_tieu_de_thuan.py (43), conftest autouse fixture runs OLD tests in giu-ma mode (marker `tieu_de_thuan` opts out), fg7 hashes re-pinned
- [x] Red at pre-SG-12 (plain export unreadable) and mutations (2) verified, restored
- [x] Converter snapshot: base == coded == plain (scratchpad conv_snap.py; recipe below)
- [ ] Related batch (51 test files + test_ws_nhan + test_van_phong_tu_nhien) was RUNNING when context ended: rerun, read result
- [ ] kiem_nhanh 7/7 (`.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20`), ruff (was clean)
- [ ] pip install playwright==1.63.0 in .venv, run UI tests of forms-nap tab with PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers (no JS touched; skipped != pass)
- [ ] Regenerate default outputs once more (`.venv/bin/python mau_forms_thi_clb/tao_mau_forms.py`) if code changes; test_cai_dat_forms_khop_de_thi checks it
- [ ] Update STATUS_C.md (Decisions, For Truong, Log line `<UTC> CODER session_01VfPzNs8qcCiQLCKtu6pP4g SG-12 READY <hash> red:... mutation:...`), commit, pull --rebase, push

## Current state
- All code + tests written, uncommitted until this handoff commit. Last full runs: old group 385 pass (fg7 re-pinned since), new file 43 pass, test_mau_forms_thi_clb 24 pass.
- Snapshot recipe (scratchpad /tmp/claude-0/-home-user-testing-dev/094ffc31-6de8-56aa-a062-22a822570bbc/scratchpad): snap.sh <worktree> <out> [--giu-ma] (NEVER run on the real tree: it does `git checkout -- mau_forms_thi_clb/`; use mkcopy.sh + snap_copy.sh); worktrees base=98709f1, pre=e729ff1. Results: `--giu-ma` == pre snapshot (diff -rq, 8 modes); pre vs BASE differ only m2/m3 (SG-5). Default mode differs only in forms carrying codes + new MAP files + MAU_XUAT xlsx + CAI_DAT_FORMS_PHAN_HOI/TUAN_3 md bullets. conv_snap.py <root> <out.json> base|coded|plain: cs_base == cs_coded == cs_plain (cmp identical; m1, chi-thi, moi-clb, path B gop/ngay, path A, phan hoi, khieu nai, tuan 3, variants, nhan_dien).
- Scratchpad files vanish with the container; if lost, rebuild from the recipe in STATUS_C.md SNAPSHOT.

## Decisions and gotchas
- --giu-ma baseline is pre-SG-12 HEAD, not BASE (SG-5 legitimately changed --fa-daa*).
- Plain exam-question titles disambiguated globally ("(CLB name, câu k)") only when two different codes share text; duplicate club names in one day -> LoiDeThi.
- Reader order: `[code]` tag first, then exact plain match (whitespace-collapsed, optional "3." prefix); options: map first, then "(code)".
- khieu nai plain day names need `de` (api_sau_xep._ban_do_forms reads the round's de); without it -> ThieuBanDo -> forms_thieu_ban_do, only when a cell is actually unresolvable.
- Unknown non-system columns: warning (forms_cot_la / canh_bao), never silent.
- conftest fixture is a shared file; mention to lead A. pyproject got a `markers` entry.
- Shell hook blocks `rm -rf $VAR` and sleep chains.

## Files touched
bieu_mau.py, tao_mau_forms.py, chuyen_forms_sang_phan_mem.py, danh_sach_chua_dang_ky.py, fa_sau_xep.py, api_sau_xep.py, api_forms_nap.py, i18n_errors.py, i18n_loi.js, mau_forms_thi_clb/README.md, regenerated CAI_DAT_FORMS.md / MAU_XUAT_TU_FORMS.xlsx / NHAP_FORMS_THI_CLB.docx + new MAP_NHAP_FORMS_THI_CLB.json, pyproject.toml, tests/{conftest,test_ws_nhan,test_fg7_bieu_mau_sau_ket_qua,test_fa_m6b_sau_ket_qua,test_fa_gap5_phan_hoi,test_fa_gap6_tuan_3,test_mau_forms_thi_clb,test_sg12_tieu_de_thuan}.py, docs/ke_hoach/sg_song_song/MANH_C.md.

## For Truong (copy into STATUS_C.md)
Other consumers of codes, untouched: TAO_GOOGLE_FORM.gs + tao_google_forms.py (Google path stays coded), skill xu-li-raw-forms, docs (README root of mau_forms_thi_clb updated; GHI_CHU_GIAO_VIEN.md, DINH_DANG_RAW.md, docs/*). Not tried on real Microsoft Forms (TH). nt byte hashes for the four fg7 modes not re-pinned (content digest asserted on both OS).

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Sonnet | SG-12 implemented, tests green on subsets, handoff at >400k tokens | batch/kiem_nhanh/UI/status line/READY entry still open |

## Result of the related batch (appended after handoff)
51 files + ws_nhan + van_phong: 844 passed, 7 failed.
- 4 x tests/test_giao_dien_fa_m8_bo.py: Playwright not installed in .venv (pip install playwright==1.63.0), not a code failure; rerun.
- 3 real, to fix next: tests/test_t4m_bo_dung_bk34.py::test_04_forms_la_dau_ra_cua_tao_mau_forms_khong_viet_lai,
  tests/test_t4m_chi_thi.py::test_q2_che_do_mac_dinh_van_sinh_giong_tep_trong_kho,
  tests/test_t4m_cong_thi.py::test_q4a_chi_thi_va_mac_dinh_van_sinh_giong_tep_trong_kho.
  Likely cause: they compare generator output with COMMITTED files in mau_forms_thi_clb/ (default plain) while the conftest
  fixture forces giu-ma, or the committed chi-thi/moi-clb files need regenerating. Try marker `tieu_de_thuan` first; check
  whether committed CAI_DAT_FORMS_CHI_THI.md etc. must be regenerated (snapshot said md unchanged, docx/MAP are new).
