# Mảnh B — FA-M9 (nạp tệp Forms / List) + FA-M10 (nút sau khi xếp) — A gộp vào CHANGELOG / TIEN_DO / hướng dẫn ở Phase 3

TH = CHƯA thử trên Microsoft thật. Mọi số liệu trong test là MÔ PHỎNG. (Phần FA-M10 ở cuối tệp.)

## CHANGELOG (văn bản mục)
**FA-M9 — Nạp tệp Forms / List ngay trong phần mềm (thẻ "Chuẩn bị đợt", bước 4).**
- `api_forms_nap.py` (`FormsNapMixin`): `nhan_dien_tep_forms(files)` phân loại từng tệp (đăng ký / bài thi / List CSV / sau kết quả /
  không rõ), loại tệp sai đường (`forms_tep_sai_duong`), đoán đề A/B/C của tệp bài thi bằng `doan_bien_the` (không ghi gì);
  `chuyen_tep_forms(files, bien_the, lua_chon)` lưu tệp ở `forms/nap/tai_len/`, gọi `chuyen_fa_daa_du_lieu`, ghi
  `forms/nap/SO_NHAP_CLB.xlsx` + `EMAIL_MA_HS.csv` (+ `BANG_DIEM.xlsx`, `PHAN_TICH_CAU_HOI.xlsx`); chênh lệch giữa các đề ->
  `trang_thai: "cho_xac_nhan"` (hai nút "Dịch điểm về trung bình chung" / "Giữ điểm đã chấm", không phải chọn lại tệp); câu bị
  gắn cờ -> `cau_co_co` để tick "Bỏ câu này" rồi chấm lại; lỗi đề / tệp -> `forms_khong_chuyen_duoc`, không ghi Sổ.
  `get_forms_nap()` nhớ các tệp đã tải khi mở lại thẻ; `lay_so_nhap_nap()` trả Sổ nhập base64.
- Nhập vào app.db vẫn bằng `xem_truoc_so_nhap` / `import_so_nhap` CÓ SẴN (không có đường nhập thứ hai).
- Giao diện `js/12_chuan_bi_nap.js` (bước 4): khung thả nhiều tệp, bảng tệp (loại + ô chọn đề, đoán sẵn), nút "Chuyển thành Sổ
  nhập", hộp xác nhận, danh sách "Bỏ câu này" + "Chấm lại", cảnh báo, xem trước, nút "Nhập sổ". Chuỗi `cb_nap_*` (vi + en).
- Mã lỗi mới (khối B): `forms_thieu_tep_nap`, `forms_thieu_tep_dang_ky`, `forms_nhieu_tep_list`, `forms_chua_chuyen_tep`
  (đã thêm vào `MA_MOI_SAU_ANH_CHUP`, đã chạy `tao_i18n_js.py`).
- Tệp test mới: `tests/test_fa_m9_nap_tep_forms.py` (19 ca API), `tests/test_giao_dien_fa_m9_nap.py` (4 ca Chromium: đường B thả
  1 đăng ký + 2 bài thi -> xem trước -> nhập, số học sinh khớp; đường A lệch đề -> xác nhận; tệp lạ / sai đường khoá nút;
  chưa chọn đường). Trước đó: `tests/test_fa_m9_thuan.py`.
- Đột biến đã chạy: API bỏ qua `lua_chon` (`lua_chon=None`) -> 3 ca đỏ (`test_xac_nhan_roi_lua_chon_thi_ghi_so`,
  `test_bo_cau_cham_lai`, `test_duong_a_lech_giua_hai_de_hien_hop_xac_nhan`); khôi phục -> xanh. (`doan_bien_the` luôn "A" đã
  đỏ ở FA-M9-THUAN.)
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; đầu ra bộ chuyển đổi dòng lệnh y hệt (API == CLI, so từng ô).

## TIEN_DO (một dòng)
| FA-M9 | Nạp tệp Forms / List ở bước 4 (nhận diện, đoán đề, xác nhận, bỏ câu, xem trước, nhập) | xong trên `claude/it-ui-b`; TH | `tests/test_fa_m9_thuan.py`, `tests/test_fa_m9_nap_tep_forms.py`, `tests/test_giao_dien_fa_m9_nap.py` |

## CLAUDE_CHI_TIET (bản đồ mã)
- `api_forms_nap.py` — `FormsNapMixin`: nạp tệp Forms / List (FA-M9) [+ nút sau khi xếp FA-M10]
- `js/12_chuan_bi_nap.js` — bước 4 (và 5) của thẻ "Chuẩn bị đợt"
- Số tệp test mới của B (đến hết FA-M9): 3 (`test_fa_m9_thuan`, `test_fa_m9_nap_tep_forms`, `test_giao_dien_fa_m9_nap`) + `test_fa_m10_thuan`.

## HUONG_DAN_SU_DUNG (đoạn cho người dùng)
**Chuẩn bị đợt — bước 4 "Nạp kết quả từ biểu mẫu".** Chọn đường A hoặc B ở đầu thẻ, rồi kéo thả các tệp tải từ biểu mẫu vào
khung: đường A cần MỘT tệp CSV xuất từ List và các tệp Excel bài thi; đường B cần các tệp Excel biểu mẫu đăng ký và các tệp
Excel bài thi. Phần mềm tự nhận loại từng tệp và đoán đề A / B / C của tệp bài thi; nếu đoán sai hoặc không đoán được, chọn đề
ở ô cạnh tệp. Bấm "Chuyển thành Sổ nhập": nếu điểm giữa các đề lệch quá mức ngẫu nhiên, phần mềm dừng và hỏi dịch điểm về
trung bình chung hay giữ điểm đã chấm; câu hỏi bị gắn cờ có thể tick "Bỏ câu này" rồi bấm "Chấm lại". Xem bản xem trước, giữ
BẬT "Dùng điểm quyết tâm" ở Cài đặt xếp, rồi bấm "Nhập sổ". Chuyển đổi chưa ghi gì vào dữ liệu xếp cho tới khi bấm "Nhập sổ".

---
# FA-M10 — ba nút sau khi xếp (bước 5)

## CHANGELOG (văn bản mục)
**FA-M10 — Ba nút "Sau khi xếp" ngay trong phần mềm (thẻ "Chuẩn bị đợt", bước 5).** TH = chưa thử trên Microsoft thật.
- `api_forms_nap.py`: `xuat_ket_qua_list()` (các dòng `export_ly_do_csv` ghép email bằng `ghep_ket_qua_email.ghep` với
  `forms/nap/EMAIL_MA_HS.csv` -> `KETQUA_NHAP_LIST.csv`; thiếu tệp email -> `forms_thieu_email`; không để lại `ket_qua_ly_do.csv`),
  `ai_chua_dang_ky(file_base64)` (CSV danh sách lớp + mã học sinh đã đăng ký ở lần nạp cuối của bước 4 -> thư mục `chua_dang_ky/`:
  mỗi lớp còn em chưa đăng ký một tệp + `tong_hop.csv`), `doi_chieu_hai_lan(cu_base64, moi_base64)` (-> `DOI_CHIEU_LIST.xlsx`, đề lấy
  từ `forms/de_thi.json`). Mọi tệp ra rơi vào `thu_muc_tai_ve()` qua `_duong_xuat`: không ghi đè tệp cũ (`x (2)`), lỗi thì không ghi gì.
  Dùng lại hàm sẵn có (`ghep`, `chua_dang_ky`, `doi_chieu` + `ghi_bao_cao`); dòng lệnh y hệt (API == CLI, so từng byte / từng ô).
- Giao diện `js/12_chuan_bi_nap.js` (bước 5): ba khối — nút "Xuất KETQUA_NHAP_LIST.csv"; ô chọn CSV danh sách lớp + nút "Tạo danh sách
  chưa đăng ký" (khoá tới khi chọn tệp; cảnh báo vượt giới hạn Power Automate); hai ô chọn CSV cũ / mới + nút "Đối chiếu" (CHỈ đường A).
  Chuỗi `cb_nap_s5_*` (vi + en). Không mã lỗi mới (dùng `forms_thieu_email`, `forms_thieu_danh_sach_lop`, `forms_khong_chuyen_duoc`...).
- Tệp test mới: `tests/test_fa_m10_sau_xep_nut.py` (8 ca API), `tests/test_giao_dien_fa_m10_nut.py` (5 ca Chromium).
- Đột biến đã chạy: (1) API ghi thêm ký tự vào `KETQUA_NHAP_LIST.csv` -> `test_xuat_ket_qua_list_bang_cli_cung_tep` đỏ; (2) giao diện bỏ điều kiện
  "đã chọn tệp" của nút "Ai chưa đăng ký" -> `test_nut_ai_chua_dang_ky_khoa_den_khi_chon_tep_roi_ghi_thu_muc` đỏ; khôi phục -> xanh.
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; ba tập lệnh dòng lệnh không đổi.

## TIEN_DO (một dòng)
| FA-M10 | Ba nút sau khi xếp ở bước 5 (xuất kết quả List, ai chưa đăng ký, đối chiếu hai lần xuất) | xong trên `claude/it-ui-b`; TH | `tests/test_fa_m10_thuan.py`, `tests/test_fa_m10_sau_xep_nut.py`, `tests/test_giao_dien_fa_m10_nut.py` |

## CLAUDE_CHI_TIET (bản đồ mã)
- `api_forms_nap.py` — thêm `xuat_ket_qua_list`, `ai_chua_dang_ky`, `doi_chieu_hai_lan` (FA-M10)
- `js/12_chuan_bi_nap.js` — bước 5 (khối IIFE thứ hai)
- Số tệp test mới của B (cả M9 + M10): 6 (`test_fa_m9_thuan`, `test_fa_m9_nap_tep_forms`, `test_giao_dien_fa_m9_nap`, `test_fa_m10_thuan`,
  `test_fa_m10_sau_xep_nut`, `test_giao_dien_fa_m10_nut`). Lưu ý: `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that`
  đỏ cho tới khi A cập nhật số tệp test trong bản đồ mã (đang ghi 254; B không sửa tệp đó).

## HUONG_DAN_SU_DUNG (đoạn cho người dùng)
**Chuẩn bị đợt — bước 5 "Sau khi xếp".** Sau khi xếp xong, ba nút giúp người phụ trách (IT). Tệp tạo ra nằm trong thư mục Tải xuống
và không bao giờ ghi đè tệp cũ. (1) "Xuất KETQUA_NHAP_LIST.csv": ghép email của từng em với kết quả và lý do của lần xếp mới nhất, để nạp
vào List KetQua; cần đã nạp tệp ở bước 4. (2) "Ai chưa đăng ký": chọn tệp CSV danh sách lớp (có cột student_id và class_id); phần mềm ghi
một tệp cho mỗi lớp còn em chưa đăng ký, kèm bảng tổng hợp tỉ lệ từng lớp, để gửi giáo viên chủ nhiệm. (3) "Đối chiếu hai lần xuất List"
(chỉ đường A): chọn tệp CSV List lần trước và lần này; báo cáo Excel liệt kê học sinh mới, học sinh rút, học sinh đổi nguyện vọng, lớp hoặc cơ sở.
