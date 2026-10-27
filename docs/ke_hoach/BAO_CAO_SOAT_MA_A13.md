# Báo cáo soát mã A13 (Điểm quyết tâm / Wharton) — 4 tầng

> Soát CHỈ BÁO CÁO, không sửa mã. Dữ liệu là MÔ PHỎNG. Không subagent, không `/code-review`.
> Phạm vi: `git diff e08af78..54a5cf4` (A13 vòng 1–5, trên `main`) + hàm cũ mà mã A13 gọi vào hoặc sửa.
> Vòng 6+7 (A13.6, A13.7) chưa đẩy: sẽ soát BỔ SUNG khi phiên điều phối báo, rồi mới push.
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
| 1.1 | nhỏ | `rbda_priority_pipeline.py:357` (`khoa` trong `uu_tien_wharton`) | `uu_tien_wharton` / `khoa_uu_tien_wharton` | Điểm thi `NaN` làm `sorted` cho thứ tự không xác định. | `tested_scores_for_club = {"A": nan, "B": 5.0, "C": 5.0}` → `['A','B','C']` (so sánh `nan` luôn sai). | Không cần sửa ở A13: `compute_club_priority` (mã cũ) có cùng hành vi; chặn `NaN` nên ở khâu nhập điểm (Tầng 2, `submit_club_scores`). | đã tái hiện (script `t1.py`, mục NaN) |
| 1.2 | nhỏ | `rbda_priority_pipeline.py:415–416` (`la_diem_hop_le`) | `kiem_ho_so_wharton` | Điểm `100.0` (số thực nguyên, kiểu Excel/JSON hay trả) bị coi KHÔNG hợp lệ, và báo thêm `wharton_chua_dung_het` (hai lỗi cho một ô, trái câu "tối đa một lỗi" trong docstring cho trường hợp giá trị xấu). | `w1={"A":{"X":100.0}}` → `['wharton_diem_khong_hop_le','wharton_chua_dung_het']`. Chỉ thành lỗi thật nếu lớp nạp (Tầng 2) không đổi `100.0`→`100`; sẽ kiểm ở Tầng 2. | Nếu lớp API không ép kiểu: chấp nhận `float` có `is_integer()` hoặc ép ở API; sửa docstring cho khớp. | đã tái hiện ở mức hàm; ảnh hưởng thật: chờ Tầng 2 |

**Không có phát hiện mức `chặn` hay `nên sửa` ở Tầng 1.** Không có đường nào cho thứ hạng nguyện vọng hay kết cục buổi trước đi vào khoá ưu tiên.

### Ghi chú ngoài phạm vi (một dòng)

- `compute_club_priority` và `uu_tien_wharton` đều sắp theo `-điểm` kiểu `float`: nếu có `NaN` lọt vào bảng `club_scores` thì thứ tự không tất định (mã cũ, không do A13).

### Tóm tắt Tầng 1

`chặn`: 0 · `nên sửa`: 0 · `nhỏ`: 2 (1.1, 1.2).
