# Báo cáo 13/11/2026 — nhánh `claude/giam-may-rui` (FA-CT1, FA-CT2, FA-D7L) + soát mã bốn tầng

> Mọi số liệu là **MÔ PHỎNG** (dữ liệu sinh ngẫu nhiên, không phải khảo sát). Không có nhận định cho báo cáo đề tài.
> Soát theo skill `soat-ma`: **chỉ báo cáo, chưa sửa** gì sau soát.

## 1. Đã làm

| Mục | Commit | Nội dung | Test mới |
|---|---|---|---|
| FA-CT1 | `bc2e670` | `fa_daa.chia_cho_theo_nhu_cau`: chia tổng chỗ một buổi theo nhu cầu, sàn = max(1, giữ chỗ), trần = giới hạn giáo viên, làm tròn Hamilton, chỗ thừa `du`. Chỉ gợi ý. | `test_fa_ct1_chia_cho.py` (105) |
| FA-CT2 | `e2885eb` | `fa_daa.goi_y_tang_them`; API `export_chia_cho` → `chia_cho_theo_nhu_cau.xlsx` (mỗi buổi một trang, không dữ liệu học sinh, chỉ đọc app.db); nút + 2 ô số + chọn tệp nhu cầu tham khảo ở thẻ kết quả. | `test_fa_ct2_tang_them.py` (63), `test_giao_dien_fa_ct2.py` (3 Chromium) |
| FA-D7L | `7254539` | Điểm lẻ 0,1 (cắt bớt) ở bộ chuyển đổi: `--diem-le`, `rules.fa_diem_le` (mặc định tắt) + ô tick ở bước 4; kiosk `dat_diem_san` (đạt sàn = điểm làm tròn nửa lên ≥ sàn). | `test_fa_d7l_diem_le.py` (10), `test_giao_dien_fa_d7l.py` (1 Chromium) |

Số MÔ PHỎNG (FA-D7L test 3; 20 seed × 200 học sinh × 6 CLB/buổi, mô hình `du_lieu_test/mo_phong_fa_daa.py`): tỉ lệ lý do
"bốc thăm" trong các lần bị từ chối ở CLB Tuyển chọn — điểm nguyên **201/3065 = 6,6 %**, điểm lẻ **13/3068 = 0,4 %**. Tập em
bị loại vì dưới điểm sàn giống hệt nhau ở cả 20 seed. (Mô hình này có nhiễu điểm liên tục nên con số khác số của Fable.)

## 2. Phần máy

- `kiem_nhanh.py --co-so origin/main --so-seed 20` sau mỗi mục: **7/7 ĐẠT, 60/60 trùng khít** (3 lần).
- Test liên quan: 87 tệp FA / ws / wharton / i18n không giao diện: 3464 qua, 1 lỗi (test cũ so khớp khoá
  `get_forms_nap`) → đã đổi thiết kế sang `get_fa_diem_le`, chạy lại xanh. Nhóm lõi FA (`test_fa_tinh_chat`, `test_fa_chay`,
  `test_fa_gap13_vong_doi_cho`, `test_fa_ly_do`): 1713 qua, 1 bỏ qua (13.12, D1 hoãn — đã biết).
- Chromium chạy thật: `test_giao_dien_fa_ct2`, `test_giao_dien_fa_d7l`, `test_giao_dien_fa_ket_qua`, `test_giao_dien_fa_m9_nap`
  xanh; hai tệp mới chạy 5 lần liền, 5/5 xanh. Toàn bộ test (~22 phút) chưa chạy (CI chạy).

## 3. Bốn tầng

**Tầng 1 — lõi.** Không đổi `run_rbda*`, `club_choice_function`, `compute_club_priority`, `verify_stability`, STB, `run_history`
(diff). CT1/CT2 không vào khoá ưu tiên (chỉ đọc số tổng của `bang_nhu_cau`). D7L chỉ đổi phép lọc điểm sàn; điểm nguyên:
`dat_diem_san(d, s) is (d >= s)` cho mọi d, s ∈ 0..10 (int và float) và chạy chay_fa_daa với phép so cũ (monkeypatch) ra từng
dòng như nhau trên 5 seed. Biên: NaN / inf / bool làm `dat_diem_san` ném lỗi, nhưng mọi đường nhập đều chặn trước
(`submit_club_scores` trả `score_not_a_number`, đã thử). → **Đạt**, 1 điểm cần bàn (D-1).

**Tầng 2 — backend.** API mới trả `{ok, data, errors}`; mã lỗi mới có trong `i18n_errors.py`, `i18n_loi.js` sinh lại. Không đổi
schema / cột CSV. `export_chia_cho` chỉ đọc (md5 app.db trước/sau bằng nhau; đột biến "ghi chỉ tiêu" làm test đỏ). Tên CLB
qua `Trang.o` (chặn công thức). → **Đạt**, 1 phát hiện nên sửa (P-1).

**Tầng 3 — giao diện.** Nút/khung chỉ hiện khi FA bật, không thêm lời gọi API khi tắt; tên tệp hiện bằng `textContent`; lỗi
API qua `chayXuat` (hiện mã lỗi dịch). Ô tick điểm lẻ: lỗi thì trả lại trạng thái cũ + toast. Chưa thử ba vai, XSS bằng tên
CLB độc, `page.route` lỗi giả (chưa đo). → **Đạt có điều kiện** (P-3, P-4 nhỏ).

**Tầng 4 — vệ sinh / test.** `ruff` sạch; bản đồ mã cập nhật (268 tệp test, tên hàm mới; `test_a13_12_tai_lieu` xanh).
Đột biến tạm (đã hoàn tác, `git status` sạch): 8 chỗ, **6 đỏ, 2 sống sót** (P-5, P-6).

| Đột biến | Kết quả |
|---|---|
| M1 Hamilton: hoà theo d nhỏ thay vì d lớn | **sống sót** |
| M2 CT2 cho vượt nhu cầu | đỏ |
| M3 `dat_diem_san` bỏ +1/2 | đỏ |
| M4 `chay_fa_daa` so điểm thô | đỏ |
| M5 `fa_vong_doi_cho` so điểm thô | **sống sót** |
| M6 `bang_nhu_cau` so điểm thô | đỏ |
| M7 export ghi `clubs.capacity` | đỏ |
| M8 làm tròn 0,1 thay vì cắt bớt | đỏ |

## 4. Phát hiện

| # | Mức | Tệp | Hàm | Vấn đề | Đường xảy ra | Đề xuất | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| P-1 | nên sửa | api_xuat.py | `_doc_tep_nhu_cau` | `tep_nhu_cau` nhận đường dẫn tuỳ ý (ai gọi được API qua `browser_host` cũng vậy); tệp có đúng cột `club_id, nhu_cau` thì ô sai lọt vào `params.detail`; không giới hạn cỡ tệp | CSV có ô `MAT_KHAU_123` ở cột nhu_cau → `errors[0].params.detail` chứa nó | Chỉ nhận `{ten, base64}` (giao diện đã dùng), bỏ `detail` khỏi params, soát cỡ như `_soat_co_xlsx` | đã tái hiện |
| P-2 | nhỏ | api_forms.py | `dat_fa_diem_le` | giá trị không phải bool trả `ws_cau_hinh_hong` ("cấu hình hỏng") — câu không đúng nghĩa | `dat_fa_diem_le("co")` | mã riêng hoặc dùng mã kiểu `gia_tri_sai` | đã tái hiện (test) |
| P-3 | nhỏ | js/03_ket_qua.js | nút chọn tệp nhu cầu | đã chọn tệp thì không bỏ được (trừ tải lại trang); `FileReader.onerror` không xử lý | chọn nhầm tệp → mọi lần xuất sau đều dùng nó | nút "Bỏ tệp", báo lỗi đọc tệp | suy luận |
| P-4 | nhỏ | js/03_ket_qua.js | ô "Tổng số chỗ" | một số áp cho MỌI buổi; trường có buổi đông / vắng khác nhau thì phải xuất từng buổi (API có `buoi`, giao diện chưa có ô chọn buổi) | 2 buổi tổng 120 / 80, gõ 100 → cả hai chia 100 | ô chọn buổi, hoặc chỉ ghi rõ trong hướng dẫn | suy luận |
| P-5 | nhỏ | tests/test_fa_ct1_chia_cho.py | — | không có ca hoà phần lẻ với nhu cầu khác nhau | M1 sống sót | thêm một ca tay | đã tái hiện |
| P-6 | nhỏ | tests/test_fa_d7l_diem_le.py | — | không ca nào đo `fa_vong_doi_cho` với điểm lẻ | M5 sống sót | thêm ca 4,5 / sàn 5 cho `khoa_tho_fa` | đã tái hiện |

## 5. Cần Truong quyết

- **D-1 (đổi hành vi khi FA bật).** `dat_diem_san` dùng cho MỌI điểm, không chỉ khi bật điểm lẻ. Điểm nguyên không đổi gì
  (60/60). Nhưng nếu thầy cô **tự nhập** điểm lẻ cho CLB Tuyển chọn (vd 4,6, sàn 5): trước đây trượt, giờ đạt (làm tròn 5).
  Lựa chọn: (a) giữ như đặc tả — đạt sàn luôn xét theo điểm làm tròn **[đề xuất]**; (b) chỉ làm tròn khi `rules.fa_diem_le`
  bật; (c) chặn điểm lẻ khi tắt cờ.
- **Gộp nhánh:** `claude/giam-may-rui` chưa gộp vào `claude/forms-gop`, chưa mở PR. Truong quyết gộp hay không, và có sửa
  P-1…P-6 trước không.

## 6. Danh sách sửa đề xuất

| Việc | Nguồn | Trạng thái |
|---|---|---|
| P-1 bỏ đường dẫn, bỏ detail, soát cỡ | soát tầng 2 | Đề xuất |
| P-2…P-4 chữ / giao diện | soát tầng 2–3 | Đề xuất |
| P-5, P-6 thêm test | soát tầng 4 | Đề xuất |
| D-1 | đặc tả FA-D7L | Cần Truong quyết (đề xuất a) |
