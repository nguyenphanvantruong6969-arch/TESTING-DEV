# Chi tiết tách khỏi CLAUDE.md (giữ nguyên nội dung)

> Tách ra để CLAUDE.md nhẹ. Nội dung dưới đây chưa đổi, chỉ chuyển chỗ.

## Bản đồ mã (định vị theo TÊN HÀM, KHÔNG ghi số dòng: số dòng trôi sau mỗi đợt sửa; muốn số dòng chạy `grep -n "^def <tên>" <tệp>`. Bảng đối chiếu 08/10/2026 và bảng cập nhật 28/10/2026 ở `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`)
| Tệp | Vai trò | Hàm then chốt |
|---|---|---|
| `rbda_priority_pipeline.py` (~2.950 dòng) | Thuật toán, schema, I/O SQLite | `compute_club_priority` · `club_choice_function` · `run_rbda` · `verify_stability` · `run_rbda_nhieu_buoi` · `generate_stb_lottery`, `chen_stb_cho_hoc_sinh_moi` · `_BANG_RANG_BUOC`, `DEFAULT_SCHEMA` · `di_tru_schema` · `default_reserve_eligible_fn` |
| Điểm quyết tâm (trong mã gọi là `wharton`; giao diện: "Xét điểm quyết tâm") | Tầng 2: mỗi em chia 100 điểm mỗi quỹ mỗi buổi; khoá sau lần chạy đầu | `rbda_priority_pipeline.py`: `khoa_uu_tien_wharton`, `uu_tien_wharton`, `kiem_ho_so_wharton`, `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc`, `dung_wharton`, `doc_du_lieu_wharton`, `load_wharton_kem_doc_them` · `api_quan_ly.py`: `submit_wharton`, `admin_save_wharton`, `phong_wharton_hang_loat`, `clear_wharton`, `mo_khoa_wharton`, `list_wharton_admin`, `get_diem_chuan`, `get_diem_chuan_clb`, `tinh_diem_chuan`, `_luu_wharton_cur`, `_ghi_nhat_ky_wharton` · `api_xuat.py`: `export_wharton_can_sua` · JS: `renderWhartonStep`, `whartonVeKhung` (`js/04_nhap_tai_cho.js`), `loadAdminWharton`, `loadAdminDiemChuan` (`js/05_quan_ly.js`) |
| `api.py` (~1.560 dòng) | `PipelineAPI`: pipeline 5 bước | `_run_pipeline_da_khoa` (rollback ở khối bắt lỗi cuối hàm; dòng khoá điểm và dòng nhật ký hành động "khoa" nằm TRONG cùng giao dịch với kết quả) · `get_data_health_report` · `_backup_db` |
| `api_nhap.py`, `api_xuat.py`, `api_quan_ly.py`, `api_bao_cao.py`, `api_cham_diem.py`, `api_chung.py` | Nhập/xuất CSV-Excel, quản lý, báo cáo, chấm điểm mù, tiện ích | `import_csv_auto`, `import_preferences_csv` (api_nhap) · `_duong_xuat` (api_xuat) · `submit_preferences`, `delete_student`, `reset_data` (api_quan_ly) |
| `fa_daa.py`, `fa_ly_do.py`, `fa_bien_ban.py` | FA-DAA (mục A13/A5/A6/C3; chỉ chạy khi `rules.fa_daa` bật, mặc định TẮT): lớp bọc quanh `run_rbda_nhieu_buoi`, lõi DA không đổi; mẫu câu lý do ở MỘT nơi (`fa_ly_do.py`) | `chay_fa_daa` · `kiem_truoc_fa` · `kiem_ho_so_huy_chuong` · `diem_huy_chuong_hieu_luc` · `ly_do_ket_qua` · `bang_nhu_cau` · `kiem_chi_tang` · `cau_ly_do`; API: `submit_huy_chuong`, `export_ly_do_csv`, `export_bang_nhu_cau`, `export_bien_ban_boc_tham` (FA-9); các bảng giu_cho, fa_nhom, fa_ly_do |
| `fa_sau_xep.py`, `api_sau_xep.py` | FA gaps — sau khi xếp (V§9.2–9.3): nhật ký điều chỉnh CHỈ GHI THÊM (bảng fa_dieu_chinh), chỗ hiện tại = lần chạy gốc + điều chỉnh phát lại theo id; match_results, run_history không bao giờ bị sửa | `vi_tri_hien_tai` · `run_goc_theo_buoi` · `doc_vi_tri` · `ghi_dieu_chinh` · `can_giai_phong` · `hang_cho` · `moi_tiep` · `moi_dang_cho`; API `get_diem_danh`, `luu_diem_danh`, `export_diem_danh`, `get_moi_cho_trong`, `tra_loi_moi` (cờ `rules.fa_diem_danh`); `trong_han_khieu_nai` · `anh_huong_sau_chay_lai`; API `gui_khieu_nai`, `get_khieu_nai`, `xu_ly_khieu_nai`, `export_khieu_nai` (cờ `rules.fa_khieu_nai`); `chay_vong_2` · `can_vong_2` · `cho_con_lai`; API `get_vong_2`, `chay_vong_2_api` (cờ `rules.fa_vong_2`); `tong_hop_phan_hoi` · `doc_tep_forms_phan_hoi`; API `gui_phan_hoi`, `get_phan_hoi_tong_hop`, `nhap_phan_hoi_forms`, `export_phan_hoi` (cờ `rules.fa_phan_hoi`); Forms (TH) `tao_mau_forms.py --phan-hoi`, `--tuan-3`; bảng fa_dieu_chinh, fa_diem_danh; giao diện `js/10_theo_doi.js` |
| `mau_forms_thi_clb/phan_tich_cau_hoi.py`, `mau_forms_thi_clb/danh_sach_chua_dang_ky.py` | FA gaps công cụ (TH): độ lệch hai người chấm (GAP-9, lệnh "lech"); danh sách chưa đăng ký theo lớp + tỉ lệ, cờ DUOI_50 (GAP-10; hướng dẫn `docs/he_sinh_thai/T4M_FLOW_NHAC_HAN.md`) | do_lech_cham · ghi_bao_cao(do_lech=) · ty_le_dang_ky · doc_da_dang_ky |
| `lop_hoc_sinh.py` | `chuan_hoa_lop` (A14, stdlib; skill xu-li-raw-forms đóng gói theo; pipeline nhập lại giữ tên) | `chuan_hoa_lop` |
| `so_nhap.py`, `so_excel.py` | Sổ nhập CLB: MỘT tệp Excel thay ba tệp nạp; nguồn duy nhất của định dạng (skill trong `.claude/skills/` cũng dùng) | `import_so_nhap`, `xem_truoc_so_nhap` (api_nhap.py) |
| `i18n_errors.py` → `tao_i18n_js.py` → `i18n_loi.js` | Thông báo lỗi song ngữ, **một nguồn** | `err`, `phan_hoi_ok`, `phan_hoi_loi` |
| `browser_host.py`, `recovery.py`, `chan_doan.py`, `main.py` | Máy chủ dự phòng 127.0.0.1, phục hồi, log, điểm vào | |
| `index.html`, `js/00…08_*.js`, `i18n.js`, `style.css` | Giao diện; gọi backend qua `window.pywebview.api.*`, trả `{ok, data, errors}` | |
| `tests/` | 240 tệp `test_*.py`, 3.645 ca (`pytest --collect-only`, 06/11/2026, nhánh claude/upbeat-shannon-g5nnms sau T4M-BK) | `test_pipeline_core.py`, `test_nhieu_buoi.py::TestTrungKhit`, `test_toi_uu_on_dinh.py`, `test_boc_tham.py`, … |
| `du_lieu_test/` (gồm `mo_phong_fa_daa.py`, FA-10: chỉ in bảng số, nhãn "SỐ LIỆU MÔ PHỎNG"), `mau_csv/`, `docs/`, `BAN_GIAO.md` | Bộ dữ liệu mô phỏng, script đo, mẫu nhập, tài liệu cơ chế, nhật ký 25 lỗi đã sửa | |

## 12 ngành đích (mã dùng trong mọi tệp)
| Mã | Ngành | Mục R riêng | Điểm công sức | Số mục trong kế hoạch |
|---|---|---|---|---|
| `DT` | Phân bổ đề tài, đồ án, người hướng dẫn | 3 | 10 | 7 |
| `KTX` | Ký túc xá, nhà ở sinh viên, nhà ở xã hội | 8 | 20 | 15 |
| `SK` | Sự kiện, hội nghị (workshop, phản biện, gặp doanh nghiệp) | 9 | 22,5 | 17 |
| `NT` | Hoạt động ngoài trường, trại hè, khoá ngắn, tình nguyện | 9 | 23,5 | 13 |
| `YT` | Y tế (học viên thực hành, luân khoa, nội trú) | 8 | 26 | 14 |
| `VL` | Nền tảng việc làm tự do, crowdsourcing | 8 | 28 | 18 |
| `KT` | Kỹ thuật – sản xuất (kỹ sư vào dự án, tác vụ vào máy) | 10 | 29 | 17 |
| `HP` | Phân bổ học phần, môn tự chọn | 10 | 29,5 | 17 |
| `TS` | Tuyển sinh cấp trường (lớp 6, lớp 10, trường tư, chọn ngành) | 13 | 37 | 21 |
| `NS` | Nhân sự nội bộ (tân tuyển, thực tập, luân chuyển, giáo viên) | 13 | 37 | 20 |
| `LG` | Logistics – vận tải (đơn hàng cho xe, tài xế cho tuyến) | 12 | 44 | 21 |
| `TC` | Tài chính – ngân hàng (chia khách hàng, hồ sơ thẩm định) | 17 | 50,5 | 23 |

Thứ tự làm chung khi chuẩn bị nhiều ngành: `Z6 → Z3 → Z7 → Z4 → Z5 → Z2 → Z1 → B1 → B2 → A1 → A2 → A3 → A4 → A5 → A6 → A7 → A8 → A9 → A10 → A11 → A12 → B3 → C1 → C2 → C3 → E1 → E2 → E3 → G1 → G2 → G3 → G4 → G5`

## Kiểm verify nhanh (chuyển từ CLAUDE.md, 05/11/2026)
- Chạy: `pip install numpy` (chỉ cho kịch bản tham khảo, KHÔNG thêm vào requirements) rồi `python docs/ke_hoach/tham_khao/kiem_verify_nhanh.py <thư mục chứa rbda_priority_pipeline.py>`.
- Test `tests/test_tham_khao_verify_nhanh.py` (không cần numpy) canh `verify_stability_nhanh`, `exp_resume.resume_da` / `kiem_tien_de`, `_chung.nap_rb` (thư mục: nạp thẳng tệp .py, cùng bản, bản khác, tiến trình mới, mô-đun anh em lạ; tệp không phải PyInstaller); `_chung.gen` chỉ được kiểm khi có numpy; đường nạp `.exe` được kiểm bằng một tệp PyInstaller tối thiểu dựng trong test (không có bản build thật trong kho).
- Thời gian toàn bộ bộ test: ~22 phút trên máy 4 nhân kèm test giao diện Chromium; `BAN_GIAO.md` ghi ~3,5 phút, chưa giải thích được (xem `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`).

## Tài liệu tham khảo thêm
4. Trong kho: `BAN_GIAO.md`, `docs/CO_CHE_THUAT_TOAN.md`, `docs/NGHIEN_CUU_TOI_UU.md`, `docs/GIAI_DAP_BOC_THAM.md`, `docs/KE_HOACH_NHIEU_BUOI.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`.
5. Tham khảo: `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản thay `verify_stability`, mục Z4), `kiem_verify_nhanh.py`, `exp_resume.py` (tiếp tục DA từ trạng thái cũ, mục G1).
