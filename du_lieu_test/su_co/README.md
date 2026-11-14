# du_lieu_test/su_co: diễn tập sự cố do con người (FA-SC)

Dữ liệu hoàn toàn **MÔ PHỎNG** (học sinh giả, sinh ngẫu nhiên có hạt giống). Không phải khảo sát thật.
Các kịch bản chỉ **đọc** mã sản phẩm (bộ chuyển đổi `chuyen_fa_daa`, kiosk `PipelineAPI`) và ghi vào thư mục `--ra`.
Không trỏ `--ra` vào thư mục có `app.db` thật: thư mục `--ra` bị xoá và tạo lại mỗi lần chạy.

```
python du_lieu_test/su_co/chay_tat_ca.py --ra /tmp/su_co            # mọi kịch bản, ghi KET_QUA_DIEN_TAP.md
python du_lieu_test/su_co/d08_diem_danh_nham.py --ra /tmp/su_co_d08  # một kịch bản
```
Tham số chung: `--seed` (mặc định 42), `--so-hs` (mặc định 120). Cùng seed cho cùng số.

| Tệp | Sự cố | Mục trong memo |
|---|---|---|
| `chung.py` | Dựng đợt FA-DAA giả theo đường B, chạy chuyển đổi và kiosk | — |
| `d01_khong_dang_ky.py` | Em không đăng ký | S8 |
| `d02_sot_mot_ngay.py` | Sót biểu mẫu một ngày | S36 |
| `d03_go_sai_ma.py` | Gõ sai mã học sinh (đường B) | S30 |
| `d04_sai_tai_khoan.py` | Thi bằng tài khoản ngoài danh sách | S5 |
| `d05_tai_khoan_ban.py` | Thi bằng tài khoản của bạn cùng trường | S37 |
| `d06_thi_nham.py` | Thi nhầm CLB | S1 |
| `d07_tu_do_dung_dau.py` | CLB Tự do đứng nguyện vọng 1 | S33 |
| `d08_diem_danh_nham.py` | Điểm danh nhầm một ô | T4, S23 |
| `d09_chi_tieu_go_nham.py` | Chỉ tiêu gõ nhầm | T3 |
| `d10_mot_em_chan_ca_truong.py` | Một em sai huy chương chặn cả lần chạy | S4b, D-SC4 |
| `d11_tat_record_name.py` | Record name tắt | T2 |
| `d12_den_muon_sau_cong_bo.py` | Em đến muộn sau khi công bố | I4, S8 |
| `d13_nap_hai_lan.py` | Nạp một sổ hai lần | I2 |
| `d14_khong_co_lop.py` | Không có lớp, xuất theo lớp | S45 |
| `d15_loi_giua_chung.py` | Lỗi giữa lần chạy (rollback) | bất biến 5 |
| `d16_den_muon_khong_tranh_cho.py` | Một em đến muộn không tranh chỗ: số bốc thăm theo ngày bị tính lại | I4, F15 |

Đã chạy thêm seed 7 (mọi kịch bản) và seed 11 (riêng d16): hướng kết quả giống seed 42, con số khác (ví dụ d12: 20 em cũ đổi
CLB ở seed 42, 51 ở seed 7; d16: 18 / 38 / 30).

Giới hạn: bộ mẫu `de_thi.json` chỉ có ba CLB mỗi ngày; 120 em; đường A (Power Apps) không có trong kho nên không diễn tập.
Memo: `docs/fable/06_CRISIS_MEMO.md`. Sổ tay: `docs/fable/06b_SO_TAY_SU_CO.md`.
