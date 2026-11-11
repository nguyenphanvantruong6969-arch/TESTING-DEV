# Soát đợt 3 FA gaps (3a: GAP-7, 9, 10; 3b: GAP-8) — 10/11/2026

Vai: cha (SOLO, đọc lại spec + diff 2d9c07d^..6b0ce75 của từng mục). Số liệu test là dữ liệu MÔ PHỎNG.

## Kết luận: GO

| Mục | Kết quả | Lỗi tìm thấy | Mức |
|---|---|---|---|
| GAP-7 gợi ý chỉ tiêu kỳ sau | đạt | — | — |
| GAP-8 bảng điều khiển | đạt | — | — |
| GAP-9 độ lệch hai người chấm | đạt | — | — |
| GAP-10 nhắc hạn + danh sách chưa đăng ký | đạt | — | — |

## Kiểm tra
- Bộ rộng (toàn bộ `tests/`, Chromium chạy thật) trên bản chụp b0d832e (đủ đợt 3 + GAP-11): **5763 qua, 4 bỏ qua**
  (D1 hoãn, thiếu numpy ×2, quyền POSIX — đã biết), **0 đỏ**.
- Test giao diện mới chạy thật: GAP-7 nút `#btnXuatGoiY` (1, trong `test_giao_dien_fa_ket_qua.py`), GAP-8 khung
  `#dashboardPanel` (2).
- Đột biến (đều bị bắt): GAP-7 `min` → `max`; GAP-8 bỏ lọc "lần chạy gốc mới nhất" khi đếm lý do; GAP-9 `>=` → `>`;
  GAP-10 `<` → `<=` ở luật 50 %.
- `kiem_nhanh --co-so origin/main --so-seed 20` sau GAP-7: 7/7, 60/60 trùng khít. `ruff check .` sạch.

## soat-ma bốn tầng (chỉ báo cáo)
- Tầng 1: không đổi `run_rbda*`, `compute_club_priority`; GAP-7/8 chỉ đọc số liệu kết quả, không đưa vào khoá ưu
  tiên. GAP-8 đọc thứ tự nguyện vọng CHỈ để đo tỉ lệ đổi huy chương khỏi mặc định D2 (báo cáo), đúng spec.
- Tầng 2: bảng mới `fa_gioi_han_gv` qua `DEFAULT_SCHEMA` (CSDL cũ nhận bảng khi mở, `di_tru_schema` lần hai không làm
  gì — có test); giới hạn sai (0, âm, chuỗi, bool, số thực) bị từ chối, không ghi gì; tệp xuất không có mã học sinh.
  GAP-8 không có INSERT/UPDATE.
- Tầng 3: nút/khung chỉ hiện khi FA bật; chữ vi + en đủ, đạt `chu_cam` và `test_van_phong_tu_nhien`.
- Tầng 4: CHANGELOG, TIEN_DO, bản đồ mã (thêm hàng công cụ GAP-9/10), số tệp test đúng.

## Nhỏ (chỉ ghi)
- N1: `export_bang_nhu_cau` thêm một cột cuối `goi_y_ky_sau` — tệp xuất FA, không phải CSV đầu vào; ai đọc tệp này
  bằng vị trí cột vẫn đúng (cột mới ở cuối).
- N2: ba chỉ số §11 (đăng ký sau 3 ngày, thử thách nghiêm túc, độ lệch chấm) luôn "chưa có dữ liệu" trong kiosk vì
  nguồn nằm ngoài kiosk (Forms / công cụ GAP-9, GAP-10) — đúng spec, không bịa số.
- N3: GAP-12 viết mã trước test (lệch S2.b); bù lại bằng hai đột biến đều bị bắt.
