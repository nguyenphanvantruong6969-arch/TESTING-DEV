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

---

## Lần 2 (27/10/2026)

Phạm vi: đóng vai lại sau khi sửa năm việc của A13.5. Lần này **có sửa mã** với vấn đề mức "chặn" (xem bảng); mức "khó chịu" và "nhỏ" chỉ ghi. Mọi số liệu là dữ liệu MÔ PHỎNG (6 CLB, 2 buổi, 30 học sinh, điểm sinh ngẫu nhiên có hạt giống). Báo cáo này là tài liệu vận hành, không phải nhận xét của đề tài.

Kịch bản: `scratchpad/dong_vai2.py` (Playwright + Chromium thật, `browser_host` cùng một `PipelineAPI` thật như các test giao diện, 1280 x 900). Kịch bản và ảnh **không** được commit; tên ảnh ghi ở cột cuối (thư mục `anh_dong_vai2/` trong scratchpad của phiên).

Hai bộ dữ liệu mô phỏng:
- **Bộ (i):** 30 học sinh, 23 em chia điểm thiếu (tổng khoảng 60), 2 em vắng thi, 3 em chưa có nguyện vọng để vai học sinh tự nhập.
- **Bộ (ii):** mọi em chia đủ 100 ở mọi quỹ, có CLB đầy (có người bị từ chối) và CLB còn chỗ, có suất dự trữ. Chạy xếp ra kết quả thật: 25/30 học sinh có CLB, 11 vòng.

### Vai đã đóng
1. **Giáo viên phụ trách:** chạy xếp bị chặn (bộ i) → mở danh sách cần xử lý → "Phóng cho đủ 100 theo tỉ lệ" → chạy xếp ở bộ (ii) → xem điểm chuẩn ở tab Kết quả và tab Quản lý (ba biểu đồ) → xuất Excel và kiểm trang "Điểm chuẩn".
2. **Học sinh ở kiosk (lần 1 chưa đánh giá được):** tìm tên không dấu ("nguyen" ra 3 em), chọn CLB thi, xếp 6 nguyện vọng, chia hai quỹ cho hai buổi (một lần thừa 120/100 rồi sửa), lưu; sau khi chạy xếp thì thử sửa: nút lưu bị khoá và có ghi chú khoá. Dữ liệu ghi đúng vào CSDL (6 dòng điểm).
3. **Người vận hành tiếng Anh:** cùng luồng với giáo viên, toàn bộ bằng tiếng Anh; không còn chữ có dấu trên thẻ Kết quả.

### Đối chiếu bảy vấn đề của Lần 1
| # | Trạng thái | Bằng chứng | Ghi chú |
|---|---|---|---|
| 1 | **Đã hết** | `gv_01_loi_chan.png`, `en_01_loi_chan.png`; `tests/test_giao_dien_loi_chan_gon.py` | Khung lỗi chỉ còn một dòng tóm tắt, 5 em đầu (mỗi em một dòng gộp mọi lỗi), "và 18 học sinh khác" và nút "Mở danh sách cần xử lý". Khi đóng vai phát hiện bước "Kiểm tra dữ liệu" trong danh sách bước vẫn hiện đoạn đỏ dài lặp từng lỗi (chính triệu chứng của #1): đã sửa trong lần này (`chuLoiBuocGon`), có test. Backend vẫn trả đủ mọi lỗi. |
| 2 | **Đã hết** | `gv_03_phong_xac_nhan.png`, `gv_04_sau_phong.png`; `tests/test_wharton_hang_loat.py` (21 ca) | Phóng được 23/23 em (bộ i không có em tổng 0 hay lỗi ngoài tập; ca bỏ qua được test kiểm). Mỗi em có một dòng nhật ký `quan_ly` / `luu`. |
| 3 | **Đổi dạng (đã hết khó tìm)** | `gv_02_tab_wh.png`, `gv_08_diem_chuan_quan_ly.png`; `tests/test_giao_dien_quan_ly_tab_con.py` | Năm tab con; Điểm chuẩn cách một cú bấm thay vì cuộn trang cao ~6.600 px. Tắt tính năng thì còn ba tab con. |
| 4 | **Đã hết** | `gv_05_xuat_khoa.png`; `tests/test_giao_dien_khoa_xuat.py`, `tests/test_xuat_khoa_chua_co_ket_qua.py` | Ô xuất kết quả bị khoá kèm dòng vàng khi chưa có kết quả; backend từ chối bằng `xuat_chua_co_ket_qua`. Mở lại sau khi chạy xếp thành công. |
| 5 | **Đổi dạng** | `gv_06_chay_xong.png`; `tests/test_giao_dien_thong_bao.py` (11 ca) | Mã cũ đã tự đóng thông báo thường sau khoảng 7 giây, nên nguyên nhân không phải thiếu hẹn giờ: thông báo nằm lại trong vài giây giữa các ảnh chụp, và vùng thông báo ở góc trên phải đè lên tiêu đề trang. Nay vùng ở góc dưới phải, thành công tự đóng sau 6 đến 10 giây (rê chuột thì dừng đếm), lỗi và cảnh báo giữ tới khi bấm ×. |
| 6 | **Còn** | không kiểm lần này | Để sau theo quyết định của Truong. |
| 7 | **Còn** | không kiểm lần này | Để sau theo quyết định của Truong. |

Hai chỗ lần 1 chưa kiểm nay đã kiểm: vai học sinh ở kiosk chạy được trọn vẹn; điểm chuẩn trên kết quả thật có đủ 6 dòng ở tab Kết quả, ba biểu đồ ở tab Quản lý (`gv_07_diem_chuan_ket_qua.png`, `gv_08_diem_chuan_quan_ly.png`), và trang "Điểm chuẩn" của tệp Excel có 6 dòng số liệu (một dòng mỗi CLB và buổi).

### Vấn đề mới phát sinh
| # | Vai | Màn | Bước | Khó khăn | Vì sao | Gợi ý sửa | Mức | Ảnh |
|---|---|---|---|---|---|---|---|---|
| N1 | Học sinh | Kiosk, Bước 3 | Lưu khi cả hai buổi cùng thừa điểm | Cùng một câu lỗi hiện hai lần liền, và gọi "Học sinh HS005" với chính học sinh đang đọc | Lỗi của từng buổi nối lại, câu không nêu tên buổi | Gộp câu trùng, thêm tên buổi | nhỏ | `hs_07_buoc3_sai.png` |
| N2 | Giáo viên | Vận hành | Sau khi phóng điểm xong | Khung "Các lỗi cần xử lý", bước đỏ "Kiểm tra dữ liệu" và thông báo đỏ của lần chạy bị chặn vẫn còn dù dữ liệu đã sửa | Lỗi cũ chỉ mất khi chạy lại | Xoá hoặc đánh dấu "đã cũ" khi dữ liệu đổi | khó chịu | `gv_04_sau_phong.png` |
| N3 | Giáo viên, vận hành | Nhiều màn | Đọc tên buổi | Nhãn buổi hiện mã thô "thu_3", "thu_5" | Sổ mẫu đặt buổi bằng mã; chưa có tên hiển thị | Cho phép đặt tên hiển thị của buổi | nhỏ | `hs_07_buoc3_sai.png`, `en_01_loi_chan.png` |
| N4 | Giáo viên | Quản lý, Điểm quyết tâm | Sau khi phóng hết hồ sơ sai | Hai nút hàng loạt chuyển sang mờ mà không nói vì sao | Nút bị khoá khi không còn hồ sơ chưa hợp lệ, không có chú thích | Thêm một dòng "Không còn hồ sơ cần sửa" cạnh hai nút | nhỏ | `gv_04_sau_phong.png` |
| N5 | Vận hành tiếng Anh | Vận hành | Đọc cảnh báo sức khoẻ dữ liệu | "student(s)" kiểu số ít hoặc nhiều trong ngoặc | Mẫu câu cũ chưa dùng nhãn số nhiều | Dùng `{person_pl}` như các câu mới | nhỏ | `en_01_loi_chan.png` |

Không có vấn đề mức "chặn" nào chưa xử lý: chỗ duy nhất đáng kể (bước "Kiểm tra dữ liệu" còn đoạn đỏ dài) đã được sửa ngay.

### Năm việc nên sửa tiếp theo
1. (N2) Xoá hoặc đánh dấu "đã cũ" các lỗi của lần chạy bị chặn khi dữ liệu đã đổi.
2. (#6) Đặt ô tích sát nhãn "Dùng điểm quyết tâm" ở trình hướng dẫn.
3. (#7) Rút lời nhắc "Còn thiếu n điểm" lặp ở mỗi khung của màn sửa.
4. (N1) Gộp câu lỗi trùng ở Bước 3 của kiosk và nêu tên buổi.
5. (N3) Cho phép đặt tên hiển thị của buổi thay cho mã thô.
