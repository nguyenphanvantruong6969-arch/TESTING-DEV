# Báo cáo đóng vai người dùng — Điểm quyết tâm và điểm chuẩn (A13.4, Bước 13)

Phạm vi: chỉ báo cáo, **không sửa mã**. Mọi số liệu là dữ liệu MÔ PHỎNG (6 CLB, 2 buổi, 30 học sinh, điểm sinh ngẫu nhiên có hạt giống).
Kịch bản: `scratchpad/dong_vai.py` (Playwright + Chromium thật, trình duyệt dự phòng, 1280 x 900). Ảnh chụp **không** được commit; tên tệp ghi ở cột cuối (thư mục `anh_dong_vai/` trong scratchpad của phiên).

## Vai đã đóng
1. **Giáo viên phụ trách (lần đầu dùng):** tạo workspace bằng trình hướng dẫn (bật Điểm quyết tâm) → xem trước và nạp Sổ nhập hai hàng → thẻ Quản lý (khối Điểm quyết tâm, sửa một em chia sai) → bấm chạy → thẻ Kết quả (mục Điểm chuẩn) → xuất Excel (trang "Điểm chuẩn" có mặt) → "Thao tác khác".
2. **Học sinh ở kiosk:** **chưa đánh giá được.** Kịch bản mở màn kiosk nhưng phần lõi không trả lời ("Không liên lạc được với phần lõi", `hs_02_tim_khong_dau.png`); đây là lỗi của kịch bản (không dựng phần lõi cho vai này), không phải bằng chứng về sản phẩm. Cần chạy lại vai này trước khi kết luận gì về kiosk.

## Bảng khó khăn
| # | Vai | Màn | Bước | Khó khăn | Vì sao | Gợi ý sửa | Mức | Ảnh |
|---|---|---|---|---|---|---|---|---|
| 1 | GV | Vận hành → Kiểm tra dữ liệu | Bấm chạy khi hồ sơ điểm chưa hợp lệ | Lỗi hiện thành một đoạn đỏ rất dài, lặp "Chưa dùng hết điểm quyết tâm: học sinh HSxxx còn thiếu n điểm ở quỹ k" cho từng em/quỹ, tràn quá màn hình | Người dùng không biết bắt đầu từ đâu; không có đường dẫn sang nơi sửa | Gộp theo học sinh, hiện tối đa ~5 em kèm "và N em khác", thêm nút "Mở danh sách hồ sơ cần xử lý" | chặn | `gv_12_sau_khi_bam_chay.png` |
| 2 | GV | Quản lý → Điểm quyết tâm | Sau khi nạp Sổ | 26/30 em "chưa hợp lệ" mà không có cách xử lý hàng loạt; phải sửa từng em | Sổ do GV điền tay thường sai tổng; chạy bị chặn nên GV bí | Thêm "Chia đều phần còn thiếu cho cả lớp" (có xác nhận), hoặc xuất danh sách em cần sửa | chặn | `gv_08_quan_ly_diem_quyet_tam.png`, `gv_10_man_sua_em_chia_sai.png` |
| 3 | GV | Quản lý | Tìm mục Điểm chuẩn | Khối "Điểm chuẩn" nằm gần cuối trang cao ~6.600 px, sau bảng 30 em; GV không biết nó ở đó | Trang một cột rất dài | Thêm neo "Đi tới Điểm chuẩn" ở đầu trang hoặc đặt khối lên trên bảng học sinh | khó chịu | `gv_quan_ly_toan_trang.png`, `gv_quan_ly_diem_chuan.png` |
| 4 | GV | Kết quả / Quản lý | Xuất Excel sau lần chạy bị chặn | Thông báo xanh "Đã xuất kết quả của 0 học sinh" hiện cùng lúc với thông báo đỏ "Sắp xếp không thành công" | Xuất khi chưa có kết quả vẫn báo thành công, dễ hiểu nhầm là có tệp dùng được | Chặn nút xuất (hoặc cảnh báo vàng) khi chưa có kết quả | khó chịu | `gv_17_thao_tac_khac_mo.png`, `gv_13_ket_qua_dau_tab.png` |
| 5 | GV | Mọi tab | Sau nạp Sổ | Thông báo xanh "Xong: 6 CLB, 30 học sinh…" còn nguyên qua nhiều màn và chồng lên thông báo đỏ, che tiêu đề | Thông báo không tự tắt | Tự đóng sau vài giây; xếp chồng gọn hơn | khó chịu | `gv_10_…`, `gv_13_…` |
| 6 | GV | Trình hướng dẫn, bước 3 | Bật Điểm quyết tâm | Ô tích nằm tách xa nhãn "Dùng điểm quyết tâm" (nhãn bên trái, ô tích ở giữa trang) | Bố cục nhãn/ô tích | Đặt ô tích sát nhãn như các ô khác | nhỏ | `gv_03_wizard_luat_bat_diem.png` |
| 7 | GV | Quản lý | Đọc thẻ "Tình trạng" | Cột và thanh "Đã dùng 17 / 100" rõ, nhưng lời nhắc "Còn thiếu 83 điểm để đủ 100" lặp ở mỗi khung nên màn sửa dài | Lặp thông tin với bộ đếm | Rút thành một dòng khi đã có bộ đếm | nhỏ | `gv_10_man_sua_em_chia_sai.png` |

## Năm việc nên sửa trước
1. (#1) Gộp và rút gọn lỗi hồ sơ điểm chưa hợp lệ, kèm đường dẫn tới nơi sửa.
2. (#2) Cách xử lý hàng loạt hồ sơ điểm chia thiếu (chia đều phần còn thiếu, có xác nhận).
3. (#4) Không báo "đã xuất" khi chưa có kết quả.
4. (#3) Neo hoặc dời khối Điểm chuẩn lên để thấy được.
5. (#5) Thông báo tự đóng, không che nội dung.

## Điều chưa kiểm
- Vai học sinh ở kiosk (xem trên).
- Điểm chuẩn khi đã có kết quả thật: lần đóng vai này chạy bị chặn ở bước kiểm dữ liệu (đúng thiết kế), nên mục Điểm chuẩn chỉ thấy ở trạng thái "Chưa có kết quả"; phần có số liệu và biểu đồ được kiểm bằng `test_giao_dien_diem_chuan.py` (11 ca) và ảnh chụp riêng `xem_dc.py`, không phải bằng kịch bản này.
- Trang "Điểm chuẩn" có trong tệp Excel xuất (7 trang) nhưng ở lần xuất này không có học sinh nào.
