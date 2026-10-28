# Stress test toàn hệ thống (sau A13.8)

**Chỉ đo và báo cáo.** Không sửa mã sản phẩm. Dữ liệu là **MÔ PHỎNG** (seed cố định, sinh bằng
`sinh_ngau_nhien` của kỹ năng `sinh-du-lieu-clb`, sổ ghi bằng `so_nhap.ghi_so_nhap`). Báo cáo:
`docs/ke_hoach/BAO_CAO_STRESS_TEST.md`.

| Nhóm | Lệnh | Cờ `--nhanh` |
|---|---|---|
| 1 Tải lớn / hiệu năng | `python du_lieu_test/stress/s1_tai_lon.py` | 800×20 và 2.000×50, 1 buổi, Điểm quyết tâm tắt |
| 2 Dữ liệu bẩn / biên | `python du_lieu_test/stress/s2_du_lieu_ban.py` (`--lai OP:SEED` chạy lại một biến thể) | ~100 biến thể |
| 3 Đồng thời / sập giữa chừng | `python du_lieu_test/stress/s3_dong_thoi.py` | 4–16 luồng, 6 lần kill |
| 4 Đúng đắn thuật toán | `python du_lieu_test/stress/s4_dung_dan.py` (`--lai I` chạy lại bộ thứ I) | 60 bộ, 3 seed trùng khít |
| 5 Giao diện dưới tải | `RBDA_TEST_CHROMIUM=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome \| head -1) python du_lieu_test/stress/s5_giao_dien.py` | 800×20, 20 vòng |
| 6 Chạy dài / lặp | `python du_lieu_test/stress/s6_chay_dai.py` | 50 lần, 10 vòng |
| 7 Workspace ngành khác | `python du_lieu_test/stress/s7_workspace.py` | 300×10, mỗi 3 cấu hình lấy 1 |
| 8 Bảo mật / tấn công | `python du_lieu_test/stress/s8_bao_mat.py` | tải 3 s, 100 kết nối treo |

Cần `.venv` với `requirements-dev.txt` (pytest, playwright, openpyxl…). Mỗi script in bảng số và ghi
JSON vào `ket_qua/` (thư mục có `.gitignore`: chỉ giữ `*.json`). `_chung.py` là phần dùng chung.

Ghi chú dựng dữ liệu: `sinh_ngau_nhien` chỉ có 20 chủ đề CLB; `_chung.mo_rong_chu_de` nối thêm chủ đề
vào danh sách **trong bộ nhớ của tiến trình đo** để dựng 50 / 100 CLB (không sửa tệp kỹ năng).
