# Soát sóng 1 — lấp khoảng trống FA-DAA (2026-11-10)

Phiên SOLO (một phiên làm cả vai cha lẫn con). Soát bằng cách đọc lại đặc tả và `git diff 4489dbb..HEAD`, chạy lại test.
Mọi số liệu là trên dữ liệu MÔ PHỎNG.

Kết luận: **GO** — không có lỗi mức cao/trung.

| Mục | Kết quả | Lỗi tìm thấy | Mức |
|---|---|---|---|
| GAP-0 nhật ký điều chỉnh + phát lại | xong (c6e0405) | không | — |
| GAP-1 điểm danh, vắng 2/3 không phép thì giải phóng chỗ | xong (a10eee5, bb49d11) | N1, N2, N3 | nhỏ |
| GAP-2 mời danh sách chờ | xong (541f945, 628cfb2) | N4 | nhỏ |

## Kiểm tra
- Test của từng mục đỏ trước rồi xanh: GAP-0 16, GAP-1 13 (3 Chromium), GAP-2 10 (1 Chromium).
- Bộ liên quan rộng: GAP-1 4.768 đạt, GAP-2 4.636 đạt; 4 bỏ qua có lý do (D1 hoãn, thiếu numpy ×2, cần người dùng POSIX).
- Giao diện chạy THẬT trong Chromium; tệp test giao diện mới chạy 10 lần liền: 10/10 đạt.
- Đột biến: 7 lần (con) + 2 lần (cha). Bỏ kiểm "lần chạy cũ" trong `vi_tri_hien_tai` → đỏ. Bỏ chặn CLB Tự do trong
  `moi_tiep` → KHÔNG đỏ, vì CLB Tự do không có dòng "bị từ chối" nên chặn này chỉ là phòng hờ (N4).
- `kiem_nhanh --so-seed 20`: 7/7, **60/60 trùng khít** với `main`. `ruff` sạch.
- Bất biến: không mã nào của sóng 1 ghi `match_results` hay `run_history` (đọc tay + `khong_sua_nhat_ky` nay canh cả
  `fa_dieu_chinh`); điểm danh/lời mời không đi vào `compute_club_priority`.

## Lỗi nhỏ (chỉ ghi lại)
- N1 (giao diện, tầng 3): `taiDiemDanh` / `taiMoi` ẩn khung khi API trả `ok=false` vì lỗi khác (không chỉ khi cờ tắt).
  Lỗi đọc CSDL sẽ làm khung biến mất thay vì báo lỗi.
- N2: lỗi chung khi lưu điểm danh / trả lời lời mời dùng mã `error_saving_preferences` ("không lưu được nguyện vọng"),
  câu chữ lệch việc đang làm.
- N3: chạy lại một buổi thì điểm danh cũ (theo lần chạy gốc) không còn hiện; đúng thiết kế G5 nhưng chưa có câu báo.
- N4: chặn loại CLB trong `moi_tiep` không có test đỏ được (tương đương hành vi); giữ làm phòng hờ.
- Ghi chú quyền (tầng 2 mục 9): như cả phần mềm, mọi hàm công khai gọi được từ trình duyệt; không thêm lớp xác thực.

## Độ phủ (vision §14, hàng P3 "Điểm danh, danh sách chờ, vòng 2, khảo sát tuần 3, khiếu nại")
- Trước: 0 % → nay: 40 % (điểm danh, danh sách chờ xong; vòng 2, khảo sát tuần 3, khiếu nại ở sóng 2).
