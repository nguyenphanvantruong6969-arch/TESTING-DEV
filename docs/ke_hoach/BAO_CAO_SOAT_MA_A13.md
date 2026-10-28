# Báo cáo soát mã A13 (Điểm quyết tâm / Wharton) — 4 tầng

> Soát CHỈ BÁO CÁO, không sửa mã. Dữ liệu là MÔ PHỎNG. Không subagent, không `/code-review`.
> Phạm vi: `git diff e08af78..54a5cf4` (A13 vòng 1–5, trên `main`) + hàm cũ mà mã A13 gọi vào hoặc sửa.
> Vòng 6+7 (A13.6 `2df59ce`, A13.7 `088573d`) đã đẩy ngày 27/10: báo cáo đã rebase lên `088573d` và soát BỔ SUNG phần `54a5cf4..088573d` vào Tầng 1–2.
> Cách ghi: `| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |`.

## Bước 0 — Chuẩn bị

- Nhánh làm việc cục bộ: `claude/wizardly-lovelace-rfd5h2` = `origin/main` (`54a5cf4`). Mốc so sánh: `e08af78` (dựng bằng `git worktree`, ngoài kho).
- venv: `/tmp/claude-0/venv`, cài `requirements.txt` + `requirements-dev.txt`. Chromium: `/opt/pw-browsers/chromium-1243`.
- Diff A13: 80 tệp, +13.248 / −498 dòng (phần lớn là test và giao diện).
- **Mốc test toàn bộ (trước khi soát, `54a5cf4`, có Chromium):** `2699 passed, 3 skipped in 910 s`. 3 ca bỏ qua đều ngoài A13: hai ca `tests/test_tham_khao_verify_nhanh.py` cần `numpy` (không thêm vào requirements, đúng CLAUDE.md), một ca cần người dùng thường trên POSIX (chạy bằng root). Số ca khác `1.515` ghi trong `CLAUDE.md` — lệch tài liệu, ghi sang Tầng 4.

### Danh sách tệp / hàm trong phạm vi (chia tầng)

| Tầng | Tệp | Hàm mới / bị sửa trong A13 | Hàm CŨ mà A13 gọi vào (một bậc) |
|---|---|---|---|
| 1 Lõi | `rbda_priority_pipeline.py` | `khoa_uu_tien_wharton`, `uu_tien_wharton`, `kiem_ho_so_wharton`, `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc`, `dung_wharton`, `_luat_de_ghi_hoac_bam`, `doc_du_lieu_wharton`, `load_from_sqlite_kem_dau_van_tay_wharton`; sửa: `run_rbda`, `run_rbda_nhieu_buoi`, `luat_xep_de_ghi`, `dau_van_tay_du_lieu`, `LUAT_XEP_MAC_DINH`, `seed_sample_data` | `compute_club_priority`, `uu_tien_theo_nhom`, `club_choice_function`, `verify_stability`, `verify_stability_tuan`, `luat_xep_cua`, `luat_xep_hieu_luc`, `tham_so_luat`, `gom_theo_buoi`, `sap_buoi`, `_doc_du_lieu`, `_mo_doc_nhat_quan`, `err` |
| 2 Backend | `api.py`, `api_nhap.py`, `api_xuat.py`, `api_quan_ly.py`, `cau_hinh_ws.py`, `so_nhap.py`, `i18n_errors.py`, bảng `wharton_bids` / `wharton_nhat_ky` / `wharton_lock` (trong `DEFAULT_SCHEMA`) | `_run_pipeline_da_khoa` (nhánh Wharton), mọi API `*_wharton*` trong `api_quan_ly.py`, nạp `wp_k` / sổ nhập hai hàng, trang "Điểm chuẩn" trong `api_xuat.py` | `di_tru_schema`, `_RESET_BANG`, `import_so_nhap`, `xem_truoc_so_nhap`, `phan_hoi_ok/loi` |
| 3 Giao diện | `index.html`, `js/00_nen.js`, `02_van_hanh.js`, `03_ket_qua.js`, `04_nhap_tai_cho.js`, `05_quan_ly.js`, `075_workspace.js`, `i18n.js`, `i18n_loi.js`, `style.css` | kiosk Bước 3, 5 tab con Quản lý, điểm chuẩn + biểu đồ SVG, thông báo, khoá nút xuất | `window.pywebview.api.*` |
| 4 Vệ sinh | toàn diff + `CHANGELOG.md`, `SO_DANG_KY_33_MUC.md`, `TIEN_DO.md`, `CLAUDE.md`, `mau_csv/`, ba skill | | |

Số hàm cũ bị chạm ở Tầng 1: 13 (< 40, không cần hỏi thu hẹp).

---

## Tầng 1 — Lõi thuật toán (`rbda_priority_pipeline.py`)

### Cách kiểm (tất cả script nằm ngoài kho, không commit)

- Trùng khít khi TẮT: chạy `PipelineAPI.run_pipeline` trên **3 bộ dữ liệu có sẵn** (`vi_du_huong_dan` 10 em/4 CLB, `bo_sach` 140 em/12 CLB, `TEST_0*` 120 em/10 CLB) × **5 seed** (1, 7, 42, 99, 12345) bằng mã `e08af78` và mã `54a5cf4`, rồi so từng dòng `match_results` (`student_id, buoi, club_id, matched_tier, rank_in_student_pref, round_num`) và cột `students.stb_number`.
- Tính chất ngẫu nhiên: 2.000 + 1.000 danh sách ngẫu nhiên (trùng STB cố ý), 300 ca chạy `run_rbda` đầy đủ có/không `tier_rank`, có/không `bo_qua_du_tru`.
- Ví dụ tay 3 em × 2 CLB; biên (điểm 0, thiếu STB, số âm / thực / `bool` / `None` / `NaN`, chính sách lạ, tổ hợp luật).

### Kết quả theo mục yêu cầu

| Mục | Kết luận | Bằng chứng |
|---|---|---|
| 1. Bất biến 2 (không đọc thứ hạng nguyện vọng) | **ĐẠT** | Chữ ký `khoa_uu_tien_wharton(student_id, diem_thi, w1, w2, stb)` và `uu_tien_wharton(club_id, applicants, tested, stb, diem_wharton_clb, tier_rank)` không có tham số nguyện vọng. 300 ca: hoán vị ngẫu nhiên danh sách nguyện vọng ⇒ `base_rank` của mọi CLB **y hệt** (`assert r3.base_rank == r.base_rank`). `kiem_ho_so_wharton`, `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc` chỉ dùng *tập* CLB của em (`preferences` → `set`), không dùng vị trí. |
| 2. Khoá ưu tiên đúng thứ tự | **ĐẠT** | Tầng 1 `(0, -điểm thi, (), -w1, stb, sid)`, tầng 2 `(1, -w2, stb, sid)`: điểm thi và điểm quyết tâm đứng TRƯỚC STB. Tầng 1 vs 2 phân biệt ở phần tử đầu (0/1) nên không bao giờ so tuple khác độ dài. Với `tier_rank`: `(hạng,)+khoá`, khớp `uu_tien_theo_nhom` (1.000 ca, 0 lệch). Ví dụ tay (dưới) khớp. |
| 3. Tắt (`diem_wharton=None`) → nhánh cũ | **ĐẠT** | `run_rbda` rẽ `if diem_wharton is not None`; nhánh `else` giữ nguyên hai lời gọi cũ. **15/15 ca (3 bộ × 5 seed) trùng khít** `match_results` (1.350 dòng) và `stb_number` so với `e08af78`. Thêm: `diem_wharton={}` hay mọi điểm 0 cũng cho đúng thứ tự `compute_club_priority` (2.000 ca, 0 lệch). |
| 4. Thay thế được + tổng cầu (bất biến 8) | **ĐẠT** | Thứ tự nền vẫn là thứ tự chặt cố định theo CLB (`base_rank` tính một lần, khoá chứa `sid` nên không hoà) ⇒ hàm lựa chọn `club_choice_function` giữ nguyên tính chất như bản cũ. Có test sẵn `test_bat_bien_8_thay_the_duoc_va_luat_tong_cau` (tests/test_wharton.py:1133). |
| 5. `verify_stability` cùng ưu tiên với lúc giải | **ĐẠT** | `verify_stability` đọc `result.base_rank` (chính là thứ tự đã dùng lúc giải), không tính lại ưu tiên; không cần đổi chữ ký. 300 ca ngẫu nhiên có điểm Wharton, có/không `tier_rank`, có/không `bo_qua_du_tru`: **0 cặp phá vỡ**. |
| 6. Biên | **ĐẠT** (kèm 2 ghi chú nhỏ) | Điểm thi `0.0` vẫn là tầng 1 (xét `sid in tested`, không xét giá trị); điểm bằng nhau → STB → mã; em thiếu dòng điểm → 0; vắng thi → tầng 2 + cảnh báo `wharton_vang_thi` (điểm quỹ 1 bị bỏ); thiếu STB → `ValueError` cùng thông điệp hàm cũ; `kiem_ho_so_wharton` bắt `str`, `float`, `bool`, `None`, số âm, `NaN` (đều `wharton_diem_khong_hop_le`); chính sách vắng thi lạ → `ValueError`; `dung_wharton` từ chối `"true"`, `1`, `priority=tier`, `per_person`. Nhiều buổi: mỗi quỹ kiểm riêng từng buổi. |
| 7. STB (bất biến 3) | **ĐẠT** | Diff A13 không đụng `generate_stb_lottery`, `chen_stb_cho_hoc_sinh_moi` (grep trên diff: 0 dòng). `stb_number` của 15 ca bằng `e08af78`. |

### Ví dụ tay (3 em, 2 CLB, mỗi CLB 1 chỗ, không dự trữ)

STB: A=1, B=2, C=3. X có điểm thi: A=8, B=8, C không thi. Y không ai thi. Điểm quyết tâm: X: A=10, B=90, C=0; Y: A=50, B=50, C=100.

- Tính tay: X (tầng 1: A, B bằng 8, B có 90 > 10) → thứ tự B, A, C. Y (tầng 2: C=100 trước, A và B đều 50, A có STB nhỏ hơn) → C, A, B. DA: vòng 1 cả ba xin X, X giữ B; A, C bị loại. Vòng 2 A, C xin Y, Y giữ C. Kết quả: **B→X, C→Y, A không có chỗ**.
- Tắt (không có điểm): A→X (STB nhỏ nhất trong A, B), B→Y, C không có chỗ.
- Chương trình khi bật: `{'A': None, 'B': 'X', 'C': 'Y'}`, `base_rank` X = [B, A, C], Y = [C, A, B] — **khớp tính tay**; `verify_stability` rỗng ở cả hai.

### Phát hiện Tầng 1

| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| 1.1 | nhỏ | `rbda_priority_pipeline.py:357` (`khoa` trong `uu_tien_wharton`) | `uu_tien_wharton` / `khoa_uu_tien_wharton` | Điểm thi `NaN` làm `sorted` cho thứ tự không xác định. | Ở mức hàm: `tested_scores_for_club = {"A": nan, "B": 5.0, "C": 5.0}` → `['A','B','C']`. **Cập nhật sau Tầng 2:** không tới được qua API — `submit_club_scores` với `nan`, `"nan"`, `inf`, `"1e999"`, `-1` trả `ok=True` nhưng KHÔNG lưu dòng nào (bỏ im lặng; mã cũ, ngoài A13). | Không cần sửa ở A13. Ghi ở mục ngoài phạm vi: `submit_club_scores` bỏ im lặng điểm xấu mà vẫn báo `ok`. | đã tái hiện (`t1.py`, `t2k.py`) |
| 1.2 | nhỏ (đóng) | `rbda_priority_pipeline.py:415–416` (`la_diem_hop_le`) | `kiem_ho_so_wharton` | Điểm `100.0` (số thực nguyên) bị coi không hợp lệ ở mức hàm. **Cập nhật sau Tầng 2: không xảy ra thật** — Sổ nhập đi qua `o_thanh_chu` (`100.0 → "100"`, đã thử với ô Excel `100.0`), CSV dùng `[0-9]{1,9}`, JSON từ giao diện gửi số nguyên. | `w1={"A":{"X":100.0}}` chỉ lỗi khi gọi trực tiếp hàm. | Không cần sửa. | đã tái hiện ở mức hàm; không có đường thật |

**Không có phát hiện mức `chặn` hay `nên sửa` ở Tầng 1.** Không có đường nào cho thứ hạng nguyện vọng hay kết cục buổi trước đi vào khoá ưu tiên.

### Ghi chú ngoài phạm vi (một dòng)

- `submit_club_scores` bỏ im lặng điểm `NaN`/`inf`/âm/`"1e999"` mà vẫn trả `ok=True` (không lưu dòng nào, không báo): người chấm tưởng đã lưu. Mã cũ, không do A13.

### Tóm tắt Tầng 1

`chặn`: 0 · `nên sửa`: 0 · `nhỏ`: 2 (1.1, 1.2 — cả hai đã hạ xuống "không có đường thật" sau Tầng 2).


### Soát bổ sung vòng 6+7 (`54a5cf4..088573d`) — phần lõi

Phạm vi mở rộng thành `e08af78..088573d`. Vòng 6+7 **không đổi một dòng nào** của `rbda_priority_pipeline.py`. Bản chạy lại trùng khít trên mã `088573d`: **15/15 ca (3 bộ × 5 seed) trùng khít `e08af78`** (1.350 dòng `match_results` và `stb_number`).

### Bốn khía cạnh — Tầng 1

- **Bảo mật:** không có SQL, tệp hay chuỗi người dùng trong mã lõi; không có bí mật trong diff (grep `password|secret|token|eval|exec|os.system|pickle`: chỉ `subprocess` dạng danh sách đối số, không `shell`, trong test).
- **Hiệu năng:** `uu_tien_wharton` là `sorted` một lần mỗi CLB, O(n log n); `diem_wharton_hieu_luc` duyệt (em × nguyện vọng). Với bộ 800 em × 20 CLB × 4 buổi, `run_pipeline` mất 0,16 giây.
- **Đúng đắn:** đã thử biên ở bảng trên; không có lệch một.
- **Bảo trì:** hằng `WHARTON_*` có chú thích quyết định; tên `wharton` trong mã so với "điểm quyết tâm" ở chữ người dùng là chủ ý (đã ghi chú trong mã).

### Điểm tốt (Tầng 1)

Nhánh bật/tắt tách bạch bằng `if diem_wharton is not None` nên đường cũ không đổi một phép so sánh. Khoá ưu tiên là một hàm thuần có chữ ký không nhận nguyện vọng, dễ chứng minh bất biến 2. `verify_stability` tự đúng vì đọc `base_rank` của chính lần giải. Hàm phụ trả bản sao, không sửa đầu vào.

### Kết luận tầng: **Đạt**

---

## Tầng 2 — Backend

Phạm vi đã đọc: diff `api.py`, `api_quan_ly.py` (≈ 800 dòng), `api_nhap.py`, `api_xuat.py`, `cau_hinh_ws.py`, `so_nhap.py`, `i18n_errors.py`, ba bảng `wharton_*` trong `DEFAULT_SCHEMA`. Script thử nằm ngoài kho (không commit): `t2a.py` … `t2k.py`.

### Kết quả theo mục yêu cầu

| Mục | Kết luận | Bằng chứng |
|---|---|---|
| 1. Bất biến 5 (thứ tự pipeline, rollback thật) | **ĐẠT** | Bước kiểm hồ sơ Wharton (`api.py` ngay sau `validate_data_integrity`) đứng TRƯỚC "Bước 3/6 · SỐ BỐC THĂM". Hồ sơ sai (đổi một ô thành 90): `run_pipeline` trả `wharton_ho_so_chua_hop_le`, **không ghi gì** (so ảnh chụp 8 bảng: `match_results`, `run_history`, `run_meta`, `stb_lock`, `wharton_lock`, `wharton_nhat_ky`, `dau_van_tay_chay`, `students.stb_number`). Ném lỗi giả ở dòng khoá Wharton (ngay trước commit, sau khi đã vẽ STB và ghi kết quả): trả `error_running_pipeline`, **cả 8 bảng y nguyên**, chạy lại sau đó thành công. |
| 2. Bất biến 4 (chỉ ghi thêm) | **ĐẠT** | `grep` mọi tệp `.py`/`.js`: `wharton_nhat_ky` chỉ có `INSERT` (api_quan_ly.py:513) và `SELECT`; `run_history` không có `UPDATE`/`DELETE`/`DROP`. `reset_data` không đụng hai bảng này và còn ghi nhật ký TRƯỚC khi xoá điểm. Ghi chú: bảng chỉ-ghi-thêm là quy ước ở mã, CSDL không có trigger chặn `UPDATE`/`DELETE` (cùng mức với `run_history`). |
| 3. Bất biến 6 (`{ok,data,errors}`, mã lỗi) | **ĐẠT** | Quét mọi `err("…")` / `_fail("…")` trong `*.py`: 0 mã thiếu trong `MESSAGES`. `tao_i18n_js.py` chạy lại → `i18n_loi.js` **không đổi một byte**. 24 mã Wharton/csv_wp có đủ. Mọi hàm công khai mới (`list_wharton_admin`, `get_diem_chuan`, `get_diem_chuan_clb`, `list_wharton_canh_bao`, `get_wharton_nhat_ky`, `get_wharton_lock_status`, `mo_khoa_wharton`, `submit_wharton`, `admin_save_wharton`, `phong_wharton_hang_loat`, `clear_wharton`, `export_wharton_can_sua`) bọc `try/except` và trả `_ok`/`_fail`. Cấu hình hỏng sửa tay (`wharton:true` + `priority:"tier"`): các hàm ghi/chạy trả `ws_cau_hinh_hong`, `get_student_entry_state` và `get_data_health_report` vẫn mở được (coi như tắt), đúng chú thích. |
| 4. Bất biến 7 (`di_tru_schema`, DB cũ) | **ĐẠT** | Tạo CSDL bằng mã `e08af78` (bộ `bo_sach`, đã chạy phân bổ), mở bằng mã mới: `di_tru_schema` lần 1 và lần 2 đều trả `[]` (không việc nào), ba bảng `wharton_*` có mặt, `run_history` giữ nguyên số dòng, sao lưu `.bak-*` có, chạy phân bổ khi tắt thành công. Ba bảng mới là bảng MỚI hoàn toàn (`CREATE TABLE IF NOT EXISTS`), nằm ngoài `_BANG_RANG_BUOC`; `_dung_lai_bang_co_rang_buoc` dựng lại `students`/`clubs` với khoá ngoại tắt nên không làm hỏng khoá ngoại của `wharton_bids` (đã có test `test_dung_lai_bang_co_rang_buoc_giu_bang_wharton_hop_le`). |
| 5. Khoá điểm | **ĐẠT, kèm phát hiện 2.1** | Khi đang khoá: `submit_wharton`, `admin_save_wharton`, `phong_wharton_hang_loat`, `clear_wharton` (một em và tất cả) đều trả `wharton_da_khoa`; nạp CSV/Sổ nhập vẫn nạp nguyện vọng nhưng bỏ phần điểm và báo `wharton_da_khoa`. Kiểm khoá nằm TRONG giao dịch ghi (`_ket_noi_ghi`), không có khe. Mở khoá: `"mo"` → `wharton_mo_khoa_sai_xac_nhan`; `"MO"` → mở, có nhật ký. Chạy phân bổ thành công khoá lại trong CÙNG giao dịch với kết quả (đã thử rollback ở dòng 1). Ngoại lệ: phát hiện 2.1. |
| 6. Phóng hàng loạt | **ĐẠT** | `phong_theo_ti_le` thử 20.000 bộ điểm ngẫu nhiên: tổng luôn 100, CLB điểm 0 giữ 0, sai khác so với tỉ lệ thật < 1, kết quả không phụ thuộc thứ tự dict. `{A:1,B:1,C:1}` → `A:34, B:33, C:33` (phần dư bằng nhau → mã CLB nhỏ trước). Em tổng 0 → `tong_0`, lỗi khác (ví dụ `wharton_tang_lech`) → `loi_khac`; sao lưu chỉ khi có em để phóng. Ghi nhận phát hiện 2.5. |
| 7. Nạp Sổ nhập / CSV | **ĐẠT** | Sổ nhập hai hàng với 5 ô bẩn: `100.0` (số thực Excel) → nhận là 100; `"100,0"`, `"abc"`, `-5` → cảnh báo `csv_wp_khong_hop_le` (đủ mã em, mã CLB, giá trị), không sập, không chặn cả sổ. CSV: `30.0` bị từ chối đúng theo đặc tả "không số lẻ"; `wp_1` có điểm mà `pref_1` trống → `csv_wp_khong_co_nguyen_vong`; ghép `wp_k` theo hậu tố số nên không gán nhầm. Wharton tắt: cột `wp_k` bị bỏ qua và báo `csv_wp_bo_qua` (n = 5), không có dòng nào vào `wharton_bids`. |
| 8. SQL, đồng thời | **ĐẠT** | Mọi truy vấn A13 dùng `?`; hai chỗ ghép chuỗi (`"DELETE FROM %s" % ten`, `dk`) chỉ nhận hằng nội bộ. 8 luồng `submit_wharton` đồng thời cho 40 em: 0 lỗi, 0 "database is locked". |
| 9. Xuất | **ĐẠT, kèm phát hiện 2.3** | Chưa chạy: `export_ket_qua` → `xuat_chua_co_ket_qua`; `get_diem_chuan` → `co_ket_qua=False`, `rows` rỗng. Sau chạy 2 buổi: sổ có trang "Điểm chuẩn" sau "Chưa có chỗ", đủ cột buổi; so với tính lại từ `match_results` + `wharton_bids`: **0 lệch trên 5 dòng** (tầng 2, suất thường). |

### Phát hiện Tầng 2

| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| 2.1 | nên sửa | `api_quan_ly.py:1233` (tỉa trong `submit_preferences`); `api_nhap.py:1373` (cùng việc ở nạp CSV) | `submit_preferences`, `_nap_nguyen_vong` | Khoá điểm Wharton không chặn việc TỈA điểm khi bỏ CLB khỏi nguyện vọng. Điểm bị xoá, và em không sửa lại được vì `submit_wharton` trả `wharton_da_khoa`. | Đã chạy phân bổ (khoá = 1). Em `s03` có `c0` (quỹ 2, 100) và `c4` (quỹ 1, 100); kiosk `submit_preferences("s03", ["c0"])` → `ok=True`, dòng `s03/c4` bị xoá, nhật ký `kiosk/tia_nguyen_vong`, `get_diem_chuan().ket_qua_cu` = True. Hệ quả: lần chạy sau vẫn chạy được (vì hồ sơ còn hợp lệ ở ví dụ này), nhưng nếu CLB bị bỏ là CLB duy nhất của quỹ thì quỹ rỗng hợp lệ; nếu còn CLB khác thì "chưa dùng hết 100" và lần chạy bị chặn tới khi quản lý mở khoá. | Hỏi Truong: (A) giữ như hiện tại, ghi rõ vào tài liệu "khoá chỉ chặn GHI, không chặn tỉa"; (B) khi khoá thì `submit_preferences` / nạp nguyện vọng của em có điểm trả `wharton_da_khoa`. Đề xuất A (B đổi hành vi nguyện vọng của trường học đang chạy, chỉ khi bật Wharton). | đã tái hiện (`t2b.py`) |
| 2.2 | nên sửa | `api_quan_ly.py:700` (docstring `get_diem_chuan`); `browser_host.py:300` | `get_diem_chuan`, `get_diem_chuan_clb`, `list_wharton_admin`, `get_wharton_nhat_ky` | Docstring nói "CHỈ cho quản trị … không có đường nào cho kiosk gọi hàm này", nhưng không có xác thực nào: `browser_host` cho gọi MỌI phương thức công khai, và thẻ "Quản lý" là một mục điều hướng ngang hàng (`index.html:44`, không mật khẩu). Học sinh ngồi ở máy mở được điểm quyết tâm của cả khối, điểm chuẩn và nhật ký. Mẫu này có từ trước (`list_students_admin` cùng mức) nhưng A13 thêm dữ liệu nhạy hơn (điểm chuẩn có thể bị dùng để "tính điểm vừa đủ"). | `a.get_diem_chuan()` gọi trực tiếp, không thông tin xác thực → `ok=True` với toàn bộ dòng điểm chuẩn; qua HTTP: `POST /__api__/get_diem_chuan`. Tầng 3 sẽ kiểm trên giao diện thật. | Hỏi Truong: (A) sửa docstring cho đúng thực tế và ghi "thẻ Quản lý đặt sau cửa vật lý / người giám sát" vào `HUONG_DAN_SU_DUNG.md`; (B) thêm mã quản trị (PIN) cho thẻ Quản lý — việc lớn, ngoài phạm vi A13, cần mục riêng trong sổ đăng ký. Đề xuất A ngay, B ghi thành mục mới. | đã tái hiện (gọi không xác thực); **giao diện: đã tái hiện ở Tầng 3** |
| 2.3 | nên sửa | `api_xuat.py:376–377` | `_trang_diem_chuan` | `get_diem_chuan` lỗi thì `rows = []` và `rong=""` (vì `co_ket_qua` đúng): sổ kết quả xuất `ok=True` với trang "Điểm chuẩn" trống, không dòng chữ nào giải thích. Trường nhận một tệp thiếu mà tưởng đầy đủ. | Giả lỗi `get_diem_chuan` (trả `error_reading_results`) sau một lần chạy thành công → `export_ket_qua` `ok=True`, trang "Điểm chuẩn" chỉ có tiêu đề và hàng đầu cột. Lỗi thật có thể đến từ CSDL bận / cấu hình hỏng giữa hai lần đọc. | Khi `kq["ok"]` sai thì ghi một dòng cảnh báo vào trang (hoặc cho cả lần xuất thất bại). | đã tái hiện (`t2i.py`, lỗi giả) |
| 2.4 | nhỏ | `api_quan_ly.py:971` (`_ke_hoach_phong`), `:927` | `phong_wharton_hang_loat` | Kế hoạch tính từ MỘT ảnh chụp, rồi ghi từng em bằng giao dịch riêng: (a) không nguyên tử — dừng giữa chừng thì một phần em đã phóng; (b) nếu em tự sửa điểm trên kiosk đúng lúc đó, bản phóng (tính từ điểm cũ) ghi đè điểm mới; (c) khi gặp `wharton_da_khoa` giữa chừng, hàm trả thẳng lỗi và mất `n_phong`. Có sao lưu và nhật ký nên phục hồi được. | Hai phiên cùng máy: quản lý bấm "Phóng" khi một em đang lưu điểm. Hẹp. | Chấp nhận, hoặc đọc lại điểm hiện tại của em trong `_luu_wharton` và bỏ qua nếu khác ảnh chụp. | suy luận |
| 2.5 | nhỏ | `api_quan_ly.py:663` | `_ngu_canh_diem_chuan` | Đọc dữ liệu + hồ sơ Wharton + dấu vân tay trong MỘT giao dịch, nhưng `match_results`, dấu vân tay đã lưu và `run_meta` trong một kết nối đọc khác. Có lần chạy xếp chen giữa → bảng điểm chuẩn lẫn dữ liệu cũ/mới. | Quản lý mở Điểm chuẩn đúng lúc lần chạy khác commit. Rất hẹp, chỉ sai hiển thị, không ghi gì. | Đọc cả hai trong cùng giao dịch. | suy luận |

### Ghi chú

- `get_diem_chuan_clb` gọi lại toàn bộ `_ngu_canh_diem_chuan` (đọc lại cả CSDL) mỗi lần bấm một CLB; ổn với ~20 CLB × ~800 em, chưa đo.
- Cảnh báo nạp CSV mang `params["buoi"] = "__mac_dinh__"` (token nội bộ); việc `format_message` có bỏ nó đi hay không thuộc Tầng 4 (chữ & i18n).

### Tóm tắt Tầng 2

`chặn`: 0 · `nên sửa`: 3 (2.1, 2.2, 2.3) · `nhỏ`: 5 (2.4, 2.5, 2.6, 2.7, 2.8). Hai mục cần Truong quyết: **2.1** và **2.2**.

### Quyết định của Truong (28/10/2026, qua phiên điều phối) — GHI CHO VÒNG SỬA, chưa sửa mã

- **2.1 → B:** khi điểm đang khoá, em đã có điểm quyết tâm KHÔNG được đổi nguyện vọng (`submit_preferences`, nạp CSV, sửa ở Quản lý đều trả `wharton_da_khoa`). **Bổ sung từ Tầng 3 (xem 3.2): phạm vi của B phải gồm cả đổi ô tick "muốn thi"** (`submit_test_selection`, nạp CSV chọn thi), vì đổi tick khi đang khoá cũng làm hồ sơ hỏng không sửa được.
- **2.2 → A:** vòng sửa chỉnh docstring và ghi tài liệu "thẻ Quản lý cần người giám sát máy"; không thêm PIN.
- **2.3:** đưa vào danh sách sửa.

### Soát bổ sung vòng 6+7 (`54a5cf4..088573d`) — phần backend và dữ liệu mẫu

Tệp đổi đúng phạm vi A13.6/A13.7: `api_xuat.py` (1 dòng), `so_nhap.py`, `mau_csv/tao_so_nhap.py`, `tests/test_ws_so_nhap.py` (đúng 2 kỳ vọng, đã duyệt), sổ mẫu, 6 sổ `SO_NHAP_DQT_*`, hai JSON, hai script sinh, test mới, tài liệu và skill.

| Mục kiểm | Kết luận | Bằng chứng |
|---|---|---|
| `ghi_so_nhap(luon_co_cot_w=False)` mặc định giữ hành vi cũ | **ĐẠT** | So `54a5cf4` và `088573d` trên 4 cấu hình × (có dữ liệu / sổ trống): từng ô, ô gộp, kiểm dữ liệu, sheet Hướng dẫn **giống hệt**. |
| Chỉ `tao_so_nhap_mau` và `mau_csv/tao_so_nhap.py` truyền True | **ĐẠT** | `grep luon_co_cot_w`: đúng ba chỗ gọi (`api_xuat.py:1079`, `tao_so_nhap.py:78`, `:84`). Script của skill gọi `ghi_so_nhap` không truyền cờ. |
| 4 sổ cũ trong `du_lieu_test/` không đổi byte | **ĐẠT** | `git diff 54a5cf4 088573d` không có tệp nào trong số đó (`SO_NHAP_CO_LOI_CO_Y`, `SO_NHAP_MAU_120HS_3BUOI`, `SO_NHAP_TEST`, `TEST_04_CO_LOI_CO_Y`). |
| 6 sổ `SO_NHAP_DQT_*` mở được, sinh lại cùng nội dung | **ĐẠT** | Chạy `sinh_du_lieu_diem_quyet_tam.py --ra <tạm>`: nội dung 6 tệp (mọi ô mọi sheet) **bằng** tệp đã commit (byte khác do dấu thời gian của openpyxl, chấp nhận). Nạp cả 6 vào CSDL trống (bật và tắt): xem trước và nạp đều `ok`. `HOP_LE` (120 và 800 em): 0 cảnh báo, `run_pipeline` thành công. `TRONG`: 0 dòng `wharton_bids`. |
| Bảng lỗi `DQT_BANG_LOI.json` khớp thực tế | **ĐẠT** | Với `CO_LOI` (15 và 40 em lỗi): mọi `loi_pipeline` và `canh_bao_nhap` ghi trong bảng đều xuất hiện đúng em, đúng quỹ, đúng buổi; **0 em ngoài bảng bị báo**, 0 thiếu. |
| Tắt tính năng: ô có số chỉ cảnh báo | **ĐẠT** | Cả 6 sổ khi tắt: `ok`, đúng một cảnh báo `csv_wp_bo_qua`, không chặn, `wharton_bids` rỗng. |
| Trùng khít 3 bộ × 5 seed so với `e08af78` | **ĐẠT** | Xem phần Tầng 1. |
| Test | **ĐẠT** | `ruff check .` sạch trên `088573d`; 95 ca của `test_du_lieu_mau_diem_quyet_tam`, `test_so_mau_co_cot_quyet_tam`, `test_ws_so_nhap`, `test_dong_goi_skill` đều qua. |

Phát hiện bổ sung từ vòng 6+7:

| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| 2.6 | nhỏ | `so_nhap.py:1232` | `ghi_so_nhap` / `huong_dan` | Sổ MẪU luôn có cột "Điểm quyết tâm" kể cả workspace không thể bật tính năng (ví dụ `priority = "tier"`), và đoạn hướng dẫn nói "chỉ dùng khi phần mềm bật tính năng". Người dùng workspace đó thấy một cột không bao giờ có tác dụng. Điểm theo người đã được loại đúng (`not ca_nhan`). | `tao_so_nhap_mau` trên workspace `priority = "tier"` → sổ có cột; nạp lại → `csv_wp_bo_qua`. Không gây sai kết quả. | Thêm điều kiện "workspace có thể bật" (cùng điều kiện của `cau_hinh_ws._chuan_hoa`) cho `luon_co_cot_w`. | suy luận (đọc mã) |
| 2.7 | nhỏ | `.claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py` (`lam_tron_100`); `api_quan_ly.py` (`phong_theo_ti_le`) | cả hai | Hai bản của cùng một thuật toán làm tròn phần dư lớn nhất. Chủ ý (skill đóng gói riêng, không nhập mã thuật toán), nhưng test chỉ canh ngân sách bằng nhau, không canh hai hàm cho cùng kết quả. | Một bên đổi luật hoà, bên kia không đổi theo → sổ mẫu sinh ra lệch với nút "Phóng". | Thêm một test so hai hàm trên cùng đầu vào ngẫu nhiên. | suy luận |
| 2.8 | nhỏ | `so_nhap.py:965–1000` | `huong_dan`, `_huong_dan_goc` | Dòng đầu docstring của `_huong_dan_goc` dài hơn 100 ký tự (trộn tóm tắt và mô tả); `huong_dan` chèn ghi chú bằng cách tìm dòng "Bước 5." rồi lùi một dòng, dễ vỡ nếu ai đổi chữ hướng dẫn. | Đổi "Bước 5." thành tên khác → ghi chú rơi xuống cuối hướng dẫn, không báo lỗi. | Dùng một hằng đánh dấu vị trí chèn; có test canh vị trí. | suy luận |

### Bốn khía cạnh — Tầng 2

- **Bảo mật:** SQL luôn tham số hoá (`?`), chỉ hai chỗ ghép chuỗi nhận hằng nội bộ. Đường dẫn xuất: tương đối bị rút về tên tệp (`os.path.basename`), thử `../../../../tmp/…` cho kết quả nằm trong thư mục xuất; đường tuyệt đối được tôn trọng nguyên văn theo thiết kế sẵn có (qua `browser_host` thì mọi trang gọi được, xem 2.2). Không có bí mật trong diff. Phát hiện 2.2 (không có xác thực) là điểm bảo mật chính.
- **Hiệu năng (bộ 800 em × 20 CLB × 4 buổi, 5.664 dòng điểm):** nạp sổ 0,42 giây; báo cáo sức khoẻ 0,04; bảng điểm Quản lý 0,04 (cả 500 dòng); danh sách cảnh báo 0,03; chạy phân bổ 0,16; điểm chuẩn 0,04 và chi tiết một CLB 0,08; xuất sổ kết quả 0,32; xuất "cần sửa" 0,04. Không có truy vấn trong vòng lặp theo em ở đường đọc (`_ho_so_wharton_tat_ca` đọc một lần). Đường ghi `phong_wharton_hang_loat` mở một giao dịch mỗi em (N giao dịch, chấp nhận vì cần nhật ký từng em).
- **Đúng đắn:** rollback thật, khoá đặt trong cùng giao dịch, kiểm khoá trong giao dịch ghi, biên rỗng/None/tràn đã thử ở trên; điều kiện tranh chấp: xem 2.4, 2.5.
- **Bảo trì:** lõi `_luu_wharton` dùng chung cho kiosk và quản lý (một bản luật). `api_quan_ly.py` tăng thêm ≈ 800 dòng, nên cân nhắc tách `api_wharton.py` về sau (không gấp).

### Điểm tốt (Tầng 2)

Kiểm hồ sơ đứng trước khoá STB và có test chứng minh; nhật ký chỉ ghi thêm trong cùng giao dịch với thao tác; khoá điểm tách khỏi khoá STB; mã lỗi một nguồn và `i18n_loi.js` khớp bản sinh lại; cấu hình hỏng không làm sập màn kiosk; sổ dữ liệu mẫu có bảng lỗi khớp thực tế từng em.

### Kết luận tầng: **Cần bàn** (không có lỗi `chặn`; 2.1 và 2.2 cần Truong quyết, 2.3 nên sửa trước khi giao)

---

## Tầng 3 — Giao diện

Phạm vi: `index.html`, `js/00_nen.js`, `02_van_hanh.js`, `03_ket_qua.js`, `04_nhap_tai_cho.js`, `05_quan_ly.js`, `075_workspace.js`, `i18n.js`, `style.css`. Chạy giao diện THẬT qua `browser_host` + Chromium (Playwright) trên bộ mô phỏng `SO_NHAP_DQT_120HS_HOP_LE.xlsx` đã chạy phân bổ, ba vai trong cùng một cửa sổ (học sinh ở "Nhập tại chỗ", giáo viên ở Quản lý / Điểm quyết tâm / Điểm chuẩn, quản trị ở Mở khoá / Phóng / Xoá). Tên một CLB và một học sinh được đặt thành `<img src=x onerror=…>` để thử XSS. Script nằm ngoài kho; ảnh chụp ở thư mục tạm, KHÔNG commit.

### Kết quả theo mục yêu cầu

| Mục | Kết luận | Bằng chứng |
|---|---|---|
| 1. Mọi lời gọi API xử lý `ok=false` | **ĐẠT MỘT PHẦN, phát hiện 3.1** | Chèn lỗi giả bằng `page.route` ở ba kiểu (JSON `ok=false`, HTTP 500, đứt mạng). Có thông báo dễ hiểu, không chữ `undefined` / `[object` / `NaN`: kiosk `get_student_entry_state` ("Không tải được thông tin của học sinh này. Hãy thử lại."), `mo_khoa_wharton` ("Không thực hiện được thao tác với điểm quyết tâm…"). **Không có thông báo**: `list_wharton_canh_bao`, `get_diem_chuan`, `get_diem_chuan_clb`, `get_wharton_nhat_ky`, `get_wharton_lock_status` — xem 3.1. Không có lỗi JS chưa bắt (`pageerror` rỗng ở mọi lượt). |
| 2. Dữ liệu người dùng vào `innerHTML` | **ĐẠT** | Mọi `${…}` do A13 thêm trong `js/` đều qua `esc()` (thoát cả `"` và `'`); phần còn lại là số hoặc gán thuộc tính SVG bằng `setAttribute` (nên `aria-label` có tên em vẫn an toàn). Chạy thật: tên CLB / tên em chứa `<img onerror>` hiện NGUYÊN VĂN ở bảng CLB, bảng điểm, điểm chuẩn, hai biểu đồ, danh sách thả xuống, Bước 3; `window.__xss` luôn 0, không hộp thoại. |
| 3a. Tắt tính năng: không còn dấu vết | **ĐẠT MỘT PHẦN, phát hiện 3.4** | Màn hình: không có Bước 3, hai tab con "Điểm quyết tâm" / "Điểm chuẩn" ẩn, không có chữ "quyết tâm" hay "Wharton" ở thẻ nào. Nhưng mỗi lần mở thẻ Quản lý vẫn gọi `list_wharton_canh_bao` và `get_diem_chuan` (để nhận `wharton_chua_bat`). |
| 3b. Đổi ngôn ngữ giữa chừng | **ĐẠT** | Bấm EN khi đang ở tab "Điểm quyết tâm" và "Điểm chuẩn": chữ đổi hết, `<title>` / `aria-label` của biểu đồ SVG đổi ("Tier 2 cut-off of …"); các dòng còn dấu tiếng Việt chỉ là tên học sinh / CLB trong dữ liệu. Bấm lại VI: trở về. |
| 3c. Bấm hai lần không gửi hai lần | **ĐẠT** | `dblclick` trên "Lưu điểm quyết tâm" (kiosk), "Xác nhận mở khoá", "Xác nhận xoá tất cả": đúng **1** yêu cầu `submit_wharton` / `mo_khoa_wharton` / `clear_wharton` (sau khi xoá tất cả thư mục có hai tệp `.bak`: một của bước sao lưu đầu lần chạy phân bổ, một của lần xoá; em chưa tách riêng từng tệp). |
| 4. Kiosk học sinh | **ĐẠT với dữ liệu em khác; KHÔNG ĐẠT với điểm chuẩn (phát hiện 2.2, đã quyết A)** | Chọn một em: vùng làm việc và phản hồi mạng chỉ chứa điểm của em đó (quét mã 6 em khác: 0 lần xuất hiện). Nhưng thẻ "Quản lý CLB & dự trữ" (mục 04 của thanh bên) mở được ngay không cần đăng nhập, và hai tab con "Điểm quyết tâm" (điểm cả khối) và "Điểm chuẩn" (cả biểu đồ phân bố) hiện đầy đủ — **đã tái hiện trên giao diện thật** (ảnh chụp `ql_diem_chuan.png`). |
| 5a. `localStorage` có `try/catch` | **ĐẠT** | Mọi `localStorage.get/setItem` trong `js/` và `i18n.js` nằm trong `try`. Chạy thật với `localStorage` ném `SecurityError` (`Object.defineProperty(window,'localStorage',{get(){throw …}})`): mở Quản lý, đổi tab con, đổi ngôn ngữ, sang tab Kết quả — 0 lỗi JS. |
| 5b. `prefers-reduced-motion` | **ĐẠT** | Có luật toàn cục `*, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important }` (style.css:2401) và riêng cho toast. Chạy với `reduced_motion="reduce"`: 0 phần tử A13 có transition/animation > 0,05 giây (kể cả thanh đếm `wh-thanh-day`). |
| 5c. Bàn phím | **ĐẠT** | Tab con Quản lý: ←/→ chuyển và đặt `aria-selected` đúng (clb→hs→wh→dc), `End` → "Dữ liệu", `Home` → "Câu lạc bộ". Biểu đồ chấm: 11 vùng tương tác có `tabindex=0`, focus hiện tooltip (đọc được khoảng điểm, số được/không được nhận). Ô điểm Bước 3: `type=number`, `min=0`, `step=1`, có `aria-label` ("CLB … — Các CLB đã thi"), `aria-describedby`; gõ `-5` hay `30.5` thì `aria-invalid=true`. |
| 5d. Tương phản biểu đồ | **ĐẠT (sát ngưỡng)** | Tính theo WCAG: thanh "được nhận" `#15714A` / trắng = 6,01; chữ trục `#5B6570` = 5,93; viền chấm "không được nhận" `#8A929B` / trắng = **3,15** (đạt 3:1 cho đồ hoạ), nhưng trên nền `--paper` chỉ 2,85. Hiện biểu đồ nằm trong thẻ trắng nên đạt; nếu ai đặt lên nền `--paper` thì hụt. Mọi nhãn chữ trên biểu đồ ≥ 5,4. Ngoài màu còn có hoa văn gạch và chú giải bảng ẩn (`dc-an-chu`), nên không chỉ dựa vào màu. |
| 6. Chạy giao diện thật ba vai | **XONG** | Học sinh (Nhập tại chỗ, Bước 3 khoá có ghi chú, nút "Lưu điểm quyết tâm" vô hiệu), giáo viên (bảng điểm, điểm chuẩn, biểu đồ, bấm từng CLB), quản trị (mở khoá, xoá tất cả có sao lưu, nhật ký). Ảnh: `hs_buoc3_khoa.png`, `ql_diem_chuan.png`, `ql_bang_diem.png`, `h1_tab_mat.png` (không commit). |

### Phát hiện Tầng 3

| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| 3.1 | nên sửa | `js/05_quan_ly.js:652` (`loadAdminWharton`), `:1800` (`loadAdminDiemChuan`), `:1834` (`loadChiTietDiemChuan`), `:928` (`loadWhNhatKy`), `:668` (`loadWhKhoa`) | các hàm trên | Chú thích nói "chỉ khi API trả `wharton_chua_bat` thì ẩn", nhưng mã coi MỌI `!res.ok` là "tính năng tắt" (ẩn cả tab) hoặc nuốt im lặng (`return`). Lỗi thật (CSDL bận, `ws_cau_hinh_hong`, mã lỗi khác) làm hai tab Wharton biến mất, hoặc nhật ký trống, mà không có dòng báo nào; người quản lý tưởng tính năng đã tắt. | Chèn `ok=false` (`error_wharton_quan_ly`) cho `list_wharton_canh_bao` và `get_diem_chuan` rồi mở thẻ Quản lý: tab con "Điểm quyết tâm" và "Điểm chuẩn" không bao giờ hiện, `#toastStack` rỗng. Chèn lỗi cho `get_wharton_nhat_ky` rồi bấm "Xem nhật ký": toast rỗng. | Chỉ ẩn khi `res.errors[0].code === "wharton_chua_bat"`; lỗi khác thì `showToast` với `trErr`, và giữ nguyên tab / để nút "Thử lại". | đã tái hiện (`t3c.py`, `t3d.py`: H1, H2) |
| 3.2 | nên sửa | backend `submit_test_selection` (+ nạp CSV chọn thi); `js/04_nhap_tai_cho.js` nút `#btnSubmitTestSelection` | `submit_test_selection` | **Bổ sung cho 2.1 (đã chọn B).** Khi điểm đang khoá, đổi ô tick "muốn thi" vẫn được, làm điểm đã lưu thành "ngoài tập" (`wharton_ngoai_tap`) và lần chạy sau bị chặn; em không sửa lại được vì `submit_wharton` bị khoá, nên chỉ còn cách nhờ quản lý mở khoá. Nút "Lưu CLB dự thi" và "Lưu nguyện vọng" vẫn bật trên giao diện khi khoá, và tỉa điểm ở Bước 2 không có thông báo (toast rỗng; bids 7 → 6). | Đã chạy phân bổ (khoá = 1): `submit_test_selection("HS001", ticks − {clb_bcs})` → `ok=True`; `run_pipeline` → `wharton_ho_so_chua_hop_le`, `wharton_ngoai_tap`, `wharton_chua_dung_het`; `submit_wharton` → `wharton_da_khoa`. Trên giao diện: bỏ một nguyện vọng rồi "Lưu nguyện vọng" → `wharton_bids` của em giảm 7 → 6, không báo gì. | Phạm vi của quyết định B phải gồm cả đổi tick; khi khoá thì vô hiệu hoá hai nút lưu ở Bước 1–2 (kèm ghi chú `wharton_da_khoa_kiosk` đã có) và cho `submit_test_selection` / nạp chọn thi trả `wharton_da_khoa` với em đã có điểm. | đã tái hiện (`t3b.py` A, `t3f.py`) |
| 3.3 | nhỏ | `js/05_quan_ly.js` (mở thẻ Quản lý) | nạp thẻ | Khi tắt tính năng, mỗi lần mở thẻ Quản lý vẫn gọi `list_wharton_canh_bao` và `get_diem_chuan` chỉ để nhận `wharton_chua_bat`: "không còn dấu vết" đúng với chữ trên màn hình nhưng không đúng với lời gọi API (hai yêu cầu thừa mỗi lần, và lỗi 3.1 bị lẫn với "tắt"). | Tắt tính năng, mở thẻ Quản lý, đếm `/__api__/`: có `get_diem_chuan` và `list_wharton_canh_bao`. | Trả cờ bật/tắt trong một API cấu hình sẵn có (đã tải lúc vào thẻ) và chỉ gọi hai API kia khi bật. | đã tái hiện (`t3c.py`: E) |
| 3.4 | nhỏ | `style.css:2900` (`.dc-chu-giai`) + dòng chú thích "N học sinh không tính…" (`#dcKhongXet`) | bố cục biểu đồ chấm | Dòng chú thích nằm sát chú giải, không có khoảng cách (phần đuôi chữ "Được nhận" chạm dòng dưới). Chỉ thẩm mỹ. | Ảnh `ql_diem_chuan.png`, chân biểu đồ chấm của CLB có 1 học sinh bị loại khỏi thang. | Thêm `margin-top: 6px` cho dòng chú thích. | đã thấy trên ảnh chụp |

### Bốn khía cạnh — Tầng 3

- **Bảo mật:** không XSS (đã thử bằng tên chứa thẻ `<img onerror>`); `esc()` thoát cả dấu nháy. Không có bí mật trong `js/`. Điểm yếu thật là 2.2 (không xác thực, đã quyết A).
- **Hiệu năng:** vẽ bảng điểm 25 dòng/trang và hai biểu đồ SVG tức thời ở bộ 120 em; bộ 800 em phía backend trả < 0,1 giây (Tầng 2), chưa đo thời gian vẽ DOM ở 800 em × 20 CLB (không có phép đo trình duyệt cho cỡ này).
- **Đúng đắn:** `callApiMoiNhat` bỏ phản hồi cũ khi gõ tìm; bấm đúp không gửi hai lần; đổi ngôn ngữ vẽ lại từ bộ nhớ (`whBoNho`) chứ không chờ API. Lỗi thật: 3.1, 3.2.
- **Bảo trì:** `js/05_quan_ly.js` dài 1.921 dòng (thêm ≈ 1.136 dòng ở A13), nên tách `js/055_wharton_ql.js` về sau. Chú thích mã và thực tế lệch nhau ở 3.1.

### Điểm tốt (Tầng 3)

Thoát HTML nhất quán, có chú thích vì sao `esc()` thoát cả dấu nháy. Mọi `localStorage` có `try/catch` và đã thử với kho bị chặn. Khung số liệu có đủ nhãn, `aria-invalid`, `aria-describedby`, bàn phím cho tab con và biểu đồ, chú giải bảng ẩn cho người đọc màn hình, hoa văn ngoài màu. Chống bấm đúp và bỏ phản hồi cũ. Giảm chuyển động áp dụng toàn cục. Đổi ngôn ngữ vẽ lại ngay, không chờ API.

### Kết luận tầng: **Cần sửa** (không có lỗi `chặn`; 3.1 và 3.2 nên sửa trong vòng sửa; 2.2 đã quyết A)

### Tóm tắt Tầng 3

`chặn`: 0 · `nên sửa`: 2 (3.1, 3.2) · `nhỏ`: 2 (3.3, 3.4).


---

## Tầng 4 — Mã viết sai / vệ sinh

Cách làm: quét tự động trên toàn bộ diff `e08af78..8ad399d` (script ngoài kho), rồi kiểm tay từng chỗ nghi. Gây hỏng tạm 11 chỗ then chốt và hoàn tác từng chỗ bằng ghi đè lại đúng nội dung gốc (`git status` sạch sau mỗi lượt và ở cuối). Chạy 10 lần liền nhóm test giao diện A13.

### Kết quả theo mục yêu cầu

| Mục | Kết luận | Bằng chứng |
|---|---|---|
| 1a. Mã chết | **ĐẠT** | `ruff check .` sạch. Mọi hàm Python và JS A13 thêm mới đều có nơi gọi (script `t4e.py`); mọi API công khai mới của `PipelineAPI` đều được `js/` gọi bằng tên chuỗi. Không có import thừa kể cả ở `.claude/`, `mau_csv/`, `du_lieu_test/` (`ruff --select F401,F841`). |
| 1b. Trùng lặp ≥ 10 dòng | **ĐẠT (một chỗ chủ ý)** | Cửa sổ 8 dòng chuẩn hoá: duy nhất `rbda_priority_pipeline.py:169–176 ↔ 346–353` — khối kiểm "thiếu STB" chép từ `compute_club_priority` vào `uu_tien_wharton`, có chú thích lý do (không sửa hàm cũ). Hai bản làm tròn phần dư lớn nhất khác dáng nên máy không bắt, xem 2.7. |
| 2a. Xưng hô cấm | **ĐẠT** | Quét mọi chuỗi hiển thị: i18n VI/EN của 146 khoá mới, 27 mã lỗi mới, chữ hiển thị thật qua Chromium ở cả tiếng Việt và tiếng Anh (mọi thẻ, ba tab con Quản lý), tiêu đề và hướng dẫn trong 8 sổ Excel mẫu: 0 lần "bạn / các em / you / your". Hai chỗ chữ "bạn" nghĩa là bạn học trong tài liệu (xem 4.2). |
| 2b. "Wharton" lọt ra chữ người dùng thấy | **ĐẠT** | 0 lần trong chữ hiển thị trên giao diện (cả hai ngôn ngữ), thông báo lỗi đã dịch, 8 sổ Excel. Chỉ có ở tài liệu dành cho người bảo trì (ghi rõ "trong mã gọi là `wharton`"). |
| 2c. Khoá i18n thiếu VI/EN | **ĐẠT** | 637 khoá VI = 637 khoá EN, không khoá nào thiếu một bên. Chạy thật tiếng Anh: không còn `{tham_so}` chưa điền, không còn dấu tiếng Việt ở phần chữ giao diện của A13 (hai chuỗi cũ còn sót, xem ngoài phạm vi). |
| 2d. Khoá i18n không ai dùng | **ĐẠT MỘT PHẦN — 4.3** | 146 khoá mới: 2 khoá không ai gọi (`dc_cot_buoi`, `dc_tooltip_so`); 14 khoá `wh_nk_*` và `wh_hl_ly_do_*` được dùng bằng tiền tố động (`whNhan("wh_nk_", …)`), đã đối chiếu đủ mọi giá trị `nguon` / `hanh_dong` backend có thể ghi. |
| 2e. Mã lỗi không qua `i18n_errors.py` | **ĐẠT** | 27 mã lỗi mới đều ở `MESSAGES` có VI và EN, đều được phát ra ở đâu đó, đều có ít nhất một test nhắc tới. Câu đã dịch không lộ token nội bộ (`__mac_dinh__`). |
| 2f. Chuỗi cứng trong JS | **ĐẠT** | Quét dòng JS thêm mới: chuỗi có dấu tiếng Việt trong literal = 0 (6 dòng khớp đều là chú thích). |
| 3. Tài liệu lệch mã | **CẦN SỬA — 4.1, 4.2, 4.4** | CHANGELOG, sổ đăng ký (A13.1–A13.7), `TIEN_DO.md` khớp mã và số liệu (2.761 qua + 3 bỏ qua = 2.764 ca; em chạy mốc 2.699 trước vòng 6+7; cộng 62 ca mới của vòng 6+7 ra 2.761, khớp CHANGELOG). Lệch: `CLAUDE.md` (bản đồ mã, số test), kỹ năng `xu-li-raw-forms`, hai chỗ chữ. |
| 4a. Test yếu (gây hỏng tạm) | **ĐẠT MỘT PHẦN — 4.5** | 11 chỗ gây hỏng, cả 11 bị test bắt, nhưng hai chỗ chỉ bị bắt bởi tệp test KHÁC ngoài tệp "đúng chủ đề", và một test mang tên "rollback" không chứng minh rollback (4.5). |
| 4b. `sleep` cứng | **CHẤP NHẬN (ghi chú 4.6)** | 14 `wait_for_timeout` 100–600 ms trong 7 tệp test giao diện A13 và 1 `time.sleep(0.5)` có chủ đích trong `test_wharton_doc.py:144` (giữ giao dịch đọc để thử ghi chen). |
| 4c. Chập chờn (10 lần liền) | **ĐẠT** | 9 tệp test giao diện A13 (85 ca) chạy 10 lần liền: **10/10 lần `85 passed`**, mỗi lượt 124–127 giây, 0 ca bỏ qua, 0 ca đỏ. |
| 4d. Test bỏ qua im lặng | **ĐẠT** | Mốc 3 ca bỏ qua, đều ngoài A13 (numpy ×2, người dùng thường POSIX ×1). CI đã có chốt "không test giao diện nào bị bỏ qua" (`tests.yml`, lấy mẫu `test_giao_dien_upload.py`); đủ làm đại diện vì cùng một Chromium. |

### Bảng gây hỏng tạm (11 chỗ)

| # | Gây hỏng | Test bắt? |
|---|---|---|
| M1 | Đảo dấu điểm tầng 2: `(1, -w2, …)` → `(1, w2, …)` | Bắt (`test_wharton.py`) |
| M2 | Bỏ kiểm khoá trong `_luu_wharton` | Bắt (`test_wharton_khoa.py`) |
| M3 | Thay `rollback()` bằng `commit()` ở nhánh lỗi giữa chừng của `_run_pipeline_da_khoa` | **Chạy nhóm A13 (`test_wharton_pipeline`, `_khoa`, `_nhat_ky`): XANH, không bắt.** Chỉ bị bắt khi thêm các test chung về rollback (`test_data_durability.py` …). Xem 4.5 |
| M4 | Bỏ `if any(…): continue` trong `tu_dien_wharton_mot_clb` (tự điền đè quỹ em đã đặt) | Bắt |
| M5 | Đảo luật hoà của `phong_theo_ti_le` | Bắt (`test_wharton_hang_loat.py`) |
| M6 | `_chua_co_ket_qua` luôn trả False (tắt khoá xuất) | Bắt |
| M7 | Chạy xong không khoá điểm | Bắt |
| M8 | Tổng 101 điểm được chấp nhận (`> ngan_sach` → `> ngan_sach + 1`) | Bắt, nhưng chỉ khi chạy cả nhóm `tests/test_wharton*.py`; riêng `test_wharton.py` không bắt |
| M9 | Điểm hiệu lực tầng 1 lấy nhầm quỹ 2 | Bắt |
| M10 | Điểm chuẩn tầng 2 lấy `max` thay `min` | Bắt (`test_diem_chuan.py`) |
| M11 | `_luu_wharton` ghi nhầm `tier` (quỹ 1 ↔ 2) | Bắt, nhưng chỉ khi chạy cả nhóm `tests/test_wharton*.py` và test giao diện; `test_wharton_luu_tru.py` + `test_wharton_kiosk.py` riêng không bắt |

### Phát hiện Tầng 4

| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| 4.1 | nên sửa | `CLAUDE.md` (bảng "Bản đồ mã", dòng "tests/") | tài liệu | Bản đồ mã đã trôi: A13 làm `rbda_priority_pipeline.py` từ ~2.187 lên **2.922** dòng, `api.py` ~1.364 lên **1.511**; MỌI số dòng hàm sau `compute_club_priority` sai: `club_choice_function` ghi L236–292, thực tế **L736**; `run_rbda` L315–452 → **L815**; `verify_stability` L456–524 → **L975**; `run_rbda_nhieu_buoi` L877–985 → **L1400**; `generate_stb_lottery` / `chen_stb_cho_hoc_sinh_moi` L1086–1182 → **L1626 / L1652**; `_BANG_RANG_BUOC` L1250 → **L1790**; `DEFAULT_SCHEMA` L1290 → **L1830**; `di_tru_schema` L1568–1666 → **L2176**; `default_reserve_eligible_fn` L1709–1720 → **L2329**; `_run_pipeline_da_khoa` L784–1364 → **L871**; `get_data_health_report` L236 → **L256**. Dòng "tests/" ghi 89 tệp, 1.515 ca; thực tế **138 tệp, 2.764 ca** (`pytest --collect-only`). Bản đồ không có hàm Wharton nào. Phiên sau tin số cũ sẽ đọc nhầm chỗ. | Mở `CLAUDE.md`, đối chiếu `grep -n "^def club_choice_function" rbda_priority_pipeline.py` → 736. | Cập nhật bảng (có thể thay số dòng bằng tên hàm, đúng quy ước "định vị theo TÊN HÀM"), thêm hàng cho nhóm Wharton, sửa số test; cùng việc cho `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`. | đã tái hiện (so số dòng) |
| 4.2 | nhỏ | `.claude/skills/xu-li-raw-forms/SKILL.md` ("bố cục giống hệt sổ mẫu trong kho"); `HUONG_DAN_SU_DUNG.md` (câu "điểm của bạn khác") | tài liệu | (a) Sau A13.7, sổ mẫu trong kho có ba cột mỗi nhóm (CLB, Điểm thi, Điểm quyết tâm) còn sổ do kỹ năng này ghi chỉ hai cột (ghi bằng `ghi_so_nhap` mặc định), nên "giống hệt" không còn đúng. (b) "bạn khác" = bạn học, nhưng bị quy tắc xưng hô quét máy bắt. | (a) `openpyxl` đọc hàng 2 của `mau_csv/SO_NHAP_CLB.xlsx` và của sổ ghi mặc định: `['CLB','Điểm thi','Điểm quyết tâm',…]` so với `['CLB','Điểm thi','CLB',…]`. | (a) Sửa câu thành "cùng bố cục hai hàng tiêu đề; sổ mẫu có thêm cột Điểm quyết tâm". (b) Đổi "của bạn khác" thành "của em khác". | đã tái hiện (a); (b) đọc chữ |
| 4.3 | nhỏ | `i18n.js:632, 655, 1285, 1308` | bảng chữ | Hai khoá `dc_cot_buoi` và `dc_tooltip_so` (VI và EN) không ai gọi (grep `js/`, `index.html`, `*.py`, test). | Đã grep mọi nơi, kể cả tiền tố động `dc_`. | Xoá bốn dòng (hoặc dùng). | đã tái hiện (grep) |
| 4.4 | nhỏ | `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md`, `HUONG_DAN_SU_DUNG.md` | tài liệu | Ba tài liệu nói "trong mã gọi là `wharton`" / "dữ liệu mẫu có Wharton" — chủ ý cho người bảo trì và đúng quy ước, nhưng người đọc tài liệu hướng dẫn sử dụng thấy tên nội bộ. Không lọt ra giao diện hay Excel. | Đọc ba tệp. | Giữ (đã có ghi chú rõ); nếu muốn sạch, chuyển câu bảo trì xuống phần cuối. | đã đọc |
| 4.5 | nên sửa | `tests/test_wharton_khoa.py:87` (`test_chay_hong_giua_chung_rollback_thi_khong_khoa`) | test | Test mang tên "rollback" không chứng minh rollback: nó làm `luat_xep_de_ghi` ném lỗi, nhưng dòng khoá điểm nằm SAU dòng đó nên chưa bao giờ được ghi; thay `rollback()` bằng `commit()` (M3) test vẫn xanh. Rollback thật của A13 (dòng khoá + nhật ký `khoa` nằm trong cùng giao dịch với kết quả) chỉ được test chung (`test_data_durability.py`) bảo vệ gián tiếp. Cùng nhóm: M8 (tổng 101) và M11 (ghi nhầm `tier`) chỉ bị bắt bởi tệp test không phải "tệp chủ đề". | Gây hỏng M3 rồi chạy `test_wharton_pipeline.py test_wharton_khoa.py test_wharton_nhat_ky.py`: `72 passed`. Ngược lại, chèn lỗi giả ngay tại `_ghi_nhat_ky_wharton(… "khoa")` (phần Tầng 2) làm cả 8 bảng nguyên vẹn khi `rollback()` đúng. | Thêm test: `monkeypatch` làm `_ghi_nhat_ky_wharton` ném lỗi khi `hanh_dong == "khoa"`, rồi khẳng định `match_results`, `run_history`, `wharton_lock`, `stb_lock` y nguyên; thêm ca biên tổng 101 / 99 vào `test_wharton.py`. | đã tái hiện (`t4m.py`) |
| 4.6 | nhỏ | `tests/test_giao_dien_wharton_quan_ly.py:135, 237, 260, 319, 391, 403` và 8 chỗ khác | test giao diện | 14 `wait_for_timeout(100–600 ms)` đợi cố định thay vì đợi điều kiện. Chưa thấy chập chờn (xem 4c) nhưng sẽ dễ vỡ trên máy chậm (CI). | Máy CI chậm gấp vài lần → ô chưa vẽ xong khi kiểm. | Đổi sang `wait_for_selector` / `wait_for_function` theo điều kiện. | suy luận |

### Ghi chú ngoài phạm vi (một dòng)

- Khi đang mở một học sinh rồi đổi ngôn ngữ, hai chuỗi cũ ở Bước 2 (`fallback_phu_buoi` "Đã xếp hạng ở 3/3 buổi" và liên kết `btn_remove_ranked` "xoá") không vẽ lại sang tiếng Anh. Khoá có sẵn từ trước A13 và đều có bản EN; Bước 3 của A13 vẽ lại đúng.

### Bốn khía cạnh — Tầng 4

- **Bảo mật:** không bí mật, không `eval`/`exec`/`os.system`; `subprocess` trong test dùng danh sách đối số, không `shell`.
- **Hiệu năng:** không có mã chết gây tốn; test giao diện A13 mất 125 giây mỗi lượt cho 85 ca.
- **Đúng đắn:** xem 4.5 (test không chứng minh điều nó nói).
- **Bảo trì:** hai bản thuật toán làm tròn (2.7), tài liệu lệch mã (4.1, 4.2), hai khoá chết (4.3), `api_quan_ly.py` +800 dòng và `js/05_quan_ly.js` +1.136 dòng (nên tách, không gấp).

### Điểm tốt (Tầng 4)

Không có mã chết hay import thừa; chỉ một khối trùng lặp và có lý do ghi rõ. Chữ hiển thị sạch ở cả hai ngôn ngữ (không xưng hô cấm, không tên nội bộ, không tham số chưa điền). Mọi mã lỗi đi một nguồn và đều có test. Mười một lần gây hỏng cố ý đều bị bắt bởi ít nhất một test. CHANGELOG, sổ đăng ký và `TIEN_DO.md` khớp số liệu đo thật.

### Kết luận tầng: **Cần sửa** (không có lỗi `chặn`; 4.1 và 4.5 nên sửa; còn lại nhỏ)

### Tóm tắt Tầng 4

`chặn`: 0 · `nên sửa`: 2 (4.1, 4.5) · `nhỏ`: 4 (4.2, 4.3, 4.4, 4.6).
