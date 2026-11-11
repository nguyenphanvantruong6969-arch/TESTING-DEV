# Mảnh A — FA-M7 (một nguồn cho CLB và đề thi) — A gộp vào CHANGELOG / TIEN_DO / hướng dẫn ở Phase 3

TH = CHƯA thử trên Microsoft / Google thật. Mọi số liệu trong test là MÔ PHỎNG.

## CHANGELOG (văn bản mục)
**FA-M7 — CLB nhập một lần, đề thi trong một tệp Excel (thẻ "Chuẩn bị đợt", bước 1 và 2).**
- Bước "1. CLB": nút "Nạp tệp xuất Phiếu thiết lập CLB" -> API `nap_phieu_clb(file_base64, ky_truoc_base64="")` ghi
  `forms/SO_NHAP_CLB_CLB.xlsx` (+ `forms/PHIEU_CLB.xlsx`, `forms/BAO_CAO_PHIEU_CLB.md`) qua `chuyen_phieu_clb.chuyen_phieu`;
  trả `{n_clb, theo_loai, loi, canh_bao, chan, clubs}`. Không ghi CLB vào app.db. Tệp sai dạng hoặc không có CLB hợp lệ ->
  `phieu_clb_tep_sai`, tệp cũ giữ nguyên.
- Bước "2. Đề thi": `tai_mau_de_thi()` ghi `MAU_DE_THI_KIOSK.xlsx` (trang `Cai_dat`, `CLB` điền sẵn từ bước 1, `De_thi`
  trống với cột `club_id, de, cau_hoi, lua_chon_a..d, dap_an`) vào Tải xuống; `nap_de_thi(file_base64)` đọc, gom MỌI lỗi
  (CLB không có ở bước 1, đáp án ngoài a–d, lựa chọn trống, cột `de`, luật biến thể) mỗi lỗi một `de_thi_tep_sai`, lỗi thì
  KHÔNG ghi gì; thành công ghi `forms/de_thi.json` (cùng dạng tệp CLI đọc). `get_forms_buoc_12()` trả trạng thái để vẽ lại
  thẻ sau khi mở lại (đề cũ không khớp CLB bước 1 -> `khop: false`, hiện màu cảnh báo).
- Mô-đun mới `mau_forms_thi_clb/so_de_thi.py` (`ghi_mau_kiosk`, `doc_so_de_thi`, `doc_clb_dot`); không nhập từ `.claude/skills/`.
- `chuyen_phieu_clb.chuyen_phieu` trả thêm khoá `kq` (chi tiết lỗi/cảnh báo); đầu ra dòng lệnh không đổi.
- Giao diện `js/11_chuan_bi.js`: hai khung vẽ bằng `ChuanBi.dangKyBuoc`; chuỗi `cb_b1_*`, `cb_b2_*`, `cb_cot_*` (vi + en).
- Mã lỗi mới: không (dùng `phieu_clb_tep_sai`, `de_thi_tep_sai`, `forms_chua_co_clb` đã có từ G0).
- Tệp test mới: `tests/test_fa_m7_nguon_mot_lan.py` (18 ca: thuần + API), `tests/test_giao_dien_fa_m7_nguon.py` (3 ca Chromium:
  bước 1 rồi bước 2 chuyển xanh, mở lại vẫn xanh; bước 1 có dòng lỗi thì đỏ; bước 2 khi chưa có bước 1 báo lỗi).
- Đột biến đã chạy: bỏ phép đối chiếu CLB với bước 1 (`if ma not in theo_ma` -> `if False and ...`) -> 3 ca đỏ
  (`test_clb_chi_o_de_thi_khong_o_buoc_1_bao_loi_neu_ten`, `test_moi_loai_loi_bao_mot_lan`,
  `test_nap_de_thi_loi_thi_khong_ghi_de_thi_json`); khôi phục -> 18/18 xanh.
- Mặc định không đổi: không đụng lõi DA, schema, cột CSV; kết quả xếp không đổi (bước này không ghi app.db).

## TIEN_DO (một dòng)
| FA-M7 | CLB nhập một lần + đề thi một tệp Excel (thẻ Chuẩn bị đợt, bước 1–2) | xong trên `claude/it-ui-a`; TH | `tests/test_fa_m7_nguon_mot_lan.py`, `tests/test_giao_dien_fa_m7_nguon.py` |

## CLAUDE_CHI_TIET
Đã sửa trực tiếp (A sở hữu): số tệp test = 254; thêm dòng bản đồ mã cho `forms_dot.py`, `api_forms.py`, `so_de_thi.py`.
Phase 3 cần đếm lại số tệp test sau khi gộp B và C.

## HUONG_DAN_SU_DUNG (đoạn cho người dùng)
**Chuẩn bị đợt — bước 1 và 2.** Bước 1: bấm "Nạp tệp xuất Phiếu thiết lập CLB" và chọn tệp Excel xuất từ biểu mẫu Phiếu
thiết lập CLB. Phần mềm hiện bảng CLB (tên, buổi, loại, chỉ tiêu) và các lỗi, cảnh báo; bước chỉ chuyển xanh khi không còn
lỗi. CLB chỉ nhập một lần ở đây. Bước 2: bấm "Tải tệp đề mẫu" (tệp đã điền sẵn CLB của bước 1, nằm trong thư mục Tải xuống),
gõ câu hỏi vào trang De_thi (mỗi dòng một câu, đủ bốn lựa chọn, đáp án là a, b, c hoặc d; cột de để trống là đề A, có thể
thêm đề B, C cùng số câu), rồi bấm "Nạp tệp đề". Có lỗi thì phần mềm liệt kê hết một lần và chưa lưu gì; sửa tệp rồi nạp lại.
CLB không có câu hỏi nào là CLB không thi. Nếu sau này nạp lại bước 1 với CLB khác, bước 2 báo đề cũ không khớp: tải lại mẫu
và nạp lại đề.

## FA-M7-FIX1
`doc_so_de_thi` chép `loai` của CLB bước 1 sang `cau_lac_bo` của `de_thi.json` (không có `loai` thì không thêm khoá), để `bieu_mau.cac_phan_fa` loại CLB Tự do khỏi câu huy chương vàng. Test: `test_nap_de_thi_giu_loai_clb_va_tu_do_khong_vao_cau_vang_fa`, `test_clb_khong_co_loai_thi_de_thi_khong_them_khoa_loai`; `test_de_thi_json_dot_giong_mac_dinh_khi_cung_noi_dung` mở rộng (khẳng định `loai` đi theo). Đỏ trước khi sửa (2 ca), xanh sau.
