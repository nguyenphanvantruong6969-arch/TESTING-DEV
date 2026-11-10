# CHANGELOG

## 2026-11-10 — AI-LOG: nhật ký AI chỉ từ dữ liệu trong repo (Truong yêu cầu)

- `docs/nhat_ky_ai/NHAT_KY_AI.md` (mới, thay `NHAT_KY_AI_TAI_KHOAN_TRUONG.md` lấy từ lịch sử phiên): dựng CHỈ từ repo — 7 lời Truong lưu nguyên văn (kèm `FA_DAA_VISION.md`), 21 quyết định của Truong theo tiêu đề `CHANGELOG.md`, 12 luồng việc theo tệp bàn giao (phiên cha chép ô Session log, phiên con lồng bên dưới một dòng), bảng 70 phiên có dòng `Claude-Session` trong git, và phần trước lịch sử git. Không bình luận hay kết luận nghiên cứu.
- `docs/nhat_ky_ai/dung_nhat_ky_ai.py` (mới): script dựng lại tệp trên; chạy hai lần cho cùng kết quả; câu nguyên văn được kiểm có trong tệp nguồn. Nằm trong `docs/` nên không tính vào độ phủ.
- `docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md` + `NHAT_KY_AI.docx` (Truong yêu cầu bản dễ đọc): tiếng Việt thường, bảng giải thích từ ngữ, 10 giai đoạn (mục tiêu / Truong quyết định / phiên chính / phiên phụ / kết quả), lời nguyên văn, giới hạn; Word A4 4 trang. `xuat_word.py` (mới) chuyển .md sang .docx có định dạng.
- `docs/nhat_ky_ai/NHAT_KY_AI_DAY_DU.md` (mới, Truong yêu cầu bản vừa dễ đọc vừa đủ chi tiết): mục 1–6 là bản dễ đọc, mục 7 dựng tự động xếp toàn bộ chi tiết vào 10 giai đoạn (24 quyết định, 146 mục `CHANGELOG.md`, 160 dòng phiên chính/phụ, 70 phiên có lưu mã; không sót mục nào). `NHAT_KY_AI.docx` nay dựng từ bản này: A4, 21 trang.

## 2026-11-10 — FA-CI3: CI Windows cài python-docx (PR #14, Truong chọn)

- `.github/workflows/tests.yml` job Windows và job test của `build-windows-exe.yml`: cài thêm `python-docx>=1.1,<2` (cùng ràng buộc với `requirements-dev.txt`). 9 test FA ghi tệp `.docx` (`test_fa_m2_forms_dang_ky.py`, `test_fa_m4_phan_tich.py`, `test_fa_m5_bo_dung.py`, `test_fa_n4_mot_de_khong_thi_lai.py`) chạy thật trên Windows thay vì đỏ `ModuleNotFoundError`; không test nào bị bỏ qua.

## 2026-11-10 — FA-CI2: test giao diện T3-19 hết chập chờn (CI Linux PR #14)

- `tests/test_giao_dien_t3_l3.py` `test_tai_bang_theo_clb_va_theo_ma_co_tim`: chờ bảng hiện đúng số thành viên CLB A (lấy từ `get_danh_sach_clb`) thay vì chỉ chờ `#kqBang` hiện; bảng "theo lớp" vẽ trước vẫn hiện tới khi danh sách CLB về, nên test có lúc đếm 2 dòng cũ. Tái hiện bằng độ trễ 1,5 giây cho `get_danh_sach_clb`: test cũ đỏ, test mới xanh; 5 lần liền xanh. Lỗi có sẵn từ trước PR, không do FA-DAA.

## 2026-11-10 — FA-CI1: sửa CI đỏ của PR #14 (Windows + văn phong)

- `du_lieu_test/mo_phong_fa_daa.py`, `mau_forms_thi_clb/so_sanh_suc_chua.py`: `main` chuyển stdout/stderr sang UTF-8 (`reconfigure`, như `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py`); console Windows cp1252 làm hai script này ném `UnicodeEncodeError` khi in tiếng Việt. Tái hiện trên Linux bằng `PYTHONIOENCODING=cp1252` (4 đỏ trước, xanh sau).
- `i18n_errors.py` (+ `i18n_loi.js` sinh lại): câu tiếng Anh của `bien_ban_chua_boc_tham` bỏ từ nội bộ "seed" (FA-9). `i18n.js`, `index.html`: nút biên bản ghi "bản in và Excel" / "printable page and Excel" thay chữ HOA "HTML" (FA-9, FA-9b). Cả hai do `tests/test_van_phong_tu_nhien.py` bắt.
- Không test nào bị bỏ qua hay tắt.

## 2026-11-10 — FA-P2: nhập tại chỗ, huy chương mặc định vẫn lưu khi người nhập sang em khác giữa lúc lưu (soát đêm 5)

- `js/04_nhap_tai_cho.js`: nút lưu nguyện vọng gọi `hcTheoNguyenVong` cả khi em vừa lưu không còn mở; `hcTheoNguyenVong` vẫn tính và gọi `submit_huy_chuong` cho đúng em đó, chỉ vẽ lại Bước 3 khi em đó còn mở; câu nhắc "đã chỉnh tay" của em đang mở không bị xoá. Trước đây em đó có nguyện vọng mà không có huy chương nào và lần chạy xếp sau không báo gì (FA-N2, đêm 4).
- Test mới: 2 ca Chromium trong `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` (giữ `submit_preferences` hay `get_student_entry_state` của em trước; đỏ trước; 2 đột biến bắt được; 5 lần liền không chập chờn).

## 2026-11-10 — FA-P1: biên bản bốc thăm bản Excel không nhận công thức (soát đêm 5)

- `fa_bien_ban.py` `ghi_xlsx`: ô mà openpyxl hiểu là công thức (tên kỳ hay tên buổi mở đầu `=`, `+`, `-`, `@`) được ép về chữ, giữ nguyên văn (`data_type = "s"`, `quotePrefix`), như `so_excel.Trang.o`. Lỗi do FA-9b (đêm 5).
- Test mới: 2 test trong `tests/test_fa_bien_ban.py` (đỏ trước: có thẻ `<f>`; đột biến bỏ dòng ép kiểu bắt được).

## 2026-11-10 — FA-9b: biên bản bốc thăm bản Excel (đêm 5, Truong duyệt)

- `fa_bien_ban.py` `ghi_xlsx` (cùng bản ghi với HTML, không mã/tên học sinh); `api_xuat.py` `export_bien_ban_boc_tham` ghi thêm `.xlsx` cạnh `.html` (không ghi đè tệp cũ), trả `path_xlsx`; nút ở thẻ Kết quả báo cả hai tệp (`i18n.js`, `index.html`, `js/03_ket_qua.js`).
- Test mới: 5 test trong `tests/test_fa_bien_ban.py` (đỏ trước; 3 đột biến bắt được) + kiểm tệp .xlsx trong test Chromium của `tests/test_giao_dien_fa_ket_qua.py`.

## 2026-11-10 — FA-O1: lý do kết quả sắp theo thứ tự ngày (đêm 5)

- `api_xuat.py` `_doc_ly_do_moi_nhat`: sắp các dòng theo `khoa_sap_buoi` (cùng khoá với `COLLATE THU_TU_BUOI`), không theo chuỗi thường; `chu_nhat` đứng sau `thu_2` ở `ket_qua_ly_do.csv` và cột "Lý do". Lỗi do bản sửa FA-N1 gây ra (soát đêm 4).
- Test mới: 1 test trong `tests/test_fa_n1_ly_do_mot_phan.py` (đỏ trước khi sửa; đột biến bắt được). Vá luôn lỗ hổng FA-O2.

## 2026-11-09 — FA-10: mô phỏng so sánh chế độ cũ và FA-DAA, hành vi hai kỳ của D1 (đêm 4)

- `du_lieu_test/mo_phong_fa_daa.py` (mới, không đụng phần mềm): cùng dữ liệu sinh có hạt giống, chạy chế độ cũ (điểm thi + hai quỹ) và `chay_fa_daa`; in bốn bảng: %NV1 / %top 2 / %không CLB, % dòng theo lý do, % thua bốc thăm theo hành vi (lười / thật thà / chiến lược), và bảng hai kỳ D1 (em xếp CLB Giới hạn hot nhất lên NV1 cố ý; không bù và có bù — bù chỉ mô phỏng bằng cách xếp em lên đầu bốc thăm kỳ 2). Mỗi bảng ghi "SỐ LIỆU MÔ PHỎNG"; KHÔNG có câu nhận định. D1 chưa cài vào phần mềm.
- Test mới: `tests/test_mo_phong_fa_daa.py` (9).

## 2026-11-09 — FA-9: biên bản bốc thăm có người chứng kiến (đêm 4)

- `fa_bien_ban.py` (mới, hàm thuần): `sha256_stb`, `tao_ban_ghi`, `html_bien_ban`. `api_xuat.py` `export_bien_ban_boc_tham` → `bien_ban_boc_tham.html` (kỳ, thời điểm, dấu vân tay dữ liệu, hạt giống, SHA-256 danh sách (mã HS, số bốc thăm) đã sắp, số liệu từng buổi, thứ tự buổi lễ, dòng ký; không tên/mã học sinh; cảnh báo nếu dữ liệu đã sửa sau lần chạy). Chỉ đọc, không đổi schema/CSV. `i18n_errors.py` + `i18n_loi.js`: `bien_ban_chua_boc_tham`. Nút "Xuất biên bản bốc thăm" ở thẻ Kết quả (chỉ khi FA bật): `index.html`, `js/03_ket_qua.js`, `i18n.js`.
- Test mới: `tests/test_fa_bien_ban.py` (9) + 1 test Chromium trong `tests/test_giao_dien_fa_ket_qua.py`.

## 2026-11-09 — FA-N4: cảnh báo CLB chỉ có một đề thì không thi lại được (đêm 4)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: em bị gắn cờ làm quá nhanh ở CLB chỉ có một đề → cảnh báo "không có đề thi lại; giữ điểm bài đầu" (thay câu hứa thi lại). `mau_forms_thi_clb/tao_mau_forms.py`: `CAI_DAT_FORMS_BIEN_THE.md` có thêm dòng nói rõ. CLB có từ hai đề: không đổi.
- Test mới: `tests/test_fa_n4_mot_de_khong_thi_lai.py` (3).

## 2026-11-09 — FA-N3: câu báo rõ khi bật FA mà tắt điểm quyết tâm (đêm 4)

- `cau_hinh_ws.py` `FaCanDiemQuyetTam(ValueError)`, `api_workspace.py` bắt riêng, `i18n_errors.py` + `i18n_loi.js`: mã `fa_can_diem_quyet_tam` (song ngữ) thay lỗi chung `ws_du_lieu_sai` ở bước luật (tạo và sửa cấu hình). Lỗi luật khác vẫn là lỗi chung.
- Test mới: `tests/test_fa_n3_loi_diem_quyet_tam.py` (5); sửa kỳ vọng `tests/test_giao_dien_fa_cai_dat.py` (câu mới) và danh sách mã mới `tests/test_ws_nhan.py`.

## 2026-11-09 — FA-N2: màn nhập tại chỗ lưu huy chương mặc định và đi theo thứ tự mới (đêm 4)

- `js/04_nhap_tai_cho.js` (`hcTheoNguyenVong`), `index.html` (`hcNhacDaChinh`), `i18n.js` (`hc_nhac_da_chinh`): sau khi lưu nguyện vọng ở workspace FA, mỗi ngày: chưa có huy chương → lưu mặc định D2; huy chương = mặc định của thứ tự cũ và thứ tự đổi → lưu mặc định mới; đã chỉnh tay → giữ nguyên + câu nhắc. Chỉ gọi `submit_huy_chuong`; không suy diễn ở máy chủ, không đổi schema.
- Test mới: `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` (3, Chromium chạy thật).

## 2026-11-09 — FA-N1: lý do theo từng buổi sau khi chạy lại một phần (đêm 4)

- `api_xuat.py` `_doc_ly_do_moi_nhat`: mỗi buổi lấy lý do của lần chạy mới nhất CÓ chạy buổi đó (`run_history.buoi_da_chay`); buổi mà lần đó không phải FA thì bỏ và báo `canh_bao` (`fa_ly_do_thieu_buoi`); chỉ lỗi `fa_chua_co_ly_do` khi không buổi nào có lý do. `i18n_errors.py` + `i18n_loi.js`: mã mới.
- Test mới: `tests/test_fa_n1_ly_do_mot_phan.py` (3). FA tắt: không đổi.

## 2026-11-09 — FA-SOAT3: soát đêm 3 và mở đêm 4 (chỉ tài liệu, chưa sửa lỗi)

- `docs/phien/bao_cao_dem/2026-11-09_soat_dem3.md`: kết luận GO; FA-N1 (chạy lại một ngày làm mất lý do của ngày khác, đã tái hiện), FA-N2 (màn nhập tại chỗ không lưu huy chương mặc định, đã tái hiện), FA-N3, FA-N4.
- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §7: spec đêm 4 (FA-N1..N4, FA-9, FA-10). `docs/phien/CHAY_DEM_FA_DAA.md`: giao thức đêm 4. `docs/phien/claude__keen-ride-72sa7t.md`: Plan đêm 4.

## 2026-11-09 — FA-UI-5: mục hướng dẫn sử dụng "Xếp theo loại CLB và huy chương" (đêm 3, chỉ tài liệu)

- `HUONG_DAN_SU_DUNG.md` §15 (mới) + mục lục: bật ở bước luật (cần điểm quyết tâm), bốn cột mới của Sổ nhập và trang Giữ chỗ, bước huy chương, cột Lý do và `ket_qua_ly_do.csv`, `bang_nhu_cau.csv`.
- Test mới (trong tệp cũ): `tests/test_fa_m6_tai_lieu.py` `test_fa_ui_5_huong_dan_su_dung_co_muc_xep_theo_loai_clb`.

## 2026-11-09 — FA-UI-4: câu lý do ở thẻ kết quả và hai nút xuất (đêm 3)

- `api_xuat.py`: `get_ly_do_ket_qua` (mới: câu giải thích của lần chạy mới nhất theo học sinh và buổi; FA tắt thì `fa_bat` false); `_doc_ly_do_moi_nhat` và `_cau_cua_dong` dùng chung với `_export_ly_do_da_khoa` (cùng kết quả như trước).
- `index.html`, `js/03_ket_qua.js` (`veCotLyDo`): cột "Lý do" và nút `#btnXuatLyDo` (`export_ly_do_csv`), `#btnXuatNhuCau` (`export_bang_nhu_cau`) chỉ khi FA bật; tắt thì không cột, nút ẩn. `i18n.js`: chữ vi + en.
- Test mới: `tests/test_giao_dien_fa_ket_qua.py` (3 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 221 tệp test.

## 2026-11-09 — FA-UI-3: bước "Huy chương" ở màn nhập tại chỗ (đêm 3)

- `api_quan_ly.py`: `get_student_entry_state` thêm khoá `huy_chuong` khi FA bật (`_trang_thai_huy_chuong`: huy chương đã lưu, loại và buổi của từng CLB trong nguyện vọng, khoá). Tắt: phản hồi như cũ.
- `index.html`, `js/04_nhap_tai_cho.js` (`renderHuyChuongStep`, `hcDoi`, `hcCapNhatNhac`, `hcThuThap`): FA bật thì bước 3 là ba ô vàng / bạc / đồng mỗi ngày thay cho điểm quyết tâm; điền sẵn theo thứ tự nguyện vọng, bỏ CLB Tự do (D2, chỉ ở lớp đăng ký); chọn CLB đang có huy chương khác thì đổi chỗ (đủ 6 cách đặt); câu nhắc V§6.1 khi vàng ở CLB Tuyển chọn; lưu qua `submit_huy_chuong`, lỗi server hiện ra. `i18n.js`: chữ vi + en.
- Test mới: `tests/test_giao_dien_fa_huy_chuong.py` (5 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 220 tệp test.

## 2026-11-09 — FA-UI-2: cột FA trong bảng CLB ở thẻ Quản lý (đêm 3)

- `api_quan_ly.py` (`list_clubs_admin`): khi FA bật, mỗi CLB thêm `loai`, `diem_san`, `so_toi_thieu`, `suc_chua_phong`, `n_giu_cho`; tắt thì phản hồi như cũ.
- `js/05_quan_ly.js` (`veCotFaBangClb`, `oFaClb`): năm cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, Giữ chỗ chỉ khi có dữ liệu FA; tắt thì không thêm phần tử nào. `i18n.js`: `th_fa_*`, `fa_loai_*` (vi + en).
- Test mới: `tests/test_giao_dien_fa_quan_ly.py` (3 ca Chromium). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 219 tệp test.

## 2026-11-09 — FA-UI-1: công tắc "Xếp theo loại CLB và huy chương" khi tạo không gian làm việc (đêm 3)

- `js/075_workspace.js`: bước luật có ô `#wzFaDaa` (tắt sẵn, lấy theo mẫu), hàng xem lại `#rvFaDaa`; chỉ gửi `rules.fa_daa: true` khi bật (tắt: cấu hình gửi đi như cũ); bật mà tắt điểm quyết tâm thì backend từ chối bằng lỗi sẵn có `ws_du_lieu_sai`, hiện trên màn hình. `wsApDungCauHinh` đặt `FA_BAT` (khai báo ở `js/05_quan_ly.js`) cho các màn FA sau.
- `i18n.js`: `ws_r_fa_daa`, `ws_r_fa_daa_ngan`, `ws_r_fa_daa_ghi_chu` (vi + en). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 218 tệp test.
- Test mới: `tests/test_giao_dien_fa_cai_dat.py` (5 ca Chromium, đều chạy thật).

## 2026-11-09 — FA-S10: sửa dòng đường B trong bảng D8 (đêm 3, chỉ tài liệu)

- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §4: đường B ghi "huy chương theo thứ tự + câu vàng và câu đổi bạc/đồng (đủ 6 cách đặt)" thay cho "không đổi được". Không đổi mã.

## 2026-11-09 — FA-S11: ghép email với mã học sinh cho list KetQua (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`chuyen_fa_daa`): ghi thêm `EMAIL_MA_HS.csv` (Email, student_id; dữ liệu cá nhân, chỉ trên máy IT).
- `mau_forms_thi_clb/ghep_ket_qua_email.py` (mới): `ket_qua_ly_do.csv` + `EMAIL_MA_HS.csv` -> `KETQUA_NHAP_LIST.csv` với các cột list `KetQua`; em thiếu email: cảnh báo, dòng vẫn ghi, Email rỗng.
- `docs/he_sinh_thai/FA_SAU_XEP.md` §2: cách ghép mới, cột `Email` "Lấy từ". `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 217 tệp test.
- Test mới: `tests/test_fa_s11_ghep_email.py` (4 ca).

## 2026-11-09 — FA-S6: bộ sinh biểu mẫu đăng ký đọc Loại CLB từ Sổ nhập CLB (đêm 3, TH)

- `mau_forms_thi_clb/tao_mau_forms.py`: `--fa-daa --so-nhap-clb <Sổ nhập CLB của FA-M1>` đọc Loại bằng `chuyen_forms_sang_phan_mem.doc_clb_fa` (`de_theo_so_nhap_clb`); CLB Tự do không có trong câu vàng; hướng dẫn ghi Loại lấy từ sổ. `--so-nhap-clb` chỉ dùng cùng `--fa-daa`. Không có cờ: tệp sinh ra giống hệt từng byte (đã so `diff -r` trước/sau).
- Test mới (trong tệp cũ): `tests/test_fa_m2_forms_dang_ky.py` `test_fa_s6_so_nhap_clb_bo_clb_tu_do_khoi_cau_vang`, `test_fa_s6_so_nhap_clb_chi_dung_cung_fa_daa`.

## 2026-11-09 — FA-S4: báo khi không đọc được giờ làm bài (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`_thoi_gian_lam_bai`): nhận ô `datetime` và chữ ISO; trả thêm số phiếu không đọc được (không đoán thứ tự ngày/tháng). `chuyen_fa_daa` thêm MỘT cảnh báo mỗi tệp kèm số phiếu đó.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` `test_fa_s4_thoi_gian_iso_va_datetime_doc_duoc_dang_khac_dem_loi`, `test_fa_s4_mot_canh_bao_moi_tep_kem_so_phieu`.

## 2026-11-09 — FA-S2: bỏ câu theo từng đề (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `bo_cau` khoá `(CLB, đề, số câu)`; CLI `--bo-cau CLB-DE-SO` (ví dụ `C3-B-4`, hàm `_doc_bo_cau`); dạng cũ `CLB-SO` chỉ nhận khi CLB có một đề, nếu không là lỗi nêu các đề (`_chuan_bo_cau`). Bỏ câu 4 đề B không đổi điểm đề A.
- `mau_forms_thi_clb/tao_mau_forms.py`: dòng hướng dẫn `--bo-cau` trong `CAI_DAT_FORMS_BIEN_THE.md` (chỉ chế độ `--bien-the`).
- `tests/test_fa_m4_phan_tich.py`: 3 ca mới `test_fa_s2_*`; ca cũ `test_bo_cau_cham_lai_cho_moi_hoc_sinh` dùng dạng mới (CLB có hai đề).

## 2026-11-09 — FA-S5: cảnh báo khi em làm sai đề được giao (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (`chuyen_fa_daa`, khi có `--bien-the-tep`): bài làm đề khác đề giao (`chon_bien_the`, hoặc `chon_bien_the_thi_lai` với bài thi lại hợp lệ) -> một cảnh báo nêu email, CLB, đề đã làm và đề giao; vẫn giữ điểm.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` `test_fa_s5_lam_sai_de_duoc_giao_thi_canh_bao_giu_diem`; thêm một dòng kiểm vào ca thi lại FA-S1.

## 2026-11-09 — FA-S1: bài thi lại chỉ tính khi lần đầu bị gắn cờ và đúng đề thi lại (đêm 3, TH)

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `--fa-daa` giữ mọi bài của một CLB rồi `_tach_lan_dau` chọn "bài lần đầu" theo đề giao (`chon_bien_the`), không theo thứ tự tệp; trung vị D9 chỉ trên bài lần đầu; bài lần hai thay bài lần đầu CHỈ khi lần đầu bị cờ quá nhanh và bài lần hai là đề `chon_bien_the_thi_lai`; mọi bài lần hai khác: không tính + cảnh báo. Chế độ mặc định (không `--fa-daa`) giữ "giữ bài đầu", đường mã không đổi.
- Test mới (trong tệp cũ): `tests/test_fa_m4_phan_tich.py` 3 ca `test_fa_s1_*` (thi lại hợp lệ, lần hai không cờ bị bỏ, đảo thứ tự tệp cho cùng kết quả).

## 2026-11-09 — FA-S3: cân bằng đề không dịch điểm khi một phía có ít bài (đêm 3, TH)

- `mau_forms_thi_clb/phan_tich_cau_hoi.py` (`so_sanh_bien_the`): `N_NHO` (chỉ báo, không dịch) khi đề này HOẶC phần còn lại có ít hơn `N_TOI_THIEU` bài.
- `tests/test_fa_m4_phan_tich.py`: ca mới `test_fa_s3_mot_phia_nho_thi_khong_dich_ca_hai_de`; ca cũ `test_d11_de_it_hon_5_em_chi_bao_khong_bao_gio_chinh` đổi kỳ vọng của đề A sang `N_NHO` (đúng theo spec §6.2).

## 2026-11-09 — FA-S7, FA-S9: xuất lý do chỉ của lần chạy mới nhất; test rollback bảng FA (đêm 3)

- `api_xuat.py` (`_export_ly_do_da_khoa`): lấy lần chạy mới nhất trong `run_history`; lần đó không có lý do FA thì trả `fa_chua_co_ly_do` (không xuất lý do của lần FA cũ hơn).
- FA-S9 (chỉ test): lỗi ném sau lần ghi FA cuối -> `fa_nhom`, `fa_ly_do`, `match_results`, `run_history` giữ nguyên.
- Test mới (trong tệp cũ): `tests/test_fa_ly_do.py` `test_fa_s7_xuat_ly_do_chi_lay_lan_chay_moi_nhat`, `test_fa_s9_chay_hong_sau_khi_ghi_fa_rollback_ca_hai_bang`.

## 2026-11-09 — FA-S8: nhập CSV CLB khi FA tắt giữ nguyên dòng (đêm 3)

- `api_nhap.py` (`import_clubs_csv`): FA tắt thì không đọc cột FA nữa (ô loại sai không còn làm bỏ dòng); dòng vẫn được tạo, một cảnh báo `fa_cot_bo_qua`. FA bật: như cũ.
- Test mới (trong tệp cũ): `tests/test_fa_du_lieu.py` `test_fa_s8_csv_fa_tat_bo_cot_fa_giu_dong`, `test_fa_s8_csv_fa_bat_giu_hanh_vi_cu`.

## 2026-11-09 — FA-SOAT2: soát đêm 2 và mở đêm 3 (chỉ tài liệu, chưa sửa lỗi)

- `docs/phien/bao_cao_dem/2026-11-09_soat_dem2.md`: kết luận GO; danh sách sửa FA-S1..FA-S11 (6 lỗi mới của bộ chuyển đổi / bộ sinh, 4 phát hiện còn mở của soát đêm 1, 1 chỗ hở email ↔ mã học sinh). Theo yêu cầu của Truong: chưa sửa.
- `docs/ke_hoach/FA_DAA_KE_HOACH.md` §6: spec đêm 3 (sửa lỗi rồi FA-UI-1..5). `docs/phien/CHAY_DEM_FA_DAA.md`: giao thức đêm 3. `docs/phien/claude__keen-ride-72sa7t.md`: Plan đêm 3.

## 2026-11-09 — FA-M6: Tài liệu sau khi xếp (kết quả, phản hồi, khiếu nại, nhắc hạn, điểm danh) (đêm 2, TH = chưa thử trên Microsoft thật)

- `docs/he_sinh_thai/FA_SAU_XEP.md` (mới, chỉ tài liệu): `ket_qua_ly_do.csv` -> list `KetQua` (cách C; IT ghép email), màn kết quả và ba nút phản hồi -> list `PhanHoi`, Forms khiếu nại (3 ngày, chỉ lỗi dữ liệu, chạy lại cùng seed) và khảo sát tuần 3, flow nhắc (mở cổng, -2 ngày, -3 giờ, NOT_ATTEMPTED hai lần, dưới 50 % sau 3 ngày -> GVCN), phép tính hạn mức 6.000 (mỗi em một thư chạm hạn mức; gửi lô Bcc 50 người ≈ 225 yêu cầu), list `DiemDanh` với cột tính `GiaiPhong`, xuất danh sách chờ; bảng kiểm K1..K14 (TH). Không nói đường nào nên chọn (D8 mở).
- Test mới: `tests/test_fa_m6_tai_lieu.py` (6 ca: cột CSV khớp mã xuất `api_xuat.py`, đủ tên list/biểu mẫu/flow, phép tính, nhãn TH, không dữ liệu thật). Không đổi mã.

## 2026-11-09 — FA-M5: Đặc tả Power Apps v2 (đường A) và cột list FA-DAA (đêm 2, TH = chưa thử trên Microsoft thật)

- `T4M_DAC_TA_SUA_APP.md` §12 (mới): màn đăng ký v2 (xáo `Shuffle()`, ▲▼, tự lưu `Patch` DRAFT, tối thiểu 3, cảnh báo thiếu CLB Tự do, nhãn thẻ, Nộp SUBMITTED, ước tính số yêu cầu so với 6.000) và widget huy chương (mặc định theo thứ tự, tự cập nhật khi chưa chỉnh tay, hoán đổi, vàng vào Tuyển chọn có nhắc); yêu cầu R39 đến R54, tất cả TH; không nói đường nào nên chọn (D8 mở).
- `bo_dung_t4m`: `cot_lists.ECA_FA` / `TAT_CA_FA` (`WP1..WP7` = huy chương, `HC_TuChinh`, `TrangThai` DRAFT/SUBMITTED/Đã khóa, không `THIk`); `site_script`, `mau_csv`, `sinh_bk1`, `tao_bo_dung_t4m.py --fa-daa` (+ `00_FA_DAA_GHI_CHU.md`). Không cờ: bộ dựng cho ra đúng như trước (`diff -r` giống hệt).
- `tests/test_t4m_bo_dung_bk34.py`: test "nhắc mọi R1 đến R38" chỉ đếm R1..R38 (R39 trở đi thuộc bộ FA).
- Test mới: `tests/test_fa_m5_bo_dung.py` (10 ca). Công thức Power Fx `02_app/` chưa viết lại cho màn FA.

## 2026-11-09 — FA-M4: Đề biến thể, phân tích câu hỏi và cân bằng điểm giữa các đề (đêm 2, TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/phan_tich_cau_hoi.py`: `chon_bien_the` (crc32(email) % n), `kiem_bien_the`, `phan_tich_cau` (V§7.5: % đúng, độ phân biệt 1/3 trên - 1/3 dưới, cờ PHAN_BIET_AM / QUA_DE / QUA_KHO), `so_sanh_bien_the` (D11: ngưỡng z·√(s²/n+s²/n), z = 1,96 hoặc 2,39; n < 5 chỉ báo; vượt ngưỡng thì dịch về trung bình chung; làm tròn nửa lên, kẹp 0-10), lệnh `chia` (Email -> đề giao, đề thi lại).
- `tao_mau_forms.py --bien-the`: mỗi CLB có `de_thi_bien_the` (đề B, C trong de_thi.json) sinh một biểu mẫu cho từng đề + `CAI_DAT_FORMS_BIEN_THE.md` (time limit BẬT, xáo câu và lựa chọn BẬT). Lệch so với bảng việc: phần hướng dẫn nằm ở tệp riêng này, không chèn vào `CAI_DAT_FORMS_CHI_THI.md`, để chế độ `--chi-thi` vẫn giống hệt từng byte khi không có cờ.
- `chuyen_forms_sang_phan_mem.py --fa-daa`: `--bien-the-tep`, `--ap-dung-dieu-chinh`, `--giu-diem-goc`, `--bo-cau`; có chênh lệch ngoài ngưỡng thì ghi `DIEU_CHINH_BAN_DE.xlsx` rồi dừng (mã thoát 3) tới khi admin chọn một cờ; luôn ghi `PHAN_TICH_CAU_HOI.xlsx`.
- Không cờ: `--chi-thi`, `--moi-clb` (sinh tệp) và chế độ mặc định của bộ chuyển đổi cho ra đúng như trước (so bằng `diff -r` và so nội dung ô).
- Test mới: `tests/test_fa_m4_phan_tich.py` (24 ca).

## 2026-11-09 — FA-M3: Bộ chuyển đổi chế độ FA-DAA (đường A và đường B) (đêm 2, TH = chưa thử trên Microsoft thật)

- `chuyen_forms_sang_phan_mem.py --fa-daa --so-nhap-clb SO_NHAP_CLB.xlsx (--dang-ky FORMS... | --lists LIST.csv) [bài thi...]`: Loại CLB, chỉ tiêu, điểm sàn, giữ chỗ lấy từ Sổ nhập CLB của FA-M1; đường B đọc biểu mẫu FA-M2 và nối `dat_huy_chuong_duong_b` (không đổi hành vi, 19 test cũ xanh); đường A (`doc_lists(fa=True)`) bỏ dòng DRAFT (trừ `--nhan-ban-nhap`), lấy lần lưu cuối, điền huy chương mặc định khi ô trống và HC_TuChinh không đặt; bỏ nguyện vọng trùng và báo; điểm thi quy về nguyên 0-10 (D7, tính bằng phân số); em xếp CLB Tuyển chọn mà chưa thi -> cảnh báo NOT_ATTEMPTED; làm bài dưới 1/3 trung vị -> cờ (D9, chỉ báo); soát huy chương bằng `fa_daa.kiem_ho_so_huy_chuong`; không soát hai quỹ 100 điểm cũ.
- Không cờ: `doc_lists`, `phan_tich_chi_thi`, `ghi_tep_phan_mem` giữ hành vi cũ (nội dung ô SO_NHAP_CLB.xlsx và BANG_DIEM.xlsx của một lần chạy mặc định giống hệt trước thay đổi).
- Test mới: `tests/test_fa_m3_chuyen.py` (25 ca). Chưa thử trên Forms/Lists thật (TH).

## 2026-11-09 — FA-M2: Biểu mẫu đăng ký đường B (--fa-daa) (đêm 2, TH = chưa thử trên Microsoft thật)

- `bieu_mau.cac_phan_fa`, `tao_mau_forms.py --fa-daa`: mỗi ngày một biểu mẫu đăng ký (không câu Ranking; `[<buổi>-nv1..3]` bắt buộc, `[<buổi>-vang]` và `[<buổi>-doi]` tuỳ chọn, có đáp án \"giữ mặc định\" vì Forms không bỏ chọn được), `NHAP_FORMS_DANG_KY_<buổi>.docx` và `CAI_DAT_FORMS_DANG_KY.md` (một dòng mô tả V§5.1, cài đặt, giới hạn đường B). Không nói đường nào được khuyên dùng (D8 còn mở).
- Không cờ: `--chi-thi` và `--moi-clb` sinh ra tệp giống hệt từng byte so với trước thay đổi (so bằng `diff -r`). `ghi_docx_chi_thi` thêm hai tham số tuỳ chọn.
- Test mới: `tests/test_fa_m2_forms_dang_ky.py` (10 ca).

## 2026-11-09 — FA-M1: Phiếu thiết lập CLB trên Forms và bộ chuyển đổi (đêm 2, TH = chưa thử trên Microsoft thật)

- `mau_forms_thi_clb/chuyen_phieu_clb.py`: Excel xuất từ Phiếu thiết lập CLB -> `SO_NHAP_CLB.xlsx` (cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng, sheet Giữ chỗ) + `BAO_CAO_PHIEU_CLB.md`; phân loại V§4.1, nộp nhiều lần lấy phiếu cuối, CLB chưa nộp phiếu -> Giới hạn với chỉ tiêu kỳ trước (`--ky-truoc`), kiểm trước bằng `fa_daa.kiem_truoc_fa`.
- `PHIEU_THIET_LAP_CLB.md`: hướng dẫn dựng Forms bằng tay (Forms không có API tạo biểu mẫu).
- Test mới: `tests/test_fa_m1_phieu_clb.py` (17 ca). Không đổi mã kiosk, lược đồ hay CSV.

## 2026-11-09 — FA-SOAT: Opus soát đêm 1 (mục cha A13)

- `tests/test_van_phong_tu_nhien.py`: thêm `DAA` vào `VIET_TAT` (tên chế độ FA-DAA là chữ viết tắt, như `DA`, `RB`). Bốn thông báo lỗi mới của đêm 1 (`fa_cot_bo_qua`, `fa_giu_cho_bo_qua`, `fa_chua_bat`, `fa_chua_co_ly_do`) làm test này đỏ; đêm 1 không chạy lại nó sau khi thêm mã lỗi.
- Báo cáo soát: `docs/phien/bao_cao_dem/2026-11-09_soat_dem1.md`. Không có test mới.

## 2026-11-09 — FA-4 đến FA-8: chạy FA-DAA, đóng CLB thiếu người, lý do, bảng nhu cầu, tính chất V§13 (mục cha A13, A5, A6, C3, Z6)

(Bốn mục dùng chung `fa_daa.py`, `api.py`, `i18n_errors.py` nên đi cùng một commit.)

- **FA-4** `fa_daa.chay_fa_daa`: CLB Tự do không giới hạn trong bộ nhớ; lọc Tuyển chọn theo điểm sàn (`NOT_ATTEMPTED` / `BELOW_PASS`); bỏ điểm thi ở CLB Giới hạn; giữ chỗ bằng suất dự trữ mềm; phương án dự phòng (CLB Tự do ít người nhất, theo thứ tự STB của buổi); chia nhóm phòng (`fa_nhom`, chỉ thêm). Lõi `run_rbda_nhieu_buoi` không đổi; `api.py` gọi lớp bọc khi FA bật và chạy hai chốt (sanity, ổn định) trên đầu vào đã chuẩn bị, không ghi danh sách tăng cường vào `preferences`.
- **FA-5** đóng CLB thiếu người: mỗi vòng một CLB (thiếu nhiều nhất trước; hoà: ít người hơn, rồi mã), chạy lại cùng STB; `dong_cua`, `CLUB_CLOSED`, cảnh báo `fa_clb_dong_thieu_nguoi` (nói rõ là xấp xỉ).
- **FA-6** `ly_do_ket_qua` (RESERVED / SCORE / MEDAL / LOTTERY / BELOW_PASS / NOT_ATTEMPTED / CLUB_CLOSED, điểm chuẩn, danh sách chờ theo D4, lỗi ổn định thì ném ValueError); bảng `fa_ly_do` (chỉ thêm); `fa_ly_do.py` (mẫu câu V§9.1, không có mã học sinh khác, không hứa ưu tiên bù); `export_ly_do_csv` → `ket_qua_ly_do.csv`.
- **FA-7** `bang_nhu_cau`, `export_bang_nhu_cau` (không có mã hay tên học sinh), `kiem_chi_tang` và `mau_forms_thi_clb/so_sanh_suc_chua.py` (từ chối giảm chỉ tiêu và đổi loại).
- **FA-8** `tests/test_fa_tinh_chat.py`: 200 bộ nhỏ ngẫu nhiên cho V§13.1-13.9, 13.11 (13.12 bỏ qua có lý do: D1 hoãn).
- Tệp mới: `fa_ly_do.py`, `mau_forms_thi_clb/so_sanh_suc_chua.py`. Bảng mới `fa_nhom`, `fa_ly_do` (CREATE TABLE IF NOT EXISTS, không đổi bảng cũ). Test mới: `tests/test_fa_chay.py`, `test_fa_toi_thieu.py`, `test_fa_ly_do.py`, `test_fa_nhu_cau.py`, `test_fa_tinh_chat.py`. `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 210 tệp test, hàng mới cho `fa_daa.py` / `fa_ly_do.py`.

## 2026-11-09 — FA-3: huy chương một quỹ (mục cha A13)

- `fa_daa.py`: `kiem_ho_so_huy_chuong` (giá trị 60 / 30 / 10 đúng kiểu số nguyên, mỗi giá trị một lần mỗi buổi, mỗi CLB một huy chương, CLB trong nguyện vọng và không phải Tự do; ít hơn 3 huy chương hợp lệ), `diem_huy_chuong_hieu_luc` (một quỹ, bỏ qua `tier`, không đọc thứ hạng nguyện vọng).
- `api_quan_ly.py`: `submit_huy_chuong(student_id, huy_chuong)` (kiểm ở server, thay toàn bộ huy chương cũ của em, ghi `wharton_bids` + `wharton_nhat_ky`, tôn trọng khoá điểm). `api.py`: khi FA bật, hồ sơ huy chương được kiểm thay hồ sơ 100 điểm (chặn chạy, báo cáo sức khoẻ) và huy chương làm `diem_wharton` của lần chạy.
- `i18n_errors.py` (+ `i18n_loi.js`): 5 mã mới. `tests/test_fa_huy_chuong.py` (mới, 20 ca); `tests/test_ws_nhan.py`; `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 205 tệp test.

## 2026-11-09 — FA-2: kiểm trước khi chạy FA-DAA (mục cha A5)

- `fa_daa.py`: `kiem_truoc_fa` (mỗi buổi có CLB Tự do; mọi CLB có loại; Giới hạn / Tuyển chọn có chỉ tiêu; Tuyển chọn có điểm sàn; giữ chỗ không vượt chỉ tiêu; giữ chỗ cho học sinh lạ / em không xếp CLB đó chỉ là cảnh báo và không được tính), `giu_cho_hop_le`, `chi_loi_chan`, `doc_du_lieu_fa`, `kiem_fa_tu_csdl`.
- `api.py`: bước kiểm dữ liệu của `_run_pipeline_da_khoa` và `get_data_health_report` gọi kiểm FA khi `fa_daa` bật (lỗi chặn dừng trước khi bốc hay khoá số, không ghi gì); hồ sơ 100 điểm của Wharton không áp khi FA bật.
- `so_nhap.py`: kiểu CLB và `kiem_thuoc_tinh` chuyển vào đây (skill đóng gói của so_nhap chạy một mình); `fa_daa.py` nhập lại.
- `i18n_errors.py` (+ `i18n_loi.js`): 7 mã `fa_*` mới. `tests/test_fa_kiem_truoc.py` (mới, 15 ca); `tests/test_ws_nhan.py`: thêm mã vào danh sách mã mới; `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 204 tệp test.

## 2026-11-09 — FA-1: mô hình dữ liệu FA-DAA (mục cha A13)

- Luật `rules.fa_daa` (mặc định TẮT; bật cần `wharton`): `cau_hinh_ws.py`, `rbda_priority_pipeline.py` (`dung_fa_daa`, khoá bỏ khỏi `run_history.luat_xep` và dấu vân tay khi tắt; khi bật, dấu vân tay gồm kiểu CLB + giữ chỗ).
- `clubs` thêm bốn cột `loai`, `diem_san`, `so_toi_thieu`, `suc_chua_phong` (`di_tru_schema` idempotent, sao lưu trước); bảng mới `giu_cho(club_id, student_id)`; xoá CLB / học sinh / dữ liệu dọn cả `giu_cho`.
- Sổ nhập: cột CLB tuỳ chọn Loại / Điểm sàn / Tối thiểu / Sức chứa phòng và sheet tuỳ chọn "Giữ chỗ" (đọc, ghi, nạp); CSV CLB nhận bốn cột cùng tên khoá. Không có cột thì giống từng byte như cũ; FA tắt thì bỏ qua kèm cảnh báo `fa_cot_bo_qua` / `fa_giu_cho_bo_qua`. Mã lỗi mới trong `i18n_errors.py` (đã chạy `tao_i18n_js.py`).
- Module mới `fa_daa.py` (kiểu CLB, `kiem_thuoc_tinh`, ghi thuộc tính, `thay_giu_cho`).
- `tests/test_fa_du_lieu.py` (mới, viết trước); `tests/test_rang_buoc_csdl.py`: hàm trợ giúp `_ha_cap` chọn đúng cột của lược đồ cũ (bảng `clubs` nay có thêm cột). `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 203 tệp test.

## 2026-11-08 — FA-KH: báo cáo đêm tự đẩy lên GitHub

- `docs/phien/CHAY_DEM_FA_DAA.md` mục E: phiên chạy đêm ghi `docs/phien/bao_cao_dem/<ngày>.md` (tiếng Việt, dễ hiểu), commit, push, kiểm push đã tới GitHub, in link. Không đổi mã.

## 2026-11-08 — FA-M3 (một phần, Truong duyệt): đặt huy chương trên đường B, đủ 6 cách đặt

- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: hàm mới `dat_huy_chuong_duong_b` (mặc định theo thứ tự nguyện vọng, câu tuỳ chọn đặt vàng, câu tuỳ chọn đổi bạc/đồng; giá trị không dùng được thì giữ mặc định và báo). Chưa nối vào luồng chuyển (việc của FA-M3, đêm 2); đầu ra hiện có không đổi.
- `tests/test_fa_m3_huy_chuong_b.py` (19 ca, viết trước, đỏ rồi xanh; đột biến tắt bước đổi bạc/đồng làm 8 ca đỏ).
- `CLAUDE.md`: ghi chú ngoại lệ bất biến 2 nay đạt trọn điều kiện "mọi học sinh đổi được". `docs/ke_hoach/FA_DAA_KE_HOACH.md` D12, FA-M2, FA-M3; `docs/ke_hoach/CLAUDE_CHI_TIET.md` 202 tệp test.

## 2026-11-08 — FA-KH (quyết định của Truong): ngoại lệ bất biến 2 cho huy chương mặc định, D11 không chặn

- `CLAUDE.md`: ghi ngoại lệ bất biến 2 (huy chương mặc định theo thứ tự nguyện vọng, chỉ ở tầng đăng ký và chỉ khi học sinh đổi được; lý do: tín hiệu riêng kiểu CADA giữ khai thật thứ tự).
- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: D2 (ngoại lệ), D11 (ngưỡng theo cỡ mẫu, tự điều chỉnh theo chênh lệch trung bình, admin xác nhận, không chặn), D12 (đường B thêm câu tuỳ chọn đặt huy chương vàng), FA-UI, FA-M2, FA-M3, FA-M4.
- `docs/phien/claude__keen-ride-72sa7t.md`: quyết định mới. Không đổi mã; D1 vẫn hoãn.

## 2026-11-08 — FA-KH (sửa sau soát hội đồng): D1, D3, D4, D5, D9, D11, D12, FA-9

- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: D1 sửa lý do (không phá ổn định; vấn đề là động cơ giữa các kỳ, cần mô phỏng trước kỳ 2); D3 đóng CLB thiếu nhiều nhất trước; D4 danh sách chờ Tuyển chọn điểm → huy chương → bốc thăm, Giới hạn huy chương → bốc thăm, chỉ em xếp CLB đó cao hơn; D5 không làm hạt giống công khai, FA-9 thành biên bản bốc thăm có giáo viên chứng kiến; D9 bật giới hạn thời gian Forms, cờ < 1/3 trung vị; D11 so điểm trung bình giữa các bản đề; D12 đường B không dùng câu Ranking, 3 câu chọn NV1–3, huy chương gán theo thứ tự.
- `docs/phien/claude__keen-ride-72sa7t.md`, `docs/phien/CHAY_DEM_FA_DAA.md`: cập nhật theo các quyết định trên. Không đổi mã.

## 2026-11-08 — FA-KH: kế hoạch triển khai FA-DAA và tệp chạy đêm (chỉ tài liệu)

- `docs/ke_hoach/FA_DAA_VISION.md`: vision của Truong (chép nguyên văn).
- `docs/ke_hoach/FA_DAA_KE_HOACH.md`: kế hoạch theo mục FA-0..FA-10, FA-UI, FA-M1..M6; mục cha A13, A5, A6, C3, Z6, A2, T4M-NC; quyết định D1..D10 (D1 ưu tiên bù CHẶN vì bất biến 2).
- `docs/phien/CHAY_DEM_FA_DAA.md`: tệp duy nhất cho phiên chạy đêm; `docs/phien/claude__keen-ride-72sa7t.md`: bàn giao nhánh.
- Không đổi mã, schema, hợp đồng CSV; không test mới.

## 2026-11-06 — T4M-NC: sửa CI đỏ của PR #13 (3 nguyên nhân do nhánh)

- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that`: `docs/ke_hoach/CLAUDE_CHI_TIET.md` bản đồ mã ghi 194 tệp test, thực tế 201; cập nhật 201 tệp, 3.645 ca.
- `tests/test_a13_13_kiem_nhan.py::test_F1_script_do_tat_wharton_ro_rang`: `du_lieu_test/demo_t4m.py` (từ T4M-Q5c) ghi `{"wharton": bool(day_du)}`; nay ghi tường minh `{"wharton": False}` / `{"wharton": True}`. Hành vi không đổi.
- `tests/test_t4m_bo_dung_bk34.py` (Windows CI không cài `python-docx`): `pytest.importorskip("docx")` như các test Forms khác; tái hiện bằng cách giả lập thiếu `docx` (25 đỏ/lỗi trước, bỏ qua sau).
- Không sửa: `tests/test_giao_dien_t3_l3.py::test_tai_bang_theo_clb_va_theo_ma_co_tim` đỏ một lần trên Linux CI (màn 2 dòng, tệp 3 dòng), xanh ở lần chạy CI kia và 6/6 lần ở máy: chập chờn, test của `main` (T3-L4), tách thành việc riêng.

## 2026-11-06 — T4M-BK3, BK4 (vòng 5, bước K2): bảng flow `DaLam_<ClubId>` và lệnh gộp `tao_bo_dung_t4m.py`

Không đổi lõi, schema, hợp đồng CSV, không thư viện mới (chỉ thư viện chuẩn); không sửa bộ sinh hay đặc tả cũ. Mọi đầu ra nhãn TH (chưa chạy trên Power Apps / SharePoint / Power Automate).
- Mới `mau_forms_thi_clb/bo_dung_t4m/bang_flow.py` (BK3): một hàng mỗi CLB CÓ đề (`bieu_mau.clb_co_thi`): `Flow` = `DaLam_<ClubId>`, `ClubId`, ô trống cho IT (`FormId`, `ChuBieuMau`, `DaThuNgay`), tệp Quick Import; `BANG_FLOW.md` (bảng + biểu thức dán `toLower(responder)`, hằng `ClubId`, OData `ResponseId eq '…'`, nhãn GĐ) và `BANG_FLOW.csv`. Không gói flow `.zip` (quyết định 3).
- Mới `mau_forms_thi_clb/bo_dung_t4m/huong_dan_it.py` (BK4): sinh `HUONG_DAN_IT.md`: bước 0 (HỎI-IT) đến bước 6 (vòng thử), mỗi bước có dòng `☐ Pass ☐ Fail` trỏ về R1..R38 và HDT §9; ba cách A/B/C với quyền và nhãn ĐXM/TT-CXM từ KQ §8.1; site script 46 hành động nên chỉ áp không đồng bộ (Settings > Apply a site template, hoặc `Add-SPOSiteDesignTask`), cấm `Invoke-SPOSiteDesign`; phụ lục R1..R38.
- Mới `mau_forms_thi_clb/tao_bo_dung_t4m.py` (BK4): `--de-thi`, `--ra`, `--zip`; ra `01_lists/` và `02_app/` (gọi `sinh_bk1.ghi_tat_ca` của K1), `03_flow/`, `04_forms/` (gọi `tao_mau_forms.sinh_moi_clb` như hàm), `HUONG_DAN_IT.md`; `<ra>.zip` nằm ngoài thư mục, tên sắp xếp, giờ cố định, sinh lại cho cùng từng byte. Kiểm đề trước khi ghi.
- Test mới `tests/test_t4m_bo_dung_bk34.py` (+25): số flow = số CLB có đề, mọi `ClubId` có trong `CLB.csv`, đủ R1..R38 (đọc từ đặc tả), dòng HDT có thật, `Invoke-SPOSiteDesign` chỉ để cấm, sinh lại giống từng byte kể cả zip (và sinh đè lên thư mục cũ), `04_forms` trùng khít đầu ra của `sinh_moi_clb`, không tên thật/tenantId/URL. Mutation check bắt 3 đột biến (flow cho mọi CLB, bỏ chữ cấm Invoke-SPOSiteDesign, đảo thứ tự zip); một đột biến sống sót lần đầu (kiểm "không" cùng dòng quá lỏng) nên đã siết test.
- `demo_t4m.py` mặc định, `--moi-clb`, `--day-du`: đầu ra trùng khít trước/sau (42, 52, 42 tệp; docx/xlsx so bỏ core.xml). README (mục 0c) và `T4M_VAN_HANH_MOT_DOT.md` (phụ lục) mỗi nơi một đoạn ngắn.

## 2026-11-06 — T4M-BK1, BK2 (vòng 5, bước K1): bộ dựng list và công thức Power Fx cho IT

Không đổi lõi, schema, hợp đồng CSV, không thư viện mới (chỉ `json`, `csv`, `uuid`, `re`); không sửa bộ sinh hay đặc tả cũ. Mọi đầu ra nhãn TH (chưa chạy trên SharePoint / Power Apps).
- Mới `mau_forms_thi_clb/bo_dung_t4m/`: `cot_lists.py` (MỘT định nghĩa cột cho ECA 30 cột, CLB 4, BaiThi 4, NHAT_KY_DA_LAM 4; GUID cố định uuid5), `site_script.py` (createSPList + addSPField / addSPFieldXml cho Choice; in số hành động, cảnh báo > 30, lỗi > 300; hiện 46), `mau_csv.py` (CSV mẫu một dòng ví dụ giả + `KIEM_COT_ECA.md`), `cong_thuc.py` (bốn tệp Power Fx khai triển k = 1..7 và bộ soát `soat_loc_uy_quyen`), `sinh_bk1.py` (một lệnh: `python -m bo_dung_t4m.sinh_bk1 --ra <thư mục>`; ra `01_lists/`, `02_app/`, `README_BK1.md`).
- Test mới (viết trước, đỏ khi thiếu mô-đun; sau đó sửa 3 lỗi sinh do test cú pháp tĩnh bắt: thiếu `;` trong `OnVisible`, `If` lệch dòng, `OnChange` k=7 thừa `;`): `tests/test_t4m_bo_dung_bk1.py` (37 ca). Gây hỏng tạm 3 chỗ (bỏ `WP7` khỏi ECA; khai triển chỉ tới k=6; `Email <>` trong `Filter(ECA…)`): test đỏ cả 3 (3, 3, 1 ca), khôi phục thì xanh.
- PHÁT HIỆN (không sửa, theo luật): `tao_mau_forms.ghi_clb_csv` ghi `Buoi` là "Thứ Hai" còn cột `Thu` của ECA là "Thứ 2"; quyết định 1 của §9 nói "cùng chữ". Bộ dựng dùng ánh xạ `buoi_theo_thu(de)` nên công thức lọc `Filter(CLB, Buoi = "Thứ Hai")` đúng; xfail ghi lại lệch.
- Sửa sau soát Opus (cùng bước K1): `addSPField`/`addSPFieldXml` nay là hành động CON (`subactions`) của `createSPList` (mức trên cùng chỉ có `createSPList`), thêm `$schema`; số hành động đếm cả hành động con (vẫn 46; cảnh báo > 30, lỗi > 300); mọi `addSPField` có `id` = GUID cố định (chạy lại không thêm cột hai lần). Test site script viết lại để ĐỎ trên đầu ra phẳng cũ (4 ca đỏ), đột biến 'làm phẳng' và 'bỏ id' đều bị bắt. Xfail Buoi/Thu đổi thành test thường (ánh xạ: khoá = 5 lựa chọn Thu, giá trị = Buoi của CLB.csv). Nhãn: công thức tên `Nhan` trong App.Formulas thay cho `ClearCollect(colNhan…)` ở App.OnStart (GĐ cú pháp).

## 2026-11-06 — T4M-Q5a/b/c (vòng 4, bước D1): bộ chuyển đổi đọc THIk/WPk, dữ liệu giả, `demo_t4m.py --day-du`

Không đổi lõi (`run_rbda`, `compute_club_priority`, `club_choice_function`), schema hay hợp đồng CSV của kiosk. Cột List cố định theo `T4M_KE_HOACH_TU_DONG.md` §8: `NV1..NV7`, `THI1..THI7`, `WP1..WP7`. List KHÔNG có `THIk`/`WPk` thì `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx` và tệp Lists giả giống hệt từng byte so với trước (băm toàn bộ khối zip trừ `docProps/core.xml`; 3 seed × {một biểu mẫu, `--moi-clb`} + tệp Lists giả mặc định; chạy tay trước và sau khi sửa).
- `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `doc_lists` nhận `THIk`/`WPk` (khoá "tick", "wp", "dong_buoi" chỉ khi có cột); Q5a: "thi" đi theo tick (tick + bài -> điểm; tick + vắng -> ô `thi`; bài không tick -> bỏ điểm, báo, BANG_DIEM ghi "chưa tick thi"; tick CLB không đề -> bỏ tick, báo; quá 5 tick/ngày -> giữ 5 đầu theo thứ tự NV, báo); Q5b: `diem_w` vào Sổ nhập (`luon_co_cot_w=True`), `_soat_hai_quy` chỉ BÁO quỹ không cộng đúng 100 (quỹ 1 = CLB đã tick, quỹ 2 = còn lại; quỹ một CLB để trống không báo), ô không phải số nguyên >= 0 -> báo, để trống; ghi chú cuối lệnh nói "giữ BẬT" khi có điểm quyết tâm. Hàm mới: `tap_thi`, `_doc_tick`, `_doc_diem_quyet_tam`.
- `du_lieu_test/sinh_xuat_lists_gia.py`: `sinh`/`ghi_csv` thêm `so_nv`, `co_tick`, `co_wp`, `clb_co_de` (bộ ngẫu nhiên riêng cho tick/điểm, nên NV không đổi); `cot_csv`, `ghi_dong`, `gai_quy_khong_du`; cờ `--so-nv --tick --wp`.
- `mau_forms_thi_clb/tao_mau_forms.py`: `ghi_mau_xuat_chi_thi` khi List có tick thì chỉ nộp bài cho CLB đã tick và gài thêm `tick_vang`, `nop_khong_tick`.
- `du_lieu_test/demo_t4m.py`: `--day-du` (kết hợp `--moi-clb`): bật `rules.wharton` trong CSDL tạm, gài một quỹ thiếu 100 -> kiosk CHẶN lần chạy đầu -> demo sửa bằng `admin_save_wharton` rồi chạy lại; tóm tắt LUÔN in "Điểm quyết tâm: BẬT/TẮT"; khoá `diem_quyet_tam`, `bi_chan_lan_dau`, `so_nv`.
- Test mới (viết trước; chạy lần đầu 29 ca đỏ, nay đủ 34 xanh): `tests/test_t4m_day_du.py` (34 ca). Gây hỏng tạm 5 chỗ (`!=100` -> `>100`, bỏ việc bỏ điểm khi không tick, bỏ trần 5, bỏ miễn trừ quỹ một CLB, bỏ ô `thi` theo tick): cả 5 bị bắt.
- Tài liệu: `mau_forms_thi_clb/README.md` (mục 0 và 0b), `T4M_VAN_HANH_MOT_DOT.md` (bước 2, 4, 5, phụ lục; bỏ "Top 3", `NV1..NV3`).

## 2026-11-06 — T4M-M6 (vòng 4, bước D2): app Top 7, tick chọn thi, điểm quyết tâm; chỉ tài liệu

Không có mã, test, schema hay hợp đồng CSV; không đụng lõi. Cột List cố định theo `T4M_KE_HOACH_TU_DONG.md` §8: `NV1..NV7`, `THI1..THI7`, `WP1..WP7`.
- `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md`: tối đa 7 nguyện vọng mỗi ngày (số ô = min(7, số CLB ngày)), tick "Thi" chỉ ở CLB có đề (tối đa 5 mỗi ngày), bước điểm quyết tâm (hai khung 100, bộ đếm "Đã dùng X / 100", chặn Gửi khi khung không rỗng khác 100), một `Patch` ghi 21 cột; R2 đến R6 sửa; R15 sửa (thẻ Thi tuyển = CLB đã tick); mục 11 thêm R25 đến R38 (pass/fail, trỏ HDT §9 dòng 14.x).
- `T4M_HUONG_DAN_THU.md`: bảng cột §1, §2 (mô hình dài tới 52.500 dòng, vượt trần 30.000), §5 (7 ô), §10, §12; §9 thêm dòng 14.1 đến 14.5; mục 14 mới. Bộ sinh giả mặc định vẫn NV1..NV3 (ghi rõ; tuỳ chọn tới NV7 chờ T4M-Q5c).
- `T4M_CONG_THI.md` §1, §2, §4.5; `T4M_MICROSOFT.md` (tóm tắt, sơ đồ, ma trận, bảng cột kho, P3, §8 thêm hàng T4M-M6); `T4M_PHIEU_PHONG_VAN.md`: ECA-6 (tối đa 7, số CLB mỗi buổi), ECA-9 (tick tối đa 5), ECA-12 mới (điểm quyết tâm, màn điện thoại), IT-19 mới.
- Không còn chữ "Top 3" lỗi thời trong năm tệp được giao (kiểm bằng grep). Mọi thứ nhãn TH, không có số đo.

## 2026-11-06 — T4M-DEMO-B: `demo_t4m.py --moi-clb` (cách B) và câu hỏi cổng thi cho GĐ2

Không đổi lõi, schema, hợp đồng CSV, bộ chuyển đổi hay bộ sinh mẫu; chế độ mặc định của demo không đổi (test cũ không sửa).
- `du_lieu_test/demo_t4m.py`: `--moi-clb` / `chay_demo(moi_clb=True)`; `tach_moi_clb` tách tệp Forms giả chung thành một tệp xuất mỗi CLB có đề (không câu cổng, cột Points là số); `ghi_bai_thi_gia` sinh `BaiThi.csv` giả, cố ý thiếu một bài của em chỉ nộp một lần; bộ chuyển đổi chạy với `--bai-thi`; tóm tắt in mục đối chiếu.
- Test mới (viết trước, 4 đỏ -> xanh): 5 ca trong `tests/test_demo_t4m.py` (nay 16): kết quả xếp trùng với bản một biểu mẫu chung cùng seed, đúng một tệp mỗi CLB không câu cổng, đối chiếu bắt đúng chỗ gài, mặc định không có tệp mới, lệnh in đối chiếu. Gây hỏng tạm 2 chỗ: cả hai bị bắt.
- `docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md`: sửa ECA-9 theo cách B; thêm mục B3 với IT-15 (sửa app hay trang SharePoint dự phòng), IT-16 (chủ biểu mẫu, trần 400), IT-17 (tài khoản dịch vụ, hạn mức flow, số ngày mở), IT-18 (quyền chỉ đọc `BaiThi`, DLP).
- README mục 0b, `T4M_VAN_HANH_MOT_DOT.md` phụ lục: lệnh `--moi-clb`.

## 2026-11-06 — T4M-NC vòng 3: soát C1 (T4M-Q4a/b/c) và C2 (T4M-M5)

Soát theo plan §7 "Nhận khi": 134 test liên quan đạt, ruff sạch, `kiem_nhanh` 7/7 (15 ca trùng khít với main); đầu ra mặc định và `--chi-thi` của `tao_mau_forms.py` trùng khít trước/sau C1 (bỏ qua `docProps/core.xml`). Không đổi mã sản phẩm.
- Gây hỏng tạm 4 chỗ trong `chuyen_forms_sang_phan_mem.py`: 3 bị bắt; `_da_thi` `any` -> `all` sống sót. Thêm `test_q4b_phieu_bo_trong_vai_cau_van_tinh_la_da_thi` (`tests/test_t4m_cong_thi.py`, nay 25): phiếu làm dở vẫn có điểm.
- M5: số dòng HDT §9 đề xuất "7.x" trùng với dòng 7.1/7.2 (flow xuất CSV) đã có. Thêm mục 13 vào `T4M_HUONG_DAN_THU.md` và dòng 13.1 đến 13.4 ở §9; cột "HDT §9" của R15 đến R24 trong `T4M_DAC_TA_SUA_APP.md` và hai chỗ trong `T4M_FLOW_DA_LAM.md` trỏ về 13.x.

## 2026-11-06 — T4M-M5 (vòng 3, bước C2): màn "Thi tuyển" và flow "Đã làm", chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` thêm mục 10 "Màn Thi tuyển" (CLB có thi mà em đã chọn, `Launch(FormUrl)` chỉ khi chưa có dòng `BaiThi` và còn hạn, "Đã làm"/"Chưa làm", nút Làm mới, lọc `=` uỷ quyền được, không hiện điểm: mức 5a) và bảng yêu cầu R15 đến R24 mỗi dòng một kiểm pass/fail. `docs/he_sinh_thai/T4M_FLOW_DA_LAM.md` (mới, 85 dòng): flow mẫu mỗi biểu mẫu một flow (When a new response is submitted → Get response details → [kiểm trùng] → Create item `BaiThi`), chủ là tài khoản dịch vụ IT, cách nhân flow và Form Id biểu mẫu nhóm, ước tính 9.000 đến 12.000 hành động so với 6.000 mỗi ngày (nhãn ƯL), xử lý lỗi, đường thủ công với `--bai-thi`. Chỉ connector chuẩn; mọi bước TH/GĐ. Không đụng `T4M_VAN_HANH_MOT_DOT.md` và `mau_forms_thi_clb/README.md` (C1 sửa). Không test mới.

## 2026-11-06 — T4M-Q4a, Q4b, Q4c: cổng thi, mỗi CLB một biểu mẫu (vòng 3, bước C1)

Không đổi lõi, schema, hợp đồng CSV. Mặc định và `--chi-thi` giữ nguyên (bất biến 1): test cũ không sửa.
- **Q4a** `bieu_mau.cac_phan_moi_clb`; `tao_mau_forms.py --moi-clb [--ra]`: `sinh_moi_clb`, `ghi_docx_moi_clb`, `ghi_clb_csv`, `ghi_cai_dat_moi_clb`. Mỗi CLB có đề một `NHAP_FORMS_MOI_CLB_<club_id>.docx` (không câu cổng, thẻ `[clb_x-k]` giữ nguyên), `CLB.csv` (ClubId, Ten, Buoi, FormUrl trống; mọi CLB), `CAI_DAT_FORMS_MOI_CLB.md`. Sinh lại giống hệt từng byte; kiểm đề trước khi ghi; tệp cũ của CLB hết đề bị xoá; không chung chế độ với `--chi-thi`.
- **Q4b** `chuyen_forms_sang_phan_mem._cot_chi_thi/_cot_mot_clb/_da_thi`: tệp xuất không câu cổng phải chứa đủ câu của đúng MỘT CLB; trộn CLB, thẻ lạ, thiếu câu thì dừng không ghi gì; phiếu có ít nhất một câu trả lời = đã thi. Tệp có câu cổng chạy như cũ. N tệp một-CLB cho cùng `SO_NHAP_CLB.xlsx` như một biểu mẫu chung.
- **Q4c** `--bai-thi BaiThi.csv` (`doc_bai_thi`, `bai_trong_tep_xuat`, `doi_chieu_bai_thi`): báo bài lệch hai phía, sheet *Đối chiếu BaiThi* chỉ khi có cờ; không đổi điểm; không cờ thì `BANG_DIEM.xlsx` như cũ.
- Test mới (viết trước): `tests/test_t4m_cong_thi.py` (24). Liên quan: test_t4m_chi_thi, test_demo_t4m, test_mau_forms_thi_clb, test_doi_chieu_lists, test_do_t4m_thi: 126 pass; ruff sạch.
- Tài liệu: `mau_forms_thi_clb/README.md` mục 0a; `T4M_VAN_HANH_MOT_DOT.md` bước 1, 4, 5. `demo_t4m.py --moi-clb` chưa làm (không rẻ: demo dựng một tệp chung).

## 2026-11-06 — T4M-NC: thiết kế cổng thi (chọn CLB → mở bài thi → trạng thái → điểm)

Chỉ tài liệu. `docs/he_sinh_thai/T4M_CONG_THI.md` (mới): app Power Apps ECA làm cổng, mỗi CLB có thi một biểu mẫu Forms Quiz, list `CLB` (FormUrl) và `BaiThi` (trạng thái), mỗi biểu mẫu một flow "Đã làm" (connector chuẩn); connector Forms không trả điểm (TT-CXM) nên điểm chính thức vẫn do bộ chuyển đổi chấm lại; ba mức trả điểm 5a/5b/5c; mã đề xuất Q4a–c, M5; phương án lui trang SharePoint.

## 2026-11-06 — T4M-M4 (bước R3): hướng dẫn flow gửi Excel theo lớp cho GVCN, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_FLOW_GUI_GVCN.md` (mới, 77 dòng): flow Power Automate tuỳ chọn, chỉ connector chuẩn (SharePoint, Outlook/Teams), chủ là tài khoản dịch vụ IT; lấy tệp `export_theo_lop` từ thư viện SharePoint, ghép với tệp ánh xạ lớp → email GVCN (nguồn HỎI-IT, NC-08; khoá ghép theo tên tệp đã làm sạch), gửi từng GVCN. Bảng giới hạn ĐXM của NC-12, NC-13, đoạn DLP (NC-14), xử lý lỗi và đường thủ công; không ghi ngược về list (NC-13). Bước chưa thử nhãn TH, công thức/hành động nhãn GĐ. Không đổi hợp đồng CSV, schema, bất biến hay mã sản phẩm; không test mới.

## 2026-11-06 — T4M-M1 (vòng 2, R1): đặc tả sửa app ECA sang Top 3 mỗi ngày, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` (mới, ~113 dòng) cho người sửa app (IT): cột dữ liệu mô hình rộng (`NV1..NV3`, `TrangThai`), hành vi màn hình (không trùng, không ô trống chen giữa, ngày trống hợp lệ, nhãn hai ngôn ngữ, điện thoại), `Patch` + `IfError` kèm báo đúng ngày lỗi, khoá theo `TrangThai`, chỉ dùng phép lọc uỷ quyền được (NC-04), sao lưu / khôi phục phiên bản (NC-21), bảng 14 yêu cầu R1..R14 mỗi yêu cầu một dòng kiểm pass/fail ánh xạ HDT §9, mục gói chỉ giữ chỗ "chờ A8-GOI". Mọi công thức gắn nhãn GĐ. Không đụng app thật, không đổi mã, schema, hợp đồng CSV.
## 2026-11-06 — T4M-M3 (vòng 2, bước R2): đối chiếu hai lần xuất List

Thêm công cụ dòng lệnh, chỉ đọc; không đụng kiosk, lõi, schema hay hợp đồng CSV.
- `mau_forms_thi_clb/doi_chieu_lists.py` (mới): `OLD.csv NEW.csv [--co-so CS1] [--ra bao_cao.xlsx] [--de de_thi.json]`. Dùng lại `doc_lists` của bộ chuyển đổi (không viết lại cách đọc). Liệt kê em mới, em rút, dòng đổi nguyện vọng (theo email chữ thường + Thu, kể cả đổi thứ tự), đổi Lớp, đổi CoSo. Hai tệp giống nhau => báo cáo rỗng; hoa/thường của email và thứ tự dòng không phải thay đổi. Lỗi thiếu cột => mã thoát 1, không ghi tệp.
- `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` bước 8: thêm đoạn dùng công cụ trước khi chạy lại.
- Sửa sau soát của điều phối: bản đầu so sánh qua `doc_lists` nên ô có mã CLB không có trong `de_thi.json` bị bỏ trước khi so (báo "không thay đổi" sai). Nay so giá trị THÔ NV1..NVn (bỏ khoảng trắng, phân biệt hoa/thường); ô mã lạ chỉ được đếm (`n_clb_la`) và dòng đầu in `CẢNH BÁO: N ô ...`, không bao giờ in "Không có thay đổi" phía trên cảnh báo chưa đọc.
- Test mới (viết trước, 17 ca + 7 ca sau soát = 24): `tests/test_doi_chieu_lists.py` (kiem_nhan ở T4M_MICROSOFT.md §8: rỗng / đúng một mục mỗi loại / email hoa-thường / lọc cơ sở / kiosk không bị nạp).

## 2026-11-06 — T4M-NC: Truong duyệt vòng 2

Chỉ tài liệu. Quyết định của Truong: duyệt nguyên tắc D1–D5 của thiết kế gói (mã A8-GOI chờ giáo viên ECA trả lời Q1–Q3); duyệt T4M-M1, M3, M4 (M2 chờ tệp xuất mẫu thật); T4-K2 giữ tạm dừng (K2-b). `T4M_KE_HOACH_TU_DONG.md` §6: vòng 2 R1–R3 kèm prompt.

## 2026-11-06 — T4M-GD4-V0 (bước S3): nháp v0 kiến trúc Microsoft, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_MICROSOFT.md` (mới), ghi rõ "Bản nháp v0 — chưa có kết quả phỏng vấn (GĐ2)", chạy prompt P2 theo dự phòng A: đủ 9 mục (tóm tắt; kiến trúc ô A–H; ma trận §7 điền đủ; mô hình kho rộng + ánh xạ Sổ nhập + điểm kiểm khi `student_id` là email; pha gói tóm tắt và dẫn `T4M_GOI_THIET_KE.md`, D1–D5 ghi là CHỜ DUYỆT; luồng muộn/đổi/rút; rủi ro + lộ trình (ước lượng); mã mục đề xuất T4M-Q1b, T4M-M1..M4, A8-GOI-1..3 kèm `kiem_nhan`; phương án T4-K2 để Truong quyết) và §10 danh sách soát lại sau GĐ2. Điểm phụ thuộc trường mang nhãn HỎI-IT; chỗ đổi thiết kế có hai nhánh (SharePoint List / Dataverse). Dẫn `T4M_VAN_HANH_MOT_DOT.md` (S1) và các bảng của `T4M_DO_MO_PHONG.md` (S4), cả hai có sau `git pull --rebase`; không diễn giải số đo. Không đổi hợp đồng CSV, schema hay bất biến nào; không test mới.

## 2026-11-06 — T4M-DO (bước S4): đo mô phỏng có / không bài thi tuyển, chỉ bảng số

Thêm công cụ đo; không đụng mã sản phẩm, schema hay hợp đồng CSV. Mọi số liệu là MÔ PHỎNG; không có nhận xét.
- `du_lieu_test/do_t4m_thi.py` (mới): 3 bộ giả (120 / 500 / 1.500 học sinh, hạt giống sinh cố định) x 20 hạt giống STB x 2 điều kiện (A không điểm thi, danh sách dự tuyển giữ nguyên; B có điểm thi như `de_thi.json`). Dữ liệu dựng bằng đúng chuỗi T4M (Lists giả → Forms giả → `--chi-thi` → `import_so_nhap`), đọc MỘT lần; mỗi lần chạy gọi `generate_stb_lottery`, `run_rbda_nhieu_buoi` (tham số như `api.run_pipeline`) và `verify_stability_tuan`. Chỉ số: tỉ lệ nguyện vọng 1 / top-3, số em chưa có CLB (tổng và theo buổi), tỉ lệ suất Tầng 1 về nhóm điểm cao nhất, số cặp phá vỡ, thời gian. `--nhanh` (lưới nhỏ cho test; bắt buộc kèm `--ra`, `--tai-lieu`). Cả lưới đủ chạy ~30 giây.
- `docs/he_sinh_thai/T4M_DO_MO_PHONG.md` (sinh ra): phương pháp, tham số, bảng trung bình / nhỏ nhất / lớn nhất, nhãn MÔ PHỎNG ở mọi tiêu đề bảng, lệnh tái lập. `du_lieu_test/ket_qua_t4m/`: CSV từng lần chạy và theo buổi.
- Sửa sau soát: bảng 2 ghi 15 CLB có đề thi, đúng là 10 (chỉ sai số đếm; điều kiện B vốn đã Tầng 1 đúng 10 CLB có `de_thi`); bảng 3 trở đi không đổi trừ số giây. Thêm test canh điều này (10 ca).
- Test mới (viết trước): `tests/test_do_t4m_thi.py` (8 ca): điều kiện A và B trùng khít từng byte với `PipelineAPI.run_pipeline`; tất định; không cặp phá vỡ; nhãn MÔ PHỎNG và không có mục nhận xét. Thử gây hỏng: bỏ danh sách dự tuyển ở điều kiện A làm kết quả không còn phụ thuộc hạt giống — đã bị bắt.

## 2026-11-06 — T4M-Q1b-b (bổ sung của điều phối vào T4M-Q1b): `--co-so` cho `--chi-thi`

`chuyen_forms_sang_phan_mem.py`: tham số tuỳ chọn `co_so` (CLI `--co-so CS1`) ở `doc_lists`, `phan_tich_chi_thi`, `chuyen_chi_thi`: chỉ giữ dòng List có `CoSo` bằng giá trị (bỏ khoảng trắng, không phân biệt hoa thường); phiếu thi của em ngoài danh sách đã lọc báo "ở cơ sở khác hoặc không có trong danh sách"; thiếu cột `CoSo` hoặc không em nào khớp thì lỗi, không ghi tệp. Không truyền `--co-so`: kết quả và cảnh báo y như cũ. `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` bước 4-5 dùng `--co-so` thay cho tách tay. Test mới: `test_q1bb_*` (4) trong `tests/test_t4m_chi_thi.py`. Không đổi hợp đồng CSV, schema, lõi.

## 2026-11-06 — T4M-Q1b (trong T4M-Q1 đã duyệt): `--chi-thi` chép Lớp từ Lists vào Sổ nhập

`chuyen_forms_sang_phan_mem.py`: `doc_lists` đọc cột `Lop` (hoặc `Lớp`) của tệp xuất Lists, giữ ô không trống đầu tiên của mỗi em; `phan_tich_chi_thi` mang `lop` theo; `ghi_tep_phan_mem` truyền `class_id` và `co_lop=True` CHỈ khi có ít nhất một em có lớp (Lists không có cột Lop hoặc mọi ô trống thì Sổ nhập y như cũ, không cột Lớp). Chế độ mặc định (Forms có Ranking) không đổi. `du_lieu_test/demo_t4m.py`: bỏ workaround `_lop_theo_email` + `set_student_class`. Test mới trong `tests/test_t4m_chi_thi.py`: `test_q1b_*` (3); sửa kỳ vọng của `test_q1_khong_co_bai_thi_so_nhap_trung_khit_ban_khong_diem` vì dữ liệu Lists của test có lớp 9A1. Không đổi hợp đồng CSV, schema, lõi.

## 2026-11-06 — T4M-VH (bước S1): vận hành một đợt xếp CLB, chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` (mới, 99 dòng): 8 bước cho IT của trường (dựng bài thi, mở/đóng, khoá, xuất, chuyển đổi, nạp kiosk, xuất theo lớp, em đến muộn/rút); mỗi bước có lệnh hoặc đường bấm, chỗ kiểm, cách xử lý lỗi, tệp cần giữ. Phần chưa thử gắn nhãn TH, phụ thuộc trường gắn HỎI-IT. Không đổi mã, schema, hợp đồng CSV. Test mới: không (tài liệu).

## 2026-11-06 — T4M-GOI-TK (bước S2): thiết kế gói nhiều buổi (tiếng Nhật), chỉ tài liệu

Không có mã. `docs/he_sinh_thai/T4M_GOI_THIET_KE.md` (mới): bộ điều phối hai pha đặt trên `run_rbda_nhieu_buoi` (pha 1 DA trên các gói như buổi giả `goi`, cấp độ là bộ lọc điều kiện ở dữ liệu vào, cam kết cả năm chỉ trừ chỉ tiêu; pha 2 từng ngày với ngày của gói bị khoá), so với hai phương án bị loại và một phương án V0 dự phòng; phân tích bất biến 1, 2, 3, 4, 5, 8 kèm phản ví dụ cặp phá vỡ toàn tuần và nhãn "bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói"; đề xuất đổi hợp đồng CSV / schema tương thích ngược (chờ Truong, quy tắc 7); ba mục con đề xuất A8-GOI-1..3 kèm `kiem_nhan`; 8 câu hỏi cho giáo viên ECA; 5 quyết định chờ duyệt. Test mới: không có.

## 2026-11-06 — T4M-NC: kế hoạch tự chạy (S1 đến S4)

Chỉ tài liệu. `docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md` (mới): Truong duyệt 06/11/2026 bốn quyết định (gói tiếng Nhật chỉ thiết kế, nháp v0 GĐ4, tự chạy chuỗi, đo mô phỏng chỉ bảng số); chuỗi bước S1 T4M-VH, S2 T4M-GOI-TK, S3 T4M-GD4-V0, S4 T4M-DO kèm phụ thuộc, tiêu chí nhận, luật dừng, vòng điều phối và prompt từng bước.

## 2026-11-06 — T4M-DEMO (Truong duyệt 06/11/2026): chạy thử trọn chuỗi bằng một lệnh

Thêm công cụ; không đụng mã sản phẩm, schema hay hợp đồng CSV. Dữ liệu hoàn toàn MÔ PHỎNG.
- `mau_forms_thi_clb/tao_mau_forms.py`: `ghi_mau_xuat_chi_thi(de, duong, danh_sach, hat_giong)` dựng tệp Forms chỉ-thi giả khớp tệp Lists giả và `de_thi.json` (Email, cột câu, cột Points); cố ý gài email viết hoa, một phiếu nộp lần hai, một email lạ, một bài thi CLB không xếp nguyện vọng.
- `du_lieu_test/sinh_xuat_lists_gia.py`: `sinh`/`ghi_csv` nhận thêm `clb_theo_ngay` (mã CLB thật); bỏ trống thì từng byte như cũ.
- `du_lieu_test/demo_t4m.py` (mới): `python du_lieu_test/demo_t4m.py --ra <thư mục>` chạy Lists giả → Forms giả → `--chi-thi` → nạp Sổ nhập vào CSDL tạm (`import_so_nhap`) → `run_pipeline` → `export_theo_lop` → tóm tắt tiếng Việt. Tắt điểm quyết tâm (mặc định BẬT) trong CSDL tạm; gán lớp bằng `set_student_class` vì bộ chuyển đổi chưa chép cột lớp; nhân chỉ tiêu mẫu cho vừa số em (`--he-so-cho`, bản sao trong bộ nhớ).
- `mau_forms_thi_clb/README.md`: mục 0b "Chạy thử trọn chuỗi".
- Test mới (viết trước): `tests/test_demo_t4m.py` (11 ca): hình dạng tệp, xác định, cảnh báo mong đợi, đủ tệp ra, không tạo `.db` ngoài thư mục tạm. Thử gây hỏng 5 chỗ: bỏ email viết hoa sống sót ở lần đầu, đã siết test; 4 chỗ còn lại bị bắt.

## 2026-11-05 — T4M-Q1, T4M-Q2, T4M-Q3 (Truong duyệt 05/11/2026): chế độ "chỉ thi" của mẫu Microsoft Forms

Thêm chế độ mới; chế độ mặc định giữ nguyên (`CAI_DAT_FORMS.md` sinh lại giống hệt tệp trong kho, test cũ 25/25 đạt). Không đụng lõi thuật toán, backend, giao diện, hợp đồng CSV hay bất biến nào; `kiem_nhanh.py` 7/7 ĐẠT (gồm `trung_khit` 15 ca). Dữ liệu thử đều MÔ PHỎNG.
- **Q1** `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py`: `--chi-thi --lists DANH_SACH.csv` (nhận nhiều tệp `.xlsx` khi biểu mẫu tách theo buổi). Hàm mới `doc_lists`, `phan_tich_chi_thi`, `chuyen_chi_thi`. Khoá là cột Email Forms (`lower().strip()`) ghép với cột Email của tệp xuất List (mô hình rộng, `Thu`, `NV1..NVn`, `HoTen`). Phiếu trùng giữ phiếu ĐẦU; email lạ báo và bỏ; thi CLB mà List không có nguyện vọng CLB đó thì bỏ điểm (vẫn có trong `BANG_DIEM.xlsx`) và báo; không có bài thi thì Sổ nhập chỉ có nguyện vọng, không điểm. Tách nhẹ hàm dùng chung `_doc_cot`, `_ap_tran_thi` (hành vi chế độ cũ không đổi).
- **Q2** `bieu_mau.py`: `cac_phan/re_nhanh(..., chi_thi, buoi)`, `dem_cau`, `chia_theo_buoi`, `TRAN_CAU_MOI_BIEU_MAU = 200`, `cau_cong_thi(..., chi_thi)`. `tao_mau_forms.py --chi-thi [--ra]`: bỏ Ranking và ô gõ mã HS/họ tên (Forms tự ghi Name + Email), settings "Record name" + "One response per person"; tách theo buổi khi tổng câu vượt 200; `.docx` giống hệt từng byte khi `de_thi.json` không đổi (giờ zip và thuộc tính tài liệu cố định). Sinh `CAI_DAT_FORMS_CHI_THI.md`, `NHAP_FORMS_CHI_THI.docx` (60 câu, một biểu mẫu cho `de_thi.json` hiện tại).
- **Q3** `mau_forms_thi_clb/GHI_CHU_GIAO_VIEN.md` (một trang): Quick Import, tick đáp án + điểm, Settings bắt buộc, giới hạn 200 câu / 400 biểu mẫu, Post scores không cần cho kiosk; khớp mục 7.1 của `T4M_KET_QUA_TAI_LIEU.md`. `README.md` của mẫu thêm mục 0.
- Test mới (viết trước): `tests/test_t4m_chi_thi.py` (27 ca). Thử gây hỏng 4 chỗ (bỏ hạ chữ thường email, bỏ giữ phiếu đầu, đổi ranh giới 200, bỏ dedupe List): ban đầu ranh giới 200 sống sót, đã thêm ca biên đúng 200 câu rồi đỏ đúng.
- Lệch nhỏ so với đặc tả cần Truong biết: bỏ cả ô gõ họ tên (không chỉ mã HS) vì Forms ghi Name tự động; tên cột List cố định (`Email`, `Thu`, `NV1..`, `HoTen`) và mã CLB trong List phải là `club_id` của `de_thi.json`.

## 2026-11-05 — T4M-NC P5: đường thu điểm thi trên Microsoft (NC-23, 24, 27)

Chỉ tài liệu. `T4M_KET_QUA_TAI_LIEU.md` mục 7 (mới): Forms Quiz (điểm, cài đặt, giới hạn 200 câu / 400 biểu mẫu, cột xuất Excel), connector Forms chỉ đọc và không có trong Power Apps, không có API được hỗ trợ để tạo biểu mẫu, Quick Import không mang đáp án; bài thi trong Power Apps và rủi ro lộ đáp án; phát hiện `mau_forms_thi_clb/` đã có sẵn đường Forms Quiz; bảng so sánh, khuyến nghị tạm V1 Forms Quiz; đặc tả ghép điểm NC-25; mã mục đề xuất T4M-Q1 đến Q3. `T4M_KE_HOACH_NGHIEN_CUU.md`: thêm NC-27. `T4M_PHIEU_PHONG_VAN.md`: thêm ECA-9 đến 11, IT-14.

## 2026-11-05 — T4M-NC GĐ3 (tài liệu): hướng dẫn thử môi trường Microsoft + bộ sinh tệp xuất Lists giả

`docs/he_sinh_thai/T4M_HUONG_DAN_THU.md` (mới): hai người đọc (Truong nếu có môi trường thử; bản một trang cho IT = dự phòng B); kho SharePoint List, mô hình RỘNG (một dòng mỗi em mỗi ngày, `NV1..NV3`), mô hình dài ghi là phương án bị loại kèm lý do; màn Top 3, màn gói tiếng Nhật, flow xuất CSV và flow gửi Excel theo lớp (không ghi từng dòng, NC-13); bảng pass/fail/lý do; mục Premium kèm phương án chuẩn; thời gian đều là ước lượng mô phỏng. `du_lieu_test/sinh_xuat_lists_gia.py` (mới): chỉ thư viện chuẩn, `random.Random(seed)`, mặc định 1.500 em × 5 ngày = 7.500 dòng, UTF-8 có BOM, email giả (có chữ hoa), có ngày trống và dòng gói tiếng Nhật. `tests/test_sinh_xuat_lists_gia.py` (mới, 7 test, viết trước): tái lập theo seed, số dòng, BOM, không trùng NV, cột khớp tài liệu, email, dòng đặc biệt. Không đổi mã sản phẩm, hợp đồng CSV hay bất biến nào. Dữ liệu hoàn toàn mô phỏng.

## 2026-11-05 — T4M-NC: quyết định thi tuyển theo RB-DA (Truong), thêm NC-23 đến NC-26 và prompt P5

Chỉ tài liệu. `T4M_KE_HOACH_NGHIEN_CUU.md`: dòng "Ưu tiên" mục 1 ghi quyết định 05/11/2026 (trường đổi quy trình theo RB-DA; CLB có thi dùng Tầng 1, bài thi do giáo viên ra, công cụ của dự án dựng giúp); hệ quả với bất biến 2 và 7; bốn câu mới NC-23 (Forms Quiz), NC-24 (tạo form bằng công cụ), NC-25 (ghép điểm vào `score_k`), NC-26 (luật công bằng của bài thi); prompt P5. Tệp bàn giao cập nhật.

## 2026-11-05 — T4M-NC chuẩn bị GĐ2: phiếu phỏng vấn in mang theo

Chỉ tài liệu. `docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md` (mới): gộp mục 6 của kế hoạch với mục 4 và cột "Còn hỏi IT" của kết quả GĐ1; 5 câu CHẶN cho IT (NC-01, 02, 03, 08, 16), 8 câu IT khác, 8 câu cho giáo viên ECA, mỗi câu có bối cảnh một dòng và chỗ ghi trả lời; nhắc riêng tư; checklist sau buổi gặp (mốc C2, dự phòng A/B). Kế hoạch bàn giao: P3 sửa sang mô hình kho rộng (một dòng mỗi em mỗi buổi) và hai người đọc (Truong hoặc IT).

## 2026-11-05 — T4M-NC GĐ1 + P4: kết quả đọc tài liệu Microsoft / PowerSchool, hợp đồng nhập của kiosk

Chỉ tài liệu. `docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md` (mới): 16 câu NC loại tài liệu, nhãn ĐXM / TT-CXM / GĐ / HỎI-IT, nguồn và ngày đọc; P4 tóm tắt hợp đồng nhập (`api_nhap.py`, `so_nhap.py`); câu mới cho IT; ma trận quyết định điền trước. Phát hiện chính: Dataverse for Teams và Developer Plan ngừng tạo mới từ 15/11/2026; PowerSchool không có trong danh sách OneRoster của SDS; hồ sơ Low của Power Automate (6.000 yêu cầu/người/ngày) nên V1 không ghi kết quả về app từng dòng; Sổ nhập không biểu diễn được CLB nhiều buổi. `TIEN_DO.md`: T4-K2 tạm dừng (Truong quyết 05/11/2026).

## 2026-11-05 — Z-CLAUDE-GON (ngoài sổ, Truong yêu cầu 05/11/2026; Truong duyệt bản tiếng Anh)

Chỉ tài liệu. `CLAUDE.md` gọn lại (9.112 B → 5.512 B): viết tiếng Anh (vẫn yêu cầu trả lời Truong bằng tiếng Việt); quy tắc 3 và 5 trỏ về bất biến 1 và 8 thay vì lặp; giữ nguyên số quy tắc 1–11 (tệp khác trỏ theo số) và câu "Trước khi push: chạy skill `soat-ma`" (test kiểm). Đoạn "Kiểm verify nhanh" và ghi chú thời gian bộ test chuyển nguyên văn sang `docs/ke_hoach/CLAUDE_CHI_TIET.md`. Test liên quan: `tests/test_skill_soat_ma.py`, `tests/test_a13_12_tai_lieu.py`, `tests/test_hook_ban_giao.py` (61 đạt).

## 2026-11-05 — T4M-NC (ngoài sổ, Truong yêu cầu 05/11/2026): kế hoạch nghiên cứu hệ sinh thái Microsoft của trường

Chỉ tài liệu; không đổi mã, test, hợp đồng CSV hay bất biến nào.

- `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (mới): hồ sơ hệ thống đăng ký ECA của trường (Power Apps, M365 A3/A5, PowerSchool; Truong trả lời, chưa kiểm với IT), gói tiếng Nhật nhiều buổi và hướng xếp hai pha, 22 câu nghiên cứu NC-01 đến NC-22, quy tắc bằng chứng (ĐXM / TT-CXM / GĐ / HỎI-IT / TH), lộ trình 5 giai đoạn kèm hai kế hoạch dự phòng, bộ câu hỏi phỏng vấn IT và giáo viên ECA, mẫu ma trận quyết định, bốn prompt P1 đến P4.
- `docs/phien/claude__upbeat-shannon-g5nnms.md` (mới): tệp bàn giao của nhánh.
- T4-K2 (Google) chưa được đánh dấu tạm dừng: chờ Truong quyết.
- Gọn prompt (cùng ngày): luật chung gom một chỗ (mục 8.0, C1 đến C4) thay vì lặp ở từng prompt; prompt viết tiếng Anh; mỗi prompt chỉ đọc đúng mục cần; mục 4 bỏ phần trùng `CLAUDE.md`; báo cáo cuối có trần độ dài. Nội dung yêu cầu giữ nguyên.

## 2026-11-05 — T3-L5 (ngoài sổ, Truong yêu cầu): Điểm chuẩn cùng nền các thẻ khác, thẻ 05 chỉ ghi "Quản lý"

- `style.css`: bỏ hai khối nền tối riêng của `#adminDiemChuanBlock` (`prefers-color-scheme: dark` và `[data-theme=dark]`); khối giờ dùng nền trắng như các thẻ khác.
- `i18n.js`, `index.html`: `nav_admin` = "Quản lý" / "Manage" (thanh bên). `admin_title` (tiêu đề trang) cũng đổi thành "Quản lý" / "Manage".
- Test: `tests/test_giao_dien_a13_10_diem_chuan.py` (thay test chế độ tối bằng test cùng nền), `tests/test_giao_dien_t3_l3.py`, `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json` (thêm `nav_admin`).

## 2026-11-04 — T3-L4 (ngoài sổ, Truong duyệt 04/11/2026): thứ tự tệp "Tải bảng này", bỏ dòng nhắc chết, Điểm chuẩn gọn

- Chỉ hiển thị / xuất theo màn hình; không đổi CSV, schema hay kết quả xếp.
- `api_xuat.py::export_bang_dang_xem`: thêm tham số tuỳ chọn `thu_tu` (mã theo thứ tự đang hiện); hàng tệp đi theo thứ tự đó, mã lạ xếp cuối. Không truyền thì như cũ. `js/09_the_xem.js`: `kqThuTuMan()` gửi thứ tự sắp hiện tại của tiêu đề cột.
- Bỏ nhánh "Chưa có lớp nào" của Theo lớp (`veKqTheoLop`) và khoá `theolop_khong_co_lop` (vi, en) trong `i18n.js`.
- `style.css`: nút "Xem chi tiết" không xuống dòng; chú giải Điểm chuẩn thành hàng ngang có ô mẫu.
- Test: `tests/test_t3_l3_backend.py::test_xuat_theo_thu_tu_man_hinh_thu_tu`, `tests/test_giao_dien_t3_l3.py` (`test_tai_bang_theo_thu_tu_dang_sap_tren_man_hinh`, `test_diem_chuan_nut_mot_dong_va_chu_giai_gon_trong_css`); `test_giao_dien_a14_lop.py` bỏ test dòng nhắc chết, đếm khoá 25→24.

## 2026-11-04 — T3-L3 fix (điều phối): test "chưa có lớp" theo hành vi thật

- `tests/test_giao_dien_a14_lop.py::test_theo_lop_chua_co_lop_nao_hien_dong_nhac`: bỏ đoạn ép `kq.tang1 = 'lop'` (người dùng không tới được từ T3-16, và lần vẽ lại bất đồng bộ làm test chập chờn trên CI); nay kiểm nút "Theo lớp" ẩn, bảng có dòng, không có ngõ cụt "Chưa có lớp nào". Dòng nhắc trong `js/03_ket_qua.js` thành đường mã chết, ghi ở mục "Cần Truong" của PR #10.

## 2026-11-04 — T3-L2 fix3 (điều phối): test node chạy được trên Windows

- `tests/test_t3_l2_buoi.py::test_loi_co_tham_so_buoi_hien_nhan_khong_hien_ma`: `subprocess.run(["node", ...])` đọc đầu ra bằng `encoding="utf-8"` (CI Windows đọc cp1252 nên gặp chữ Việt thì `stdout` là `None`).

## 2026-11-04 — T3-L3 (ngoài sổ, Truong duyệt 04/11/2026): tên thẻ, thẻ Kết quả gọn, tải bảng, Điểm chuẩn một nơi, chữ Sổ nhập (nghiên cứu T3, lô 3)

Chỉ đổi hiển thị (thêm một API xuất đọc `match_results`); thuật toán, `match_results`, `run_history`, STB, hợp đồng cột CSV không đụng tới.

- **Tên thẻ:** 03 "Dữ liệu khác" thành "Chi tiết và xuất tệp" / "Details and export" (`nav_others`, `others_title`); 05 thành "Quản lý {slot_sl}" / "Manage {slot_pl}" (`nav_admin`, `admin_title`). Chữ báo lỗi nhắc tên thẻ 05 (`i18n_errors.py`) theo tên mới.
- **T3-16/17/18 (`js/09_the_xem.js`, `index.html`, `style.css`):** nút "Theo lớp" chỉ hiện khi đã có lớp (chưa có lớp thì mở sẵn "Theo mã học sinh"); bỏ hàng sắp xếp `#kqTang2` (và khoá `kq_sap_nhan`, `kq_sx_*`, `kq_aria_tang2`), sắp bằng cách bấm tiêu đề cột (`.kq-sx-cot`, `aria-sort`; mã tự nhiên, lớp tự nhiên, còn lại theo vần tiếng Việt, ô trống luôn cuối); bỏ cột "Thứ tự" (`th_stt`), giữ dòng đếm. `localStorage` `rbda_ket_qua_xem_v1` không còn `tang2`.
- **T3-19:** nút "Tải bảng này (Excel)" (`#btnKqTaiBang`) ở thẻ 02, API mới `export_bang_dang_xem(kieu, gia_tri, output_path)` (`api_xuat.py`): một tệp, một trang, đúng lớp / CLB / danh sách theo mã đang xem; không điểm, không số bốc thăm; không ghi đè; chưa có kết quả thì `xuat_chua_co_ket_qua`.
- **T3-22:** Điểm chuẩn chỉ còn ở thẻ 05, tab "Điểm chuẩn" (`#qlTabDc`); bỏ thẻ và nút `#dcKqPanel` / `#btnDcKqMo` ở thẻ 03 (cùng `veDiemChuanKetQua`, `dongDiemChuanKq`, `initDiemChuanKetQua`, khoá `dc_xem`, `dc_an`).
- **T3-31 (`js/05_quan_ly.js`):** Điểm chuẩn mặc định MỘT bảng bằng số (CLB, điểm thi chuẩn, điểm quyết tâm chuẩn, "N đơn · M chỗ") + nút "Xem chi tiết" từng CLB; biểu đồ chấm và bảng hai cách xét x hai mức chuyển vào chi tiết (đóng bằng "Đóng chi tiết"); bỏ thanh điểm, thanh xếp chồng ba màu, ba mức "Đủ chỗ / Đông / Rất đông", hộp chọn CLB và các khoá `dc_muc_*`, `dc_bar_*`, `dc_chu_giai_thanh`, `dc_muc_giai_thich`, `dc_thanh_nhan`, `dc_ti_le_nhan`, `dc_chon_clb`.
- **T3-27:** chữ giao diện = chữ Sổ nhập ở mọi nơi trong `i18n.js`, `index.html`, `i18n_errors.py`: Chỉ tiêu (thay "Tổng chỗ"), Suất ưu tiên (thay "Suất dự trữ"), Nhóm ưu tiên (thay "Nhãn dự trữ"); tiếng Anh Quota / Priority seats / Priority group. Chỉ chữ hiển thị; không đổi mã, cột CSV hay tiêu đề cột trong tệp Excel xuất (`api_xuat.py`).
- **T3-11 (`js/075_workspace.js`):** tạo workspace từ mẫu: bước 1 có nút "Tạo" ngay (2 cú bấm) và nút "Tuỳ chỉnh từ vựng và luật" (`#wzTuyChinh`, kiểm tên trước) mở bước 2 đến 4; thanh bước và bước "Xem lại" chỉ có khi tuỳ chỉnh; dòng "Thứ tự các nhóm" trống ẩn đi.
- **Test mới:** `tests/test_t3_l3_backend.py` (7), `tests/test_giao_dien_t3_l3.py` (Chromium). **Test cũ sửa:** `test_giao_dien_t2_ket_qua.py` (viết lại ca tầng 2, sắp theo tiêu đề cột, không lớp), `test_giao_dien_diem_chuan.py`, `test_giao_dien_a13_10_diem_chuan.py` (một bảng, chi tiết mở theo yêu cầu, thẻ 03 không còn Điểm chuẩn), `test_i18n_khoa_dc_khong_chet.py`, `test_ws_nhan.py` (+ `chu_ui_doi_co_y_t3.json`: bảng thay chữ T3-27), `test_giao_dien_danh_sach_clb.py`, và các test đi qua trình hướng dẫn (`test_ws_giao_dien.py`, `test_giao_dien_a13_12_ws.py`, `test_giao_dien_a13_13_kiem_nhan.py`, `test_giao_dien_a14_lop.py`, `test_giao_dien_t3_l1_ws.py`, `test_ws_wharton_giao_dien.py`: bước 2 mở bằng "Tuỳ chỉnh").
- **Sửa test sau CI (13 ca):** `test_giao_dien_a14_lop.py` (bỏ cột "Thứ tự", tiêu đề cột kèm ▲, 25 khoá i18n, dòng nhắc "chưa có lớp" ép bằng `kq.tang1`), `test_giao_dien_a13_10_nhan.py` (bấm "Xem chi tiết" trước khi chờ `#dcChiTiet`; ≥ 50 khoá `dc_*`), `test_giao_dien_a13_12_ngon_ngu.py` (so thứ tự CLB, nhãn buổi đổi theo ngôn ngữ), `test_giao_dien_t2_ket_qua.py` và `test_giao_dien_wharton_quan_ly.py` (chờ vẽ xong, hết chạy đua). Không đổi mã sản phẩm.
- **Không làm (Truong):** T3-41 (ô trống "—" giữ nguyên), bỏ số 01 đến 06 ở thanh bên.

## 2026-11-04 — T3-L2 fix2 (điều phối): test bảng lỗi theo nhãn buổi

- `tests/test_giao_dien_bang_loi.py`: mẫu `health_thi_qua_tran_buoi` dùng buổi chữ tự đặt ("Buổi tối") thay cho mã `thu_2`, vì từ T3-L2 giao diện đổi mã buổi sang nhãn còn `format_message` giữ mã; phần đổi mã đã có test ở `tests/test_t3_l2_buoi.py`.

## 2026-11-04 — T3-L2 (ngoài sổ, Truong duyệt 04/11/2026): bớt khối, gom nút (nghiên cứu T3, lô 2)

Chỉ đổi hiển thị; thuật toán, `match_results`, `run_history`, STB, hợp đồng cột CSV không đụng tới.

- **T3-14:** nhãn buổi (Thứ 2…) qua `i18n.js`, bảng JS phản chiếu `so_nhap.NHAN_BUOI` (đường a). **T3-07:** bỏ hai ô Từ/đến chọn buổi. **T3-02/03/04:** cảnh báo gọn + nút tới Điểm quyết tâm; ẩn nút khi chưa có tệp (sửa lỗi `.import-actions{display:flex}` đè `hidden`); một nút kiểm tra.
- **T3-06/10/12/15:** dòng kết quả gọn; một nút chính theo trạng thái (`#view-pipeline[data-trang-thai]`); chân thanh bên + menu ⋯; dòng workspace "Mở" + ⋯.
- **T3-20/24/25:** mục "Chi tiết để kiểm tra"; ba ô tóm tắt (số NV1 và suất dự trữ chuyển xuống mục chi tiết, không xoá); tiêu đề cột.
- **T3-21:** bỏ thẻ "Mức lấp đầy của từng CLB" (`#fillPanel`); ô "Sắp xếp" (`#fillSapXep`, vẫn nhớ qua `rbda_sap_xep_lap_day`) chuyển lên thẻ "Theo từng câu lạc bộ"; bảng thêm cột thanh lấp đầy (hai đoạn dự trữ/chung, `veOThanhLapDay`) và cột "Lưu ý" (nhãn `nhanCanDeY` thành chữ, không còn chỉ hiện khi rê chuột); ô tóm tắt "Chỗ còn trống" mở thẻ này và đặt "Vắng nhất". Bỏ `veBieuDoLapDay`/`veDongLapDay`, CSS `.fill-row…`, khoá `fill_panel_title`, `fill_hint`, `fill_nhom_tong`, `fill_choi`; khoá mới `th_muc_lap_day`, `th_luu_y`.
- **T3-23:** khung "Xuất dữ liệu" mặc định chỉ hai nút "Xuất kết quả (Excel)" (`btn_xuat_tuy_chon`) và "Xuất theo lớp"; các ô tích và "Chọn học sinh…" nằm trong `<details id="xuatNangCao">` "Tuỳ chọn khác" (`xuat_tuy_chon_khac`); giữ cảnh báo đỏ.
- **T3-28:** một bảng "Tải theo buổi"; bỏ khối "Lịch tuần" (`loadLichTuan`, `admin_lich_tuan_*`, CSS `.lich-*`); tỉ lệ ghi "2,3" (dấu phẩy), không "2.3×".
- **T3-29/32/33/34/35:** điểm quyết tâm mặc định "Chỉ hồ sơ có vấn đề"; hàng học sinh mới cạnh ô tìm + cuộn tới phiếu; lớp hiện dạng chữ; menu ⋯ ba nút phụ (giữ "Xuất CSV học sinh này"); bỏ mã thô, chấm "Chưa lưu" nổi hơn. Chưa làm: thu gọn danh sách kết quả sau khi chọn (T3-32).
- **Test mới:** `tests/test_t3_l2_buoi.py` (5), `tests/test_giao_dien_t3_l2_van_hanh.py` (Chromium). **Test cũ sửa:** `test_giao_dien_tom_tat_ket_qua.py` (bỏ test chú thích rê chuột và nhóm theo buổi, thêm test cột thanh/Lưu ý), `test_giao_dien_bieu_do.py`, `test_giao_dien_phong_chu.py`, `test_giao_dien_thu_gon_ket_qua.py`, `test_giao_dien_diem_chuan.py` (đọc bảng CLB thay vì `.fill-row`), `test_giao_dien_khoa_xuat.py`, `test_giao_dien_ux_xuat.py`, `test_giao_dien_xuat_du_lieu.py` (mở "Tuỳ chọn khác"), `test_ws_nhan.py` + `du_lieu_ws/chu_ui_doi_co_y_t3.json`.
- **Vòng sửa 1 (tester L2):** `btn_reset_entry` = "Xoá toàn bộ phiếu của {person_l} này" / "Clear this {person_l}'s whole entry" (khớp câu xác nhận); lỗi/cảnh báo có tham số `buoi` là mã (`thu_2`) nay hiện nhãn (`nhanHoaBuoi` trong `translateError`, `i18n.js`); dòng "Lần chạy gần nhất" ở thẻ 03 dùng `dinhDangGio` và bỏ số khởi tạo; cột "Thao tác" trống ở danh sách workspace thành `sr-only`; test `test_t3_l2_buoi.py` canh tập mã `MA_BUOI_CO_NHAN` khớp `so_nhap.NHAN_BUOI` và lỗi có `buoi` hiện nhãn. T3-32 phần "thu gọn danh sách sau khi chọn" vẫn bỏ: nhiều test UI cũ bấm thẻ khác sau khi chọn; cuộn tới phiếu đã có.
- **Bất biến:** `kiem_nhanh.py` 7/7 ĐẠT, `trung_khit` (3 bộ × 5 seed) trùng khít so với `origin/main`.

## 2026-11-04 — CI-HUY (ngoài sổ, Truong yêu cầu 04/11/2026): huỷ lượt CI cũ khi có commit mới

- **`.github/workflows/tests.yml`:** thêm `concurrency` (nhóm theo workflow + loại sự kiện + nhánh; `cancel-in-progress` trừ nhánh `main`). Workflow build `.exe` (chạy tay) không đổi.

## 2026-11-04 — T3-L1 (ngoài sổ, Truong duyệt 04/11/2026): chữ và hiển thị nhỏ (nghiên cứu T3, lô 1)

- **T3-05:** ô mã bốc thăm vào mục "Nâng cao" thu gọn (`<details id="nangCao">`, mặc định 42, mở tự động khi bấm "Bốc thăm lại"); bỏ `#seedLockHint`; `stb_locked_label` thành một dòng "Đã bốc thăm lúc {locked_at}. Muốn bốc thăm lại, bấm "Bốc thăm lại…"." (giờ dạng người đọc).
- **T3-08:** bỏ ô "đã nộp nguyện vọng" (`#statPrefs`) khỏi dải số liệu; giờ chạy dạng `dd/mm/yyyy hh:mm` (`dinhDangGio` ở `js/00_nen.js`) ở chân thanh bên và bảng lịch sử; bỏ "số khởi tạo" khỏi `#lastRunLine`.
- **T3-09:** thẻ Lịch sử sắp xếp chỉ hiện khi có từ 2 lần chạy (`capNhatTheLichSu`); không đụng `run_history`.
- **T3-13:** bỏ dòng phụ "Reserve-Based DA"; tiêu đề trang và cửa sổ không còn "RB-DA" (`page_title`, `APP_TITLE`).
- **T3-30:** tab con "Dữ liệu" đổi thành "Xoá dữ liệu" (en "Delete data").
- **T3-36:** bảng tiến độ chấm bỏ cột mã CLB và thanh tiến độ; nút "Chấm" là nút phụ không mũi tên.
- **T3-37/38/39:** tiêu đề bước hộp tạo workspace "Bước n/4: …"; tiêu đề cửa sổ và `aria-label` dùng " · " hoặc ": " thay gạch dài (`main.py`, `js/075_workspace.js`, `js/04_nhap_tai_cho.js`); khoảng số "(từ 1 đến 20)", "(từ 0 đến 20)".
- **T3-40:** chữ dự phòng của `index.html` khớp catalog (62 chỗ); test mới `tests/test_t3_l1_chu_du_phong.py` canh từng phần tử `data-i18n`, placeholder và aria-label. Sửa kèm `wh_sua_rong` (đầu câu viết thường).
- **T3-43:** chữ trong tệp Excel xuất (`api_xuat.py`, 51 chuỗi): bỏ gạch dài và đại từ "em", dùng `{person_l}` theo từ vựng workspace; hai chuỗi đếm của trang "Theo lớp" nay cũng qua `t.n` (trước đây lọt `em` cứng khi workspace đặt tên khác).
- **Bảng 5.1-5.3 (trừ mục để lô sau):** tên thẻ "Xếp CLB" (`nav_pipeline`, `pipeline_title`), "Nhập nguyện vọng" (`nav_fallback`, `fallback_title`) và mọi chỗ nhắc tên thẻ (catalog, `i18n_errors.py`, `HUONG_DAN_SU_DUNG.md`); sáu mô tả `pipeline_desc`, `others_desc`, `admin_desc`, `scoring_desc`, `fallback_desc`, `import_hint`; nhãn "Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên"; "Số đơn và số chỗ", "Học sinh trên mỗi chỗ", "Chọn là nguyện vọng 1"; `xuat_hint_hoc_sinh`, `xuat_opt_kem_csv`; nút `ws_btn_*`. Lệch khỏi bảng có chủ ý: tiếng Việt giữ "tệp nén" và en "archive file" (test `test_giao_dien_tieng_viet_sach` cấm chữ zip); "Draw code" thay "Draw seed" (cấm từ kỹ thuật); `pipeline_desc`/`import_hint` viết "sổ nhập" thường, không "Sổ nhập CLB" (từ vựng workspace). Chưa làm ở lô này (để L2/L3): hai dòng cảnh báo gộp T3-02 (hàng 213, 214 của bảng 5.3), `nav_others`, `nav_admin`, `ql_tab_dc`, `kq_sx_ngay`, `kq_sap_nhan`.
- **T3-27 chia hai lô (tester L1, vòng 1):** L1 làm nhãn và placeholder của biểu mẫu CLB ở thẻ Quản lý (`th_capacity`, `th_reserve_capacity`, `th_reserve_group`, `placeholder_capacity`, `placeholder_reserve_capacity`, `placeholder_reserve_group`: Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên; en Quota / Priority seats / Priority group) và `admin_desc`. Phần còn lại của T3-27 (`th_tong_cho`, `admin_reserve_assign_title`, các chỗ khác nói "dự trữ") để L3.
- **Vòng sửa 1 (tester L1):** test Excel cũ `test_so_excel_de_dung.py` đọc theo chữ mới ("Số học sinh đã có câu lạc bộ", "Số học sinh chưa có chỗ", "mọi học sinh đều"); `th_ti_le_choi` dùng chỗ giữ danh từ (`{person} trên mỗi chỗ`, en `{person_p} per place`).
- **Khoá catalog bỏ:** `brand_sub`, `label_submitted_prefs`, `seed_locked_hint`, `seed_unlocked_for_redraw`; khoá mới `nang_cao`.
- **Test mới:** `tests/test_t3_l1_chu.py` (4), `tests/test_t3_l1_chu_du_phong.py` (1), `tests/test_giao_dien_t3_l1.py` (7, Chromium), `tests/test_giao_dien_t3_l1_ws.py` (1, Chromium). **Test cũ sửa theo chữ mới:** `test_ws_nhan.py` (bảng ảnh chụp: `KHOA_UI_DA_BO`, `THAY_CHU_T3`, `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json`), `test_ws_nhan_giao_dien.py`, `test_giao_dien_khoa_hat_giong.py`, `test_giao_dien_chay.py`, `test_giao_dien_sua_loi_p1.py`, `test_giao_dien_xoa_du_lieu.py`, `test_giao_dien_quan_ly_tab_con.py`, `test_giao_dien_a13_10_diem_chuan.py`. Bản đồ mã: 188 tệp test, 3.396 ca.
- **Bất biến 1:** `kiem_nhanh.py trung_khit` (3 bộ × 5 seed) ĐẠT so với `origin/main`; lô này không đổi thuật toán.

## 2026-11-04 — T3-L0 (ngoài sổ, Truong duyệt 04/11/2026): ba lỗi sản phẩm của nghiên cứu T3 (B1/T3-26, B2/T3-01, B3/T3-42)

- **B1 / T3-26 — sửa CLB không còn xoá suất dự trữ, nhãn, buổi.** `api_quan_ly.py::create_or_update_club`: `reserve_capacity`, `reserve_group`, `buoi` mặc định `None` = "không gửi" — CLB đã có thì GIỮ giá trị đang lưu, CLB mới lấy 0 / không nhãn / không buổi; `name=None` giữ tên cũ; muốn xoá thật thì gửi 0 hoặc `""`. Kiểm suất dự trữ ≤ chỉ tiêu dùng giá trị hiệu lực (kể cả giá trị cũ). Lời gọi tường minh cũ (`("c","C",5,0,"")`) cho kết quả y như trước. Giao diện (`js/05_quan_ly.js`, `index.html`, `style.css`): sáu nhãn thường trực phía trên sáu ô (dùng lại khoá `th_*`); bấm một dòng bảng thì điền biểu mẫu từ dòng đó, khoá ô mã, nút Huỷ; khi đang sửa ô trống = xoá, gõ tay thì ô trống = không gửi (`null`).
- **B2 / T3-01 — chạy trên dữ liệu trống bị chặn.** `api.py::_run_pipeline_da_khoa`: bước 0, TRƯỚC sao lưu / khoá STB / mọi lần ghi, đếm học sinh và CLB; thiếu một trong hai thì trả `chua_co_du_lieu_de_chay` (không ghi `run_history`, không khoá seed). Giao diện (`js/02_van_hanh.js`): `khoa.thieuDuLieu` khoá nút "Chạy sắp xếp" kèm `title` lý do, ô Cảnh báo ghi "Chưa có dữ liệu để xếp…" thay cho dòng xanh.
- **B3 / T3-42 — câu `wharton_ho_so_chua_hop_le`** chỉ việc làm được (thẻ 05, tab Điểm quyết tâm, "Phóng cho đủ 100 theo tỉ lệ"), không còn bảo tắt tính năng. Chỉ đổi chữ (vi + en), không thêm công tắc.
- **Mã lỗi mới** `chua_co_du_lieu_de_chay` (`i18n_errors.py` vi+en, đã sinh lại `i18n_loi.js`); khoá UI mới `health_chua_co_du_lieu` (`i18n.js` vi+en).
- **Sửa CI L0 (fixci1):** nghiệm thu A13.13 đổi chữ theo quyết định B3 của Truong (04/11/2026): `test_a13_13_kiem_nhan.py` (D1, E3) và `test_wharton_mac_dinh_bat.py` nay đòi câu chỉ trỏ tới việc làm được (điền điểm, "Phóng cho đủ 100"), KHÔNG còn đòi chữ "tắt"; `test_a13_9_stress.py::test_8_so_rong_...` nay đòi chạy xếp trên sổ rỗng bị từ chối `chua_co_du_lieu_de_chay` (không sập, không `run_history`, không khoá STB); mã mới thêm vào `MA_MOI_SAU_ANH_CHUP` của `test_ws_nhan.py`.
- **Test mới:** `tests/test_t3_l0_backend.py` (11 ca), `tests/test_giao_dien_t3_l0.py` (7 ca, Chromium).
- **Vòng sửa 1 (tester):** ô "Suất dự trữ" mặc định để TRỐNG (trước là "0" nên gõ tay lại mã cũ vẫn xoá suất dự trữ); câu B3 bản tiếng Việt dùng "mục Điểm quyết tâm" thay "tab" (test `test_giao_dien_tieng_viet_sach`).
- **Bất biến 1:** cấu hình mặc định trùng khít `origin/main` — `kiem_nhanh.py trung_khit` (3 bộ × 5 seed) và `kiem_trung_khit` gọi trực tiếp với 20 seed (3 bộ × 20 seed).

## 2026-11-04 — T3-HT (ngoài sổ, Truong duyệt 04/11/2026): hạ tầng tự động hoá T3 (điều phối + viết mã + soát)

- **`.claude/hooks/handoff_khi_day_ngu_canh.py`:** đọc vai phiên từ `.claude/phien_vai.json` (không vào git): ngưỡng riêng (`nguong`; con 400k, điều phối 700k), tệp bàn giao theo vai (`docs/phien/<nhánh>__impl.md`, `__tester.md`), phiên con được nhắc `send_message` báo phiên điều phối; không có tệp vai thì giữ hành vi cũ. Lấy tên nhánh bằng `git branch --show-current`.
- **Tài liệu:** `docs/phien/T3_GIAO_THUC.md` (giao thức, khuôn tin nhắn, bàn giao), `docs/phien/claude__gallant-mendel-uki8j2.md` (kế hoạch bốn lô T3-L0..L3 và quyết định của Truong).
- **Test:** `tests/test_hook_ban_giao.py` (6 ca).
- **Sửa CI:** `docs/ke_hoach/CLAUDE_CHI_TIET.md` bản đồ mã đếm lại: 184 tệp test, 3.384 ca (test `test_ban_do_ma_so_tep_test_la_so_that`). `tests/test_hook_ban_giao.py` giữ PATH hệ thống (CI Windows không tìm thấy git) và chỉ `git init` một lần mỗi thư mục.

## 2026-11-04 — sửa CI main 3c67776: test giao diện A14 chập chờn

- `tests/test_giao_dien_a14_lop.py::test_theo_lop_nhieu_buoi_cot_theo_ngay_o_trong_va_dong_do`: CI Linux (run 41803199666) báo `IndexError` ở `r.split("\t", 3)[3]` — `innerText` của `<tr>` chỉ có dấu tab khi bảng đã được vẽ bố cục. Nay chờ đủ 3 hàng rồi đọc từng ô bằng `textContent`, kiểm mỗi hàng 6 ô. Chỉ sửa test; máy cloud chạy cả tệp 3 lần đều 24/24 xanh.

## 2026-11-04 — PR #8: sửa CI sau T4-K1 (Windows báo 4 lỗi ở 5a88060)

- `test_a14_sua_sau_soat.py::test_a5_...` (DROP COLUMN): đã khỏi khi gộp main (lấy bản B9 của main).
- **`docs/ke_hoach/tham_khao/_chung.py::nap_rb`:** từ T4-K1 `rbda_priority_pipeline` import `lop_hoc_sinh` theo tên; `_ten_can_nap` nạp `lop_hoc_sinh` (từ cùng thư mục hoặc cùng tệp .exe) trước mô-đun chính khi có, bản cũ không có thì bỏ như `nhan_ws`. `tests/test_tham_khao_verify_nhanh.py` chép thêm `lop_hoc_sinh.py` vào thư mục thử.
- `tests/test_mau_forms_thi_clb.py::test_raw_google_khop_tai_lieu_dinh_dang`: kỳ vọng dòng ghi RAW_PHIEU theo `.gs` mới (cột `lop` tuỳ chọn, T4-K1).

## 2026-11-03 — Z-SOAT-2 (ngoài sổ, Truong duyệt 03/11/2026): `soat-ma` tìm ruff trên PATH

- **`.claude/skills/soat-ma/scripts/kiem_nhanh.py::kiem_ruff`:** trước chỉ chạy `python -m ruff`, nên máy cài ruff bằng pipx / uv (máy cloud) luôn báo KHÔNG ĐẠT "chưa cài ruff" dù mã sạch. Nay khi Python không có mô-đun ruff thì thử `ruff` trên PATH (`shutil.which`); không có ở đâu cả mới báo chưa cài. Máy đã có mô-đun ruff: không đổi.
- **Test:** `tests/test_skill_soat_ma.py` thêm 2 ca (`test_ruff_chi_co_tren_path_van_chay`, `test_ruff_khong_co_o_dau_ca_thi_bao_chua_cai`); `_co_ruff` nhận cả ruff trên PATH nên ca cũ `test_ruff_dat_va_khong_dat` không còn bị bỏ qua trên máy đó. 47 ca xanh.

## 2026-11-03 — A14-B10 (ngoài sổ, Truong duyệt 03/11/2026): bỏ `DROP COLUMN` ở hai test A14 còn lại

Cùng kiểu rủi ro với B9 (SQLite của CI báo "incomplete input"). Chỉ sửa test, không đụng mã sản phẩm.

- Hàm phụ trợ mới `_bo_cot(conn, bang, cot)` (trong từng tệp test): đọc schema thật bằng `PRAGMA table_info`, dựng lại bảng thiếu đúng một cột (giữ khoá chính và dữ liệu) bằng `CREATE TABLE` / `INSERT ... SELECT` / `RENAME`, cú pháp có ở mọi bản SQLite. Không chép cứng schema, nên tự theo khi bảng thêm cột về sau.
- Dùng ở `tests/test_a14_tu_vung_cohort.py::test_di_tru_schema_them_cot_vao_csdl_cu_chay_lap_va_giu_du_lieu` và `tests/test_a14_sua_sau_soat.py::_csdl_cu_co_du_lieu`. Mọi assert giữ nguyên; 48 ca của hai tệp xanh.
- Trên nhánh này `test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien` vẫn là bản trước B9; bản sửa B9 có ở `main`, giữ nguyên để gộp không xung đột.

## 2026-11-04 — T4-K1 sửa vòng 1 (tester soát fff0f41)

- **[Chặn] Gói skill chạy ngoài kho:** `chuan_hoa_lop` chuyển sang mô-đun gốc kho mới `lop_hoc_sinh.py` (chỉ thư viện chuẩn, hành vi y hệt). `rbda_priority_pipeline.py` nhập lại và giữ tên công khai, nên mọi nơi gọi cũ và test cũ không đổi. `xu_li_raw.py` nhập từ `lop_hoc_sinh`; `dong_goi_skill.py` đưa `lop_hoc_sinh.py` vào `xu-li-raw-forms.zip` (skill không mang mã thuật toán). PyInstaller: `rbda_priority_pipeline` nhập `lop_hoc_sinh` ở mức mô-đun nên phân tích tĩnh tự gom, không cần đổi `kiosk.spec`.
- **Báo cáo lớp:** phiếu giữ không ghi lớp thì ghi rõ "phiếu giữ N không ghi lớp, phiếu M ghi X; Sổ để trống" (cả khi các phiếu khác nhau lẫn khi chỉ có một lớp ở phiếu khác); Sổ vẫn không mượn lớp. Tiêu đề mục đổi thành "Lớp không thống nhất giữa các phiếu của cùng một mã".
- **`.gs` (hai bộ sinh vẫn trùng):** khớp mã `ma_hs` bằng cắt khoảng trắng và IN HOA ở cả hai phía (`maLop_`); đếm mã học sinh không có trong tab `hoc_sinh` (`maKhongCoLop_`), ghi một dòng vào trang Cảnh báo và Logger. Tài liệu: cột `ma_hs` định dạng văn bản `@`.
- **Test:** `tests/test_t4_k1_lop.py` lên 12 ca (thêm: khớp mã chuẩn hoá và đếm mã không khớp ở `.gs`; gói zip chạy ngoài kho với cột `lop`; mở rộng ca phiếu giữ trống lớp).
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: thêm `lop_hoc_sinh.py` vào bản đồ mã.

## 2026-11-04 — T4-K1 (ngoài sổ, Truong duyệt 03/11/2026): cột `lop` tuỳ chọn từ `hoc_sinh` tới cột Lớp của Sổ

Thay đổi số 1 ở mục 11.2 của `docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md` (DEC-2: lớp lấy từ `hoc_sinh` lúc xuất, biểu mẫu KHÔNG hỏi lớp).

- **`xu_li_raw.py`:** `COT_RAW` giữ 19 cột. RAW có cột `lop` (cột thứ 20) thì ghi vào cột Lớp của Sổ (`ghi_so_nhap(co_lop=True)`, A14), lấy lớp từ PHIẾU GIỮ, chuẩn hoá bằng `chuan_hoa_lop` của phần mềm (không viết hàm mới). Các phiếu của cùng một mã ghi lớp (khác rỗng) khác nhau thì thêm mục "lop_khac_giua_cac_phieu" vào `BAO_CAO_BAT_THUONG.md`. Không có cột `lop`: Sổ và báo cáo y như cũ.
- **`TAO_GOOGLE_FORM.gs` và `tao_google_forms.py` (sinh giống hệt):** `chamTheoCLB(ghiLop)`, chỉ `ghiLop === true` mới bật (menu/trigger truyền đối tượng sự kiện không bật nhầm); mặc định TẮT thì RAW 19 cột như cũ. Bật thì thêm cột `lop` đọc từ tab `hoc_sinh` (`ma_hs`, `lop`); hàm mới `chamTheoCLBCoLop`, `docLopHocSinh_`, `themCotLop_`, hằng `ID_BANG_HOC_SINH`. Thiếu tab thì báo lỗi trước khi tạo thư mục. `COT_RAW` của `.gs` vẫn bằng của skill.
- **Tài liệu:** `DINH_DANG_RAW.md` (cột tuỳ chọn thứ 20), `SKILL.md` của `xu-li-raw-forms` và `tao-google-form-clb`.
- **Test mới:** `tests/test_t4_k1_lop.py` (10 ca lúc đầu, 12 sau vòng sửa 1): có `lop`; không có `lop` (Sổ bằng đúng cách cũ); `lop` rỗng; lớp khác nhau giữa các phiếu; phiếu giữ trống lớp; thư mục nhiều phần có `lop`; `.gs` mặc định tắt (kể cả khi truyền sự kiện), bật, thiếu tab `hoc_sinh`; `.gs` khớp `noi_dung()`. Ca ghim `COT_RAW` ở `test_skill_xu_li_raw.py` giữ xanh.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 180 tệp test.
- Không đụng kiosk, hợp đồng cột CSV, `match_results`.

## 2026-11-03 — T4-K3 (ngoài sổ, Truong duyệt 03/11/2026): skill `xu-li-raw-forms` đọc thư mục nhiều phần CSV

Thay đổi số 3 ở mục 11.2 của `docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md`: đợt trên 1.000 phiếu được xuất thành nhiều phần `<tên>_p01.csv`, `_p02.csv`... nên skill phải ghép được.

- **`xu_li_raw.py`:** hàm mới `doc_raw(duong)`. Tệp đơn: y như `doc_bang` cũ. Thư mục: ghép các phần theo số phần (thứ tự tự nhiên), từ chối bằng `LoiDauVao` (không ghi tệp nào) khi không có phần, nhiều bộ xuất lẫn nhau, thiếu phần / số phần trùng, tiêu đề lệch, hoặc một `phieu_so` ở hai phần. `chay` gọi `doc_raw`; `--raw` nhận thư mục. `COT_RAW` không đổi.
- **`SKILL.md`:** ghi cách dùng thư mục và các trường hợp bị từ chối.
- **Test mới:** `tests/test_skill_xu_li_raw_nhieu_phan.py` (8 ca): thư mục 3 phần cho Sổ và báo cáo giống hệt một tệp; p2 trước p10; tệp đơn như cũ; năm ca từ chối. `tests/test_skill_xu_li_raw.py` (8 ca) giữ xanh.
- `docs/ke_hoach/CLAUDE_CHI_TIET.md`: 179 tệp test (canh bởi `tests/test_a13_12_tai_lieu.py`).
- Không đụng kiosk, hợp đồng cột CSV, `match_results`.

## 2026-11-03 — T1a, T1b (nhánh `claude/epic-knuth-801pkw`; Truong duyệt, bỏ qua sổ đăng ký)

- **T1a — sổ mẫu chính có cột Lớp:** `mau_csv/SO_NHAP_CLB.xlsx` là sổ TRỐNG (không có học sinh nào để gán lớp). Nó giờ có cột **Lớp** ngay sau **Họ tên**, giống hệt sổ phần mềm tạo (`tao_so_nhap_mau`, A14). `mau_csv/tao_so_nhap.py::tao_mau_trong` gọi `ghi_so_nhap(..., co_lop=True)`; tệp sinh lại bằng kịch bản, không sửa tay. `HUONG_DAN_SO_NHAP.md` ghi đây là sổ mẫu chính. Hai sổ ví dụ `vi_du_*` GIỮ NGUYÊN (khớp từng dòng với bộ ba CSV, mà CSV ví dụ không có lớp).
- **T1b — nhãn trùng cũ không chặn lưu:** `cau_hinh_ws.ghi_cau_hinh` chỉ ném `NhanTrung` khi cấu hình mới có cặp danh từ trùng nhãn mà cấu hình ĐANG LƯU chưa có. Workspace cũ đã trùng đổi tên / đổi luật được; thêm cặp trùng thứ hai vẫn bị chặn; sửa hết trùng thì qua. `chuan_hoa()` (kiểm trước khi dựng workspace) và cảnh báo nhập `so_nhap_canh_bao_nhan_trung` giữ nguyên.
- **Test:** mới `tests/test_t1b_nhan_trung_cu.py` (6); sửa `tests/test_so_nhap.py::test_mau_trong_doc_duoc_va_dung_bo_cuc` (tiêu đề có Lớp).

### T2 sửa vòng 3

- Ảnh chụp `tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json` (bốn ca `test_mac_dinh_truong_hoc_cho_ra_dung_so_nhu_truoc`): sau vòng 2 (G3) chữ sheet "Hướng dẫn" đổi theo quy tắc chữ của chủ dự án. Đã so từng khoá: CHỈ năm ô `Hướng dẫn/o/A1, A16, A18, A23, A33` khác (hai ảnh `co_du_lieu` và `trong`, cả bốn cấu hình); mọi khoá khác trùng. Chỉ thay hai cây con `Hướng dẫn` bằng lập trình, giữ định dạng tệp; ghi chú ở `tests/test_ws_so_nhap.py`. Đã tìm ảnh chụp khác chứa chữ hướng dẫn: không còn tệp nào.

### T2 sửa vòng 2

- **G1 (T2, tràn ngang):** `.main { min-width: 0 }` (cột `1fr` của lưới không còn nở theo bảng rộng, nên bảng chỉ cuộn ngang trong `.scroll-x`, trang thì không); ô CLB `min-width` 7em. Test mới `test_khong_tran_ngang_trang_voi_ten_clb_rat_dai` (độ rộng 600, 1024, 1280; tên CLB 60 ký tự; ba cách xem; `scrollWidth <= innerWidth`). Đã thử gỡ dòng sửa: test đỏ ở 600 và 1024.
- **G2 (tài liệu):** `HUONG_DAN_SU_DUNG.md` bảng "xuất hồ sơ học sinh" đổi số thẻ (04, 03, 05) và đoạn lớp mô tả đúng: lọc và sắp theo lớp ở thẻ 03, cột Lớp và cách xem Theo lớp ở thẻ 02.
- **G3 (chữ sheet Hướng dẫn):** bỏ dấu gạch dài và xưng "em" trong các dòng hướng dẫn của `so_nhap.py` (cả bản hằng số lẫn bản dựng theo cấu hình); sinh lại `mau_csv/SO_NHAP_CLB.xlsx`. Test kiểm mọi dòng hướng dẫn của sổ mẫu: không "—", không từ "em/tôi/tớ". Các sheet khác không đổi. Sinh lại sáu sổ `du_lieu_test/SO_NHAP_DQT_*.xlsx` bằng `sinh_du_lieu_diem_quyet_tam.py` (test `test_sinh_lai_bang_script_ra_dung_noi_dung_o` đòi tệp khớp script).

### T1/T2 sửa vòng 1 (tester: 2 lớn, 5 vừa, 3 nhỏ)

- **F1 (T1b):** `cau_hinh_ws._cap_trung_day_du` liệt kê MỌI cặp danh từ cùng nhãn kèm ngôn ngữ (ba danh từ cùng nhãn cho ba cặp; `cac_cap_nhan_trung` giữ nguyên cho cảnh báo nhập). `ghi_cau_hinh` chỉ từ chối khi có cặp (ngôn ngữ, a, b) mới so với mốc; báo cặp mới đầu tiên theo thứ tự `DANH_TU`, vi trước en.
- **F2 (T1b):** `ghi_cau_hinh(..., nhan_goc=None)` và `workspace.tao(..., nhan_goc=None)`; `nhan_ban` kiểm không nghiêm phần nhãn trùng và lấy nhãn nguồn làm mốc, cả hai chế độ `kem_du_lieu`: bản sao giữ nhãn trùng cũ, trùng mới vẫn bị chặn.
- **F3 (T1b):** `luu_mau` kiểm nghiêm: workspace cũ trùng nhãn lưu mẫu thì lỗi `nhan_trung_danh_tu`, không ghi tệp.
- **F4 (T1a):** sổ mẫu tĩnh dựng bằng cấu hình mặc định như phần mềm (`chuan_hoa({})`), nên MỌI ô của MỌI sheet (cả Hướng dẫn) trùng sổ phần mềm tạo; `huong_dan(co_lop=True)` thêm một dòng nói cột Lớp tuỳ chọn. README, TAI_LIEU_DU_LIEU, BAN_GIAO ghi đây là sổ mẫu chính có cột Lớp.
- **F5:** số thẻ cũ sửa lại sau khi đánh số lại (`i18n.js`, `index.html`, `i18n_errors.py` và `i18n_loi.js` sinh lại, README, HUONG_DAN_CSV, HUONG_DAN_SO_NHAP, chú thích đầu các tệp js, `api_bao_cao.py`).
- **F6:** bỏ khoá mồ côi `results_title`, `results_desc`, `tkb_title`, `tkb_desc`, `tkb_so_clb` (`tests/test_ws_nhan.py` đổi mẫu `tkb_desc` thành `kq_desc`).
- **F7:** số ít / số nhiều ở bản tiếng Anh: `kq_dem_ma_nhieu`, `theolop_dem_nhieu` (số ít chỉ khi n = 1).
- **F8 (T2):** *Theo CLB*: tầng 2 "Theo ngày trong tuần" chia ô chọn CLB thành nhóm theo buổi (thứ tự ngày), "Theo mã học sinh" là danh sách phẳng theo vần; bảng thành viên luôn theo mã. Cột STT, mã, họ tên, lớp không xuống dòng. Ô tìm ngắn hơn (`kq_tim_ph`). Nhớ cả lớp và CLB đã chọn trong khoá `rbda_ket_qua_xem_v1` (giá trị không còn tồn tại thì lùi về mục đầu).
- **Test cũ sửa có chủ đích:** `tests/test_ws_nhan.py` (ảnh chụp chuỗi mặc định: bỏ năm khoá mồ côi khỏi phép so, cho phép đúng hai chuỗi đổi số thẻ; mẫu 20 chuỗi dùng `fill_hint`); `docs/ke_hoach/CLAUDE_CHI_TIET.md` (178 tệp, 3.299 ca).
- **Test:** `tests/test_t1b_nhan_trung_cu.py` (thêm F1, F2, F3 và so mọi sheet sổ mẫu), `tests/test_giao_dien_t2_ket_qua.py` (thêm nhóm theo buổi, nhớ lớp / CLB, số ít số nhiều); `test_giao_dien_a14_lop.py` (khoá i18n 25 thành 26, tuỳ chọn CLB có nhóm).

### T2 — gộp thẻ 02, 06, 07 thành "Kết quả" và "Dữ liệu khác" (bảy thẻ thành sáu)

- **Thanh bên:** 01 Vận hành sắp xếp, 02 Kết quả (`results`), 03 Dữ liệu khác (`others`), 04 Nhập tại chỗ, 05 Quản lý CLB & dự trữ, 06 Nhập điểm. Bỏ thẻ `members` và `theolop`; `TAB_LOADERS` (`js/01_khung.js`), khởi động (`initKetQuaHandlers`) và vẽ lại khi đổi ngôn ngữ (`reapplyDynamicTextForLangChange`) theo tên mới.
- **02 Kết quả** (`js/09_the_xem.js`, `view-results`, chỉ đọc, không điểm, không số bốc thăm): tầng 1 *Theo lớp | Theo CLB | Theo mã học sinh*; tầng 2 (cách sắp) *Theo ngày trong tuần | Theo mã học sinh | Theo lớp*, mục *Theo lớp* chỉ hiện khi tầng 1 là *Theo mã học sinh* (lựa chọn lưu ở tầng 2 mà không hợp lệ thì lùi về *Theo ngày trong tuần*, không ghi đè). Sắp theo ngày = vị trí buổi sớm nhất em có CLB (thứ tự `ds_buoi` do backend sắp theo ngày), sau đó theo mã; sắp theo mã là sắp tự nhiên (HS9 trước HS10); sắp theo lớp theo thứ tự `list_classes` (tự nhiên, lớp trống cuối). Nhớ hai tầng ở `localStorage` khoá `rbda_ket_qua_xem_v1` (try/catch). Giữ lớp và CLB đã chọn khi đổi cách xem hay rời thẻ. Dùng lại `get_thoi_khoa_bieu`, `get_danh_sach_clb`, `get_club_fill_stats`, `list_classes`, `get_trang_thai_ket_qua`; không thêm backend. Trạng thái rỗng: chưa chạy xếp, chưa có lớp nào, tìm không thấy.
- **03 Dữ liệu khác** (`view-others`, hàm vẫn tên `loadResultsTab`): mọi mục còn lại của thẻ 02 cũ, giữ nguyên thu gọn. Bảng thời khoá biểu từng học sinh (`tkbPanel`, `loadThoiKhoaBieu`) chuyển sang 02 Kết quả, không giữ hai bản.
- **Chữ:** khoá i18n mới `nav_others`, `others_*`, `kq_*` (vi và en); bỏ `nav_members`, `nav_theo_lop`, `members_title|desc|chon|chua_chon`, `theolop_title|desc|chon|chua_chon`. `style.css`: nút chọn hai tầng và `.main:has(#view-results.is-active)` để thẻ không co lại ở *Theo CLB*.
- **Test mới:** `tests/test_giao_dien_t2_ket_qua.py` (11 ca Chromium: đổi tầng 1, tầng 2 và mục *Theo lớp*, sắp theo mã / lớp / ngày, nhớ sau khi mở lại, kho lưu trữ hỏng, giữ lựa chọn, trạng thái rỗng, đổi ngôn ngữ, không điểm và không số bốc thăm). **Test cũ sửa có chủ đích** (thay đổi đã duyệt): các tệp `tests/test_giao_dien_*` bấm `data-tab="results"` cho nội dung cũ nay bấm `others` và `#view-others`; `test_giao_dien_a14_lop.py` (hai thẻ xem cũ thành các ca của thẻ Kết quả, fixture `mo` thêm tham số `them` và ngữ cảnh trình duyệt dựng tường minh, số khoá i18n 35 thành 25); `test_giao_dien_thu_gon_ket_qua.py` (`tkbPanel` bỏ, chín mục thành tám, mục thay thế `doPhuPanel`); `test_giao_dien_a13_12_tkb.py` (ô tìm nay ở *Theo mã học sinh*).

## 2026-11-02 — A14 — phần A (nền, nhập, API): lớp của học sinh

**Đã merge vào main qua PR #6 (b044c4c, 03/11/2026).**

Mỗi học sinh có thể có "lớp" (vd 10H1A) CHỈ để hiển thị, sắp, lọc, xuất cho giáo viên chủ nhiệm. Thuật toán phân bổ KHÔNG đọc lớp. Phần B (xuất + giao diện) ở nhánh `claude/a14-giao-dien`.

**NGOẠI LỆ BẤT BIẾN 7 (Truong duyệt 02/11/2026).** Hợp đồng cột CSV đổi có chủ đích: cột TUỲ CHỌN `class_id` ngay sau `reserve_group` trong CSV nguyện vọng và CSV chọn thi; Sổ nhập thêm cột "Lớp" (nhãn `cohort`) ngay sau "Họ tên". Không có cột / ô trống thì giữ lớp cũ; lần ghi sau cùng thắng. Không lớp nào thì `thanh_csv` và Sổ xuất ra giống từng byte như cũ.

- **Schema:** `students.class_id TEXT` (NULL = chưa có); `di_tru_schema` bước 7 `ALTER TABLE` có sao lưu `.bak-` khi bảng đã có dữ liệu, chạy lặp an toàn.
- **`chuan_hoa_lop(raw)`** (`rbda_priority_pipeline.py`): NFC, bỏ ký tự vô hình (Cf) và điều khiển (Cc), cắt hai đầu, gộp khoảng trắng liên tiếp, IN HOA; rỗng → None. Không ép mẫu. `LOP_TOI_DA = 50`.
- **Từ vựng:** danh từ thứ sáu `cohort` (vi "Lớp", en "Class") ở `nhan_ws.py`; cấu hình cũ thiếu `cohort` lấy mặc định. Kỹ năng `tao-workspace-tu-raw` nhận `labels.cohort` tuỳ chọn. Bản JS (`i18n.js`, `js/075_workspace.js`) thuộc phần B.
- **Nhập:** `import_preferences_csv`, `import_test_selection_csv` (dài: giá trị không trống đầu tiên); `so_nhap` đọc theo tên cột (Lớp, Mã lớp, Lop, Class, Class ID, class_id, nhãn `cohort`), `doc_so_nhap` → `class_id` (None = sổ không có cột; "" = ô trống), `ghi_so_nhap(co_lop=)`; `tao_so_nhap_mau` luôn có cột Lớp; `export_du_lieu_dau_vao` có cột Lớp khi có em có lớp (hai chỗ trong `api_xuat.py`). Cảnh báo `so_nhap_canh_bao_thieu_lop` {n} chỉ khi Sổ có cột mà n ô trống.
- **API:** `list_students_admin(sort_by, class_id)`, `set_student_class`, `list_classes`, `create_student_if_missing(class_id)`, `submit_test_selection(class_id)` và `submit_preferences(class_id)` (đối số vị trí thứ 3; lớp phải nằm trong `list_classes`, sai → `lop_khong_co_trong_danh_sach`), `get_match_results(class_id, sort_by)`. Mã lỗi mới: `error_saving_student_class`, `error_reading_classes`, `lop_khong_co_trong_danh_sach`, `so_nhap_canh_bao_thieu_lop`.
- **Test mới:** `tests/test_a14_lop_backend.py` (13), `tests/test_a14_lop_nhap.py` (18), `tests/test_a14_tu_vung_cohort.py` (22), `tests/test_a14_sua_sau_soat.py` (26, vòng sửa bên dưới) — gồm các bất biến: `match_results` giống hệt khi có / không lớp; `class_id` không có trong lõi phân bổ ngoài schema / `di_tru_schema` / `chuan_hoa_lop`; đổi lớp không làm `ket_qua_cu`; `run_history` không đụng.
- **Vòng sửa sau soát chéo (Truong duyệt 02/11/2026), commit riêng từng mục:**
  - **A1 — nhãn hai danh từ trùng nhau:** `cau_hinh_ws` từ chối (ném `NhanTrung`, mã `nhan_trung_danh_tu` {a, b, nhan}) cấu hình có hai danh từ cùng nhãn sau strip + casefold, vi và en xét riêng, mọi cặp trong sáu danh từ. Cấu hình ĐÃ LƯU mà trùng vẫn đọc được (`doc_cau_hinh` không kiểm trùng); `so_nhap._khop_cot` gán cột trùng tên theo thứ tự Sổ ghi (Lớp trước Nhóm; chỉ một cột trùng thì là Nhóm như cũ) nên khứ hồi không đảo; nạp Sổ báo `so_nhap_canh_bao_nhan_trung`. Lưu ý: ghi một cấu hình trùng đã lưu từ trước (đổi tên workspace…) cũng bị từ chối cho tới khi đặt lại nhãn.
  - **A2 — `_khoa_lop_tu_nhien`:** chỉ chữ số ASCII 0-9 là số (lớp "10²" không còn làm hỏng `list_classes` / sắp theo lớp). Giữ tên và chữ ký.
  - **A3 — `chuan_hoa_lop`:** NFC, bỏ Cf (U+200B, U+FEFF…) trước khi cắt / gộp / IN HOA.
  - **A4 — giới hạn đầu vào:** `set_student_class`, `submit_*`, `create_student_if_missing` từ chối kiểu không phải str / int / float (`lop_sai_kieu`), bỏ ký tự điều khiển (Cc), > 50 ký tự sau chuẩn hoá → `lop_qua_dai` {toi_da: 50}. Nhập CSV / Sổ không chặn: cắt còn 50 và cảnh báo `canh_bao_lop_bi_cat` {n}.
  - **A5 — `di_tru_schema`:** sao lưu chụp MỘT lần ngay trước việc di trú đầu tiên cần sửa schema (trước chỉ ở bước 7, sau các bước 1 và 6) và chỉ khi đã có dữ liệu; lỗi ghi tệp sao lưu không làm hỏng việc mở workspace.
  - **A6 — tài liệu:** mục này, `CLAUDE_CHI_TIET.md`, tiêu đề `SO_DANG_KY_33_MUC.md`, `TIEN_DO.md`, tệp bàn giao.
  - **C1 — ghi lại cấu hình đã lưu có nhãn trùng (Truong duyệt 03/11/2026):** `ghi_cau_hinh` / `chuan_hoa` / `workspace.tao` nhận `cho_phep_trung_nhu`; cặp nhãn trùng Y HỆT cấu hình đang lưu (hoặc nguồn nhân bản) được để qua, nên đổi tên workspace, cập nhật phần khác và nhân bản (có / không kèm dữ liệu) một workspace cũ trùng nhãn đều chạy, nhãn giữ nguyên. Cặp trùng MỚI hoặc bị đổi vẫn bị `nhan_trung_danh_tu`. Test: `tests/test_a14_sua_sau_soat.py` (6 ca `test_c1_*`).
  - **C2 — Sổ / CSV mẫu tĩnh có cột Lớp MÔ PHỎNG (Truong duyệt 03/11/2026: Sổ mẫu tĩnh có cột Lớp mô phỏng):** script mới `du_lieu_test/them_lop_vao_mau.py` (seed cố định 112026201–204, lớp `10A1` … `12A3`, chạy lại ra đúng cùng byte) chèn cột `class_id` NGAY SAU `reserve_group` trong CSV và dựng lại các Sổ bằng `mau_csv/tao_so_nhap.py` (cột "Lớp" ngay sau "Họ tên"). KHÔNG đụng `bo_sach` và dữ liệu của số liệu đã công bố; `SO_NHAP_CO_LOI_CO_Y.xlsx` giữ bố cục cũ (`LOI_CO_Y` trỏ vào ô cụ thể). `match_results` của mọi bộ giống hệt trước (băm chốt trước khi thêm lớp, có test). Nạp các Sổ mới: không có `so_nhap_canh_bao_thieu_lop`. Tệp đổi băm (chỉ băm TỆP, kết quả xếp không đổi):
    - `mau_csv/SO_NHAP_CLB.xlsx` — sổ mẫu trống có thêm cột Lớp.
    - `mau_csv/vi_du_day_du/SO_NHAP_CLB_vi_du.xlsx`, `mau_csv/vi_du_ca_tuan/SO_NHAP_CLB_vi_du.xlsx`, `du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx` — dựng lại từ CSV có `class_id` (24 / 60 / 10 em, chỉ thêm lớp).
    - `mau_csv/vi_du_day_du/{02_chon_CLB_muon_thi,03_xep_hang_nguyen_vong}.csv`, `mau_csv/vi_du_ca_tuan/{02,03}_….csv`, `mau_csv/{07_chon_club_thi_nhieu_buoi,08_nguyen_vong_nhieu_buoi}.csv`, `du_lieu_test/vi_du_huong_dan/VIDU_{02,03}_….csv` và `.xlsx` — thêm cột `class_id`.
    - Tài liệu khớp: `TAI_LIEU_DU_LIEU.md` (header và cỡ tệp), `mau_csv/HUONG_DAN_SO_NHAP.md`, `mau_csv/HUONG_DAN_CSV.md`, hai `GIAI_THICH.md`. Test mới: `tests/test_a14_mau_co_lop.py` (30 ca). Test cũ sửa có chủ đích: `tests/test_so_nhap.py::test_mau_trong_doc_duoc_va_dung_bo_cuc` (bố cục sổ mẫu), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (173 tệp, 3.253 ca của nhánh A). Việc để sau: skill `sinh-du-lieu-clb` chưa có tuỳ chọn lớp mô phỏng.
- **Test cũ sửa có chủ đích:** `tests/test_ws_nhan.py` và `tests/test_wharton_ma_loi.py` (danh sách danh từ thành sáu); `tests/test_ws_nhan.py` thêm đúng 4 mã lỗi mới vào `MA_MOI_SAU_ANH_CHUP` (theo tiền lệ A13).
- **Test cũ khác sửa có chủ đích (thay đổi đã duyệt: Sổ mẫu có cột Lớp, `get_student_entry_state` thêm `class_id`, thêm 3 tệp test):** `tests/test_ws_so_nhap.py` (3 ca), `tests/test_ws_luat.py`, `tests/test_ws_sua_loi_3.py` (dòng học sinh thêm một ô cho cột Lớp; vị trí NV1 dịch một cột), `tests/test_wharton_kiosk.py` (thêm khoá `class_id`), `docs/ke_hoach/CLAUDE_CHI_TIET.md` (168 → 171 tệp test).

## 2026-11-02 — A14 — phần B (xuất theo lớp và giao diện lớp)

Phần B của mục A14 "Lớp của học sinh" (phần A: cột `students.class_id`, `chuan_hoa_lop`, danh từ `cohort`, các API lớp). Lớp chỉ để hiển thị, lọc, sắp và xuất cho giáo viên chủ nhiệm; thuật toán, `match_results`, `run_history` không đổi.

- **`api_xuat.py`:** trang mới **"Theo lớp"** trong Sổ kết quả, LUÔN có, đứng sau "Theo CLB" (sổ từ 6 thành 7 trang; 8 khi bật điểm quyết tâm). Mỗi lớp một khối (thứ tự tự nhiên: 10A2 trước 10A10), ngắt trang giữa các lớp, khối cuối "Chưa có lớp" nếu có em trống lớp. Không có điểm thi, điểm quyết tâm, số bốc thăm hay diện trúng tuyển; nhiều buổi thì mỗi buổi một cột; em chưa có chỗ tô đỏ. Trang Hướng dẫn thêm một dòng nói trang này không có điểm, gửi giáo viên chủ nhiệm được.
- **`export_theo_lop(output_path="")`:** API mới, ra MỘT THƯ MỤC, mỗi lớp một `.xlsx` một trang, thêm `_chua_co_lop.xlsx` nếu cần; tên tệp qua `_ten_file_an_toan` + `_ten_chua_dung`; đường dẫn theo `_duong_xuat` (đường tuyệt đối đã có thì thành `x (2)`, không ghi đè); chạy dưới `_khoa_xuat`; chưa có kết quả → `xuat_chua_co_ket_qua`, không tạo gì. Trả {thu_muc, n_tep}.
- **Cột "Lớp" ngay sau "Họ tên"** (luôn có, kể cả trống): trang Danh sách (một buổi và bảng thời khoá biểu nhiều buổi, CHỈ bản Excel qua `du["tkb_xlsx"]`), trang "Theo CLB", CSV tổng, CSV `_theo_club`. KHÔNG đổi: CSV thời khoá biểu, CSV từng buổi, CSV số bốc thăm, `export_hoc_sinh_csv`, báo cáo Word.
- **Giao diện:** thẻ Quản lý/Học sinh có cột Lớp, ô lọc (Tất cả / từng lớp / Chưa có lớp), ô sắp theo lớp, ô sửa lớp từng em (`set_student_class`). Thẻ Kết quả có cột Lớp, ô lọc, ô sắp, nút **Xuất theo lớp** (khoá khi chưa có kết quả). Kiosk (thẻ 03) có danh sách thả xuống cố định từ `list_classes`: có lớp thì BẮT BUỘC chọn trước khi Lưu (cả tạo em mới), không có lớp nào thì ẩn. Workspace có ô nhãn thứ 6 cho `cohort`. `i18n.js` thêm `cohort` vào bản JS của danh từ (`NHAN_MAC_DINH`, `CHO_GIU_DANH_TU`); chữ mới ở `i18n.js` (vi + en), `js/075_workspace.js` thêm `cohort` vào `WS_DANH_TU`.
- **Hai thẻ XEM chỉ đọc ở thanh bên (yêu cầu thêm của Truong, thuộc A14):** thẻ **06 "Thành viên {CLB}"** (chọn CLB; nhiều buổi ghi kèm buổi, sắp theo thứ tự ngày rồi tên; bảng STT | Mã | Họ tên | Lớp, dòng đầu "Đã xếp x/y chỗ") và thẻ **07 "Theo {lớp}"** (chọn lớp, gồm "Chưa có lớp"; STT | Mã | Họ tên rồi mỗi buổi một cột theo thứ tự NGÀY, ô trống ghi "—", em chưa có CLB nào tô đỏ; một buổi thì một cột CLB). Chưa chạy xếp: cả hai hiện "chưa có kết quả"; chưa có lớp nào: thẻ 07 hiện dòng nhắc. Chỉ kết quả xếp, không điểm, điểm quyết tâm, số bốc thăm hay diện trúng tuyển. Mã: `js/09_the_xem.js` (mới), `index.html`, `js/01_khung.js` (`TAB_LOADERS`), `js/07_ngon_ngu.js`, `js/08_khoi_dong.js`, `style.css`, `i18n.js` (36 khoá vi + en). Backend `api_bao_cao.py`: `get_thoi_khoa_bieu(search="", class_id=None)` (None = hành vi cũ; `""` = chưa có lớp; mỗi em có `class_id`) và `get_danh_sach_clb` có `class_id` mỗi thành viên.
- **Đổi ngôn ngữ vẽ lại chữ trong các ô thả xuống lớp ở thẻ 03** (dòng "— Chọn lớp —" của kiosk và của ô tạo em mới).
- **`export_theo_lop` lỗi giữa chừng thì xoá thư mục dở do chính lần xuất đó tạo** (không bao giờ thư mục có sẵn; trả `error_exporting_excel`).
- **DUYỆT NGOẠI LỆ TRÙNG KHÍT TỆP XUẤT (Truong duyệt 02/11/2026):** trang **"Theo lớp"** và cột **"Lớp"** LUÔN có trong Sổ kết quả và CSV kết quả (tệp tổng, `_theo_club`) kể cả khi không em nào có lớp (cột trống, trang chỉ có khối "Chưa có lớp"). Sổ kết quả từ 6 thành 7 trang. KHÔNG đổi: `match_results`, CSV thời khoá biểu, CSV từng buổi, CSV số bốc thăm, tệp tổng hợp, `export_hoc_sinh_csv`, báo cáo Word.
- **Vòng sửa sau soát chéo (Truong duyệt, mỗi mục một commit "A14 sửa Bx"):**
  - **B1** `export_theo_lop` trả thêm `ket_qua_cu` như `export_ket_qua`; mỗi tệp lớp và trang "Theo lớp" có dòng đỏ "CHÚ Ý: … có thể đã cũ" khi dữ liệu đã sửa sau lần chạy; giao diện hiện cảnh báo `xuat_kq_cu` như các nút xuất khác.
  - **B2** Kiosk: ô lớp tính là "chưa lưu" (dấu • Chưa lưu cạnh ô, bấm sang em khác / tạo em mới phải bấm hai lần, chặn "Xuất CSV em này"); đổi lại đúng giá trị đã lưu thì hết dấu.
  - **B3** Tên tệp lớp dài (300 ký tự) từng làm hỏng cả lần xuất (`File name too long`): cắt còn ~100 ký tự và ≤200 byte UTF-8 trước `_ten_chua_dung`, vẫn khử trùng; tên thật còn đủ trong tiêu đề khối.
  - **B4** Bỏ `api_xuat._khoa_lop_xuat`; dùng `_khoa_lop_tu_nhien` của phần A. Test chặn mọi hàm riêng trùng tên giữa các mixin; test lớp "10²" (xanh khi có bản sửa `isdecimal` của A).
  - **B5** Dòng nhắc thẻ 07 "chưa có lớp nào" gọi đúng tên thẻ 04 và mục Học sinh như thanh bên bằng chỗ giữ (vi + en), theo nhãn workspace.
  - **B6** `tests/_trinh_duyet.py` tìm Chromium ở `chromium-N/chrome-linux64/chrome` và tệp `chromium` chạy được (trước chỉ `chrome-linux/chrome`, nên test giao diện bị bỏ qua im lặng khi thiếu `RBDA_TEST_CHROMIUM`); hành vi không đổi khi đã đặt biến. Test mới `tests/test_trinh_duyet_tim.py` (7 ca).
  - **B9 (CI của PR #6)** `tests/test_a14_sua_sau_soat.py::test_a5_sao_luu_dung_mot_lan_truoc_buoc_di_tru_dau_tien` dựng CSDL cũ bằng `CREATE TABLE` tường minh, không phụ thuộc phiên bản SQLite: trước đó bỏ liên tiếp hai cột bằng `ALTER TABLE ... DROP COLUMN` trên bảng có chú thích `--` làm SQLite của CI (Linux và Windows, Python 3.11) báo "incomplete input". Mọi assert cũ giữ nguyên; thêm một assert bản sao lưu có dữ liệu (em S1), nên tệp sao lưu rỗng cũng làm test đỏ.
  - **B8 (kiểm cuối của điều phối viên)** Luật văn phong (`tests/test_van_phong_tu_nhien.py`): sửa CHỮ trong `i18n.js`, không sửa test. Bỏ gạch ngang nối câu (dùng dấu chấm, dấu phẩy); lựa chọn rỗng viết "Chọn lớp…" như "Chọn học sinh…" đã có; cột "STT" thành "Thứ tự" (HOA nhấn mạnh bị cấm); ô trống thẻ 07 ghi "—" trực tiếp trong JS như các bảng cũ (bỏ khoá `theolop_o_trong`). `tests/test_diem_chuan.py::test_tep_xuat_tat_tinh_nang_giong_het_truoc` so tên bảy trang tường minh (có "Theo lớp") thay cho `== 6`, giữ ý "Điểm chuẩn" không có khi tắt.
  - **B7** Tài liệu: mục này, `js/_danh_sach.txt` thêm `09_the_xem`, bản ghi bàn giao.
- **Test mới (số ca thật):** `tests/test_a14_lop_xuat.py` (23 ca), `tests/test_a14_the_xem.py` (8 ca, backend + thứ tự tệp JS), `tests/test_giao_dien_a14_lop.py` (24 ca, Chromium), `tests/test_trinh_duyet_tim.py` (7 ca).
- **Test cũ sửa có chủ đích (trang mới luôn có):** `tests/test_so_excel_de_dung.py` (`CAC_TRANG`), `tests/test_ws_nhan.py` (3 ca danh sách tên trang), `tests/test_ws_so_nhap_giao_dien.py` (tiêu đề Sổ mẫu có cột Lớp sau Họ tên; thay đổi đã duyệt của phần A, test trình duyệt nên A chưa chạy), `tests/test_giao_dien_upload.py` (sửa ô theo vị trí D3/E4 thành E3/F4 vì Sổ ví dụ tĩnh có cột Lớp sau Họ tên: NV1 sang cột E, điểm sang F; thay đổi đã duyệt của phần A, mục C2).

## 2026-11-01 — A13.13 (phần tiếp theo) CSDL demo thể hiện điểm quyết tâm + vá đường dẫn cứng

- **`du_lieu_test/tao_db_demo.py`:** mặc định dựng CSDL demo với Wharton BẬT (không ghi `wharton: false`), nạp `SO_NHAP_DQT_120HS_HOP_LE.xlsx` qua `import_so_nhap` (chọn bản 120HS vì giữ nguyên nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`, chỉ thêm điểm quyết tâm MÔ PHỎNG; nhỏ, demo nhanh). Vẫn dừng trước khi chạy phân bổ. Cờ mới `--tat-wharton` dựng y như trước (TEST_01..03, `wharton: false`); cờ `--ra` chọn tệp đầu ra (mặc định giữ chỗ cũ). Đã so với bản dựng ở `cee2940`: 14/15 bảng trùng khít từng dòng, chỉ `workspace_settings` khác (có khoá `wharton=false`) — đúng dự kiến.
- **`du_lieu_test/app_DEMO_da_cham_diem.db`:** commit bản dựng mới (Wharton bật; 3 cảnh báo mức thường `health_oversubscribed_buoi`, 0 nghiêm trọng).
- **Tài liệu đổi lệnh sang `--tat-wharton` (để số cũ tái lập):** `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`, `poster/chup_giao_dien.py` (ảnh poster đứng cạnh số đã công bố nên dựng bản cũ vào thư mục tạm). Lời hướng dẫn cập nhật: `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md`, `poster/DU_LIEU_POSTER.md`, `BAN_GIAO.md`. Không sửa con số nào.
- **`du_lieu_test/do_do_dai_nguyen_vong.py`:** bỏ đường dẫn cứng `/home/user/truong/rbda-kiosk`, tính từ `__file__`; ghi bước chuẩn bị dữ liệu vào docstring (`bo_sach/` có sẵn trong kho, sinh lại bằng `bo_sach/tao_bo_sach.py`). Đầu ra trùng khít bản `cee2940` (đã vá tạm đường dẫn trong worktree).
- **Test:** mới `tests/test_db_demo_wharton.py` (6 ca: bật/tắt, chạy trên bản sao, `luat_xep.wharton`, trùng khít `match_results` seed 42, không còn `/home/user/truong`); `tests/test_a13_13_kiem_nhan.py` thêm `tao_db_demo.py` vào `NGOAI_LE_F1`; `tests/test_rang_buoc_csdl.py` tắt Wharton tường minh trong `_nap_nhieu_buoi` (3 test này đỏ sẵn từ nhánh cha vì dữ liệu CSV không có điểm quyết tâm).

## 2026-11-01 — A13.13 Điểm quyết tâm (Wharton) BẬT mặc định cho workspace trường học

**NGOẠI LỆ BẤT BIẾN 1 (đã duyệt).** Bất biến 1 ("cấu hình mặc định cho kết quả trùng khít với trước khi sửa") bị phá có chủ đích, theo quyết định rõ ràng của Truong. Các bất biến 2–8 vẫn giữ. Tắt RÕ RÀNG (`wharton: false`) thì kết quả, dấu vân tay và `run_history.luat_xep` trùng khít bản trước (đã chạy lại `do_anh_huong_seed.py` và `bao_cao_phan_bo.py`, so với bản gốc: đầu ra giống hệt).

- **Mã:** `cau_hinh_ws.py` — `MAC_DINH_TRUONG_HOC["rules"]["wharton"] = True`. Tổ hợp không bật được (`priority = "tier"` hoặc `score_scope = "per_person"`) mà người dùng KHÔNG ghi rõ `wharton` thì tự tắt (`_chuan_hoa`, và `tron_len` khi cập nhật); ghi rõ `wharton: true` với tổ hợp sai vẫn báo lỗi như cũ.
- **Giữ nguyên có chủ ý:** `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"] = False`. Đây là mặc định ở tầng thuật toán thuần (gọi `run_full_pipeline`, `luat_xep_de_ghi`… không kèm cấu hình workspace) nên số liệu cũ vẫn tái lập; mặc định BẬT chỉ nằm ở cấu hình workspace.
- **Thông báo:** `wharton_ho_so_chua_hop_le` (`i18n_errors.py` → `tao_i18n_js.py`) nay chỉ cách khắc phục: điền đủ điểm quyết tâm, hoặc tắt "Dùng điểm quyết tâm" trong cấu hình workspace.
- **Tài liệu:** `HUONG_DAN_SU_DUNG.md` (mục "Bật ở đâu"), `mau_csv/HUONG_DAN_SO_NHAP.md`, hai chú thích trong `api_nhap.py`, `rbda_priority_pipeline.py`.
- **Công cụ:** `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (kiểm `trung_khit`) tắt Wharton rõ ràng cho cả hai bản so sánh; không thì kiểm này lặng lẽ so hai kết quả "bị chặn" với nhau. 15 script trong `du_lieu_test/` (và `stress/_chung.py`, `stress/s8_bao_mat.py`, `bo_thu_workspace/tao_bo_workspace.py`) truyền `wharton: false` tường minh để tái lập số liệu cũ (quy tắc 4).

**Ảnh hưởng tới workspace cũ**
- Workspace đã lưu từ phiên bản có khoá `wharton` (A13.2 trở đi) ghi rõ `wharton: false` nên KHÔNG đổi.
- Cấu hình lưu TRƯỚC khi có khoá `wharton`, CSDL chưa có hàng `workspace_settings` (kể cả `app.db` cũ được di trú), và mẫu dựng sẵn "Trường học" nay ĐỌC THÀNH BẬT. Không viết di trú (đúng yêu cầu gốc).
- Hệ quả: dữ liệu mà một quỹ có từ hai CLB trở lên và chưa có điểm quyết tâm bị chặn khi chạy (`wharton_ho_so_chua_hop_le` + `wharton_chua_dung_het`); quỹ chỉ có một CLB được tự điền 100 trong bộ nhớ (quyết định "cách A"). Muốn chạy như cũ: tắt "Dùng điểm quyết tâm" trong cấu hình workspace. Không nới luật kiểm Wharton.
- `run_history.luat_xep` và dấu vân tay của workspace mặc định đổi (có khoá `wharton: true`): kết quả đã chạy trước đó của workspace đọc thành bật sẽ báo "đã cũ".
- Sổ mẫu `mau_csv/SO_NHAP_CLB.xlsx` và hai sổ `vi_du_*` nạp với mặc định mới: các sổ `vi_du_*` chưa điền cột Điểm quyết tâm nên bị chặn khi chạy; tắt rõ ràng thì nạp và chạy trùng khít bộ ba CSV (seed 1, 7, 42).

**Nhóm B (tệp mẫu / ví dụ giao người dùng) — Truong chốt hướng (c), làm xong:**
- **Bộ ví dụ THÊM điểm quyết tâm MÔ PHỎNG hợp lệ** (mỗi quỹ mỗi buổi đủ 100), bằng script có seed cố định `du_lieu_test/them_diem_quyet_tam_vao_mau.py` (không gõ tay; chạy lại ra đúng cùng nội dung): `du_lieu_test/vi_du_huong_dan` (VIDU_03 `.csv`/`.xlsx`, `SO_NHAP_VIDU.xlsx`), `mau_csv/vi_du_day_du`, `mau_csv/vi_du_ca_tuan` (bộ ba CSV + `SO_NHAP_CLB_vi_du.xlsx`), `mau_csv/08_nguyen_vong_nhieu_buoi.csv`. Hợp đồng cột CSV không đổi (chỉ thêm `wp_k` / `<buổi>_wp_k` mà bộ nhập đã hỗ trợ). `mau_csv/tao_so_nhap.py` đọc cột `wp` từ CSV để dựng sổ. Test giữ nguyên assert, chỉ đổi dữ liệu. Kết quả của `vi_du_huong_dan` và `08` không đổi. Riêng `vi_du_day_du`: với điểm quyết tâm, HS024 (mỗi buổi khai 2 CLB không thi, nên ≤ 75 điểm) luôn thua các em chỉ khai một CLB (100 điểm) — bỏ nguyện vọng thứ Hai `clb_bongro` của HS024 trong `tao_bo_mau.py` để đúng một em trắng tay như `GIAI_THICH.md` kể; 23 / 24 em và 1,88 CLB/em giữ nguyên. **Truong đã duyệt 01/11/2026** (thay đổi HS024, mã băm mới của `test_ket_qua_khong_doi[vi_du_day_du]`, và 4 ca test chỉnh theo bộ ví dụ có điểm quyết tâm). Tài liệu cập nhật: `GIAI_THICH.md` (hai bộ), `README.md` của `vi_du_huong_dan`, `HUONG_DAN_SU_DUNG.md`, `TAI_LIEU_DU_LIEU.md`; ghi rõ là dữ liệu MÔ PHỎNG.
- **`bo_sach` (dữ liệu của báo cáo đề tài): GIỮ NGUYÊN dữ liệu.** Mọi nơi chạy bộ này tắt Wharton RÕ RÀNG (`test_bo_sach`, phần `bo_sach` của `test_diem_bat_thuong`, các script `du_lieu_test/`) để số liệu đã công bố tái lập được. Không sửa con số nào trong báo cáo.
- **Skill `sinh-du-lieu-clb`:** mặc định sinh KÈM điểm quyết tâm MÔ PHỎNG hợp lệ (`--diem-quyet-tam hop_le`); thêm cờ `--khong-diem-quyet-tam` để tắt (đầu ra như trước). `SKILL.md` và `TAI_LIEU_DU_LIEU.md` cập nhật.
- **Skill `tao-workspace-tu-raw`** (dữ liệu THẬT, không bịa điểm): spec không ghi `rules.wharton` thì workspace ghi `wharton: false` và báo "Dữ liệu không có điểm quyết tâm nên đã tắt tính năng này" (CLI, `ghi_chu` trong `--json`, `BAO_CAO_SOAT.md`). **Skill `xu-li-raw-forms`** và bộ chuyển Forms mẫu `mau_forms_thi_clb`: sổ không chứa được cấu hình nên báo trong báo cáo/CLI "cần TẮT 'Dùng điểm quyết tâm' trước khi nạp". Test đi theo nhánh này.
- **`du_lieu_test/NHAP_TAY.md`:** thêm Bước 3 "chia điểm quyết tâm" (số MÔ PHỎNG do `random.Random(112026105)` sinh, test canh bảng khớp tài liệu); đánh số lại các bước sau. Bảng kết quả không đổi (mọi em đã thi mọi CLB mình ghi; không có cặp bằng điểm thi) — test canh cả hai cấu hình.
- **CSDL demo:** đã gộp `claude/demo-wharton-va-duong-dan` (merge); `test_csdl_demo_that_duoc_nang_len` xanh với CSDL demo mới.
- **Để sau:** biểu mẫu Google Forms (`tao-google-form-clb`) chưa đổi; việc để sau là thêm phần thu điểm quyết tâm vào biểu mẫu.

**Đính chính phạm vi chạy test (01/11/2026, sau CI):** lần báo "0 đỏ" trước đó chỉ đúng trên danh sách test chọn bằng grep (`wharton|MAC_DINH_TRUONG_HOC|luat_xep|dau_van_tay|trung_khit`); danh sách đó bỏ sót phần lớn các tệp chạy pipeline với dữ liệu không có điểm quyết tâm, nên CI toàn bộ báo thêm 241 ca đỏ (40 tệp). Sửa nhóm A (fixture nội bộ, không phải mẫu giao người dùng): 27 tệp được thêm fixture `api` cục bộ gọi `tat_wharton` (KHÔNG autouse toàn cục, không nới assert, không skip): `test_so_excel_de_dung`, `test_export_ket_qua`, `test_du_lieu_ket_qua`, `test_xoa_du_lieu`, `test_nghich_canh`, `test_api`, `test_bo_kich_tran`, `test_diem_theo_o_tick`, `test_bo_toan_tuan`, `test_xuat_khoa_chua_co_ket_qua`, `test_xuat_du_lieu`, `test_thi_qua_tran_sau_doi_buoi`, `test_nap_diem_tu_file`, `test_diem_bat_thuong`, `test_khoa_hat_giong`, `test_data_durability`, `test_rang_buoc_csdl`, `test_a13_9_stress`, `test_ket_qua_khong_doi` và 9 tệp `test_giao_dien_*` (`chay`, `chon_buoi`, `khoa_hat_giong`, `tom_tat_ket_qua`, `thu_gon_ket_qua`, `danh_sach_clb`, `a13_11_csdl_ban`, `a13_12_tkb`). Thêm một lỗi thật do chính A13.13 gây ra: câu tiếng Việt của `wharton_ho_so_chua_hop_le` có từ "workspace" (bị `test_giao_dien_tieng_viet_sach` bắt) — đổi thành "không gian làm việc". Nhóm B (tệp mẫu / ví dụ giao người dùng, KHÔNG che bằng `tat_wharton`; chờ Truong quyết) còn đỏ có chủ ý; danh sách trong tệp bàn giao `docs/phien/claude__wharton-mac-dinh-bat.md`.

**Kiểm nhận độc lập (phiên cha thiết kế):** `tests/test_a13_13_kiem_nhan.py` (45 ca, nhóm A–F) và `tests/test_giao_dien_a13_13_kiem_nhan.py` (2 ca, nhóm G): đều qua, không phải sửa mã. So hai script đo với bản gốc `cee2940` bằng `git worktree`: `do_anh_huong_seed.py --so-seed 5` và `bao_cao_phan_bo.py` cho đầu ra giống hệt.

**Test** (`tests/test_wharton_mac_dinh_bat.py`, 16 ca mới; helper `tests/_wharton.py::tat_wharton`, KHÔNG autouse). Test cũ sửa, không xoá, không skip: (a) đổi sang mặc định mới + giữ khẳng định cũ dưới dạng ca `wharton: false` tường minh: `test_wharton_luat`, `test_ws_cau_hinh`, `test_ws_api`, `test_ws_sua_loi_2`, `test_ws_so_nhap`, `test_ws_nhan`, `test_so_mau_co_cot_quyet_tam`, `test_wharton_so_nhap`; (b) truyền `wharton: false` ở fixture / đầu test (hành vi cũ làm nền): `test_nhieu_buoi`, `test_wharton_pipeline`, `test_thay_doi_ket_qua`, `test_ws_luat`, `test_ws_sua_loi_3`, `test_diem_chuan`, `test_wharton_{quan_ly,hang_loat,kiosk,khoa,nhap,suc_khoe,dau_cuoi}`, `test_so_nhap_hai_hang`.

## 2026-11-01 — Công cụ phiên (ngoài sổ): sửa test tài liệu sau khi rút gọn CLAUDE.md

- `tests/test_a13_12_tai_lieu.py::_doan_ban_do` đọc "Bản đồ mã" ở `docs/ke_hoach/CLAUDE_CHI_TIET.md` (bảng đã chuyển nguyên văn khỏi `CLAUDE.md` ở `5fd624b`). Trước đó hai ca `test_ban_do_ma_co_nhom_ham_diem_quyet_tam`, `test_ban_do_ma_so_tep_test_la_so_that` đỏ trên `cee2940`. Không đổi mã sản phẩm. `kiem_nhanh.py --co-so cee2940`: 7/7 ĐẠT.
- `TAI_LIEU_DU_LIEU.md` mục 4 nay tả `.claude/settings.json` và hook bàn giao (thêm ở `5fd624b`); `tests/test_tai_lieu_du_lieu.py`: `VANG_MAT_CO_Y` thành tập rỗng. Trước đó `test_nhung_tep_tai_lieu_noi_khong_co_thi_van_khong_co` đỏ trên nhánh này và mọi nhánh tách từ nó.
- Lưu ý khi gộp nhánh `claude/wharton-mac-dinh-bat`: nhánh đó thêm tệp test, nên phải cập nhật số tệp ở dòng `tests/` của bản đồ mã trong `CLAUDE_CHI_TIET.md`.

## 2026-10-28 — A13.12 Sửa Tầng 4 của đợt soát A13 và toàn bộ mục chặn / nên sửa của đợt soát hệ thống nhập

Theo yêu cầu của Truong qua phiên điều phối. Mô phỏng. Tắt Điểm quyết tâm: kết quả trùng khít `e08af78`. Mỗi mục có test đỏ trước, xanh sau (mục chỉ thêm test: ghi rõ). Bảng xử lý từng mục (commit hoặc "không sửa – lý do"): `docs/ke_hoach/BAO_CAO_SOAT_NHAP.md` (cột cuối mỗi bảng) và mục "Vòng sửa A13.12" cuối `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md`.

**Phần 1 — Tầng 4 (`BAO_CAO_SOAT_MA_A13.md`, Truong đã chốt)**
- **4.5 (`f1292c8`):** `tests/test_wharton_khoa.py::test_loi_o_buoc_nhat_ky_khoa_rollback_ca_giao_dich` làm `_ghi_nhat_ky_wharton("khoa")` ném lỗi SAU khi dòng khoá đã chèn và khẳng định `match_results`, `run_history`, `wharton_lock`, `stb_lock`, nhật ký nguyên vẹn; gây hỏng `rollback()` → `commit()` thì tệp chủ đề nay đỏ. `tests/test_wharton.py::TestKiemHoSo::test_bien_ngan_sach_99_100_101` bắt đột biến `> ngan_sach + 1`. Chỉ thêm test, không đổi mã sản phẩm.
- **4.1 (`047b2cb`):** `CLAUDE.md` bản đồ mã định vị theo TÊN HÀM, không ghi số dòng; thêm hàng "Điểm quyết tâm"; số tệp test thật; `DOI_CHIEU_KHO_MA.md` mục "Cập nhật 28/10/2026". Test `tests/test_a13_12_tai_lieu.py` canh: không số dòng, mọi tên trong dấu huyền đều tồn tại, số tệp test đúng.
- **4.2 (`1ab2174`):** `xu-li-raw-forms/SKILL.md` tả đúng bố cục (sổ mẫu có cột Điểm quyết tâm, sổ của kỹ năng không có); `HUONG_DAN_SU_DUNG.md` "điểm của em khác".
- **4.3 (`56cc766`, `9a19068`):** xoá khoá i18n chết `dc_cot_buoi` (`dc_tooltip_so` đã xoá từ A13.10); test `tests/test_i18n_khoa_dc_khong_chet.py`.
- **Hai chuỗi đổi ngôn ngữ (`fallback_phu_buoi`, `btn_remove_ranked`) (`8021916`):** KHÔNG tái hiện được ở mã hiện tại (đã đúng từ A13.7: `js/07_ngon_ngu.js` gọi lại `renderRankingList()`); chỉ thêm `tests/test_giao_dien_a13_12_ngon_ngu.py` (bỏ dòng đó thì cả hai ca đỏ).

**Phần 2 — `BAO_CAO_SOAT_NHAP.md` (39 mục: 1 chặn, 21 nên sửa, 17 nhỏ)**
- **1.1 CHẶN (`173e017`):** F5 ở chế độ trình duyệt không còn tắt máy chủ. `/__closed__` chỉ đánh dấu; watchdog (kiểm mỗi giây) tắt khi ≥ 4,5 s sau đó không có ping hay kết nối sống mới (`_CHO_SAU_BAO_DONG_SECONDS`). Test: `tests/test_giao_dien_a13_12_f5.py` (Chromium, F5 ×3 rồi gọi API; đỏ trước với `ERR_CONNECTION_REFUSED`), `tests/test_a13_12_browser_host.py`. Chưa thử trên cửa sổ `--app` Edge/Chrome thật.
- **1.2 (`173e017`):** mọi lỗi HTTP trả `errors = [{code, params}]`; 4 mã mới `http_bi_tu_choi`, `http_khong_co_dich`, `http_khong_co_ham`, `http_than_qua_lon`.
- **1.4, 1.5 (`c8f986e`):** cột phụ bên phải nhóm cuối của Sổ hai hàng không làm cả sổ bị từ chối (nhóm cuối rộng bằng nhóm liền trước; cột lạ TRONG nhóm vẫn là lỗi); `re.fullmatch(r"[0-9]+", …)` cho ô điểm quyết tâm khi ghi sổ.
- **Backend (`a6738ca`):** 1.6/3.3 `page` vượt tổng được kẹp về trang cuối ở `list_students_admin`, `list_wharton_admin`, `get_wharton_nhat_ky`; 3.1 `create_student_if_missing` bỏ khoảng trắng đầu / cuối, từ chối mã rỗng (mã mới `student_id_required`); 3.2 `delete_club` sao lưu rồi xoá và trả `n_scores_removed`, `n_tests_removed`, `backup_path` (Truong chọn); 4.1 `delete_workspace` kiểm "đang mở" trong khoá; 4.2 xoá hết workspace thì dựng lại "Trường học"; 4.3/4.4 workspace `priority = tier`: `submit_person_scores`, `get_club_applicants_for_scoring`, `get_scoring_overview` trả `scoring_not_per_slot` (Truong chọn: không chắn `per_person`); 4.5 mã không băm được thì bỏ qua mục đó; 4.6 `export_workspace` lùi về thư mục gốc chương trình; 2.7 bộ nhớ xuất nhận keyword; 2.8 bỏ trần 1.000 bản của `duong_dan_khong_de`; 2.9 số âm dạng chuỗi (`-1,5`) không thêm dấu nháy; 1.10 `api_nhap._doc_diem` / `_o_excel_thanh_chu` là CHÍNH `so_nhap.doc_diem` / `o_thanh_chu`. Test: `tests/test_a13_12_backend.py` (38 ca).
- **Kiosk (`15eabd9`):** 2.2 ô tự điền 100 (ô bị khoá) không gửi lên khi Lưu; 1.8/2.4 ô tự điền không còn báo "Chưa lưu" giả; 1.7/2.3 mốc "đã lưu" và dòng thông báo theo bản chụp LÚC BẤM; 1.9/2.6 xoá em đang mở dọn sạch Bước 3, xếp hạng, mốc, hẹn giờ; 2.5 chọn em khác xoá dòng "Đã lưu" của em trước; đồng bộ trang. **Bốn test cũ sửa có duyệt (Truong chọn A):** `tests/test_giao_dien_wharton.py::test_luu_thieu_40_…`, `test_o_chua_luu_hien_dau_chua_luu_…`, `test_bo_clb_o_buoc_2_…`, `test_nhieu_buoi_moi_buoi_…` (sau Lưu, CSDL không còn dòng 100 tự điền; ô tự điền không hiện "Chưa lưu"). Test mới: `tests/test_giao_dien_a13_12_nhap.py` (7 ca).
- **Quản lý và workspace (`dd94e50`):** 3.2 toast xoá CLB nêu số điểm / ô tick đã xoá và tên tệp sao lưu; 3.4 sau thao tác đổi dữ liệu (xoá một, phóng, mở khoá…) màn sửa không điền lại chữ cũ (`loadAdminWharton(giuTrang, giuChu)`); 3.6 tìm TKB không khớp giữ ô tìm; 3.9 chi tiết điểm chuẩn dùng `callApiMoiNhat`; 3.10 lưu / xoá CLB làm mới bảng tải theo buổi; 4.8 tạo workspace mà mở lỗi thì bấm "Tạo" lại chỉ thử mở lại; 4.10 wizard chặn nhãn bắt đầu bằng `= + - @` (khoá mới `ws_v_cong_thuc`). Test: `tests/test_giao_dien_a13_12_ql_diem_chuan.py`, `_ql_wharton.py`, `_tkb.py`, `_ws.py`.
- **Không sửa:** 3.8 (đo 800 × 20: mỗi hàm đọc ≤ 0,05 s), 4.7 (tên workspace không vào ô Excel nào; chặn sẽ từ chối tên hợp lệ), 4.9 (cần giao diện mới, ngoài ít mã). **Đã sửa trước đó:** 1.3 (A13.9 `1dac117`), 2.1 (A13.8 `04740a5`), 3.5 (A13.8 `a710a31`), 3.7 (A13.8 `d4dc297`).
- **Mã lỗi / khoá mới:** `http_bi_tu_choi`, `http_khong_co_dich`, `http_khong_co_ham`, `http_than_qua_lon`, `student_id_required` (thêm vào `MA_MOI_SAU_ANH_CHUP`, sinh lại `i18n_loi.js`); khoá giao diện `toast_club_deleted_removed`, `ws_v_cong_thuc`.
- **CI Windows (`e1f6d56`) và `ws_v_cong_thuc` (`2f313ec`):** `chan_doan` chuẩn hoá `\r\n` trước khi so mục trùng; `sinh_du_lieu_diem_quyet_tam.py` và `kiem_nhanh.py` reconfigure stdout/stderr utf-8, `kiem_nhanh` thêm `errors="replace"`; chuỗi `ws_v_cong_thuc` không còn " - " đứng riêng. Test giả lập: `tests/test_a13_12_windows.py` (CRLF, cp1252). Chưa có Windows thật để xác nhận.
- **Kiểm (28/10/2026):** toàn bộ test có Chromium, `-rs`, phủ **92,98 %**: 3.051 qua, 1 bỏ qua (cần người dùng thường trên POSIX), 2 ca đỏ ở `tests/test_i18n_sync.py` do lượt chạy trùng lúc sửa `i18n_errors.py` (chưa sinh lại `i18n_loi.js`); chạy lại tệp đó sau khi sinh lại: 9 qua. Lượt chạy này có trước ba commit cuối (`4d02c6d`, `2f313ec`, `e1f6d56`); các tệp test liên quan đã chạy lại riêng: 135 qua (`test_a13_9_stress`, `test_du_lieu_mau_diem_quyet_tam`, `test_skill_soat_ma`, `test_a13_12_windows`) và 25 qua (`test_van_phong_tu_nhien`, `test_i18n_sync`, `test_giao_dien_a13_12_ws`). `kiem_nhanh.py --co-so e08af78`: **7/7**, trùng khít 15 ca. `ruff check .` sạch.


## 2026-10-28 — A13.11 Sửa 4 phát hiện N1–N4 của đợt stress test (trên đỉnh A13.9)

Theo danh sách Truong chọn trong phiên điều phối (`docs/ke_hoach/VAN_DE_STRESS_TEST.md`, N1–N4). Mô phỏng. Test mới: `tests/test_a13_11_stress.py`, `tests/test_giao_dien_a13_11_csdl_ban.py` (mỗi mục đỏ trước, xanh sau). Không đụng màn Điểm chuẩn (phiên A13.10).
- **N1 (`902cb6b`, `02c3089`):** đường xuất tuyệt đối là THƯ MỤC có sẵn → lỗi mới `xuat_duong_la_thu_muc` (`LoiDuongXuat` ở `api_workspace.py`; mọi hàm xuất và `export_workspace` trả lỗi có tên, không đẻ tệp `x (2)` cạnh thư mục). Phản hồi chỉ mang TÊN thư mục, không lộ đường dẫn máy (s8 T7 sạch).
- **N2 (`442725f`):** nạp Sổ / CSV ghi MỘT dòng `wharton_nhat_ky` (`nguon = nap_tep`, `hanh_dong = luu_hang_loat`, `student_id` rỗng, `moi_json = {so_em_doi, so_dong_nap}`) thay vì một dòng mỗi em; không em nào đổi điểm thì không ghi gì; vẫn chỉ ghi thêm, trong cùng giao dịch. Giao diện thẻ Quản lý hiện dòng tóm tắt (`wh_nk_luu_hang_loat`, `wh_nk_tom_tat`). s6 phần B (100 vòng nạp-xoá-nạp, 800 em): `app.db` 16,7 → **1,66 MB**, sao lưu 158 → **16,1 MB**.
- **N3 (`49c7319`):** `_BUSY_TIMEOUT_MS` 15.000 → 3.000; `err()` đổi MỌI lỗi có `detail` là "database is locked / busy" thành `csdl_dang_ban` (một chỗ, phủ hàng trăm khối `except`); `get_data_health_report` báo ngay; `run_pipeline` dừng với `csdl_dang_ban` khi bước sao lưu gặp CSDL bận (không chạy tiếp thiếu lưới an toàn; lỗi sao lưu khác vẫn không chặn); giao diện: "Kiểm tra dữ liệu" và "Chạy sắp xếp" nói "CSDL đang bận" thay vì "chưa hợp lệ" / "không thành công" (`coLoiCsdlBan` ở `js/00_nen.js`); ô cảnh báo dữ liệu và thống kê tổng quan vốn đã hiện đúng. s3 phép D: `list_students_admin` 15,0 → **3,0 s**, `reset_data` 15,0 → **3,0 s**, `run_pipeline` 17,6 → **3,0 s**, `submit_preferences` / `import_so_nhap` 15,0 → 2,5 s; tất cả `csdl_dang_ban`, CSDL không đổi, mở khoá xong chạy lại bình thường.
- **N4 (`2fb9680`):** NGUYÊN NHÂN (đo bằng `server`/`browser` tách tiến trình): KHÔNG phải vẽ DOM và không phải một lời gọi chậm — từng hàm đọc chỉ 10 – 50 ms khi chạy riêng, nhưng thẻ Kết quả bắn 13 lời gọi đọc cùng lúc và chúng tranh GIL (mỗi bước `sqlite3` nhả rồi giành lại GIL), nên trong máy chủ `get_match_results` mất 3,1 s, `get_em_chua_co_cho` 3,6 s. Sửa: `PipelineAPI._xep_hang_doc` xếp hàng mọi hàm đọc (`get_*`, `list_*`, `check_*`, `xem_truoc_*`) bằng một RLock `_cong_doc`; ghi vẫn dùng `_khoa_ghi`, không bị chặn. 5.000 × 100: lần đầu mở thẻ Kết quả **13,6 s → 1,06 s**; trang chậm nhất của danh sách học sinh **6,5 s → 0,34 s** (không trang nào > 1 s). 800 × 20 không chậm đi (`--nhanh`: mở thẻ Kết quả lớn nhất 500 → 249 ms; mỗi trang trung vị 92 → 91 ms).
- **Test cũ sửa có duyệt (Truong chọn A, 28/10/2026), do N2:** `tests/test_wharton_nhat_ky.py::test_nap_tep_ghi_nguon_nap_tep` (chờ MỘT dòng `("nap_tep", "luu_hang_loat", None, None, {so_em_doi: 1, so_dong_nap: 1})`; nạp lại y nguyên vẫn không ghi thêm) và `tests/test_wharton_quan_ly_dau_cuoi.py::test_kich_ban_dau_cuoi` (một dòng `luu_hang_loat` thay 15 dòng `luu`, hai chỗ).
- **Lỗi xuất không lộ đường dẫn máy (Truong chọn, 28/10/2026):** `error_exporting_csv`, `error_exporting_excel`, `so_nhap_mau_loi` và `export_workspace` trước đây đưa `str(e)` (có tên tệp / đường dẫn máy) vào `detail`. Nay `detail` chỉ là kiểu lỗi + lý do của hệ điều hành (`FileNotFoundError: No such file or directory`); đường dẫn đầy đủ vào `loi_ung_dung.txt` (`XuatKetQuaMixin._chi_tiet_loi_xuat`). Test: `tests/test_a13_11_stress.py` (nhóm `n1b`, 9 ca).
- **Kiểm:** `kiem_nhanh.py` 7/7. Toàn bộ test có Chromium, `-rs`, phủ 92 %: 2.938 qua, 2 đỏ (hai ca trên), 1 bỏ qua (cần người dùng thường trên POSIX). `ruff check .` sạch.

## 2026-10-28 — A13.10 Nhãn "Xét điểm thi / Xét điểm quyết tâm" và thiết kế lại màn Điểm chuẩn

Theo yêu cầu của Truong (duyệt ba điểm: sửa bộ chọn test giao diện cũ; biểu đồ chỉ khối Điểm chuẩn tự đổi nền tối vì ứng dụng chưa có giao diện tối chung; EN dùng "commitment points" trong cả khối). Chỉ đổi cách hiện; API `get_diem_chuan` / `get_diem_chuan_clb`, schema, hợp đồng cột CSV, thuật toán và kết quả xếp KHÔNG đổi. Mô phỏng.
- **1. Nhãn hiển thị:** "Tầng 1" thành "Xét điểm thi" / "Exam-based", "Tầng 2" thành "Xét điểm quyết tâm" / "Commitment points" ở giao diện (`i18n.js`, khoá `dc_*`, VI và EN), tệp xuất Excel (`api_xuat.py`: tiêu đề cột và mô tả trang Điểm chuẩn) và hướng dẫn (`HUONG_DAN_SU_DUNG.md`, `README.md`, `TAI_LIEU_DU_LIEU.md`, `GIAI_THICH_DE_HIEU.html`, `BAO_CAO_CACH_CHAY.html`, `mau_csv/vi_du_day_du/GIAI_THICH.md`). Nơi cần danh từ thì ghi "nhóm xét điểm thi / nhóm xét điểm quyết tâm". Mã, biến, cột, mã lỗi giữ `tier`, `tang1`, `tang2`. Chưa đổi: `poster/`, chú thích trong `.py`, `BAN_GIAO.md` và các tài liệu kế hoạch nội bộ.
- **2a. Bảng tổng** (`js/05_quan_ly.js`, `veTongQuanDiemChuan`): hai cột điểm chuẩn riêng, mỗi ô một thanh SVG (thang điểm thi 10 / 100 tự chọn theo dữ liệu, điểm quyết tâm 0 đến 100); bỏ dòng chữ nhỏ dưới tên CLB (mã `dc-phu`).
- **2b. Đơn và chỗ (làm lại sau góp ý của Truong: bản đầu khó hiểu):** cột "Đơn và chỗ" có nhãn mức bằng chữ (`dc-chip`: Đủ chỗ / Đông / Rất đông, `data-muc` = `thap` / `vua` / `cao`, ngưỡng đơn / chỗ 1 và 2), "N đơn · M chỗ" có đơn vị, và một thanh chung một thang cho cả bảng gồm ba phần: đơn nằm trong số chỗ (xám đậm), đơn vượt chỗ (màu theo mức), chỗ còn trống (khung rỗng); chú giải ba phần và một câu giải thích ba mức. Bỏ thanh tối đa 5 lần chỗ có vạch mốc và các khoá `dc_ti_le_thap/vua/cao`; khoá mới `dc_muc_*`, `dc_don_chu`, `dc_bar_*`, `dc_muc_giai_thich`. Thay chấm đỏ.
- **2c. Chi tiết một CLB:** histogram và dải chấm cũ gộp thành MỘT SVG beeswarm (`veChiTietDiemChuan`, `svg[data-bieu-do=chi-tiet]`): chấm cùng điểm xếp cột không chồng nhau, vạch chuẩn ghi số, vùng nhạt bên phải vạch là vùng được nhận, chấm đặc xanh được nhận / chấm rỗng xám không được nhận, chú giải ba mục, tooltip và bảng chữ ẩn giữ nguyên. Xoá `veCotPhanBoQuyetTam`, `veDaiChamQuyetTam`, `dcCotTronTren` và khoá i18n không còn dùng (`dc_cot_chuan`, `dc_nong`, `dc_cot_tieu_de`, `dc_truc_y`, `dc_tooltip_khoang`, `dc_tooltip_so`); khoá mới `dc_ti_le_*`.
- **Sáng / tối, chuyển động** (`style.css`): màu qua biến; `prefers-color-scheme: dark` (và `[data-theme=dark]`) chỉ đổi khối Điểm chuẩn sang nền tối; hiệu ứng chấm vào dần chỉ chạy khi `prefers-reduced-motion: no-preference`. Không thư viện ngoài.
- **Test mới:** `tests/test_giao_dien_a13_10_nhan.py` (5 ca: nhãn VI / EN, khoá `dc_*`, tài liệu) và `tests/test_giao_dien_a13_10_diem_chuan.py` (9 ca: hai cột, bỏ chữ phụ, nhãn mức / đơn vị / thang chung của cột Đơn và chỗ, một SVG, chấm không chồng, chú giải và tooltip, reduced-motion, chế độ tối, EN). **Test cũ sửa có duyệt:** `tests/test_giao_dien_diem_chuan.py` đổi bộ chọn (`svg[data-bieu-do=cot|cham]`, `#dcCot`, `#dcCham` thành `svg[data-bieu-do=chi-tiet]`, `#dcBieuDo`; hai test (a), (b) gộp một); `tests/test_diem_chuan.py` đổi chữ tiêu đề cột Excel.
- **EN: một tên "commitment points" cho toàn giao diện (Truong yêu cầu, chỉ chữ giao diện):** mọi "preference point(s)" trong `i18n.js` (18 chỗ) và thông báo lỗi EN `i18n_errors.py` (24 chỗ, sinh lại `i18n_loi.js`) đổi thành "commitment point(s)" (tab Quản lý, bước 3 nhập tại chỗ, nút lưu / mở khoá / xoá, tên tính năng ở workspace, lỗi nhập). "Preference(s)" nghĩa là nguyện vọng giữ nguyên. Sổ nhập: `so_nhap.py` nhận thêm tên cột "commitment points" (vẫn nhận "preference points" cũ). Sáu test giao diện cũ đổi chữ EN mong đợi; test mới `test_en_moi_cho_deu_la_commitment_points_khong_con_preference_points`. Không đổi mã, schema, tài liệu.
- **Ảnh trước / sau:** `docs/anh/a13_10/{truoc,sau}_{vi,en}_{sang,toi}.png` từ `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`, seed 3, chụp bằng `docs/anh/a13_10/chup_anh.py`. Ảnh "trước" có "Tầng 1/2" vì chụp từ bản gốc; ứng dụng chưa có giao diện tối chung nên ảnh "tối" chỉ khác ở khối Điểm chuẩn.
- **Kiểm (28/10/2026):** toàn bộ test có Chromium, `-rfs`, phủ 92,57 %: 2.911 qua, 3 bỏ qua (numpy ×2, POSIX ×1), 4 ca đỏ ở `test_giao_dien_tro_nang.py` (WCAG đọc mã màu cuối cùng của từng biến trong `style.css`, nên bảng màu tối của khối Điểm chuẩn bị tính nhầm); đã sửa bằng cách đặt màu tối ở biến `--dcd-*` rồi gán qua `var()`, chạy lại các tệp đọc `style.css` (57 qua) và các tệp Điểm chuẩn (37 qua). `kiem_nhanh.py` (`--co-so 167be48`, trước A13.10): trước khi rebase 6/7 (12 lỗi `ruff`, tất cả trong `du_lieu_test/stress/*` của phiên stress test); sau `git pull --rebase` lên A13.11: **7/7**, trùng khít 15 ca; chạy lại 100 ca giao diện / điểm chuẩn / WCAG sau rebase, qua cả.

## 2026-10-28 — A13.9 Sửa 9 vấn đề từ đợt stress test

Theo danh sách Truong đã chốt (mục 1–9; #10 numpy không làm). Mô phỏng. Tắt Điểm quyết tâm: kết quả trùng khít `e08af78` (`kiem_nhanh.py --co-so e08af78`, 15 ca, 3 bộ × 5 seed). Test mới: `tests/test_a13_9_stress.py` (mỗi mục đỏ trước, xanh sau).
- **1. CSDL bận:** mã lỗi mới `csdl_dang_ban` (`CsdlBan`, con của `CauHinhHong`, nên mọi nơi đang dừng vẫn dừng; `loi_cau_hinh(e)` chọn mã). `connect_db(cho_khoa_ms=)`; `cau_hinh_ws.CHO_KHOA_DOC_CAU_HINH_MS = 2500`. Tệp: `rbda_priority_pipeline.py`, `cau_hinh_ws.py`, `api_workspace.py`, `api*.py`, `i18n_errors.py`, `i18n_loi.js`. Lưu ý: `run_pipeline` vẫn chờ tới 15 s ở bước sao lưu (cố ý: rút ngắn là bỏ qua sao lưu khi khoá ngắn).
- **2, 3, 5. `browser_host.py`:** `_Handler.timeout = 45`; `_token_khop` so token trên byte (token không ASCII ở tiêu đề / `?t=` → 403); `loi_ngoai_du_kien` chỉ trả tên kiểu ngoại lệ, thông điệp thật nằm ở `loi_ung_dung.txt`.
- **4. `chan_doan.py`:** `loi_ung_dung.txt` trần `TRAN_LOG_UNG_DUNG_BYTE` = 1.000.000, cắt xuống 75 % giữ phần cuối ở ranh giới mục; bỏ mục trùng hệt mục ngay trước (khác giờ). Log khởi động không đổi.
- **6. `api_xuat.py`:** `_duong_xuat` với đường tuyệt đối cũng đi qua `duong_dan_khong_de` (kể cả `kem_duoi`): `x (2).xlsx`. Áp cho mọi hàm xuất và `export_workspace`.
- **7. `workspace.py`:** `nhap_zip` — `TRAN_SO_TEP_ZIP = 1000`, `TRAN_GIAI_NEN_BYTE` hạ 500 → 200 MB, từ chối tên trùng (chuẩn hoá dấu phân cách, hoa/thường), kiểm NUL trên `orig_filename` (trước đây `zipfile` cắt tên nên kiểm NUL không bao giờ bắt được).
- **8. Sổ rỗng:** `so_nhap.py` bỏ lỗi `so_nhap_khong_co_clb`; `api_nhap.py` báo `so_nhap_canh_bao_khong_co_clb` / `so_nhap_canh_bao_khong_co_hs`, bỏ bước nạp CLB khi sổ không có CLB; `run_pipeline` sau đó chạy được.
- **9. Skill `sinh-du-lieu-clb`:** quá 20 CLB tự sinh "CLB Chuyên đề N"; ≤ 20 giữ đúng từng byte (băm 6 cấu hình so với `0f13771`).
- **Test cũ (Truong chọn 1A, 2A, 28/10/2026):** thêm 3 mã vào `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`); hai test sửa có duyệt — `test_nap_xuat_ca_hiem.py::test_khong_con_tep_cua_lan_xuat_truoc` gọi thẳng `_ghi_bo_csv` hai lần trên cùng đường (qua `export_csv` giờ ra `x (2).csv`, không còn ghi đè tại chỗ); `test_so_nhap.py::test_ma_trong_dung_lai_clb_cung_ten_va_bao_clb_ngoai_so` thêm một em vào sổ để không dính cảnh báo sổ rỗng.
- **Kiểm:** `kiem_nhanh.py` 7/7. Toàn bộ test có Chromium, `-rs`, phủ 93 %: 2.902 qua, 2 đỏ trước khi sửa hai test trên (chạy lại hai tệp đó: 95 qua), 1 bỏ qua (cần người dùng thường trên POSIX). `ruff check .` sạch. **Chưa làm:** chạy lại s3/s8 `--nhanh` và cột "Đã sửa ở commit" — `VAN_DE_STRESS_TEST.md`, `BAO_CAO_STRESS_TEST.md` và kịch bản s3/s8 chưa có trên nhánh (Truong chọn 4A: chờ đẩy lên rồi làm).

## 2026-10-28 — A13.8 Sửa 12 lỗi từ đợt soát A13

Theo danh sách Truong đã chốt (báo cáo `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md`, mục "Vòng sửa A13.8"). Mô phỏng. Tắt Điểm quyết tâm: kết quả, dấu vân tay, run_history trùng khít `e08af78` (`kiem_nhanh.py`: 15 ca, 3 bộ × 5 seed).
- **2.1 + 3.2:** khoá đang bật và em đã có điểm thì `submit_preferences` / `submit_test_selection` trả `wharton_da_khoa` (gửi lại đúng danh sách cũ vẫn ok); nạp CSV / Sổ nhập bỏ qua em đó, cảnh báo `csv_wharton_khoa_giu_nguyen`; kiosk vô hiệu hai nút lưu kèm ghi chú. Tệp: `api_quan_ly.py`, `api_nhap.py`, `js/04_nhap_tai_cho.js`, `index.html`, `i18n.js`, `i18n_errors.py`. Test: `test_a13_8_khoa_nguyen_vong.py`, `test_giao_dien_a13_8_khoa.py`. **Hai test cũ sửa** (`tests/test_wharton_khoa.py`: nạp tệp khi khoá, cửa xoá khi khoá) vì mã hoá hành vi tỉa mà quyết định này đổi.
- **2.2:** docstring bốn API đúng thực tế; `HUONG_DAN_SU_DUNG.md` ghi "thẻ Quản lý cần người giám sát máy". Không PIN.
- **2.3:** `_trang_diem_chuan` ghi lý do lên trang và `export_ket_qua` trả `canh_bao` (`xuat_diem_chuan_loi`). Test: `test_a13_8_xuat_diem_chuan.py`.
- **3.1, 3.3, 3.4:** `js/05_quan_ly.js` chỉ ẩn tab khi `wharton_chua_bat`, lỗi khác hiện thông báo; tắt tính năng không gọi `list_wharton_canh_bao` / `get_diem_chuan` (cờ `WHARTON_BAT` đặt ở `js/075_workspace.js`); `style.css` `#dcKhongXet`. Test: `test_giao_dien_a13_8_quan_ly.py`.
- **2.4:** `phong_wharton_hang_loat` một giao dịch, đọc lại điểm hiện tại (`ly_do = "da_doi"`), rollback toàn bộ kèm `backup_path`; `_luu_wharton` tách `_luu_wharton_cur`. Test: `test_a13_8_phong_mot_giao_dich.py`.
- **2.5:** `_ngu_canh_diem_chuan` đọc trong một giao dịch (`load_wharton_kem_doc_them`, hàm mới ở `rbda_priority_pipeline.py`; hàm cũ giữ nguyên). Test: `test_a13_8_diem_chuan_mot_giao_dich.py`.
- **2.6, 2.7, 2.8:** `so_nhap.py` — cột W của sổ mẫu chỉ khi workspace bật được (`wharton_bat_duoc`); hằng `CHO_CHEN_GHI_CHU_W` thay việc dò "Bước 5."; test so `lam_tron_100` với `phong_theo_ti_le`. Test: `test_a13_8_so_mau.py`.
- **1.1 `submit_club_scores` (Truong chọn B, 28/10/2026):** lượt không lưu và không xoá được dòng nào vì ô điểm sai (`nan`, `inf`, `"1e999"`, `-1`, chữ) trả `ok=false`, `errors` liệt kê từng (student_id, giá trị) bằng `score_not_a_number` / `score_negative`; lượt lẫn ô đúng và sai vẫn lưu phần đúng, `ok=true` + `warnings` như cũ. `js/06_cham_diem.js` tô đỏ các ô sai cả khi thất bại. **Test cũ sửa có duyệt** (`tests/test_diem_bat_thuong.py`, đúng các ca một-ô-sai): `test_man_hinh_cham_diem_tu_choi_diem_am`, `test_hai_duong_nhap_cung_mot_luat_voi_diem_am`, `test_gia_tri_khong_doc_duoc_thi_khong_ghi_de_diem_cu`, `test_diem_am_viet_bang_dau_phay_van_bi_chan`; ca mới thêm ở cuối tệp. `js/06_cham_diem.js` hiện thông báo vàng liệt kê hết các ô sai khi lượt thất bại (nên test giao diện `test_o_bi_bo_qua_duoc_to_do_va_khong_bao_xanh` giữ nguyên). Hai test cũ ở `tests/test_wharton_khoa.py` (lỗi 2.1) cũng được Truong đồng ý giữ nguyên bản sửa.
- **Kiểm:** toàn bộ test có Chromium, `-rs`, độ phủ 92,47 %: 2.859 qua (sau khi sửa 1 ca giao diện chấm điểm, đã chạy lại riêng và qua), 3 bỏ qua (numpy ×2, POSIX ×1; không ca giao diện nào bị bỏ qua). `ruff check .` sạch.

## 2026-10-28 — Z-SOAT Skill `soat-ma`: soát mã trước khi push

Theo yêu cầu của Truong (28/10/2026, "làm bước cuối" của đợt soát A13). Mã mục `Z-SOAT` do Claude đề xuất, chưa có trong sổ đăng ký 33 mục (quy ước khác thì đổi tên). Đây là lần duy nhất đợt soát được thêm mã; KHÔNG sửa lỗi nào trong `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md` (sẽ làm ở A13.8, dùng chính skill này).

- **Tệp mới:** `.claude/skills/soat-ma/SKILL.md` (luật không subagent / chỉ báo cáo, phạm vi diff so với `main`, cách ghi phát hiện, checklist bốn tầng viết tổng quát kèm bài học rút từ đợt soát A13, lệnh, mẫu báo cáo); `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (một lệnh, bảy mục in ĐẠT / KHÔNG ĐẠT: `ruff`, `chu_cam`, `ma_loi_js`, `i18n_loi_khop`, `i18n_khoa`, `trung_khit` so với `main` 3 bộ × 5 seed, `khong_sua_nhat_ky`; chỉ thư viện chuẩn, `ruff` là công cụ ngoài đã có ở requirements-dev; mục không chạy được tính KHÔNG ĐẠT kèm lý do, không bỏ qua im lặng); `tests/test_skill_soat_ma.py`.
- **Tệp sửa:** `CLAUDE.md` — đúng MỘT dòng mới ở "Quy tắc làm việc" (quy tắc 8: "Trước khi push: chạy skill `soat-ma`"); bản đồ mã KHÔNG đụng (để A13.8).
- **Không đổi** mã sản phẩm, schema, hợp đồng cột CSV, hay kết quả xếp (bất biến 1–8 giữ nguyên). Skill KHÔNG vào `mau_forms_thi_clb/dong_goi_skill.py` (danh sách đó chỉ đóng .zip cho người dùng cuối); đăng ký theo kiểu của `sinh-du-lieu-clb` và `tao-workspace-tu-raw`: nằm trong `.claude/skills/`, có test riêng.
- **Test mới (45 ca):** `tests/test_skill_soat_ma.py` — mỗi mục một ca ĐẠT và các ca KHÔNG ĐẠT dựng trong thư mục tạm (xưng hô cấm ở VI / EN / lỗi / HTML, "Wharton" lộ ra chữ, mã lỗi lạ ở `.js` và `.html`, `i18n_loi.js` lệch và thiếu, khoá thiếu một ngôn ngữ hay rỗng, `DELETE` / `UPDATE` / `DROP` một dòng và nhiều dòng trên bảng dấu vết, tên bảng nằm trong danh sách `_RESET_BANG`-kiểu, hai bản mã khác thứ tự ưu tiên cho kết quả lệch, nhánh so sánh không có); khung `SKILL.md`, dòng trong `CLAUDE.md`, skill không nằm trong gói zip; và MỘT ca chạy script thật trên kho thật (năm mục nhanh phải ĐẠT: ai thêm xưng hô cấm, mã lỗi lạ, khoá i18n lệch hay xoá nhật ký thì test đỏ).
- **Chạy trên kho thật:** `kiem_nhanh.py` 7/7 ĐẠT (so với `main` và so với `e08af78`; trùng khít 15 ca). Hai điều chỉnh ghi trong mã và SKILL.md: chữ trong phần tử có `data-i18n` ở `index.html` là chữ dự phòng (có "em" từ trước A13) nên không soát lần hai; mã `loi_giao_dien_ngoai_du_kien` (từ trước A13) trùng một khoá UI nên được chấp nhận.
- **Kiểm toàn bộ (28/10/2026, Chromium thật, `-rs`):** 2.806 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua) — 2.761 của A13.7 cộng 45 ca mới. `ruff check .` sạch.

## 2026-10-27 — A13.7 Sổ nhập mẫu luôn có cột Điểm quyết tâm

Theo quyết định của Truong (27/10/2026): sổ MẪU luôn có cột "Điểm quyết tâm" kèm ghi chú "chỉ dùng khi bật tính năng". Không đổi mặc định `rules.wharton` (vẫn tắt), thuật toán, schema, hợp đồng CSV. Các đường ghi sổ khác (xuất dữ liệu đầu vào, ba skill, `du_lieu_test/`) giữ hành vi cũ.
- **Mã:** `so_nhap.ghi_so_nhap(..., luon_co_cot_w=False)` (mặc định = hành vi cũ; `True` thì `co_w` bật dù workspace tắt, trừ điểm theo người); `so_nhap.huong_dan(cfg, ghi_chu_cot_w)` thêm đoạn ghi chú trong sheet Hướng dẫn (chữ qua biến nhãn); `tao_so_nhap_mau` (`api_xuat.py`) và `mau_csv/tao_so_nhap.py` (mẫu trống và hai sổ `vi_du_*`) truyền `True`. Sinh lại ba sổ trong `mau_csv/`; các sổ trong `du_lieu_test/` (kịch bản đổi luôn chúng sang hai hàng) khôi phục bằng `git checkout`.
- **Khi tắt tính năng mà sổ có cột:** ô trống bỏ qua hoàn toàn; ô có số chỉ báo cảnh báo `csv_wp_bo_qua`, không chặn; không có dòng `wharton_bids`. `match_results` của sổ ví dụ trùng khít nạp bộ ba CSV cũ (seed 1, 7, 42).
- **Test mới (19 ca):** `tests/test_so_mau_co_cot_quyet_tam.py`.
- **Test cũ được sửa (Truong đã duyệt, 27/10/2026), chỉ hai kỳ vọng trong `tests/test_ws_so_nhap.py`:** `test_api_company_xuat_mau_roi_nap_lai` (hàng 1 của sổ mẫu là `["Nguyện vọng 1", None, None, "Nguyện vọng 2"]` thay vì `["Nguyện vọng 1", None, "Nguyện vọng 2"]`) và `test_api_mau_truong_hoc_giong_het_truoc_day` (`3 * 15` ô ở hàng 2 thay vì `2 * 15`). Lý do: đó đúng là thay đổi được chọn, sổ mẫu có ba cột mỗi nhóm. Không test nào bị `skip` hay nới.
- **Giao diện (`browser_host`):** workspace mặc định, bấm "Tải sổ nhập mẫu" ra sổ có cột ở 15/15 nhóm; nạp `vi_du_day_du` và chạy xếp xong, không lỗi JS.
- **Kiểm toàn bộ cho A13.6 và A13.7 (27/10/2026, Chromium thật, `-rs`):** 2.761 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), `ruff check .` sạch, độ phủ 92,37 % (CI đòi 85 %). Sau đó chỉ sửa chữ ở tài liệu; các test đọc CHANGELOG / TIEN_DO / sổ đăng ký / HUONG_DAN_SO_NHAP chạy lại (2.468 qua) và xanh.

## 2026-10-27 — A13.6 Dữ liệu mẫu có Điểm quyết tâm (vòng 6)

Thêm bộ sổ nhập mẫu có Điểm quyết tâm (trong mã: `wharton`, cột CSV `wp_k`), sinh lại được bằng một lệnh, và cho kỹ năng `sinh-du-lieu-clb` sinh điểm khi được yêu cầu. Mọi số liệu là dữ liệu MÔ PHỎNG. Không đổi thuật toán, schema, hợp đồng CSV, định dạng sổ; không thêm thư viện. Mặc định của kỹ năng (`--diem-quyet-tam khong`) cho đầu ra cũ từng ô.
- **Sáu tệp** trong `du_lieu_test/`: `SO_NHAP_DQT_{120HS,800HS}_{HOP_LE,CO_LOI,TRONG}.xlsx`. NHỎ (120 em, 3 buổi) giữ nguyên nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`; LỚN (800 em, 20 CLB, 4 buổi) sinh bằng `sinh_ngau_nhien` (seed 8002026). Điểm chia kiểu TRỘN (`don_dau`, `deu`, `all_in`, `ngau_nhien`; seed 27102026), làm tròn theo phần dư lớn nhất, hoà theo mã CLB.
- **`CO_LOI`:** năm loại lỗi (`thieu`, `thua`, `ngoai_nguyen_vong`, `tang_lech`, `toan_0`), 3 em mỗi loại ở bản nhỏ, 8 ở bản lớn, ghi trong `DQT_BANG_LOI.json` (kèm mã lỗi, quỹ, buổi mà bước Kiểm tra dữ liệu phải báo). Vì sổ chỉ có một ô điểm cạnh mỗi nguyện vọng và tầng do ô tick thi quyết định, `ngoai_nguyen_vong` thể hiện bằng điểm đặt cạnh ô nguyện vọng trống (phần mềm bỏ ô đó lúc nạp, quỹ còn thiếu) và `tang_lech` bằng một quỹ chung cho cả CLB có thi lẫn không thi của một buổi.
- **Kỹ năng:** `sinh_du_lieu.py` thêm `--diem-quyet-tam {khong,hop_le,co_loi,trong}`, `--kieu-chia {tron,don_dau,deu,all_in,ngau_nhien}` (cho `ngau`, `tao`), lệnh `ap` (áp điểm lên sổ có sẵn), `ap_diem_quyet_tam`, `soat_diem_quyet_tam` (`soat` tự soát hồ sơ điểm nếu sổ có điểm), `lam_tron_100`. Ghi sổ vẫn qua `so_nhap.ghi_so_nhap`. `SKILL.md` thêm mục "Điểm quyết tâm"; hai skill còn lại không đổi.
- **Script:** `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py` (sinh sáu tệp và hai JSON `DQT_BANG_LOI.json`, `DQT_KIEU_CHIA.json`).
- **Tài liệu:** `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md` (bản dán `SKILL.md` và mục 5.3b), `docs/ke_hoach/TIEN_DO.md`, mục A13 của `SO_DANG_KY_33_MUC.md`.
- **Test mới (43 ca):** `tests/test_du_lieu_mau_diem_quyet_tam.py` (nạp 6 tệp; HOP_LE chạy xếp ok, có điểm chuẩn, mọi quỹ đúng 100; CO_LOI bị chặn đúng em đúng loại; TRONG không có `wharton_bids`, tự điền như cũ, kiosk nhập được; tắt tính năng thì `match_results` trùng khít với cùng sổ bỏ cột điểm, seed 1, 7, 42 ở cỡ nhỏ và seed 42 ở cỡ lớn; bản nhỏ giữ nguyên nguyện vọng và điểm thi; sinh lại ra đúng nội dung ô; kỹ năng). Không sửa test cũ nào.
- **Thử qua giao diện:** nạp `SO_NHAP_DQT_120HS_HOP_LE.xlsx` bằng `browser_host`, bật tính năng, chạy xếp (88/120 em được xếp, seed 42), tab Điểm chuẩn có bảng và biểu đồ, không lỗi JS.
- **Kiểm toàn bộ (27/10/2026, Chromium thật):** lần chạy đầy đủ 2.741 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), 1 đỏ: `test_tai_lieu_du_lieu::test_toan_van_skill_md_con_dung` (bản dán `SKILL.md` trong `TAI_LIEU_DU_LIEU.md` thiếu mục mới). Đã sửa tài liệu, chạy lại bốn tệp liên quan (69 ca) xanh; chưa chạy lại toàn bộ sau sửa tài liệu. `ruff check .` sạch; độ phủ 92,34 % (CI đòi 85 %).

## 2026-10-27 — A13.5 Sửa 5 việc từ báo cáo đóng vai

Sửa các vấn đề #1 đến #5 của `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md` (#6, #7 để sau), cộng một lỗi chập chờn của vòng 4 và đóng vai lần 2. Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 5 (bất biến 1): 15 lần chạy (3 bộ dữ liệu x 5 seed, `PipelineAPI.run_pipeline`) so với bản `d85fe2c`, `match_results` từng dòng, `run_history.luat_xep` và mã băm dấu vân tay GIỐNG HỆT (chỉ cột thời điểm chạy `luc` khác, đúng bản chất); `TestTrungKhit` qua. Không đụng thuật toán, `api.py`, schema, STB, thứ tự 5 bước.
- **Lỗi chập chờn của vòng 4 (Bước 0b):** `test_tieng_anh_chu_cua_khoi_doi_theo_va_khong_con_chu_co_dau` hỏng 1/20 lần. Nguyên nhân: đổi ngôn ngữ thì khối Điểm quyết tâm ở tab Quản lý nạp lại qua nhiều lời gọi API, và chữ cũ còn trên màn hình tới khi từng lời gọi về. Nay khối giữ dữ liệu lần vẽ gần nhất (`whBoNho`) và vẽ lại ngay khi đổi ngôn ngữ (`veLaiWhTuBoNho`, `js/05_quan_ly.js`). Sau sửa: 20/20 xanh. Kiosk Bước 3 đã vẽ lại ngay từ trước.
- **#1 Lỗi chặn gọn (`js/02_van_hanh.js`):** khung lỗi chỉ còn một dòng tóm tắt (`wharton_tom_tat_chua_hop_le`), 5 em đầu (mỗi em một dòng gộp mọi lỗi), "và M ... khác" và nút "Mở danh sách cần xử lý" (sang tab con Điểm quyết tâm, bộ lọc "chỉ hồ sơ có vấn đề" đã bật). Bước "Kiểm tra dữ liệu" trong danh sách bước cũng chỉ còn câu tóm tắt (`chuLoiBuocGon`, phát hiện khi đóng vai). Hợp đồng `{ok, data, errors}` KHÔNG đổi (bất biến 6): backend vẫn trả đủ mọi lỗi; gộp theo em làm ở JS bằng `params.student_id`.
- **#2 Hai nút hàng loạt:** "Tải danh sách cần sửa" (`export_wharton_can_sua`, `api_xuat.py`: Excel gồm mã, họ tên, buổi, quỹ, tổng hiện tại, thiếu, thừa, câu lỗi; không đổi điểm nào) và "Phóng cho đủ 100 theo tỉ lệ" (`phong_wharton_hang_loat`, `api_quan_ly.py`). Hàm thuần `phong_theo_ti_le(diem, ngan_sach=100)`: làm tròn theo phần dư lớn nhất, hoà phần dư xét theo MÃ CLB tăng dần, không nhận thứ hạng nguyện vọng (bất biến 2), không phụ thuộc thứ tự dict, tổng 0 trả `None`. Phải gõ `PHONG`; sao lưu trước; mỗi em qua `_luu_wharton(..., "quan_ly")` nên có kiểm khoá, kiểm hồ sơ và nhật ký giá trị cũ / mới; em tổng 0 (`tong_0`) hoặc còn lỗi khác (`loi_khac`) được bỏ qua và liệt kê; đang khoá thì `wharton_da_khoa`.
- **#3 Tab con của tab Quản lý:** CLB · Học sinh · Điểm quyết tâm · Điểm chuẩn · Dữ liệu. Hai tab điểm chỉ hiện khi bật tính năng (tắt thì ba tab con, nội dung y như cũ). Nhớ tab đang mở bằng `localStorage` (có `try/catch`; không đọc được thì mở tab đầu); `role="tablist"` / `tab` / `tabpanel`, `aria-selected`, phím mũi tên, Home, End. Id phần tử bên trong giữ nguyên.
- **#4 Khoá xuất khi chưa có kết quả (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** `export_ket_qua` và `export_csv` từ chối với `xuat_chua_co_ket_qua` TRƯỚC khi tạo tệp (`_chua_co_ket_qua`, cùng phép đo với `get_trang_thai_ket_qua`); ô xuất kết quả ở thẻ Kết quả bị khoá kèm dòng vàng (`khoaXuatKetQua`). Xuất dữ liệu đầu vào, Sổ nhập mẫu và hồ sơ học sinh dùng như cũ.
- **#5 Thông báo (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** nguyên nhân thông báo "Xong: ..." sau khi nạp Sổ "không tự tắt": mã cũ ĐÃ tự đóng thông báo thường sau `min(10000, 4000 + 40 x độ dài)` ms (khoảng 7 giây; `test_giao_dien_chay` canh), không phải thiếu hẹn giờ. Điều người đóng vai thấy là thông báo nằm lại vài giây giữa các ảnh chụp và vùng thông báo ở góc trên phải đè lên tiêu đề trang. Quy tắc mới (`js/00_nen.js`, `style.css`): thành công tự đóng sau 6 giây, câu dài thêm thời gian, tối đa 10 giây; rê chuột hoặc có tiêu điểm thì tạm dừng đếm; lỗi và cảnh báo giữ tới khi bấm ×; thành công kèm cảnh báo (`opts.canhBao`) tách thành thông báo xanh tự đóng và thông báo vàng giữ; vùng thông báo ở góc dưới phải, không nhận chuột ngoài từng thông báo; `prefers-reduced-motion` bỏ hiệu ứng; `aria-live` `polite` cho thông báo thường và `assertive` kèm `role="alert"` cho lỗi. Chữ của thông báo không đổi.
- **Mã lỗi mới:** `xuat_chua_co_ket_qua`, `wharton_phong_sai_xac_nhan`, `wharton_da_phong`, `wharton_tom_tat_chua_hop_le` (thêm vào `MA_MOI_SAU_ANH_CHUP`, `tests/test_ws_nhan.py`).
- **Test mới (60 ca):** `test_wharton_hang_loat` (21), `test_giao_dien_thong_bao` (11), `test_giao_dien_quan_ly_tab_con` (9), `test_giao_dien_loi_chan_gon` (6), `test_xuat_khoa_chua_co_ket_qua` (6), `test_giao_dien_khoa_xuat` (5), cộng hai test đổi ngôn ngữ khi lời gọi API còn treo (`test_giao_dien_wharton_quan_ly`, `test_giao_dien_wharton`).
- **Test cũ đã sửa theo ngoại lệ:** thêm thao tác bấm sang đúng tab con ở `test_giao_dien_diem_chuan`, `test_giao_dien_wharton_quan_ly`, `test_giao_dien_diem_quyet_tam_gon`, `test_giao_dien_xoa_du_lieu`, `test_giao_dien_ux_xuat`, `test_giao_dien_xuat_du_lieu`, `test_giao_dien_doi_ngon_ngu`, `test_khoi_dong_backend`, `test_giao_dien_sua_loi_p1`; xuất kết quả khi chưa có kết quả: `test_so_excel_de_dung` (`test_chua_chay_thi_van_xuat_duoc` đổi thành kiểm bị từ chối; `test_qua_nhieu_clb_khong_vuot_gioi_han_ngat_trang_cua_excel` thêm một em và chạy xếp) và `test_giao_dien_chay` (`test_loi_goi_phan_loi_hien_cau_tieng_viet` chạy xếp trước khi bấm xuất). Không test nào bị `skip` hay nới.
- **Kiểm toàn bộ (27/10/2026):** 2.699 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng thường trên POSIX), không có test giao diện nào bị bỏ qua; `ruff` sạch; độ phủ 92,34 % (CI đòi 85 %).
- **Đóng vai lần 2** (có sửa mã với lỗi mức "chặn"): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`, mục "Lần 2 (27/10/2026)". Còn lại: #6, #7, biểu mẫu Google, mô phỏng VISEF, ngưỡng điểm tối thiểu, giải trình từng em.

## 2026-10-25 — A13.4 Giao diện Điểm quyết tâm và điểm chuẩn

Đổi tên hiển thị, đổi Sổ nhập sang hai hàng tiêu đề, thêm điểm chuẩn từng CLB (API, tab Kết quả, tab Quản lý, trang trong tệp xuất, ba biểu đồ SVG ngoại tuyến) và dọn gọn các màn của tính năng.
Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 4: 15 lần chạy (3 bộ dữ liệu x 5 seed) so từng dòng `match_results` GIỐNG HỆT bản `4c448ae`; sổ Excel kết quả so từng ô cũng giống hệt. Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Tên hiển thị (Điểm quyết tâm; trong mã: wharton):** tiếng Việt "Điểm quyết tâm", tiếng Anh "Preference points" ở `i18n.js`, `i18n_errors.py` (sinh lại `i18n_loi.js`), Sổ nhập, tệp xuất, `HUONG_DAN_SU_DUNG.md`. Giữ nguyên tên hàm, bảng, mã lỗi `wharton_*`, khoá `rules.wharton`, cột CSV `wp_k`, id HTML.
- **Sổ nhập hai hàng (đổi hợp đồng, bất biến 7):** sheet học sinh luôn có hai hàng tiêu đề (hàng 1 ô gộp "Nguyện vọng k"; hàng 2 "CLB", "Điểm thi", "Điểm quyết tâm" khi bật), cột đầu gộp dọc, dữ liệu từ hàng 3, sheet CLB một hàng. Nạp đọc ba dạng (một hàng cũ, một hàng có "Điểm W k", hai hàng), nhận dạng bằng hàng 1. Cột lệch nhóm báo `so_nhap_cot_lech_nhom` / `so_nhap_nhom_thieu_cot` (sheet, cột, nhóm) và không nạp gì. CSV không đổi. `so_nhap.py` vẫn chạy một mình. Sổ mẫu trong `mau_csv/` sinh lại; `du_lieu_test/` giữ nguyên dạng một hàng.
- **Ba skill** `sinh-du-lieu-clb`, `xu-li-raw-forms`, `tao-workspace-tu-raw`: cập nhật SKILL.md (script đã ghi sổ qua `so_nhap.ghi_so_nhap` nên tự theo bố cục mới); chạy thử sinh sổ 60 em rồi `import_so_nhap` thành công.
- **Điểm chuẩn:** `tinh_diem_chuan` (hàm thuần, ở `api_quan_ly.py`), API `get_diem_chuan` và `get_diem_chuan_clb` (chỉ quản trị; kiosk không có đường gọi), trang "Điểm chuẩn" trong sổ Excel kết quả (chỉ khi bật). Tầng 2: điểm hiệu lực thấp nhất đã được nhận; tầng 1: điểm thi thấp nhất kèm điểm quỹ 1 của em cuối; tách suất thường và suất dự trữ theo `matched_tier`; CLB còn chỗ ghi 0 kèm số chỗ còn.
- **Giao diện:** mục "Điểm chuẩn" ở tab Kết quả luôn đóng mỗi lần vào thẻ (không nhớ trạng thái); khối chi tiết ở tab Quản lý; ba biểu đồ SVG (cột phân bố, dải chấm, bảng tổng quan) chọn màu theo kỹ năng dataviz, có tiêu đề, chú giải, bảng chữ ẩn, không tải gì từ mạng. Dọn gọn: hai khung Bước 3 cạnh nhau (màn hẹp xếp dọc) kèm thanh tiến độ, ô sai tô màu và dòng lỗi tại chỗ, giải thích sau nút (i); khối Quản lý có mục "Thao tác khác" đóng sẵn (mở khoá, xem nhật ký, xoá tất cả), bộ lọc một hàng; công tắc workspace một dòng ngắn kèm nút (i).
- **Test mới (110 ca):** `test_diem_quyet_tam_chu` (18), `test_so_nhap_hai_hang` (20), `test_diem_chuan` (53), `test_giao_dien_diem_chuan` (11), `test_giao_dien_diem_quyet_tam_gon` (8).
- **Test cũ đã sửa theo ngoại lệ:** chữ "Wharton" trong `test_giao_dien_wharton.py`, `test_giao_dien_wharton_quan_ly.py`, `test_ws_wharton_giao_dien.py`; tiêu đề và toạ độ Sổ nhập một hàng trong `test_so_nhap.py`, `test_wharton_so_nhap.py`, `test_ws_so_nhap.py` (kèm làm mới bản chụp `tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json`: chỉ sheet học sinh và sheet hướng dẫn đổi, sheet CLB giống hệt), `test_ws_so_nhap_giao_dien.py`, `test_giao_dien_upload.py`. Ngoài ngoại lệ, buộc phải thêm bước "mở mục Thao tác khác" vào ba test của `test_giao_dien_wharton_quan_ly.py` (mục đóng sẵn theo yêu cầu thiết kế); `tests/test_ws_nhan.py` thêm hai mã mới vào danh sách cho phép.
- **Kiểm toàn bộ (27/10/2026):** lần chạy đầu 2.636 xanh, 3 đỏ, 3 bỏ qua; đã xử lý cả 3 (một câu `ORDER BY buoi` thiếu `COLLATE THU_TU_BUOI` ở `get_diem_chuan`; hai test cũ theo ngoại lệ: chữ "Wharton" trong `test_wharton.py` và tiêu đề Sổ một hàng trong `test_so_nhap.py`), chạy lại các tệp liên quan 288 ca xanh. Tổng sau sửa: 2.639 xanh, 3 bỏ qua (2 do thiếu `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 278 ca giao diện dùng Chromium thật), `ruff check .` sạch, độ phủ 92,42 % (sàn CI: 85 %), `TestTrungKhit` 7/7.
- **Đóng vai người dùng** (chỉ báo cáo, không sửa mã): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`.

## 2026-10-25 — A13.3 Quản lý điểm Wharton

Thêm khối **Điểm Wharton** vào thẻ Quản lý (chỉ hiện khi workspace bật `rules.wharton`): bảng điểm, sửa từng em, xoá, cảnh báo hồ sơ có vấn đề; kèm nhật ký và khoá riêng.
Tắt Wharton thì thẻ Quản lý, mọi API cũ, kết quả, dấu vân tay và `run_history` y hệt trước vòng 3 (bất biến 1). Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Quyết định đã chốt (25/10/2026):** (1) nhật ký mọi lần ghi hoặc xoá điểm: lúc nào, nguồn (`quan_ly`, `kiosk`, `nap_tep`, `xoa_du_lieu`, `he_thong`), tên tài khoản máy
  (`getpass.getuser()`, lỗi thì rỗng), giá trị cũ và mới; không bao giờ bị xoá hay ghi đè, kể cả `reset_data`. (2) Khoá Wharton RIÊNG (không dính STB): lần chạy xếp thành công
  khi Wharton bật tự khoá, kể cả chạy riêng một số buổi; đang khoá thì mọi cửa GHI điểm trả `wharton_da_khoa`; mở bằng `mo_khoa_wharton("MO")`. (3) Các cửa xoá dữ liệu
  vẫn chạy khi khoá nhưng ghi nhật ký; `reset_data` mở luôn khoá Wharton. (4) Chỉ hiện khi bật Wharton. (5) Màn dành cho quản trị. (6) Giữ STB; thứ tự 5 bước pipeline không đổi.
- **Sửa "cách A" (Bước 2, Truong đã duyệt):** `submit_wharton` chỉ ghi ô em đã GỬI (ô 100 tự điền chỉ có trong bộ nhớ), nên thêm CLB thứ hai vào quỹ đó sau này thì hồ sơ bị coi là
  chưa chia thay vì "hợp lệ" nhờ một ô em chưa từng đặt; cảnh báo sau khi nạp tệp (`_soat_ho_so_wharton`) cũng tự điền trong bộ nhớ như pipeline và báo cáo sức khoẻ dữ liệu.
- **Hai bảng mới** trong `DEFAULT_SCHEMA` (chỉ `CREATE TABLE IF NOT EXISTS`, không vào `_BANG_RANG_BUOC`; `di_tru_schema` chạy lặp an toàn): `wharton_nhat_ky(id, luc, nguon, nguoi, hanh_dong, student_id, cu_json, moi_json)`,
  không khoá ngoại, `nguon` bị CHECK; `wharton_lock(id = 1, is_locked, locked_at, unlocked_at)`. Không câu `DELETE` / `UPDATE` nào chạm nhật ký.
- **API mới** (`api_quan_ly.py`): `list_wharton_admin`, `list_wharton_canh_bao`, `get_wharton_nhat_ky`, `admin_save_wharton` (dùng lại lõi `_luu_wharton` với `submit_wharton`), `clear_wharton`
  (một em, hoặc tất cả khi gõ `XOA`, có sao lưu), `mo_khoa_wharton`, `get_wharton_lock_status`; `get_student_entry_state` có thêm cờ `khoa` trong khoá `wharton`. `_ho_so_wharton_tat_ca` là MỘT hàm đọc
  một lần, dùng chung cho bảng điểm, danh sách cảnh báo và `get_data_health_report` (số liệu báo cáo không đổi).
- **Cửa có nhật ký:** `submit_wharton` (`kiosk` / `luu`), `admin_save_wharton` (`quan_ly` / `luu`), nạp tệp kể cả Sổ nhập (`nap_tep` / `luu`), tỉa trong `submit_preferences` (`kiosk` / `tia_nguyen_vong`),
  `reset_student_entry` (`kiosk` / `xoa_mot_em`), `delete_student` (`quan_ly` / `xoa_mot_em`), `delete_club` (`quan_ly` / `xoa_theo_clb`, mỗi em một dòng), `reset_data` (`xoa_du_lieu` / `xoa_tat_ca`, một dòng tổng),
  `clear_wharton`, khoá sau khi chạy (`he_thong` / `khoa`) và mở khoá (`mo_khoa`). Nhật ký nằm trong CÙNG giao dịch với thao tác. Cửa ghi có kiểm khoá trong giao dịch ghi: `submit_wharton`, `admin_save_wharton`,
  `clear_wharton`, nạp cột `wp_*` (nguyện vọng vẫn nạp, phần điểm bị bỏ kèm cảnh báo `wharton_da_khoa`).
- **Pipeline** (`api.py`, chỉ bước 5/6): đặt khoá trong cùng giao dịch ghi `run_history` khi Wharton bật; thứ tự năm bước không đổi; khoá và nhật ký không vào dấu vân tay.
- **Giao diện:** `js/04_nhap_tai_cho.js` tách `whartonVeKhung` / `whartonThuThapTu` / `whartonChuoiTu` / `whartonGiuTamTu` dùng chung (hành vi kiosk không đổi) và Bước 3 chỉ đọc khi khoá;
  `js/05_quan_ly.js` khối mới (bảng, lọc, phân trang, cảnh báo, màn sửa, nhật ký, hộp xác nhận `MO` / `XOA`); `index.html`, `style.css`, `i18n.js` (vi/en).
- **Mã lỗi** (`i18n_errors.py` rồi `python tao_i18n_js.py`, `i18n_loi.js` chỉ thêm dòng): `wharton_da_khoa`, `wharton_mo_khoa_sai_xac_nhan`, `wharton_xoa_sai_xac_nhan`, `wharton_da_xoa`,
  `wharton_da_mo_khoa`, `error_wharton_quan_ly`; thêm vào `MA_MOI_SAU_ANH_CHUP` của `tests/test_ws_nhan.py`.
- **Test cũ đã sửa theo ngoại lệ A.3:** `tests/test_wharton_kiosk.py::test_tu_dien_khi_quy_chi_co_mot_clb` (ô tự điền không còn được ghi, Bước 2) và
  `tests/test_wharton_kiosk.py::test_bat_wharton_trang_thai_co_khoa_wharton_dung_dang` (khoá `khoa` do vòng này cố ý thêm). `tests/test_ws_nhan.py`: chỉ thêm 6 mã vào danh sách cho phép.
- **Test mới (141 ca):** `test_wharton_cach_a` (6), `test_wharton_nhat_ky` (22), `test_wharton_khoa` (21), `test_wharton_quan_ly` (23), `test_wharton_quan_ly_ghi` (21),
  `test_wharton_quan_ly_dau_cuoi` (1), `test_giao_dien_wharton_quan_ly` (10, Chromium thật), cộng 37 ca vòng 3 trong `test_wharton_ma_loi`.
- **Trùng khít (bất biến 1):** Wharton tắt: 15 lần chạy `run_pipeline` (3 bộ trong `du_lieu_test/do_anh_huong_seed.BO_DU_LIEU` × seed 1, 7, 42, 3, 11) cho `match_results` đầy đủ cột (1.350 dòng),
  `dau_van_tay_chay` và `run_history.luat_xep` GIỐNG HỆT bản chụp lấy trước khi sửa (đỉnh vòng 2, `a8b077d`); `tests/test_nhieu_buoi.py::TestTrungKhit` 7/7 xanh. Toàn bộ: 2.529 ca xanh, 3 ca bỏ qua (2 do thiếu
  `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 212 ca giao diện chạy bằng Chromium thật), `ruff check .` sạch, độ phủ 92,34 % (sàn của CI: 85 %). Một ca trợ năng
  (`test_giao_dien_tro_nang::test_moi_o_nhap_deu_co_ten_doc_duoc`) bắt được hai ô gõ chữ xác nhận thiếu tên đọc được; đã sửa bằng `aria-label` qua `i18n.js`.
- **Cần biết:** ở màn (kiosk và thẻ Quản lý) khung chỉ có một CLB tự điền 100 và khoá ô; giao diện gửi cả ô đó khi bấm Lưu nên server GHI ô đó (đúng với "ô người dùng gửi thì được ghi"). Cách A (không ghi ô tự điền)
  vì vậy giữ trọn với gọi API trực tiếp, nạp tệp và Sổ nhập; đường bấm Lưu trên giao diện vẫn ghi ô 100 như vòng 2 (`js/04_nhap_tai_cho.js` ngoài phạm vi vòng này để sửa phần thu thập).


## 2026-10-25 — A13 Điểm Wharton: pipeline tự điền quỹ một CLB trong bộ nhớ (theo quyết định của Truong, cách A)

Quỹ (mỗi buổi) chỉ có MỘT CLB mà em chưa đặt điểm: lúc chạy xếp và lúc lập báo cáo sức khoẻ dữ liệu, `api.py` gọi `tu_dien_wharton_mot_clb`
trong bộ nhớ TRƯỚC `kiem_ho_so_wharton` / `diem_wharton_hieu_luc`. Không ghi `wharton_bids`; kết quả vẫn tất định (hàm thuần của nguyện vọng,
ô tick và điểm đã lưu, đều nằm trong dấu vân tay). Quỹ đã có khoá (kể cả 0) hoặc có từ hai CLB mà chưa chia thì vẫn bị chặn. Tắt Wharton: không đổi.
Test mới (5 ca, trong `tests/test_wharton_pipeline.py`): chạy được khi chưa lưu, CSDL không đổi, bằng kết quả khi đã lưu 100, không che lỗi thật,
sức khoẻ dữ liệu cùng cách tính. Sửa mục 14 của `HUONG_DAN_SU_DUNG.md` cho khớp.

## 2026-10-24 — A13 Điểm Wharton (vòng 2: lưu trữ, nhập liệu, kiosk, pipeline)

Làm tiếp mục A13 theo quyết định của Truong: chỉ bật được khi `priority` là `score` / `score+tier` và `score_scope` là
`per_slot`; hồ sơ Wharton sai CHẶN cả lần chạy ở bước Kiểm tra dữ liệu, trước khi bốc hay khoá STB; nhập bằng tệp (CSV, Sổ
nhập) và bằng một màn kiosk; lưu tầng lúc nhập; mặc định **TẮT** — mọi hành vi, tệp, dấu vân tay và kết quả giống hệt trước
vòng 2 (bất biến 1). Giữ STB (không SHA-256, không `public_value`; bất biến 3 nguyên). Mọi số liệu trong test là dữ liệu
MÔ PHỎNG. Ghi hợp đồng cột vào sổ đăng ký TRƯỚC khi làm (bất biến 7).
- **Bảng `wharton_bids(student_id, club_id, tier, points)`** trong `DEFAULT_SCHEMA` (khoá chính `(student_id, club_id)`, `tier IN (1, 2)`,
  `points >= 0`, khoá ngoại tới `students`, `clubs`); bảng mới hoàn toàn nên chỉ cần `CREATE TABLE IF NOT EXISTS`, không vào
  `_BANG_RANG_BUOC`. `tier` = quỹ lúc NỘP (1 = lúc ghi em đang tick thi CLB đó). Đổi ô tick sau khi chia điểm thì hồ sơ thành chưa
  hợp lệ (`wharton_ngoai_tap`); phần mềm KHÔNG tự chuyển điểm sang quỹ kia. Dọn ở mọi cửa xoá: `delete_student`, `delete_club`,
  `reset_student_entry`, `reset_data` (`_RESET_BANG`), `submit_preferences` (bỏ CLB thì xoá điểm CLB đó), `seed_sample_data`; nạp CSV
  nguyện vọng cũng dọn dòng của CLB bị bỏ.
- **Thay đổi hợp đồng cột (bất biến 7), chỉ khi workspace bật Wharton:** CSV nguyện vọng thêm `wp_k` đi cặp `pref_k`, `<buoi>_wp_k`
  đi cặp `<buoi>_pref_k`, và cột `wp` cho dạng dài (ghép theo HẬU TỐ SỐ, không theo vị trí); Sổ nhập thêm cột "Điểm W k" ngay sau
  "Điểm k" (kèm kiểm số nguyên ở Excel, màu riêng, đoạn hướng dẫn hai quỹ). Tệp không có các cột này nạp như cũ; chưa bật mà có thì bỏ
  qua kèm `csv_wp_bo_qua`. Xuất "dữ liệu đầu vào" ra Sổ nhập có cột W khi bật; nạp lại ra `wharton_bids` giống hệt.
- **Khoá luật `rules.wharton`** (bool, mặc định `False`): `cau_hinh_ws` từ chối tổ hợp khác; `LUAT_XEP_MAC_DINH["wharton"]`, `dung_wharton`.
  Khoá `wharton` chỉ vào chuỗi ghi `run_history.luat_xep` và phần băm dấu vân tay khi BẬT (`_luat_de_ghi_hoac_bam`), nên workspace
  tuỳ biến cũ giữ nguyên từng byte. Dấu vân tay có thêm bảng `wharton_bids` khi bật.
- **Đọc dữ liệu:** `doc_du_lieu_wharton`, `load_from_sqlite_kem_dau_van_tay_wharton` (dữ liệu, dấu vân tay và Wharton trong MỘT giao
  dịch đọc); `_doc_du_lieu`, `load_from_sqlite_kem_dau_van_tay` giữ nguyên chữ ký và giá trị trả về.
- **API kiosk:** `submit_wharton(student_id, w1, w2)` (kiểm ở server theo V6: tự điền một CLB → `kiem_ho_so_wharton` → thay toàn bộ dòng
  của em; hồ sơ sai thì không ghi gì và trả đúng danh sách lỗi); `get_student_entry_state` có thêm khoá `wharton` CHỈ khi bật (tắt thì
  y hệt trước).
- **Nối pipeline** (`_run_pipeline_da_khoa`, chỉ bước 2 và 4): bước Kiểm tra dữ liệu đọc bằng bản có Wharton, chạy `kiem_ho_so_wharton` và
  `diem_wharton_hieu_luc` NGAY SAU `validate_data_integrity` — trước soát buổi, bốc, khoá STB; có lỗi (mọi mã trừ `wharton_vang_thi`) thì
  trả `wharton_ho_so_chua_hop_le` cùng đủ lỗi, không vẽ số, không ghi, không thêm dòng `run_history`. Vắng thi chỉ là cảnh báo trong chi
  tiết bước validate. Bước 4 truyền `diem_wharton` cho `run_rbda_nhieu_buoi`. Thứ tự năm bước giữ nguyên.
- **Sức khoẻ dữ liệu:** `health_wharton_chua_hop_le` (mức high) và `health_wharton_vang_thi` (mức medium), chỉ khi bật, đặt sau các mục sẵn có.
- **Giao diện:** ô "Dùng điểm Wharton" ở bước luật của trình hướng dẫn workspace (khoá và tự bỏ chọn khi không dùng được) và hàng tóm tắt
  `rvWharton`; màn "Bước 3. Điểm Wharton" ở tab Nhập tại chỗ (hai khung mỗi buổi, bộ đếm "Đã dùng X / 100", tự điền và khoá khung một CLB,
  "Cần chia lại điểm" khi lệch tier, vẽ lại sau khi lưu Bước 1 / 2, chung cơ chế "chưa lưu"; học sinh chỉ thấy điểm của chính mình).
- **Mã lỗi song ngữ (8):** `csv_wp_khong_hop_le`, `csv_wp_khong_co_nguyen_vong`, `csv_wp_bo_qua`, `wharton_chua_bat`,
  `wharton_ho_so_chua_hop_le`, `health_wharton_chua_hop_le`, `health_wharton_vang_thi`, `error_saving_wharton`; `i18n_loi.js` sinh lại, chỉ thêm dòng.
- **Test mới: 252 ca** (viết trước, thấy đỏ rồi mới viết mã): `test_wharton_luu_tru` (21), `test_wharton_luat` (30), `test_wharton_doc` (15),
  `test_wharton_ma_loi` (56), `test_wharton_nhap` (24), `test_wharton_so_nhap` (23), `test_wharton_kiosk` (29), `test_wharton_pipeline` (24),
  `test_wharton_suc_khoe` (6), `test_wharton_dau_cuoi` (1), `test_ws_wharton_giao_dien` (9), `test_giao_dien_wharton` (14). Bản chụp mốc
  `tests/du_lieu_ws/wharton_moc_truoc_vong2.json` (`match_results`, `dau_van_tay_chay`, `luat_xep` của 3 bộ × 3 seed, chụp bằng mã TRƯỚC
  vòng 2) được so trong `test_wharton_pipeline`. Đã thử phá hoại có chủ đích (bỏ truyền `diem_wharton` ở bước 4): bị bắt.
- **Xác nhận.** Tắt Wharton: giống hệt mốc (810 dòng `match_results`, dấu vân tay, `luat_xep`); `TestTrungKhit` 7/7. Toàn bộ test (kèm Chromium
  thật): 2.383 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng không phải root), 0 đỏ; `ruff check .` 0 lỗi; độ phủ 92,43 % (sàn 85 %).
- **Chỗ lệch yêu cầu, có lý do.** (1) Câu chữ màn kiosk không dùng "bạn" ("Các CLB bạn đã thi" thành "Các {slot_sl} đã thi") vì
  `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong mọi chuỗi giao diện; câu báo lỗi vẫn là "Chưa dùng hết điểm Wharton…".
  (2) `{detail}` của `error_saving_wharton` không nằm trong câu (test văn phong cấm); `format_message` tự thêm chi tiết ở cuối như các mã
  `error_*` khác. (3) `tests/test_ws_nhan.py`: chỉ THÊM 8 mã mới vào `MA_MOI_SAU_ANH_CHUP` (test đó tự quy định cách này; ngoại lệ "wharton: False"
  của luật KHÔNG phải dùng cho test nào). (4) `get_student_entry_state` có thêm `tu_dien_mot_clb` và `ds_buoi` trong khoá `wharton`.
  (5) Khoá `wharton` chỉ được ghi vào `luat_xep` / băm khi bật, để bất biến 1 đúng cả với workspace tuỳ biến cũ.
- **Việc sau:** cập nhật ba skill trong `.claude/skills/` (sinh dữ liệu, xử lí raw forms, tạo workspace) cho cột mới; biểu mẫu Google hai khung;
  mô phỏng VISEF; ngưỡng điểm tối thiểu; công bố điểm chuẩn; giải trình từng em (C3). Điểm cần Truong quyết: em có quỹ chỉ một CLB mà chưa
  bấm Lưu ở kiosk thì lần chạy bị chặn (màn kiosk tự điền 100 nhưng chưa ghi) — có muốn tự điền ngay trong pipeline không.

## 2026-10-24 — A13 Điểm Wharton (vòng 1: lõi thuật toán và test)

Mục mới A13 trong sổ đăng ký (`docs/ke_hoach/`), làm theo quyết định của Truong ngày 24/10: **giữ nguyên STB**
(bộ số đã khoá, chế độ `stb_ngay`, cách chèn em đến muộn), điểm Wharton xét **TRƯỚC** STB, mỗi quỹ **100 điểm
MỖI BUỔI**, vòng này **chỉ làm lõi thuật toán, test, mã lỗi và tài liệu sổ**. Không đổi schema, `api*.py`, sổ nhập,
giao diện hay `compute_club_priority` (không đổi một ký tự). Mọi số liệu dưới đây là dữ liệu MÔ PHỎNG.
- **Cơ chế.** Mỗi học sinh có hai quỹ cho mỗi buổi: quỹ 1 chia cho CLB có thi (chỉ phá hoà khi bằng điểm thi),
  quỹ 2 chia cho CLB không thi (tiêu chí chính tầng 2). Khoá ưu tiên: tầng 1 `(0, -điểm thi, (), -w1, stb, mã)`,
  tầng 2 `(1, -w2, stb, mã)`; `()` là chỗ dành cho tiêu chí phụ của mục A1. Gale–Shapley vẫn chạy MỘT lần cho cả
  hai tầng; thứ hạng nguyện vọng không vào khoá.
- **Hàm mới** (`rbda_priority_pipeline.py`, khối `BƯỚC A2` L252–L574): `khoa_uu_tien_wharton`, `uu_tien_wharton`
  (hàm bọc như `uu_tien_theo_nhom`, nhận `tier_rank`), `kiem_ho_so_wharton` (V1–V5, theo từng buổi, trả đủ mọi
  lỗi theo thứ tự cố định), `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc` (lúc khoá: vắng thi rơi xuống tầng
  2, T2 chuyển lên T1 là lỗi); ba hằng `WHARTON_NGAN_SACH = 100`, `WHARTON_TU_DIEN_MOT_CLB = True`,
  `WHARTON_VANG_THI = "tier2_zero_points"` (hai hằng sau chờ chủ dự án quyết).
- **Hai tham số mới**, mặc định `None` = hành vi cũ: `diem_wharton` của `run_rbda` (thay NGUỒN `base_rank`; dự
  trữ mềm, `verify_stability` giữ nguyên) và của `run_rbda_nhieu_buoi` (chuyển nguyên cho mọi buổi).
- **7 mã lỗi song ngữ** trong `i18n_errors.py` (`wharton_nguyen_vong_chua_xep`, `wharton_chua_dung_het`,
  `wharton_vuot_ngan_sach`, `wharton_diem_khong_hop_le`, `wharton_ngoai_tap`, `wharton_tang_lech`,
  `wharton_vang_thi`); `i18n_loi.js` sinh lại bằng `tao_i18n_js.py`, chỉ thêm 28 dòng. Câu chữ dùng chỗ giữ nhãn
  workspace (`{person}`, `{slot_sl}`, `{session_l}`…), không viết cứng "học sinh" / "CLB".
- **Test mới.** Phần hàm và mã lỗi viết trước, thấy đỏ rồi mới viết mã; nhóm test tính chất viết sau, trên mã đã
  xong, đúng theo đặc tả của bước đó. `tests/test_wharton.py`, 144 ca: khoá ưu tiên và W1, W3;
  hàm bọc (200 bộ ngẫu nhiên: bằng điểm Wharton thì y hệt `compute_club_priority` / `uu_tien_theo_nhom`); VD1–VD5
  qua `run_rbda`, W7, mặc định `None` trùng khít trên 30 bộ, và hai buổi khớp `run_rbda` chạy riêng; mã lỗi;
  `kiem_ho_so_wharton` (W5, 32 ca); `tu_dien_wharton_mot_clb`; `diem_wharton_hieu_luc` (VD6, W4); VD1–VD5 đi từ
  `w1`/`w2` thô (W9); test tính chất: W1 (hoán vị nguyện vọng không đổi `base_rank`), W2, W6 (50 bộ một buổi có
  dự trữ / nhóm xếp cứng + bốn cấu hình nhiều buổi), W8 (mọi hoán vị nguyện vọng của từng em trên 15 bộ nhỏ,
  không hoán vị nào cho CLB tốt hơn kết quả thật). Thử phá hoại có chủ đích: đổi dấu `w1`, đặt STB trước Wharton ở
  tầng 2, bỏ qua `diem_wharton` trong `run_rbda`, xác định tầng bằng "điểm > 0" — cả bốn đều bị bắt.
  `tests/test_ws_nhan.py`: chỉ THÊM 7 mã vào `MA_MOI_SAU_ANH_CHUP` (cách test đó quy định).
- **Bất biến.** Bất biến 1: `TestTrungKhit` 7/7 qua, cùng test mặc định `None` trùng khít. Bất biến 8: test thay
  thế được và luật tổng cầu (400 nhóm ứng viên, thứ tự nền của `uu_tien_wharton` + dự trữ mềm, có và không
  `tier_rank`) qua. Toàn bộ test: 1.923 qua, 211 bỏ qua do máy không tìm thấy Chromium (trình trợ giúp tìm
  `chrome-linux/chrome`, bản cài sẵn nằm ở `chrome-linux64/chrome`); chạy riêng 28 tệp giao diện với
  `RBDA_TEST_CHROMIUM` đặt tay: 253 qua, 0 bỏ qua. `ruff check .` 0 lỗi (mốc 0); độ phủ 92,11 % (sàn 85 %).
- **Chỗ cố ý lệch đặc tả.** (1) Điểm thi giữ `float`, không đổi `Decimal`: so `float` cho cùng thứ tự với
  `Decimal(str(x))` và điểm đọc thẳng từ cột REAL (ghi trong docstring). (2) Không có `round_id`, không làm số bốc
  SHA-256 / `public_value` (giữ STB). (3) Câu `wharton_chua_dung_het` mở đầu "Chưa dùng hết điểm Wharton…", không
  phải "Bạn chưa dùng hết…": `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong câu báo lỗi. (4) Câu
  `wharton_nguyen_vong_chua_xep` dùng `{session_l}` thay chữ "buổi" viết cứng, để workspace gọi là "ca" cũng đúng.
  (5) `kiem_ho_so_wharton` có thêm tham số tuỳ chọn `tran_nguyen_vong` (mặc định `TRAN_NGUYEN_VONG_MOI_BUOI`) vì
  workspace có thể đặt trần khác. (6) Mỗi ô điểm có tối đa một lỗi: khoá ngoài tập chỉ báo `wharton_ngoai_tap`.
  (7) W2 chỉ kiểm khi không dự trữ và không nhóm xếp cứng: có dự trữ thì em tầng 2 đủ diện dự trữ được giữ suất
  trước em tầng 1, có `tier_rank` thì nhóm đứng trước cả tầng — đo thử trên dữ liệu mô phỏng thấy đúng như vậy; đó
  là đặc tính cũ của dự trữ và nhóm, không do A13. Hai chế độ ấy được canh bằng W6 (ổn định).
- **Rủi ro đã ghi trong sổ.** "Khai thật là tốt nhất" chỉ được bảo đảm với THỨ TỰ nguyện vọng (W8), KHÔNG với
  cách chia điểm Wharton: người biết tính có thể lợi hơn người ngây thơ; cần đo bằng mô phỏng.
- **Việc vòng sau** (chưa làm): bảng `wharton_bids`; cột CSV / Sổ nhập (đổi hợp đồng cột, bất biến 7); nối
  pipeline (kiểm hồ sơ ở bước "kiểm dữ liệu", TRƯỚC khoá STB; thứ tự tự điền → kiểm hồ sơ → khoá STB → điểm hiệu
  lực → chạy); khoá luật workspace; biểu mẫu hai khung "Đã dùng X / 100"; mô phỏng VISEF; ngưỡng điểm tối thiểu;
  công bố điểm chuẩn.

## 2026-10-15 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

Ở giao diện tiếng Việt, màn chọn workspace còn "workspace" và ".zip" lẫn trong câu, và bảng bị vỡ.
Giao diện tiếng Anh giữ nguyên chữ cũ. Không đổi backend, thuật toán hay hợp đồng `{ok, data, errors}`.
- **Chữ tiếng Việt.** "workspace" → "không gian làm việc"; ".zip" → "tệp nén" (nút Xuất tệp nén / Nhập tệp nén,
  câu nhắc, thông báo). Sửa trong `i18n.js` (khối `vi`, các khoá `ws_*`), `i18n_errors.py` (sáu mã `ws_*` và bốn
  câu có "Workspace này"), `index.html` (chữ mặc định của nút thanh bên); `i18n_loi.js` sinh lại bằng
  `tao_i18n_js.py`. "thư mục _trash" giữ nguyên vì là tên thư mục thật trên đĩa.
- **Chuỗi do backend đặt, không đổi theo ngôn ngữ.** Tên mẫu dựng sẵn "Trường học" nay dịch ở JS theo khoá mới
  `ws_mau_truong_hoc` (vi "Trường học", en "School"); cột "Sửa lần cuối" hiện `15/10/2026 12:19:20` ở tiếng Việt,
  giữ `2026-10-15 12:19:20` ở tiếng Anh (`js/075_workspace.js`: `wsTenMau`, `wsDinhDangNgay`).
- **Bảng.** `display:flex` đặt thẳng lên `<td>` làm ô mất kiểu `table-cell`: nền hàng "Đang mở" dừng giữa chừng,
  đường kẻ lệch, nút Xoá rớt dòng. Nay `<td class="ws-cot-hanh-dong">` chứa `<div class="ws-hanh-dong">` (flex);
  hộp thoại rộng 1040px; cột Tên về font chữ thường (trước đó dùng font mã của `.data-table td:first-child`);
  `select` / `textarea` trong trình hướng dẫn kế thừa font. Màn hẹp thì sáu nút xuống dòng gọn trong ô.
- **Test mới (viết trước, thấy đỏ rồi mới sửa).** `tests/test_giao_dien_tieng_viet_sach.py`: thêm "workspace" vào
  danh sách cấm và một test quét thô chữ "zip". `tests/test_ws_giao_dien.py`: tiếng Việt không còn
  workspace/zip ở màn chọn và cả bốn bước hướng dẫn; tiếng Anh không còn chữ có dấu tiếng Việt ở màn chọn và ba
  bước đầu; tên mẫu và ngày đổi theo ngôn ngữ; bảng vẽ đúng (ô hành động là `table-cell`, mọi ô cao bằng hàng,
  sáu nút một dòng, nền phủ cả hàng, tên không dùng font mã).
- **Ảnh chụp chuỗi làm mới có chủ đích.** `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json`: chỉ 24 chuỗi `vi` đã đổi
  (5 mã lỗi `ws_*`, 19 khoá `ws_*` của giao diện); `test_ws_nhan.py` vẫn so toàn bộ phần còn lại như cũ.

## 2026-10-15 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

- **Skill mới `.claude/skills/tao-workspace-tu-raw/`**: raw bất kỳ (Excel/CSV tự do, Google/Microsoft Forms, hai
  tệp tách rời, văn bản dán) → workspace `.zip` nạp sẵn dữ liệu + Sổ nhập theo nhãn + `BAO_CAO_SOAT.md`.
  Bốn dạng nguyện vọng (`cot_xep_hang`, `mot_o`, `dong_dai`, `ma_tran`), đủ luật workspace, điểm theo chỗ / theo
  người. Đoán rồi hỏi duyệt; chỉ tiêu bắt buộc hỏi; sai một điều không ghi tệp nào; kiểm bằng `import_so_nhap` +
  báo cáo sức khoẻ + chạy thử; từ chối ghi đầu ra vào kho git (dữ liệu người thật). Không đụng mã sản phẩm.
  Test: `tests/test_skill_tao_workspace.py` (21 ca).
- **Bộ dữ liệu thử (mô phỏng)**: `du_lieu_test/bo_thu_chuong_trinh/` (trường 3 buổi, 180 học sinh) và
  `du_lieu_test/bo_thu_workspace/` (workspace "Công ty Bình Minh", zip nạp sẵn, kèm script sinh lại).

## 2026-10-14 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)

Bộ test Windows đỏ 24 ca trong khi Linux xanh. Hai nguyên nhân, một thật của sản phẩm và một của test:
- **Lỗi sản phẩm — `connect_db` rò kết nối khi tệp không phải SQLite.** PRAGMA đầu tiên ném mà kết nối chưa
  được đóng. Trên Linux không ai hay; trên Windows tệp đang mở không dời / xoá / đổi tên được (WinError 32 / 5),
  nên **xoá một workspace hỏng, nhập zip có `app.db` hỏng (thư mục tạm không dọn được), di trú `app.db` cũ hỏng**
  đều hỏng đúng lúc người dùng cần. Nay `connect_db` đóng kết nối rồi mới ném lại. Bộ dò
  `tests/test_ws_ket_noi_dong.py` bắt lỗi kiểu này NGAY TRÊN LINUX (kết nối bị huỷ mà chưa `close()`), và phủ các
  đường workspace / zip / di trú / chạy xếp. Vì sao Linux không thấy: kết nối sqlite3 của CPython 3.11 nằm trong vòng
  tham chiếu vòng (bộ nhớ đệm câu lệnh) nên chỉ nhả tệp khi GC chạy.
- **Lỗi của test.** (1) `with sqlite3.connect(db) as c` chỉ commit, KHÔNG đóng — các helper của
  `test_ws_registry.py` / `test_ws_sua_loi_3.py` nay dùng `contextlib.closing`. (2) Tiến trình con của
  `test_tham_khao_verify_nhanh.py` in tiếng Việt ra cp1252 nên `UnicodeEncodeError`: nay chạy `python -X utf8` và
  đọc đầu ra bằng UTF-8 (tái hiện được trên Linux bằng `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`: 33 ca đỏ
  trước, 0 sau). (3) So đường dẫn bằng `'/'` ghép tay: dùng `os.path.join`. (4) `write_text` / `open(..., "w")` thiếu
  `encoding="utf-8"` với nội dung tiếng Việt.

## 2026-10-14 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)

Mỗi mục có test trong `tests/test_ws_sua_loi_3.py` (viết trước, đỏ trước khi sửa):
- **Đọc cấu hình NGHIÊM ở nơi quyết định.** `run_pipeline`, `check_data_integrity`, trần nguyện vọng / thi
  (nhập tay, CSV, sổ), chấm điểm theo CLB đọc bằng `doc_cau_hinh(nghiem=True)` (`PipelineAPI._luat_nghiem`).
  Cấu hình có mà đọc không được (JSON hỏng, khoá của bản khác, CSDL bị khoá) thì dừng với lỗi mới
  `ws_cau_hinh_hong`, không lặng lẽ chạy bằng luật trường học rồi ghi `luat_xep = NULL`. `get_data_health_report`
  vẫn trả báo cáo nhưng thêm cảnh báo mức cao. `run_pipeline` đọc cấu hình MỘT lần (trước: hai lần, hai kết
  nối). Không có hàng cấu hình = mặc định, như cũ.
- `workspace.nhap_zip`: cấu hình trong zip đọc không được thì từ chối cả zip (trước: ghi mặc định đè lên luật thật).
- `update_workspace_config`: cập nhật MỘT PHẦN giữ nguyên phần không nhắc tới (`cau_hinh_ws.tron_len`); trước
  đây trộn lên mặc định trường học nên `{"name": "X"}` đặt lại mọi luật. Cấu hình cũ hỏng thì từ chối.
- `reset_student_entry` ("Sửa lại từ đầu") KHÔNG xoá `diem_ca_nhan` nữa (điểm do giáo viên chấm, không gắn
  với ô tick). *Đổi hành vi so với bản trước; test cũ đổi theo.*
- `delete_workspace` trên workspace "mở tạm" chuyển `db_path` sang workspace còn lại (không để trỏ vào `_trash`).
- `submit_club_scores` từ chối (`scoring_not_per_slot`) khi workspace chấm theo người hoặc `priority = tier`;
  CSV có điểm ở các chế độ đó: không lưu, cảnh báo `csv_score_ignored_mode`.
- Dấu vân tay kết quả, `run_history.luat_xep` và `run_full_pipeline` dùng luật HIỆU LỰC
  (`luat_xep_hieu_luc`): danh sách nhóm khi nhóm không cứng, `score_scope` khi chỉ theo nhóm... không còn
  làm kết quả báo "cũ". Luật mặc định không đổi (vân tay cũ giữ nguyên).
- Sổ nhập: cột điểm sai kiểu chấm (cột "Điểm k" ở workspace chấm theo người, hoặc cột "Điểm" đơn ở workspace
  chấm theo CLB) mà có dữ liệu thì báo `so_nhap_diem_sai_che_do` (trước: bỏ lặng lẽ, điểm mất).
- `xuat_zip` không nén chính zip đích (nằm trong thư mục workspace) và bỏ mọi `*.zip` trong thư mục.
- `main.khoi_dong_workspace`: bỏ qua workspace hỏng khi còn workspace lành (không còn rơi vào màn phục hồi vì một
  workspace hỏng); chỉ khi không cái nào mở được mới ném `WorkspaceKhoiDongHong(db_path)` cho màn phục hồi. Màn
  phục hồi dùng đúng tệp hỏng, hoặc workspace gần nhất khi `app.db` cũ đã di trú (trước: trỏ vào `app.db` không
  còn, "bắt đầu lại" đẻ ra tệp mồ côi).
- Nhóm cứng: nhập CSV không còn cảnh báo `csv_reserve_group_unknown` cho tên nhóm.
- Dọn: bỏ `main.chon_db_path` (chỉ test dùng) và khoá `bo_diem` của `tham_so_luat` (không ai đọc); tên trang
  Excel của tệp xuất dùng chung `so_nhap._ten_sheet`; docstring `cau_hinh_ws.py` nói đúng việc cấu hình
  nối vào thuật toán.
- `docs/ke_hoach/TIEN_DO.md`: thêm hàng WS (ngoài sổ) và ghi chú chồng lấn ở Z1, Z2 (chưa đóng mục).
- Hai việc còn lại sau vòng này (cùng ngày):
  - Mã lỗi riêng `ws_cau_hinh_hong` ở MỌI chỗ phụ thuộc cấu hình (trước chỉ ở chạy xếp / kiểm tra dữ liệu / báo
    cáo sức khoẻ; còn lại ra lỗi chung): nhập tay nguyện vọng và thi, nhập CSV, chấm điểm theo CLB và theo
    người, đọc / xem trước sổ nhập, tạo sổ mẫu, xuất dữ liệu đầu vào, hồ sơ học sinh, trạng thái kết quả. Bố
    cục sổ và tệp xuất cũng đọc cấu hình NGHIÊM (trước: đoán bằng mặc định trường học). Nhãn hiển thị vẫn
    đọc dễ tính. Test: `tests/test_ws_sua_loi_3.py` (mục P).
  - Màn phục hồi lúc khởi động được kiểm bằng `main.main()` thật và Chromium thật
    (`tests/test_ws_phuc_hoi.py`): đúng tệp hỏng trong thư mục workspace, thấy bản sao lưu cạnh nó, bấm
    "Khôi phục" đưa workspace về đúng dữ liệu, lần khởi động sau vào giao diện chính, và lỗi không nêu tệp thì
    dùng workspace gần nhất chứ không phải `app.db` cũ đã di trú.

## 2026-10-14 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)

Ghép `practical-faraday` (nền), `cool-hamilton` (tài liệu) và `upbeat-ride` vào nhánh này; bản workspace
cũ của nhánh còn ở `backup/nifty-truoc-khi-ghep`. Sửa các lỗi còn lại, mỗi lỗi một test
(`tests/test_ws_sua_loi_2.py`):
- `workspace.xoa`: workspace có `app.db` hỏng vẫn xoá được (sao lưu rơi về chép tệp thô, rồi dời vào `_trash`).
- `workspace.nhap_zip`: trần 500 MB giải nén cho cả zip, đếm BYTE THẬT khi chép (tiêu đề zip khai sao cũng
  được); bỏ `app.db-journal/-wal/-shm` và `*.bak-*` trong zip (SQLite tự phát lại nhật ký có sẵn); từ chối mục mã hoá.
- Slug: cắt ở 60 ký tự; `con`, `nul`, `com1`... (tên thiết bị Windows) thành `ws-<tên>`.
- `delete_workspace`: workspace "mở tạm" lúc khởi động nhiều workspace (người dùng chưa chọn) xoá được.
- `run_history.luat_xep` (cột mới, `ADD COLUMN`, không dựng lại bảng): JSON luật xếp đã dùng; NULL = luật mặc
  định của trường học (dòng cũ và workspace mặc định không đổi). `get_run_history` trả cột này.
- `run_full_pipeline` (đường thử nghiệm) từ chối chạy khi workspace có luật khác mặc định, thay vì xếp sai
  âm thầm.
- Nhãn workspace bắt đầu bằng `=`, `+`, `-`, `@` bị từ chối (`cau_hinh_ws.chuan_hoa`): nhãn thành tiêu đề cột / tên
  sheet của Sổ nhập, và openpyxl ghi `=...` thành ô công thức thật; nhãn có thể đến từ zip nhập vào. Cấu hình
  như thế đọc lại ra mặc định.
- Test giao diện `test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa` hết chập chờn: `#lastRunLine` và
  `#statStudents` do hai lời gọi API riêng điền, test từng assert ngay mà không chờ. Nay chờ `#lastRunLine`, và
  làm chậm `get_last_run_info` 600 ms để thứ tự trả về là chắc chắn (bản assert ngay đỏ ổn định với độ trễ này).
- `docs/ke_hoach/tham_khao`: `verify_stability_nhanh` nhận `bo_qua_du_tru`; bộ nạp `_chung.nap_rb` nạp thêm
  `nhan_ws` (từ bản có workspace, `i18n_errors` import nó), bản build cũ không có thì vẫn nạp được.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

- Không sửa hành vi. Ba điểm "móc lỗi chặn cả `import json`" là đúng hành vi: tệp `json.py` cạnh mã vẫn che được
  `json`, và lần chạy thật (thư mục đứng đầu sys.path) cũng hỏng ở chính móc đó — sai là ở LỜI: dòng CHANGELOG
  vòng R và chú thích test ghi "thư viện chuẩn" thay vì "dựng sẵn / đóng băng". Đã sửa lời (đánh dấu tại chỗ),
  docstring `_tu_thu_muc` (dòng tóm tắt còn ghi "nghi ngờ thì coi là có"), và thêm ca `import json` bị từ chối
  vào test làm chốt (228 ca, 2 bỏ qua tuỳ môi trường).
- `_khong_the_bi_che` nhớ theo tên (`functools.cache`).
- Bác: tên đã có trong `sys.modules` của tiến trình đo — `sys.modules` của lần chạy thật là của tiến trình khác;
  chỉ đáng kể khi có móc đường dẫn hỏng, đã báo lỗi rõ.
- Vòng lặp 2 dừng tại đây theo tiêu chí "một vòng không còn lỗi đúng/sai được xác nhận".

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)

Không điểm nào làm phép đo chạy nhầm mã; đều là chẩn đoán, độ chặt của test và một ca từ chối thừa hiếm gặp.
- `_chung`: lỗi khi xét một tên (móc đường dẫn hỏng với thư mục, lỗi trong bộ tìm / PathFinder) -> SystemExit nêu
  đúng tên và lỗi gốc, thay vì báo nhầm thành "mô-đun anh em"; lỗi móc với thư mục chỉ nêu khi thật sự cần xét
  một tên (mã chỉ import mô-đun dựng sẵn / đóng băng không bị chặn; *sửa ở vòng S: bản đầu ghi nhầm
  "thư viện chuẩn"*).
- Luật "dựng sẵn / đóng băng không bị che" còn một chỗ, đứng trước phép xét thư mục trong `la_ten`.
- Test (227 ca, 2 bỏ qua tuỳ môi trường): bộ tìm cài thêm ghi mọi tên ngoài thư viện chuẩn (không chỉ hai tên);
  ca lỗi PathFinder kiểm cả lỗi gốc và đặt mục lỗi cuối sys.path; 1 ca mới. 3 ca thất bại với bản vòng Q.
- Bác: PathFinder chạy các móc đường dẫn trên sys.path khi xét phần namespace — đó chính là việc mọi import của
  mã được đo làm trong cùng tiến trình; docstring ghi rõ điều này.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)

- `_chung`: mô-đun dựng sẵn / đóng băng ngoài `sys.stdlib_module_names` (`__phello__`, `xxsubtype`) lại được nhận
  (hồi quy của vòng P: bỏ ngoại lệ của vòng O mà không thay bằng `_khong_the_bi_che`).
- Móc đường dẫn ném lỗi khác ImportError với thư mục đã chọn -> SystemExit rõ (PathFinder cũng chỉ bỏ qua
  ImportError); mọi lỗi khi tìm phần namespace (kể cả PathFinder trên sys.path) -> coi là có, từ chối rõ — không
  còn traceback. Không móc nào nhận thư mục -> trả ngay hàm luôn "không".
- Test (226 ca, 2 bỏ qua tuỳ môi trường): 3 ca mới, đều thất bại với bản vòng P (đã kiểm là lỗi thật, không phải
  lỗi cú pháp của mã test); bộ tìm cài thêm trong test chỉ ghi tên đang xét (không bắt nhầm import khác);
  `_chay_tien_trinh_moi` nối mã test sau một dòng mới (mã bắt đầu bằng `def` / `try` không còn thành lỗi cú pháp
  lặng lẽ).
- Bác:
  - Không dùng `sys.path_importer_cache[thu_muc]` của tiến trình đo: lần chạy thật là một tiến trình khác, bộ
    nhớ đệm trống, dựng bộ tìm từ `sys.path_hooks` — đúng như kịch bản làm.
  - Mô-đun đóng băng ở tiến trình đo nhưng không đóng băng ở lần chạy thật với cờ / bản Python khác: như vòng O —
    phép đo chạy trong chính trình thông dịch này, đối chiếu là nạp bình thường trong cùng trình thông dịch.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)

- `_chung`: **rút lại** việc hỏi các bộ tìm cài thêm trong `sys.meta_path` (vòng O). Đã tái hiện: hỏi
  `DistutilsMetaFinder` của setuptools về `distutils` / `pip` làm đổi trạng thái tiến trình đo; một bộ tìm chuyển
  tiếp cho PathFinder (kiểu móc của pytest / typeguard) làm tệp `pytest.py` cạnh mã lọt qua — lần chạy thật thư
  mục đứng đầu sys.path nên chính bộ tìm đó trả tệp cạnh mã (đo nhầm mã, lặng lẽ).
- Luật mới, bảo thủ (nghi ngờ thì từ chối rõ, không bao giờ đo nhầm): chỉ mô-đun dựng sẵn / đóng băng (hai bộ
  tìm của CPython, không tác dụng phụ) được coi là không thể bị che; bộ tìm của thư mục dựng từ `sys.path_hooks`
  như PathFinder làm (móc đường dẫn kiểu Hy thêm đuôi mới cũng được tính), lỗi khi tìm thì coi là có; phần
  namespace chỉ được nhận khi PathFinder trên sys.path tìm được mô-đun / gói thường. Tên do bộ tìm cài thêm cung
  cấp mà thư mục cũng có thì bị từ chối (ca `hookmod/` của vòng O đổi từ "nhận" sang "từ chối, không gọi bộ tìm").
- Một hàm phân loại duy nhất (`_tu_thu_muc`, nhớ theo tên); bỏ `_bo_tim_truoc_cung_cap` và lần gọi lặp trong
  `la_ten`.
- Test (223 ca, 2 bỏ qua tuỳ môi trường): ca bộ tìm cài thêm của vòng O thay bằng 2 ca bảo thủ (kèm kiểm bộ tìm
  không bị gọi lần nào) + 1 ca `sys.path_hooks`; cả 3 thất bại với bản vòng O.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)

- `_chung`: sửa tận gốc luật mô-đun anh em — bỏ các luật tự bắt chước hệ thống import (`_anh_em`,
  `_nap_truoc_filefinder`, `_mo_dun_thuong_ngoai`; bốn vòng K–N mỗi vòng lại thấy một chỗ lệch) và hỏi chính các
  bộ tìm theo đúng thứ tự import: bộ tìm trong `sys.meta_path` đứng trước PathFinder (dựng sẵn, đóng băng, móc
  cài thêm) → FileFinder của thư mục đã chọn → PathFinder trên sys.path (gói thường thắng phần namespace).
  Không gọi PathFinder với thư mục đã chọn (giữ sys.path_importer_cache sạch); kết quả nhớ theo tên trong một lần nạp.
- Tên do bộ tìm đứng trước PathFinder cung cấp được nhận (vòng N từ chối nhầm khi có thư mục dữ liệu cùng tên).
- Docstring `_import_la` theo luật mới. Test dựng sẵn / đóng băng bỏ qua trên trình thông dịch không đóng băng `os`.
- Test (221 ca, 2 bỏ qua tuỳ môi trường): 1 ca mới thất bại với bản vòng N; mọi ca của vòng K–N vẫn qua với
  cách làm mới (lưới hồi quy cho lần viết lại).
- Bác:
  - Tệp cạnh mã trùng tên mô-đun đóng băng trên một trình thông dịch KHÁC (phiên bản cũ, `-X frozen_modules=off`):
    kịch bản đo chạy mã trong chính trình thông dịch đang chạy; đối chiếu là nạp bình thường trong cùng trình
    thông dịch đó, không phải một bản Python khác.
  - Thư mục hiện hành nằm trên sys.path của tiến trình kiểm (`python -m`, pytest) che phần namespace: cách chạy
    ghi trong CLAUDE.md (`python <kịch bản> <thư mục>`) không đưa thư mục hiện hành vào sys.path; tình huống cần
    hai bản kho mã lệch nhau ở đúng một tên — xa thực tế, không đáng thêm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)

- `_chung` (luật mô-đun anh em): mô-đun dựng sẵn / đóng băng (`time`, `os`…) xét TRƯỚC — BuiltinImporter /
  FrozenImporter chạy trước FileFinder nên tệp cùng tên cạnh mã không che được (vòng M từ chối nhầm). Thư mục
  không `__init__` cạnh mã chỉ được nhận khi tên là mô-đun / gói THƯỜNG trên sys.path (PathFinder); gói
  namespace đã cài thì thư mục được gộp vào (`nsgoi.helper` chạy thật lấy từ thư mục) — từ chối (vòng M nhận nhầm).
- Docstring `_import_la` theo luật hiện hành; `importlib.machinery.all_suffixes()`; `with os.scandir(...)`.
- Test (220 ca, 1 bỏ qua khi chạy bằng root): 2 ca mới, đều thất bại với bản vòng M.
- Bác, kèm đường đã lần:
  - Thoát tiến trình qua bí danh (`_s.exit`, `from os import _exit`, `os.abort`) và nhánh except ghi bằng
    thuộc tính / biến bộ (`except errors.ImportError`, `except _LOI`): luật import tuỳ chọn chỉ còn áp cho tên
    KHÔNG có trong thư mục; với tên đó, chạy thật và chạy dưới kịch bản tìm trên cùng sys.path nên hành xử
    giống nhau — sai ở đây chỉ làm thông báo lỗi muộn hơn, không làm phép đo đo nhầm mã. Theo dõi bí danh tốn
    mã hơn lợi ích.
  - Thư mục dữ liệu namespace (vd `mau_csv/`) trong try/except ImportError vẫn bị từ chối: chạy thật gán một
    gói namespace rỗng, dưới kịch bản gán None — hai lần chạy đi hai nhánh khác nhau, từ chối là đúng.
  - Chi phí stat cho mỗi thư mục con: vài chục lần stat mỗi lần nạp, không đáng kể.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)

- `_chung` (luật mô-đun anh em) bám đúng FileFinder: tính cả bản biên dịch không nguồn (`.pyc`); tên tệp là
  phần trước ĐÚNG đuôi (tệp `random.old.py` không phải `random`); thư mục không có `__init__` chỉ là phần gói
  namespace — không che thư viện chuẩn / gói đã cài, chỉ bị coi là anh em khi tên không có ở đâu khác (vòng L
  từ chối nhầm mã hợp lệ khi có thư mục dữ liệu tên `random/`, `csv/`...).
- Import tuỳ chọn: thân lớp chạy ngay nên được đường lui che (vòng L từ chối nhầm); xét nhánh except ĐẦU TIÊN
  bắt được ImportError theo thứ tự (kể cả `except Exception`), nhánh kết thúc bằng ném lại hay
  `sys.exit` / `os._exit` / `exit` / `quit` không phải đường lui. Điều kiện động (`if STRICT: raise`) không xét
  được tĩnh — coi là đường lui, ghi trong docstring.
- Chỉ kiểm / biên dịch các mô-đun CÒN THIẾU (i18n_errors đã nạp đúng bản thì không đọc lại), dựng đủ rồi mới
  gán. Spec không có bộ nạp và `cached = None` (vòng L chỉ đặt `__cached__`, `__spec__` vẫn trỏ .pyc và
  `importlib.reload` đi vòng qua phép kiểm). `functools.cache` thay danh sách tự chế.
- Test (218 ca, 1 bỏ qua khi chạy bằng root): 8 ca mới thất bại với bản vòng L (ca gói thường `random/__init__.py` đã đúng từ vòng L, giữ
  làm chốt chặn khi thu hẹp luật thư mục).
- Bác: nhãn "ngoài sổ" trái quy tắc 1 của CLAUDE.md — quy tắc cho phép khi đã hỏi; việc này do Truong (chủ dự
  án) yêu cầu trực tiếp, nhãn ghi đúng điều đó.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)

- `_chung` (kiểm import): thêm luật **mô-đun anh em** — tên có mặt trong thư mục đã chọn (tệp .py, mô-đun mở
  rộng, thư mục) mà không được phép thì luôn bị từ chối, kể cả nằm trong `try/except ImportError` hay trùng tên
  gói đã cài (vòng K để lọt: `try: import rbda_priority_pipeline` trong i18n_errors; tệp `openpyxl.py` cạnh mã).
  Import tuỳ chọn chỉ được che khi nằm trực tiếp trong khối try (không vào thân hàm / lớp định nghĩa ở đó) và
  nhánh except không chỉ ném lại; nhận cả `except*`. Danh sách gói đã cài quét một lần, chỉ khi cần.
- Kiểm và biên dịch CẢ HAI tệp trước khi chạy tệp nào (vòng K chạy i18n_errors rồi mới đọc mô-đun chính).
  Thông báo nêu đúng tệp được import gì (i18n_errors: không mô-đun nào của kho mã, vì nó nạp trước).
- `__cached__ = None` (không trỏ tới .pyc không tồn tại); `compile(..., dont_inherit=True)`.
- Test (209 ca): khôi phục test "không thêm mục cache bộ tìm" (bỏ ở vòng K là sai: nó chặn hồi quy kiểu chèn
  tạm sys.path); 9 ca mới, đều thất bại với bản vòng K.
- Bác phần còn lại của điểm 6 (không dùng bộ nhớ đệm .pyc): cố ý từ vòng H–I (bản .pyc cũ từng bị dùng nhầm);
  phân tích + biên dịch mô-đun chính tốn ~46 ms mỗi tiến trình, không đáng kể so với phép đo.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)

- `_chung` (kiểm import tĩnh của vòng J): nhận cả gói đã cài trong site-packages (theo `importlib.metadata.packages_distributions`) — vòng J đã thu hẹp quá mức mà CHANGELOG không ghi; bỏ qua import tuỳ chọn trong khối `try/except ImportError`; `i18n_errors` (nạp trước) không được import `rbda_priority_pipeline` (sẽ lấy nhầm bản khác); import tương đối báo đúng tên mô-đun (`.helpers`, không phải `.helpers.f`); bỏ điều kiện thừa `__future__`.
- Kiểm và biên dịch NGAY LÚC NẠP từ đúng bản đã đọc (`compile(cây ast)` rồi `exec`): không còn khe giữa lúc kiểm và lúc chạy; lỗi đọc / cú pháp / byte NUL thành SystemExit rõ; đã nạp đúng thư mục thì trả bản đã nạp mà không đọc lại tệp.
- Test (199 ca): bỏ test cache không thể thất bại (vòng J); 5 test mới, đều thất bại với bản vòng J.
- Bác: một tệp tên trùng thư viện chuẩn (vd `random.py`) chen trên sys.path — mối nguy chung của mọi chương trình Python, ngoài phạm vi kịch bản; phép kiểm theo đường dẫn của vòng I từng có báo nhầm nặng hơn.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)

- `_chung`: đính chính vòng I — phép kiểm "mô-đun anh em" chạy SAU khi nạp nên bỏ lọt import bên trong hàm (đúng kiểu import của mã này; đã tái hiện), từ chối nhầm mô-đun C của thư viện chuẩn trên Windows (`<base>\DLLs`), không dùng tham số `thu_muc`, và để lại mô-đun lạ trong sys.modules. Thay bằng kiểm TĨNH trước khi chạy gì: đọc cả hai tệp nguồn bằng `ast`, lấy mọi import (đầu tệp lẫn trong hàm, kể cả import tương đối) và từ chối tên không thuộc `sys.stdlib_module_names` hay `i18n_errors` / `rbda_priority_pipeline`. Bỏ `_thu_muc_chuan`, `_phu_thuoc_la` (không còn đoán theo đường dẫn, không còn sysconfig). Hai tệp thật của kho qua kiểm (không import lạ).
- Test (195 ca): 4 ca import lạ (đầu tệp, trong hàm, anh em ngay thư mục chọn, import tương đối — đều thất bại với bản vòng I) và kiểm không mô-đun nào bị nạp; 1 ca nhận mô-đun C của thư viện chuẩn; 1 ca thư mục chưa có mục cache vẫn không có sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)

- `_chung.nap_rb` (thư mục), sửa tận gốc theo điểm "sai tầng": bỏ hẳn cơ chế đoán tệp Python sẽ nạp (`sys.path_hooks`, bộ tìm riêng, các ca .so / gói / namespace — thêm dần từ vòng C tới H). Nay nạp THẲNG `<thư mục>/<tên>.py` bằng `spec_from_file_location`: bản biên dịch cũ, gói cùng tên, gói namespace nằm cạnh không thể chen vào; không đụng sys.path hay cache bộ tìm; không còn đường lỗi traceback từ bộ tìm hay loader cũ. Đổi hành vi có chủ đích: thư mục chỉ có bản biên dịch không kèm nguồn (.pyc) nay bị TỪ CHỐI (kịch bản đo mã nguồn) — đảo lại phần nhận .pyc của vòng C–D.
- Mới: nếu mã được nạp import thêm mô-đun ngoài thư viện chuẩn / site-packages (vd một phiên bản khác import mô-đun anh em, lấy nhầm từ thư mục khác trên sys.path), từ chối thay vì đo lẫn mã. Mã hiện tại chỉ import thư viện chuẩn và `i18n_errors` (đã kiểm).
- Test (190 ca): viết lại nhóm test bộ nạp thư mục theo thiết kế mới (8 test thất bại với bản vòng H vì hành vi đổi có chủ đích hoặc vì mô-đun anh em trước đây lọt).
- Bác: khoá import và "đọc lại sys.modules sau exec" của bộ import — kịch bản chạy một luồng, và `_nap_co_kiem` đã kiểm nguồn của mục sys.modules sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)

- `_chung.nap_rb` (thư mục), sửa tận gốc: không còn import theo tên qua sys.path nữa. Hỏi bộ tìm mà CHÍNH Python dùng (gọi `sys.path_hooks` như PathFinder, kể cả hook tuỳ biến, nhưng tạo mới và không ghi cache) lấy spec cho từng mô-đun, rồi nạp ĐÚNG spec đó (`module_from_spec` + `exec_module`, đặt vào sys.modules trước như import). Hệ quả: dự đoán và lần nạp thật không thể lệch; bỏ toàn bộ phần sửa / khôi phục sys.path và `sys.path_importer_cache` (vòng G bỏ sót bước xoá mục cũ trước khi import nên có thể đi qua bộ tìm cũ hoặc mục None — đã tái hiện bằng test); thư mục mất quyền giữa chừng vẫn báo lỗi đọc.
- Test (193 ca): test cache tự gieo mục sẵn có (không còn đúng vô nghĩa khi cache trống); test thư mục đã ở trên sys.path với mục cache cũ None (thất bại với bản vòng G).

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)

- `_chung`: đính chính vòng F — `nap_rb` vẫn để lại bộ tìm tệp của thư mục trong `sys.path_importer_cache` (vòng F chỉ dọn ở `_tep_se_nap`; đã tái hiện). Nay `_tep_se_nap` dùng một `FileFinder` RIÊNG (cùng thứ tự loại tệp như mặc định) nên không đụng cache toàn cục, và bước import của `nap_rb` trả mục cache về như cũ (không để lại cho thư mục tạm, không thay bộ tìm sẵn có). Kiểm đọc được thư mục bằng `os.scandir` (rẻ); lỗi OSError khi tìm thành SystemExit; docstring nói rõ thư mục không có `<tên>.py` thì nhận đúng thứ Python nạp.
- Test (192 ca): test chmod 000 thật (bỏ qua khi chạy root hay Windows; CI Linux chạy được); `.pyc` trong `__pycache__` bỏ qua khi `cache_tag` là None; 2 test cache bộ tìm (thất bại với bản vòng F); test giả lập lỗi quyền đổi sang `os.scandir` (thất bại với bản vòng F chỉ vì vòng F dùng `os.listdir`).
- Bác: thư mục chỉ có gói `rbda_priority_pipeline/__init__.py` (không có `.py`) được nhận — đúng ý: đó là mã Python sẽ chạy khi import từ thư mục đó; docstring đã ghi rõ.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)

Không điểm nào làm phép đo sai; đều là thông báo lỗi và độ vững của test.
- `_chung._tep_se_nap`: thư mục không đọc được báo đúng "Không đọc được thư mục" (FileFinder nuốt lỗi quyền rồi trả None nên trước đây báo nhầm "không có mô-đun"); tạo bộ tìm tệp mới mỗi lần và không để lại trong `sys.path_importer_cache`; thông báo nêu cả khả năng "gói cùng tên nằm cạnh". `nap_rb` kiểm mô-đun chính trước, nên thư mục sai báo thiếu `rbda_priority_pipeline`.
- Test (190 ca): test `__pycache__` ghi .pyc vào đúng chỗ và kiểm là có (không thành vô nghĩa khi đặt PYTHONPYCACHEPREFIX); 4 test mới, đều thất bại với bản vòng E.
- Bác: gọi `nap_rb` lần hai trên cùng thư mục sau khi tệp trong đó đổi giữa chừng thì bị từ chối — chỉ là từ chối (đòi tiến trình mới), không bao giờ đo nhầm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)

- `_chung.nap_rb`, sửa tận gốc: bỏ các luật đoán theo tên tệp (`_co_mo_dun`, phần tiền tố của `_cung_nguon`); hỏi chính bộ import của Python (`importlib.machinery.PathFinder.find_spec`) tệp nào sẽ được nạp từ thư mục, rồi đòi đúng tệp đó sau khi nạp. Hệ quả: .pyc có thẻ trong `__pycache__` (Python không nạp) và hậu tố mở rộng của hệ khác không còn bị nhận nhầm; thư mục chỉ có `__pycache__` báo SystemExit rõ thay vì traceback; bản mở rộng cũ chen trước tệp nguồn vẫn bị từ chối; gói namespace bị chặn ngay ở bước kiểm trước (không phụ thuộc sys.path của máy); thông báo nêu đúng tệp mong đợi; lỗi đọc thư mục thành SystemExit; thông báo "đã nạp nơi khác" nêu nguồn thật (gói namespace, mục None).
- Test (186 ca): 2 test cho hàm mới `_tep_se_nap` (thất bại với bản vòng D chỉ vì hàm chưa có) và 1 test hành vi qua `nap_rb` (thất bại thật với bản vòng D).
- Bác: điểm cũ float và điểm mới Decimal cùng giá trị bị coi là "đổi" — giữ, vì đổi kiểu có thể đổi thứ hạng thật: `Decimal('7.1') > 7.1` (float 7.1 là 7,0999…), nên từ chối là đúng.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)

- `_chung.nap_rb`: sửa lỗi do vòng C đưa vào — khi thư mục CÓ `<tên>.py`, chỉ nhận đúng tệp đó; một bản biên dịch cũ (.so/.pyd) nằm cạnh mà Python ưu tiên nạp trước bị từ chối (trước đây vòng C nhận nó và đo nhầm mã cũ). Bản biên dịch không kèm nguồn chỉ được nhận khi KHÔNG có .py, nay cho cả mô-đun chính; gói namespace chen vào được nêu đúng nơi (thay vì "None").
- `exp_resume.kiem_tien_de`: nhận điểm Decimal (không là numbers.Real); chỉ kiểm điểm của dữ liệu mới (điểm em cũ đã phải bằng hệt dữ liệu cũ).
- Test (184 ca): bỏ test tiền đề không có khẳng định (luôn xanh), giữ lý do thành chú thích; 4 test mới, đều thất bại với bản vòng C.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)

- `exp_resume.kiem_tien_de`: một luật `_so_hop_le` cho mọi số mà `compute_club_priority` sắp (số bốc thăm và điểm): điểm là chuỗi CSV, None, bool, pd.NA hay NaN đều bị từ chối bằng ValueError rõ (trước đây chuỗi / None lọt kiểm rồi gây TypeError giữa `resume_da` — đã tái hiện).
- `_chung.nap_rb`: nhận bản biên dịch không kèm nguồn (`i18n_errors.pyc` trong đúng thư mục) thay vì báo "nạp nhầm"; thông báo lỗi sau khi nạp nêu đúng nguồn thực và nguồn mong đợi.
- Test (181 ca): test tiền đề về NaN chuyển thành tự bỏ qua nếu sau này mã sản phẩm xử lý NaN xác định (không chặn bản sửa đúng); thêm 8 ca điểm không hợp lệ (2 ca NaN thất bại với bản vòng B chỉ vì đổi thông báo lỗi; 6 ca chuỗi / None / bool là lỗi thật) và 1 ca `.pyc`.
- Hồ sơ: đính chính câu "6 test mới đều thất bại" của vòng B; cập nhật ngày ở TIEN_DO.md.
- Bác: từ chối NaN cả ở điểm không ảnh hưởng thứ hạng (em không có trong apps, điểm nhập trước của em mới) — giữ, vì thận trọng: chỉ tốn một lần chạy lại toàn bộ, không bao giờ cho kết quả sai.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)

- `_chung.nap_rb`: kiểm SAU khi nạp rằng mỗi mô-đun đến đúng từ thư mục / bản build đã chọn — thư mục thiếu `i18n_errors.py` trước đây lặng lẽ lấy tệp cùng tên ở chỗ khác trên sys.path (đã tái hiện), nay từ chối và gỡ mô-đun; mục sys.modules không rõ nguồn (None, mô-đun giả) báo rõ; tệp build không chứa mô-đun cần thiết báo SystemExit thay vì KeyError.
- `exp_resume.kiem_tien_de`: TỪ CHỐI điểm NaN (cả em cũ lẫn em mới) — `compute_club_priority` cho thứ tự phụ thuộc thứ tự đầu vào khi có NaN (đã tái hiện), nên vòng A coi NaN == NaN là sai; chưa nạp mô-đun rbda là RuntimeError (lỗi cài đặt, để người gọi bắt ValueError rồi chạy lại toàn bộ không nuốt mất).
- Test (174 ca): 7 test mới — 6 thất bại với bản vòng A; 1 là test tiền đề chỉ chạy mã sản phẩm (`compute_club_priority` với NaN) nên không phân biệt hai bản (đính chính ở vòng C).
- Bác: (1) em mới đã có trong apps/điểm của dữ liệu cũ làm `resume_da` lệch — thử 5.000 thể hiện ngẫu nhiên có trường hợp này: 0 lệch; (2) bản nhanh gọi `club_choice_function` một lần mỗi CLB làm chậm — đo 10.000 HS: 0,037 s so với 0,034 s, không đáng kể so với giá trị (khớp mọi kiểm tra đầu vào của bản gốc).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)

Quyết định của Truong: KHÔNG sửa mã sản phẩm (phân xử em không có thứ hạng trong `club_choice_function` vẫn hoãn); lặp tới khi một vòng không còn lỗi đúng đắn.
- `exp_resume.kiem_tien_de`: mọi vi phạm là ValueError (kể cả chưa nạp rbda); bỏ em mới ở CẢ dữ liệu cũ khi so điểm / apps (điểm nhập trước cho em đến muộn không còn báo nhầm "em cũ đổi"); nhóm dự trữ '' và None coi như một (như `default_reserve_eligible_fn`); điểm NaN không đổi không bị báo đổi; kiểm thứ tự bốc thăm sắp một lần; `resume_test` dùng bản rbda đã nạp.
- `de_xuat_verify_nhanh.py`: lần đầu xét mỗi CLB, gọi đúng lời gọi `club_choice_function` của bản gốc (đang giữ + ứng viên, hàm đủ tư cách và thứ hạng thật) — mọi kiểm tra đầu vào, hiện tại và sau này, chạy y hệt.
- `_chung.py`: một hàm `_nap_co_kiem` cho cả thư mục lẫn bản build (kiểm "đã nạp nơi khác", trả bản đã nạp, gỡ mô-đun dở dang); thư mục lấy theo đường dẫn người dùng đưa (không theo đích liên kết); đường dẫn không tồn tại báo rõ; đọc được tệp PyInstaller < 6 (mục `PYZ-00.pyz`, mục lục dict).
- Test (169 ca): 7 test mới, đều thất bại với bản trước; chuỗi so lỗi chính xác ("thứ tự bốc thăm"); đường dẫn Windows dự phòng thật sự viết khác.
- Bác: gộp đoạn mồi 4 dòng (lý do như trước); thay `compute_club_priority` bằng chèn bisect trong `resume_da` (ghi ở DOI_CHIEU, để khi làm G1); sửa phân xử trong `club_choice_function` (chủ dự án hoãn).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)

- `exp_resume.kiem_tien_de`: số bốc thăm phải là số thực (không chuỗi CSV, không bool, không NaN) — báo ValueError rõ; kiểm sức chứa dùng bản rbda đã nạp kể cả khi `exp_resume.rb` chưa gán (trước đây lặng lẽ bỏ qua).
- `_chung.nap_rb`: so đường dẫn như hệ điều hành (liên kết, hoa/thường Windows) khi nạp lại cùng .exe; nhánh thư mục nạp hỏng cũng gỡ mô-đun dở dang như nhánh bản build.
- Test (162 ca): lần đầu có test cho đường nạp `.exe` (tệp PyInstaller tối thiểu dựng trong test): nạp, nạp lại qua đường dẫn khác, nạp hỏng không để mô-đun dở dang, lệch phiên bản Python; danh sách cấm cả `.index`/`.count`; dùng đúng một bản `_chung` trong tiến trình; sửa chú thích sai (v + 20).
- Bác một phần: kiểm sức chứa trong `kiem_tien_de` lặp lại luật của `club_choice_function` — giữ, vì cần nêu tên CLB trước khi làm việc và chỉ tốn một lần gọi mỗi CLB.

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).
