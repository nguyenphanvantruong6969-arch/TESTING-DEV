# Soát đợt 4 FA gaps (GAP-11, 12, 13, 14) — 10/11/2026

Vai: cha (SOLO, đọc lại spec + diff từ commit spec đợt 4 tới 8069c08). Số liệu test là dữ liệu MÔ PHỎNG.

## Kết luận: GO (GAP-14 chờ Truong quyết, đúng thiết kế)

| Mục | Kết quả | Lỗi tìm thấy | Mức |
|---|---|---|---|
| GAP-11 công thức Power Fx màn FA (TH) | đạt | — | — |
| GAP-12 mô phỏng đầy đủ | đạt | — | — |
| GAP-13 chu trình cải thiện ổn định (chế độ đo) | đạt sau sửa spec | spec ghi điều kiện cạnh thừa ("khoá không kém người đang giữ chỗ"): với bốc thăm đơn, điều kiện đó làm chu trình không bao giờ có (test 200 ca ngẫu nhiên bắt được); đã sửa về đúng định nghĩa Erdil & Ergin và ghi trong spec | trung (lỗi spec, sửa trước khi commit) |
| GAP-14 bản ghi nhớ D1 | chờ Truong | — | — |

## Kiểm tra
- Bộ rộng (toàn bộ `tests/`, Chromium chạy thật) trên HEAD 8069c08: **5774 qua, 4 bỏ qua** (đã biết), **0 đỏ**.
- Đột biến (đều bị bắt): GAP-11 bỏ `TrangThai = DRAFT` khỏi khối tự lưu; GAP-12 `<` → `<=` ở luật mốc, bỏ luật dời
  vàng; GAP-13 bỏ lọc "khoá tốt nhất" ở luật cạnh.
- GAP-11: bộ dựng mặc định so từng byte với bản cũ — giống hệt; lọc trên ECA/CLB đạt `soat_loc_uy_quyen`.
- GAP-12/13: `chay_mo_phong` (bảng FA-10) không đổi; bảng mới chỉ qua `chay_mo_phong_day_du` / `--day-du`.
- `kiem_nhanh --co-so origin/main --so-seed 20` trên HEAD: 7/7, 60/60 trùng khít. `ruff check .` sạch.

## soat-ma bốn tầng (chỉ báo cáo)
- Tầng 1: GAP-13 không vào đường xếp; `get_vong_doi_cho` chỉ đọc (test so `match_results` và `fa_dieu_chinh` trước /
  sau); nhãn "không bảo đảm ổn định" (bất biến 8). Khoá thô `khoa_tho_fa` không đọc thứ hạng nguyện vọng (bất biến 2).
  Cờ `fa_vong_doi_cho` mặc định TẮT, cần FA, không vào dấu vân tay.
- Tầng 2: không bảng mới; API trả `{ok, data, errors}`.
- Tầng 3: không giao diện mới ở kiosk. Chữ của app Power Apps (GAP-11) gọi học sinh là "em" như các biểu mẫu sẵn có
  (không thuộc phạm vi `chu_cam`, vốn chỉ soát chữ của kiosk).
- Tầng 4: CHANGELOG, TIEN_DO, bản đồ mã (hàng `fa_vong_doi_cho.py`, công cụ GAP-11), số tệp test 246.

## Nhỏ (chỉ ghi)
- N1: `khoa_tho_fa` là xấp xỉ khoá FA (giữ chỗ, điểm, huy chương; bỏ dự trữ mềm hai lượt) — đủ cho chế độ đo.
- N2: trên dữ liệu mô phỏng mặc định, bảng `vong_doi_cho_theo_loai` ra 0 % ở cả bốn kiểu (n = 100, 3 hạt giống);
  test 200 ca ngẫu nhiên vẫn tìm được chu trình, nên đây là số đo, không phải lỗi.
