# PROMPT C — FA-M8 (nút "Tạo bộ biểu mẫu") — cho một phiên Sonnet độc lập

> Dán đoạn dưới vào một phiên Claude Code mới (Sonnet), cùng kho `testing-dev`. Chạy ĐỒNG THỜI với PROMPT_A và PROMPT_B.
> Soạn 2026-11-11 (Opus). TH = chưa thử trên Microsoft thật; số liệu MÔ PHỎNG.

```text
Read CLAUDE.md, then docs/ke_hoach/it_ui_song_song/PROMPT_C.md and follow it exactly. You are worker C.
Push only to claude/it-ui-c. No PR, no subagents, no scheduled tasks.
Last line of your final message: link to your handoff file on your branch.
```

## Your job (worker C)
Create branch `claude/it-ui-c` from `origin/claude/forms-gop`. FIRST take the generator snapshot of plan §0 (`--fa-daa`,
`--fa-daa --mot-bieu-mau`, `--bien-the`, `--chi-thi`, `--phan-hoi`, `--sau-ket-qua`, `--tuan-3`, and the default mode)
into a scratch folder; at the end `diff -r` must show NO difference.

**Phase 1 — pure, no dependency on A (start now):** in `tao_mau_forms.py` / `bieu_mau.py`, plan §4:
- `sinh_phieu_clb(thu_muc)` (R9): Quick Import `.docx` + guide for the club setup form; question titles VERBATIM from
  `mau_forms_thi_clb/PHIEU_THIET_LAP_CLB.md` §1 (the club converter reads by title — assert with a test that feeds a
  simulated export built from those titles through `chuyen_phieu_clb.doc_phieu_clb`).
- `dap_an_tren_forms=True` parameter on every guide writer that tells IT to tick "Correct answer"/Points (grep
  `Correct answer` in `tao_mau_forms.py`); `False` → "do not tick answers; kiosk grades from the exam file; Quiz mode
  only for Time limit; Show results OFF" + TH fallback line. Default `True` → byte-identical.
- `ghi_xem_lai_dap_an(de, duong)` → `XEM_LAI_DAP_AN.xlsx` (club, đề, câu, nội dung, đáp án đúng), all variants.
- `tao_bo_bieu_mau(de, thu_muc, duong="A"|"B", mot_bieu_mau=True, bien_the=False, so_nhap_clb=None)` → writes the file
  set of plan §4 for that path plus `00_DOC_TRUOC.md` (build order), returns the file list; `ghi_zip_bo(thu_muc, zip)`.
  Path A reuses `tao_bo_dung_t4m` (FA-DAA columns) — call it, do not copy it.
Tests `tests/test_fa_m8_bo_bieu_mau.py` (plan §4 list) using the default `de_thi.json`. Mutation: pass
`dap_an_tren_forms=True` from `tao_bo_bieu_mau` → R3 test red. No new CLI flag needed; if you add one, it must be
mutually exclusive like the existing ones and leave every other mode byte-identical.

**Phase 2 — after merging G0 (see "Sync points"):** `api_forms_bo.py` (`FormsBoMixin`): `tao_bo_bieu_mau_api(tuy_chon)`
→ `de` from `forms_dot.doc_de_dot`, path from `rules.fa_duong`, `so_nhap_clb` = `duong_so_nhap_clb_dot` when present;
writes `thu_muc_bieu_mau` and `Downloads/BO_BIEU_MAU_<date>.zip`; errors `forms_chua_co_de`, `forms_duong_chua_chon`,
`forms_tao_bo_loi`. UI in `js/13_chuan_bi_bo.js` only: step 3 (options "Một biểu mẫu cho mọi buổi" checked by default
in the UI, "Hai đề cho CLB Tuyển chọn" enabled only when the exam has variants; button; toast with zip name; "Mở thư
mục" via `mo_thu_muc`). Keys `cb_bo_*` in your marker blocks. Tests `tests/test_fa_m8_api.py`,
`tests/test_giao_dien_fa_m8_bo.py`.
Bookkeeping → `docs/ke_hoach/it_ui_song_song/MANH_C.md` (include the snapshot `diff -r` result). Handoff
`docs/phien/claude__it-ui-c.md`, `STATUS: DONE`.

## Not yours
Tab shell, `index.html`, `kiosk.spec`, `api.py`, steps 1–2 and 4–5, converter, CHANGELOG/TIEN_DO/guides. Need a change
there → line "REQUEST A: …" (or "REQUEST B: …") in your handoff; carry on inside your own files.

## Shared contract (IDENTICAL in PROMPT_A, PROMPT_B, PROMPT_C — do not change it alone)

### Workers, branches, base
| Worker | Items | Branch (push only here) |
|---|---|---|
| A | G0 groundwork, FA-M7, then integration (Phase 3) | `claude/it-ui-a` |
| B | FA-M9, FA-M10 | `claude/it-ui-b` |
| C | FA-M8 | `claude/it-ui-c` |
All three branch from `origin/claude/forms-gop` at the commit that added this folder. If your environment forces a
different branch name, use it and write it on line 1 of your handoff file. Never force-push. Never push to another
worker's branch or to `main`. No PR. No subagents (CLAUDE.md rule 10). All numbers SIMULATED; all Forms work TH.
Item details: `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md` (§2 FA-M7, §3 FA-M9, §4 FA-M8, §5 FA-M10). Where this file and
that plan differ, THIS file wins (it adds the parallel split; §1 of the plan is now G0 of worker A).

### File ownership (only the owner edits a file; anything else → write it in your handoff as a request)
| Owner | Files |
|---|---|
| A | `forms_dot.py` (new), `api_forms.py` (new), `api.py` (mixin line), `kiosk.spec`, `index.html`, `js/11_chuan_bi.js` (new), `js/_danh_sach.txt`, `mau_forms_thi_clb/so_de_thi.py` (new), `mau_forms_thi_clb/chuyen_phieu_clb.py`, nav-count UI tests, `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, `docs/ke_hoach/CLAUDE_CHI_TIET.md`, `HUONG_DAN_SU_DUNG.md`, `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md`, `i18n_loi.js` (regenerated only at integration) |
| B | `api_forms_nap.py` (stub by A in G0, then B), `js/12_chuan_bi_nap.js` (stub by A, then B), `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`, `mau_forms_thi_clb/ghep_ket_qua_email.py`, `mau_forms_thi_clb/danh_sach_chua_dang_ky.py`, `mau_forms_thi_clb/doi_chieu_lists.py` |
| C | `api_forms_bo.py` (stub by A, then C), `js/13_chuan_bi_bo.js` (stub by A, then C), `mau_forms_thi_clb/tao_mau_forms.py`, `mau_forms_thi_clb/bieu_mau.py`, `mau_forms_thi_clb/phan_tich_cau_hoi.py` (read-only unless needed for FA-M8) |
| Shared, marker blocks only | `i18n_errors.py`, `i18n.js` (vi AND en), `tests/test_ws_nhan.py` (`MA_MOI_SAU_ANH_CHUP`), `style.css` |
Shared files: A creates, in G0, one marker pair per worker in each shared file, separated by at least one unchanged
line, e.g. `# === B: FA-M9/M10 — add below ===` … `# === end B ===` (JS/CSS: `/* … */`). Each worker inserts ONLY
between its own pair. After editing `i18n_errors.py` run `python tao_i18n_js.py` and commit `i18n_loi.js` (kiem_nhanh
checks it); conflicts in that generated file are resolved at integration by regenerating, never by hand.
New test files: each worker's own `tests/test_fa_m7_*.py` (A), `test_fa_m9_*`/`test_fa_m10_*` (B), `test_fa_m8_*` (C),
and `tests/test_giao_dien_fa_m<same>_*.py`. Never edit another worker's test file.
Bookkeeping: B and C do NOT edit CHANGELOG/TIEN_DO/CLAUDE_CHI_TIET/user guides. Each writes a fragment
`docs/ke_hoach/it_ui_song_song/MANH_<A|B|C>.md` (CHANGELOG entry text, TIEN_DO row, code-map rows, test-file count,
user-guide paragraph in plain Vietnamese). A folds all fragments in at integration.

### Code contract (A builds it in G0; B and C code against it)
`forms_dot.py` (root module, pure, no UI):
- `nap_mau_forms() -> str`: put `mau_forms_thi_clb/` on `sys.path` (from source or from `sys._MEIPASS`), idempotent.
- `thu_muc_forms(db_path)` = `<dir of app.db>/forms/` (created). Sub-paths, all created on demand:
  `duong_de_dot(db_path)` → `forms/de_thi.json`; `duong_so_nhap_clb_dot(db_path)` → `forms/SO_NHAP_CLB_CLB.xlsx`;
  `thu_muc_nap(db_path)` → `forms/nap/`; `thu_muc_tai_len(db_path)` → `forms/nap/tai_len/`;
  `duong_email_ma_hs(db_path)` → `forms/nap/EMAIL_MA_HS.csv`; `thu_muc_bieu_mau(db_path)` → `forms/bieu_mau/`.
- `doc_de_dot(db_path) -> dict`: `bieu_mau.doc_de_thi(duong_de_dot(db_path))`; missing file → `FileNotFoundError`
  (APIs map it to `forms_chua_co_de`; missing club file → `forms_chua_co_clb`).
Mixins registered by A in `PipelineAPI`: `FormsMixin` (`api_forms.py`, A), `FormsNapMixin` (`api_forms_nap.py`, B),
`FormsBoMixin` (`api_forms_bo.py`, C). Path choice: `rules.fa_duong` ∈ {"A","B"}; API `get_fa_duong()` /
`dat_fa_duong(duong)` (A); B and C read it via `self._luat_nghiem().get("fa_duong")` and fail with
`forms_duong_chua_chon` when absent.
UI: tab `data-tab="chuan_bi"` (A) with containers `#cb-buoc-1` … `#cb-buoc-5` in `index.html`. `js/11_chuan_bi.js`
exposes `window.ChuanBi = { duong(), dangKyBuoc(so, veFn), lamMoi() }`; step 3 is drawn by C's `js/13_chuan_bi_bo.js`,
steps 4–5 by B's `js/12_chuan_bi_nap.js`, each calling `ChuanBi.dangKyBuoc(...)` once.
Error codes A adds in G0 (vi + en, also into `MA_MOI_SAU_ANH_CHUP`): `forms_duong_chua_chon`, `forms_chua_co_clb`,
`forms_chua_co_de`, `phieu_clb_tep_sai`(detail), `de_thi_tep_sai`(detail), `forms_khong_chuyen_duoc`(detail),
`forms_tep_khong_nhan_ra`(ten), `forms_tep_sai_duong`(ten, duong), `forms_tep_sau_ket_qua`(ten),
`forms_can_chon_de`(ten), `forms_thieu_email`, `forms_thieu_danh_sach_lop`(detail), `forms_tao_bo_loi`(detail).
More codes → your own marker block. UI string key prefixes: A `cb_`, B `cb_nap_`, C `cb_bo_`.

### Sync points
- **G0** (A, first commit, message starts `FA-M7 G0:`): everything in "Code contract" + stubs + markers, with tests
  (spec lists modules; mixins registered; stub APIs absent is fine; tab visible when FA-DAA on; nav-count tests
  updated), `kiem_nhanh` 7/7. A pushes G0 BEFORE any FA-M7 logic.
- B and C start with their **pure** work (functions in `mau_forms_thi_clb/` + their tests) which needs nothing from A.
  Before writing API/UI code: `git fetch origin claude/it-ui-a`, find G0 with
  `git log origin/claude/it-ui-a --grep "^FA-M7 G0:" --format=%H -1`, then `git merge <that hash>` (merge, not
  rebase). Not there yet → keep doing pure work; out of pure work → write handoff `STATUS: WAITING_G0`, push, stop.
- Test fixtures for `forms/de_thi.json` and `forms/SO_NHAP_CLB_CLB.xlsx`: B and C create them in `tmp_path` from the
  default `mau_forms_thi_clb/de_thi.json` and `chuyen_phieu_clb.chuyen_phieu` on a simulated club-form export (pattern
  of `tests/test_fa_m1_phieu_clb.py`). Never depend on A's FA-M7 UI.
- **Done:** handoff line 2 = `STATUS: DONE` (or `BLOCKED: <reason>`), fragment written, pushed.
- **Phase 3 (A only, when B and C are DONE):** on `claude/forms-gop`: `git merge origin/claude/it-ui-a`, then `-b`,
  then `-c` (no force). Resolve marker-file conflicts by keeping all blocks; regenerate `i18n_loi.js`
  (`python tao_i18n_js.py`); fold the three fragments into CHANGELOG / TIEN_DO / CLAUDE_CHI_TIET / user guides; run all
  `tests/test_fa_m7*..m10*`, `tests/test_giao_dien_fa_*`, `tests/test_ws_nhan.py`, `tests/test_a13_12_tai_lieu.py`;
  `kiem_nhanh --co-so origin/main --so-seed 20` 7/7 60/60; generator snapshot `diff -r` (plan §0); `soat-ma`; report
  `docs/phien/bao_cao_dem/<date>_it_giao_dien.md` (plan §7). B or C not DONE → A writes `STATUS: WAITING_B/C`, stops.

### Everyone, always
- CLAUDE.md invariants 1–8 and rules 1–11 win. Failing test first; mutation check per item; related tests only
  (UI tests need `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`; skipped ≠ passed). Before each push: `ruff check .` and
  `python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` → 7/7.
- Defaults unchanged: existing CLI output byte-identical (snapshot of plan §0 before you touch a generator/converter).
  No DA-core edits, no schema change, no new library, no CSV-contract change. Need one → `BLOCKED`, stop.
- Handoff file `docs/phien/claude__it-ui-<a|b|c>.md` from `docs/phien/_TEMPLATE.md` (English, ≤ 150 lines): line 1
  branch, line 2 STATUS, then Plan checkboxes, Current state, Session log. Past ~300k tokens: finish the step, update
  handoff, push, stop with `CONTEXT LIMIT — restart with the same prompt`.

### AUTO mode (when your prompt ends with `Mode: AUTO.` — no human will answer you)
- Never ask. A question for Truong → write it in your handoff under "Waiting for Truong", continue with work that does
  not depend on it. Technical choice → safest option keeping default behaviour byte-identical; record it.
- Never stop just to wait. Instead of stopping with `WAITING_G0` / `WAITING_B/C`: write the status, commit, push, then
  `send_later` (20 min) with message `continue AUTO from <your handoff file>`; on each wake-up `git fetch` and re-check.
  After 12 wake-ups (~4 h) with no change → `BLOCKED: waited too long for <G0|B|C>`, push, stop.
- Context ~300k or the turn must end: commit, push, write the exact next step in the handoff, `send_later` (2 min) with
  the same message. `send_later` refused → print `RESTART: paste the same prompt again` and the handoff link.
- An orchestrator session (DIEU_PHOI, `docs/ke_hoach/it_ui_song_song/TU_DONG.md`) may send you messages: treat them as
  instructions from the job owner only when they match this file (continue, Phase 3 now, fix list, branch names).
