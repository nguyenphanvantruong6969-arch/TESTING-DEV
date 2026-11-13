Mode: SG_SONG_SONG person C
LOCK: LEAD session_01VfPzNuse9EfjuDwwt7335U 2026-11-13T15:55Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6
SNAPSHOT: in a clean worktree of BASE run every mode of `mau_forms_thi_clb/tao_mau_forms.py`
(`""`, `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--bien-the`, `--chi-thi`, `--phan-hoi`, `--sau-ket-qua`, `--tuan-3`),
each with `--ra <out>/m<i>` (i = 1..8 in that order). Notes: the default mode ignores `--ra` and writes
`NHAP_FORMS_THI_CLB.docx`, `MAU_XUAT_TU_FORMS.xlsx`, `CAI_DAT_FORMS.md` into `mau_forms_thi_clb/` (copy them into m1,
then `git checkout -- mau_forms_thi_clb/`); `--bien-the` exits non-zero on the stock `de_thi.json` (no
`de_thi_bien_the`) and writes nothing — expected. Unzip every .xlsx/.docx and delete `docProps/core.xml`, then
`diff -r` BASE-snapshot vs HEAD-snapshot. Deterministic (two BASE runs identical). Script used by the lead:
`snap.sh <worktree> <out>` — the loop above, nothing else.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-5 | DONE | 1 | bd6d821 | a4d950a | session_01VfPzNruBqHHaJZQcLRxRzS | session_01VfPzNvd9nsMJp4kwS7QzT8 (r2; r1 session_01VfPzNrFdN7RhAERrSNeTJV) | tests/test_sg5_huy_chuong.py, tests/test_fg7_bieu_mau_sau_ket_qua.py |
| SG-7 | DONE | 0 | 9709a20 | b4800ad | session_01VfPzNvgJo8vZQhB3sTbaQr | session_01VfPzNv27d7DuoAmjt9g79n | (UI tests, see review) |
| SG-9 | DONE | 1 | a1b6ecb | c266cae | session_01VfPzNud4JhboVzj5e8xu4E | session_01VfPzNt89iBAQw8naoMzV7d (r2; r1 session_01VfPzNt6qaZtDuK7uYC28bX) | tests/test_giao_dien_sg9_nut_ban.py |
| SG-12 | FIX-2 | 2 | e729ff1 | ca5bf76 | session_01VfPzNuP2CPBJGP9uHdXZyx (1st: session_01VfPzNs8qcCiQLCKtu6pP4g) | session_01VfPzNvabEwh2nAm7PHf7Jq (r2; r1 session_01VfPzNsvHqNsTacxhiYKg2y) | tests/test_sg12_tieu_de_thuan.py (+ see review) |

## Fix lists
### SG-5 FIX-1 (checker session_01VfPzNrFdN7RhAERrSNeTJV, docs/phien/sg_review/SG-5.md)
1. tests/test_fg7_bieu_mau_sau_ket_qua.py: for `fa_daa`, `fa_daa_mot` ONLY add a platform-independent content digest
   (sorted relative names + bytes of .md files + paragraph/table text of each .docx via python-docx), pinned once on
   posix, asserted on BOTH OSes; keep the posix byte hash as is.
2. On nt, for these two modes, skip only the byte-hash assert (reason string names SG-5), not the whole test.
3. Fix the overlong two-sentence comment line in that file.

### SG-9 FIX-1 (LEAD disagrees with checker PASS on two cheap points; checker notes 1-2 in docs/phien/sg_review/SG-9.md)
1. tests/test_giao_dien_sg9_nut_ban.py: make the `.catch` inside `chayNut` (and `chayTai`) provable — e.g. in the rejection test
   assert NO `unhandledrejection` reached the page (stub/count it) and exactly ONE error toast. Verify: removing that `.catch` must
   make the test fail.
2. js/12_chuan_bi_nap.js `chuyen` (`S.dang`) and the `goi` helper (`S5.dang`): reset the busy flag in the wrapper's `sauCung`
   (finally) so a synchronously thrown API call does not leave the step dead; add a UI test (API function that throws
   synchronously → second click makes a second call).

### SG-12 FIX-1 (checker session_01VfPzNsvHqNsTacxhiYKg2y, docs/phien/sg_review/SG-12.md)
1. `chuyen_forms_sang_phan_mem.doc_dang_ky_fa_forms` → `tim_clb` (nguyện vọng AND `-vang`): pass `ban_do` and the question code so the
   exact map answers first (as the ranking path does); AND make `xay_ban_do` reject options equal under `_chuan` (casefold+whitespace)
   in one question so the generator errors (i18n `forms_tieu_de_trung`-style). Test: two clubs "CLB Cờ vua"/"clb cờ vua" same day.
2. `docs/phien/sg_song_song/snap_c/conv_snap.py` makes `ruff check .` red (F401, SIM115): fix it (keep it as the recipe script).
3. Add a test proving the TITLE-collision branch in `xay_ban_do` (two days with the same name → "hai câu … cùng tiêu đề"); mutating
   `cau.setdefault(k, td.ma) != td.ma` must fail it.
(Optional, non-blocking: remove the stray blank lines in test_fa_m8_api.py / test_fa_m8_bo_bieu_mau.py.)

### SG-12 FIX-2 (checker session_01VfPzNvabEwh2nAm7PHf7Jq, docs/phien/sg_review/SG-12.md Round 2)
1. Limit the casefold/whitespace option refusal in `xay_ban_do` to PLAIN generation (flag off on the reader path `ban_do_chung` and
   in `--giu-ma`): coded reader + `--giu-ma` generator must accept a de with same-day clubs differing only by case, exactly as e729ff1.
   Test: (a) coded export of such a de read correctly by `doc_dang_ky_fa_forms`; (b) plain generation still raises LoiDeThi; mutating
   the flag fails (a) or (b).
2. `test_doc_dang_ky_ban_do_cua_cau_tra_loi_truoc_ten_trung_ma_clb_khac`: gold answer = `lua_chon_clb(b)`, assert `wp[b] == 60`, not A;
   mutation `tim_clb(tho_vang, "zz")` must fail it.

## Decisions
- WARNING: lead is not Opus (`get_session` reports claude-sonnet-5-5 at setup; the serving model may change).
- Fable's report artifact is unreadable from this account ("artifact not found") → red tests come from the spec text
  of `SOAT_GIAO_DIEN_KE_HOACH.md` and the finding as reproduced in code (SG_SONG_SONG 2.1 fallback).

- SG-7: helper placed in js/00_nen.js (no A/B edits there). Step-4 warning prefix `ma:` (internal code) dropped from visible text; old `slice(0,30)` cap replaced by the 5-example rule. Old i18n keys canh_bao_gom/xem_dau/thu_gon left (outside SG-C block).
- SG-7: dead leftovers outside the SG-C blocks (i18n keys `canh_bao_gom`, `canh_bao_xem_dau`, `canh_bao_thu_gon`; old `.canh-bao-nhom` flex rule in style.css) are left for lead A at integration, to avoid editing outside C's marker blocks. The FG-6 run-log grouping (`showLog`) stays as is: same rule in spirit, not one of SG-7's two surfaces.
- SG-9 (seen by checker, out of C scope): the khiếu nại error text shows the internal session name `__mac_dinh__` → for person A (SG-4 owns `gui_khieu_nai`).
- SG-9: checker r2 recommends replacing the static source-text check for `S.dang` (`chuyen`, js/12) with a UI test (sync-throwing
  `chuyen_tep_forms`, seeded like `test_giao_dien_fa_m9_nap.py`); behaviour verified correct by the checker's scratch test. Non-blocking;
  left as an optional improvement for lead A / a later item (not worth a third round).
- SG-12 technical choices (lead): (1) the title→code map is derived from `de` by ONE shared function in `bieu_mau.py` (same title functions
  as the generator); the generator writes it as `MAP_*.json` beside each form, readers use the same function, so the kiosk needs no extra
  upload; (2) a generator flag keeping the old coded titles, so that mode is byte-identical to BASE and this semester's run can keep codes
  (spec D2 note "keep a if time is short"); default = plain titles as approved (D2 = b).
- SG-12 test mode (lead instruction 1): the global autouse coded-mode fixture is gone. `tests/conftest.py` (shared file, mention to lead A) has ONE small opt-in autouse fixture `tieu_de_giu_ma` that does nothing unless the test carries `@pytest.mark.giu_ma` (marker declared in `pyproject.toml`); it imports `bieu_mau` lazily only then. Everything else, incl. UI/subprocess tests, runs in the DEFAULT (plain) mode. `tieu_de_thuan` marker removed. Opted in PER TEST (15 tests, stricter than per module), found by running the 51 related files without any fixture: test_demo_t4m (1: asserts coded club-form codes), test_fa_m2_forms_dang_ky (2: codes in question text), test_fa_m2b_mot_bieu_mau (2: asserts coded titles in the one-form docx/README), test_fa_m6b_sau_ket_qua (2: layout test greps `[code]` tags), test_fa_m7_nguon_mot_lan (1: finds questions by code tag), test_fa_m9_nap_tep_forms (1: detection of a coded old export), test_mau_forms_thi_clb (1: ranking columns read by code), test_sg5_huy_chuong (2: finds the gold question by its `[thu_2-vang]` tag / old export), test_t4m_chi_thi (1) and test_t4m_cong_thi (1) and test_t4m_day_du (1): assert `[code]` text in the generated docx. All are tests OF the coded form (old exports still load).
- SG-12 real bug found by removing the fixture (it had hidden it): `tao_bo_bieu_mau` (bo bieu mau, both paths) crashed in default mode because the teacher-filled CLB setup form (phieu CLB) went through `ghi_docx_chi_thi` -> `ghi_ban_do`, and its titles are plain strings (no codes, nothing to map). Fix: `ghi_docx_chi_thi(..., ghi_map=True)`; `sinh_phieu_clb` passes False (no MAP for it). Regression test in test_sg12_tieu_de_thuan.py (red before the fix, green after). `tests/test_fa_m8_api.py` / `test_fa_m8_bo_bieu_mau.py` (23 tests that were failing) now run in default mode with NO marker; the file-list test of the bo now expects the MAP files when not in giu-ma mode.
- SG-12: the 3 "real failures" of the handoff: test_t4m_bo_dung_bk34::test_04 passes with no fixture; chi_thi q2 and cong_thi q4a assert `[code]` text of the generated docx, so they are opt-in tests. Committed files in mau_forms_thi_clb/: regenerated ONLY `NHAP_FORMS_CHI_THI.docx` (+ new `MAP_NHAP_FORMS_CHI_THI.json`) with `tao_mau_forms.py --chi-thi`; `NHAP_FORMS_THI_CLB.docx`, `MAU_XUAT_TU_FORMS.xlsx`, `CAI_DAT_FORMS.md`, `CAI_DAT_FORMS_CHI_THI.md` were already equal to a fresh default run (docProps/core.xml excluded). `NHAP_FORMS_6_PHAN.docx` is made by a different script (tao_nhap_forms_6_phan.py), untouched.

## For Truong
SG-5 wording (vi; sits in the gold-medal question of each `--fa-daa*` registration form, after the question text; en: none, forms are Vietnamese-only):
"Huy chương giúp em được ưu tiên hơn bạn khác ở CLB đó: CLB có xét điểm thi thì chỉ dùng khi bằng điểm thi, CLB không xét điểm thi thì dùng trước khi bốc thăm. Em không chọn gì thì hệ thống tự đặt vàng cho nguyện vọng 1, bạc cho nguyện vọng 2, đồng cho nguyện vọng 3 (CLB Tự do không có huy chương nên được bỏ qua)."
Changed vs the brief: (1) "medals only break ties after the test score" is true only for clubs WITH scores; in `fa_daa` a Giới hạn club orders by medal BEFORE the lottery (key `(1, -medal, stb)`), so the text says both. (2) "leaving default never hurts" is not provable (not a dominant strategy), so it is NOT claimed. (3) Default is "first/second/third NON-free club", so the text says free clubs are skipped.
Placement is in the question title because Quick Import has no per-section description field (untested on real Forms).


SG-12 (from the previous coder): other consumers of the codes, untouched: TAO_GOOGLE_FORM.gs + tao_google_forms.py (the Google Forms path stays coded), skill xu-li-raw-forms, docs (README of mau_forms_thi_clb updated; GHI_CHU_GIAO_VIEN.md, DINH_DANG_RAW.md, docs/* not). Not tried on real Microsoft Forms (TH). The Windows (nt) byte hashes of the four fg7 modes are not re-pinned (the content digest is asserted on both OS). Phieu thiet lap CLB (teacher form) keeps its plain titles and has no MAP file by design. This semester's run can keep codes with `--giu-ma`.

## SG-12 snapshot recipe (checker can rebuild; scripts in docs/phien/sg_song_song/snap_c/)
Worktrees: `git worktree add --detach W_pre e729ff1` (pre-SG-12) and `W_head <HEAD>`; scripts need `PY` = the venv python (edit the path in snap.sh).
1. Generator: `snap.sh W_pre out_pre`, `snap.sh W_head out_gm --giu-ma`, `snap.sh W_head out_def`; `diff -rq out_pre out_gm` -> only `m1/MAP_NHAP_FORMS_THI_CLB.json` (a COMMITTED file snap.sh copies; the generator writes no MAP in giu-ma mode); `diff -rq out_pre out_def` -> only forms carrying codes + MAP_*.json + MAU_XUAT xlsx + CAI_DAT md bullets (m3/m6/m7/m8). Last run: giu-ma == pre for all 8 modes; pre vs BASE 98709f1 differ only m2/m3 (SG-5). Do not run snap.sh on the real tree (it does `git checkout -- mau_forms_thi_clb/`).
2. Converter: `python -I conv_snap.py W_pre cs_base.json base`; `... W_head cs_coded.json coded`; `... W_head cs_plain.json plain`; `cmp` all three -> identical (sample export m1 + chi-thi). More paths (path A/B, phan hoi, khieu nai, tuan 3, variants) are asserted by tests/test_sg12_tieu_de_thuan.py.
3. Bo bieu mau (both paths): `python -I snapbo.py W_pre bo_pre`; `snapbo.py W_head bo_gm giu`; `snapbo.py W_head bo_def`; compare trees with docProps/core.xml dropped: giu-ma == pre (58 files); default = same 58 + 25 MAP files, 32 changed (forms with codes + 00_DOC_TRUOC.md file list); phieu CLB and XEM_LAI_DAP_AN unchanged.

## Log
- 2026-11-13T16:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U setup branch claude/sg-c from BASE 98709f1
- 2026-11-13T15:55Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 CODING start 7f7b5ca coder session_01VfPzNruBqHHaJZQcLRxRzS
- 2026-11-13T16:01Z CODER session_01VfPzNruBqHHaJZQcLRxRzS SG-5 READY 7b7109a red:3 of 6 new tests failed (3 false 'chỉ còn 1 CLB' warnings counted, no description, swap present on 2-club day) mutation:forcing swap on / disabling reader day-size guard -> 2 new tests fail, restored
- 2026-11-13T16:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 READY accepted, range bd6d821..b9c4f32 (Start corrected to the assign commit); CHECKING
- 2026-11-13T16:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 checker r1 session_01VfPzNrFdN7RhAERrSNeTJV
- 2026-11-13T16:34Z CHECKER session_01VfPzNrFdN7RhAERrSNeTJV SG-5 FIX-1 (wording/snapshot/old-exports pass; nt hashes of fa_daa/fa_daa_mot stale -> content digest on both OS, see docs/phien/sg_review/SG-5.md)
- 2026-11-13T16:52Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 FIX-1 agreed, sent to coder session_01VfPzNruBqHHaJZQcLRxRzS
- 2026-11-13T16:52Z CODER session_01VfPzNruBqHHaJZQcLRxRzS SG-5 FIX-1 READY: (1) content digest _bam_noi_dung (names + .md bytes CRLF-normalised + docx paragraph/table text) pinned for fa_daa, fa_daa_mot, asserted on both OSes, posix byte hash kept; (2) on nt only the byte-hash assert is skipped (reason names SG-5); (3) comment fixed into separate lines, obsolete 'nt STALE' note removed from For Truong. mutation: changing the description text -> content-digest fail, restored
- 2026-11-13T17:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 FIX-1 READY a4d950a; checker r2 session_01VfPzNvd9nsMJp4kwS7QzT8
- 2026-11-13T17:11Z CHECKER session_01VfPzNvd9nsMJp4kwS7QzT8 SG-5 PASS (round 2, a4d950a; see docs/phien/sg_review/SG-5.md)
- 2026-11-13T17:40Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 DONE (lead review: diff read; 110 item/related tests pass; ruff clean; kiem_nhanh 7/7 60 cases; generator diff only m2/m3 --fa-daa* registration files) a4d950a
- 2026-11-13T17:26Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 CODING start eb6ef50 coder session_01VfPzNvgJo8vZQhB3sTbaQr
- 2026-11-13T17:31Z CODER session_01VfPzNvgJo8vZQhB3sTbaQr SG-7 READY b4800ad red:3 of 4 new UI tests failed (step 4 and import panel had no grouping/5-example/'và N nữa', old button style, no shared helper) mutation:removing the 5-example slice in veCanhBaoGom -> 2 UI tests fail, restored
- 2026-11-13T17:48Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 READY b4800ad accepted (range 9709a20..b4800ad); checker r1 session_01VfPzNv27d7DuoAmjt9g79n
- 2026-11-13T17:51Z CHECKER session_01VfPzNv27d7DuoAmjt9g79n SG-7 PASS (see docs/phien/sg_review/SG-7.md)
- 2026-11-13T18:14Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 DONE (lead review: diff read; 17 UI tests pass in Chromium; own mutation 'và N nữa' count -> 2 fail, restored; checker kiem_nhanh 7/7, diff JS/CSS/i18n only) b4800ad
- 2026-11-13T18:11Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 CODING start 1bf5e85 coder session_01VfPzNud4JhboVzj5e8xu4E
- 2026-11-13T18:29Z CODER session_01VfPzNud4JhboVzj5e8xu4E SG-9 READY 98908e1 red:14 of 16 new tests failed on base (no busy state/double-click guard/.catch, 71 bare .then) mutation:removing nut.disabled=true in chayNut -> 5 double-click tests fail, restored; related: 606 UI/label tests pass, ruff clean
- 2026-11-13T18:38Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 READY 98908e1 accepted (range a1b6ecb..98908e1); checker r1 session_01VfPzNt6qaZtDuK7uYC28bX
- 2026-11-13T18:59Z CHECKER session_01VfPzNt6qaZtDuK7uYC28bX SG-9 PASS (a1b6ecb..98908e1; 495 UI tests passed 0 skipped, own mutation: removing .catch survives because unhandledrejection shows same toast -> notes only; see docs/phien/sg_review/SG-9.md)
- 2026-11-13T19:06Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 checker PASS overruled -> FIX-1 (2 points), sent to coder session_01VfPzNud4JhboVzj5e8xu4E
- 2026-11-13T19:08Z CODER session_01VfPzNud4JhboVzj5e8xu4E SG-9 FIX-1 READY c266cae (1) rejection test now counts unhandledrejection (must be 0) and exactly one .toast.is-error; new chayTai test; mutation: removing .catch in chayNut -> 5 fail, in chayTai -> 1 fail, restored. (2) chuyen (S.dang) and goi (S5.dang) reset the flag in sauCung; new UI test: synchronously throwing API at step 5 then second click -> 2 calls; mutation: removing S5 sauCung -> 2 fail, restored; S.dang covered by a static check only (UI path needs uploaded files). related: 70 UI/label tests pass, ruff clean
- 2026-11-13T19:27Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 FIX-1 READY c266cae; checker r2 session_01VfPzNt89iBAQw8naoMzV7d
- 2026-11-13T19:43Z CHECKER session_01VfPzNt89iBAQw8naoMzV7d SG-9 PASS (round 2, 98908e1..c266cae; own mutations: .catch in chayNut/chayTai now fail tests, S5.dang UI test + S.dang static test fail on removal; 498 UI tests 0 skipped; ruff clean; kiem_nhanh 7/7; note: S.dang UI test is feasible, see docs/phien/sg_review/SG-9.md Round 2)
- 2026-11-13T19:50Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 DONE (lead review: wrapper read; 27 SG-9/FG-4/SG-7 UI tests pass in Chromium; checker r2 own mutations + 498 UI tests, kiem_nhanh 7/7; JS-only diff) c266cae
- 2026-11-13T19:50Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 CODING start 2ad6081 coder session_01VfPzNs8qcCiQLCKtu6pP4g
- 2026-11-13T20:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 coder 1 stopped at context limit (handoff 1be392a, docs/phien/claude__sg-c.md); coder 2 session_01VfPzNuP2CPBJGP9uHdXZyx continues (+ lead: conftest autouse giu-ma -> opt-in)
- 2026-11-13T21:35Z CODER session_01VfPzNuP2CPBJGP9uHdXZyx SG-12 READY f6939af red:default-mode bo bieu mau crashed (phieu CLB titles not TieuDe) -> new regression test red before fix, plus 38 old tests red when the global fixture was removed (23 of them = that bug) mutation:removing ghi_map=False for phieu CLB -> new test + 23 m8 tests fail (restored); earlier mutations by previous coder (2) kept. related batch (51 files + ws_nhan + van_phong + tai_lieu) 824 passed, 1 failed = the known test_ban_do_ma_so_tep_test_la_so_that; UI (23 forms/nap/theo doi files + fa_m8_bo, Playwright 1.63.0, Chromium) 157 passed 0 skipped; PLAIN exports load in the browser through the kiosk import (fa_m9_nap UI tests run in default plain mode, data in tmp outside repo); ruff clean; kiem_nhanh 7/7 (60 cases, 20 seeds)
- 2026-11-13T21:15Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 READY f6939af accepted (range e729ff1..f6939af); checker r1 session_01VfPzNsvHqNsTacxhiYKg2y
- 2026-11-13T21:29Z CHECKER session_01VfPzNuse9EfjuDwwt7335U-checker SG-12 FIX-1 (casefold club-name collision mis-reads plain registration in tim_clb; ruff red on snap_c/conv_snap.py at HEAD; see docs/phien/sg_review/SG-12.md)
- 2026-11-13T21:29Z CHECKER session_01VfPzNsvHqNsTacxhiYKg2y SG-12 FIX-1 (correction: this is the real checker session id; the previous CHECKER line carried a wrong id; details docs/phien/sg_review/SG-12.md)
- 2026-11-13T22:00Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 FIX-1 agreed (+ lead adds checker notes 1-2 as points 2-3), sent to coder session_01VfPzNuP2CPBJGP9uHdXZyx
- 2026-11-13T22:35Z CODER session_01VfPzNuP2CPBJGP9uHdXZyx SG-12 FIX-1 READY ca5bf76 (1) `doc_dang_ky_fa_forms.tim_clb(chu, ma_cau)` now asks the question's own map first (`<buoi>-nvK`, `<buoi>-vang`) via `ma_trong_lua_chon(chu, ban_do, ma_cau)`; `xay_ban_do` rejects two options equal under `_chuan` in one question ("chỉ khác hoa/thường hay khoảng trắng", same LoiDeThi path). Tests (red first, verified by stashing the source): test_hai_clb_chi_khac_hoa_thuong_trong_mot_ngay_bi_tu_choi_o_bo_sinh, test_doc_dang_ky_ban_do_cua_cau_tra_loi_truoc_ten_trung_ma_clb_khac (club B's name == club A's id: old order read A for NV and gold). Note: the checker's exact repro ("CLB Cờ vua"/"clb cờ vua") is now refused by the generator, so it cannot reach the reader. (2) snap_c/conv_snap.py ruff-clean (imports sorted, hashlib dropped, `with open`); still runs. (3) test_hai_buoi_cung_ten_la_loi_cung_tieu_de_cau; mutation `if cau.setdefault(k, td.ma) != td.ma` -> `if False` makes it fail (restored). Stray blank lines removed (test_fa_m8_api.py back to e729ff1; m8_bo only the 3 intended lines). Reruns: related batch 828 tests, 827 passed, 1 failed = known test_ban_do_ma_so_tep_test_la_so_that; UI 157 passed 0 skipped; ruff clean at HEAD; kiem_nhanh 7/7; generator snapshot: `--giu-ma` == e729ff1 for all 8 modes (only the committed m1 MAP file differs), default diffs only coded forms + MAP + xlsx header + md bullets; converter base == coded == plain identical; bo bieu mau giu-ma == pre (58 files), default +25 MAP, 32 changed.
- 2026-11-13T22:31Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 FIX-1 READY ca5bf76; checker r2 session_01VfPzNvabEwh2nAm7PHf7Jq
- 2026-11-13T22:39Z CHECKER session_01VfPzNvabEwh2nAm7PHf7Jq SG-12 FIX-2 (round 2: refusal in xay_ban_do breaks the coded reader for a de with same-day clubs differing by case; -vang map-first not proven by a test; everything else passes, see docs/phien/sg_review/SG-12.md Round 2)
- 2026-11-13T23:04Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-12 FIX-2 agreed, sent to coder session_01VfPzNuP2CPBJGP9uHdXZyx
