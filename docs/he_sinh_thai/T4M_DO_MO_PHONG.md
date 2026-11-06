# T4M — Đo mô phỏng: có và không có bài thi tuyển

> **MÔ PHỎNG.** Mọi con số dưới đây do dữ liệu bịa sinh ra; không phải khảo sát thật. Tệp này chỉ gồm phương pháp và bảng số (mã việc T4M-DO). Nhận xét và kết luận do học sinh tự viết.

## 1. Phương pháp

- Dữ liệu: chuỗi T4M ngoại tuyến (`demo_t4m.sinh_lists` -> `tao_mau_forms.ghi_mau_xuat_chi_thi` -> `chuyen_chi_thi` -> `import_so_nhap`), 15 CLB (3 mỗi buổi, 5 buổi) theo `de_thi.json`, trong đó 10 CLB có đề thi (Tầng 1 ở điều kiện B); chỉ tiêu mỗi CLB nhân hệ số ở bảng 2 (cách tính của `demo_t4m.he_so_cho_tu_dong`).
- Mỗi bộ dữ liệu x 20 hạt giống STB (1..20) x 2 điều kiện. Dữ liệu đọc MỘT lần; mỗi lần chạy sinh lại `generate_stb_lottery`, gọi `run_rbda_nhieu_buoi` (tham số như `api.run_pipeline`) rồi `verify_stability_tuan`.
- Điều kiện A. không bài thi (mọi CLB Tầng 2)
- Điều kiện B. có bài thi theo de_thi.json (CLB có đề = Tầng 1)
- Chỉ số (trung bình / nhỏ nhất / lớn nhất trên 20 hạt giống):
  - Tỉ lệ nguyện vọng 1 và top-3: mẫu số = số lượt (em, buổi) mà em có ít nhất một nguyện vọng trong buổi đó.
  - Số em chưa có CLB: số em có ít nhất một nguyện vọng trong buổi mà kết quả buổi đó rỗng, trung bình qua các buổi; theo từng buổi ở bảng cuối.
  - Suất Tầng 1 về nhóm điểm cao nhất: trong các suất mà em được xếp vào CLB em có điểm thi, tỉ lệ em có điểm >= điểm của người thứ `chỉ tiêu` trong số em có điểm của CLB đó (hoà điểm tính hết). Chỉ có ở điều kiện B.
  - Cặp phá vỡ: tổng số vấn đề `verify_stability_tuan` trả về (phải bằng 0).
  - Thời gian: giây cho STB + xếp + kiểm ổn định của một lần chạy.

## 2. Tham số các bộ dữ liệu (MÔ PHỎNG)

| Bộ | Số học sinh | Hạt giống sinh dữ liệu | Hệ số chỉ tiêu | Số CLB | Số CLB có đề thi | Chỉ tiêu TB mỗi buổi |
|---|---|---|---|---|---|---|
| 120 hs | 120 | 20261101 | 2 | 15 | 10 | 84 |
| 500 hs | 500 | 20261102 | 8.3 | 15 | 10 | 349 |
| 1500 hs | 1500 | 20261103 | 25 | 15 | 10 | 1050 |

## 3. Tỉ lệ xếp vào nguyện vọng 1 (% lượt em x buổi có đăng ký) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống).

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | 75.57 / 74.52 / 76.44 | 63.96 / 62.26 / 66.09 |
| 500 hs | 75.78 / 75.29 / 76.58 | 65.01 / 63.44 / 66.91 |
| 1500 hs | 74.86 / 74.25 / 75.17 | 62.97 / 62.29 / 63.93 |

## 4. Tỉ lệ xếp vào top-3 nguyện vọng (%) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống).

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | 80.46 / 80.46 / 80.46 | 80.46 / 80.46 / 80.46 |
| 500 hs | 80.70 / 80.70 / 80.70 | 80.70 / 80.70 / 80.70 |
| 1500 hs | 80.47 / 80.47 / 80.47 | 80.47 / 80.47 / 80.47 |

## 5. Số em có đăng ký mà chưa có CLB, trung bình mỗi buổi (em) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống).

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | 20.40 / 20.40 / 20.40 | 20.40 / 20.40 / 20.40 |
| 500 hs | 83.40 / 83.40 / 83.40 | 83.40 / 83.40 / 83.40 |
| 1500 hs | 254.80 / 254.80 / 254.80 | 254.80 / 254.80 / 254.80 |

## 6. Tỉ lệ suất Tầng 1 về em thuộc nhóm điểm cao nhất CLB (%) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống). Chỉ điều kiện B có suất Tầng 1.

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | — | 80.79 / 78.57 / 83.33 |
| 500 hs | — | 74.68 / 73.60 / 75.49 |
| 1500 hs | — | 73.17 / 72.09 / 74.21 |

## 7. Số cặp phá vỡ (verify_stability_tuan) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống).

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | 0 / 0 / 0 | 0 / 0 / 0 |
| 500 hs | 0 / 0 / 0 | 0 / 0 / 0 |
| 1500 hs | 0 / 0 / 0 | 0 / 0 / 0 |

## 8. Thời gian chạy một lần (giây) — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống).

| Bộ | Điều kiện A | Điều kiện B |
|---|---|---|
| 120 hs | 0.0057 / 0.0044 / 0.0089 | 0.0053 / 0.0050 / 0.0060 |
| 500 hs | 0.0483 / 0.0408 / 0.0863 | 0.0540 / 0.0464 / 0.0960 |
| 1500 hs | 0.3922 / 0.3419 / 0.4855 | 0.4296 / 0.4018 / 0.5742 |

## 9. Số em có đăng ký mà chưa có CLB, theo buổi — MÔ PHỎNG

Ô: trung bình / nhỏ nhất / lớn nhất (20 hạt giống), đơn vị em.

| Bộ | Điều kiện | thu_2 | thu_3 | thu_4 | thu_5 | thu_6 |
|---|---|---|---|---|---|---|
| 120 hs | A | 24.0 / 24.0 / 24.0 | 20.0 / 20.0 / 20.0 | 22.0 / 22.0 / 22.0 | 14.0 / 14.0 / 14.0 | 22.0 / 22.0 / 22.0 |
| 120 hs | B | 24.0 / 24.0 / 24.0 | 20.0 / 20.0 / 20.0 | 22.0 / 22.0 / 22.0 | 14.0 / 14.0 / 14.0 | 22.0 / 22.0 / 22.0 |
| 500 hs | A | 94.0 / 94.0 / 94.0 | 75.0 / 75.0 / 75.0 | 101.0 / 101.0 / 101.0 | 62.0 / 62.0 / 62.0 | 85.0 / 85.0 / 85.0 |
| 500 hs | B | 94.0 / 94.0 / 94.0 | 75.0 / 75.0 / 75.0 | 101.0 / 101.0 / 101.0 | 62.0 / 62.0 / 62.0 | 85.0 / 85.0 / 85.0 |
| 1500 hs | A | 309.0 / 309.0 / 309.0 | 213.0 / 213.0 / 213.0 | 301.0 / 301.0 / 301.0 | 209.0 / 209.0 / 209.0 | 242.0 / 242.0 / 242.0 |
| 1500 hs | B | 309.0 / 309.0 / 309.0 | 213.0 / 213.0 / 213.0 | 301.0 / 301.0 / 301.0 | 209.0 / 209.0 / 209.0 | 242.0 / 242.0 / 242.0 |

## 10. Số suất Tầng 1 đã xếp (điều kiện B) — MÔ PHỎNG

| Bộ | Số suất Tầng 1 (trung bình / nhỏ nhất / lớn nhất) |
|---|---|
| 120 hs | 239.9 / 236.0 / 242.0 |
| 500 hs | 960.7 / 947.0 / 981.0 |
| 1500 hs | 3012.8 / 3003.0 / 3029.0 |

## Tái lập

```
python du_lieu_test/do_t4m_thi.py
```

Tệp số liệu từng lần chạy: `du_lieu_test/ket_qua_t4m/t4m_tung_lan.csv`, `t4m_theo_buoi.csv`.

Thời gian chạy cả lưới trên máy đo: 30 giây (0.5 phút).
