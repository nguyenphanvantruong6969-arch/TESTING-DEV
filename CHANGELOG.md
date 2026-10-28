# CHANGELOG

## 2026-10-28 — A13.10 Nhãn "Xét điểm thi / Xét điểm quyết tâm" và thiết kế lại màn Điểm chuẩn

Theo yêu cầu của Truong (duyệt ba điểm: sửa bộ chọn test giao diện cũ; biểu đồ chỉ khối Điểm chuẩn tự đổi nền tối vì ứng dụng chưa có giao diện tối chung; EN dùng "commitment points" trong cả khối). Chỉ đổi cách hiện; API `get_diem_chuan` / `get_diem_chuan_clb`, schema, hợp đồng cột CSV, thuật toán và kết quả xếp KHÔNG đổi. Mô phỏng.
- **1. Nhãn hiển thị:** "Tầng 1" thành "Xét điểm thi" / "Exam-based", "Tầng 2" thành "Xét điểm quyết tâm" / "Commitment points" ở giao diện (`i18n.js`, khoá `dc_*`, VI và EN), tệp xuất Excel (`api_xuat.py`: tiêu đề cột và mô tả trang Điểm chuẩn) và hướng dẫn (`HUONG_DAN_SU_DUNG.md`, `README.md`, `TAI_LIEU_DU_LIEU.md`, `GIAI_THICH_DE_HIEU.html`, `BAO_CAO_CACH_CHAY.html`, `mau_csv/vi_du_day_du/GIAI_THICH.md`). Nơi cần danh từ thì ghi "nhóm xét điểm thi / nhóm xét điểm quyết tâm". Mã, biến, cột, mã lỗi giữ `tier`, `tang1`, `tang2`. Chưa đổi: `poster/`, chú thích trong `.py`, `BAN_GIAO.md` và các tài liệu kế hoạch nội bộ.
- **2a. Bảng tổng** (`js/05_quan_ly.js`, `veTongQuanDiemChuan`): hai cột điểm chuẩn riêng, mỗi ô một thanh SVG (thang điểm thi 10 / 100 tự chọn theo dữ liệu, điểm quyết tâm 0 đến 100); bỏ dòng chữ nhỏ dưới tên CLB (mã `dc-phu`).
- **2b. Đơn / chỗ:** số kèm thanh tỉ lệ nhỏ (tối đa 5 lần chỗ, vạch mốc ở 1 lần), màu theo mức: xanh đến 1, vàng đến 2, đỏ trên 2 (`data-muc` = `thap` / `vua` / `cao`); thay chấm đỏ. Chú giải ba mức.
- **2c. Chi tiết một CLB:** histogram và dải chấm cũ gộp thành MỘT SVG beeswarm (`veChiTietDiemChuan`, `svg[data-bieu-do=chi-tiet]`): chấm cùng điểm xếp cột không chồng nhau, vạch chuẩn ghi số, vùng nhạt bên phải vạch là vùng được nhận, chấm đặc xanh được nhận / chấm rỗng xám không được nhận, chú giải ba mục, tooltip và bảng chữ ẩn giữ nguyên. Xoá `veCotPhanBoQuyetTam`, `veDaiChamQuyetTam`, `dcCotTronTren` và khoá i18n không còn dùng (`dc_cot_chuan`, `dc_nong`, `dc_cot_tieu_de`, `dc_truc_y`, `dc_tooltip_khoang`, `dc_tooltip_so`); khoá mới `dc_ti_le_*`.
- **Sáng / tối, chuyển động** (`style.css`): màu qua biến; `prefers-color-scheme: dark` (và `[data-theme=dark]`) chỉ đổi khối Điểm chuẩn sang nền tối; hiệu ứng chấm vào dần chỉ chạy khi `prefers-reduced-motion: no-preference`. Không thư viện ngoài.
- **Test mới:** `tests/test_giao_dien_a13_10_nhan.py` (5 ca: nhãn VI / EN, khoá `dc_*`, tài liệu) và `tests/test_giao_dien_a13_10_diem_chuan.py` (9 ca: hai cột, bỏ chữ phụ, thanh tỉ lệ và màu, một SVG, chấm không chồng, chú giải và tooltip, reduced-motion, chế độ tối, EN). **Test cũ sửa có duyệt:** `tests/test_giao_dien_diem_chuan.py` đổi bộ chọn (`svg[data-bieu-do=cot|cham]`, `#dcCot`, `#dcCham` thành `svg[data-bieu-do=chi-tiet]`, `#dcBieuDo`; hai test (a), (b) gộp một); `tests/test_diem_chuan.py` đổi chữ tiêu đề cột Excel.
- **Ảnh trước / sau:** `docs/anh/a13_10/{truoc,sau}_{vi,en}_{sang,toi}.png` từ `du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx`, seed 3, chụp bằng `docs/anh/a13_10/chup_anh.py`. Ảnh "trước" có "Tầng 1/2" vì chụp từ bản gốc; ứng dụng chưa có giao diện tối chung nên ảnh "tối" chỉ khác ở khối Điểm chuẩn.

## 2026-10-28 — A13.9 Sửa 9 vấn đề từ đợt stress test

Theo danh sách Truong đã chốt (mục 1–9; #10 numpy không làm). Mô phỏng. Tắt Điểm quyết tâm: kết quả trùng khít `e08af78` (`kiem_nhanh.py --co-so e08af78`, 15 ca, 3 bộ × 5 seed). Test mới: `tests/test_a13_9_stress.py` (mỗi mục đỏ trước, xanh sau).
- **1. CSDL bận:** mã lỗi mới `csdl_dang_ban` (`CsdlBan`, con của `CauHinhHong`, nên mọi nơi đang dừng vẫn dừng; `loi_cau_hinh(e)` chọn mã). `connect_db(cho_khoa_ms=)`; `cau_hinh_ws.CHO_KHOA_DOC_CAU_HINH_MS = 2500`. Tệp: `rbda_priority_pipeline.py`, `cau_hinh_ws.py`, `api_workspace.py`, `api*.py`, `i18n_errors.py`, `i18n_loi.js`. Lưu ý: `run_pipeline` vẫn chờ tới 15 s ở bước sao lưu (cố ý: rút ngắn là bỏ qua sao lưu khi khoá ngắn).
- **2, 3, 5. `browser_host.py`:** `_Handler.timeout = 45`; `_token_khop` so token trên byte (token không ASCII ở tiêu đề / `?t=` → 403); `loi_ngoai_du_kien` chỉ trả tên kiểu ngoại lệ, thông điệp thật nằm ở `loi_ung_dung.txt`.
- **4. `chan_doan.py`:** `loi_ung_dung.txt` trần `TRAN_LOG_UNG_DUNG_BYTE` = 1.000.000, cắt xuống 75 % giữ phần cuối ở ranh giới mục; bỏ mục trùng hệt mục ngay trước (khác giờ). Log khởi động không đổi.
- **6. `api_xuat.py`:** `_duong_xuat` với đường tuyệt đối cũng đi qua `duong_dan_khong_de` (kể cả `kem_duoi`): `x (2).xlsx`. Áp cho mọi hàm xuất và `export_workspace`.
- **7. `workspace.py`:** `nhap_zip` — `TRAN_SO_TEP_ZIP = 1000`, `TRAN_GIAI_NEN_BYTE` hạ 500 → 200 MB, từ chối tên trùng (chuẩn hoá dấu phân cách, hoa/thường), kiểm NUL trên `orig_filename` (trước đây `zipfile` cắt tên nên kiểm NUL không bao giờ bắt được).
- **8. Sổ rỗng:** `so_nhap.py` bỏ lỗi `so_nhap_khong_co_clb`; `api_nhap.py` báo `so_nhap_canh_bao_khong_co_clb` / `so_nhap_canh_bao_khong_co_hs`, bỏ bước nạp CLB khi sổ không có CLB; `run_pipeline` sau đó chạy được.
- **9. Skill `sinh-du-lieu-clb`:** quá 20 CLB tự sinh "CLB Chuyên đề N"; ≤ 20 giữ đúng từng byte (băm 6 cấu hình so với `0f13771`).
- **Test cũ (Truong chọn 1A, 2A, 28/10/2026):** thêm 3 mã vào `MA_MOI_SAU_ANH_CHUP` (`tests/test_ws_nhan.py`); hai test sửa có duyệt — `test_nap_xuat_ca_hiem.py::test_khong_con_tep_cua_lan_xuat_truoc` gọi thẳng `_ghi_bo_csv` hai lần trên cùng đường (qua `export_csv` giờ ra `x (2).csv`, không còn ghi đè tại chỗ); `test_so_nhap.py::test_ma_trong_dung_lai_clb_cung_ten_va_bao_clb_ngoai_so` thêm một em vào sổ để không dính cảnh báo sổ rỗng.
- **Kiểm:** `kiem_nhanh.py` 7/7. Toàn bộ test có Chromium, `-rs`, phủ 93 %: 2.902 qua, 2 đỏ trước khi sửa hai test trên (chạy lại hai tệp đó: 95 qua), 1 bỏ qua (cần người dùng thường trên POSIX). `ruff check .` sạch. **Chưa làm:** chạy lại s3/s8 `--nhanh` và cột "Đã sửa ở commit" — `VAN_DE_STRESS_TEST.md`, `BAO_CAO_STRESS_TEST.md` và kịch bản s3/s8 chưa có trên nhánh (Truong chọn 4A: chờ đẩy lên rồi làm).

## 2026-10-28 — A13.8 Sửa 12 lỗi từ đợt soát A13

Theo danh sách Truong đã chốt (báo cáo `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md`, mục "Vòng sửa A13.8"). Mô phỏng. Tắt Điểm quyết tâm: kết quả, dấu vân tay, run_history trùng khít `e08af78` (`kiem_nhanh.py`: 15 ca, 3 bộ × 5 seed).
- **2.1 + 3.2:** khoá đang bật và em đã có điểm thì `submit_preferences` / `submit_test_selection` trả `wharton_da_khoa` (gửi lại đúng danh sách cũ vẫn ok); nạp CSV / Sổ nhập bỏ qua em đó, cảnh báo `csv_wharton_khoa_giu_nguyen`; kiosk vô hiệu hai nút lưu kèm ghi chú. Tệp: `api_quan_ly.py`, `api_nhap.py`, `js/04_nhap_tai_cho.js`, `index.html`, `i18n.js`, `i18n_errors.py`. Test: `test_a13_8_khoa_nguyen_vong.py`, `test_giao_dien_a13_8_khoa.py`. **Hai test cũ sửa** (`tests/test_wharton_khoa.py`: nạp tệp khi khoá, cửa xoá khi khoá) vì mã hoá hành vi tỉa mà quyết định này đổi.
- **2.2:** docstring bốn API đúng thực tế; `HUONG_DAN_SU_DUNG.md` ghi "thẻ Quản lý cần người giám sát máy". Không PIN.
- **2.3:** `_trang_diem_chuan` ghi lý do lên trang và `export_ket_qua` trả `canh_bao` (`xuat_diem_chuan_loi`). Test: `test_a13_8_xuat_diem_chuan.py`.
- **3.1, 3.3, 3.4:** `js/05_quan_ly.js` chỉ ẩn tab khi `wharton_chua_bat`, lỗi khác hiện thông báo; tắt tính năng không gọi `list_wharton_canh_bao` / `get_diem_chuan` (cờ `WHARTON_BAT` đặt ở `js/075_workspace.js`); `style.css` `#dcKhongXet`. Test: `test_giao_dien_a13_8_quan_ly.py`.
- **2.4:** `phong_wharton_hang_loat` một giao dịch, đọc lại điểm hiện tại (`ly_do = "da_doi"`), rollback toàn bộ kèm `backup_path`; `_luu_wharton` tách `_luu_wharton_cur`. Test: `test_a13_8_phong_mot_giao_dich.py`.
- **2.5:** `_ngu_canh_diem_chuan` đọc trong một giao dịch (`load_wharton_kem_doc_them`, hàm mới ở `rbda_priority_pipeline.py`; hàm cũ giữ nguyên). Test: `test_a13_8_diem_chuan_mot_giao_dich.py`.
- **2.6, 2.7, 2.8:** `so_nhap.py` — cột W của sổ mẫu chỉ khi workspace bật được (`wharton_bat_duoc`); hằng `CHO_CHEN_GHI_CHU_W` thay việc dò "Bước 5."; test so `lam_tron_100` với `phong_theo_ti_le`. Test: `test_a13_8_so_mau.py`.
- **1.1 `submit_club_scores` (Truong chọn B, 28/10/2026):** lượt không lưu và không xoá được dòng nào vì ô điểm sai (`nan`, `inf`, `"1e999"`, `-1`, chữ) trả `ok=false`, `errors` liệt kê từng (student_id, giá trị) bằng `score_not_a_number` / `score_negative`; lượt lẫn ô đúng và sai vẫn lưu phần đúng, `ok=true` + `warnings` như cũ. `js/06_cham_diem.js` tô đỏ các ô sai cả khi thất bại. **Test cũ sửa có duyệt** (`tests/test_diem_bat_thuong.py`, đúng các ca một-ô-sai): `test_man_hinh_cham_diem_tu_choi_diem_am`, `test_hai_duong_nhap_cung_mot_luat_voi_diem_am`, `test_gia_tri_khong_doc_duoc_thi_khong_ghi_de_diem_cu`, `test_diem_am_viet_bang_dau_phay_van_bi_chan`; ca mới thêm ở cuối tệp. `js/06_cham_diem.js` hiện thông báo vàng liệt kê hết các ô sai khi lượt thất bại (nên test giao diện `test_o_bi_bo_qua_duoc_to_do_va_khong_bao_xanh` giữ nguyên). Hai test cũ ở `tests/test_wharton_khoa.py` (lỗi 2.1) cũng được Truong đồng ý giữ nguyên bản sửa.
- **Kiểm:** toàn bộ test có Chromium, `-rs`, độ phủ 92,47 %: 2.859 qua (sau khi sửa 1 ca giao diện chấm điểm, đã chạy lại riêng và qua), 3 bỏ qua (numpy ×2, POSIX ×1; không ca giao diện nào bị bỏ qua). `ruff check .` sạch.

## 2026-10-28 — Z-SOAT Skill `soat-ma`: soát mã trước khi push

Theo yêu cầu của Truong (28/10/2026, "làm bước cuối" của đợt soát A13). Mã mục `Z-SOAT` do Claude đề xuất, chưa có trong sổ đăng ký 33 mục (quy ước khác thì đổi tên). Đây là lần duy nhất đợt soát được thêm mã; KHÔNG sửa lỗi nào trong `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md` (sẽ làm ở A13.8, dùng chính skill này).

- **Tệp mới:** `.claude/skills/soat-ma/SKILL.md` (luật không subagent / chỉ báo cáo, phạm vi diff so với `main`, cách ghi phát hiện, checklist bốn tầng viết tổng quát kèm bài học rút từ đợt soát A13, lệnh, mẫu báo cáo); `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (một lệnh, bảy mục in ĐẠT / KHÔNG ĐẠT: `ruff`, `chu_cam`, `ma_loi_js`, `i18n_loi_khop`, `i18n_khoa`, `trung_khit` so với `main` 3 bộ × 5 seed, `khong_sua_nhat_ky`; chỉ thư viện chuẩn, `ruff` là công cụ ngoài đã có ở requirements-dev; mục không chạy được tính KHÔNG ĐẠT kèm lý do, không bỏ qua im lặng); `tests/test_skill_soat_ma.py`.
- **Tệp sửa:** `CLAUDE.md` — đúng MỘT dòng mới ở "Quy tắc làm việc" (quy tắc 8: "Trước khi push: chạy skill `soat-ma`"); bản đồ mã KHÔNG đụng (để A13.8).
- **Không đổi** mã sản phẩm, schema, hợp đồng cột CSV, hay kết quả xếp (bất biến 1–8 giữ nguyên). Skill KHÔNG vào `mau_forms_thi_clb/dong_goi_skill.py` (danh sách đó chỉ đóng .zip cho người dùng cuối); đăng ký theo kiểu của `sinh-du-lieu-clb` và `tao-workspace-tu-raw`: nằm trong `.claude/skills/`, có test riêng.
- **Test mới (45 ca):** `tests/test_skill_soat_ma.py` — mỗi mục một ca ĐẠT và các ca KHÔNG ĐẠT dựng trong thư mục tạm (xưng hô cấm ở VI / EN / lỗi / HTML, "Wharton" lộ ra chữ, mã lỗi lạ ở `.js` và `.html`, `i18n_loi.js` lệch và thiếu, khoá thiếu một ngôn ngữ hay rỗng, `DELETE` / `UPDATE` / `DROP` một dòng và nhiều dòng trên bảng dấu vết, tên bảng nằm trong danh sách `_RESET_BANG`-kiểu, hai bản mã khác thứ tự ưu tiên cho kết quả lệch, nhánh so sánh không có); khung `SKILL.md`, dòng trong `CLAUDE.md`, skill không nằm trong gói zip; và MỘT ca chạy script thật trên kho thật (năm mục nhanh phải ĐẠT: ai thêm xưng hô cấm, mã lỗi lạ, khoá i18n lệch hay xoá nhật ký thì test đỏ).
- **Chạy trên kho thật:** `kiem_nhanh.py` 7/7 ĐẠT (so với `main` và so với `e08af78`; trùng khít 15 ca). Hai điều chỉnh ghi trong mã và SKILL.md: chữ trong phần tử có `data-i18n` ở `index.html` là chữ dự phòng (có "em" từ trước A13) nên không soát lần hai; mã `loi_giao_dien_ngoai_du_kien` (từ trước A13) trùng một khoá UI nên được chấp nhận.
- **Kiểm toàn bộ (28/10/2026, Chromium thật, `-rs`):** 2.806 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua) — 2.761 của A13.7 cộng 45 ca mới. `ruff check .` sạch.

## 2026-10-27 — A13.7 Sổ nhập mẫu luôn có cột Điểm quyết tâm

Theo quyết định của Truong (27/10/2026): sổ MẪU luôn có cột "Điểm quyết tâm" kèm ghi chú "chỉ dùng khi bật tính năng". Không đổi mặc định `rules.wharton` (vẫn tắt), thuật toán, schema, hợp đồng CSV. Các đường ghi sổ khác (xuất dữ liệu đầu vào, ba skill, `du_lieu_test/`) giữ hành vi cũ.
- **Mã:** `so_nhap.ghi_so_nhap(..., luon_co_cot_w=False)` (mặc định = hành vi cũ; `True` thì `co_w` bật dù workspace tắt, trừ điểm theo người); `so_nhap.huong_dan(cfg, ghi_chu_cot_w)` thêm đoạn ghi chú trong sheet Hướng dẫn (chữ qua biến nhãn); `tao_so_nhap_mau` (`api_xuat.py`) và `mau_csv/tao_so_nhap.py` (mẫu trống và hai sổ `vi_du_*`) truyền `True`. Sinh lại ba sổ trong `mau_csv/`; các sổ trong `du_lieu_test/` (kịch bản đổi luôn chúng sang hai hàng) khôi phục bằng `git checkout`.
- **Khi tắt tính năng mà sổ có cột:** ô trống bỏ qua hoàn toàn; ô có số chỉ báo cảnh báo `csv_wp_bo_qua`, không chặn; không có dòng `wharton_bids`. `match_results` của sổ ví dụ trùng khít nạp bộ ba CSV cũ (seed 1, 7, 42).
- **Test mới (19 ca):** `tests/test_so_mau_co_cot_quyet_tam.py`.
- **Test cũ được sửa (Truong đã duyệt, 27/10/2026), chỉ hai kỳ vọng trong `tests/test_ws_so_nhap.py`:** `test_api_company_xuat_mau_roi_nap_lai` (hàng 1 của sổ mẫu là `["Nguyện vọng 1", None, None, "Nguyện vọng 2"]` thay vì `["Nguyện vọng 1", None, "Nguyện vọng 2"]`) và `test_api_mau_truong_hoc_giong_het_truoc_day` (`3 * 15` ô ở hàng 2 thay vì `2 * 15`). Lý do: đó đúng là thay đổi được chọn, sổ mẫu có ba cột mỗi nhóm. Không test nào bị `skip` hay nới.
- **Giao diện (`browser_host`):** workspace mặc định, bấm "Tải sổ nhập mẫu" ra sổ có cột ở 15/15 nhóm; nạp `vi_du_day_du` và chạy xếp xong, không lỗi JS.
- **Kiểm toàn bộ cho A13.6 và A13.7 (27/10/2026, Chromium thật, `-rs`):** 2.761 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), `ruff check .` sạch, độ phủ 92,37 % (CI đòi 85 %). Sau đó chỉ sửa chữ ở tài liệu; các test đọc CHANGELOG / TIEN_DO / sổ đăng ký / HUONG_DAN_SO_NHAP chạy lại (2.468 qua) và xanh.

## 2026-10-27 — A13.6 Dữ liệu mẫu có Điểm quyết tâm (vòng 6)

Thêm bộ sổ nhập mẫu có Điểm quyết tâm (trong mã: `wharton`, cột CSV `wp_k`), sinh lại được bằng một lệnh, và cho kỹ năng `sinh-du-lieu-clb` sinh điểm khi được yêu cầu. Mọi số liệu là dữ liệu MÔ PHỎNG. Không đổi thuật toán, schema, hợp đồng CSV, định dạng sổ; không thêm thư viện. Mặc định của kỹ năng (`--diem-quyet-tam khong`) cho đầu ra cũ từng ô.
- **Sáu tệp** trong `du_lieu_test/`: `SO_NHAP_DQT_{120HS,800HS}_{HOP_LE,CO_LOI,TRONG}.xlsx`. NHỎ (120 em, 3 buổi) giữ nguyên nguyện vọng và điểm thi của `SO_NHAP_MAU_120HS_3BUOI.xlsx`; LỚN (800 em, 20 CLB, 4 buổi) sinh bằng `sinh_ngau_nhien` (seed 8002026). Điểm chia kiểu TRỘN (`don_dau`, `deu`, `all_in`, `ngau_nhien`; seed 27102026), làm tròn theo phần dư lớn nhất, hoà theo mã CLB.
- **`CO_LOI`:** năm loại lỗi (`thieu`, `thua`, `ngoai_nguyen_vong`, `tang_lech`, `toan_0`), 3 em mỗi loại ở bản nhỏ, 8 ở bản lớn, ghi trong `DQT_BANG_LOI.json` (kèm mã lỗi, quỹ, buổi mà bước Kiểm tra dữ liệu phải báo). Vì sổ chỉ có một ô điểm cạnh mỗi nguyện vọng và tầng do ô tick thi quyết định, `ngoai_nguyen_vong` thể hiện bằng điểm đặt cạnh ô nguyện vọng trống (phần mềm bỏ ô đó lúc nạp, quỹ còn thiếu) và `tang_lech` bằng một quỹ chung cho cả CLB có thi lẫn không thi của một buổi.
- **Kỹ năng:** `sinh_du_lieu.py` thêm `--diem-quyet-tam {khong,hop_le,co_loi,trong}`, `--kieu-chia {tron,don_dau,deu,all_in,ngau_nhien}` (cho `ngau`, `tao`), lệnh `ap` (áp điểm lên sổ có sẵn), `ap_diem_quyet_tam`, `soat_diem_quyet_tam` (`soat` tự soát hồ sơ điểm nếu sổ có điểm), `lam_tron_100`. Ghi sổ vẫn qua `so_nhap.ghi_so_nhap`. `SKILL.md` thêm mục "Điểm quyết tâm"; hai skill còn lại không đổi.
- **Script:** `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py` (sinh sáu tệp và hai JSON `DQT_BANG_LOI.json`, `DQT_KIEU_CHIA.json`).
- **Tài liệu:** `du_lieu_test/README.md`, `TAI_LIEU_DU_LIEU.md` (bản dán `SKILL.md` và mục 5.3b), `docs/ke_hoach/TIEN_DO.md`, mục A13 của `SO_DANG_KY_33_MUC.md`.
- **Test mới (43 ca):** `tests/test_du_lieu_mau_diem_quyet_tam.py` (nạp 6 tệp; HOP_LE chạy xếp ok, có điểm chuẩn, mọi quỹ đúng 100; CO_LOI bị chặn đúng em đúng loại; TRONG không có `wharton_bids`, tự điền như cũ, kiosk nhập được; tắt tính năng thì `match_results` trùng khít với cùng sổ bỏ cột điểm, seed 1, 7, 42 ở cỡ nhỏ và seed 42 ở cỡ lớn; bản nhỏ giữ nguyên nguyện vọng và điểm thi; sinh lại ra đúng nội dung ô; kỹ năng). Không sửa test cũ nào.
- **Thử qua giao diện:** nạp `SO_NHAP_DQT_120HS_HOP_LE.xlsx` bằng `browser_host`, bật tính năng, chạy xếp (88/120 em được xếp, seed 42), tab Điểm chuẩn có bảng và biểu đồ, không lỗi JS.
- **Kiểm toàn bộ (27/10/2026, Chromium thật):** lần chạy đầy đủ 2.741 qua, 3 bỏ qua (thiếu `numpy` ×2; cần người dùng thường trên POSIX ×1; không ca giao diện nào bị bỏ qua), 1 đỏ: `test_tai_lieu_du_lieu::test_toan_van_skill_md_con_dung` (bản dán `SKILL.md` trong `TAI_LIEU_DU_LIEU.md` thiếu mục mới). Đã sửa tài liệu, chạy lại bốn tệp liên quan (69 ca) xanh; chưa chạy lại toàn bộ sau sửa tài liệu. `ruff check .` sạch; độ phủ 92,34 % (CI đòi 85 %).

## 2026-10-27 — A13.5 Sửa 5 việc từ báo cáo đóng vai

Sửa các vấn đề #1 đến #5 của `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md` (#6, #7 để sau), cộng một lỗi chập chờn của vòng 4 và đóng vai lần 2. Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 5 (bất biến 1): 15 lần chạy (3 bộ dữ liệu x 5 seed, `PipelineAPI.run_pipeline`) so với bản `d85fe2c`, `match_results` từng dòng, `run_history.luat_xep` và mã băm dấu vân tay GIỐNG HỆT (chỉ cột thời điểm chạy `luc` khác, đúng bản chất); `TestTrungKhit` qua. Không đụng thuật toán, `api.py`, schema, STB, thứ tự 5 bước.
- **Lỗi chập chờn của vòng 4 (Bước 0b):** `test_tieng_anh_chu_cua_khoi_doi_theo_va_khong_con_chu_co_dau` hỏng 1/20 lần. Nguyên nhân: đổi ngôn ngữ thì khối Điểm quyết tâm ở tab Quản lý nạp lại qua nhiều lời gọi API, và chữ cũ còn trên màn hình tới khi từng lời gọi về. Nay khối giữ dữ liệu lần vẽ gần nhất (`whBoNho`) và vẽ lại ngay khi đổi ngôn ngữ (`veLaiWhTuBoNho`, `js/05_quan_ly.js`). Sau sửa: 20/20 xanh. Kiosk Bước 3 đã vẽ lại ngay từ trước.
- **#1 Lỗi chặn gọn (`js/02_van_hanh.js`):** khung lỗi chỉ còn một dòng tóm tắt (`wharton_tom_tat_chua_hop_le`), 5 em đầu (mỗi em một dòng gộp mọi lỗi), "và M ... khác" và nút "Mở danh sách cần xử lý" (sang tab con Điểm quyết tâm, bộ lọc "chỉ hồ sơ có vấn đề" đã bật). Bước "Kiểm tra dữ liệu" trong danh sách bước cũng chỉ còn câu tóm tắt (`chuLoiBuocGon`, phát hiện khi đóng vai). Hợp đồng `{ok, data, errors}` KHÔNG đổi (bất biến 6): backend vẫn trả đủ mọi lỗi; gộp theo em làm ở JS bằng `params.student_id`.
- **#2 Hai nút hàng loạt:** "Tải danh sách cần sửa" (`export_wharton_can_sua`, `api_xuat.py`: Excel gồm mã, họ tên, buổi, quỹ, tổng hiện tại, thiếu, thừa, câu lỗi; không đổi điểm nào) và "Phóng cho đủ 100 theo tỉ lệ" (`phong_wharton_hang_loat`, `api_quan_ly.py`). Hàm thuần `phong_theo_ti_le(diem, ngan_sach=100)`: làm tròn theo phần dư lớn nhất, hoà phần dư xét theo MÃ CLB tăng dần, không nhận thứ hạng nguyện vọng (bất biến 2), không phụ thuộc thứ tự dict, tổng 0 trả `None`. Phải gõ `PHONG`; sao lưu trước; mỗi em qua `_luu_wharton(..., "quan_ly")` nên có kiểm khoá, kiểm hồ sơ và nhật ký giá trị cũ / mới; em tổng 0 (`tong_0`) hoặc còn lỗi khác (`loi_khac`) được bỏ qua và liệt kê; đang khoá thì `wharton_da_khoa`.
- **#3 Tab con của tab Quản lý:** CLB · Học sinh · Điểm quyết tâm · Điểm chuẩn · Dữ liệu. Hai tab điểm chỉ hiện khi bật tính năng (tắt thì ba tab con, nội dung y như cũ). Nhớ tab đang mở bằng `localStorage` (có `try/catch`; không đọc được thì mở tab đầu); `role="tablist"` / `tab` / `tabpanel`, `aria-selected`, phím mũi tên, Home, End. Id phần tử bên trong giữ nguyên.
- **#4 Khoá xuất khi chưa có kết quả (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** `export_ket_qua` và `export_csv` từ chối với `xuat_chua_co_ket_qua` TRƯỚC khi tạo tệp (`_chua_co_ket_qua`, cùng phép đo với `get_trang_thai_ket_qua`); ô xuất kết quả ở thẻ Kết quả bị khoá kèm dòng vàng (`khoaXuatKetQua`). Xuất dữ liệu đầu vào, Sổ nhập mẫu và hồ sơ học sinh dùng như cũ.
- **#5 Thông báo (TOÀN ứng dụng, NGOÀI PHẠM VI A13, theo yêu cầu của Truong):** nguyên nhân thông báo "Xong: ..." sau khi nạp Sổ "không tự tắt": mã cũ ĐÃ tự đóng thông báo thường sau `min(10000, 4000 + 40 x độ dài)` ms (khoảng 7 giây; `test_giao_dien_chay` canh), không phải thiếu hẹn giờ. Điều người đóng vai thấy là thông báo nằm lại vài giây giữa các ảnh chụp và vùng thông báo ở góc trên phải đè lên tiêu đề trang. Quy tắc mới (`js/00_nen.js`, `style.css`): thành công tự đóng sau 6 giây, câu dài thêm thời gian, tối đa 10 giây; rê chuột hoặc có tiêu điểm thì tạm dừng đếm; lỗi và cảnh báo giữ tới khi bấm ×; thành công kèm cảnh báo (`opts.canhBao`) tách thành thông báo xanh tự đóng và thông báo vàng giữ; vùng thông báo ở góc dưới phải, không nhận chuột ngoài từng thông báo; `prefers-reduced-motion` bỏ hiệu ứng; `aria-live` `polite` cho thông báo thường và `assertive` kèm `role="alert"` cho lỗi. Chữ của thông báo không đổi.
- **Mã lỗi mới:** `xuat_chua_co_ket_qua`, `wharton_phong_sai_xac_nhan`, `wharton_da_phong`, `wharton_tom_tat_chua_hop_le` (thêm vào `MA_MOI_SAU_ANH_CHUP`, `tests/test_ws_nhan.py`).
- **Test mới (60 ca):** `test_wharton_hang_loat` (21), `test_giao_dien_thong_bao` (11), `test_giao_dien_quan_ly_tab_con` (9), `test_giao_dien_loi_chan_gon` (6), `test_xuat_khoa_chua_co_ket_qua` (6), `test_giao_dien_khoa_xuat` (5), cộng hai test đổi ngôn ngữ khi lời gọi API còn treo (`test_giao_dien_wharton_quan_ly`, `test_giao_dien_wharton`).
- **Test cũ đã sửa theo ngoại lệ:** thêm thao tác bấm sang đúng tab con ở `test_giao_dien_diem_chuan`, `test_giao_dien_wharton_quan_ly`, `test_giao_dien_diem_quyet_tam_gon`, `test_giao_dien_xoa_du_lieu`, `test_giao_dien_ux_xuat`, `test_giao_dien_xuat_du_lieu`, `test_giao_dien_doi_ngon_ngu`, `test_khoi_dong_backend`, `test_giao_dien_sua_loi_p1`; xuất kết quả khi chưa có kết quả: `test_so_excel_de_dung` (`test_chua_chay_thi_van_xuat_duoc` đổi thành kiểm bị từ chối; `test_qua_nhieu_clb_khong_vuot_gioi_han_ngat_trang_cua_excel` thêm một em và chạy xếp) và `test_giao_dien_chay` (`test_loi_goi_phan_loi_hien_cau_tieng_viet` chạy xếp trước khi bấm xuất). Không test nào bị `skip` hay nới.
- **Kiểm toàn bộ (27/10/2026):** 2.699 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng thường trên POSIX), không có test giao diện nào bị bỏ qua; `ruff` sạch; độ phủ 92,34 % (CI đòi 85 %).
- **Đóng vai lần 2** (có sửa mã với lỗi mức "chặn"): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`, mục "Lần 2 (27/10/2026)". Còn lại: #6, #7, biểu mẫu Google, mô phỏng VISEF, ngưỡng điểm tối thiểu, giải trình từng em.

## 2026-10-25 — A13.4 Giao diện Điểm quyết tâm và điểm chuẩn

Đổi tên hiển thị, đổi Sổ nhập sang hai hàng tiêu đề, thêm điểm chuẩn từng CLB (API, tab Kết quả, tab Quản lý, trang trong tệp xuất, ba biểu đồ SVG ngoại tuyến) và dọn gọn các màn của tính năng.
Tắt `rules.wharton` thì kết quả, dấu vân tay và `run_history` y hệt trước vòng 4: 15 lần chạy (3 bộ dữ liệu x 5 seed) so từng dòng `match_results` GIỐNG HỆT bản `4c448ae`; sổ Excel kết quả so từng ô cũng giống hệt. Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Tên hiển thị (Điểm quyết tâm; trong mã: wharton):** tiếng Việt "Điểm quyết tâm", tiếng Anh "Preference points" ở `i18n.js`, `i18n_errors.py` (sinh lại `i18n_loi.js`), Sổ nhập, tệp xuất, `HUONG_DAN_SU_DUNG.md`. Giữ nguyên tên hàm, bảng, mã lỗi `wharton_*`, khoá `rules.wharton`, cột CSV `wp_k`, id HTML.
- **Sổ nhập hai hàng (đổi hợp đồng, bất biến 7):** sheet học sinh luôn có hai hàng tiêu đề (hàng 1 ô gộp "Nguyện vọng k"; hàng 2 "CLB", "Điểm thi", "Điểm quyết tâm" khi bật), cột đầu gộp dọc, dữ liệu từ hàng 3, sheet CLB một hàng. Nạp đọc ba dạng (một hàng cũ, một hàng có "Điểm W k", hai hàng), nhận dạng bằng hàng 1. Cột lệch nhóm báo `so_nhap_cot_lech_nhom` / `so_nhap_nhom_thieu_cot` (sheet, cột, nhóm) và không nạp gì. CSV không đổi. `so_nhap.py` vẫn chạy một mình. Sổ mẫu trong `mau_csv/` sinh lại; `du_lieu_test/` giữ nguyên dạng một hàng.
- **Ba skill** `sinh-du-lieu-clb`, `xu-li-raw-forms`, `tao-workspace-tu-raw`: cập nhật SKILL.md (script đã ghi sổ qua `so_nhap.ghi_so_nhap` nên tự theo bố cục mới); chạy thử sinh sổ 60 em rồi `import_so_nhap` thành công.
- **Điểm chuẩn:** `tinh_diem_chuan` (hàm thuần, ở `api_quan_ly.py`), API `get_diem_chuan` và `get_diem_chuan_clb` (chỉ quản trị; kiosk không có đường gọi), trang "Điểm chuẩn" trong sổ Excel kết quả (chỉ khi bật). Tầng 2: điểm hiệu lực thấp nhất đã được nhận; tầng 1: điểm thi thấp nhất kèm điểm quỹ 1 của em cuối; tách suất thường và suất dự trữ theo `matched_tier`; CLB còn chỗ ghi 0 kèm số chỗ còn.
- **Giao diện:** mục "Điểm chuẩn" ở tab Kết quả luôn đóng mỗi lần vào thẻ (không nhớ trạng thái); khối chi tiết ở tab Quản lý; ba biểu đồ SVG (cột phân bố, dải chấm, bảng tổng quan) chọn màu theo kỹ năng dataviz, có tiêu đề, chú giải, bảng chữ ẩn, không tải gì từ mạng. Dọn gọn: hai khung Bước 3 cạnh nhau (màn hẹp xếp dọc) kèm thanh tiến độ, ô sai tô màu và dòng lỗi tại chỗ, giải thích sau nút (i); khối Quản lý có mục "Thao tác khác" đóng sẵn (mở khoá, xem nhật ký, xoá tất cả), bộ lọc một hàng; công tắc workspace một dòng ngắn kèm nút (i).
- **Test mới (110 ca):** `test_diem_quyet_tam_chu` (18), `test_so_nhap_hai_hang` (20), `test_diem_chuan` (53), `test_giao_dien_diem_chuan` (11), `test_giao_dien_diem_quyet_tam_gon` (8).
- **Test cũ đã sửa theo ngoại lệ:** chữ "Wharton" trong `test_giao_dien_wharton.py`, `test_giao_dien_wharton_quan_ly.py`, `test_ws_wharton_giao_dien.py`; tiêu đề và toạ độ Sổ nhập một hàng trong `test_so_nhap.py`, `test_wharton_so_nhap.py`, `test_ws_so_nhap.py` (kèm làm mới bản chụp `tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json`: chỉ sheet học sinh và sheet hướng dẫn đổi, sheet CLB giống hệt), `test_ws_so_nhap_giao_dien.py`, `test_giao_dien_upload.py`. Ngoài ngoại lệ, buộc phải thêm bước "mở mục Thao tác khác" vào ba test của `test_giao_dien_wharton_quan_ly.py` (mục đóng sẵn theo yêu cầu thiết kế); `tests/test_ws_nhan.py` thêm hai mã mới vào danh sách cho phép.
- **Kiểm toàn bộ (27/10/2026):** lần chạy đầu 2.636 xanh, 3 đỏ, 3 bỏ qua; đã xử lý cả 3 (một câu `ORDER BY buoi` thiếu `COLLATE THU_TU_BUOI` ở `get_diem_chuan`; hai test cũ theo ngoại lệ: chữ "Wharton" trong `test_wharton.py` và tiêu đề Sổ một hàng trong `test_so_nhap.py`), chạy lại các tệp liên quan 288 ca xanh. Tổng sau sửa: 2.639 xanh, 3 bỏ qua (2 do thiếu `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 278 ca giao diện dùng Chromium thật), `ruff check .` sạch, độ phủ 92,42 % (sàn CI: 85 %), `TestTrungKhit` 7/7.
- **Đóng vai người dùng** (chỉ báo cáo, không sửa mã): `docs/ke_hoach/BAO_CAO_DONG_VAI_DIEM_QUYET_TAM.md`.

## 2026-10-25 — A13.3 Quản lý điểm Wharton

Thêm khối **Điểm Wharton** vào thẻ Quản lý (chỉ hiện khi workspace bật `rules.wharton`): bảng điểm, sửa từng em, xoá, cảnh báo hồ sơ có vấn đề; kèm nhật ký và khoá riêng.
Tắt Wharton thì thẻ Quản lý, mọi API cũ, kết quả, dấu vân tay và `run_history` y hệt trước vòng 3 (bất biến 1). Mọi số liệu trong test là dữ liệu MÔ PHỎNG.
- **Quyết định đã chốt (25/10/2026):** (1) nhật ký mọi lần ghi hoặc xoá điểm: lúc nào, nguồn (`quan_ly`, `kiosk`, `nap_tep`, `xoa_du_lieu`, `he_thong`), tên tài khoản máy
  (`getpass.getuser()`, lỗi thì rỗng), giá trị cũ và mới; không bao giờ bị xoá hay ghi đè, kể cả `reset_data`. (2) Khoá Wharton RIÊNG (không dính STB): lần chạy xếp thành công
  khi Wharton bật tự khoá, kể cả chạy riêng một số buổi; đang khoá thì mọi cửa GHI điểm trả `wharton_da_khoa`; mở bằng `mo_khoa_wharton("MO")`. (3) Các cửa xoá dữ liệu
  vẫn chạy khi khoá nhưng ghi nhật ký; `reset_data` mở luôn khoá Wharton. (4) Chỉ hiện khi bật Wharton. (5) Màn dành cho quản trị. (6) Giữ STB; thứ tự 5 bước pipeline không đổi.
- **Sửa "cách A" (Bước 2, Truong đã duyệt):** `submit_wharton` chỉ ghi ô em đã GỬI (ô 100 tự điền chỉ có trong bộ nhớ), nên thêm CLB thứ hai vào quỹ đó sau này thì hồ sơ bị coi là
  chưa chia thay vì "hợp lệ" nhờ một ô em chưa từng đặt; cảnh báo sau khi nạp tệp (`_soat_ho_so_wharton`) cũng tự điền trong bộ nhớ như pipeline và báo cáo sức khoẻ dữ liệu.
- **Hai bảng mới** trong `DEFAULT_SCHEMA` (chỉ `CREATE TABLE IF NOT EXISTS`, không vào `_BANG_RANG_BUOC`; `di_tru_schema` chạy lặp an toàn): `wharton_nhat_ky(id, luc, nguon, nguoi, hanh_dong, student_id, cu_json, moi_json)`,
  không khoá ngoại, `nguon` bị CHECK; `wharton_lock(id = 1, is_locked, locked_at, unlocked_at)`. Không câu `DELETE` / `UPDATE` nào chạm nhật ký.
- **API mới** (`api_quan_ly.py`): `list_wharton_admin`, `list_wharton_canh_bao`, `get_wharton_nhat_ky`, `admin_save_wharton` (dùng lại lõi `_luu_wharton` với `submit_wharton`), `clear_wharton`
  (một em, hoặc tất cả khi gõ `XOA`, có sao lưu), `mo_khoa_wharton`, `get_wharton_lock_status`; `get_student_entry_state` có thêm cờ `khoa` trong khoá `wharton`. `_ho_so_wharton_tat_ca` là MỘT hàm đọc
  một lần, dùng chung cho bảng điểm, danh sách cảnh báo và `get_data_health_report` (số liệu báo cáo không đổi).
- **Cửa có nhật ký:** `submit_wharton` (`kiosk` / `luu`), `admin_save_wharton` (`quan_ly` / `luu`), nạp tệp kể cả Sổ nhập (`nap_tep` / `luu`), tỉa trong `submit_preferences` (`kiosk` / `tia_nguyen_vong`),
  `reset_student_entry` (`kiosk` / `xoa_mot_em`), `delete_student` (`quan_ly` / `xoa_mot_em`), `delete_club` (`quan_ly` / `xoa_theo_clb`, mỗi em một dòng), `reset_data` (`xoa_du_lieu` / `xoa_tat_ca`, một dòng tổng),
  `clear_wharton`, khoá sau khi chạy (`he_thong` / `khoa`) và mở khoá (`mo_khoa`). Nhật ký nằm trong CÙNG giao dịch với thao tác. Cửa ghi có kiểm khoá trong giao dịch ghi: `submit_wharton`, `admin_save_wharton`,
  `clear_wharton`, nạp cột `wp_*` (nguyện vọng vẫn nạp, phần điểm bị bỏ kèm cảnh báo `wharton_da_khoa`).
- **Pipeline** (`api.py`, chỉ bước 5/6): đặt khoá trong cùng giao dịch ghi `run_history` khi Wharton bật; thứ tự năm bước không đổi; khoá và nhật ký không vào dấu vân tay.
- **Giao diện:** `js/04_nhap_tai_cho.js` tách `whartonVeKhung` / `whartonThuThapTu` / `whartonChuoiTu` / `whartonGiuTamTu` dùng chung (hành vi kiosk không đổi) và Bước 3 chỉ đọc khi khoá;
  `js/05_quan_ly.js` khối mới (bảng, lọc, phân trang, cảnh báo, màn sửa, nhật ký, hộp xác nhận `MO` / `XOA`); `index.html`, `style.css`, `i18n.js` (vi/en).
- **Mã lỗi** (`i18n_errors.py` rồi `python tao_i18n_js.py`, `i18n_loi.js` chỉ thêm dòng): `wharton_da_khoa`, `wharton_mo_khoa_sai_xac_nhan`, `wharton_xoa_sai_xac_nhan`, `wharton_da_xoa`,
  `wharton_da_mo_khoa`, `error_wharton_quan_ly`; thêm vào `MA_MOI_SAU_ANH_CHUP` của `tests/test_ws_nhan.py`.
- **Test cũ đã sửa theo ngoại lệ A.3:** `tests/test_wharton_kiosk.py::test_tu_dien_khi_quy_chi_co_mot_clb` (ô tự điền không còn được ghi, Bước 2) và
  `tests/test_wharton_kiosk.py::test_bat_wharton_trang_thai_co_khoa_wharton_dung_dang` (khoá `khoa` do vòng này cố ý thêm). `tests/test_ws_nhan.py`: chỉ thêm 6 mã vào danh sách cho phép.
- **Test mới (141 ca):** `test_wharton_cach_a` (6), `test_wharton_nhat_ky` (22), `test_wharton_khoa` (21), `test_wharton_quan_ly` (23), `test_wharton_quan_ly_ghi` (21),
  `test_wharton_quan_ly_dau_cuoi` (1), `test_giao_dien_wharton_quan_ly` (10, Chromium thật), cộng 37 ca vòng 3 trong `test_wharton_ma_loi`.
- **Trùng khít (bất biến 1):** Wharton tắt: 15 lần chạy `run_pipeline` (3 bộ trong `du_lieu_test/do_anh_huong_seed.BO_DU_LIEU` × seed 1, 7, 42, 3, 11) cho `match_results` đầy đủ cột (1.350 dòng),
  `dau_van_tay_chay` và `run_history.luat_xep` GIỐNG HỆT bản chụp lấy trước khi sửa (đỉnh vòng 2, `a8b077d`); `tests/test_nhieu_buoi.py::TestTrungKhit` 7/7 xanh. Toàn bộ: 2.529 ca xanh, 3 ca bỏ qua (2 do thiếu
  `numpy`, 1 do cần người dùng thường trên POSIX; không ca giao diện nào bị bỏ qua, 212 ca giao diện chạy bằng Chromium thật), `ruff check .` sạch, độ phủ 92,34 % (sàn của CI: 85 %). Một ca trợ năng
  (`test_giao_dien_tro_nang::test_moi_o_nhap_deu_co_ten_doc_duoc`) bắt được hai ô gõ chữ xác nhận thiếu tên đọc được; đã sửa bằng `aria-label` qua `i18n.js`.
- **Cần biết:** ở màn (kiosk và thẻ Quản lý) khung chỉ có một CLB tự điền 100 và khoá ô; giao diện gửi cả ô đó khi bấm Lưu nên server GHI ô đó (đúng với "ô người dùng gửi thì được ghi"). Cách A (không ghi ô tự điền)
  vì vậy giữ trọn với gọi API trực tiếp, nạp tệp và Sổ nhập; đường bấm Lưu trên giao diện vẫn ghi ô 100 như vòng 2 (`js/04_nhap_tai_cho.js` ngoài phạm vi vòng này để sửa phần thu thập).


## 2026-10-25 — A13 Điểm Wharton: pipeline tự điền quỹ một CLB trong bộ nhớ (theo quyết định của Truong, cách A)

Quỹ (mỗi buổi) chỉ có MỘT CLB mà em chưa đặt điểm: lúc chạy xếp và lúc lập báo cáo sức khoẻ dữ liệu, `api.py` gọi `tu_dien_wharton_mot_clb`
trong bộ nhớ TRƯỚC `kiem_ho_so_wharton` / `diem_wharton_hieu_luc`. Không ghi `wharton_bids`; kết quả vẫn tất định (hàm thuần của nguyện vọng,
ô tick và điểm đã lưu, đều nằm trong dấu vân tay). Quỹ đã có khoá (kể cả 0) hoặc có từ hai CLB mà chưa chia thì vẫn bị chặn. Tắt Wharton: không đổi.
Test mới (5 ca, trong `tests/test_wharton_pipeline.py`): chạy được khi chưa lưu, CSDL không đổi, bằng kết quả khi đã lưu 100, không che lỗi thật,
sức khoẻ dữ liệu cùng cách tính. Sửa mục 14 của `HUONG_DAN_SU_DUNG.md` cho khớp.

## 2026-10-24 — A13 Điểm Wharton (vòng 2: lưu trữ, nhập liệu, kiosk, pipeline)

Làm tiếp mục A13 theo quyết định của Truong: chỉ bật được khi `priority` là `score` / `score+tier` và `score_scope` là
`per_slot`; hồ sơ Wharton sai CHẶN cả lần chạy ở bước Kiểm tra dữ liệu, trước khi bốc hay khoá STB; nhập bằng tệp (CSV, Sổ
nhập) và bằng một màn kiosk; lưu tầng lúc nhập; mặc định **TẮT** — mọi hành vi, tệp, dấu vân tay và kết quả giống hệt trước
vòng 2 (bất biến 1). Giữ STB (không SHA-256, không `public_value`; bất biến 3 nguyên). Mọi số liệu trong test là dữ liệu
MÔ PHỎNG. Ghi hợp đồng cột vào sổ đăng ký TRƯỚC khi làm (bất biến 7).
- **Bảng `wharton_bids(student_id, club_id, tier, points)`** trong `DEFAULT_SCHEMA` (khoá chính `(student_id, club_id)`, `tier IN (1, 2)`,
  `points >= 0`, khoá ngoại tới `students`, `clubs`); bảng mới hoàn toàn nên chỉ cần `CREATE TABLE IF NOT EXISTS`, không vào
  `_BANG_RANG_BUOC`. `tier` = quỹ lúc NỘP (1 = lúc ghi em đang tick thi CLB đó). Đổi ô tick sau khi chia điểm thì hồ sơ thành chưa
  hợp lệ (`wharton_ngoai_tap`); phần mềm KHÔNG tự chuyển điểm sang quỹ kia. Dọn ở mọi cửa xoá: `delete_student`, `delete_club`,
  `reset_student_entry`, `reset_data` (`_RESET_BANG`), `submit_preferences` (bỏ CLB thì xoá điểm CLB đó), `seed_sample_data`; nạp CSV
  nguyện vọng cũng dọn dòng của CLB bị bỏ.
- **Thay đổi hợp đồng cột (bất biến 7), chỉ khi workspace bật Wharton:** CSV nguyện vọng thêm `wp_k` đi cặp `pref_k`, `<buoi>_wp_k`
  đi cặp `<buoi>_pref_k`, và cột `wp` cho dạng dài (ghép theo HẬU TỐ SỐ, không theo vị trí); Sổ nhập thêm cột "Điểm W k" ngay sau
  "Điểm k" (kèm kiểm số nguyên ở Excel, màu riêng, đoạn hướng dẫn hai quỹ). Tệp không có các cột này nạp như cũ; chưa bật mà có thì bỏ
  qua kèm `csv_wp_bo_qua`. Xuất "dữ liệu đầu vào" ra Sổ nhập có cột W khi bật; nạp lại ra `wharton_bids` giống hệt.
- **Khoá luật `rules.wharton`** (bool, mặc định `False`): `cau_hinh_ws` từ chối tổ hợp khác; `LUAT_XEP_MAC_DINH["wharton"]`, `dung_wharton`.
  Khoá `wharton` chỉ vào chuỗi ghi `run_history.luat_xep` và phần băm dấu vân tay khi BẬT (`_luat_de_ghi_hoac_bam`), nên workspace
  tuỳ biến cũ giữ nguyên từng byte. Dấu vân tay có thêm bảng `wharton_bids` khi bật.
- **Đọc dữ liệu:** `doc_du_lieu_wharton`, `load_from_sqlite_kem_dau_van_tay_wharton` (dữ liệu, dấu vân tay và Wharton trong MỘT giao
  dịch đọc); `_doc_du_lieu`, `load_from_sqlite_kem_dau_van_tay` giữ nguyên chữ ký và giá trị trả về.
- **API kiosk:** `submit_wharton(student_id, w1, w2)` (kiểm ở server theo V6: tự điền một CLB → `kiem_ho_so_wharton` → thay toàn bộ dòng
  của em; hồ sơ sai thì không ghi gì và trả đúng danh sách lỗi); `get_student_entry_state` có thêm khoá `wharton` CHỈ khi bật (tắt thì
  y hệt trước).
- **Nối pipeline** (`_run_pipeline_da_khoa`, chỉ bước 2 và 4): bước Kiểm tra dữ liệu đọc bằng bản có Wharton, chạy `kiem_ho_so_wharton` và
  `diem_wharton_hieu_luc` NGAY SAU `validate_data_integrity` — trước soát buổi, bốc, khoá STB; có lỗi (mọi mã trừ `wharton_vang_thi`) thì
  trả `wharton_ho_so_chua_hop_le` cùng đủ lỗi, không vẽ số, không ghi, không thêm dòng `run_history`. Vắng thi chỉ là cảnh báo trong chi
  tiết bước validate. Bước 4 truyền `diem_wharton` cho `run_rbda_nhieu_buoi`. Thứ tự năm bước giữ nguyên.
- **Sức khoẻ dữ liệu:** `health_wharton_chua_hop_le` (mức high) và `health_wharton_vang_thi` (mức medium), chỉ khi bật, đặt sau các mục sẵn có.
- **Giao diện:** ô "Dùng điểm Wharton" ở bước luật của trình hướng dẫn workspace (khoá và tự bỏ chọn khi không dùng được) và hàng tóm tắt
  `rvWharton`; màn "Bước 3. Điểm Wharton" ở tab Nhập tại chỗ (hai khung mỗi buổi, bộ đếm "Đã dùng X / 100", tự điền và khoá khung một CLB,
  "Cần chia lại điểm" khi lệch tier, vẽ lại sau khi lưu Bước 1 / 2, chung cơ chế "chưa lưu"; học sinh chỉ thấy điểm của chính mình).
- **Mã lỗi song ngữ (8):** `csv_wp_khong_hop_le`, `csv_wp_khong_co_nguyen_vong`, `csv_wp_bo_qua`, `wharton_chua_bat`,
  `wharton_ho_so_chua_hop_le`, `health_wharton_chua_hop_le`, `health_wharton_vang_thi`, `error_saving_wharton`; `i18n_loi.js` sinh lại, chỉ thêm dòng.
- **Test mới: 252 ca** (viết trước, thấy đỏ rồi mới viết mã): `test_wharton_luu_tru` (21), `test_wharton_luat` (30), `test_wharton_doc` (15),
  `test_wharton_ma_loi` (56), `test_wharton_nhap` (24), `test_wharton_so_nhap` (23), `test_wharton_kiosk` (29), `test_wharton_pipeline` (24),
  `test_wharton_suc_khoe` (6), `test_wharton_dau_cuoi` (1), `test_ws_wharton_giao_dien` (9), `test_giao_dien_wharton` (14). Bản chụp mốc
  `tests/du_lieu_ws/wharton_moc_truoc_vong2.json` (`match_results`, `dau_van_tay_chay`, `luat_xep` của 3 bộ × 3 seed, chụp bằng mã TRƯỚC
  vòng 2) được so trong `test_wharton_pipeline`. Đã thử phá hoại có chủ đích (bỏ truyền `diem_wharton` ở bước 4): bị bắt.
- **Xác nhận.** Tắt Wharton: giống hệt mốc (810 dòng `match_results`, dấu vân tay, `luat_xep`); `TestTrungKhit` 7/7. Toàn bộ test (kèm Chromium
  thật): 2.383 qua, 3 bỏ qua (thiếu `numpy`; cần người dùng không phải root), 0 đỏ; `ruff check .` 0 lỗi; độ phủ 92,43 % (sàn 85 %).
- **Chỗ lệch yêu cầu, có lý do.** (1) Câu chữ màn kiosk không dùng "bạn" ("Các CLB bạn đã thi" thành "Các {slot_sl} đã thi") vì
  `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong mọi chuỗi giao diện; câu báo lỗi vẫn là "Chưa dùng hết điểm Wharton…".
  (2) `{detail}` của `error_saving_wharton` không nằm trong câu (test văn phong cấm); `format_message` tự thêm chi tiết ở cuối như các mã
  `error_*` khác. (3) `tests/test_ws_nhan.py`: chỉ THÊM 8 mã mới vào `MA_MOI_SAU_ANH_CHUP` (test đó tự quy định cách này; ngoại lệ "wharton: False"
  của luật KHÔNG phải dùng cho test nào). (4) `get_student_entry_state` có thêm `tu_dien_mot_clb` và `ds_buoi` trong khoá `wharton`.
  (5) Khoá `wharton` chỉ được ghi vào `luat_xep` / băm khi bật, để bất biến 1 đúng cả với workspace tuỳ biến cũ.
- **Việc sau:** cập nhật ba skill trong `.claude/skills/` (sinh dữ liệu, xử lí raw forms, tạo workspace) cho cột mới; biểu mẫu Google hai khung;
  mô phỏng VISEF; ngưỡng điểm tối thiểu; công bố điểm chuẩn; giải trình từng em (C3). Điểm cần Truong quyết: em có quỹ chỉ một CLB mà chưa
  bấm Lưu ở kiosk thì lần chạy bị chặn (màn kiosk tự điền 100 nhưng chưa ghi) — có muốn tự điền ngay trong pipeline không.

## 2026-10-24 — A13 Điểm Wharton (vòng 1: lõi thuật toán và test)

Mục mới A13 trong sổ đăng ký (`docs/ke_hoach/`), làm theo quyết định của Truong ngày 24/10: **giữ nguyên STB**
(bộ số đã khoá, chế độ `stb_ngay`, cách chèn em đến muộn), điểm Wharton xét **TRƯỚC** STB, mỗi quỹ **100 điểm
MỖI BUỔI**, vòng này **chỉ làm lõi thuật toán, test, mã lỗi và tài liệu sổ**. Không đổi schema, `api*.py`, sổ nhập,
giao diện hay `compute_club_priority` (không đổi một ký tự). Mọi số liệu dưới đây là dữ liệu MÔ PHỎNG.
- **Cơ chế.** Mỗi học sinh có hai quỹ cho mỗi buổi: quỹ 1 chia cho CLB có thi (chỉ phá hoà khi bằng điểm thi),
  quỹ 2 chia cho CLB không thi (tiêu chí chính tầng 2). Khoá ưu tiên: tầng 1 `(0, -điểm thi, (), -w1, stb, mã)`,
  tầng 2 `(1, -w2, stb, mã)`; `()` là chỗ dành cho tiêu chí phụ của mục A1. Gale–Shapley vẫn chạy MỘT lần cho cả
  hai tầng; thứ hạng nguyện vọng không vào khoá.
- **Hàm mới** (`rbda_priority_pipeline.py`, khối `BƯỚC A2` L252–L574): `khoa_uu_tien_wharton`, `uu_tien_wharton`
  (hàm bọc như `uu_tien_theo_nhom`, nhận `tier_rank`), `kiem_ho_so_wharton` (V1–V5, theo từng buổi, trả đủ mọi
  lỗi theo thứ tự cố định), `tu_dien_wharton_mot_clb`, `diem_wharton_hieu_luc` (lúc khoá: vắng thi rơi xuống tầng
  2, T2 chuyển lên T1 là lỗi); ba hằng `WHARTON_NGAN_SACH = 100`, `WHARTON_TU_DIEN_MOT_CLB = True`,
  `WHARTON_VANG_THI = "tier2_zero_points"` (hai hằng sau chờ chủ dự án quyết).
- **Hai tham số mới**, mặc định `None` = hành vi cũ: `diem_wharton` của `run_rbda` (thay NGUỒN `base_rank`; dự
  trữ mềm, `verify_stability` giữ nguyên) và của `run_rbda_nhieu_buoi` (chuyển nguyên cho mọi buổi).
- **7 mã lỗi song ngữ** trong `i18n_errors.py` (`wharton_nguyen_vong_chua_xep`, `wharton_chua_dung_het`,
  `wharton_vuot_ngan_sach`, `wharton_diem_khong_hop_le`, `wharton_ngoai_tap`, `wharton_tang_lech`,
  `wharton_vang_thi`); `i18n_loi.js` sinh lại bằng `tao_i18n_js.py`, chỉ thêm 28 dòng. Câu chữ dùng chỗ giữ nhãn
  workspace (`{person}`, `{slot_sl}`, `{session_l}`…), không viết cứng "học sinh" / "CLB".
- **Test mới.** Phần hàm và mã lỗi viết trước, thấy đỏ rồi mới viết mã; nhóm test tính chất viết sau, trên mã đã
  xong, đúng theo đặc tả của bước đó. `tests/test_wharton.py`, 144 ca: khoá ưu tiên và W1, W3;
  hàm bọc (200 bộ ngẫu nhiên: bằng điểm Wharton thì y hệt `compute_club_priority` / `uu_tien_theo_nhom`); VD1–VD5
  qua `run_rbda`, W7, mặc định `None` trùng khít trên 30 bộ, và hai buổi khớp `run_rbda` chạy riêng; mã lỗi;
  `kiem_ho_so_wharton` (W5, 32 ca); `tu_dien_wharton_mot_clb`; `diem_wharton_hieu_luc` (VD6, W4); VD1–VD5 đi từ
  `w1`/`w2` thô (W9); test tính chất: W1 (hoán vị nguyện vọng không đổi `base_rank`), W2, W6 (50 bộ một buổi có
  dự trữ / nhóm xếp cứng + bốn cấu hình nhiều buổi), W8 (mọi hoán vị nguyện vọng của từng em trên 15 bộ nhỏ,
  không hoán vị nào cho CLB tốt hơn kết quả thật). Thử phá hoại có chủ đích: đổi dấu `w1`, đặt STB trước Wharton ở
  tầng 2, bỏ qua `diem_wharton` trong `run_rbda`, xác định tầng bằng "điểm > 0" — cả bốn đều bị bắt.
  `tests/test_ws_nhan.py`: chỉ THÊM 7 mã vào `MA_MOI_SAU_ANH_CHUP` (cách test đó quy định).
- **Bất biến.** Bất biến 1: `TestTrungKhit` 7/7 qua, cùng test mặc định `None` trùng khít. Bất biến 8: test thay
  thế được và luật tổng cầu (400 nhóm ứng viên, thứ tự nền của `uu_tien_wharton` + dự trữ mềm, có và không
  `tier_rank`) qua. Toàn bộ test: 1.923 qua, 211 bỏ qua do máy không tìm thấy Chromium (trình trợ giúp tìm
  `chrome-linux/chrome`, bản cài sẵn nằm ở `chrome-linux64/chrome`); chạy riêng 28 tệp giao diện với
  `RBDA_TEST_CHROMIUM` đặt tay: 253 qua, 0 bỏ qua. `ruff check .` 0 lỗi (mốc 0); độ phủ 92,11 % (sàn 85 %).
- **Chỗ cố ý lệch đặc tả.** (1) Điểm thi giữ `float`, không đổi `Decimal`: so `float` cho cùng thứ tự với
  `Decimal(str(x))` và điểm đọc thẳng từ cột REAL (ghi trong docstring). (2) Không có `round_id`, không làm số bốc
  SHA-256 / `public_value` (giữ STB). (3) Câu `wharton_chua_dung_het` mở đầu "Chưa dùng hết điểm Wharton…", không
  phải "Bạn chưa dùng hết…": `tests/test_van_phong_tu_nhien.py` cấm xưng hô "bạn/em" trong câu báo lỗi. (4) Câu
  `wharton_nguyen_vong_chua_xep` dùng `{session_l}` thay chữ "buổi" viết cứng, để workspace gọi là "ca" cũng đúng.
  (5) `kiem_ho_so_wharton` có thêm tham số tuỳ chọn `tran_nguyen_vong` (mặc định `TRAN_NGUYEN_VONG_MOI_BUOI`) vì
  workspace có thể đặt trần khác. (6) Mỗi ô điểm có tối đa một lỗi: khoá ngoài tập chỉ báo `wharton_ngoai_tap`.
  (7) W2 chỉ kiểm khi không dự trữ và không nhóm xếp cứng: có dự trữ thì em tầng 2 đủ diện dự trữ được giữ suất
  trước em tầng 1, có `tier_rank` thì nhóm đứng trước cả tầng — đo thử trên dữ liệu mô phỏng thấy đúng như vậy; đó
  là đặc tính cũ của dự trữ và nhóm, không do A13. Hai chế độ ấy được canh bằng W6 (ổn định).
- **Rủi ro đã ghi trong sổ.** "Khai thật là tốt nhất" chỉ được bảo đảm với THỨ TỰ nguyện vọng (W8), KHÔNG với
  cách chia điểm Wharton: người biết tính có thể lợi hơn người ngây thơ; cần đo bằng mô phỏng.
- **Việc vòng sau** (chưa làm): bảng `wharton_bids`; cột CSV / Sổ nhập (đổi hợp đồng cột, bất biến 7); nối
  pipeline (kiểm hồ sơ ở bước "kiểm dữ liệu", TRƯỚC khoá STB; thứ tự tự điền → kiểm hồ sơ → khoá STB → điểm hiệu
  lực → chạy); khoá luật workspace; biểu mẫu hai khung "Đã dùng X / 100"; mô phỏng VISEF; ngưỡng điểm tối thiểu;
  công bố điểm chuẩn.

## 2026-10-15 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

Ở giao diện tiếng Việt, màn chọn workspace còn "workspace" và ".zip" lẫn trong câu, và bảng bị vỡ.
Giao diện tiếng Anh giữ nguyên chữ cũ. Không đổi backend, thuật toán hay hợp đồng `{ok, data, errors}`.
- **Chữ tiếng Việt.** "workspace" → "không gian làm việc"; ".zip" → "tệp nén" (nút Xuất tệp nén / Nhập tệp nén,
  câu nhắc, thông báo). Sửa trong `i18n.js` (khối `vi`, các khoá `ws_*`), `i18n_errors.py` (sáu mã `ws_*` và bốn
  câu có "Workspace này"), `index.html` (chữ mặc định của nút thanh bên); `i18n_loi.js` sinh lại bằng
  `tao_i18n_js.py`. "thư mục _trash" giữ nguyên vì là tên thư mục thật trên đĩa.
- **Chuỗi do backend đặt, không đổi theo ngôn ngữ.** Tên mẫu dựng sẵn "Trường học" nay dịch ở JS theo khoá mới
  `ws_mau_truong_hoc` (vi "Trường học", en "School"); cột "Sửa lần cuối" hiện `15/10/2026 12:19:20` ở tiếng Việt,
  giữ `2026-10-15 12:19:20` ở tiếng Anh (`js/075_workspace.js`: `wsTenMau`, `wsDinhDangNgay`).
- **Bảng.** `display:flex` đặt thẳng lên `<td>` làm ô mất kiểu `table-cell`: nền hàng "Đang mở" dừng giữa chừng,
  đường kẻ lệch, nút Xoá rớt dòng. Nay `<td class="ws-cot-hanh-dong">` chứa `<div class="ws-hanh-dong">` (flex);
  hộp thoại rộng 1040px; cột Tên về font chữ thường (trước đó dùng font mã của `.data-table td:first-child`);
  `select` / `textarea` trong trình hướng dẫn kế thừa font. Màn hẹp thì sáu nút xuống dòng gọn trong ô.
- **Test mới (viết trước, thấy đỏ rồi mới sửa).** `tests/test_giao_dien_tieng_viet_sach.py`: thêm "workspace" vào
  danh sách cấm và một test quét thô chữ "zip". `tests/test_ws_giao_dien.py`: tiếng Việt không còn
  workspace/zip ở màn chọn và cả bốn bước hướng dẫn; tiếng Anh không còn chữ có dấu tiếng Việt ở màn chọn và ba
  bước đầu; tên mẫu và ngày đổi theo ngôn ngữ; bảng vẽ đúng (ô hành động là `table-cell`, mọi ô cao bằng hàng,
  sáu nút một dòng, nền phủ cả hàng, tên không dùng font mã).
- **Ảnh chụp chuỗi làm mới có chủ đích.** `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json`: chỉ 24 chuỗi `vi` đã đổi
  (5 mã lỗi `ws_*`, 19 khoá `ws_*` của giao diện); `test_ws_nhan.py` vẫn so toàn bộ phần còn lại như cũ.

## 2026-10-15 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

- **Skill mới `.claude/skills/tao-workspace-tu-raw/`**: raw bất kỳ (Excel/CSV tự do, Google/Microsoft Forms, hai
  tệp tách rời, văn bản dán) → workspace `.zip` nạp sẵn dữ liệu + Sổ nhập theo nhãn + `BAO_CAO_SOAT.md`.
  Bốn dạng nguyện vọng (`cot_xep_hang`, `mot_o`, `dong_dai`, `ma_tran`), đủ luật workspace, điểm theo chỗ / theo
  người. Đoán rồi hỏi duyệt; chỉ tiêu bắt buộc hỏi; sai một điều không ghi tệp nào; kiểm bằng `import_so_nhap` +
  báo cáo sức khoẻ + chạy thử; từ chối ghi đầu ra vào kho git (dữ liệu người thật). Không đụng mã sản phẩm.
  Test: `tests/test_skill_tao_workspace.py` (21 ca).
- **Bộ dữ liệu thử (mô phỏng)**: `du_lieu_test/bo_thu_chuong_trinh/` (trường 3 buổi, 180 học sinh) và
  `du_lieu_test/bo_thu_workspace/` (workspace "Công ty Bình Minh", zip nạp sẵn, kèm script sinh lại).

## 2026-10-14 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)

Bộ test Windows đỏ 24 ca trong khi Linux xanh. Hai nguyên nhân, một thật của sản phẩm và một của test:
- **Lỗi sản phẩm — `connect_db` rò kết nối khi tệp không phải SQLite.** PRAGMA đầu tiên ném mà kết nối chưa
  được đóng. Trên Linux không ai hay; trên Windows tệp đang mở không dời / xoá / đổi tên được (WinError 32 / 5),
  nên **xoá một workspace hỏng, nhập zip có `app.db` hỏng (thư mục tạm không dọn được), di trú `app.db` cũ hỏng**
  đều hỏng đúng lúc người dùng cần. Nay `connect_db` đóng kết nối rồi mới ném lại. Bộ dò
  `tests/test_ws_ket_noi_dong.py` bắt lỗi kiểu này NGAY TRÊN LINUX (kết nối bị huỷ mà chưa `close()`), và phủ các
  đường workspace / zip / di trú / chạy xếp. Vì sao Linux không thấy: kết nối sqlite3 của CPython 3.11 nằm trong vòng
  tham chiếu vòng (bộ nhớ đệm câu lệnh) nên chỉ nhả tệp khi GC chạy.
- **Lỗi của test.** (1) `with sqlite3.connect(db) as c` chỉ commit, KHÔNG đóng — các helper của
  `test_ws_registry.py` / `test_ws_sua_loi_3.py` nay dùng `contextlib.closing`. (2) Tiến trình con của
  `test_tham_khao_verify_nhanh.py` in tiếng Việt ra cp1252 nên `UnicodeEncodeError`: nay chạy `python -X utf8` và
  đọc đầu ra bằng UTF-8 (tái hiện được trên Linux bằng `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`: 33 ca đỏ
  trước, 0 sau). (3) So đường dẫn bằng `'/'` ghép tay: dùng `os.path.join`. (4) `write_text` / `open(..., "w")` thiếu
  `encoding="utf-8"` với nội dung tiếng Việt.

## 2026-10-14 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)

Mỗi mục có test trong `tests/test_ws_sua_loi_3.py` (viết trước, đỏ trước khi sửa):
- **Đọc cấu hình NGHIÊM ở nơi quyết định.** `run_pipeline`, `check_data_integrity`, trần nguyện vọng / thi
  (nhập tay, CSV, sổ), chấm điểm theo CLB đọc bằng `doc_cau_hinh(nghiem=True)` (`PipelineAPI._luat_nghiem`).
  Cấu hình có mà đọc không được (JSON hỏng, khoá của bản khác, CSDL bị khoá) thì dừng với lỗi mới
  `ws_cau_hinh_hong`, không lặng lẽ chạy bằng luật trường học rồi ghi `luat_xep = NULL`. `get_data_health_report`
  vẫn trả báo cáo nhưng thêm cảnh báo mức cao. `run_pipeline` đọc cấu hình MỘT lần (trước: hai lần, hai kết
  nối). Không có hàng cấu hình = mặc định, như cũ.
- `workspace.nhap_zip`: cấu hình trong zip đọc không được thì từ chối cả zip (trước: ghi mặc định đè lên luật thật).
- `update_workspace_config`: cập nhật MỘT PHẦN giữ nguyên phần không nhắc tới (`cau_hinh_ws.tron_len`); trước
  đây trộn lên mặc định trường học nên `{"name": "X"}` đặt lại mọi luật. Cấu hình cũ hỏng thì từ chối.
- `reset_student_entry` ("Sửa lại từ đầu") KHÔNG xoá `diem_ca_nhan` nữa (điểm do giáo viên chấm, không gắn
  với ô tick). *Đổi hành vi so với bản trước; test cũ đổi theo.*
- `delete_workspace` trên workspace "mở tạm" chuyển `db_path` sang workspace còn lại (không để trỏ vào `_trash`).
- `submit_club_scores` từ chối (`scoring_not_per_slot`) khi workspace chấm theo người hoặc `priority = tier`;
  CSV có điểm ở các chế độ đó: không lưu, cảnh báo `csv_score_ignored_mode`.
- Dấu vân tay kết quả, `run_history.luat_xep` và `run_full_pipeline` dùng luật HIỆU LỰC
  (`luat_xep_hieu_luc`): danh sách nhóm khi nhóm không cứng, `score_scope` khi chỉ theo nhóm... không còn
  làm kết quả báo "cũ". Luật mặc định không đổi (vân tay cũ giữ nguyên).
- Sổ nhập: cột điểm sai kiểu chấm (cột "Điểm k" ở workspace chấm theo người, hoặc cột "Điểm" đơn ở workspace
  chấm theo CLB) mà có dữ liệu thì báo `so_nhap_diem_sai_che_do` (trước: bỏ lặng lẽ, điểm mất).
- `xuat_zip` không nén chính zip đích (nằm trong thư mục workspace) và bỏ mọi `*.zip` trong thư mục.
- `main.khoi_dong_workspace`: bỏ qua workspace hỏng khi còn workspace lành (không còn rơi vào màn phục hồi vì một
  workspace hỏng); chỉ khi không cái nào mở được mới ném `WorkspaceKhoiDongHong(db_path)` cho màn phục hồi. Màn
  phục hồi dùng đúng tệp hỏng, hoặc workspace gần nhất khi `app.db` cũ đã di trú (trước: trỏ vào `app.db` không
  còn, "bắt đầu lại" đẻ ra tệp mồ côi).
- Nhóm cứng: nhập CSV không còn cảnh báo `csv_reserve_group_unknown` cho tên nhóm.
- Dọn: bỏ `main.chon_db_path` (chỉ test dùng) và khoá `bo_diem` của `tham_so_luat` (không ai đọc); tên trang
  Excel của tệp xuất dùng chung `so_nhap._ten_sheet`; docstring `cau_hinh_ws.py` nói đúng việc cấu hình
  nối vào thuật toán.
- `docs/ke_hoach/TIEN_DO.md`: thêm hàng WS (ngoài sổ) và ghi chú chồng lấn ở Z1, Z2 (chưa đóng mục).
- Hai việc còn lại sau vòng này (cùng ngày):
  - Mã lỗi riêng `ws_cau_hinh_hong` ở MỌI chỗ phụ thuộc cấu hình (trước chỉ ở chạy xếp / kiểm tra dữ liệu / báo
    cáo sức khoẻ; còn lại ra lỗi chung): nhập tay nguyện vọng và thi, nhập CSV, chấm điểm theo CLB và theo
    người, đọc / xem trước sổ nhập, tạo sổ mẫu, xuất dữ liệu đầu vào, hồ sơ học sinh, trạng thái kết quả. Bố
    cục sổ và tệp xuất cũng đọc cấu hình NGHIÊM (trước: đoán bằng mặc định trường học). Nhãn hiển thị vẫn
    đọc dễ tính. Test: `tests/test_ws_sua_loi_3.py` (mục P).
  - Màn phục hồi lúc khởi động được kiểm bằng `main.main()` thật và Chromium thật
    (`tests/test_ws_phuc_hoi.py`): đúng tệp hỏng trong thư mục workspace, thấy bản sao lưu cạnh nó, bấm
    "Khôi phục" đưa workspace về đúng dữ liệu, lần khởi động sau vào giao diện chính, và lỗi không nêu tệp thì
    dùng workspace gần nhất chứ không phải `app.db` cũ đã di trú.

## 2026-10-14 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)

Ghép `practical-faraday` (nền), `cool-hamilton` (tài liệu) và `upbeat-ride` vào nhánh này; bản workspace
cũ của nhánh còn ở `backup/nifty-truoc-khi-ghep`. Sửa các lỗi còn lại, mỗi lỗi một test
(`tests/test_ws_sua_loi_2.py`):
- `workspace.xoa`: workspace có `app.db` hỏng vẫn xoá được (sao lưu rơi về chép tệp thô, rồi dời vào `_trash`).
- `workspace.nhap_zip`: trần 500 MB giải nén cho cả zip, đếm BYTE THẬT khi chép (tiêu đề zip khai sao cũng
  được); bỏ `app.db-journal/-wal/-shm` và `*.bak-*` trong zip (SQLite tự phát lại nhật ký có sẵn); từ chối mục mã hoá.
- Slug: cắt ở 60 ký tự; `con`, `nul`, `com1`... (tên thiết bị Windows) thành `ws-<tên>`.
- `delete_workspace`: workspace "mở tạm" lúc khởi động nhiều workspace (người dùng chưa chọn) xoá được.
- `run_history.luat_xep` (cột mới, `ADD COLUMN`, không dựng lại bảng): JSON luật xếp đã dùng; NULL = luật mặc
  định của trường học (dòng cũ và workspace mặc định không đổi). `get_run_history` trả cột này.
- `run_full_pipeline` (đường thử nghiệm) từ chối chạy khi workspace có luật khác mặc định, thay vì xếp sai
  âm thầm.
- Nhãn workspace bắt đầu bằng `=`, `+`, `-`, `@` bị từ chối (`cau_hinh_ws.chuan_hoa`): nhãn thành tiêu đề cột / tên
  sheet của Sổ nhập, và openpyxl ghi `=...` thành ô công thức thật; nhãn có thể đến từ zip nhập vào. Cấu hình
  như thế đọc lại ra mặc định.
- Test giao diện `test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa` hết chập chờn: `#lastRunLine` và
  `#statStudents` do hai lời gọi API riêng điền, test từng assert ngay mà không chờ. Nay chờ `#lastRunLine`, và
  làm chậm `get_last_run_info` 600 ms để thứ tự trả về là chắc chắn (bản assert ngay đỏ ổn định với độ trễ này).
- `docs/ke_hoach/tham_khao`: `verify_stability_nhanh` nhận `bo_qua_du_tru`; bộ nạp `_chung.nap_rb` nạp thêm
  `nhan_ws` (từ bản có workspace, `i18n_errors` import nó), bản build cũ không có thì vẫn nạp được.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

- Không sửa hành vi. Ba điểm "móc lỗi chặn cả `import json`" là đúng hành vi: tệp `json.py` cạnh mã vẫn che được
  `json`, và lần chạy thật (thư mục đứng đầu sys.path) cũng hỏng ở chính móc đó — sai là ở LỜI: dòng CHANGELOG
  vòng R và chú thích test ghi "thư viện chuẩn" thay vì "dựng sẵn / đóng băng". Đã sửa lời (đánh dấu tại chỗ),
  docstring `_tu_thu_muc` (dòng tóm tắt còn ghi "nghi ngờ thì coi là có"), và thêm ca `import json` bị từ chối
  vào test làm chốt (228 ca, 2 bỏ qua tuỳ môi trường).
- `_khong_the_bi_che` nhớ theo tên (`functools.cache`).
- Bác: tên đã có trong `sys.modules` của tiến trình đo — `sys.modules` của lần chạy thật là của tiến trình khác;
  chỉ đáng kể khi có móc đường dẫn hỏng, đã báo lỗi rõ.
- Vòng lặp 2 dừng tại đây theo tiêu chí "một vòng không còn lỗi đúng/sai được xác nhận".

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)

Không điểm nào làm phép đo chạy nhầm mã; đều là chẩn đoán, độ chặt của test và một ca từ chối thừa hiếm gặp.
- `_chung`: lỗi khi xét một tên (móc đường dẫn hỏng với thư mục, lỗi trong bộ tìm / PathFinder) -> SystemExit nêu
  đúng tên và lỗi gốc, thay vì báo nhầm thành "mô-đun anh em"; lỗi móc với thư mục chỉ nêu khi thật sự cần xét
  một tên (mã chỉ import mô-đun dựng sẵn / đóng băng không bị chặn; *sửa ở vòng S: bản đầu ghi nhầm
  "thư viện chuẩn"*).
- Luật "dựng sẵn / đóng băng không bị che" còn một chỗ, đứng trước phép xét thư mục trong `la_ten`.
- Test (227 ca, 2 bỏ qua tuỳ môi trường): bộ tìm cài thêm ghi mọi tên ngoài thư viện chuẩn (không chỉ hai tên);
  ca lỗi PathFinder kiểm cả lỗi gốc và đặt mục lỗi cuối sys.path; 1 ca mới. 3 ca thất bại với bản vòng Q.
- Bác: PathFinder chạy các móc đường dẫn trên sys.path khi xét phần namespace — đó chính là việc mọi import của
  mã được đo làm trong cùng tiến trình; docstring ghi rõ điều này.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)

- `_chung`: mô-đun dựng sẵn / đóng băng ngoài `sys.stdlib_module_names` (`__phello__`, `xxsubtype`) lại được nhận
  (hồi quy của vòng P: bỏ ngoại lệ của vòng O mà không thay bằng `_khong_the_bi_che`).
- Móc đường dẫn ném lỗi khác ImportError với thư mục đã chọn -> SystemExit rõ (PathFinder cũng chỉ bỏ qua
  ImportError); mọi lỗi khi tìm phần namespace (kể cả PathFinder trên sys.path) -> coi là có, từ chối rõ — không
  còn traceback. Không móc nào nhận thư mục -> trả ngay hàm luôn "không".
- Test (226 ca, 2 bỏ qua tuỳ môi trường): 3 ca mới, đều thất bại với bản vòng P (đã kiểm là lỗi thật, không phải
  lỗi cú pháp của mã test); bộ tìm cài thêm trong test chỉ ghi tên đang xét (không bắt nhầm import khác);
  `_chay_tien_trinh_moi` nối mã test sau một dòng mới (mã bắt đầu bằng `def` / `try` không còn thành lỗi cú pháp
  lặng lẽ).
- Bác:
  - Không dùng `sys.path_importer_cache[thu_muc]` của tiến trình đo: lần chạy thật là một tiến trình khác, bộ
    nhớ đệm trống, dựng bộ tìm từ `sys.path_hooks` — đúng như kịch bản làm.
  - Mô-đun đóng băng ở tiến trình đo nhưng không đóng băng ở lần chạy thật với cờ / bản Python khác: như vòng O —
    phép đo chạy trong chính trình thông dịch này, đối chiếu là nạp bình thường trong cùng trình thông dịch.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)

- `_chung`: **rút lại** việc hỏi các bộ tìm cài thêm trong `sys.meta_path` (vòng O). Đã tái hiện: hỏi
  `DistutilsMetaFinder` của setuptools về `distutils` / `pip` làm đổi trạng thái tiến trình đo; một bộ tìm chuyển
  tiếp cho PathFinder (kiểu móc của pytest / typeguard) làm tệp `pytest.py` cạnh mã lọt qua — lần chạy thật thư
  mục đứng đầu sys.path nên chính bộ tìm đó trả tệp cạnh mã (đo nhầm mã, lặng lẽ).
- Luật mới, bảo thủ (nghi ngờ thì từ chối rõ, không bao giờ đo nhầm): chỉ mô-đun dựng sẵn / đóng băng (hai bộ
  tìm của CPython, không tác dụng phụ) được coi là không thể bị che; bộ tìm của thư mục dựng từ `sys.path_hooks`
  như PathFinder làm (móc đường dẫn kiểu Hy thêm đuôi mới cũng được tính), lỗi khi tìm thì coi là có; phần
  namespace chỉ được nhận khi PathFinder trên sys.path tìm được mô-đun / gói thường. Tên do bộ tìm cài thêm cung
  cấp mà thư mục cũng có thì bị từ chối (ca `hookmod/` của vòng O đổi từ "nhận" sang "từ chối, không gọi bộ tìm").
- Một hàm phân loại duy nhất (`_tu_thu_muc`, nhớ theo tên); bỏ `_bo_tim_truoc_cung_cap` và lần gọi lặp trong
  `la_ten`.
- Test (223 ca, 2 bỏ qua tuỳ môi trường): ca bộ tìm cài thêm của vòng O thay bằng 2 ca bảo thủ (kèm kiểm bộ tìm
  không bị gọi lần nào) + 1 ca `sys.path_hooks`; cả 3 thất bại với bản vòng O.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)

- `_chung`: sửa tận gốc luật mô-đun anh em — bỏ các luật tự bắt chước hệ thống import (`_anh_em`,
  `_nap_truoc_filefinder`, `_mo_dun_thuong_ngoai`; bốn vòng K–N mỗi vòng lại thấy một chỗ lệch) và hỏi chính các
  bộ tìm theo đúng thứ tự import: bộ tìm trong `sys.meta_path` đứng trước PathFinder (dựng sẵn, đóng băng, móc
  cài thêm) → FileFinder của thư mục đã chọn → PathFinder trên sys.path (gói thường thắng phần namespace).
  Không gọi PathFinder với thư mục đã chọn (giữ sys.path_importer_cache sạch); kết quả nhớ theo tên trong một lần nạp.
- Tên do bộ tìm đứng trước PathFinder cung cấp được nhận (vòng N từ chối nhầm khi có thư mục dữ liệu cùng tên).
- Docstring `_import_la` theo luật mới. Test dựng sẵn / đóng băng bỏ qua trên trình thông dịch không đóng băng `os`.
- Test (221 ca, 2 bỏ qua tuỳ môi trường): 1 ca mới thất bại với bản vòng N; mọi ca của vòng K–N vẫn qua với
  cách làm mới (lưới hồi quy cho lần viết lại).
- Bác:
  - Tệp cạnh mã trùng tên mô-đun đóng băng trên một trình thông dịch KHÁC (phiên bản cũ, `-X frozen_modules=off`):
    kịch bản đo chạy mã trong chính trình thông dịch đang chạy; đối chiếu là nạp bình thường trong cùng trình
    thông dịch đó, không phải một bản Python khác.
  - Thư mục hiện hành nằm trên sys.path của tiến trình kiểm (`python -m`, pytest) che phần namespace: cách chạy
    ghi trong CLAUDE.md (`python <kịch bản> <thư mục>`) không đưa thư mục hiện hành vào sys.path; tình huống cần
    hai bản kho mã lệch nhau ở đúng một tên — xa thực tế, không đáng thêm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)

- `_chung` (luật mô-đun anh em): mô-đun dựng sẵn / đóng băng (`time`, `os`…) xét TRƯỚC — BuiltinImporter /
  FrozenImporter chạy trước FileFinder nên tệp cùng tên cạnh mã không che được (vòng M từ chối nhầm). Thư mục
  không `__init__` cạnh mã chỉ được nhận khi tên là mô-đun / gói THƯỜNG trên sys.path (PathFinder); gói
  namespace đã cài thì thư mục được gộp vào (`nsgoi.helper` chạy thật lấy từ thư mục) — từ chối (vòng M nhận nhầm).
- Docstring `_import_la` theo luật hiện hành; `importlib.machinery.all_suffixes()`; `with os.scandir(...)`.
- Test (220 ca, 1 bỏ qua khi chạy bằng root): 2 ca mới, đều thất bại với bản vòng M.
- Bác, kèm đường đã lần:
  - Thoát tiến trình qua bí danh (`_s.exit`, `from os import _exit`, `os.abort`) và nhánh except ghi bằng
    thuộc tính / biến bộ (`except errors.ImportError`, `except _LOI`): luật import tuỳ chọn chỉ còn áp cho tên
    KHÔNG có trong thư mục; với tên đó, chạy thật và chạy dưới kịch bản tìm trên cùng sys.path nên hành xử
    giống nhau — sai ở đây chỉ làm thông báo lỗi muộn hơn, không làm phép đo đo nhầm mã. Theo dõi bí danh tốn
    mã hơn lợi ích.
  - Thư mục dữ liệu namespace (vd `mau_csv/`) trong try/except ImportError vẫn bị từ chối: chạy thật gán một
    gói namespace rỗng, dưới kịch bản gán None — hai lần chạy đi hai nhánh khác nhau, từ chối là đúng.
  - Chi phí stat cho mỗi thư mục con: vài chục lần stat mỗi lần nạp, không đáng kể.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)

- `_chung` (luật mô-đun anh em) bám đúng FileFinder: tính cả bản biên dịch không nguồn (`.pyc`); tên tệp là
  phần trước ĐÚNG đuôi (tệp `random.old.py` không phải `random`); thư mục không có `__init__` chỉ là phần gói
  namespace — không che thư viện chuẩn / gói đã cài, chỉ bị coi là anh em khi tên không có ở đâu khác (vòng L
  từ chối nhầm mã hợp lệ khi có thư mục dữ liệu tên `random/`, `csv/`...).
- Import tuỳ chọn: thân lớp chạy ngay nên được đường lui che (vòng L từ chối nhầm); xét nhánh except ĐẦU TIÊN
  bắt được ImportError theo thứ tự (kể cả `except Exception`), nhánh kết thúc bằng ném lại hay
  `sys.exit` / `os._exit` / `exit` / `quit` không phải đường lui. Điều kiện động (`if STRICT: raise`) không xét
  được tĩnh — coi là đường lui, ghi trong docstring.
- Chỉ kiểm / biên dịch các mô-đun CÒN THIẾU (i18n_errors đã nạp đúng bản thì không đọc lại), dựng đủ rồi mới
  gán. Spec không có bộ nạp và `cached = None` (vòng L chỉ đặt `__cached__`, `__spec__` vẫn trỏ .pyc và
  `importlib.reload` đi vòng qua phép kiểm). `functools.cache` thay danh sách tự chế.
- Test (218 ca, 1 bỏ qua khi chạy bằng root): 8 ca mới thất bại với bản vòng L (ca gói thường `random/__init__.py` đã đúng từ vòng L, giữ
  làm chốt chặn khi thu hẹp luật thư mục).
- Bác: nhãn "ngoài sổ" trái quy tắc 1 của CLAUDE.md — quy tắc cho phép khi đã hỏi; việc này do Truong (chủ dự
  án) yêu cầu trực tiếp, nhãn ghi đúng điều đó.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)

- `_chung` (kiểm import): thêm luật **mô-đun anh em** — tên có mặt trong thư mục đã chọn (tệp .py, mô-đun mở
  rộng, thư mục) mà không được phép thì luôn bị từ chối, kể cả nằm trong `try/except ImportError` hay trùng tên
  gói đã cài (vòng K để lọt: `try: import rbda_priority_pipeline` trong i18n_errors; tệp `openpyxl.py` cạnh mã).
  Import tuỳ chọn chỉ được che khi nằm trực tiếp trong khối try (không vào thân hàm / lớp định nghĩa ở đó) và
  nhánh except không chỉ ném lại; nhận cả `except*`. Danh sách gói đã cài quét một lần, chỉ khi cần.
- Kiểm và biên dịch CẢ HAI tệp trước khi chạy tệp nào (vòng K chạy i18n_errors rồi mới đọc mô-đun chính).
  Thông báo nêu đúng tệp được import gì (i18n_errors: không mô-đun nào của kho mã, vì nó nạp trước).
- `__cached__ = None` (không trỏ tới .pyc không tồn tại); `compile(..., dont_inherit=True)`.
- Test (209 ca): khôi phục test "không thêm mục cache bộ tìm" (bỏ ở vòng K là sai: nó chặn hồi quy kiểu chèn
  tạm sys.path); 9 ca mới, đều thất bại với bản vòng K.
- Bác phần còn lại của điểm 6 (không dùng bộ nhớ đệm .pyc): cố ý từ vòng H–I (bản .pyc cũ từng bị dùng nhầm);
  phân tích + biên dịch mô-đun chính tốn ~46 ms mỗi tiến trình, không đáng kể so với phép đo.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)

- `_chung` (kiểm import tĩnh của vòng J): nhận cả gói đã cài trong site-packages (theo `importlib.metadata.packages_distributions`) — vòng J đã thu hẹp quá mức mà CHANGELOG không ghi; bỏ qua import tuỳ chọn trong khối `try/except ImportError`; `i18n_errors` (nạp trước) không được import `rbda_priority_pipeline` (sẽ lấy nhầm bản khác); import tương đối báo đúng tên mô-đun (`.helpers`, không phải `.helpers.f`); bỏ điều kiện thừa `__future__`.
- Kiểm và biên dịch NGAY LÚC NẠP từ đúng bản đã đọc (`compile(cây ast)` rồi `exec`): không còn khe giữa lúc kiểm và lúc chạy; lỗi đọc / cú pháp / byte NUL thành SystemExit rõ; đã nạp đúng thư mục thì trả bản đã nạp mà không đọc lại tệp.
- Test (199 ca): bỏ test cache không thể thất bại (vòng J); 5 test mới, đều thất bại với bản vòng J.
- Bác: một tệp tên trùng thư viện chuẩn (vd `random.py`) chen trên sys.path — mối nguy chung của mọi chương trình Python, ngoài phạm vi kịch bản; phép kiểm theo đường dẫn của vòng I từng có báo nhầm nặng hơn.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)

- `_chung`: đính chính vòng I — phép kiểm "mô-đun anh em" chạy SAU khi nạp nên bỏ lọt import bên trong hàm (đúng kiểu import của mã này; đã tái hiện), từ chối nhầm mô-đun C của thư viện chuẩn trên Windows (`<base>\DLLs`), không dùng tham số `thu_muc`, và để lại mô-đun lạ trong sys.modules. Thay bằng kiểm TĨNH trước khi chạy gì: đọc cả hai tệp nguồn bằng `ast`, lấy mọi import (đầu tệp lẫn trong hàm, kể cả import tương đối) và từ chối tên không thuộc `sys.stdlib_module_names` hay `i18n_errors` / `rbda_priority_pipeline`. Bỏ `_thu_muc_chuan`, `_phu_thuoc_la` (không còn đoán theo đường dẫn, không còn sysconfig). Hai tệp thật của kho qua kiểm (không import lạ).
- Test (195 ca): 4 ca import lạ (đầu tệp, trong hàm, anh em ngay thư mục chọn, import tương đối — đều thất bại với bản vòng I) và kiểm không mô-đun nào bị nạp; 1 ca nhận mô-đun C của thư viện chuẩn; 1 ca thư mục chưa có mục cache vẫn không có sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)

- `_chung.nap_rb` (thư mục), sửa tận gốc theo điểm "sai tầng": bỏ hẳn cơ chế đoán tệp Python sẽ nạp (`sys.path_hooks`, bộ tìm riêng, các ca .so / gói / namespace — thêm dần từ vòng C tới H). Nay nạp THẲNG `<thư mục>/<tên>.py` bằng `spec_from_file_location`: bản biên dịch cũ, gói cùng tên, gói namespace nằm cạnh không thể chen vào; không đụng sys.path hay cache bộ tìm; không còn đường lỗi traceback từ bộ tìm hay loader cũ. Đổi hành vi có chủ đích: thư mục chỉ có bản biên dịch không kèm nguồn (.pyc) nay bị TỪ CHỐI (kịch bản đo mã nguồn) — đảo lại phần nhận .pyc của vòng C–D.
- Mới: nếu mã được nạp import thêm mô-đun ngoài thư viện chuẩn / site-packages (vd một phiên bản khác import mô-đun anh em, lấy nhầm từ thư mục khác trên sys.path), từ chối thay vì đo lẫn mã. Mã hiện tại chỉ import thư viện chuẩn và `i18n_errors` (đã kiểm).
- Test (190 ca): viết lại nhóm test bộ nạp thư mục theo thiết kế mới (8 test thất bại với bản vòng H vì hành vi đổi có chủ đích hoặc vì mô-đun anh em trước đây lọt).
- Bác: khoá import và "đọc lại sys.modules sau exec" của bộ import — kịch bản chạy một luồng, và `_nap_co_kiem` đã kiểm nguồn của mục sys.modules sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)

- `_chung.nap_rb` (thư mục), sửa tận gốc: không còn import theo tên qua sys.path nữa. Hỏi bộ tìm mà CHÍNH Python dùng (gọi `sys.path_hooks` như PathFinder, kể cả hook tuỳ biến, nhưng tạo mới và không ghi cache) lấy spec cho từng mô-đun, rồi nạp ĐÚNG spec đó (`module_from_spec` + `exec_module`, đặt vào sys.modules trước như import). Hệ quả: dự đoán và lần nạp thật không thể lệch; bỏ toàn bộ phần sửa / khôi phục sys.path và `sys.path_importer_cache` (vòng G bỏ sót bước xoá mục cũ trước khi import nên có thể đi qua bộ tìm cũ hoặc mục None — đã tái hiện bằng test); thư mục mất quyền giữa chừng vẫn báo lỗi đọc.
- Test (193 ca): test cache tự gieo mục sẵn có (không còn đúng vô nghĩa khi cache trống); test thư mục đã ở trên sys.path với mục cache cũ None (thất bại với bản vòng G).

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)

- `_chung`: đính chính vòng F — `nap_rb` vẫn để lại bộ tìm tệp của thư mục trong `sys.path_importer_cache` (vòng F chỉ dọn ở `_tep_se_nap`; đã tái hiện). Nay `_tep_se_nap` dùng một `FileFinder` RIÊNG (cùng thứ tự loại tệp như mặc định) nên không đụng cache toàn cục, và bước import của `nap_rb` trả mục cache về như cũ (không để lại cho thư mục tạm, không thay bộ tìm sẵn có). Kiểm đọc được thư mục bằng `os.scandir` (rẻ); lỗi OSError khi tìm thành SystemExit; docstring nói rõ thư mục không có `<tên>.py` thì nhận đúng thứ Python nạp.
- Test (192 ca): test chmod 000 thật (bỏ qua khi chạy root hay Windows; CI Linux chạy được); `.pyc` trong `__pycache__` bỏ qua khi `cache_tag` là None; 2 test cache bộ tìm (thất bại với bản vòng F); test giả lập lỗi quyền đổi sang `os.scandir` (thất bại với bản vòng F chỉ vì vòng F dùng `os.listdir`).
- Bác: thư mục chỉ có gói `rbda_priority_pipeline/__init__.py` (không có `.py`) được nhận — đúng ý: đó là mã Python sẽ chạy khi import từ thư mục đó; docstring đã ghi rõ.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)

Không điểm nào làm phép đo sai; đều là thông báo lỗi và độ vững của test.
- `_chung._tep_se_nap`: thư mục không đọc được báo đúng "Không đọc được thư mục" (FileFinder nuốt lỗi quyền rồi trả None nên trước đây báo nhầm "không có mô-đun"); tạo bộ tìm tệp mới mỗi lần và không để lại trong `sys.path_importer_cache`; thông báo nêu cả khả năng "gói cùng tên nằm cạnh". `nap_rb` kiểm mô-đun chính trước, nên thư mục sai báo thiếu `rbda_priority_pipeline`.
- Test (190 ca): test `__pycache__` ghi .pyc vào đúng chỗ và kiểm là có (không thành vô nghĩa khi đặt PYTHONPYCACHEPREFIX); 4 test mới, đều thất bại với bản vòng E.
- Bác: gọi `nap_rb` lần hai trên cùng thư mục sau khi tệp trong đó đổi giữa chừng thì bị từ chối — chỉ là từ chối (đòi tiến trình mới), không bao giờ đo nhầm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)

- `_chung.nap_rb`, sửa tận gốc: bỏ các luật đoán theo tên tệp (`_co_mo_dun`, phần tiền tố của `_cung_nguon`); hỏi chính bộ import của Python (`importlib.machinery.PathFinder.find_spec`) tệp nào sẽ được nạp từ thư mục, rồi đòi đúng tệp đó sau khi nạp. Hệ quả: .pyc có thẻ trong `__pycache__` (Python không nạp) và hậu tố mở rộng của hệ khác không còn bị nhận nhầm; thư mục chỉ có `__pycache__` báo SystemExit rõ thay vì traceback; bản mở rộng cũ chen trước tệp nguồn vẫn bị từ chối; gói namespace bị chặn ngay ở bước kiểm trước (không phụ thuộc sys.path của máy); thông báo nêu đúng tệp mong đợi; lỗi đọc thư mục thành SystemExit; thông báo "đã nạp nơi khác" nêu nguồn thật (gói namespace, mục None).
- Test (186 ca): 2 test cho hàm mới `_tep_se_nap` (thất bại với bản vòng D chỉ vì hàm chưa có) và 1 test hành vi qua `nap_rb` (thất bại thật với bản vòng D).
- Bác: điểm cũ float và điểm mới Decimal cùng giá trị bị coi là "đổi" — giữ, vì đổi kiểu có thể đổi thứ hạng thật: `Decimal('7.1') > 7.1` (float 7.1 là 7,0999…), nên từ chối là đúng.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)

- `_chung.nap_rb`: sửa lỗi do vòng C đưa vào — khi thư mục CÓ `<tên>.py`, chỉ nhận đúng tệp đó; một bản biên dịch cũ (.so/.pyd) nằm cạnh mà Python ưu tiên nạp trước bị từ chối (trước đây vòng C nhận nó và đo nhầm mã cũ). Bản biên dịch không kèm nguồn chỉ được nhận khi KHÔNG có .py, nay cho cả mô-đun chính; gói namespace chen vào được nêu đúng nơi (thay vì "None").
- `exp_resume.kiem_tien_de`: nhận điểm Decimal (không là numbers.Real); chỉ kiểm điểm của dữ liệu mới (điểm em cũ đã phải bằng hệt dữ liệu cũ).
- Test (184 ca): bỏ test tiền đề không có khẳng định (luôn xanh), giữ lý do thành chú thích; 4 test mới, đều thất bại với bản vòng C.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)

- `exp_resume.kiem_tien_de`: một luật `_so_hop_le` cho mọi số mà `compute_club_priority` sắp (số bốc thăm và điểm): điểm là chuỗi CSV, None, bool, pd.NA hay NaN đều bị từ chối bằng ValueError rõ (trước đây chuỗi / None lọt kiểm rồi gây TypeError giữa `resume_da` — đã tái hiện).
- `_chung.nap_rb`: nhận bản biên dịch không kèm nguồn (`i18n_errors.pyc` trong đúng thư mục) thay vì báo "nạp nhầm"; thông báo lỗi sau khi nạp nêu đúng nguồn thực và nguồn mong đợi.
- Test (181 ca): test tiền đề về NaN chuyển thành tự bỏ qua nếu sau này mã sản phẩm xử lý NaN xác định (không chặn bản sửa đúng); thêm 8 ca điểm không hợp lệ (2 ca NaN thất bại với bản vòng B chỉ vì đổi thông báo lỗi; 6 ca chuỗi / None / bool là lỗi thật) và 1 ca `.pyc`.
- Hồ sơ: đính chính câu "6 test mới đều thất bại" của vòng B; cập nhật ngày ở TIEN_DO.md.
- Bác: từ chối NaN cả ở điểm không ảnh hưởng thứ hạng (em không có trong apps, điểm nhập trước của em mới) — giữ, vì thận trọng: chỉ tốn một lần chạy lại toàn bộ, không bao giờ cho kết quả sai.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)

- `_chung.nap_rb`: kiểm SAU khi nạp rằng mỗi mô-đun đến đúng từ thư mục / bản build đã chọn — thư mục thiếu `i18n_errors.py` trước đây lặng lẽ lấy tệp cùng tên ở chỗ khác trên sys.path (đã tái hiện), nay từ chối và gỡ mô-đun; mục sys.modules không rõ nguồn (None, mô-đun giả) báo rõ; tệp build không chứa mô-đun cần thiết báo SystemExit thay vì KeyError.
- `exp_resume.kiem_tien_de`: TỪ CHỐI điểm NaN (cả em cũ lẫn em mới) — `compute_club_priority` cho thứ tự phụ thuộc thứ tự đầu vào khi có NaN (đã tái hiện), nên vòng A coi NaN == NaN là sai; chưa nạp mô-đun rbda là RuntimeError (lỗi cài đặt, để người gọi bắt ValueError rồi chạy lại toàn bộ không nuốt mất).
- Test (174 ca): 7 test mới — 6 thất bại với bản vòng A; 1 là test tiền đề chỉ chạy mã sản phẩm (`compute_club_priority` với NaN) nên không phân biệt hai bản (đính chính ở vòng C).
- Bác: (1) em mới đã có trong apps/điểm của dữ liệu cũ làm `resume_da` lệch — thử 5.000 thể hiện ngẫu nhiên có trường hợp này: 0 lệch; (2) bản nhanh gọi `club_choice_function` một lần mỗi CLB làm chậm — đo 10.000 HS: 0,037 s so với 0,034 s, không đáng kể so với giá trị (khớp mọi kiểm tra đầu vào của bản gốc).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)

Quyết định của Truong: KHÔNG sửa mã sản phẩm (phân xử em không có thứ hạng trong `club_choice_function` vẫn hoãn); lặp tới khi một vòng không còn lỗi đúng đắn.
- `exp_resume.kiem_tien_de`: mọi vi phạm là ValueError (kể cả chưa nạp rbda); bỏ em mới ở CẢ dữ liệu cũ khi so điểm / apps (điểm nhập trước cho em đến muộn không còn báo nhầm "em cũ đổi"); nhóm dự trữ '' và None coi như một (như `default_reserve_eligible_fn`); điểm NaN không đổi không bị báo đổi; kiểm thứ tự bốc thăm sắp một lần; `resume_test` dùng bản rbda đã nạp.
- `de_xuat_verify_nhanh.py`: lần đầu xét mỗi CLB, gọi đúng lời gọi `club_choice_function` của bản gốc (đang giữ + ứng viên, hàm đủ tư cách và thứ hạng thật) — mọi kiểm tra đầu vào, hiện tại và sau này, chạy y hệt.
- `_chung.py`: một hàm `_nap_co_kiem` cho cả thư mục lẫn bản build (kiểm "đã nạp nơi khác", trả bản đã nạp, gỡ mô-đun dở dang); thư mục lấy theo đường dẫn người dùng đưa (không theo đích liên kết); đường dẫn không tồn tại báo rõ; đọc được tệp PyInstaller < 6 (mục `PYZ-00.pyz`, mục lục dict).
- Test (169 ca): 7 test mới, đều thất bại với bản trước; chuỗi so lỗi chính xác ("thứ tự bốc thăm"); đường dẫn Windows dự phòng thật sự viết khác.
- Bác: gộp đoạn mồi 4 dòng (lý do như trước); thay `compute_club_priority` bằng chèn bisect trong `resume_da` (ghi ở DOI_CHIEU, để khi làm G1); sửa phân xử trong `club_choice_function` (chủ dự án hoãn).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)

- `exp_resume.kiem_tien_de`: số bốc thăm phải là số thực (không chuỗi CSV, không bool, không NaN) — báo ValueError rõ; kiểm sức chứa dùng bản rbda đã nạp kể cả khi `exp_resume.rb` chưa gán (trước đây lặng lẽ bỏ qua).
- `_chung.nap_rb`: so đường dẫn như hệ điều hành (liên kết, hoa/thường Windows) khi nạp lại cùng .exe; nhánh thư mục nạp hỏng cũng gỡ mô-đun dở dang như nhánh bản build.
- Test (162 ca): lần đầu có test cho đường nạp `.exe` (tệp PyInstaller tối thiểu dựng trong test): nạp, nạp lại qua đường dẫn khác, nạp hỏng không để mô-đun dở dang, lệch phiên bản Python; danh sách cấm cả `.index`/`.count`; dùng đúng một bản `_chung` trong tiến trình; sửa chú thích sai (v + 20).
- Bác một phần: kiểm sức chứa trong `kiem_tien_de` lặp lại luật của `club_choice_function` — giữ, vì cần nêu tên CLB trước khi làm việc và chỉ tốn một lần gọi mỗi CLB.

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).
