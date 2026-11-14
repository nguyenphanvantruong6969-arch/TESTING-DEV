# Checker verdicts: FA-SC (branch claude/fa-sc-sua)

> Role: checker (Sonnet). Only this file is edited by the checker. English. Append one section per lot/round.

## L1 — reviewed b0614a3..cc2d9a4 — verdict: NO BUGS
- Related tests: `test_fa_sc_l1_danh_sach`, `test_mau_forms_thi_clb`, `test_fa_m3_chuyen`, `test_fa_m2_forms_dang_ky`,
  `test_fa_m9_nap_tep_forms`, `test_a13_12_tai_lieu` -> 95 passed. `ruff check` clean on changed files.
- Drills (60 students, fake data): d01 (student in CHUA_DANG_KY + 1 warning), d02 (student in "Thiếu ngày" = thu_4 + 1 warning),
  d03a (no longer blocked, typed ID replaced by roster ID via email, real ID kept in kiosk), d03b (stranger-ID warning, real ID
  has 5 results), d14 (0/60 without class, 6 class files) all flip as specified.
- Invariant 1: converter run on fake path-B data (60 students, 5 days) at base b0614a3 vs head WITHOUT the option: output dir
  identical (same file list; xlsx cell values equal sheet by sheet; EMAIL_MA_HS.csv cmp equal). Invariant 7: with roster,
  only the existing optional "Lớp" column is added to sheet "2. Học sinh" (layout shifts one column, as any file with a class);
  sheet "1. CLB", EMAIL_MA_HS.csv and BANG_DIEM sheets unchanged. Invariant 2/6: report + class fill only; kiosk untouched
  (diff has no kiosk file). Privacy: CHUA_DANG_KY.xlsx has only student ID, class, missing days (no score/STB).
- Own edge cases: header-only roster and roster without class_id -> clear LoiTepXuat (no output); duplicate roster row ->
  one warning; roster email upper-case and class with diacritics ("Lớp 10Ă2") -> fine; roster without/blank email column;
  collision without roster emails -> one line naming both emails (kiosk still refuses later at nap_so, as before);
  typed "hs005" vs roster "HS005" -> flagged as unknown ID; partial roster (20 of 30) -> 1 line per unknown ID, no crash.
- Notes (not bugs, outside spec): a roster email repeated on two different IDs is silently resolved to the first ID
  (`theo_email.setdefault`); consider a warning later. Unknown-ID student with no roster email also appears in "Chưa đăng ký".
