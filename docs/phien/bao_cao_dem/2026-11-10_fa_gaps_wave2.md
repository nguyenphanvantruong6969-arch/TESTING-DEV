# Soát đợt 2 FA gaps (GAP-3, 4, 5, 6) — 10/11/2026

Vai: cha (SOLO, đọc lại spec + `git diff 9bb9deb..HEAD`, không dựa trí nhớ). Số liệu test là dữ liệu MÔ PHỎNG.

## Kết luận: GO (sau 3 sửa ngay trong đợt)

| Mục | Kết quả | Lỗi tìm thấy | Mức |
|---|---|---|---|
| GAP-3 khiếu nại | đạt | — | — |
| GAP-4 vòng 2 | đạt sau sửa | chữ `v2_khong_chon` dùng gạch ngang nối câu (`test_van_phong_tu_nhien` đỏ) → "(không chọn)" (b0d832e) | trung (test đỏ) |
| GAP-5 phản hồi | đạt sau sửa | (1) chữ khung phản hồi xưng "Em/you" (`chu_cam` KHÔNG ĐẠT, `test_skill_soat_ma` đỏ) → câu trung tính; (2) nạp tệp Forms: mã ngoài miền (vd. "(7)") làm vỡ ràng buộc CHECK của `fa_phan_hoi` → cả tệp bị từ chối bằng lỗi chung; nay lọc theo `MIEN_PHAN_HOI` (đọc thành rỗng) | trung |
| GAP-6 khảo sát tuần 3 | đạt | — | — |

## Kiểm tra
- Bộ rộng (toàn bộ `tests/`, Chromium chạy thật) trên bản chụp 8c4b37d: 5733 qua, 4 bỏ qua (D1 hoãn, thiếu numpy ×2, quyền POSIX — đã biết), 2 đỏ = hai lỗi chữ ở trên; sau sửa: `test_van_phong_tu_nhien.py` + `test_skill_soat_ma.py` 60 qua, test GAP-4/5 giao diện chạy thật xanh.
- GAP-3 bộ rộng riêng trên 513711a: 4791 qua, 0 đỏ.
- Đột biến: GAP-3 ×2, GAP-4 ×2, GAP-5 ×2 (+1 cho `MIEN_PHAN_HOI`), GAP-6 ×1 — đều bị test bắt.
- `kiem_nhanh --co-so origin/main --so-seed 20`: 7/7, 60/60 trùng khít (sau sửa chữ).
- `ruff check .` sạch.

## soat-ma bốn tầng (chỉ báo cáo)
- Tầng 1 (lõi): không hàm nào của đợt đọc/ghi khoá ưu tiên; `run_rbda*`, `compute_club_priority` không đổi; vòng 2 dùng
  `sinh_stb_theo_buoi` với hạt giống đã khoá (cùng hàm của lần chạy) — không sinh số mới.
- Tầng 2 (backend): mọi đổi chỗ là dòng mới trong `fa_dieu_chinh` (khiếu nại `appeal_rerun`, vòng 2 `round2`);
  `match_results`/`run_history` không bị sửa; `{ok, data, errors}` đủ; bảng mới qua `DEFAULT_SCHEMA`, CSDL cũ được nâng khi mở.
- Tầng 3 (giao diện): khung tự ẩn khi cờ tắt, lỗi thật hiện thông báo (W1 N1 đã sửa); chữ hiển thị nay đạt `chu_cam`.
- Tầng 4 (vệ sinh): CHANGELOG, TIEN_DO, bản đồ mã cập nhật; số tệp test đúng.

## Nhỏ (chỉ ghi)
- N1: vòng 2 cố định chế độ bốc thăm `stb_ngay` và đọc hạt giống từ `stb_lock` (đúng với mọi lần chạy từ giao diện;
  hai chế độ đối chứng chỉ có ở kịch bản `du_lieu_test/`).
- N2: `xu_ly_khieu_nai` gọi được từ kiosk như mọi hàm công khai (đã biết, tầng 2 mục 9).
- N3: GAP-4/5/6 chung một commit (e76bf48) thay vì mỗi mục một commit.
