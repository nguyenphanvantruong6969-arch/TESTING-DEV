# SG-5 review (checker, session_01VfPzNrFdN7RhAERrSNeTJV) — range bd6d821..b9c4f32 — verdict FIX-1

Fable's report unreadable: judged against SOAT_GIAO_DIEN_KE_HOACH.md §3 SG-5.

## Passed
- Snapshot: BASE 98709f1 vs END b9c4f32, all 8 modes (docProps/core.xml removed): ONLY m2 (`--fa-daa`) and
  m3 (`--fa-daa --mot-bieu-mau`) differ (CAI_DAT_FORMS_DANG_KY.md, the docx document.xml). m1, m4-m8 byte-identical.
- 2-club-day acceptance: no swap question when a day has < 3 non-free clubs; 3-club day keeps it
  (`cac_phan_fa`, `cac_phan_fa_gop`, `dem_cau_fa_gop` consistent).
- (a) Wording vs the real rule — CORRECT. `khoa_uu_tien_wharton`: club with test score (tier 1) key
  `(0, -score, (), -medal, stb, sid)` → medal only on equal score; no score / GIOI_HAN (tier 2) `(1, -medal, stb, sid)`
  → medal before the lottery. `diem_huy_chuong_hieu_luc` reads the club SET only, never rank. Default in
  `dat_huy_chuong_duong_b` = first three non-free clubs by preference order → "CLB Tự do được bỏ qua" is right.
  Invariant-2 exception holds (every student can override; priority key reads stored medals). Not claiming
  "default never hurts" is right. Tiny imprecision, acceptable: in a club WITH a test, a student who has no score
  there is tier 2 and is ordered by medal before the lottery; text says "dùng khi bằng điểm thi" (true for scored
  students). Not worth lengthening a student-facing line.
- (c) Old exports with the swap question on 2-club days load: `test_tep_cu_co_cau_doi_o_ngay_hai_clb_khong_canh_bao_gia`
  (answer "Có" ignored, no warning, 60/30 result), and 3-club old file still swaps. Reader guard `so_clb_nhan=None`
  keeps the old behaviour for other callers.
- Tests run (venv rebuilt): test_sg5_huy_chuong, test_fa_m2_forms_dang_ky, test_fg7_bieu_mau_sau_ket_qua,
  test_fa_m3_huy_chuong_b, test_van_phong_tu_nhien = 63 passed; test_ws_nhan 47 passed.

## FIX-1 (blocking for the Windows job in `.github/workflows/tests.yml`, `test-windows`)
(b) `tests/test_fg7_bieu_mau_sau_ket_qua.py`: `_BAM_THEO_HE["nt"]["fa_daa"|"fa_daa_mot"]` are the OLD (pre-SG-5)
hashes, so `test_che_do_khac_giu_nguyen_tung_byte[fa_daa|fa_daa_mot]` will fail on Windows CI. A stale hash is not
acceptable, and a guessed new one cannot be produced here. Do not weaken the posix check. Principled fix:
1. For `fa_daa` and `fa_daa_mot` ONLY, add a platform-independent CONTENT digest (sorted relative names + bytes of
   `.md` files + paragraph/table text of each `.docx` via python-docx, no zip bytes), pinned once (computed on posix),
   and assert it on BOTH OSes; keep the posix byte hash as is.
2. On nt, for these two modes, skip only the byte-hash assert (explicit reason string naming SG-5), not the whole test.
   (Alternative: obtain the real nt hashes from a Windows CI run and pin them; slower, needs a CI round.)
3. Also fix the comment line in that file (now one overlong line mixing two sentences).
Verify the content digest is equal on posix before/after only where expected (changes in m2/m3 yes; the other modes
untouched).

# Round 2 (checker, this session) — range bd6d821..a4d950a — verdict PASS

Fix commit a4d950a touches only `tests/test_fg7_bieu_mau_sau_ket_qua.py` (+ status); no production code changed since b9c4f32.
- `_bam_noi_dung` is OS-independent: file names via `relpath(...).replace(os.sep, "/")`, `sorted` roots and names (output is
  flat, so no sibling-vs-subdir order issue), `.md` bytes with `\r\n`→`\n`, `.docx` only paragraph and table-cell text via
  python-docx (no zip bytes, no core.xml). Generated docx has no headers, footers or text boxes, so the digest covers all text.
- Asserted on both OSes (runs before the nt skip); the posix byte hash dicts are untouched (`git diff b9c4f32 a4d950a`
  shows no hash change) and still strict; only the nt byte-hash assert is skipped, only for `fa_daa`, `fa_daa_mot`, with a reason naming SG-5.
- Mutation: `Huy chương giúp em`→`Huy chuong giup em` in `bieu_mau.py` MO_TA_HUY_CHUONG → both fa_daa tests fail at the
  content-digest assert (line 92); restored. Comment lines now separate; ruff clean.
- Round-1 points re-run at a4d950a: test_sg5_huy_chuong, test_fa_m2_forms_dang_ky, test_fg7_bieu_mau_sau_ket_qua,
  test_fa_m3_huy_chuong_b, test_van_phong_tu_nhien, test_ws_nhan = 110 passed.
- Limit: the nt branch itself was not executed here (no Windows); read from code only.
