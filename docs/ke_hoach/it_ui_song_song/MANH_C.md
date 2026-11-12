# Mảnh C — FA-M8 (nút "Tạo bộ biểu mẫu", thẻ "Chuẩn bị đợt" bước 3) — A gộp vào CHANGELOG / TIEN_DO / CLAUDE_CHI_TIET / hướng dẫn ở Phase 3

TH = CHƯA thử trên Microsoft / Google thật. Mọi số liệu trong test là MÔ PHỎNG.

## CHANGELOG (văn bản mục)
**FA-M8 — Tạo bộ biểu mẫu một lần bấm (R3, R8, R9).**
- Hàm thuần (`mau_forms_thi_clb/tao_mau_forms.py`, `bieu_mau.py`): `sinh_phieu_clb` (R9, biểu mẫu thiết lập CLB, tiêu đề câu hỏi
  y nguyên `PHIEU_THIET_LAP_CLB.md` §1), tham số `dap_an_tren_forms` (mặc định True = như cũ; False = hướng dẫn KHÔNG dặn đặt đáp án
  trên Forms, R3), `ghi_xem_lai_dap_an` (`XEM_LAI_DAP_AN.xlsx`), `tao_bo_bieu_mau` và `ghi_zip_bo` (R8, một tệp zip cho đường đã chọn
  kèm `00_DOC_TRUOC.md`). Đường A gọi lại `tao_bo_dung_t4m.tao_bo_dung(fa=True)`, không sao chép.
- API `api_forms_bo.py` (`FormsBoMixin`): `get_bo_bieu_mau()` -> `{co_de, duong, co_bien_the}`; `tao_bo_bieu_mau_api(tuy_chon, output_path="")`
  (`tuy_chon = {mot_bieu_mau (mặc định True), bien_the (mặc định False)}`) lấy đề từ `forms/de_thi.json`, đường từ `rules.fa_duong`, Loại CLB
  từ `forms/SO_NHAP_CLB_CLB.xlsx` khi có (đường B); ghi `forms/bieu_mau/` và `BO_BIEU_MAU_<ngày>.zip` vào Tải xuống (không ghi đè, trùng
  tên thì "(2)"). Trả `{path, dir, ten_zip, thu_muc, n_tep, duong, mot_bieu_mau, bien_the}`. Lỗi: `forms_chua_co_de`, `forms_duong_chua_chon`,
  `forms_tao_bo_loi`. API KHÔNG có tuỳ chọn nào đổi R3; không ghi app.db.
- Giao diện `js/13_chuan_bi_bo.js`: bước 3 vẽ bằng `ChuanBi.dangKyBuoc(3, ...)`: ô "Một biểu mẫu cho mọi buổi" (tích sẵn; tắt ở đường A vì
  đường A dùng bộ dựng riêng), ô "Hai đề cho CLB Tuyển chọn" (chỉ bật khi đề có CLB có biến thể), nút "Tạo bộ biểu mẫu" (tắt khi chưa chọn đường
  hoặc chưa có đề), thông báo có tên tệp zip, nút "Mở thư mục" (`mo_thu_muc`). Chuỗi `cb_bo_*` (vi + en) trong khối C của `i18n.js`; kiểu `style.css`
  khối C.
- Mã lỗi mới: không (dùng ba mã đã có từ G0).
- Tệp test mới (3): `tests/test_fa_m8_bo_bieu_mau.py` (28 ca, hàm thuần), `tests/test_fa_m8_api.py` (12 ca), `tests/test_giao_dien_fa_m8_bo.py` (6 ca Chromium).
- Đột biến đã chạy: (1) `tao_bo_bieu_mau` truyền `dap_an_tren_forms=True` -> `test_r3_so_voi_dap_an_tren_forms_true` (API) đỏ, và ở lớp thuần
  `test_bo_khong_co_dap_an_tren_forms_o_moi_huong_dan` đỏ; (2) API bỏ qua `mot_bieu_mau` (luôn True) -> `test_mot_bieu_mau_theo_tuy_chon` đỏ;
  (3) giao diện luôn gửi `mot_bieu_mau: true` -> `test_bo_tich_mot_bieu_mau_doi_bo` đỏ. Khôi phục -> xanh.
- Mặc định không đổi: snapshot 8 chế độ của máy sinh (mặc định, `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--chi-thi`, `--phan-hoi`,
  `--sau-ket-qua`, `--tuan-3`, `--bien-the` với đề hai CLB dựng trong thư mục tạm) dựng từ BASE 5196217 và từ nhánh: `diff -rq` KHÔNG khác biệt (23 tệp).
  Không đụng lõi DA, schema, cột CSV.

## TIEN_DO (một dòng)
| FA-M8 | Nút "Tạo bộ biểu mẫu" (thẻ Chuẩn bị đợt, bước 3): R3 không đáp án trên Forms, R8 một zip, R9 biểu mẫu thiết lập CLB | xong trên `claude/it-ui-c`; TH | `tests/test_fa_m8_bo_bieu_mau.py`, `tests/test_fa_m8_api.py`, `tests/test_giao_dien_fa_m8_bo.py` |

## CLAUDE_CHI_TIET (dòng bản đồ mã)
| `api_forms_bo.py`, `js/13_chuan_bi_bo.js` | Bước 3 thẻ "Chuẩn bị đợt" (FA-M8, TH): `FormsBoMixin.get_bo_bieu_mau` · `tao_bo_bieu_mau_api` (gọi `tao_mau_forms.tao_bo_bieu_mau` + `ghi_zip_bo`; ghi `forms/bieu_mau/`, zip ở Tải xuống; không ghi app.db) |
| `mau_forms_thi_clb/tao_mau_forms.py` (thêm) | `sinh_phieu_clb` · `ghi_xem_lai_dap_an` · `tao_bo_bieu_mau` · `ghi_zip_bo`; `dap_an_tren_forms` (mặc định True) trên các hàm ghi hướng dẫn |
Số tệp test: C thêm **3** tệp (`test_fa_m8_bo_bieu_mau.py`, `test_fa_m8_api.py`, `test_giao_dien_fa_m8_bo.py`); trên nhánh C đếm được 257
(`ls tests/test_*.py | wc -l`). Phase 3: đếm lại sau khi gộp A, B, C.

## HUONG_DAN_SU_DUNG (đoạn cho người dùng)
**Chuẩn bị đợt — bước 3: Tạo bộ biểu mẫu.** Sau khi đã chọn đường A hoặc B và nạp đề thi ở bước 2, bấm "Tạo bộ biểu mẫu". Phần mềm làm sẵn mọi
biểu mẫu cần cho đợt (phiếu thiết lập CLB, phiếu đăng ký, bài thi, biểu mẫu sau khi xem kết quả, khảo sát tuần 3), kèm tệp "00_DOC_TRUOC.md"
cho biết nên làm theo thứ tự nào, rồi nén tất cả vào một tệp zip trong thư mục Tải xuống; bấm "Mở thư mục" để tìm tệp. Có hai ô chọn: "Một biểu
mẫu cho mọi buổi" (tích sẵn, học sinh chỉ điền một phiếu đăng ký) và "Hai đề cho CLB Tuyển chọn" (chỉ bật khi đề thi của đợt có CLB dùng hai đề).
Bộ này không dặn đặt đáp án đúng trên Forms: phần mềm tự chấm từ tệp đề thi; tệp "XEM_LAI_DAP_AN.xlsx" chỉ để người soát đề đọc lại đáp án.
Phần Forms chưa được thử trên Microsoft thật, nên hãy tạo thử một biểu mẫu trước khi gửi cho học sinh.
