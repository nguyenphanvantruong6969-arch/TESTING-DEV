# D1 — Ưu tiên bù (CompensationCredit): bản ghi nhớ để Truong quyết (GAP-14, 10/11/2026)

> Tài liệu vận hành, KHÔNG phải nhận định cho báo cáo đề tài. Mọi số dưới đây là **SỐ LIỆU MÔ PHỎNG** (dữ liệu sinh
> ngẫu nhiên có hạt giống, không có người thật). Không có mã nào được viết cho D1; `tests/test_fa_tinh_chat.py` vẫn
> bỏ qua ca V§13.12 ("hoãn sang kỳ 2").

## 1. D1 là gì (tầm nhìn V§8.4)
Em bị từ chối ở **NV1** vì `LOTTERY` ở kỳ T nhận một credit; kỳ T+1 credit đó đứng trước bốc thăm ở mọi CLB và bị
dùng khi nó là tiêu chí quyết định. Mỗi credit dùng một lần.

## 2. Phương án
| | A. Không bù | B. Bù đầy đủ (V§8.4) | C. Bù hẹp |
|---|---|---|---|
| Luật | như hiện nay | thua bốc thăm ở NV1 kỳ T → đứng đầu bốc thăm ở MỌI CLB kỳ T+1 | chỉ đứng đầu bốc thăm ở đúng CLB đã thua, kỳ T+1 |
| Cần đổi mã | không | khoá ưu tiên đọc kết cục kỳ trước | như B, phạm vi một CLB |
| Ngoại lệ bất biến 2 | không cần | **cần** | **cần** |

## 3. Rủi ro khuyến khích (điều được đo)
Một em có thể cố ý xếp một CLB Giới hạn đông nhất lên NV1 ở kỳ T (dù không thích nhất) để thua bốc thăm và có credit ở
kỳ T+1. Mô phỏng đo: trong số em mẫu, bao nhiêu em mà cách "lệch" đó cho tổng độ thích hai kỳ cao hơn cách khai thật.

## 4. Số đo (SỐ LIỆU MÔ PHỎNG)
Lệnh: `./.venv/bin/python du_lieu_test/mo_phong_fa_daa.py --n 100 --so-seed 5 --hai-ky 15` (bảng `hai_ky`; mô hình
ghi ở đầu tệp: một buổi, mọi em khác khai thật, "có bù" = thua bốc thăm kỳ 1 thì kỳ 2 đứng đầu bốc thăm).

| dieu_kien | so_em_mau | so_em_co_lech | so_thua_ky_1 | so_em_co_loi | pt_co_loi_tren_mau |
|---|---|---|---|---|---|
| khong_bu | 30 | 13 | 7 | 0 | 0.0 |
| co_bu | 30 | 13 | 7 | 1 | 3.3 |

Giới hạn của số đo: mẫu nhỏ (30 em, 3 hạt giống của bảng hai kỳ), một buổi, mô hình độ thích giả định; chưa đo
phương án C riêng. Muốn mẫu lớn hơn: tăng `--so-seed` và `--hai-ky`.

## 5. Nếu chọn B hoặc C: ngoại lệ bất biến 2 cần ghi
Bất biến 2 cấm `compute_club_priority` đọc "kết cục của phiên trước". D1 đọc đúng thứ đó. Cần một ngoại lệ do Truong
ghi trong `CLAUDE.md` (như ngoại lệ D2 ngày 2026-11-08), tối thiểu nêu: (1) chỉ ở tầng bốc thăm (thứ tự STB), không
chạm điểm hay huy chương; (2) nguồn là `fa_ly_do` của lần chạy gốc kỳ trước (`LOTTERY` ở NV1), không phải thứ hạng;
(3) mỗi credit dùng một lần, ghi nhật ký chỉ ghi thêm; (4) tắt mặc định, kết quả mặc định trùng khít (bất biến 1).

## 6. Câu hỏi cho Truong
**Kỳ 2 dùng A, B hay C?** Nếu B hoặc C: đồng ý ghi ngoại lệ bất biến 2 theo mục 5 không?
