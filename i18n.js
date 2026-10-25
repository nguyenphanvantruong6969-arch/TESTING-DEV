/* ==========================================================================
   i18n.js — bilingual (vi/en) text catalog + helpers for the kiosk UI.
   ==========================================================================
   ERROR_MESSAGES is NOT written here: it comes from i18n_loi.js, which
   tao_i18n_js.py generates from MESSAGES in i18n_errors.py (the single
   source). Edit i18n_errors.py, then run `python tao_i18n_js.py`.
   UI_STRINGS covers every other string the app shows: static HTML text
   (via data-i18n[-placeholder|-html] attributes, applied by
   applyStaticText()) and dynamic text js/*.js builds at runtime (via
   I18N.t(key, params)).
   ========================================================================== */

(function (global) {
  "use strict";

  /* Bảng thông báo lỗi SINH TỪ i18n_errors.py (tệp i18n_loi.js, nạp trước
     tệp này). Không chép tay ở đây nữa — sửa i18n_errors.py rồi chạy
     `python tao_i18n_js.py`. */
  const ERROR_MESSAGES = global.I18N_ERROR_MESSAGES || {};

  const UI_STRINGS = {
    vi: {
      th_muc: "Mức",
      th_thao_tac: "Thao tác",
      th_chon: "Chọn",
      page_title: "Sắp xếp {slot} · RB-DA",
      lang_toggle_label: "EN",
      brand_title: "Sắp xếp {slot_sl}",
      brand_sub: "Reserve-Based DA",
      nav_pipeline: "Vận hành sắp xếp",
      nav_results: "Kết quả",
      nav_fallback: "Nhập tại chỗ",
      nav_admin: "Quản lý {slot_sl} & dự trữ",
      nav_scoring: "Nhập {score_l}",
      db_status_loading: "Đang tải…",
      db_connected: "Đã kết nối dữ liệu",
      backend_dang_ket_noi: "Đang kết nối với phần lõi chương trình…",
      api_chua_san_sang: "Chương trình chưa sẵn sàng. Đợi vài giây rồi thử lại.",
      api_mat_ket_noi: "Không liên lạc được với phần lõi chương trình. Hãy thử lại; nếu vẫn lỗi, đóng cửa sổ rồi mở lại chương trình.",
      loi_giao_dien_ngoai_du_kien: "Có lỗi ngoài dự kiến trên màn hình. Hãy thử lại. Nếu vẫn lỗi, đóng rồi mở lại chương trình.",
      backend_khong_ket_noi: "Chưa kết nối được dữ liệu",
      backend_qua_han: "Chương trình chưa khởi động xong. Hãy đóng cửa sổ rồi mở lại. Nếu vẫn không được, gửi tệp loi_khoi_dong.txt (nằm trong thư mục dữ liệu) cho người phụ trách.",
      display_native: "Cửa sổ ứng dụng riêng",
      display_browser: "Chế độ dự phòng (trình duyệt)",
      last_run_line: "Chạy gần nhất: {run_at} (số khởi tạo {seed}, xếp được {n_matched}/{n_total})",
      never_run: "Chưa chạy sắp xếp lần nào",

      pipeline_title: "Vận hành sắp xếp",
      pipeline_desc: "Kiểm tra dữ liệu, bốc thăm, xếp {person_l} vào {slot_sl} và xuất kết quả.",
      label_students: "{person_l}",
      label_clubs: "{slot_sl}",
      label_submitted_prefs: "đã nộp nguyện vọng",
      label_matched: "đã xếp {slot_sl}",
      import_panel_title: "Nhập dữ liệu",
      import_hint: "Toàn bộ dữ liệu nằm trong một tệp Excel duy nhất: Sổ nhập CLB. Chưa có sổ thì bấm \"Tải sổ nhập mẫu\", điền danh sách {slot_sl} và {person_l}, lưu lại rồi kéo sổ vào ô bên dưới.",
      drop_zone_main: "Kéo Sổ nhập CLB vào đây",
      drop_zone_sub: "Một tệp Excel (.xlsx). Bấm để chọn tệp.",
      btn_import_all: "Nhập sổ",
      btn_clear_queue: "Bỏ tệp",
      btn_tai_so_mau: "Tải sổ nhập mẫu",
      so_mau_da_tao: "Đã tạo sổ nhập ({n} {slot_sl} điền sẵn) → {path}",
      so_nhap_dang_doc: "Đang đọc sổ…",
      so_nhap_tom_tat: "Sẵn sàng nhập: {n_clb} {slot_sl} · {n_buoi} {session_l} · {n_hoc_sinh} {person_l} · {n_nguyen_vong} nguyện vọng · {n_thi} lượt thi",
      so_nhap_co_loi: "Sổ có {n} lỗi cần sửa. Chưa nạp gì cả. Hãy sửa trong Excel, lưu lại rồi kéo sổ vào lần nữa.",
      so_nhap_loi_con_lai: "… và {n} lỗi khác.",
      so_nhap_xong: "Xong: {n_clb} {slot_sl}, {n_hoc_sinh} {person_l} ({n_moi} {person_l} mới, {n_bo} bỏ qua)",
      so_nhap_khong_nap: "Không nạp được sổ. Xem lý do ở dưới.",
      so_nhap_canh_bao_tieu_de: "Lưu ý trước khi nhập:",
      xuat_kq_ten_doi: "  {n} {slot_sl} trùng tên với {slot_sl} khác nên được thêm mã vào tên trong sổ.",
      steps_panel_title: "Các bước xử lý",
      label_seed: "Số khởi tạo bốc thăm",
      seed_locked_hint: "Số khởi tạo {seed} được khoá cùng số bốc thăm. Muốn đổi, bấm \"Bốc thăm lại…\".",
      seed_unlocked_for_redraw: "Đang chờ bốc thăm lại: có thể nhập số khởi tạo mới trước khi bấm \"Chạy sắp xếp\".",
      btn_validate: "Kiểm tra dữ liệu",
      btn_run_pipeline: "Chạy sắp xếp",
      btn_dang_chay: "Đang chạy…",
      hat_giong_khong_hop_le: "Số khởi tạo bốc thăm phải là một số nguyên, ví dụ 2026. Hãy sửa ô này rồi bấm chạy lại.",
      btn_dong: "Đóng thông báo",
      step_title_backup: "Sao lưu dữ liệu",
      step_title_rollback: "Hoàn tác",
      step_title_unknown: "Lỗi ngoài dự kiến",
      toast_run_success_no_backup: "Lưu ý: chưa sao lưu được dữ liệu trước lần chạy này.",
      step_title_validate: "Kiểm tra dữ liệu",
      step_title_stb: "Bốc thăm",
      step_title_rbda: "Xếp {person_l} vào {slot_sl}",
      step_title_write: "Lưu kết quả",
      step_title_export: "Xuất kết quả",
      step_not_run_yet: "Chưa chạy",
      step_running: "Đang chạy…",
      step_done_default: "Hoàn tất",
      generic_error: "Có lỗi xảy ra",
      error_log_title: "Các lỗi cần xử lý",
      history_panel_title: "Lịch sử sắp xếp",
      btn_toggle: "Hiện/ẩn",
      th_time: "Thời điểm",
      th_seed: "Số khởi tạo",
      th_rounds: "Số vòng",
      th_matched_count: "Đã xếp",
      th_total: "Tổng",
      th_buoi_da_chay: "{session} đã xếp",
      th_redrawn: "Đã bốc lại",
      history_empty: "Chưa có lần sắp xếp nào.",
      yes: "Có",
      no: "Không",

      results_title: "Kết quả",
      results_desc: "{person} đã được xếp vào {slot_sl} nào và mỗi {slot_sl} đã đủ chỗ chưa.",
      aria_thu_gon_muc: "Thu gọn hoặc mở rộng mục này",
      hieu_ung_bat: "Hiệu ứng: bật",
      hieu_ung_tat: "Hiệu ứng: tắt",
      aria_hieu_ung: "Bật hoặc tắt hiệu ứng chuyển động để máy chạy nhanh hơn",
      btn_thu_gon_tat_ca: "Thu gọn tất cả",
      btn_mo_rong_tat_ca: "Mở rộng tất cả",
      dem_hoc_sinh: "{n} {person_l}",
      dem_cau_lac_bo: "{n} {slot_l}",
      dem_dong: "{n} dòng",
      clb_title: "Theo từng {slot_l}",
      clb_desc: "Không cộng dồn cột \"Số {person_l} đăng ký\": một {person_l} chọn ba {slot_sl} trong cùng {session_l} sẽ được đếm ở cả ba dòng, nhưng chỉ nhận được một chỗ.",
      clb_empty: "Chưa có {slot_l} nào.",
      clb_ds_tieu_de: "Thành viên {ten}",
      btn_xem_danh_sach: "Xem danh sách",
      btn_dong_danh_sach: "Đóng danh sách",
      th_so_dang_ky: "Số {person_l} đăng ký",
      th_dat_nv1: "Đặt nguyện vọng 1",
      th_da_xep: "Đã xếp",
      du_tru_title: "Suất dự trữ đã dùng",
      du_tru_desc: "Suất dự trữ không ai dùng sẽ thành suất thường, và phần ưu tiên dành cho nhóm đó không còn tác dụng.",
      du_tru_khong_co: "Chưa {slot_l} nào đặt suất dự trữ.",
      th_nhom_dang_ky: "{person} thuộc nhóm đã đăng ký",
      th_da_dung: "Đã dùng",
      th_con_thua: "Còn thừa",
      nv_title: "Mức đáp ứng nguyện vọng",
      nv_donut_tam: "nguyện vọng 1",
      nv_desc: "Số {person_l} có chỗ chưa cho biết chỗ đó có đúng nguyện vọng hay không. Bảng này cho biết điều đó.",
      nv_hang: "Nguyện vọng {n}",
      nv_hang_gop: "Nguyện vọng {n} trở lên",
      nv_khong_ro: "Không rõ thứ hạng",
      chua_co_cho_title: "{person} chưa có {slot_sl} nào",
      chua_co_cho_desc: "{person} chỉ chọn một {slot_sl} đông người và {person_l} chọn nhiều {slot_sl} nhưng vẫn chưa có chỗ là hai trường hợp khác nhau, cần cách xử lý khác nhau.",
      chua_co_cho_khong_ai: "Mọi {person_l} đều có ít nhất một {slot_sl}.",
      th_so_nguyen_vong: "Số nguyện vọng",
      th_da_khai: "Các {slot_sl} đã chọn",
      chua_khai_gi: "Chưa chọn nguyện vọng nào",
      dem_suat: "{n} suất chưa dùng",
      dem_cho: "{n} chỗ đã xếp",
      fill_panel_title: "Mức lấp đầy của từng {slot_sl}",
      tom_tat_title: "Tóm tắt lần xếp",
      tom_tat_lan_chay: "Lần chạy gần nhất: {luc} · số khởi tạo {seed}",
      kpi_da_xep: "{person} đã có chỗ",
      kpi_da_xep_phu: "{p}% {person_l}",
      kpi_nv1: "Được nguyện vọng 1",
      kpi_nv1_phu: "{p}% trong 3 nguyện vọng đầu",
      kpi_cho_trong: "Chỗ còn trống",
      kpi_cho_trong_phu: "trên tổng {n} chỗ",
      kpi_chua_co_cho: "{person} chưa có chỗ nào",
      kpi_du_tru_thua: "Suất dự trữ bỏ phí",
      kpi_du_tru_thua_phu: "Chính sách ưu tiên chưa dùng hết",
      kpi_can_xu_ly: "Cần xử lý",
      kpi_on: "Ổn",
      kpi_bam_de_xem: "Bấm để mở mục chi tiết",
      fill_hint: "Rê chuột (hoặc dùng bàn phím di tới) một dòng để xem chi tiết. Nhãn bên phải chỉ ra {slot_sl} cần để ý.",
      fill_sap_xep_nhan: "Sắp xếp",
      fill_sap_xep_buoi: "Theo {session_l}",
      fill_sap_xep_day: "Đầy nhất",
      fill_sap_xep_vang: "Vắng nhất",
      fill_sap_xep_choi: "Chọi cao nhất",
      fill_nhom_tong: "{xep}/{cho} chỗ · {p}%",
      fill_choi: "chọi {x}×",
      fill_tag_khong_ai: "Không ai",
      fill_tag_con_nhieu: "Còn nhiều chỗ",
      legend_trong: "Còn trống",
      tt_da_xep: "Đã xếp",
      tt_so_cho: "Số chỗ",
      tt_so_em: "Số {person_l}",
      tt_ti_le: "Tỉ lệ",
      tt_luy_ke: "Cộng dồn tới đây",
      nv_tieu_diem: "{p1}% chỗ đã xếp là nguyện vọng 1 · {p3}% nằm trong 3 nguyện vọng đầu",
      legend_general: "Suất thường",
      legend_reserve: "Vào bằng suất dự trữ",
      results_list_title: "Danh sách xếp {slot_sl}",
      placeholder_results_search: "Tìm theo mã hoặc tên {person_l}…",
      ket_qua_cu_banner: "Dữ liệu đã được sửa sau lần chạy gần nhất, nên kết quả bên dưới có thể đã cũ. Hãy chạy lại ở thẻ \"Vận hành sắp xếp\" trước khi xuất hoặc công bố.",
      xuat_title: "Xuất dữ liệu",
      xuat_opt_ket_qua: "Kết quả sắp xếp: một tệp Excel (danh sách {person_l}, từng {slot_sl}, {person_l} chưa có chỗ, thống kê)",
      xuat_opt_kem_csv: "Kèm các tệp CSV rời (chỉ cần khi đổ số liệu vào phần mềm khác)",
      xuat_opt_dau_vao: "Dữ liệu đầu vào hiện tại: một Sổ nhập CLB nạp lại được",
      xuat_opt_thay_doi: "Thay đổi so với lần chạy trước",
      xuat_thay_doi_dem: "({n} thay đổi)",
      xuat_thay_doi_chua_co: "(chưa có lần chạy trước để so sánh)",
      btn_xuat_tuy_chon: "Xuất các mục đã chọn",
      xuat_hint_hoc_sinh: "Hồ sơ {person_l}: bấm \"Chọn {person_l}…\" rồi đánh dấu {person_l} ở bảng bên dưới. Đang mở một {person_l} ở thẻ 03 thì bấm \"Xuất CSV {person_l} này\" ngay tại đó.",
      xuat_opt_hoc_sinh: "Hồ sơ {person_l} đã chọn",
      xuat_hoc_sinh_dem: "({n} {person_l})",
      xuat_hoc_sinh_chua_chon: "(chưa chọn {person_l} nào)",
      btn_chon_hoc_sinh: "Chọn {person_l}…",
      hien_ca_em_chua_xep: "Hiện cả {person_l} chưa được xếp",
      ca_tuan: "Cả tuần",
      btn_di_toi_chay: "Đi tới Vận hành sắp xếp",
      btn_mo_thu_muc: "Mở thư mục",
      btn_xuat_em_nay: "Xuất CSV {person_l} này",
      fallback_xuat_chua_luu: "{person} này còn thay đổi chưa lưu. Bấm Lưu trước rồi hãy xuất.",
      fallback_chua_luu: "• Chưa lưu",
      fallback_chua_luu_canh_bao: "{person} {student_id} còn thay đổi chưa lưu. Bấm Lưu, hoặc bấm lại để bỏ thay đổi.",
      admin_dem_danh_dau: "Đã đánh dấu {n} {person_l}",
      xuat_canh_bao_diem: "Tệp xuất có {score_l} chấm và số bốc thăm. Không gửi các tệp này cho giáo viên chấm {score_l}.",
      btn_xuat_hs_da_chon: "Xuất CSV {person_l} đã chọn",
      btn_bo_chon_hs: "Bỏ chọn",
      btn_admin_xuat_hs: "Xuất CSV {person_l} đã đánh dấu",
      aria_chon_tat_ca_dang_hien: "Chọn tất cả {person_l} đang hiện",
      aria_chon_tat_ca_trang: "Chọn tất cả {person_l} trên trang này",
      hs_da_chon_dem: "Đã chọn {n} {person_l}",
      hs_chua_chon: "Chưa chọn {person_l} nào. Đánh dấu ở cột đầu bảng.",
      toast_xuat_chua_chon_muc: "Chưa chọn mục nào để xuất.",
      xuat_kq_dau_vao: "Dữ liệu đầu vào (Sổ nhập CLB) → {path}",
      xuat_kq_dau_vao_thieu: "  {n} lượt thi là {slot_sl} {person_l} không xếp nguyện vọng nên không có trong sổ (không ảnh hưởng kết quả).",
      xuat_kq_thay_doi: "Thay đổi so với lần trước: {n} dòng → {path}",
      xuat_kq_hoc_sinh: "Hồ sơ {n} {person_l} ({n_dong} dòng) → {path}",
      xuat_kq_loi: "Không xuất được {muc}: {errors}",
      xuat_kq_cu: "Lưu ý: dữ liệu đã sửa sau lần chạy gần nhất, nên kết quả trong tệp có thể đã cũ.",
      xuat_muc_ket_qua: "kết quả",
      xuat_muc_dau_vao: "dữ liệu đầu vào",
      xuat_muc_thay_doi: "thay đổi",
      xuat_muc_hoc_sinh: "hồ sơ {person_l}",
      xuat_bo_hs_khong_con: "Đã bỏ khỏi danh sách chọn những {person_l} không còn trong hệ thống: {ds}. Bấm Xuất lại để xuất những {person_l} còn lại.",
      th_student_id: "Mã {person_l}",
      th_name: "Họ tên",
      th_club: "{slot}",
      th_tier: "Loại chỗ",
      th_pref_rank: "Hạng nguyện vọng",
      results_empty_state: "Chưa có kết quả. Hãy chạy sắp xếp ở thẻ \"Vận hành sắp xếp\" trước.",
      not_matched_label: "Không xếp được",
      unmatched_badge: "{n} {person_l} chưa có {slot_sl}",
      tier_general: "Tổng quát",
      tier_reserve: "Dự trữ",

      fallback_title: "Nhập tại chỗ",
      fallback_desc: "Tìm hoặc tạo {person_l}, rồi làm hai bước: chọn {slot_sl} dự thi và xếp hạng nguyện vọng. Hai bước này không phụ thuộc nhau.",
      fallback_step0_title: "Tìm hoặc tạo {person_l}",
      placeholder_fallback_search: "Nhập mã {person_l} hoặc tên…",
      btn_search: "Tìm",
      placeholder_new_student_id: "Mã {person_l} mới",
      placeholder_full_name: "Họ tên",
      btn_create_student: "Tạo {person_l} mới",
      btn_reset_entry: "Sửa lại từ đầu",
      confirm_reset_entry: "Bấm lần nữa để xoá hết, kể cả {score_l} đã chấm, và nhập lại",
      btn_delete_student: "Xoá {person_l}",
      confirm_delete_student: "Bấm lần nữa để xoá {person_l}",
      fallback_step1_title: "Bước 1. Chọn {slot_sl} dự thi",
      fallback_step1_hint: "Mỗi {session_l} chọn tối đa {max_tests} {slot_sl}. Bỏ chọn một {slot_sl} đã chấm {score_l} thì {score_l} đó bị xoá khi bấm Lưu.",
      fallback_step1_hint_khong_gioi_han: "Mỗi {session_l} chọn bao nhiêu {slot_sl} dự thi cũng được. Bỏ chọn một {slot_sl} đã chấm {score_l} thì {score_l} đó bị xoá khi bấm Lưu.",
      btn_save_test_selection: "Lưu {slot_sl} dự thi",
      fallback_step2_title: "Bước 2. Xếp hạng nguyện vọng",
      fallback_step2_hint: "Bấm vào {slot_sl} theo thứ tự muốn vào nhất trước, mỗi {session_l} tối đa {max_choices} {slot_sl}. Có thể chọn cả {slot_sl} không có ở Bước 1.",
      ranking_current_label: "Thứ tự nguyện vọng",
      btn_clear_all: "Xoá hết",
      btn_save_preferences: "Lưu nguyện vọng",
      fallback_step3_title: "Bước 3. Điểm quyết tâm",
      fallback_step3_hint: "Chia đúng 100 điểm cho các {slot_sl} đã thi và đúng 100 điểm cho các {slot_sl} không thi, ở mỗi {session_l}. Ô để trống tính là 0 điểm.",
      wharton_khung_thi: "Các {slot_sl} đã thi",
      wharton_khung_thi_ghi_chu: "Điểm này chỉ dùng khi hai {person_l} bằng {score_l} thi.",
      wharton_khung_khong_thi: "Các {slot_sl} không thi",
      wharton_khung_khong_thi_ghi_chu: "Điểm càng cao thì {person_l} càng được xếp trước các {person_l} khác cũng không thi {slot_sl} này.",
      wharton_da_dung: "Đã dùng {x} / {tong}",
      wharton_can_chia_lai: "Cần chia lại điểm.",
      btn_save_wharton: "Lưu điểm quyết tâm",
      feedback_wharton_saved: "Đã lưu điểm quyết tâm.",
      wharton_da_khoa_kiosk: "Điểm quyết tâm đang khoá vì đã chạy xếp. Nhờ người quản lý mở khoá ở thẻ Quản lý nếu cần sửa.",
      /* Khối "Điểm quyết tâm" ở thẻ Quản lý (A13.3). */
      wh_ql_title: "Điểm quyết tâm",
      wh_ql_desc: "Xem, sửa và xoá điểm quyết tâm mà từng {person_l} đã chia. Sau khi chạy xếp, điểm được khoá để kết quả không đổi âm thầm.",
      wh_ql_dang_khoa: "Đang khoá từ {luc}",
      wh_ql_dang_mo: "Đang mở, có thể sửa điểm",
      btn_wh_mo_khoa: "Mở khoá sửa điểm quyết tâm",
      wh_mo_khoa_hoi: "Mở khoá để sửa điểm. Kết quả đã xếp không tự đổi, lần chạy xếp tiếp theo sẽ khoá lại. Gõ {can_go} để xác nhận.",
      btn_wh_mo_khoa_xn: "Xác nhận mở khoá",
      aria_wh_go_mo_khoa: "Gõ chữ xác nhận để mở khoá",
      aria_wh_go_xoa: "Gõ chữ xác nhận để xoá",
      wh_canh_bao_title: "Hồ sơ cần xử lý",
      wh_cb_chua_hop_le: "Chưa chia đủ",
      wh_cb_vang_thi: "Vắng thi",
      wh_cb_rong: "Không có hồ sơ nào cần xử lý.",
      wh_tim_placeholder: "Tìm {person_l} theo mã hoặc tên…",
      wh_loc_quy: "Quỹ",
      wh_loc_buoi: "{session}",
      wh_loc_clb: "{slot}",
      wh_loc_tat_ca: "Tất cả",
      wh_quy_1: "Quỹ 1, đã thi",
      wh_quy_2: "Quỹ 2, không thi",
      wh_quy_ngan: "Quỹ {q}",
      wh_loc_chi_loi: "Chỉ hồ sơ có vấn đề",
      th_wh_diem: "Điểm đã chia",
      th_wh_tt: "Tình trạng",
      wh_tong: "Tổng {x}",
      wh_o_tu_dien: "tự điền",
      wh_tt_ok: "Hợp lệ",
      wh_tt_loi: "Chưa hợp lệ",
      wh_tt_vang: "Vắng thi",
      wh_tt_lech: "Cần chia lại",
      wh_bang_rong: "Không có hồ sơ nào khớp.",
      wh_sua_title: "Sửa điểm của {name}",
      wh_sua_dong: "Đóng",
      wh_sua_khoa: "Điểm đang khoá nên chỉ xem được. Mở khoá ở đầu khối này để sửa.",
      wh_sua_rong: "{person_l} này chưa có nguyện vọng nên chưa có gì để chia.",
      btn_wh_xoa_mot: "Xoá điểm của {person_l} này",
      confirm_wh_xoa_mot: "Bấm lần nữa để xoá điểm",
      toast_wh_xoa_mot: "Đã xoá điểm quyết tâm của {student_id}.",
      wh_nhat_ky_title: "Nhật ký thay đổi",
      wh_nhat_ky_rong: "Chưa có thay đổi nào.",
      btn_wh_xem_them: "Xem thêm",
      wh_nk_quan_ly: "thẻ Quản lý",
      wh_nk_kiosk: "nhập tại chỗ",
      wh_nk_nap_tep: "nạp tệp",
      wh_nk_xoa_du_lieu: "xoá dữ liệu",
      wh_nk_he_thong: "hệ thống",
      wh_nk_luu: "lưu điểm",
      wh_nk_xoa_mot_em: "xoá điểm",
      wh_nk_xoa_tat_ca: "xoá điểm của tất cả",
      wh_nk_tia_nguyen_vong: "bỏ điểm của mục bị gỡ khỏi nguyện vọng",
      wh_nk_xoa_theo_clb: "xoá điểm do xoá {slot_l}",
      wh_nk_khoa: "khoá điểm",
      wh_nk_mo_khoa: "mở khoá điểm",
      wh_nk_dong: "{luc}, {nguon}{nguoi}: {hanh_dong}",
      btn_wh_xoa_tat_ca: "Xoá điểm quyết tâm của tất cả {person_l}",
      wh_xoa_tat_ca_hoi: "Xoá điểm quyết tâm của tất cả {person_l}. Dữ liệu được sao lưu trước khi xoá. Gõ {can_go} để xác nhận.",
      btn_wh_xoa_tat_ca_xn: "Xác nhận xoá",
      btn_remove_ranked: "xoá",
      search_no_students_found: "Không tìm thấy {person_l} nào.",
      hs_nhan_clb_thi: "{slot_s} dự thi",
      hs_nhan_nguyen_vong: "Nguyện vọng",
      hs_the_chua_chon: "Chưa chọn",
      hs_trang_thai_du: "Đã nhập đủ",
      hs_trang_thai_thieu_thi: "Thiếu {slot_sl} dự thi",
      hs_trang_thai_thieu_nv: "Thiếu nguyện vọng",
      hs_trang_thai_trong: "Chưa nhập gì",
      toast_need_id_and_name: "Cần nhập cả mã {person_l} và họ tên.",
      toast_student_created: "Đã tạo {person_l} mới.",
      toast_student_exists: "{person} này đã có sẵn. Đang mở thông tin.",
      feedback_test_selection_saved: "Đã lưu {n} {slot_sl} dự thi.",
      feedback_test_selection_saved_removed: "Đã lưu {n} {slot_sl} dự thi và xoá {m} {score_l} của {slot_sl} bỏ chọn.",
      feedback_preferences_saved: "Đã lưu {n} nguyện vọng.",
      toast_reset_done: "Đã xoá {slot_sl} dự thi và nguyện vọng. Có thể nhập lại.",
      toast_reset_done_removed: "Đã xoá {slot_sl} dự thi, nguyện vọng và {m} {score_l} đã chấm. Có thể nhập lại.",
      toast_student_deleted: "Đã xoá {person_l} {student_id}.",

      admin_title: "Quản lý {slot_sl} & dự trữ",
      admin_desc: "Thêm, sửa {slot_sl} và gán nhãn dự trữ cho {person_l}. Trường tự quyết định ai được dự trữ. Phần mềm chỉ ghép {person_l} và {slot_sl} có cùng nhãn.",
      admin_club_form_title: "Thêm hoặc sửa {slot_sl}",
      placeholder_club_id: "Mã {slot_sl} (ví dụ: clb_01)",
      placeholder_club_name: "Tên {slot_sl}",
      placeholder_capacity: "Tổng chỗ",
      placeholder_reserve_capacity: "Suất dự trữ",
      placeholder_reserve_group: "Nhãn dự trữ (để trống nếu không có)",
      btn_save_club: "Lưu {slot_sl}",
      th_club_id: "Mã {slot_sl}",
      th_name_short: "Tên",
      th_capacity: "Tổng chỗ",
      th_reserve_capacity: "Suất dự trữ",
      th_reserve_group: "Nhãn dự trữ",
      admin_club_empty: "Chưa có {slot_sl} nào. Thêm {slot_sl} đầu tiên bằng biểu mẫu ở trên.",
      admin_reserve_assign_title: "Gán nhãn dự trữ và xuất hồ sơ {person_l}",
      placeholder_admin_student_search: "Tìm {person_l} theo mã hoặc tên…",
      placeholder_reserve_group_apply: "Nhãn dự trữ cần gán",
      btn_bulk_assign: "Gán cho {person_l} đã đánh dấu",
      th_current_reserve_group: "Nhãn dự trữ hiện tại",
      admin_student_empty: "Chưa có {person_l} nào. Thêm ở thẻ \"Nhập tại chỗ\" hoặc nạp tệp từ Microsoft Forms.",
      btn_prev_page: "‹ Trước",
      btn_next_page: "Sau ›",
      pagination_label: "Trang {page}/{total_pages} · {total} {person_l}",
      btn_delete: "Xoá",
      confirm_delete_generic: "Bấm lần nữa để xoá",
      toast_club_deleted: "Đã xoá {slot_sl} {club_id}.",

      danger_zone_title: "Vùng nguy hiểm: xoá dữ liệu để làm lại",
      danger_zone_desc: "Nạp tệp chỉ thêm {person_l} mới, không xoá {person_l} cũ. Muốn làm lại với bộ dữ liệu khác, hãy xoá ở đây trước, nếu không {person_l} cũ vẫn chiếm chỗ.",
      danger_zone_safety: "Cả hai nút đều tự sao lưu dữ liệu trước khi xoá. Lịch sử các lần sắp xếp được giữ lại.",
      btn_reset_students: "Xoá toàn bộ {person_l} (giữ {slot_sl})",
      btn_reset_all: "Xoá toàn bộ dữ liệu (cả {slot_sl})",
      confirm_reset_students: "Bấm lần nữa để xoá tất cả {person_l}",
      confirm_reset_all: "Bấm lần nữa để xoá tất cả dữ liệu",
      confirm_reset_students_has_results: "Bấm lần nữa. Kết quả đã sắp xếp cũng sẽ bị xoá",
      confirm_reset_all_has_results: "Bấm lần nữa. {slot_s} và kết quả đã sắp xếp cũng sẽ bị xoá",
      toast_reset_students_done: "Đã xoá {n_students} {person_l}, giữ lại {n_clubs_left} {slot_sl}. Bản sao lưu: {backup_name}",
      toast_reset_all_done: "Đã xoá {n_students} {person_l} và {n_clubs} {slot_sl}. Bản sao lưu: {backup_name}",
      toast_reset_blocked_busy: "Đang nhập tệp hoặc đang sắp xếp. Chờ xong rồi hãy xoá dữ liệu.",
      feedback_club_form_required: "Hãy nhập mã {slot_sl}, tên và tổng chỗ.",
      feedback_club_saved: "Đã lưu {slot_sl} {club_id}.",
      toast_no_students_ticked: "Chưa đánh dấu {person_l} nào.",
      toast_bulk_assign_success: "Đã gán cho {n} {person_l}.",

      scoring_title: "Nhập {score_l}",
      scoring_desc: "Chọn {slot_sl} để chấm. Danh sách chỉ có mã và họ tên, không có số bốc thăm hay thứ hạng nguyện vọng, để việc chấm {score_l} được khách quan.",
      scoring_desc_person: "Nhập một {score_l} cho mỗi {person_l}. Danh sách chỉ có mã và họ tên, không có số bốc thăm hay thứ hạng nguyện vọng, để việc chấm {score_l} được khách quan.",
      scoring_person_title: "{score} của từng {person_l}",
      scoring_person_progress: "Đã chấm {n_scored}/{n}",
      scoring_person_empty: "Chưa có {person_l} nào để chấm. Hãy nạp danh sách trước.",
      scoring_overview_title: "Tiến độ chấm của từng {slot_sl}",
      th_n_applicants: "Đã đăng ký",
      th_n_scored: "Đã chấm",
      scoring_overview_empty: "Chưa {slot_sl} nào có {person_l} đăng ký dự thi.",
      btn_save_scores: "Lưu {score_l}",
      th_score: "{score}",
      btn_score_link: "Chấm →",
      feedback_scores_saved: "Đã lưu {score_l} cho {n} {person_l}.",
      feedback_scores_saved_mot_phan: "Đã lưu {score_l} cho {n} {person_l}, {k} ô không hợp lệ nên chưa lưu (đã tô đỏ).",

      stb_locked_label: "Số bốc thăm đã khoá từ {locked_at}. Các lần sắp xếp sau giữ nguyên thứ tự cũ, {person_l} mới được xếp ngẫu nhiên vào.",
      stb_unlocked_label: "Chưa bốc thăm lần nào. Lần sắp xếp đầu tiên sẽ bốc thăm và tự khoá kết quả.",
      btn_redraw_stb: "Bốc thăm lại…",
      toast_redraw_armed: "Bấm \"Chạy sắp xếp\" để bốc thăm lại. Sẽ có thêm một bước xác nhận trước khi chạy.",
      health_panel_title: "Cảnh báo dữ liệu",
      health_panel_hint: "Những điểm dưới đây không chặn việc sắp xếp nhưng có thể làm kết quả sai lệch. Nên xem trước khi chạy.",
      health_clean: "Không thấy vấn đề nào. Dữ liệu đã sẵn sàng.",
      health_summary: "{n} cảnh báo, {n_high} cảnh báo nghiêm trọng.",
      health_sev_high: "Nghiêm trọng",
      health_sev_medium: "Cần lưu ý",
      health_sev_info: "Thông tin",
      btn_health_recheck: "Kiểm tra lại",
      toast_data_valid: "Dữ liệu hợp lệ: {n_students} {person_l}, {n_clubs} {slot_sl}.",
      toast_hop_le_con_canh_bao: "Nhưng còn {n_high} cảnh báo nghiêm trọng. Xem mục Cảnh báo dữ liệu trước khi chạy.",
      toast_data_invalid: "Dữ liệu có lỗi. Xem danh sách lỗi bên dưới.",
      confirm_redraw_run: "Bốc thăm lại toàn bộ và sắp xếp lại? Kết quả hiện tại sẽ bị thay thế.",
      confirm_overwrite_run: "Đã có kết quả cũ. Sắp xếp lại sẽ thay kết quả này, bản cũ vẫn được lưu trong lịch sử. Tiếp tục?",
      confirm_overwrite_mot_phan: "Sắp xếp lại {buoi} và thay kết quả cũ của các {session_l} đó. Các {session_l} khác giữ nguyên. Tiếp tục?",
      btn_confirm_run: "Chạy",
      btn_cancel: "Huỷ",
      toast_run_success: "Sắp xếp xong: {n_matched}/{n_total} {person_l} có {slot_sl}, sau {rounds} vòng.",
      toast_run_failed: "Sắp xếp không thành công. Xem danh sách lỗi bên dưới.",
      feedback_no_file_selected: "Chưa chọn tệp.",
      toast_export_success: "Đã xuất kết quả của {n_hoc_sinh} {person_l} ra một tệp Excel: {path}\nGồm {n_trang} trang: {trang}.",
      xuat_kq_kem_csv: "Kèm các tệp CSV rời: {path} và {n_club_files} tệp theo từng {slot_sl}.",
      xuat_kq_csv_loi: "Tệp Excel đã ghi xong, nhưng không ghi được các tệp CSV rời: {errors}",

      recovery_title: "Phục hồi dữ liệu",
      recovery_heading: "Không mở được dữ liệu",
      recovery_intro: "Chương trình không khởi động được vì tệp dữ liệu bị lỗi. Dữ liệu có thể vẫn còn. Hãy thử các bước bên dưới trước khi nhờ hỗ trợ.",
      recovery_error_detail_label: "Chi tiết kỹ thuật (gửi cho người hỗ trợ nếu cần)",
      recovery_backups_label: "Các bản sao lưu tìm thấy trên máy này:",
      th_backup_name: "Tên tệp",
      th_backup_time: "Thời điểm sao lưu",
      th_backup_size: "Dung lượng",
      btn_restore_backup: "Khôi phục từ bản sao lưu gần nhất",
      btn_start_fresh: "Bắt đầu với dữ liệu trống",
      confirm_start_fresh: "Bấm lần nữa để xác nhận. Tệp lỗi sẽ được đổi tên, không bị xoá",
      recovery_working: "Đang xử lý…",
      recovery_please_restart: "Hãy đóng và mở lại chương trình để tiếp tục.",
      recovery_kg_heading: "Chương trình không lưu được dữ liệu vào thư mục này",
      recovery_kg_intro: "Dữ liệu không hỏng. Vấn đề là Windows không cho chương trình tạo tệp trong thư mục đang chứa nó.",
      recovery_kg_thu_muc: "Thư mục của chương trình:",
      recovery_kg_vi_sao: "Thường do một trong ba điều: thư mục nằm trong Documents/Desktop và Windows đang bật \"Quyền truy cập thư mục được kiểm soát\" (chống mã độc tống tiền); thư mục nằm trong OneDrive đang đồng bộ; hoặc thư mục nằm trong Program Files.",
      recovery_kg_cach_tieu_de: "Cách sửa, chỉ cần làm một trong hai cách:",
      recovery_kg_cach_1: "Đóng chương trình. Chuyển cả thư mục chương trình sang một chỗ đơn giản, ví dụ C:\\RBDA (tạo thư mục này ngay trong ổ C:, không đặt trong Documents, Desktop hay OneDrive). Rồi mở lại PhanBoCauLacBo.exe.",
      recovery_kg_cach_2: "Hoặc giữ nguyên chỗ cũ và cho phép chương trình: Bảo mật Windows → Bảo vệ khỏi vi-rút và mối đe doạ → Bảo vệ khỏi mã độc tống tiền → Quyền truy cập thư mục được kiểm soát → Cho phép ứng dụng → thêm PhanBoCauLacBo.exe. Rồi mở lại chương trình.",
      recovery_kg_khong_mat: "Dữ liệu cũ (nếu có) không bị mất. Không cần bấm khôi phục hay bắt đầu lại.",
      btn_kiem_lai_thu_muc: "Kiểm tra lại",
      recovery_kg_van_chua: "Vẫn chưa ghi được vào thư mục này. Hãy làm một trong hai cách ở trên.",
      recovery_kg_da_duoc: "Đã ghi được vào thư mục. Hãy đóng rồi mở lại chương trình.",

      /* --- Nhiều buổi sinh hoạt trong tuần --- */
      buoi_chua_chia: "Chưa chia {session_l}",
      th_buoi: "{session}",
      placeholder_buoi: "{session} sinh hoạt (ví dụ: thu_3)",
      buoi_hint_form: "Hai {slot_sl} cùng {session_l} là trùng giờ, mỗi {person_l} chỉ vào được một. Để trống nếu trường chỉ có một {session_l}.",
      admin_lich_tuan_title: "Lịch tuần",
      admin_lich_tuan_desc: "Mỗi cột là một {session_l}. Thanh dưới mỗi {slot_sl} là mức lấp đầy của lần sắp xếp gần nhất.",
      admin_tai_buoi_title: "Tải theo {session_l}",
      admin_tai_buoi_desc: "Nên xem trước khi sắp xếp. Nếu một {session_l} quá đông trong khi {session_l} khác còn chỗ, hãy chuyển bớt {slot_sl} sang {session_l} vắng hơn.",
      th_so_clb: "Số {slot_sl}",
      th_tong_cho: "Tổng chỗ",
      th_em_muon_buoi: "{person} chọn {session_l} này",
      th_ti_le_choi: "Tỉ lệ chọi",
      ti_le_choi_giai_thich: "Tỉ lệ chọi tính theo số {person_l}, không theo số nguyện vọng, vì mỗi {person_l} chỉ nhận một chỗ mỗi {session_l}.",
      tai_buoi_qua_tai: "Quá tải",
      tai_buoi_vua_du: "Vừa đủ",
      tai_buoi_con_trong: "Còn trống",
      tai_buoi_empty: "Chưa có {slot_sl} nào để tính tải.",
      chon_buoi_title: "{session} sẽ xếp",
      chon_buoi_tu: "Từ",
      chon_buoi_den: "đến",
      chon_buoi_tat_ca: "Chọn tất cả",
      chon_buoi_nhac_giu: "Giữ nguyên kết quả của: {buoi}. Chỉ các {session_l} đang chọn được sắp xếp lại.",
      chon_buoi_nhac_het: "Sắp xếp lại tất cả các {session_l} trong tuần.",
      tham_title: "Số bốc thăm theo {session_l}",
      tham_desc: "Mỗi {session_l} có thứ tự riêng, được xáo từ bộ số đã khoá, nên không {person_l} nào bị xếp cuối ở mọi {session_l}.",
      tham_tai_lap: "Chỉ cần công bố bộ số đã khoá và số khởi tạo. Ai tính lại cũng ra đúng bảng này.",
      tham_cach_cu: "Lần sắp xếp gần nhất dùng cách bốc thăm cũ, một thứ tự chung cho cả tuần, nên các cột bên dưới giống nhau. Chạy sắp xếp lại để mỗi {session_l} có thứ tự riêng.",
      results_xem_tkb: "Thời khoá biểu",
      results_xem_danh_sach: "Danh sách",
      tkb_title: "Thời khoá biểu tuần",
      tkb_desc: "Mỗi {person_l} một dòng, mỗi {session_l} một ô. Ô trống là {session_l} đó chưa có {slot_sl}.",
      tkb_so_clb: "Số {slot_sl}",
      do_phu_title: "Số {slot_sl} của mỗi {person_l}",
      do_phu_desc: "Con số quan trọng nhất là số {person_l} không có {slot_sl} nào trong cả tuần.",
      do_phu_tb: "{slot_s} trung bình mỗi {person_l}",
      do_phu_trang_tay: "{person} không có {slot_sl} nào cả tuần",
      do_phu_x_clb: "{n} {slot_sl}",
      do_phu_0_clb: "Không {slot_sl} nào",
      do_phu_1_clb: "1 {slot_sl}",
      do_phu_danh_sach: "{person} chưa có {slot_sl}",
      fallback_buoi_hint: "Mỗi {session_l} chỉ nhận được tối đa một {slot_sl}. Chọn {slot_sl} ở nhiều {session_l} để có lịch cả tuần.",
      fallback_phu_buoi: "Đã xếp hạng ở {n}/{tong} {session_l}",
      chi_tiet_ky_thuat: "Chi tiết kỹ thuật",
      btn_dong_thong_bao: "Đóng",
      ws_switcher_nhan: "Không gian làm việc",
      ws_switcher_aria: "Đổi không gian làm việc",
      ws_chon_title: "Chọn không gian làm việc",
      ws_chon_hint: "Mỗi không gian làm việc có dữ liệu và luật xếp riêng, nằm trong một thư mục riêng.",
      ws_rong: "Chưa có không gian làm việc nào. Hãy tạo mới hoặc nhập từ tệp nén.",
      ws_dang_mo_nhan: "Đang mở",
      ws_cot_ten: "Tên",
      ws_cot_loai: "Loại",
      ws_cot_sua: "Sửa lần cuối",
      ws_loai_school: "Trường học",
      ws_loai_company: "Công ty",
      ws_loai_event: "Sự kiện",
      ws_loai_custom: "Tuỳ chỉnh",
      ws_mau_truong_hoc: "Trường học",
      ws_btn_mo: "Mở",
      ws_btn_doi_ten: "Đổi tên",
      ws_btn_nhan_ban: "Nhân bản",
      ws_btn_luu_mau: "Lưu thành mẫu",
      ws_btn_xuat: "Xuất tệp nén",
      ws_btn_xoa: "Xoá",
      ws_btn_xoa_xn: "Bấm lần nữa để xoá",
      ws_btn_moi: "Tạo mới",
      ws_btn_nhap_zip: "Nhập tệp nén",
      ws_btn_dong: "Đóng",
      ws_btn_luu: "Lưu",
      ws_btn_tiep: "Tiếp",
      ws_btn_quay_lai: "Quay lại",
      ws_btn_tao: "Tạo không gian làm việc",
      ws_ten_moi: "Tên mới",
      ws_ten_mau: "Tên mẫu",
      ws_nhan_ban_ten_mac_dinh: "{ten} (bản sao)",
      ws_nhan_ban_kem: "Kèm dữ liệu",
      ws_khong_xoa_dang_mo: "Đang mở không gian làm việc này nên chưa xoá được. Hãy mở không gian làm việc khác trước.",
      ws_chi_nhan_zip: "Chỉ nhận tệp nén do chương trình này xuất ra.",
      ws_da_mo: "Đã mở không gian làm việc \"{ten}\".",
      ws_da_tao: "Đã tạo không gian làm việc \"{ten}\".",
      ws_da_doi_ten: "Đã đổi tên thành \"{ten}\".",
      ws_da_nhan_ban: "Đã nhân bản thành \"{ten}\".",
      ws_da_luu_mau: "Đã lưu mẫu \"{ten}\".",
      ws_da_xuat: "Đã xuất không gian làm việc: {path}",
      ws_da_xoa: "Đã chuyển không gian làm việc \"{ten}\" vào thùng rác (thư mục _trash), chưa xoá vĩnh viễn.",
      ws_da_nhap: "Đã nhập không gian làm việc \"{ten}\".",
      ws_wz_title: "Tạo không gian làm việc mới",
      ws_wz_buoc: "Bước {n}/{tong}",
      ws_wz_b1: "Thông tin chung",
      ws_wz_b2: "Từ vựng",
      ws_wz_b3: "Luật xếp",
      ws_wz_b4: "Xem lại",
      ws_wz_ten: "Tên không gian làm việc",
      ws_wz_ten_ph: "Ví dụ: Trường Trung học A, năm học 2026",
      ws_wz_loai: "Loại",
      ws_wz_mau: "Bắt đầu từ mẫu",
      ws_wz_mau_hint: "Chọn mẫu sẽ điền sẵn cả bốn bước, và vẫn sửa được từng ô.",
      ws_wz_tu_vung_hint: "Đặt tên gọi cho năm khái niệm của không gian làm việc này. Ô tiếng Anh để trống thì dùng tiếng Việt.",
      ws_wz_vi: "Tiếng Việt",
      ws_wz_en: "Tiếng Anh",
      ws_wz_en_ph: "Để trống = dùng tiếng Việt",
      ws_wz_xem_lai_hint: "Kiểm tra lần cuối. Bấm Quay lại để sửa; bấm Tạo không gian làm việc để dựng và mở nó.",
      ws_dt_person: "Người tham gia",
      ws_dt_person_mo_ta: "Người được xếp vào chỗ (vd. học sinh, nhân viên).",
      ws_dt_slot: "Chỗ được xếp",
      ws_dt_slot_mo_ta: "Nơi người tham gia được xếp vào (vd. câu lạc bộ, dự án, phòng).",
      ws_dt_session: "Đợt",
      ws_dt_session_mo_ta: "Mỗi người nhận tối đa một chỗ trong mỗi đợt (vd. buổi, ca, đợt).",
      ws_dt_group: "Nhóm ưu tiên",
      ws_dt_group_mo_ta: "Nhóm của người tham gia được ưu tiên khi xếp (vd. khối, chính sách, cấp bậc).",
      ws_dt_score: "Điểm",
      ws_dt_score_mo_ta: "Con số dùng để xếp hạng người tham gia (vd. điểm thi tuyển).",
      ws_r_max_choices: "Số lựa chọn tối đa mỗi đợt (1–20)",
      ws_r_max_tests: "Số mục dự thi tối đa mỗi đợt (0–20)",
      ws_r_khong_gioi_han: "Không giới hạn",
      ws_r_priority: "Cách xếp ưu tiên",
      ws_r_priority_score: "Theo điểm",
      ws_r_priority_tier: "Chỉ theo nhóm (không chấm điểm)",
      ws_r_priority_both: "Nhóm trước, rồi đến điểm",
      ws_r_tier_mode: "Cách dùng nhóm ưu tiên",
      ws_r_tm_reserve: "Suất dự trữ mềm (như trường học)",
      ws_r_tm_strict: "Thứ hạng nhóm nghiêm ngặt",
      ws_r_score_scope: "Phạm vi của điểm",
      ws_r_ss_per_slot: "Mỗi chỗ một điểm riêng (như trường học)",
      ws_r_ss_per_person: "Mỗi người một điểm duy nhất",
      ws_r_wharton: "Dùng điểm quyết tâm",
      ws_r_wharton_ghi_chu: "Mỗi người tự chia 100 điểm cho các mục đã thi và 100 điểm cho các mục không thi, ở mỗi đợt. Chỉ dùng được khi cách xếp ưu tiên có điểm và điểm tính riêng cho từng chỗ.",
      ws_r_wharton_bat: "Bật",
      ws_r_wharton_tat: "Tắt",
      ws_r_tiers: "Thứ tự các nhóm: tốt nhất ở trên cùng, mỗi dòng một nhóm",
      ws_r_tiers_ph: "Khối 12\nKhối 11\nKhối 10",
      ws_r_tiers_chi_strict: "Dùng khi chọn \"Thứ hạng nhóm nghiêm ngặt\" hoặc ưu tiên \"Chỉ theo nhóm\". Người không thuộc nhóm nào đứng sau cùng.",
      ws_r_canh_bao_nhom: "Lưu ý: ưu tiên \"Nhóm trước, rồi đến điểm\" nhưng chưa chọn \"Thứ hạng nhóm nghiêm ngặt\", nên thứ tự các nhóm sẽ không được dùng.",
      ws_v_ten: "Hãy nhập tên.",
      ws_v_vi: "Ô tiếng Việt của \"{muc}\" không được để trống.",
      ws_v_max_choices: "Số lựa chọn tối đa phải là số nguyên từ 1 đến 20.",
      ws_v_max_tests: "Số mục dự thi tối đa phải là số nguyên từ 0 đến 20, hoặc tích \"Không giới hạn\".",
      ws_v_tiers: "Danh sách nhóm có hai dòng trùng nhau.",
    },

    en: {
      th_muc: "Level",
      th_thao_tac: "Actions",
      th_chon: "Select",
      page_title: "{slot} Allocation · RB-DA",
      lang_toggle_label: "VI",
      brand_title: "{slot} Allocation",
      brand_sub: "Reserve-Based DA",
      nav_pipeline: "Allocation",
      nav_results: "Results",
      nav_fallback: "Kiosk entry",
      nav_admin: "{slot_p} & reserves",
      nav_scoring: "{score} entry",
      db_status_loading: "Loading…",
      db_connected: "Data connected",
      backend_dang_ket_noi: "Connecting to the application core…",
      api_chua_san_sang: "The program is not ready yet. Wait a few seconds and try again.",
      api_mat_ket_noi: "Could not reach the application core. Try again; if it keeps failing, close the window and reopen the program.",
      loi_giao_dien_ngoai_du_kien: "Something unexpected went wrong on screen. Try again. If it keeps happening, close and reopen the program.",
      backend_khong_ket_noi: "Data not connected yet",
      backend_qua_han: "The program didn't finish starting. Close the window and open it again. If that doesn't help, send the file loi_khoi_dong.txt (in the data folder) to the person in charge.",
      display_native: "Native application window",
      display_browser: "Fallback mode (browser)",
      last_run_line: "Last run: {run_at} (starting number {seed}, {n_matched}/{n_total} placed)",
      never_run: "No allocation has been run yet",

      pipeline_title: "Allocation",
      pipeline_desc: "Check the data, draw lottery numbers, place {person_pl} in {slot_pl}, and export the results.",
      label_students: "{person_pl}",
      label_clubs: "{slot_pl}",
      label_submitted_prefs: "submitted preferences",
      label_matched: "matched to {slot_la}",
      import_panel_title: "Import data",
      import_hint: "All input lives in a single Excel file: the Club Input Workbook. No workbook yet? Click \"Download the input workbook\", fill in the {slot_pl} and {person_pl}, save it, then drop it below.",
      drop_zone_main: "Drop the Club Input Workbook here",
      drop_zone_sub: "One Excel file (.xlsx). Click to choose it.",
      btn_import_all: "Import workbook",
      btn_clear_queue: "Remove file",
      btn_tai_so_mau: "Download the input workbook",
      so_mau_da_tao: "Input workbook created ({n} {slot_l}(s) filled in) → {path}",
      so_nhap_dang_doc: "Reading the workbook…",
      so_nhap_tom_tat: "Ready to import: {n_clb} {slot_l}(s) · {n_buoi} {session_l}(s) · {n_hoc_sinh} {person_l}(s) · {n_nguyen_vong} preference(s) · {n_thi} test entry(ies)",
      so_nhap_co_loi: "The workbook has {n} problem(s) to fix. Nothing was imported. Fix them in Excel, save, and drop the workbook again.",
      so_nhap_loi_con_lai: "… and {n} more.",
      so_nhap_xong: "Done: {n_clb} {slot_l}(s), {n_hoc_sinh} {person_l}(s) ({n_moi} new, {n_bo} skipped)",
      so_nhap_khong_nap: "The workbook couldn't be imported. See the reason below.",
      so_nhap_canh_bao_tieu_de: "Before importing:",
      xuat_kq_ten_doi: "  {n} {slot_l}(s) shared a name with another {slot_l}, so their code was added to the name in the workbook.",
      steps_panel_title: "Processing steps",
      label_seed: "Lottery starting number",
      seed_locked_hint: "Starting number {seed} is locked together with the lottery numbers. To change it, click \"Redraw lottery…\".",
      seed_unlocked_for_redraw: "Redraw armed: a new starting number can be entered before clicking \"Run allocation\".",
      btn_validate: "Validate data",
      btn_run_pipeline: "Run allocation",
      btn_dang_chay: "Running…",
      hat_giong_khong_hop_le: "The lottery starting number must be a whole number, for example 2026. Fix that box, then run again.",
      btn_dong: "Close message",
      step_title_backup: "Back up data",
      step_title_rollback: "Undo",
      step_title_unknown: "Unexpected error",
      toast_run_success_no_backup: "Note: the data could not be backed up before this run.",
      step_title_validate: "Check data",
      step_title_stb: "Draw lottery numbers",
      step_title_rbda: "Place {person_pl} in {slot_pl}",
      step_title_write: "Save results",
      step_title_export: "Export results",
      step_not_run_yet: "Not run yet",
      step_running: "Running…",
      step_done_default: "Done",
      generic_error: "Something went wrong",
      error_log_title: "Problems to fix",
      history_panel_title: "Allocation history",
      btn_toggle: "Show/hide",
      th_time: "Time",
      th_seed: "Starting number",
      th_rounds: "Rounds",
      th_matched_count: "Matched",
      th_total: "Total",
      th_buoi_da_chay: "{session_p} allocated",
      th_redrawn: "Redrawn",
      history_empty: "No allocations yet.",
      yes: "Yes",
      no: "No",

      results_title: "Results",
      results_desc: "{person_p} matched to {slot_la}, and how full each {slot_l} is.",
      aria_thu_gon_muc: "Collapse or expand this section",
      hieu_ung_bat: "Animations: on",
      hieu_ung_tat: "Animations: off",
      aria_hieu_ung: "Turn motion effects on or off to make the app faster",
      btn_thu_gon_tat_ca: "Collapse all",
      btn_mo_rong_tat_ca: "Expand all",
      dem_hoc_sinh: "{n} {person_pl}",
      dem_cau_lac_bo: "{n} {slot_pl}",
      dem_dong: "{n} rows",
      clb_title: "By {slot_l}",
      clb_desc: "Don't add up the \"Applicants\" column: {person_la} who picks three {slot_pl} in one {session_l} is counted on all three rows but can only get one seat.",
      clb_empty: "No {slot_pl} yet.",
      clb_ds_tieu_de: "Members of {ten}",
      btn_xem_danh_sach: "View roster",
      btn_dong_danh_sach: "Close roster",
      th_so_dang_ky: "{person_p} who applied",
      th_dat_nv1: "Ranked it first",
      th_da_xep: "Placed",
      du_tru_title: "Reserve seats used",
      du_tru_desc: "Reserve seats nobody uses become regular seats, and the priority meant for that group is lost.",
      du_tru_khong_co: "No {slot_l} reserves any seats yet.",
      th_nhom_dang_ky: "Group members who applied",
      th_da_dung: "Used",
      th_con_thua: "Unused",
      nv_title: "How well choices were met",
      nv_donut_tam: "first choice",
      nv_desc: "A seat count doesn't show whether each seat matches a preference. This chart does.",
      nv_hang: "Choice {n}",
      nv_hang_gop: "Choice {n} or later",
      nv_khong_ro: "Rank not recorded",
      chua_co_cho_title: "{person_p} without {slot_la}",
      chua_co_cho_desc: "{person_lac} who chose one crowded {slot_l} and {person_la} who chose many {slot_pl} but still has no seat are different cases that need different fixes.",
      chua_co_cho_khong_ai: "Every {person_l} has at least one {slot_l}.",
      th_so_nguyen_vong: "Preferences entered",
      th_da_khai: "{slot_p} ranked",
      chua_khai_gi: "No preferences yet",
      dem_suat: "{n} unused seats",
      dem_cho: "{n} placements",
      fill_panel_title: "Fill rate by {slot_l}",
      tom_tat_title: "Run summary",
      tom_tat_lan_chay: "Latest run: {luc} · starting number {seed}",
      kpi_da_xep: "{person_p} placed",
      kpi_da_xep_phu: "{p}% of {person_pl}",
      kpi_nv1: "Got first choice",
      kpi_nv1_phu: "{p}% within top 3 choices",
      kpi_cho_trong: "Empty seats",
      kpi_cho_trong_phu: "out of {n} seats",
      kpi_chua_co_cho: "{person_p} with no place",
      kpi_du_tru_thua: "Reserve seats unused",
      kpi_du_tru_thua_phu: "Priority policy not fully used",
      kpi_can_xu_ly: "Needs action",
      kpi_on: "OK",
      kpi_bam_de_xem: "Click to open the detail section",
      fill_hint: "Hover (or Tab to) a row for details. The tags on the right flag {slot_pl} worth a look.",
      fill_sap_xep_nhan: "Sort",
      fill_sap_xep_buoi: "By {session_l}",
      fill_sap_xep_day: "Fullest first",
      fill_sap_xep_vang: "Emptiest first",
      fill_sap_xep_choi: "Most competitive",
      fill_nhom_tong: "{xep}/{cho} seats · {p}%",
      fill_choi: "{x}× demand",
      fill_tag_khong_ai: "Nobody",
      fill_tag_con_nhieu: "Many seats left",
      legend_trong: "Empty",
      tt_da_xep: "Placed",
      tt_so_cho: "Placements",
      tt_so_em: "{person_p}",
      tt_ti_le: "Share",
      tt_luy_ke: "Cumulative",
      nv_tieu_diem: "{p1}% of placements are a first choice · {p3}% are within the top 3",
      legend_general: "Regular seats",
      legend_reserve: "Admitted on a reserved seat",
      results_list_title: "{slot} assignments",
      placeholder_results_search: "Search by {person_l} ID or name…",
      ket_qua_cu_banner: "Data was edited after the last run, so the results below may be out of date. Run again in the \"Allocation\" tab before exporting or publishing.",
      xuat_title: "Export data",
      xuat_opt_ket_qua: "Placement results: one Excel file ({person_l} list, each {slot_l}, {person_pl} without a place, statistics)",
      xuat_opt_kem_csv: "Also write separate CSV files (only needed to load the data into other software)",
      xuat_opt_dau_vao: "Current input data: one Club Input Workbook that can be imported again",
      xuat_opt_thay_doi: "Changes since the previous run",
      xuat_thay_doi_dem: "({n} change(s))",
      xuat_thay_doi_chua_co: "(no previous run to compare with)",
      btn_xuat_tuy_chon: "Export selected items",
      xuat_hint_hoc_sinh: "{person} profiles: press \"Choose {person_pl}…\" and tick them in the table below. With {person_la} open in tab 03, press \"Export this {person_l} as CSV\" right there.",
      xuat_opt_hoc_sinh: "Selected {person_l} profiles",
      xuat_hoc_sinh_dem: "({n} {person_l}(s))",
      xuat_hoc_sinh_chua_chon: "(no {person_pl} selected)",
      btn_chon_hoc_sinh: "Choose {person_pl}…",
      hien_ca_em_chua_xep: "Also show {person_pl} with no place",
      ca_tuan: "Whole week",
      btn_di_toi_chay: "Go to Allocation",
      btn_mo_thu_muc: "Open folder",
      btn_xuat_em_nay: "Export this {person_l} as CSV",
      fallback_xuat_chua_luu: "This {person_l} has unsaved changes. Save first, then export.",
      fallback_chua_luu: "• Unsaved",
      fallback_chua_luu_canh_bao: "{person} {student_id} has unsaved changes. Press Save, or click again to discard them.",
      admin_dem_danh_dau: "{n} {person_l}(s) ticked",
      xuat_canh_bao_diem: "Exported files contain {score_pl} and lottery numbers. Do not send them to the scoring teachers.",
      btn_xuat_hs_da_chon: "Export selected {person_pl} as CSV",
      btn_bo_chon_hs: "Clear selection",
      btn_admin_xuat_hs: "Export ticked {person_pl} as CSV",
      aria_chon_tat_ca_dang_hien: "Select all {person_pl} shown",
      aria_chon_tat_ca_trang: "Select all {person_pl} on this page",
      hs_da_chon_dem: "{n} {person_l}(s) selected",
      hs_chua_chon: "No {person_pl} selected. Tick them in the first column.",
      toast_xuat_chua_chon_muc: "Nothing selected to export.",
      xuat_kq_dau_vao: "Input data (Club Input Workbook) → {path}",
      xuat_kq_dau_vao_thieu: "  {n} test entry(ies) for {slot_pl} the {person_l} didn't rank are not in the workbook (they can't affect the result).",
      xuat_kq_thay_doi: "Changes since the previous run: {n} row(s) → {path}",
      xuat_kq_hoc_sinh: "{n} {person_l} profile(s) ({n_dong} row(s)) → {path}",
      xuat_kq_loi: "Could not export {muc}: {errors}",
      xuat_kq_cu: "Note: data was edited after the last run, so results in the file may be out of date.",
      xuat_muc_ket_qua: "results",
      xuat_muc_dau_vao: "input data",
      xuat_muc_thay_doi: "changes",
      xuat_muc_hoc_sinh: "{person_l} profiles",
      xuat_bo_hs_khong_con: "Removed {person_pl} who no longer exist from the selection: {ds}. Press Export again for the rest.",
      th_student_id: "{person} ID",
      th_name: "Name",
      th_club: "{slot}",
      th_tier: "Seat type",
      th_pref_rank: "Preference rank",
      results_empty_state: "No results yet. Run the allocation on the \"Allocation\" tab first.",
      not_matched_label: "Not matched",
      unmatched_badge: "{n} {person_l}(s) without {slot_la}",
      tier_general: "General",
      tier_reserve: "Reserve",

      fallback_title: "Kiosk entry",
      fallback_desc: "Find or add {person_la}, then complete two steps: choose test {slot_pl} and rank preferences. The steps don't depend on each other.",
      fallback_step0_title: "Find or create {person_la}",
      placeholder_fallback_search: "Enter {person_l} ID or name…",
      btn_search: "Search",
      placeholder_new_student_id: "New {person_l} ID",
      placeholder_full_name: "Full name",
      btn_create_student: "Create new {person_l}",
      btn_reset_entry: "Start over",
      confirm_reset_entry: "Click again to clear everything, {score_pl} included, and start over",
      btn_delete_student: "Delete {person_l}",
      confirm_delete_student: "Click again to delete this {person_l}",
      fallback_step1_title: "Step 1. Choose test {slot_pl}",
      fallback_step1_hint: "Up to {max_tests} {slot_pl} per {session_l}. Unticking {slot_la} that has already been scored deletes that {score_l} on save.",
      fallback_step1_hint_khong_gioi_han: "Any number of {slot_pl} per {session_l} can be tested. Unticking {slot_la} that has already been scored deletes that {score_l} on save.",
      btn_save_test_selection: "Save test {slot_pl}",
      fallback_step2_title: "Step 2. Rank preferences",
      fallback_step2_hint: "Click {slot_pl} in order, most wanted first, up to {max_choices} per {session_l}. {slot_p} not picked in Step 1 can be ranked too.",
      ranking_current_label: "Preference order",
      btn_clear_all: "Clear all",
      btn_save_preferences: "Save preferences",
      fallback_step3_title: "Step 3. Preference points",
      fallback_step3_hint: "Split exactly 100 points across the tested {slot_pl} and exactly 100 across the {slot_pl} not tested, in each {session_l}. A blank box counts as 0.",
      wharton_khung_thi: "Tested {slot_pl}",
      wharton_khung_thi_ghi_chu: "These points only matter when two {person_pl} have the same test {score_l}.",
      wharton_khung_khong_thi: "{slot_p} not tested",
      wharton_khung_khong_thi_ghi_chu: "The more points, the higher the {person_l} ranks among other {person_pl} who did not test for this {slot_l}.",
      wharton_da_dung: "Used {x} / {tong}",
      wharton_can_chia_lai: "The points need to be split again.",
      btn_save_wharton: "Save preference points",
      feedback_wharton_saved: "Saved the preference points.",
      wharton_da_khoa_kiosk: "Preference points are locked because the allocation has run. Ask the manager to unlock them in the Manage tab if they need editing.",
      /* "Preference points" block in the Manage tab (A13.3). */
      wh_ql_title: "Preference points",
      wh_ql_desc: "View, edit and delete the preference points each {person_l} has split. After an allocation run the points are locked so the results can't change quietly.",
      wh_ql_dang_khoa: "Locked since {luc}",
      wh_ql_dang_mo: "Unlocked, points can be edited",
      btn_wh_mo_khoa: "Unlock preference points",
      wh_mo_khoa_hoi: "Unlock to edit the points. Existing results don't change by themselves, and the next allocation run locks them again. Type {can_go} to confirm.",
      btn_wh_mo_khoa_xn: "Confirm unlock",
      aria_wh_go_mo_khoa: "Type the confirmation word to unlock",
      aria_wh_go_xoa: "Type the confirmation word to delete",
      wh_canh_bao_title: "Profiles that need attention",
      wh_cb_chua_hop_le: "Not split correctly",
      wh_cb_vang_thi: "Missed the test",
      wh_cb_rong: "No profile needs attention.",
      wh_tim_placeholder: "Search {person_pl} by ID or name…",
      wh_loc_quy: "Fund",
      wh_loc_buoi: "{session}",
      wh_loc_clb: "{slot}",
      wh_loc_tat_ca: "All",
      wh_quy_1: "Fund 1, tested",
      wh_quy_2: "Fund 2, not tested",
      wh_quy_ngan: "Fund {q}",
      wh_loc_chi_loi: "Only profiles with problems",
      th_wh_diem: "Points split",
      th_wh_tt: "Status",
      wh_tong: "Total {x}",
      wh_o_tu_dien: "auto-filled",
      wh_tt_ok: "Valid",
      wh_tt_loi: "Not valid",
      wh_tt_vang: "Missed the test",
      wh_tt_lech: "Needs a new split",
      wh_bang_rong: "No profile matches.",
      wh_sua_title: "Edit points for {name}",
      wh_sua_dong: "Close",
      wh_sua_khoa: "The points are locked, so they can only be viewed. Unlock them at the top of this section to edit.",
      wh_sua_rong: "This {person_l} has no preferences yet, so there is nothing to split.",
      btn_wh_xoa_mot: "Delete this {person_l}'s points",
      confirm_wh_xoa_mot: "Click again to delete the points",
      toast_wh_xoa_mot: "Deleted the preference points of {student_id}.",
      wh_nhat_ky_title: "Change log",
      wh_nhat_ky_rong: "No changes yet.",
      btn_wh_xem_them: "Show more",
      wh_nk_quan_ly: "Manage tab",
      wh_nk_kiosk: "kiosk entry",
      wh_nk_nap_tep: "file import",
      wh_nk_xoa_du_lieu: "data deletion",
      wh_nk_he_thong: "system",
      wh_nk_luu: "saved points",
      wh_nk_xoa_mot_em: "deleted points",
      wh_nk_xoa_tat_ca: "deleted everyone's points",
      wh_nk_tia_nguyen_vong: "removed points of an item dropped from the preferences",
      wh_nk_xoa_theo_clb: "deleted points because the {slot_l} was deleted",
      wh_nk_khoa: "locked the points",
      wh_nk_mo_khoa: "unlocked the points",
      wh_nk_dong: "{luc}, {nguon}{nguoi}: {hanh_dong}",
      btn_wh_xoa_tat_ca: "Delete the preference points of all {person_pl}",
      wh_xoa_tat_ca_hoi: "Delete the preference points of all {person_pl}. The data is backed up before deleting. Type {can_go} to confirm.",
      btn_wh_xoa_tat_ca_xn: "Confirm delete",
      btn_remove_ranked: "remove",
      search_no_students_found: "No {person_pl} found.",
      hs_nhan_clb_thi: "Test {slot_pl}",
      hs_nhan_nguyen_vong: "Preferences",
      hs_the_chua_chon: "None yet",
      hs_trang_thai_du: "Complete",
      hs_trang_thai_thieu_thi: "No test {slot_pl}",
      hs_trang_thai_thieu_nv: "No preferences",
      hs_trang_thai_trong: "Nothing entered",
      toast_need_id_and_name: "Both {person_la} ID and a name are required.",
      toast_student_created: "New {person_l} created.",
      toast_student_exists: "This {person_l} already exists. Opening the details.",
      feedback_test_selection_saved: "Saved {n} test {slot_l}(s).",
      feedback_test_selection_saved_removed: "Saved {n} test {slot_l}(s) and deleted {m} {score_l}(s) for unticked {slot_pl}.",
      feedback_preferences_saved: "Saved {n} preference(s).",
      toast_reset_done: "Cleared the test {slot_pl} and preferences. Ready to enter again.",
      toast_reset_done_removed: "Cleared test {slot_pl}, preferences and {m} {score_l}(s). Ready to re-enter.",
      toast_student_deleted: "Deleted {person_l} {student_id}.",

      admin_title: "{slot_p} & reserves",
      admin_desc: "Add or edit {slot_pl} and give {person_pl} reserve labels. The school decides who gets reserve seats. The app only matches {person_pl} and {slot_pl} that share a label.",
      admin_club_form_title: "Add or edit {slot_la}",
      placeholder_club_id: "{slot} ID (e.g. club_01)",
      placeholder_club_name: "{slot} name",
      placeholder_capacity: "Total seats",
      placeholder_reserve_capacity: "Reserved seats",
      placeholder_reserve_group: "Reserve label (leave blank if none)",
      btn_save_club: "Save {slot_l}",
      th_club_id: "{slot} ID",
      th_name_short: "Name",
      th_capacity: "Total seats",
      th_reserve_capacity: "Reserved seats",
      th_reserve_group: "Reserve label",
      admin_club_empty: "No {slot_pl} yet. Add the first one with the form above.",
      admin_reserve_assign_title: "Reserve labels and {person_l} profile export",
      placeholder_admin_student_search: "Search {person_pl} by ID or name…",
      placeholder_reserve_group_apply: "Reserve label to apply",
      btn_bulk_assign: "Assign to ticked {person_pl}",
      th_current_reserve_group: "Current reserve label",
      admin_student_empty: "No {person_pl} yet. Add them on the \"Kiosk entry\" tab or import a Microsoft Forms file.",
      btn_prev_page: "‹ Prev",
      btn_next_page: "Next ›",
      pagination_label: "Page {page}/{total_pages} · {total} {person_pl}",
      btn_delete: "Delete",
      confirm_delete_generic: "Click again to delete",
      toast_club_deleted: "Deleted {slot_l} {club_id}.",

      danger_zone_title: "Danger zone: delete data to start over",
      danger_zone_desc: "Importing a file only adds {person_pl}. It doesn't remove existing ones. To start over with a different set, delete here first, or the old {person_pl} will keep taking seats.",
      danger_zone_safety: "Both buttons back up the data before deleting. The allocation history is kept.",
      btn_reset_students: "Delete all {person_pl} (keep {slot_pl})",
      btn_reset_all: "Delete all data ({slot_pl} too)",
      confirm_reset_students: "Click again to delete all {person_pl}",
      confirm_reset_all: "Click again to delete all data",
      confirm_reset_students_has_results: "Click again. The allocation results will also be deleted",
      confirm_reset_all_has_results: "Click again. {slot_p} and allocation results will also be deleted",
      toast_reset_students_done: "Deleted {n_students} {person_l}(s); {n_clubs_left} {slot_l}(s) kept. Backup: {backup_name}",
      toast_reset_all_done: "Deleted {n_students} {person_l}(s) and {n_clubs} {slot_l}(s). Backup: {backup_name}",
      toast_reset_blocked_busy: "Files are being imported or an allocation is running. Wait for it to finish, then delete the data.",
      feedback_club_form_required: "Enter the {slot_l} code, name, and total seats.",
      feedback_club_saved: "Saved {slot_l} {club_id}.",
      toast_no_students_ticked: "No {person_pl} ticked.",
      toast_bulk_assign_success: "Assigned to {n} {person_l}(s).",

      scoring_title: "{score} entry",
      scoring_desc: "Choose {slot_la} to score. The list shows only codes and names, never lottery numbers or preference ranks, so scoring stays fair.",
      scoring_desc_person: "Enter one {score_l} for each {person_l}. The list shows only codes and names, never lottery numbers or preference ranks, so scoring stays fair.",
      scoring_person_title: "{score} for each {person_l}",
      scoring_person_progress: "Scored {n_scored} of {n}",
      scoring_person_empty: "No {person_pl} to score yet. Import the list first.",
      scoring_overview_title: "Scoring progress by {slot_l}",
      th_n_applicants: "Registered",
      th_n_scored: "Scored",
      scoring_overview_empty: "No {slot_l} has {person_pl} signed up to test yet.",
      btn_save_scores: "Save {score_pl}",
      th_score: "{score}",
      btn_score_link: "Score →",
      feedback_scores_saved: "Saved {score_pl} for {n} {person_l}(s).",
      feedback_scores_saved_mot_phan: "Saved {score_pl} for {n} {person_l}(s); {k} box(es) were not valid and were not saved (marked in red).",

      stb_locked_label: "Lottery numbers locked since {locked_at}. Later allocations keep the same order, and new {person_pl} are added at random.",
      stb_unlocked_label: "No lottery has been drawn yet. The first allocation will draw and lock the numbers.",
      btn_redraw_stb: "Redraw lottery…",
      toast_redraw_armed: "Click \"Run allocation\" to redraw the lottery. There will be one more confirmation before it runs.",
      health_panel_title: "Data warnings",
      health_panel_hint: "These don't stop the allocation, but they can skew the results. Check them before running.",
      health_clean: "No problems found. The data is ready.",
      health_summary: "{n} warning(s), {n_high} serious.",
      health_sev_high: "Serious",
      health_sev_medium: "Worth checking",
      health_sev_info: "Information",
      btn_health_recheck: "Re-check",
      toast_data_valid: "The data is valid: {n_students} {person_pl}, {n_clubs} {slot_pl}.",
      toast_hop_le_con_canh_bao: "But {n_high} serious warning(s) remain. Check Data warnings before running.",
      toast_data_invalid: "The data has problems. See the list below.",
      confirm_redraw_run: "Redraw every lottery number and allocate again? The current results will be replaced.",
      confirm_overwrite_run: "Results already exist. Allocating again replaces them, and the old ones stay in the history. Continue?",
      confirm_overwrite_mot_phan: "Allocate {buoi} again and replace those {session_pl}' results. Other {session_pl} stay as they are. Continue?",
      btn_confirm_run: "Run",
      btn_cancel: "Cancel",
      toast_run_success: "Allocation finished: {n_matched}/{n_total} {person_pl} placed in {rounds} round(s).",
      toast_run_failed: "The allocation didn't finish. See the list below.",
      feedback_no_file_selected: "No file selected.",
      toast_export_success: "Exported the results of {n_hoc_sinh} {person_l}(s) to one Excel file: {path}\n{n_trang} sheets: {trang}.",
      xuat_kq_kem_csv: "Separate CSV files too: {path} and {n_club_files} file(s) per {slot_l}.",
      xuat_kq_csv_loi: "The Excel file was written, but the separate CSV files could not be: {errors}",

      recovery_title: "Data recovery",
      recovery_heading: "Couldn't open the data",
      recovery_intro: "The program couldn't start because the data file has a problem. The data may still be there. Try the steps below before asking for help.",
      recovery_error_detail_label: "Technical details (send to support if needed)",
      recovery_backups_label: "Backups found on this machine:",
      th_backup_name: "File name",
      th_backup_time: "Backed up at",
      th_backup_size: "Size",
      btn_restore_backup: "Restore from the latest backup",
      btn_start_fresh: "Start with empty data",
      confirm_start_fresh: "Click again to confirm. The damaged file will be renamed, not deleted",
      recovery_working: "Working…",
      recovery_please_restart: "Close and reopen the program to continue.",
      recovery_kg_heading: "The program cannot save data in this folder",
      recovery_kg_intro: "The data is not damaged. Windows is not letting the program create files in the folder it is in.",
      recovery_kg_thu_muc: "Program folder:",
      recovery_kg_vi_sao: "Usually one of three things: the folder is inside Documents/Desktop and Windows has \"Controlled folder access\" (ransomware protection) turned on; the folder is inside a syncing OneDrive; or the folder is inside Program Files.",
      recovery_kg_cach_tieu_de: "How to fix it, doing just one of these:",
      recovery_kg_cach_1: "Close the program. Move the whole program folder to a plain location such as C:\\RBDA (create it directly on drive C:, not inside Documents, Desktop or OneDrive). Then open PhanBoCauLacBo.exe again.",
      recovery_kg_cach_2: "Or keep it where it is and allow the program: Windows Security → Virus & threat protection → Ransomware protection → Controlled folder access → Allow an app through → add PhanBoCauLacBo.exe. Then open the program again.",
      recovery_kg_khong_mat: "Existing data (if any) is not lost. There is no need to restore or start over.",
      btn_kiem_lai_thu_muc: "Check again",
      recovery_kg_van_chua: "The folder is still not writable. Please do one of the two fixes above.",
      recovery_kg_da_duoc: "The folder is writable now. Close the program and open it again.",

      /* --- Multiple sessions per week --- */
      buoi_chua_chia: "No {session_l} set",
      th_buoi: "{session}",
      placeholder_buoi: "{session} (e.g. thu_3)",
      buoi_hint_form: "Two {slot_pl} in the same {session_l} clash, so {person_la} can join only one. Leave it blank if the school has a single {session_l}.",
      admin_lich_tuan_title: "The week at a glance",
      admin_lich_tuan_desc: "Each column is one {session_l}. The bar under each {slot_l} shows how full it was on the latest run.",
      admin_tai_buoi_title: "Demand by {session_l}",
      admin_tai_buoi_desc: "Check this before allocating. If one {session_l} is crowded while another has room, move {slot_la} to the quieter {session_l}.",
      th_so_clb: "{slot_p}",
      th_tong_cho: "Seats",
      th_em_muon_buoi: "{person_p} wanting it",
      th_ti_le_choi: "Applicants per seat",
      ti_le_choi_giai_thich: "Applicants per seat counts {person_pl}, not preferences, because each {person_l} gets at most one seat per {session_l}.",
      tai_buoi_qua_tai: "Oversubscribed",
      tai_buoi_vua_du: "About right",
      tai_buoi_con_trong: "Room to spare",
      tai_buoi_empty: "No {slot_pl} yet, so there is nothing to measure.",
      chon_buoi_title: "{session_p} to allocate",
      chon_buoi_tu: "From",
      chon_buoi_den: "to",
      chon_buoi_tat_ca: "Select all",
      chon_buoi_nhac_giu: "Keeping the existing results for {buoi}. Only the selected {session_pl} are allocated again.",
      chon_buoi_nhac_het: "Every {session_l} in the week will be allocated again.",
      tham_title: "Lottery order by {session_l}",
      tham_desc: "Each {session_l} has its own order, shuffled from the locked numbers, so no {person_l} ends up last in every {session_l}.",
      tham_tai_lap: "Publishing the locked numbers and the starting number is enough. Anyone who recalculates gets this exact table.",
      tham_cach_cu: "The last allocation used the old lottery, one order for the whole week, so the columns below match. Run the allocation again to give each {session_l} its own order.",
      results_xem_tkb: "Timetable",
      results_xem_danh_sach: "List",
      tkb_title: "The week each {person_l} gets",
      tkb_desc: "One row per {person_l}, one cell per {session_l}. An empty cell means no {slot_l} for that {person_l} in that {session_l}.",
      tkb_so_clb: "{slot_p}",
      do_phu_title: "How many {slot_pl} each {person_l} got",
      do_phu_desc: "The most important number is how many {person_pl} have no {slot_l} all week.",
      do_phu_tb: "{slot_p} per {person_l}",
      do_phu_trang_tay: "{person_p} with no {slot_l} all week",
      do_phu_x_clb: "{n} {slot_pl}",
      do_phu_0_clb: "No {slot_l}",
      do_phu_1_clb: "1 {slot_l}",
      do_phu_danh_sach: "{person_p} without {slot_la}",
      fallback_buoi_hint: "{person_lac} can get at most one {slot_l} per {session_l}. Choosing {slot_pl} in several {session_pl} fills the week.",
      fallback_phu_buoi: "Ranked in {n} of {tong} {session_pl}",
      chi_tiet_ky_thuat: "Technical details",
      btn_dong_thong_bao: "Close",
      ws_switcher_nhan: "Workspace",
      ws_switcher_aria: "Switch workspace",
      ws_chon_title: "Choose a workspace",
      ws_chon_hint: "Each workspace has its own data and allocation rules, kept in its own folder.",
      ws_rong: "There are no workspaces yet. Create one or import a .zip file.",
      ws_dang_mo_nhan: "Open now",
      ws_cot_ten: "Name",
      ws_cot_loai: "Type",
      ws_cot_sua: "Last modified",
      ws_loai_school: "School",
      ws_loai_company: "Company",
      ws_loai_event: "Event",
      ws_loai_custom: "Custom",
      ws_mau_truong_hoc: "School",
      ws_btn_mo: "Open",
      ws_btn_doi_ten: "Rename",
      ws_btn_nhan_ban: "Duplicate",
      ws_btn_luu_mau: "Save as template",
      ws_btn_xuat: "Export .zip",
      ws_btn_xoa: "Delete",
      ws_btn_xoa_xn: "Click again to delete",
      ws_btn_moi: "New",
      ws_btn_nhap_zip: "Import .zip",
      ws_btn_dong: "Close",
      ws_btn_luu: "Save",
      ws_btn_tiep: "Next",
      ws_btn_quay_lai: "Back",
      ws_btn_tao: "Create workspace",
      ws_ten_moi: "New name",
      ws_ten_mau: "Template name",
      ws_nhan_ban_ten_mac_dinh: "{ten} (copy)",
      ws_nhan_ban_kem: "Include data",
      ws_khong_xoa_dang_mo: "This workspace is open, so it can't be deleted. Open another workspace first.",
      ws_chi_nhan_zip: "Only .zip files exported by this program are accepted.",
      ws_da_mo: "Opened workspace \"{ten}\".",
      ws_da_tao: "Created workspace \"{ten}\".",
      ws_da_doi_ten: "Renamed to \"{ten}\".",
      ws_da_nhan_ban: "Duplicated as \"{ten}\".",
      ws_da_luu_mau: "Saved template \"{ten}\".",
      ws_da_xuat: "Exported workspace: {path}",
      ws_da_xoa: "Moved workspace \"{ten}\" to the trash (the _trash folder). It is not deleted permanently.",
      ws_da_nhap: "Imported workspace \"{ten}\".",
      ws_wz_title: "Create a new workspace",
      ws_wz_buoc: "Step {n} of {tong}",
      ws_wz_b1: "Basics",
      ws_wz_b2: "Vocabulary",
      ws_wz_b3: "Rules",
      ws_wz_b4: "Review",
      ws_wz_ten: "Workspace name",
      ws_wz_ten_ph: "For example: Company A, 2026 projects",
      ws_wz_loai: "Type",
      ws_wz_mau: "Start from a template",
      ws_wz_mau_hint: "Choosing a template pre-fills all four steps, and every field can still be edited.",
      ws_wz_tu_vung_hint: "Name the five concepts of this workspace. Leave the English box empty to use the Vietnamese word.",
      ws_wz_vi: "Vietnamese",
      ws_wz_en: "English",
      ws_wz_en_ph: "Empty = use Vietnamese",
      ws_wz_xem_lai_hint: "One last check. Click Back to change something; click Create workspace to build and open it.",
      ws_dt_person: "Participant",
      ws_dt_person_mo_ta: "Who gets placed (e.g. student, employee).",
      ws_dt_slot: "Place",
      ws_dt_slot_mo_ta: "Where participants are placed (e.g. club, project, room).",
      ws_dt_session: "Round",
      ws_dt_session_mo_ta: "Each person gets at most one place per round (e.g. session, shift).",
      ws_dt_group: "Priority group",
      ws_dt_group_mo_ta: "The group a participant belongs to that can earn priority (e.g. grade, policy, level).",
      ws_dt_score: "Score",
      ws_dt_score_mo_ta: "The number used to rank participants (e.g. entrance test score).",
      ws_r_max_choices: "Most choices per round (1–20)",
      ws_r_max_tests: "Most tested places per round (0–20)",
      ws_r_khong_gioi_han: "No limit",
      ws_r_priority: "Priority order",
      ws_r_priority_score: "By score",
      ws_r_priority_tier: "By group only (no scores)",
      ws_r_priority_both: "Group first, then score",
      ws_r_tier_mode: "How groups are used",
      ws_r_tm_reserve: "Soft reserved seats (as in schools)",
      ws_r_tm_strict: "Strict group ranking",
      ws_r_score_scope: "Scope of the score",
      ws_r_ss_per_slot: "A separate score for each place (as in schools)",
      ws_r_ss_per_person: "One score per person",
      ws_r_wharton: "Use preference points",
      ws_r_wharton_ghi_chu: "Each person splits 100 points across the items they took a test for and 100 across the items they did not, in every round. Only available when the priority order uses scores and each place has its own score.",
      ws_r_wharton_bat: "On",
      ws_r_wharton_tat: "Off",
      ws_r_tiers: "Group order: best first, one group per line",
      ws_r_tiers_ph: "Senior\nMiddle\nJunior",
      ws_r_tiers_chi_strict: "Used with \"Strict group ranking\" or the \"By group only\" priority. People in no listed group come last.",
      ws_r_canh_bao_nhom: "Note: priority is \"Group first, then score\", but \"Strict group ranking\" is not selected, so the group order won't be used.",
      ws_v_ten: "Enter a name.",
      ws_v_vi: "The Vietnamese box for \"{muc}\" can't be empty.",
      ws_v_max_choices: "Most choices must be a whole number from 1 to 20.",
      ws_v_max_tests: "Most tested places must be a whole number from 0 to 20, or tick \"No limit\".",
      ws_v_tiers: "The group list has two identical lines.",
    },
  };

  let currentLang = "vi";
  try {
    const stored = global.localStorage && global.localStorage.getItem("rbda_lang");
    if (stored === "vi" || stored === "en") currentLang = stored;
  } catch (e) {
    /* localStorage unavailable — default to vi */
  }

  /* ------------------------------------------------------------------ *
   * TỪ VỰNG CỦA WORKSPACE
   * ------------------------------------------------------------------ *
   * Chuỗi nói về năm danh từ của nghiệp vụ (học sinh, câu lạc bộ, buổi, nhóm
   * ưu tiên, điểm) không ghi cứng mà dùng chỗ giữ {person} {slot} {session}
   * {group} {score}; t() điền nhãn của workspace đang mở, theo ngôn ngữ đang
   * chọn. Đối xứng với nhan_ws.py (Python) — tests/test_ws_nhan.py so từng ca.
   *
   * Cờ sau dấu gạch dưới: l chữ thường · p số nhiều (tiếng Anh) · s viết tắt
   * ("Câu lạc bộ" -> "CLB") · a mạo từ a/an (tiếng Anh) · c viết hoa chữ đầu · u VIẾT HOA TOÀN BỘ · v luôn lấy nhãn tiếng Việt;
   * áp theo thứ tự s l p a c u.
   * Ví dụ {slot_sl}, {person_pl}, {person_lac}. Mặc định trường học cho ra
   * ĐÚNG những chuỗi từng được ghi cứng.
   */
  const NHAN_MAC_DINH = {
    person: { vi: "Học sinh", en: "Student" },
    slot: { vi: "Câu lạc bộ", en: "Club" },
    session: { vi: "Buổi", en: "Session" },
    group: { vi: "Nhóm ưu tiên", en: "Priority group" },
    score: { vi: "Điểm", en: "Score" },
  };
  const VIET_TAT = { "slot|Câu lạc bộ": "CLB" };
  const CHO_GIU_DANH_TU = /^(person|slot|session|group|score)(?:_([lpsacuv]+))?$/;
  let currentLabels = NHAN_MAC_DINH;
  /* Hai con số luật của workspace hiện trong chữ: {max_choices}, {max_tests}. Mặc định
     trường học (10 và 5) cho ra đúng chữ từng ghi cứng. max_tests null = không giới hạn:
     chuỗi nào cần câu riêng cho trường hợp đó thì chọn khoá khác (xem 075_workspace.js). */
  const LUAT_MAC_DINH = { max_choices: 10, max_tests: 5 };
  let currentRules = LUAT_MAC_DINH;

  /* Nhãn của workspace; thiếu/rỗng thì lấy mặc định. Trả về true nếu có đổi. */
  function setLabels(labels) {
    const moi = {};
    Object.keys(NHAN_MAC_DINH).forEach((dt) => {
      const cap = labels && labels[dt];
      if (!cap || !Object.keys(cap).length) {
        moi[dt] = { vi: NHAN_MAC_DINH[dt].vi, en: NHAN_MAC_DINH[dt].en };
        return;
      }
      /* Khai vi mà bỏ en thì en = vi đó, không phải en mặc định ("Student" cạnh "Nhân viên"). */
      const vi = String(cap.vi || "").trim() || NHAN_MAC_DINH[dt].vi;
      moi[dt] = { vi, en: String(cap.en || "").trim() || vi };
    });
    const doi = JSON.stringify(moi) !== JSON.stringify(currentLabels);
    currentLabels = moi;
    return doi;
  }

  function getLabels() {
    return JSON.parse(JSON.stringify(currentLabels));
  }

  /* Luật của workspace (rules.max_choices / rules.max_tests). Trả về true nếu có đổi. */
  function setRules(rules) {
    const r = rules || {};
    const moi = {
      max_choices: Number.isInteger(r.max_choices) ? r.max_choices : LUAT_MAC_DINH.max_choices,
      max_tests: r.max_tests === null ? null
        : (Number.isInteger(r.max_tests) ? r.max_tests : LUAT_MAC_DINH.max_tests),
    };
    const doi = JSON.stringify(moi) !== JSON.stringify(currentRules);
    currentRules = moi;
    return doi;
  }

  function getRules() {
    return JSON.parse(JSON.stringify(currentRules));
  }

  function soNhieuTiengAnh(chu) {
    if (!chu) return chu;
    const thuong = chu.toLowerCase();
    if (/(s|x|z|ch|sh)$/.test(thuong)) return chu + "es";
    if (/[^aeiou]y$/.test(thuong)) return chu.slice(0, -1) + "ies";
    return chu + "s";
  }

  /* Nhãn tiếng Anh thật gần như luôn là chữ Latin không dấu. Nhãn en để trống rơi về
     chữ Việt, và "nhân viêns" / "a nhân viên" là sai — nên chỉ chữ Latin mới được
     chia số nhiều hoặc thêm a/an. */
  function laChuAnh(chu) {
    return /^[A-Za-z][A-Za-z '\-]*$/.test(chu);
  }

  function nounText(noun, flags, lang) {
    if (flags.indexOf("v") !== -1) lang = "vi";   // chữ có thật trên tệp tiếng Việt
    const cap = currentLabels[noun];
    let chu = lang === "en" ? (cap.en || cap.vi) : cap.vi;
    if (flags.indexOf("s") !== -1 && lang === "vi") chu = VIET_TAT[noun + "|" + chu] || chu;
    /* Hạ thường TRƯỚC số nhiều: "HR" giữ nguyên rồi mới thành "HRs". Chữ viết tắt
       (CLB, HR) không hạ thường: "clb" không phải một từ. */
    if (flags.indexOf("l") !== -1 && chu !== chu.toUpperCase()) chu = chu.toLowerCase();
    if (flags.indexOf("p") !== -1 && lang === "en" && laChuAnh(chu)) chu = soNhieuTiengAnh(chu);
    if (flags.indexOf("a") !== -1 && lang === "en" && chu && laChuAnh(chu)) {
      chu = ("aeiou".indexOf(chu.charAt(0).toLowerCase()) !== -1 ? "an " : "a ") + chu;
    }
    if (flags.indexOf("c") !== -1 && chu) chu = chu.charAt(0).toUpperCase() + chu.slice(1);
    if (flags.indexOf("u") !== -1) chu = chu.toUpperCase();
    return chu;
  }

  /* MỘT lượt thay duy nhất, tham số trước, danh từ sau. Một lượt (không phải hai
     lượt nối nhau) vì dữ liệu người dùng — tên học sinh, nhãn — có thể chứa
     chính chuỗi "{person}", và điền lần hai sẽ biến nó thành nhãn. */
  function interpolate(template, params) {
    return template.replace(/\{(\w+)\}/g, (match, key) => {
      if (params && key in params) {
        const v = params[key];
        if (v === null || v === undefined) return "";
        return Array.isArray(v) ? v.join(", ") : String(v);
      }
      const dt = CHO_GIU_DANH_TU.exec(key);
      if (dt) return nounText(dt[1], dt[2] || "", currentLang);
      if ((key === "max_choices" || key === "max_tests") && currentRules[key] !== null) {
        return String(currentRules[key]);
      }
      return match;
    });
  }

  function t(key, params) {
    const table = UI_STRINGS[currentLang] || UI_STRINGS.vi;
    const template = key in table ? table[key] : (UI_STRINGS.vi[key] || key);
    return interpolate(template, params);
  }

  function translateError(entry) {
    if (entry === null || entry === undefined) return "";
    if (typeof entry === "string") return entry;
    if (typeof entry === "object" && entry.code) {
      const table = ERROR_MESSAGES[entry.code];
      const template = table ? (table[currentLang] || table.vi) : entry.code;
      return interpolate(template, entry.params);
    }
    try {
      return JSON.stringify(entry);
    } catch (e) {
      return String(entry);
    }
  }

  function translateErrors(list) {
    if (!Array.isArray(list)) return [translateError(list)];
    return list.map(translateError);
  }

  /* Chi tiet ky thuat (params.detail = thong bao goc cua may) cua mot
     danh sach loi, bo trung va bo rong. Cau loi khong chen chi tiet nay;
     giao dien hien no rieng trong muc "Chi tiet ky thuat". */
  function errorDetails(list) {
    const ds = Array.isArray(list) ? list : [list];
    const kq = [];
    ds.forEach((e) => {
      const d = e && typeof e === "object" && e.params ? e.params.detail : null;
      if (d !== null && d !== undefined && String(d).trim() && kq.indexOf(String(d)) === -1) {
        kq.push(String(d));
      }
    });
    return kq;
  }

  function applyStaticText() {
    document.querySelectorAll("[data-i18n]").forEach((elm) => {
      // Skip a two-step-confirm button while it's armed (.is-confirming):
      // armTwoStepConfirm tracks "armed" state internally and only the
      // element's OWN reset logic may change its label back — overwriting
      // it here would desync visible state from internal state (button
      // would look freshly-unarmed while a single click still fires the
      // destructive action).
      if (elm.classList && elm.classList.contains("is-confirming")) return;
      elm.textContent = t(elm.getAttribute("data-i18n"));
    });
    // KHONG co `data-i18n-html`: truoc day co mot nhanh gan thang
    // innerHTML tu catalog, khong phan tu nao dung, va la cho duy nhat bien
    // chuoi dich thanh HTML. Can dinh dang thi dung the con + data-i18n.
    document.querySelectorAll("[data-i18n-placeholder]").forEach((elm) => {
      elm.placeholder = t(elm.getAttribute("data-i18n-placeholder"));
      /* Placeholder bien mat khi da go chu, va trinh doc man hinh khong coi
         no la nhan. O nao khong co <label> rieng thi lay chinh cau goi y do
         lam nhan doc len — cung khoa dich, nen doi ngon ngu cung doi theo. */
      if (!(elm.labels && elm.labels.length) && !elm.hasAttribute("data-i18n-aria-label")) {
        elm.setAttribute("aria-label", elm.placeholder);
      }
    });
    /* Nut chi co bieu tuong thi khong co chu nao de doc len — nhan cho
       trinh doc man hinh phai dich theo ngon ngu nhu moi chu khac.
       CANH: bieu thuc trong tests/test_i18n_sync.py phai phu ca duoi
       "-aria-label", neu khong khoa moi se lot khoi luoi canh va hien ra
       chuoi khoa tho ma khong test nao do. */
    document.querySelectorAll("[data-i18n-aria-label]").forEach((elm) => {
      elm.setAttribute("aria-label", t(elm.getAttribute("data-i18n-aria-label")));
    });
    document.title = t("page_title");
    /* Dat ca khi KHOI DONG, khong chi khi bam doi: truoc day ngon ngu luu
       tu lan truoc la tieng Anh thi trang hien tieng Anh ma van khai
       lang="vi" — trinh doc man hinh doc chu Anh bang giong Viet. */
    document.documentElement.lang = currentLang;
    const langBtn = document.getElementById("btnLangToggle");
    if (langBtn) langBtn.textContent = t("lang_toggle_label");
  }

  function getLang() {
    return currentLang;
  }

  function setLang(lang) {
    if (lang !== "vi" && lang !== "en") return;
    currentLang = lang;
    try {
      global.localStorage && global.localStorage.setItem("rbda_lang", lang);
    } catch (e) {
      /* ignore */
    }
    document.documentElement.lang = lang;
    applyStaticText();
    global.dispatchEvent(new Event("langchange"));
  }

  /* Gọi sau khi đặt nhãn mới: vẽ lại chữ tĩnh và báo cho phần động vẽ lại như khi đổi ngôn ngữ. */
  function applyLabels(labels) {
    if (!setLabels(labels)) return false;
    applyStaticText();
    global.dispatchEvent(new Event("langchange"));
    return true;
  }

  /* Nhãn + luật của một workspace (đúng dạng get_workspace_state().config). */
  function applyConfig(cfg) {
    const a = setLabels(cfg && cfg.labels);
    const b = setRules(cfg && cfg.rules);
    if (!a && !b) return false;
    applyStaticText();
    global.dispatchEvent(new Event("langchange"));
    return true;
  }

  global.I18N = {
    t, translateError, translateErrors, errorDetails, getLang, setLang, applyStaticText,
    setLabels, getLabels, applyLabels, setRules, getRules, applyConfig,
    fill: interpolate, nounText,
  };
})(window);
