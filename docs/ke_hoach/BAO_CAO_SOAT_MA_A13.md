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
| 1.1 | nhỏ | `rbda_priority_pipeline.py:357` (`khoa` trong `uu_tien_wharton`) | `uu_tien_wharton` / `khoa_uu_tien_wharton` | Điểm thi `NaN` làm `sorted` cho thứ tự không xác định. | Ở mức hàm: `tested_scores_for_club = {"A": nan, "B": 5.0, "C": 5.0}` → `['A','B','C']`. **Cập nhật sau Tầng 2:** không tới được qua API — `submit_club_scores` với `nan`, `"nan"`, `inf`, `"1e999"`, `-1` trả `ok=True` nhưng KHÔNG lưu dòng nào (bỏ im lặng; mã cũ, ngoài A13). | Không cần sửa ở A13. Ghi ở mục ngoài phạm vi: `submit_club_scores` bỏ im lặng điểm xấu mà vẫn báo `ok`. | đã tái hiện (`t1.py`, `t2k.py`) |
| 1.2 | nhỏ (đóng) | `rbda_priority_pipeline.py:415–416` (`la_diem_hop_le`) | `kiem_ho_so_wharton` | Điểm `100.0` (số thực nguyên) bị coi không hợp lệ ở mức hàm. **Cập nhật sau Tầng 2: không xảy ra thật** — Sổ nhập đi qua `o_thanh_chu` (`100.0 → "100"`, đã thử với ô Excel `100.0`), CSV dùng `[0-9]{1,9}`, JSON từ giao diện gửi số nguyên. | `w1={"A":{"X":100.0}}` chỉ lỗi khi gọi trực tiếp hàm. | Không cần sửa. | đã tái hiện ở mức hàm; không có đường thật |

**Không có phát hiện mức `chặn` hay `nên sửa` ở Tầng 1.** Không có đường nào cho thứ hạng nguyện vọng hay kết cục buổi trước đi vào khoá ưu tiên.

### Ghi chú ngoài phạm vi (một dòng)

- `submit_club_scores` bỏ im lặng điểm `NaN`/`inf`/âm/`"1e999"` mà vẫn trả `ok=True` (không lưu dòng nào, không báo): người chấm tưởng đã lưu. Mã cũ, không do A13.

### Tóm tắt Tầng 1

`chặn`: 0 · `nên sửa`: 0 · `nhỏ`: 2 (1.1, 1.2 — cả hai đã hạ xuống "không có đường thật" sau Tầng 2).

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
| 2.2 | nên sửa | `api_quan_ly.py:700` (docstring `get_diem_chuan`); `browser_host.py:300` | `get_diem_chuan`, `get_diem_chuan_clb`, `list_wharton_admin`, `get_wharton_nhat_ky` | Docstring nói "CHỈ cho quản trị … không có đường nào cho kiosk gọi hàm này", nhưng không có xác thực nào: `browser_host` cho gọi MỌI phương thức công khai, và thẻ "Quản lý" là một mục điều hướng ngang hàng (`index.html:44`, không mật khẩu). Học sinh ngồi ở máy mở được điểm quyết tâm của cả khối, điểm chuẩn và nhật ký. Mẫu này có từ trước (`list_students_admin` cùng mức) nhưng A13 thêm dữ liệu nhạy hơn (điểm chuẩn có thể bị dùng để "tính điểm vừa đủ"). | `a.get_diem_chuan()` gọi trực tiếp, không thông tin xác thực → `ok=True` với toàn bộ dòng điểm chuẩn; qua HTTP: `POST /__api__/get_diem_chuan`. Tầng 3 sẽ kiểm trên giao diện thật. | Hỏi Truong: (A) sửa docstring cho đúng thực tế và ghi "thẻ Quản lý đặt sau cửa vật lý / người giám sát" vào `HUONG_DAN_SU_DUNG.md`; (B) thêm mã quản trị (PIN) cho thẻ Quản lý — việc lớn, ngoài phạm vi A13, cần mục riêng trong sổ đăng ký. Đề xuất A ngay, B ghi thành mục mới. | đã tái hiện (gọi không xác thực); giao diện: chờ Tầng 3 |
| 2.3 | nên sửa | `api_xuat.py:376–377` | `_trang_diem_chuan` | `get_diem_chuan` lỗi thì `rows = []` và `rong=""` (vì `co_ket_qua` đúng): sổ kết quả xuất `ok=True` với trang "Điểm chuẩn" trống, không dòng chữ nào giải thích. Trường nhận một tệp thiếu mà tưởng đầy đủ. | Giả lỗi `get_diem_chuan` (trả `error_reading_results`) sau một lần chạy thành công → `export_ket_qua` `ok=True`, trang "Điểm chuẩn" chỉ có tiêu đề và hàng đầu cột. Lỗi thật có thể đến từ CSDL bận / cấu hình hỏng giữa hai lần đọc. | Khi `kq["ok"]` sai thì ghi một dòng cảnh báo vào trang (hoặc cho cả lần xuất thất bại). | đã tái hiện (`t2i.py`, lỗi giả) |
| 2.4 | nhỏ | `api_quan_ly.py:971` (`_ke_hoach_phong`), `:927` | `phong_wharton_hang_loat` | Kế hoạch tính từ MỘT ảnh chụp, rồi ghi từng em bằng giao dịch riêng: (a) không nguyên tử — dừng giữa chừng thì một phần em đã phóng; (b) nếu em tự sửa điểm trên kiosk đúng lúc đó, bản phóng (tính từ điểm cũ) ghi đè điểm mới; (c) khi gặp `wharton_da_khoa` giữa chừng, hàm trả thẳng lỗi và mất `n_phong`. Có sao lưu và nhật ký nên phục hồi được. | Hai phiên cùng máy: quản lý bấm "Phóng" khi một em đang lưu điểm. Hẹp. | Chấp nhận, hoặc đọc lại điểm hiện tại của em trong `_luu_wharton` và bỏ qua nếu khác ảnh chụp. | suy luận |
| 2.5 | nhỏ | `api_quan_ly.py:663` | `_ngu_canh_diem_chuan` | Đọc dữ liệu + hồ sơ Wharton + dấu vân tay trong MỘT giao dịch, nhưng `match_results`, dấu vân tay đã lưu và `run_meta` trong một kết nối đọc khác. Có lần chạy xếp chen giữa → bảng điểm chuẩn lẫn dữ liệu cũ/mới. | Quản lý mở Điểm chuẩn đúng lúc lần chạy khác commit. Rất hẹp, chỉ sai hiển thị, không ghi gì. | Đọc cả hai trong cùng giao dịch. | suy luận |

### Ghi chú

- `get_diem_chuan_clb` gọi lại toàn bộ `_ngu_canh_diem_chuan` (đọc lại cả CSDL) mỗi lần bấm một CLB; ổn với ~20 CLB × ~800 em, chưa đo.
- Cảnh báo nạp CSV mang `params["buoi"] = "__mac_dinh__"` (token nội bộ); việc `format_message` có bỏ nó đi hay không thuộc Tầng 4 (chữ & i18n).

### Tóm tắt Tầng 2

`chặn`: 0 · `nên sửa`: 3 (2.1, 2.2, 2.3) · `nhỏ`: 2 (2.4, 2.5). Hai mục cần Truong quyết: **2.1** và **2.2**.
