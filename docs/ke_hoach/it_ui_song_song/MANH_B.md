# Mảnh B — FA-M9 (nạp tệp Forms / List) — A gộp vào CHANGELOG / TIEN_DO / hướng dẫn ở Phase 3

TH = CHƯA thử trên Microsoft thật. Mọi số liệu trong test là MÔ PHỎNG. (FA-M10 sẽ thêm phần riêng ở dưới.)

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
