# Báo cáo stress test toàn hệ thống (sau A13.8, đo lại trên đỉnh A13.9)

> **Dữ liệu MÔ PHỎNG** (tên bịa, điểm do máy sinh, seed cố định), sinh bằng `sinh_ngau_nhien` của kỹ năng `sinh-du-lieu-clb` và `so_nhap.ghi_so_nhap`. Báo cáo **chỉ đo**, không đặt ngưỡng đạt / không đạt, không viết nhận xét hay kết luận đề tài. Không sửa mã sản phẩm; chỉ thêm `du_lieu_test/stress/` và các tệp báo cáo.

## 0. Cấu hình máy đo, đỉnh commit, mốc

| Mục | Giá trị |
|---|---|
| Máy | 4 nhân CPU, 15,7 GB RAM, Linux 6.18 (container), Python 3.13.17, SQLite 3.45.1, Chromium (Chrome for Testing) 153.0.8010.12 |
| Đỉnh mã được đo (bản đầy đủ) | **`1fcef81`** = A13.9 (`32cbf0f`) + script stress. Tức là **SAU** các sửa A13.9, không phải trước |
| Số TRƯỚC A13.9 | chỉ có ở `s3`, `s8`, `s2` bản `--nhanh`, chạy trên `0f13771` (đỉnh A13.8) + cùng script (xem mục 9) |
| Test toàn bộ có Chromium (`pytest -q -rs`, đo trên đỉnh A13.8 `0f13771`) | **2859 passed, 3 skipped, 26 phút 10 giây.** 3 skipped: 2 do `.venv` thiếu `numpy` (đúng theo `CLAUDE.md`), 1 do cần người dùng thường trên POSIX (đo bằng root). Test Chromium **không** bị bỏ qua |

**Vì sao bản đầy đủ đo trên A13.9 chứ không phải A13.8.** Lần chạy nền đầu (đo trên A13.8) bị mất khi phiên bị ngắt giữa chừng (không để lại kết quả nào). Sau khi phiên điều phối chốt đẩy và A13.9 vào nhánh, em chạy lại bản đầy đủ trên đỉnh `1fcef81` (đã ghi `dinh_commit.txt`). Số đo hiệu năng vì vậy là của A13.9.

**Nhiễu đo.** Trong lúc `s1` (nhóm 1) chạy, em chạy song song hai phép kiểm nhẹ (`s8 --nhanh --cho-treo 55`, `s2 --nhanh`, khoảng 2 phút mỗi phép) và một phép đếm dòng bảng (30 giây). Các bậc lớn của `s1` (5.000 × 100) có thể bị chậm nhẹ vì tranh CPU. Các nhóm 5, 6, 7, 3, 8, 4, 2 chạy một mình; nhóm 5 được chạy lại hai lần khi máy rảnh (mục 5).

Chạy lại: `python du_lieu_test/stress/sN_<tên>.py [--nhanh]` (xem `du_lieu_test/stress/README.md`). Kết quả thô: `du_lieu_test/stress/ket_qua/*.json`.

---

## 1. Tải lớn / hiệu năng (`s1_tai_lon.py`)

Mỗi cấu hình trong một tiến trình con riêng, lặp 3 lần (CSDL mới mỗi lần). Giây, **trung vị / lớn nhất**. `RSS` là `ru_maxrss` của tiến trình đo; `tracemalloc` là đỉnh của riêng `run_pipeline`.

| Em | CLB | Buổi | ĐQT | Nạp Sổ | `run_pipeline` | `export_ket_qua` | RSS MB | tracemalloc MB | `app.db` MB (+1 sao lưu) |
|---:|---:|---:|:-:|---|---|---|---:|---:|---|
| 800 | 20 | 1 | tắt | 0,40 / 0,50 | 0,08 / 0,08 | 0,31 / 0,90 | 70 | 1,5 | 0,41 (+0,34) |
| 800 | 20 | 1 | bật | 0,55 / 0,64 | 0,07 / 0,10 | 0,44 / 0,52 | 90 | 2,2 | 0,58 (+0,52) |
| 800 | 20 | 3 | tắt | 0,42 / 0,46 | 0,19 / 0,23 | 0,46 / 0,48 | 73 | 2,7 | 0,90 (+0,75) |
| 800 | 20 | 3 | bật | 0,64 / 0,84 | 0,36 / 0,39 | 0,66 / 0,87 | 86 | 4,0 | 1,28 (+1,13) |
| 2.000 | 50 | 1 | tắt | 0,67 / 0,79 | 0,10 / 0,12 | 0,85 / 0,88 | 85 | 3,4 | 0,85 (+0,68) |
| 2.000 | 50 | 1 | bật | 0,90 / 0,99 | 0,19 / 0,20 | 0,80 / 1,11 | 97 | 5,2 | 1,29 (+1,12) |
| 2.000 | 50 | 3 | tắt | 0,68 / 0,92 | 0,38 / 0,53 | 1,16 / 1,38 | 88 | 5,9 | 1,75 (+1,36) |
| 2.000 | 50 | 3 | bật | 1,38 / 1,59 | 0,47 / 0,52 | 1,64 / 1,82 | 107 | 9,0 | 2,66 (+2,28) |
| 5.000 | 100 | 1 | tắt | 1,92 / 2,51 | 0,24 / 0,26 | 2,02 / 2,02 | 131 | 7,7 | 1,79 (+1,35) |
| 5.000 | 100 | 1 | bật | 2,60 / 3,11 | 0,40 / 0,41 | 2,23 / 2,40 | 174 | 12,0 | 2,86 (+2,43) |
| 5.000 | 100 | 3 | tắt | 1,94 / 2,03 | 1,13 / 1,26 | 3,25 / 3,51 | 145 | 14,1 | 4,25 (+3,27) |
| 5.000 | 100 | 3 | bật | 3,88 / 4,13 | 1,94 / 2,07 | 3,85 / 4,99 | 195 | 21,5 | 6,54 (+5,56) |

**Tách thời gian `run_pipeline`** (trung vị, giây; "còn lại" = tổng − các bước đo được, gồm ghi kết quả, xuất CSV và việc khác):

| Cấu hình | đọc dữ liệu | kiểm dữ liệu | khoá STB | giải | sanity | verify | sao lưu | còn lại | tổng |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 800×20, 1 buổi, ĐQT tắt | 0,031 | 0,004 | 0,001 | 0,007 | 0,000 | 0,003 | 0,006 | 0,024 | 0,084 |
| 2.000×50, 3 buổi, ĐQT bật | 0,102 | 0,052 | 0,001 | 0,034 | 0,001 | 0,181 | 0,013 | 0,085 | 0,468 |
| 5.000×100, 1 buổi, ĐQT tắt | 0,104 | 0,009 | 0,004 | 0,024 | 0,002 | 0,006 | 0,010 | 0,085 | 0,244 |
| 5.000×100, 3 buổi, ĐQT tắt | 0,211 | 0,013 | 0,004 | 0,084 | 0,003 | **0,667** | 0,020 | 0,186 | 1,134 |
| 5.000×100, 3 buổi, ĐQT bật | 0,389 | 0,199 | 0,004 | 0,124 | 0,003 | **0,807** | 0,035 | 0,329 | 1,945 |

Nhận xét kỹ thuật: với nhiều buổi, `verify_stability` là bước chiếm nhiều nhất ở bậc lớn; với một buổi thì bước đọc dữ liệu từ CSDL chiếm nhiều nhất.

**API đọc** (trung vị, giây; hai bậc cực biên; đủ 12 cấu hình trong JSON):

| API | 800×20, 1 buổi | 5.000×100, 3 buổi, ĐQT bật |
|---|---:|---:|
| `list_students_admin` trang 1 / trang cuối (100 dòng) | 0,004 / 0,004 | 0,016 / 0,031 |
| `list_students_admin` tìm "Nguyễn" | 0,022 | 0,131 |
| `list_clubs_admin` | 0,001 | 0,003 |
| `get_match_results` | 0,005 | 0,127 |
| `get_club_fill_stats` | 0,006 | 0,094 |
| `get_data_health_report` | 0,008 | 0,576 |
| `list_wharton_admin` trang 1 / chỉ hồ sơ lỗi | 0,036 / 0,034 | 0,548 / 0,560 |
| `get_diem_chuan`, `get_diem_chuan_clb`, `list_wharton_canh_bao` | xem JSON | xem JSON |

Mọi `export_ket_qua` / `run_pipeline` ở cả 12 cấu hình trả `ok`. Số tệp sao lưu giữ lại tối đa 10 bản (xem nhóm 6).

## 2. Dữ liệu bẩn / biên (`s2_du_lieu_ban.py`)

**640 biến thể có seed** (34 toán tử Sổ + CSV, mỗi toán tử 18–19 biến thể): mã hoá (UTF-8 có BOM, UTF-16 đọc nhầm UTF-8, cp1258 đọc nhầm UTF-8), NFC / NFD, ô gộp lạ, số dạng chữ / thực / âm / rất lớn / Unicode ("²", "٣", "①"), dòng trống, mã trùng, thiếu cột, cột thừa, 0 em, 1 CLB, 0 CLB, chỉ tiêu 0, mọi em cùng NV1, ô điểm quyết tâm rác, tệp rác (cắt ngắn, byte ngẫu nhiên, toàn 0, CSV đổi đuôi, HTML), công thức Excel, 500–3.000 em thêm vào.

| Chỉ số | Số biến thể |
|---|---:|
| Tổng | 640 |
| Bị từ chối (kể cả bản xem trước có `loi`) | 257 |
| Được nhận | 383 |
| Được nhận nhưng `run_pipeline` sau đó từ chối bằng lỗi có tên | 33 (toàn bộ là điểm quyết tâm rác: `wharton_chua_dung_het`, `wharton_vuot_ngan_sach`, `wharton_ho_so_chua_hop_le`) |
| **Sập (ngoại lệ thoát ra ngoài API)** | **0** |
| **Sai hợp đồng `{ok, data, errors}` / mã lỗi không có trong `i18n_errors`** | **0** |
| **Ghi nửa chừng (ok = false mà CSDL đổi)** | **0** |
| **Lỗi bị bắt ở lớp ngoài cùng (`loi_nap_so_nhap`, `loi_ngoai_du_kien`…)** | **0** |
| **Lộ vết ngăn xếp / đường dẫn máy** | **0** |
| `PRAGMA integrity_check` sau khi nhận | `ok` ở mọi ca |

Lưu ý khi đọc: `khong_em` (0 học sinh) được nhận kèm cảnh báo mới `so_nhap_canh_bao_khong_co_hs` (A13.9, mục 8); `khong_clb` (0 CLB) và `mot_clb` bị từ chối bằng danh sách lỗi `so_nhap_clb_khong_co` vì sổ còn nguyện vọng trỏ tới CLB không có. Tái hiện một ca: `python du_lieu_test/stress/s2_du_lieu_ban.py --lai OP:SEED`.

## 3. Đồng thời / sập giữa chừng (`s3_dong_thoi.py`)

**A. Luồng đồng thời** (giây cho cả nhóm luồng; không ngoại lệ, không lỗi khoá, không sai hợp đồng ở mọi dòng):

| Hàm | N | Em khác nhau | Cùng một em |
|---|---:|---:|---:|
| `submit_preferences` | 4 / 16 / 64 | 0,032 / 0,120 / 0,443 | 0,023 / 0,106 / 0,412 |
| `submit_wharton` | 4 / 16 / 64\* | 0,026 / 0,079 / 0,282 | 0,039 / 0,128 / 0,442 |

Mọi lời gọi `ok`. Cùng một em: kết quả cuối đúng **một** trong các bản đã gửi (không trộn). Khác em: mỗi em đúng bản của mình. `integrity_check = ok`. \*Với N = 64 và em khác nhau chỉ có 60 em đủ điều kiện nên chạy 60 luồng.

**B. `run_pipeline` song song:** cùng một đối tượng API (hai luồng): cả hai `ok`, 0,16 s / 0,08 s, `run_history` +2, khoá STB 1 dòng. Hai đối tượng API ở hai tiến trình trên cùng `app.db`: cả hai `ok`, `run_history` +2, `match_results` 1.000 dòng, mọi em có STB, `integrity_check = ok`.

**C. SIGKILL giữa `run_pipeline`:** 30 lần kill ở các thời điểm ngẫu nhiên trong 0 – 1,6 × (thời gian một lần chạy 0,158 s). Sau mỗi lần: `integrity_check = ok`, `run_history` không giảm, khoá STB không mồ côi, mở lại và `run_pipeline(42)` chạy được, `run_history` tăng đúng 1. **0 vấn đề / 30.**

**D. CSDL bị khoá bởi kết nối khác (`BEGIN EXCLUSIVE`), trên A13.9:**

| Hàm | Thời gian tới lỗi (s) | Mã lỗi |
|---|---:|---|
| `submit_preferences` | 2,51 | `csdl_dang_ban` |
| `import_so_nhap` | 2,51 | `csdl_dang_ban` |
| `run_pipeline` | 17,56 | `csdl_dang_ban` |
| `list_students_admin` | 15,04 | `error_reading_student_list` |
| `reset_data` | 15,08 | `error_resetting_data` + `xem_nhat_ky` |

CSDL không đổi khi lỗi; `integrity_check = ok`; mở khoá xong `submit_preferences` và `run_pipeline` chạy lại bình thường.

**E. Đĩa đầy giả lập** (`RLIMIT_FSIZE` trong tiến trình con, `SIGXFSZ` bỏ qua): `run_pipeline` với giới hạn dưới cỡ CSDL → `ok = false`, rollback đúng (bước `rollback` done, CSDL không đổi, không để lại bản sao lưu dở); giới hạn +64 KB → `ok`. `import_so_nhap` hỏng khi giới hạn quá thấp → không ghi gì, `integrity_check = ok`. `export_ket_qua` hỏng với giới hạn 0 / 20 KB / 60 KB → `error_exporting_excel`, không để lại tệp dở. `submit_preferences` thành công ở mọi giới hạn thử (một dòng nhỏ). 0 ngoại lệ thoát ra ngoài.

## 4. Đúng đắn thuật toán (`s4_dung_dan.py`)

**2.000 bộ ngẫu nhiên** (806 có Điểm quyết tâm, 1.319 có dự trữ, 1.131 nhiều buổi; 5–200 em, 2–15 CLB, 1–3 buổi, độ chơi 0,6 – 1,4), nạp qua Sổ thật, chạy `run_pipeline`, rồi kiểm độc lập trên CSDL:

| Kiểm | Kết quả |
|---|---|
| K1 pipeline tự báo cặp phá vỡ / lỗi gì | 0 / 2.000 |
| K2 không vượt chỉ tiêu; CLB trúng nằm trong nguyện vọng và đúng buổi | 0 vi phạm |
| K3 dự trữ đúng nhóm, không quá `reserve_capacity` | 0 vi phạm |
| K4 ổn định (tự cài lại hàm lựa chọn, duyệt mọi cặp em–CLB em ưa hơn); bộ ≤ 8 em × 4 CLB: vét cạn mọi ghép → kết quả ổn định **và** tối ưu phía học sinh | 0 cặp phá vỡ; 0 ca không tối ưu |
| K5 cấu trúc khoá ưu tiên thật sự dùng: Tầng 1 trước Tầng 2, điểm giảm dần | 0 vi phạm |
| K6 hoán vị thứ tự nguyện vọng của mọi em (giữ tập) → danh sách ưu tiên của mọi CLB y nguyên | 0 thay đổi (chạy 1 / 5 bộ) |
| K7 STB: khoá sau lần đầu; đổi seed bị từ chối (`hat_giong_da_khoa`) và số không đổi; chèn 3 em muộn → thứ tự tương đối của em cũ giữ nguyên, số vẫn là hoán vị | 0 vi phạm |
| K8 tất định: cùng dữ liệu + seed → `match_results` y nguyên (cùng CSDL, và CSDL mới 1 / 5 bộ) | 0 lệch |
| K9 `run_history` tăng đúng 1 mỗi lần chạy thành công; không tăng khi bị từ chối | 0 vi phạm |
| Tự kiểm bộ kiểm (phá cố ý CSDL tạm: đổi CLB một em / gán dự trữ bừa / bỏ trống hết) | bắt được: K2+K4; K2+K3+K4; K4 |
| **Tắt Điểm quyết tâm: trùng khít `e08af78`** (so từng dòng `match_results` và số bốc thăm) | **60 ca (3 bộ × 20 seed) trùng khít** |

Ghi chú: chạy lại đúng một bộ: `python du_lieu_test/stress/s4_dung_dan.py --lai I`. Hai bộ dữ liệu có sẵn dùng cho phép so là `vi_du_huong_dan`, `bo_sach`, `TEST_0*` (do `do_anh_huong_seed.py`).

## 5. Giao diện dưới tải (`s5_giao_dien.py`, Chromium qua `browser_host`)

5.000 em × 100 CLB, 1 buổi, Điểm quyết tâm bật, đã chạy xếp; viewport 1366×900. Mỗi phép đo lặp 3 lần. Số của lần chạy lại thứ ba (máy rảnh):

| Phép đo | Trung vị (ms) | Lớn nhất (ms) |
|---|---:|---:|
| Tải trang tới khi vẽ xong | 410 | — |
| Thẻ Quản lý, tab CLB (đổi sang từ thẻ khác) | 450 | — |
| Tab Học sinh (50 dòng/trang) | 150 | — |
| Tab Điểm quyết tâm / Điểm chuẩn / Dữ liệu | 152 / 183 / 150 | — |
| Điểm chuẩn: đổi CLB, vẽ biểu đồ | 55 | — |
| Tìm theo mã "HS100" / theo tên "Nguyễn" / không có kết quả | 387 / 376 / 392 | — |
| Thẻ Kết quả (5.000 dòng vẽ) | 280 | **13.638** (lần đầu mở) |
| Cuộn hết trang Kết quả | 7 – 23 | — |
| Lật hết 99 trang danh sách học sinh | tổng ≈ 50 s; trung vị mỗi trang 90 ms | **19.742** (trang 2), 8.131 (trang 3), 10.334 (trang 4) |
| Đổi tab + đổi ngôn ngữ × 100 vòng | 295 mỗi vòng (tổng ≈ 30 s) | — |

- **Bộ nhớ:** heap JS 2,95 MB (đầu trang) → 4,48 MB → 6,67 MB sau 100 vòng đổi tab / ngôn ngữ (+1,85 MB trong vòng lặp; nút DOM 56.158 → 56.728, tăng 230–570); không thấy tăng tuyến tính rõ trong mẫu 10 vòng một lần.
- **Tác vụ dài:** 80 – 104 tác vụ, lớn nhất 195 – 417 ms.
- **Lỗi console / pageerror:** 0 / 0 trong mọi lần chạy.
- **Điểm bất thường đo được và lặp lại 3 / 3 lần chạy:** lần đầu mở thẻ Kết quả mất khoảng 13,6 s (hai lần sau chỉ 0,27 s), và ba lần lật trang đầu của danh sách học sinh mất 8 – 20 s (các trang sau 90 ms). Nguyên nhân chưa tách (ứng viên: vẽ đồng loạt 5.000 dòng kết quả lần đầu, hoặc một lời gọi backend lần đầu sau khi chạy xếp). Chỉ ghi nhận.
- Hai lần chạy đầu có phép tìm với chuỗi không khớp nên hiển thị 20 s: đó là lỗi chuỗi tìm của script (đã sửa ở `c27ff32`), không phải lỗi phần mềm.

## 6. Chạy dài / lặp (`s6_chay_dai.py`)

**A. 500 lần `run_pipeline(42)` liên tiếp (800 × 20, 3 buổi, ĐQT bật; mỗi 100 lần có một lần `force_redraw_stb`):**

| Chỉ số | Giá trị |
|---|---|
| Thất bại | 0 / 500 |
| Thời gian một lần: trung vị / lớn nhất | 0,256 s / 0,424 s |
| Trung vị 10% đầu → 10% cuối | 0,2515 → 0,2862 s |
| Hệ số góc theo số thứ tự lần chạy | −0,00004 s/lần (không chậm dần tuyến tính) |
| `run_history` | 500 dòng (mỗi lần một dòng) |
| `app.db` | 1,14 → 1,39 MB (≈ 0,5 KB mỗi lần) |
| Sao lưu | giữ tối đa 10 tệp, tổng ≈ 13,9 MB |
| RSS | 71,9 MB (lần 26) → 51,6 MB, phẳng từ lần 51 |
| `integrity_check` | ok |

**B. 100 vòng nạp Sổ → `reset_data("hoc_sinh","XOA")` → nạp lại:** thất bại 0; nạp trung vị 0,669 s / lớn nhất 1,097 s; xoá trung vị 0,074 s / 0,138 s; hệ số góc thời gian nạp 0,00008 s/vòng (phẳng); học sinh cuối 800; `integrity_check = ok`.
**`app.db` phình từ 1,4 MB (vòng 1) lên 16,7 MB sau 100 vòng** dù dữ liệu đang dùng không đổi (freelist 0); tổng 10 bản sao lưu 158 MB. Nguyên nhân (đếm bảng sau từng vòng): `wharton_nhat_ky` (nhật ký, không bao giờ xoá theo bất biến 4) thêm **801 dòng mỗi vòng** (800 dòng `nap_tep` + 1 dòng `xoa_du_lieu`): 801, 1.602, 2.403, 3.204… Không bảng nào khác tăng.

## 7. Workspace ngành khác (`s7_workspace.py`)

22 cấu hình × 2.000 em × 50 CLB × 2 buổi: mọi tổ hợp luật mà `cau_hinh_ws` cho phép (3 `priority` × 2 `tier_mode` × 2 `score_scope` × `wharton`, bỏ tổ hợp bị từ chối: 16 tổ hợp) cộng 3 bộ nhãn ngành khác (công ty — nhãn lấy từ `bo_thu_workspace`, sự kiện, tuỳ biến) × 2 luật. Giây, trung vị (3 lần):

| Cấu hình | Nạp | Chạy | Xuất | Em trúng |
|---|---:|---:|---:|---:|
| score / reserve / per_slot, W tắt | 0,76 | 0,33 | 0,97 | 2.300 |
| score / reserve / per_slot, **W bật** | 1,26 | 0,40 | 1,14 | 2.300 |
| score / reserve / per_person | 0,68 | 0,31 | 1,21 | 2.300 |
| score / strict / per_slot, **W bật** | 1,64 | 0,50 | 1,26 | 2.300 |
| tier / reserve / per_slot | 0,82 | 0,31 | 1,36 | 2.300 |
| tier / strict / per_person | 0,61 | 0,35 | 1,02 | 2.300 |
| score+tier / reserve / per_slot, **W bật** | 1,34 | 0,47 | 1,49 | 2.300 |
| score+tier / strict / per_slot, **W bật** | 1,40 | 0,53 | 1,16 | 2.300 |
| nhãn công ty / sự kiện / tuỳ biến (score hoặc tier) | 0,69 – 0,88 | 0,26 – 0,33 | 0,83 – 1,26 | 2.300 |

(Toàn bộ 22 dòng trong `ket_qua/s7_workspace.json`.) Kiểm như nhóm 4 (chỉ tiêu, dự trữ, ổn định tự cài lại, cấu trúc khoá khi luật là điểm thuần, không có dòng `reserve` khi chế độ bỏ qua dự trữ): **0 vấn đề ở cả 22 cấu hình**; `integrity_check = ok`.

## 8. Bảo mật / tấn công vào `browser_host.py` (`s8_bao_mat.py`)

Máy chủ ở tiến trình con, thư mục cát riêng, đối chiếu cây thư mục trước / sau.

| Kiểm | Quan sát (A13.9) |
|---|---|
| Tải 1.000 yêu cầu/s × 10 s (4 tiến trình khách) | đạt **567 rps thực**, 5.682 / 5.682 trả 200, độ trễ p50 6,8 / p95 10,7 / p99 13,4 / max 23,5 ms; máy chủ còn sống; RSS 43 → 45 MB; luồng 3 → 3 |
| Token thiếu / rỗng / sai / dài 1 MB / lệch độ dài / tên khác / hai tiêu đề | 403 (dài 1 MB: 431) |
| Token không ASCII (UTF-8 thô, byte 0xFF…, trong URL `?t=é`) | **403** (trước A13.9: đóng kết nối, không trả lời) |
| Host lạ + token đúng | 403 |
| Tệp tĩnh: `/app.db`, `/../app.db`, `/%2e%2e/app.db`, `/.git/config`, `/api.py`, `/CLAUDE.md`, `/loi_ung_dung.txt` | 404 |
| Thân 50 MB / `Content-Length` không phải số, âm, 10¹², 32 MB + 1 | 413 (50 MB: máy chủ đóng trước khi nhận hết) |
| JSON hỏng, `null`, mảng, `args` sai kiểu, 100.000 cấp lồng | 200 + `{ok:false}` kèm `loi_ngoai_du_kien` chỉ có **tên kiểu ngoại lệ** (`JSONDecodeError`, `TypeError`…) |
| 400 kết nối gửi dở tiêu đề | luồng 3 → 305 khi treo → **3 sau 60 s** (thả ở 45 s); vẫn phục vụ được khi treo |
| `Content-Length` lớn hơn thân thật | máy chủ trả 200 sau **45,1 s** (timeout) |
| Phương thức `_backup_db`, `__init__`, `__class__`, `__dict__`, `_khoa_ghi`, `db_path`, `..`, `%2e%2e%2f`, tên 100.000 ký tự, NUL, hoa / thường lạ… | 404 (tên dài: 414) |
| Slug workspace có `..` (`open`, `delete`, `export`, `rename`, `duplicate`, `get_config`) | `{ok:false}` (`ws_khong_co`, …) |
| Zip độc: zip slip `../`, `..\`, đường tuyệt đối, ổ đĩa `C:`, symlink (kể cả tên `app.db`), thiếu `app.db`, `app.db` rác, thư mục lồng 2.000 cấp, **50.000 tệp**, **tên trùng**, **zip bom 700 MB (→ 721 KB)** | **từ chối** hết; không tệp nào thoát ra ngoài thư mục workspace |
| Zip: tên có NUL; tiêu đề nói dối (60 MB khai nhỏ) | nhận (dưới trần 200 MB; Python cắt tên tại NUL) |
| Đường xuất `../../x`, `..\..\x`, `sub/../../x`, `~/x`, NUL, 5.000 ký tự, `con.xlsx`, `..` | ép vào thư mục Tải xuống bằng `basename` hoặc lỗi; **không tệp nào thoát ra** theo hướng tương đối |
| Đường xuất tuyệt đối ra ngoài | ghi đúng nơi đó (thiết kế); tệp sẵn có **không bị ghi đè** (`NAN_NHAN (2).xlsx`), tệp gốc nguyên vẹn |
| Đường xuất = một **thư mục** có sẵn | ghi tệp tên `ngoai (2)` (không đuôi) **ngay cạnh** thư mục đó, ngoài thư mục cho phép (xem mục 10, phát hiện N1) |
| Nhật ký lỗi sau 2.000 yêu cầu JSON hỏng | 6.726 → 7.530 byte (≈ 0,4 B/yêu cầu) |
| Vết ngăn xếp / đường dẫn máy trong phần `errors` | không thấy (đã quét `Traceback`, `File "`, `/home/`, thư mục cát, `.py", line`) |
| Máy chủ còn sống sau từng nhóm và cuối cùng | có |

Còn thấy trong stderr của máy chủ vài khối `Traceback` của `socketserver` (rất có thể do khách đóng kết nối giữa chừng, như `BrokenPipe`); chưa tách nguyên nhân từng khối. Chỉ ghi nhận.

---

## 9. Số TRƯỚC / SAU A13.9 và tình trạng 9 vấn đề của đợt trước

Số TRƯỚC = `0f13771` (A13.8) + script; SAU = `1fcef81` (A13.9) + script. Bản `--nhanh` của `s3`, `s8`, `s2` chạy một lần mỗi bên (nhanh nên chỉ để so sánh hành vi, không để so tốc độ).

| # | Vấn đề | TRƯỚC (A13.8) | SAU (A13.9) | Còn / hết | Đã sửa ở commit |
|---|---|---|---|---|---|
| 1 | CSDL bị khoá: báo sai nguyên nhân, chờ lâu | `ws_cau_hinh_hong` sau 15,0 s (`run_pipeline` 30,1 s) | `csdl_dang_ban` sau 2,5 s (`run_pipeline` 17,6 s) cho `submit_preferences`, `import_so_nhap`, `run_pipeline`. **`list_students_admin` và `reset_data` vẫn 15 s với mã chung** (`error_reading_student_list`, `error_resetting_data`); `run_pipeline` vẫn 17,6 s | **Hết phần mã lỗi sai**; còn chờ 15 – 17,6 s ở ba hàm (xem N3) | 814b5d4 |
| 2 | Máy chủ dự phòng không timeout kết nối | 100 kết nối treo giữ 103 luồng mãi; `Content-Length` lớn hơn thân treo mãi | luồng 103 → 3 sau 45 s; trả 200 sau 45,1 s | **Hết** | 1dac117 |
| 3 | Token không ASCII: đóng kết nối không trả lời | 4 biến thể "đóng kết nối" | 4 biến thể trả **403** | **Hết** | 1dac117 |
| 4 | `loi_ung_dung.txt` tăng không giới hạn | 801 B/yêu cầu (200 yêu cầu: 6,2 → 166 KB) | 0,4 B/yêu cầu (2.000 yêu cầu: 6,7 → 7,5 KB) | **Hết** | 1066456 |
| 5 | Phản hồi lỗi chứa thông điệp ngoại lệ Python nguyên văn | "takes from 1 to 4 positional arguments…", "Expecting property name…" | chỉ tên kiểu (`JSONDecodeError`, `TypeError`, `UnicodeDecodeError`) | **Hết** | 1dac117 |
| 6 | Đường xuất tuyệt đối ghi đè tệp có sẵn | tệp mẫu bị ghi đè | `NAN_NHAN (2).xlsx`, tệp gốc nguyên vẹn | **Hết** (phát sinh N1) | bf67701 |
| 7 | Zip workspace không trần số tệp / nhận tên trùng, tên NUL | 50.000 tệp: nhận 5,6 – 8,2 s; tên trùng: nhận; NUL: nhận | 50.000 tệp: từ chối 0,3 s; tên trùng: từ chối; zip bom 700 MB: từ chối. **Tên NUL vẫn nhận** (Python cắt tại NUL, vô hại); tiêu đề nói dối 60 MB vẫn nhận (dưới trần 200 MB) | **Hết** phần chính; tên NUL còn (ghi nhận) | 4a94376 |
| 8 | Sổ 0 học sinh / 0 CLB | 0 học sinh: nhận, không cảnh báo. (0 CLB: đã bị từ chối bằng `so_nhap_clb_khong_co`; ghi nhận ban đầu "nhận" là do bản xem trước trả `ok = true` kèm `loi` — nhầm của em) | 0 học sinh: nhận **kèm cảnh báo** `so_nhap_canh_bao_khong_co_hs`; `run_pipeline` sau đó `ok`; 0 CLB: vẫn từ chối | **Hết** | bc36bb7 |
| 9 | Skill sinh dữ liệu chỉ có 20 chủ đề CLB | script đo phải nối thêm chủ đề trong bộ nhớ | skill tự sinh tên khi > 20 CLB (A13.9); script đo vẫn dùng `mo_rong_chu_de` của riêng nó, chưa đổi | **Hết** ở phía skill (script đo chưa chuyển sang dùng) | 30f6d82 |

## 10. Bảng phát hiện chung (trên đỉnh A13.9)

Không có phát hiện mức **chặn** (không sập, treo, mất / hỏng dữ liệu, không phá bất biến nào trong 8 nhóm).

| # | Mức | Nhóm | Mô tả | Tái hiện (lệnh + đầu vào) | Đề xuất |
|---|---|---|---|---|---|
| N1 | nhỏ | 8 | `export_ket_qua(<đường tuyệt đối của một THƯ MỤC có sẵn>)` ghi tệp tên `ngoai (2)` (không đuôi) ngay cạnh thư mục đó, ngoài thư mục cho phép. Trước A13.9 trả lỗi. Là hệ quả của "trùng tên → `x (2)`" áp dụng cả cho thư mục | `python du_lieu_test/stress/s8_bao_mat.py` (T6, dòng "thư mục") | Từ chối đường xuất là thư mục (như trước), hoặc ghi vào trong thư mục đó với tên mặc định |
| N2 | nhỏ | 6 | `wharton_nhat_ky` thêm 801 dòng mỗi vòng nạp → xoá → nạp (800 `nap_tep` + 1 `xoa_du_lieu`), không có trần; `app.db` 1,4 → 16,7 MB sau 100 vòng, sao lưu 158 MB. Theo thiết kế (nhật ký không xoá) nhưng không giới hạn | `python du_lieu_test/stress/s6_chay_dai.py` (phần B) | Quyết có cần trần / gộp dòng `nap_tep` hàng loạt thành một dòng tóm tắt (cần Truong quyết vì nhật ký là bất biến) |
| N3 | nhỏ | 3 | Khi CSDL bị khoá: `list_students_admin` và `reset_data` vẫn chờ 15 s rồi báo lỗi chung; `run_pipeline` chờ 17,6 s | `python du_lieu_test/stress/s3_dong_thoi.py` (phép D) | Dùng cùng mã `csdl_dang_ban` và thời gian chờ ngắn cho mọi hàm đọc / ghi |
| N4 | nên xem | 5 | 5.000 × 100: lần đầu mở thẻ Kết quả mất ≈ 13,6 s (hai lần sau 0,27 s); ba lần lật trang đầu của danh sách học sinh mất 8 – 20 s. Lặp lại ở cả 3 lần chạy nhóm 5 | `RBDA_TEST_CHROMIUM=… python du_lieu_test/stress/s5_giao_dien.py` | Tách nguyên nhân (vẽ 5.000 dòng hay lời gọi backend lần đầu) ở vòng sau |
| N5 | ghi nhận | 8 | Tên mục zip có NUL được nhận; zip khai nhỏ giải ra 60 MB được nhận (đều dưới trần) | `s8_bao_mat.py` (T5) | Không cần |
| N6 | ghi nhận | 1 | `verify_stability` chiếm 0,67 – 0,81 s trong 1,1 – 1,9 s của `run_pipeline` ở 5.000 × 100 × 3 buổi | `s1_tai_lon.py` | Chỉ ghi nhận (có `verify_stability_nhanh` trong `docs/ke_hoach/tham_khao/`, mục Z4) |
| N7 | ghi nhận | 5 | Heap JS +1,85 MB sau 100 vòng đổi tab / ngôn ngữ ở 56 k nút DOM | `s5_giao_dien.py` | Chỉ ghi nhận |

## 11. Câu cần Truong quyết (đề xuất kèm)

1. **N2 — nhật ký `wharton_nhat_ky` tăng không giới hạn khi nạp Sổ lặp.** (a) giữ nguyên (nhật ký bất biến); (b) gộp mọi dòng `nap_tep` của một lần nạp thành MỘT dòng tóm tắt; (c) đặt trần số dòng và giữ N dòng gần nhất. **Đề xuất: (b)** — vẫn giữ dấu vết "đã nạp bao nhiêu em, lúc nào, từ tệp nào" mà bớt 800 dòng mỗi lần.
2. **N1 — đường xuất là thư mục có sẵn.** (a) từ chối bằng lỗi có tên; (b) ghi vào trong thư mục với tên mặc định. **Đề xuất: (a)** (đúng hành vi cũ, ít bất ngờ).
3. **N3 — đồng bộ xử lý CSDL bận ở mọi hàm.** (a) để như hiện tại; (b) đồng bộ `csdl_dang_ban` + thời gian chờ ≤ 3 s cho các hàm còn lại. **Đề xuất: (b).**

## 12. Lệnh chạy lại

```
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
export RBDA_TEST_CHROMIUM=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome | head -1)
for n in s1_tai_lon s5_giao_dien s6_chay_dai s7_workspace s3_dong_thoi s8_bao_mat s4_dung_dan s2_du_lieu_ban; do
  .venv/bin/python du_lieu_test/stress/$n.py [--nhanh]
done
```
Thời gian chạy bản đầy đủ trên máy đo: s1 336 s, s5 253 s, s6 218 s, s7 218 s, s3 143 s, s8 193 s, s4 4.003 s (≈ 67 phút), s2 615 s.
