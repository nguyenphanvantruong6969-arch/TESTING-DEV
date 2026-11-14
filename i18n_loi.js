/* ==========================================================================
   i18n_loi.js — TỆP SINH TỰ ĐỘNG, KHÔNG SỬA TAY.
   ==========================================================================
   Nguồn: MESSAGES trong i18n_errors.py. Sửa ở đó rồi chạy:
       python tao_i18n_js.py
   tests/test_i18n_sync.py đỏ ngay nếu tệp này lệch khỏi nguồn.
   ========================================================================== */
window.I18N_ERROR_MESSAGES = {
  "error_reading_last_run": {
    "vi": "Không đọc được thông tin lần sắp xếp gần nhất. Hãy thử lại.",
    "en": "Couldn't load the latest allocation. Try again."
  },
  "error_reading_dashboard": {
    "vi": "Không tải được trang tổng quan. Hãy thử lại.",
    "en": "Couldn't load the overview. Try again."
  },
  "error_checking_integrity": {
    "vi": "Không kiểm tra được dữ liệu. Hãy thử lại.",
    "en": "Couldn't check the data. Try again."
  },
  "error_checking_run_warning": {
    "vi": "Không kiểm tra được dữ liệu trước khi sắp xếp. Hãy thử lại.",
    "en": "Couldn't check the data before allocating. Try again."
  },
  "error_reading_stb_lock": {
    "vi": "Không kiểm tra được số bốc thăm. Hãy thử lại.",
    "en": "Couldn't check the lottery numbers. Try again."
  },
  "error_reading_run_history": {
    "vi": "Không mở được nhật ký các lần sắp xếp. Hãy thử lại.",
    "en": "Couldn't open the allocation history. Try again."
  },
  "error_running_pipeline": {
    "vi": "Sắp xếp bị dừng giữa chừng do một lỗi ngoài dự kiến. Dữ liệu chưa bị thay đổi. Hãy thử lại.",
    "en": "The allocation stopped because of an unexpected problem. No data was changed. Try again."
  },
  "xem_nhat_ky": {
    "vi": "Chi tiết kỹ thuật đã được ghi vào tệp {file}, nằm cùng thư mục với tệp dữ liệu. Nếu lỗi còn lặp lại, gửi tệp đó cho người phụ trách kỹ thuật.",
    "en": "Technical details were saved to {file}, in the same folder as the data file. If the error keeps happening, send that file to the technical contact."
  },
  "loi_ngoai_du_kien": {
    "vi": "Có lỗi ngoài dự kiến khi thực hiện thao tác ({ten}). Hãy thử lại.",
    "en": "Something unexpected went wrong during an operation ({ten}). Try again."
  },
  "error_reading_csv_preview": {
    "vi": "Không xem trước được tệp này. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't preview this file. Check the file and try again."
  },
  "error_importing_preferences_csv": {
    "vi": "Không nạp được tệp nguyện vọng. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the preferences file. Check the file and try again."
  },
  "error_importing_test_selection_csv": {
    "vi": "Không nạp được tệp chọn {slot_sl} dự thi. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the test {slot_l} file. Check the file and try again."
  },
  "error_reading_scoring_overview": {
    "vi": "Không tải được tình hình chấm {score_l}. Hãy thử lại.",
    "en": "Couldn't load the scoring overview. Try again."
  },
  "error_reading_scoring_list": {
    "vi": "Không tải được danh sách chấm {score_l}. Hãy thử lại.",
    "en": "Couldn't load the scoring list. Try again."
  },
  "error_saving_scores": {
    "vi": "Không lưu được {score_l}. Hãy thử lại.",
    "en": "Couldn't save the {score_pl}. Try again."
  },
  "error_reading_club_roster": {
    "vi": "Không tải được danh sách thành viên của {slot_l}. Hãy thử lại.",
    "en": "Couldn't load the {slot_l}'s member list. Try again."
  },
  "error_reading_pref_distribution": {
    "vi": "Không tải được thống kê nguyện vọng. Hãy thử lại.",
    "en": "Couldn't load the preference summary. Try again."
  },
  "error_reading_unplaced": {
    "vi": "Không tải được danh sách {person_l} chưa có chỗ. Hãy thử lại.",
    "en": "Couldn't load the list of unplaced {person_pl}. Try again."
  },
  "error_reading_reserve_usage": {
    "vi": "Không tải được thống kê suất ưu tiên. Hãy thử lại.",
    "en": "Couldn't load the priority seat summary. Try again."
  },
  "error_reading_results": {
    "vi": "Không tải được kết quả. Hãy thử lại.",
    "en": "Couldn't load the results. Try again."
  },
  "error_detecting_csv_kind": {
    "vi": "Không nhận ra được đây là tệp gì. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't tell what kind of file this is. Check the file and try again."
  },
  "error_importing_csv_auto": {
    "vi": "Không nạp được tệp này. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import this file. Check the file and try again."
  },
  "error_importing_clubs_csv": {
    "vi": "Không nạp được tệp danh sách {slot_sl}. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the {slot_l} list file. Check the file and try again."
  },
  "csv_kind_ambiguous": {
    "vi": "Chưa rõ đây là tệp chọn {slot_sl} dự thi hay tệp xếp hạng nguyện vọng (các cột: {fieldnames}). Hãy chọn loại tệp, hoặc thêm cột rank nếu đây là tệp nguyện vọng.",
    "en": "Couldn't tell whether this is a test {slot_l} file or a preferences file (columns: {fieldnames}). Choose the file type, or add a rank column if it holds preferences."
  },
  "csv_kind_unknown": {
    "vi": "Không nhận ra định dạng của tệp này. Xem các cột được hỗ trợ trong mau_csv/HUONG_DAN_CSV.md.",
    "en": "This file format isn't recognised. See the supported columns in mau_csv/HUONG_DAN_CSV.md."
  },
  "csv_club_row_invalid": {
    "vi": "Dòng {line} bị bỏ qua vì {reason} không hợp lệ. Chỉ tiêu phải lớn hơn 0 và suất ưu tiên không được nhiều hơn chỉ tiêu.",
    "en": "Line {line} was skipped because {reason} isn't valid. Quota must be above 0, and priority seats can't be more than quota."
  },
  "xlsx_read_failed": {
    "vi": "Không mở được tệp Excel này. Kiểm tra tệp có đúng định dạng .xlsx không, hoặc lưu lại tệp rồi thử lần nữa.",
    "en": "Couldn't open this Excel file. Check that it's an .xlsx file, or save it again and retry."
  },
  "file_too_large": {
    "vi": "Tệp quá lớn ({size_mb} MB, tối đa {max_mb} MB). Tệp danh sách của một trường không lớn cỡ này. Hãy kiểm tra xem có chọn nhầm tệp không.",
    "en": "The file is too large ({size_mb} MB, maximum {max_mb} MB). A school's list is never this big. Check that the right file was chosen."
  },
  "xlsx_empty": {
    "vi": "Tệp Excel này không có dữ liệu.",
    "en": "This Excel file has no data."
  },
  "xlsx_support_missing": {
    "vi": "Bản cài này không mở được tệp Excel. Hãy lưu tệp ở dạng CSV UTF-8 rồi nạp lại.",
    "en": "This version can't open Excel files. Save the file as CSV UTF-8 and import it again."
  },
  "csv_reserve_group_unknown": {
    "vi": "Nhóm ưu tiên {reserve_group} không khớp với {slot_l} nào, nên {n} {person_l} mang nhãn này sẽ không được xét suất ưu tiên. Có thể nhãn đúng là {goi_y}.",
    "en": "The priority group {reserve_group} doesn't match any {slot_l}, so {n} {person_l}(s) with this label won't be considered for priority seats. The intended label may be {goi_y}."
  },
  "csv_duplicate_student_rows": {
    "vi": "Mã {student_id} có ở {n} dòng trong tệp. Chỉ dòng cuối cùng được giữ.",
    "en": "{person} {student_id} appears on {n} rows. Only the last row was kept."
  },
  "csv_score_not_a_number": {
    "vi": "{score} “{diem_goc}” của {person_l} {student_id} ở {slot_sl} {club_id} không phải là số nên chưa được lưu. Các lựa chọn dự thi vẫn được giữ. Sửa {score_l} rồi nạp lại tệp.",
    "en": "The {score_l} “{diem_goc}” for {person_l} {student_id} in {slot_l} {club_id} isn't a number, so it wasn't saved. The test {slot_l} choices were kept. Fix the {score_l} and import the file again."
  },
  "csv_score_ignored_mode": {
    "vi": "Không gian làm việc này không dùng {score_l} theo từng {slot_l} (chấm theo {person_l}, hoặc chỉ xét nhóm): {n} ô {score_l} trong tệp đã được bỏ qua, không lưu.",
    "en": "This workspace doesn't use a {score_l} per {slot_l} (it scores per {person_l}, or ranks by group only): {n} {score_l} cell(s) in the file were skipped and not saved."
  },
  "csv_score_negative": {
    "vi": "{score} “{diem_goc}” của {person_l} {student_id} ở {slot_sl} {club_id} là số âm, có thể do gõ thừa dấu trừ. {score} này chưa được lưu.",
    "en": "The {score_l} “{diem_goc}” for {person_l} {student_id} in {slot_l} {club_id} is negative, probably an extra minus sign. This {score_l} wasn't saved."
  },
  "csv_score_for_unselected_club": {
    "vi": "{person} {student_id} có {score_l} ở {slot_sl} {club_id} nhưng không đăng ký dự thi {slot_sl} này, nên {score_l} chưa được lưu. Kiểm tra xem mã {slot_sl} có bị gõ nhầm không.",
    "en": "{person} {student_id} has a {score_l} for {slot_l} {club_id} but didn't sign up to test for it, so the {score_l} wasn't saved. Check the {slot_l} code for typos."
  },
  "thu_muc_khong_hop_le": {
    "vi": "Không mở được thư mục \"{path}\". Chỉ mở được thư mục chứa tệp phần mềm vừa xuất.",
    "en": "Cannot open the folder \"{path}\". Only folders holding files this app exported can be opened."
  },
  "thu_muc_khong_mo_duoc": {
    "vi": "Máy không mở được thư mục. Hãy mở thủ công theo đường dẫn hiện trên màn hình.",
    "en": "The computer could not open the folder. Open it by hand using the path shown on screen."
  },
  "chua_chon_hoc_sinh": {
    "vi": "Chưa chọn {person_l} nào để xuất. Hãy đánh dấu ít nhất một {person_l}.",
    "en": "No {person_pl} selected to export. Tick at least one {person_l}."
  },
  "chua_co_lan_chay_truoc": {
    "vi": "Chưa có lần chạy trước để so sánh. Cần chạy sắp xếp ít nhất hai lần.",
    "en": "There is no previous run to compare with. Run the allocation at least twice."
  },
  "csv_score_removed_unselected": {
    "vi": "{person} {student_id}: tệp mới không còn {n} {slot_sl} đã có {score_l} chấm. {person} được coi như rút khỏi bài thi đó, nên {n} {score_l} cũ đã bị xoá theo.",
    "en": "{person} {student_id}: the new file no longer lists {n} {slot_l}(s) that already had a {score_l}. The {person_l} is treated as withdrawn from that test, so the {n} old {score_l}(s) were deleted."
  },
  "csv_score_without_club": {
    "vi": "{person} {student_id} có {score_l} ở ô {score_l} số {cot} nhưng ô mã {slot_sl} bên cạnh để trống, có thể do lệch cột. {score} này chưa được lưu.",
    "en": "{person} {student_id} has a {score_l} in {score_l} column {cot} but the {slot_l} column next to it is empty, probably a shifted column. This {score_l} wasn't saved."
  },
  "csv_scores_ignored_here": {
    "vi": "Tệp xếp hạng nguyện vọng không dùng để nạp {score_l}, nên các cột {score_l} trong tệp này được bỏ qua. Hãy đưa {score_l} vào tệp chọn {slot_sl} dự thi.",
    "en": "{score_p} can't be imported from a preferences file, so the {score_l} columns here were ignored. Put the {score_pl} in the test {slot_l} file instead."
  },
  "csv_student_id_case_conflict": {
    "vi": "Mã {student_id} và mã {da_co} chỉ khác nhau ở chữ hoa, chữ thường nên đang được tính là hai {person_l}. Nếu là cùng một {person_l}, hãy viết mã giống nhau ở cả hai tệp.",
    "en": "The codes {student_id} and {da_co} differ only in upper and lower case, so they count as two {person_pl}. If both codes belong to one {person_l}, write the code the same way in both files."
  },
  "csv_student_id_maybe_truncated": {
    "vi": "Mã {student_id} có {do_dai} chữ số, trong khi phần lớn mã khác có {do_dai_pho_bien}. Có thể Excel đã bỏ số 0 ở đầu. Mở tệp gốc, đặt cột mã ở dạng Text rồi nạp lại.",
    "en": "The code {student_id} has {do_dai} digits while most codes have {do_dai_pho_bien}. Excel may have removed a leading zero. Open the original file, set the code column to Text, and import again."
  },
  "error_reading_club_stats": {
    "vi": "Không tải được thống kê {slot_l}. Hãy thử lại.",
    "en": "Couldn't load the {slot_l} summary. Try again."
  },
  "error_exporting_csv": {
    "vi": "Không xuất được tệp kết quả. Kiểm tra thư mục lưu còn chỗ trống và tệp cũ không đang mở, rồi thử lại.",
    "en": "Couldn't export the results. Check that the folder has free space and the old file isn't open, then try again."
  },
  "error_exporting_excel": {
    "vi": "Không ghi được tệp Excel kết quả. Đóng tệp cũ nếu đang mở trong Excel, kiểm tra thư mục lưu còn chỗ trống, rồi thử lại.",
    "en": "Couldn't write the results Excel file. Close the old file if it's open in Excel, check that the folder has free space, then try again."
  },
  "error_saving_club": {
    "vi": "Không lưu được {slot_l}. Hãy thử lại.",
    "en": "Couldn't save the {slot_l}. Try again."
  },
  "error_deleting_club": {
    "vi": "Không xoá được {slot_l}. Hãy thử lại.",
    "en": "Couldn't delete the {slot_l}. Try again."
  },
  "error_reading_reserve_groups": {
    "vi": "Không tải được danh sách nhóm ưu tiên. Hãy thử lại.",
    "en": "Couldn't load the priority groups. Try again."
  },
  "error_assigning_reserve_group": {
    "vi": "Không gán được nhóm ưu tiên. Hãy thử lại.",
    "en": "Couldn't assign the priority group. Try again."
  },
  "error_bulk_assigning": {
    "vi": "Không gán được nhãn cho các {person_l} đã chọn. Hãy thử lại.",
    "en": "Couldn't assign the label to the selected {person_pl}. Try again."
  },
  "error_reading_student_list": {
    "vi": "Không tải được danh sách {person_l}. Hãy thử lại.",
    "en": "Couldn't load the {person_l} list. Try again."
  },
  "error_reading_club_list": {
    "vi": "Không tải được danh sách {slot_l}. Hãy thử lại.",
    "en": "Couldn't load the {slot_l} list. Try again."
  },
  "error_searching_students": {
    "vi": "Không tìm được {person_l} lúc này. Hãy thử lại.",
    "en": "Couldn't search for {person_pl} right now. Try again."
  },
  "error_reading_student_state": {
    "vi": "Không tải được thông tin của {person_l} này. Hãy thử lại.",
    "en": "Couldn't load this {person_l}'s details. Try again."
  },
  "error_saving_test_selection": {
    "vi": "Không lưu được lựa chọn {slot_sl} dự thi. Hãy thử lại.",
    "en": "Couldn't save the test {slot_l} choices. Try again."
  },
  "error_saving_preferences": {
    "vi": "Không lưu được nguyện vọng. Hãy thử lại.",
    "en": "Couldn't save the preferences. Try again."
  },
  "lop_sai_kieu": {
    "vi": "{cohort} phải là chữ hoặc số.",
    "en": "The {cohort_l} must be text or a number."
  },
  "lop_qua_dai": {
    "vi": "Tên {cohort_l} quá dài (tối đa {toi_da} ký tự).",
    "en": "The {cohort_l} name is too long (at most {toi_da} characters)."
  },
  "canh_bao_lop_bi_cat": {
    "vi": "{n} tên {cohort_l} dài quá {toi_da_cat} ký tự nên đã bị cắt bớt. Kiểm lại tên {cohort_l} trong tệp.",
    "en": "{n} {cohort_l} name(s) were longer than {toi_da_cat} characters and were shortened. Check the {cohort_l} names in the file."
  },
  "nhan_trung_danh_tu": {
    "vi": "Hai mục trong bước Từ vựng đang cùng tên \"{nhan}\". Hãy đặt tên khác nhau cho từng mục, nếu không Sổ nhập sẽ đọc nhầm cột.",
    "en": "Two items in the vocabulary step have the same name \"{nhan}\". Give each item its own name, otherwise the entry workbook would read the wrong column."
  },
  "so_nhap_canh_bao_nhan_trung": {
    "vi": "Cấu hình đang lưu có hai mục cùng tên \"{nhan}\" ({a} và {b}). Phần mềm đọc cột theo thứ tự trong Sổ; nên đặt lại để hai mục có tên khác nhau.",
    "en": "The saved settings give two items the same name \"{nhan}\" ({a} and {b}). Columns are read in workbook order; rename them so the two items differ."
  },
  "error_saving_student_class": {
    "vi": "Không lưu được {cohort_l} của {person_l}. Hãy thử lại.",
    "en": "Couldn't save the {cohort_l} of the {person_l}. Try again."
  },
  "error_reading_classes": {
    "vi": "Không đọc được danh sách {cohort_l}. Hãy thử lại.",
    "en": "Couldn't load the list of {cohort_pl}. Try again."
  },
  "lop_khong_co_trong_danh_sach": {
    "vi": "{cohort} {class_id} chưa có trong danh sách {cohort_l}. Hãy chọn một {cohort_l} đã có.",
    "en": "{cohort} {class_id} isn't in the list. Choose an existing {cohort_l}."
  },
  "so_nhap_canh_bao_thieu_lop": {
    "vi": "{n} {person_l} chưa có {cohort_l} trong Sổ nhập (ô để trống). {cohort} cũ của những {person_l} này được giữ nguyên.",
    "en": "{n} {person_pl} have no {cohort_l} in the workbook (blank cell). Their existing {cohort_l} is kept."
  },
  "error_creating_student": {
    "vi": "Không tạo được {person_l} mới. Hãy thử lại.",
    "en": "Couldn't add the new {person_l}. Try again."
  },
  "error_resetting_student_entry": {
    "vi": "Không xoá được lựa chọn của {person_l} này. Hãy thử lại.",
    "en": "Couldn't clear this {person_l}'s choices. Try again."
  },
  "error_deleting_student": {
    "vi": "Không xoá được {person_l}. Hãy thử lại.",
    "en": "Couldn't delete the {person_l}. Try again."
  },
  "reset_confirmation_mismatch": {
    "vi": "Chưa xoá dữ liệu nào vì thiếu bước xác nhận. Hãy bấm nút xoá thêm một lần để xác nhận.",
    "en": "Nothing was deleted because the confirmation step was missing. Click the delete button once more to confirm."
  },
  "reset_scope_unknown": {
    "vi": "Chưa xoá dữ liệu nào vì yêu cầu xoá không hợp lệ. Hãy dùng các nút xoá trong ứng dụng.",
    "en": "Nothing was deleted because the request wasn't valid. Use the delete buttons in the app."
  },
  "error_resetting_data": {
    "vi": "Không xoá được dữ liệu. Nếu bản sao lưu đã được tạo, bản đó vẫn nằm trong thư mục dữ liệu.",
    "en": "Couldn't delete the data. If a backup was made, it's still in the data folder."
  },
  "csv_empty": {
    "vi": "Tệp này trống hoặc không có dòng nào đọc được.",
    "en": "This file is empty, or none of its rows could be read."
  },
  "csv_missing_columns": {
    "vi": "Tệp dạng dọc cần có cột mã {person_l} và cột mã {slot_sl} (tên cột \"student_id\" và \"club_id\"). Các cột đang có: {fieldnames}",
    "en": "A long-format file needs {person_la} code column and {slot_la} code column (named \"student_id\" and \"club_id\"). Columns found: {fieldnames}"
  },
  "capacity_must_be_positive": {
    "vi": "Chỉ tiêu phải lớn hơn 0.",
    "en": "Quota must be more than 0."
  },
  "no_data_to_run": {
    "vi": "Chưa có dữ liệu để sắp xếp. Cần ít nhất một {slot_l} và một {person_l}.",
    "en": "There's no data to allocate yet. Add at least one {slot_l} and one {person_l}."
  },
  "clb_thieu_buoi": {
    "vi": "Có {n} {slot_l} chưa có {session_l} sinh hoạt: {club_ids}. Các {slot_l} này sẽ bị tính chung một {session_l}, nên mỗi {person_l} chỉ vào được một trong số đó. Hãy điền {session_l} cho tất cả {slot_l}, hoặc để trống cột {session_l} ở tất cả.",
    "en": "{n} {slot_l}(s) have no {session_l}: {club_ids}. These {slot_pl} will be treated as one {session_l}, so {person_la} can join only one of them. Fill in {session_la} for every {slot_l}, or leave the {session_l} column empty for all of them."
  },
  "buoi_khong_ton_tai": {
    "vi": "Không có {session_l} sinh hoạt nào tên “{buoi}”. Các {session_l} hiện có: {dang_co}.",
    "en": "There's no {session_l} called “{buoi}”. Current {session_pl}: {dang_co}."
  },
  "chua_chon_buoi_nao": {
    "vi": "Chưa chọn {session_l} nào để sắp xếp. Hãy chọn ít nhất một {session_l}.",
    "en": "No {session_l} is selected. Choose at least one {session_l}."
  },
  "khong_ve_lai_tham_khi_chay_mot_phan": {
    "vi": "Không thể bốc thăm lại khi chỉ sắp xếp một số {session_l}, vì bốc thăm lại sẽ đổi thứ tự của cả những {session_l} đang giữ kết quả cũ. Muốn bốc thăm lại, hãy chọn tất cả các {session_l}.",
    "en": "The lottery can't be redrawn when only some {session_pl} are allocated, because a redraw also changes the order of the {session_pl} that keep their results. To redraw, select every {session_l}."
  },
  "khong_chen_tham_khi_chay_mot_phan": {
    "vi": "Có {n} {person_l} chưa có số bốc thăm. Cấp số mới sẽ đổi thứ tự của mọi {session_l}, kể cả những {session_l} đang giữ kết quả cũ. Hãy chọn tất cả các {session_l} rồi sắp xếp một lần cho cả tuần.",
    "en": "{n} {person_l}(s) don't have a lottery number yet. Adding them changes the order of every {session_l}, including those keeping their results. Select every {session_l} and allocate the whole week at once."
  },
  "khong_doi_hat_giong_khi_chay_mot_phan": {
    "vi": "Lần sắp xếp trước dùng số khởi tạo bốc thăm {cu}, lần này là {moi}. Đổi số này sẽ đổi thứ tự của mọi {session_l}, kể cả những {session_l} đang giữ kết quả cũ. Hãy đặt lại số {cu}, hoặc chọn tất cả các {session_l} và sắp xếp một lần cho cả tuần.",
    "en": "The last allocation used lottery starting number {cu}; this one uses {moi}. Changing it changes the order of every {session_l}, including those keeping their results. Set it back to {cu}, or select every {session_l} and allocate the whole week at once."
  },
  "hat_giong_da_khoa": {
    "vi": "Số khởi tạo bốc thăm đã khoá ở {cu} cùng bộ số bốc thăm, nhưng lần này lại là {moi}. Đổi số khởi tạo là đổi thứ tự ưu tiên của từng {session_l}, tức là đổi kết quả đã công bố, giống như bốc thăm lại. Hãy đặt lại số khởi tạo là {cu}. Muốn dùng số mới thì bấm \"Bốc thăm lại…\" rồi chạy lại.",
    "en": "The lottery starting number is locked at {cu} together with the lottery numbers, but this run uses {moi}. Changing it changes each {session_l}'s priority order and so the published results, just like redrawing the lottery. Set it back to {cu}. To use a new number, click \"Redraw lottery…\" and run again."
  },
  "nguyen_vong_lech_buoi": {
    "vi": "Dòng {line}: {person_l} {student_id} xếp {slot_sl} {club_id} vào cột {session_l} {buoi_cot}, nhưng {slot_sl} này sinh hoạt {session_l} {buoi_that}. Nguyện vọng này được bỏ qua.",
    "en": "Row {line}: {person_l} {student_id} put {slot_l} {club_id} under {buoi_cot}, but the {slot_l} meets on {buoi_that}. This preference was skipped."
  },
  "reserve_capacity_negative": {
    "vi": "Suất ưu tiên không được là số âm",
    "en": "Priority seats cannot be negative"
  },
  "reserve_capacity_exceeds_capacity": {
    "vi": "Suất ưu tiên không được nhiều hơn chỉ tiêu.",
    "en": "Priority seats can't be more than quota."
  },
  "club_id_required": {
    "vi": "Hãy nhập mã {slot_sl}.",
    "en": "Enter {slot_la} code."
  },
  "student_id_required": {
    "vi": "Hãy nhập mã {person_l}.",
    "en": "Enter the {person_l} ID."
  },
  "cannot_delete_club_referenced": {
    "vi": "Không xoá được {slot_sl} {club_id} vì {slot_sl} này đang có trong {n_prefs} nguyện vọng và {n_matches} kết quả. Hãy xử lý các dữ liệu đó trước.",
    "en": "{slot} {club_id} can't be deleted because it's still in {n_prefs} preference(s) and {n_matches} result(s). Deal with that data first."
  },
  "student_not_found": {
    "vi": "Không tìm thấy {person_l} {student_id}.",
    "en": "{person} {student_id} wasn't found."
  },
  "gioi_han_gv_sai": {
    "vi": "Giới hạn chỉ tiêu phải là số nguyên dương (nhận {value}).",
    "en": "The capacity limit must be a positive whole number (got {value})."
  },
  "club_not_found": {
    "vi": "Không tìm thấy {slot_sl} {club_id}.",
    "en": "{slot} {club_id} wasn't found."
  },
  "unknown_clubs": {
    "vi": "Không tìm thấy các {slot_sl}: {club_ids}.",
    "en": "These {slot_pl} weren't found: {club_ids}."
  },
  "scores_must_be_nonempty_list": {
    "vi": "Chưa có {score_l} nào để lưu.",
    "en": "There are no {score_pl} to save."
  },
  "student_ids_must_be_nonempty_list": {
    "vi": "Chưa chọn {person_l} nào.",
    "en": "No {person_pl} are selected."
  },
  "club_ids_must_be_list": {
    "vi": "Danh sách {slot_sl} không hợp lệ. Hãy thử lại.",
    "en": "The {slot_l} list isn't valid. Try again."
  },
  "ordered_club_ids_must_be_list": {
    "vi": "Danh sách nguyện vọng không hợp lệ. Hãy thử lại.",
    "en": "The preference list isn't valid. Try again."
  },
  "must_rank_at_least_one": {
    "vi": "Hãy chọn ít nhất một nguyện vọng.",
    "en": "Choose at least one preference."
  },
  "max_pref_moi_buoi": {
    "vi": "{session} {buoi} đã đủ {tran} nguyện vọng. Muốn thêm, hãy bỏ bớt một {slot_sl} của {session_l} này.",
    "en": "{buoi} already has {tran} preferences, the most allowed. To add another, remove one from this {session_l}."
  },
  "max_thi_moi_buoi": {
    "vi": "{session} {buoi} đã đủ {tran} {slot_sl} dự thi. Muốn thêm, hãy bỏ bớt một {slot_sl} của {session_l} này.",
    "en": "{buoi} already has {tran} test {slot_pl}, the most allowed. To add another, remove one from this {session_l}."
  },
  "duplicate_preference_in_list": {
    "vi": "{slot_s} này đã có trong danh sách nguyện vọng.",
    "en": "This {slot_l} is already in the preference list."
  },
  "cannot_delete_student_matched": {
    "vi": "Không xoá được {person_l} {student_id} vì {person_l} này có trong kết quả sắp xếp gần nhất. Hãy xử lý xong rồi sắp xếp lại.",
    "en": "{person} {student_id} can't be deleted because the {person_l} is in the latest results. Sort that out, then run the allocation again."
  },
  "stb_redrawn_and_locked": {
    "vi": "Đã bốc thăm cho {n} {person_l} và khoá kết quả bốc thăm.",
    "en": "Drew lottery numbers for {n} {person_l}(s) and locked them."
  },
  "stb_supplemented": {
    "vi": "Số bốc thăm đã khoá. Thứ tự cũ được giữ nguyên, {n} {person_l} mới được xếp ngẫu nhiên vào.",
    "en": "Lottery numbers were already locked. The existing order was kept and {n} new {person_l}(s) were added at random."
  },
  "stb_reused": {
    "vi": "Số bốc thăm đã khoá nên được dùng lại, không bốc thăm mới.",
    "en": "Lottery numbers were already locked, so they were reused."
  },
  "rbda_done": {
    "vi": "Hoàn tất sau {rounds} vòng, không có lỗi.",
    "en": "Finished in {rounds} round(s) with no errors."
  },
  "db_backed_up": {
    "vi": "Đã sao lưu dữ liệu trước khi sắp xếp: {backup_name}",
    "en": "Backed up the data before allocating: {backup_name}"
  },
  "db_backup_failed": {
    "vi": "Không sao lưu được dữ liệu. Việc sắp xếp vẫn tiếp tục.",
    "en": "Couldn't back up the data. The allocation continued anyway."
  },
  "pipeline_rolled_back": {
    "vi": "Sắp xếp bị dừng giữa chừng nên mọi thay đổi của lần này đã được huỷ, kể cả số bốc thăm mới. Dữ liệu giữ nguyên như trước khi bấm chạy.",
    "en": "The allocation stopped partway, so every change from this run was undone, including new lottery numbers. The data is the same as before the run."
  },
  "pref_student_not_in_students": {
    "vi": "Mã {student_id} có nguyện vọng nhưng không có trong danh sách {person_l}.",
    "en": "Code {student_id} has preferences but isn't in the {person_l} list."
  },
  "pref_duplicate_club": {
    "vi": "{person} {student_id} có một {slot_sl} bị lặp trong danh sách nguyện vọng.",
    "en": "{person} {student_id} has the same {slot_l} twice in the preference list."
  },
  "pref_too_many": {
    "vi": "{person} {student_id} có {count} nguyện vọng, nhiều hơn mức tối đa {tran}.",
    "en": "{person} {student_id} has {count} preferences. The most allowed is {tran}."
  },
  "pref_too_many_buoi": {
    "vi": "{person} {student_id} có {count} nguyện vọng ở {session_l} {buoi}, nhiều hơn mức tối đa {tran} mỗi {session_l}.",
    "en": "{person} {student_id} has {count} preferences in {buoi}. The most allowed is {tran} per {session_l}."
  },
  "thi_too_many": {
    "vi": "{person} {student_id} đăng ký dự thi {count} {slot_sl}, nhiều hơn mức tối đa {tran}.",
    "en": "{person} {student_id} signed up to test for {count} {slot_pl}. The most allowed is {tran}."
  },
  "thi_too_many_buoi": {
    "vi": "{person} {student_id} đăng ký dự thi {count} {slot_sl} ở {session_l} {buoi}, nhiều hơn mức tối đa {tran} mỗi {session_l}.",
    "en": "{person} {student_id} signed up to test for {count} {slot_pl} in {buoi}. The most allowed is {tran} per {session_l}."
  },
  "pref_unknown_club": {
    "vi": "{person} {student_id} có nguyện vọng vào {slot_sl} {club_id}, nhưng không tìm thấy {slot_sl} này.",
    "en": "{person} {student_id} chose {slot_l} {club_id}, but that {slot_l} wasn't found."
  },
  "club_capacity_not_positive": {
    "vi": "{slot_s} {club_id} có chỉ tiêu bằng 0. Chỉ tiêu phải lớn hơn 0.",
    "en": "{slot} {club_id} has 0 seats. Quota must be more than 0."
  },
  "club_reserve_negative": {
    "vi": "{slot_s} {club_id} có số suất ưu tiên âm. Số này phải từ 0 trở lên.",
    "en": "{slot} {club_id} has a negative number of priority seats. It must be 0 or more."
  },
  "club_reserve_exceeds_capacity": {
    "vi": "{slot_s} {club_id} có suất ưu tiên nhiều hơn chỉ tiêu.",
    "en": "{slot} {club_id} has more priority seats than quota."
  },
  "applicants_unknown_club": {
    "vi": "Danh sách dự thi có {slot_sl} {club_id}, nhưng không tìm thấy {slot_sl} này.",
    "en": "The test list includes {slot_l} {club_id}, but that {slot_l} wasn't found."
  },
  "applicants_unknown_student": {
    "vi": "Danh sách dự thi có mã {student_id}, nhưng không tìm thấy {person_l} này.",
    "en": "The test list includes {person_l} {student_id}, but that {person_l} wasn't found."
  },
  "assignment_not_in_preferences": {
    "vi": "{person} {student_id} được xếp vào {slot_sl} {club_id} dù {slot_sl} này không có trong nguyện vọng.",
    "en": "{person} {student_id} was placed in {slot_l} {club_id}, which isn't among the {person_l}'s preferences."
  },
  "club_over_capacity": {
    "vi": "{slot_s} {club_id} có {count} {person_l} nhưng chỉ có {capacity} chỗ.",
    "en": "{slot} {club_id} has {count} {person_l}(s) but only {capacity} seat(s)."
  },
  "club_over_reserve_capacity": {
    "vi": "{slot_s} {club_id} có {count} {person_l} dùng suất ưu tiên nhưng chỉ có {reserve_capacity} suất.",
    "en": "{slot} {club_id} has {count} {person_l}(s) in priority seats but only {reserve_capacity} priority seat(s)."
  },
  "blocking_pair": {
    "vi": "Có thể chưa công bằng: {person_l} {student_id} thích {slot_sl} {club_id} hơn {slot_sl} đang được xếp ({current_club}) và đủ điều kiện vào {club_id}. {slot_s} {club_id} hiện đã nhận {n_holders}/{capacity} chỗ.",
    "en": "Possible unfair result: {person_l} {student_id} prefers {slot_l} {club_id} to the assigned {slot_l} ({current_club}) and qualifies for {club_id}. {slot} {club_id} has filled {n_holders}/{capacity} seats."
  },
  "wharton_nguyen_vong_chua_xep": {
    "vi": "Nguyện vọng chưa được sắp xếp xong. {person} {student_id} cần từ 1 đến {tran} {slot_sl} mỗi {session_l}, không trùng nhau (hiện có {n}, trùng {n_trung}).",
    "en": "Preferences aren't complete yet. {person} {student_id} needs 1 to {tran} {slot_pl} per {session_l}, with no repeats (now {n}, repeated {n_trung})."
  },
  "wharton_chua_dung_het": {
    "vi": "Chưa dùng hết điểm quyết tâm: {person_l} {student_id} còn thiếu {thieu} điểm ở quỹ {quy}.",
    "en": "Commitment points not fully used: {person_l} {student_id} still has {thieu} point(s) left in fund {quy}."
  },
  "wharton_vuot_ngan_sach": {
    "vi": "{person} {student_id} đặt {tong} điểm quyết tâm ở quỹ {quy}, nhiều hơn {ngan_sach} điểm được phép.",
    "en": "{person} {student_id} placed {tong} commitment points in fund {quy}, more than the {ngan_sach} allowed."
  },
  "wharton_diem_khong_hop_le": {
    "vi": "{person} {student_id} đặt “{gia_tri}” điểm quyết tâm cho {slot_sl} {club_id}. Điểm quyết tâm phải là số nguyên từ 0 trở lên.",
    "en": "{person} {student_id} placed “{gia_tri}” commitment points on {slot_l} {club_id}. Commitment points must be a whole number of 0 or more."
  },
  "wharton_ngoai_tap": {
    "vi": "{person} {student_id} đặt điểm quyết tâm quỹ {quy} cho {slot_sl} {club_id}, nhưng {slot_sl} này không thuộc quỹ {quy} (không có trong nguyện vọng, hoặc sai loại có thi / không thi).",
    "en": "{person} {student_id} placed fund {quy} commitment points on {slot_l} {club_id}, but that {slot_l} isn't in fund {quy} (not in the preferences, or the wrong tested / not-tested group)."
  },
  "wharton_tang_lech": {
    "vi": "{person} {student_id} có {score_l} thi ở {slot_sl} {club_id} nhưng chỉ đặt điểm quyết tâm cho {slot_sl} này ở quỹ không thi. Cần chia lại điểm.",
    "en": "{person} {student_id} has a test {score_l} for {slot_l} {club_id} but placed commitment points for it only in the not-tested fund. The points need to be split again."
  },
  "wharton_vang_thi": {
    "vi": "{person} {student_id} vắng thi {slot_sl} {club_id}, nên được xét như không thi với {diem} điểm quyết tâm quỹ 2 ({diem_bo} điểm quỹ 1 không được tính).",
    "en": "{person} {student_id} missed the test for {slot_l} {club_id}, so is ranked as not tested with {diem} fund 2 commitment point(s) ({diem_bo} fund 1 point(s) not counted)."
  },
  "csv_wp_khong_hop_le": {
    "vi": "Điểm quyết tâm của {person_l} {student_id} ở {slot_sl} {club_id} là “{gia_tri}”, không phải số nguyên từ 0 trở lên. Ô này chưa được lưu.",
    "en": "The commitment points for {person_l} {student_id} on {slot_l} {club_id} are “{gia_tri}”, not a whole number of 0 or more. This cell wasn't saved."
  },
  "csv_wp_khong_co_nguyen_vong": {
    "vi": "{student_id}: có điểm quyết tâm ở cột {cot} nhưng ô nguyện vọng cạnh đó để trống. Điểm này chưa được lưu.",
    "en": "{student_id}: there are commitment points in column {cot} but the preference cell next to it is empty. Those points weren't saved."
  },
  "fa_loai_sai": {
    "vi": "Loại CLB \"{loai}\" không hợp lệ. Chỉ nhận Tự do, Giới hạn hoặc Tuyển chọn.",
    "en": "Club type \"{loai}\" isn't valid. Use Free, Limited or Selective."
  },
  "fa_diem_san_sai": {
    "vi": "Điểm sàn \"{diem_san}\" không hợp lệ: phải là số nguyên từ 0 đến 10.",
    "en": "Pass mark \"{diem_san}\" isn't valid: it must be a whole number from 0 to 10."
  },
  "fa_toi_thieu_sai": {
    "vi": "Số thành viên tối thiểu \"{so_toi_thieu}\" không hợp lệ: phải là số nguyên từ 0 trở lên.",
    "en": "Minimum members \"{so_toi_thieu}\" isn't valid: it must be a whole number, 0 or more."
  },
  "fa_suc_chua_phong_sai": {
    "vi": "Sức chứa phòng \"{suc_chua_phong}\" không hợp lệ: phải là số nguyên lớn hơn 0.",
    "en": "Room capacity \"{suc_chua_phong}\" isn't valid: it must be a whole number above 0."
  },
  "so_nhap_fa_loai_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Loại \"{gia_tri}\" không hợp lệ. Chỉ nhận Tự do, Giới hạn hoặc Tuyển chọn.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): type \"{gia_tri}\" isn't valid. Use Free, Limited or Selective."
  },
  "so_nhap_fa_diem_san_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Điểm sàn \"{gia_tri}\" phải là số nguyên từ 0 đến 10.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): pass mark \"{gia_tri}\" must be a whole number from 0 to 10."
  },
  "so_nhap_fa_toi_thieu_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Tối thiểu \"{gia_tri}\" phải là số nguyên từ 0 trở lên.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): minimum \"{gia_tri}\" must be a whole number, 0 or more."
  },
  "so_nhap_fa_suc_chua_phong_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Sức chứa phòng \"{gia_tri}\" phải là số nguyên lớn hơn 0.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): room capacity \"{gia_tri}\" must be a whole number above 0."
  },
  "csv_club_fa_invalid": {
    "vi": "Dòng {line} bị bỏ qua vì cột {reason} không hợp lệ (loại CLB, điểm sàn, tối thiểu hoặc sức chứa phòng).",
    "en": "Line {line} was skipped because column {reason} isn't valid (club type, pass mark, minimum or room capacity)."
  },
  "fa_cot_bo_qua": {
    "vi": "Không gian làm việc này chưa bật chế độ FA-DAA: {n} CLB có cột loại / điểm sàn / tối thiểu / sức chứa phòng đã được bỏ qua phần đó, không lưu.",
    "en": "This workspace doesn't use FA-DAA yet: the type / pass mark / minimum / room capacity columns of {n} club(s) were skipped and not saved."
  },
  "fa_giu_cho_bo_qua": {
    "vi": "Không gian làm việc này chưa bật chế độ FA-DAA: {n} dòng giữ chỗ trong sổ đã được bỏ qua, không lưu.",
    "en": "This workspace doesn't use FA-DAA yet: {n} reserved-seat row(s) in the file were skipped and not saved."
  },
  "so_nhap_fa_giu_cho_khong_ton_tai": {
    "vi": "{n} dòng giữ chỗ bị bỏ qua vì CLB hoặc học sinh không có trong phần mềm (ví dụ: {vi_du}).",
    "en": "{n} reserved-seat row(s) were skipped because the club or student isn't in the app (for example: {vi_du})."
  },
  "fa_thieu_clb_tu_do": {
    "vi": "Buổi \"{buoi}\" chưa có CLB loại Tự do. Mỗi buổi cần ít nhất một CLB Tự do để nhận học sinh chưa có chỗ.",
    "en": "Session \"{buoi}\" has no Free club. Each session needs at least one Free club to take students without a seat."
  },
  "fa_clb_thieu_loai": {
    "vi": "CLB {club_id} chưa có loại (Tự do, Giới hạn hoặc Tuyển chọn).",
    "en": "Club {club_id} has no type yet (Free, Limited or Selective)."
  },
  "fa_clb_thieu_suc_chua": {
    "vi": "CLB {club_id} (Giới hạn hoặc Tuyển chọn) cần chỉ tiêu lớn hơn 0.",
    "en": "Club {club_id} (Limited or Selective) needs a seat count above 0."
  },
  "fa_clb_thieu_diem_san": {
    "vi": "CLB {club_id} (Tuyển chọn) chưa có điểm sàn.",
    "en": "Club {club_id} (Selective) has no pass mark yet."
  },
  "fa_giu_cho_vuot_suc_chua": {
    "vi": "CLB {club_id} giữ chỗ cho {n} học sinh, nhiều hơn chỉ tiêu {suc_chua}.",
    "en": "Club {club_id} reserves seats for {n} students, more than its {suc_chua} seats."
  },
  "fa_giu_cho_hoc_sinh_la": {
    "vi": "Giữ chỗ ở CLB {club_id} cho {student_id} bị bỏ qua vì không có học sinh này.",
    "en": "The reserved seat at club {club_id} for {student_id} was ignored because that student doesn't exist."
  },
  "fa_giu_cho_khong_xep_clb": {
    "vi": "Giữ chỗ ở CLB {club_id} cho {student_id} bị bỏ qua vì học sinh chưa xếp CLB này trong nguyện vọng.",
    "en": "The reserved seat at club {club_id} for {student_id} was ignored because the student didn't rank this club."
  },
  "fa_chua_bat": {
    "vi": "Không gian làm việc này chưa bật chế độ FA-DAA, nên chưa nhận huy chương.",
    "en": "This workspace doesn't use FA-DAA yet, so medals can't be saved."
  },
  "fa_huy_chuong_gia_tri_sai": {
    "vi": "{student_id}: huy chương ở CLB {club_id} có giá trị {gia_tri}; chỉ nhận vàng (60), bạc (30) hoặc đồng (10).",
    "en": "{student_id}: the medal at club {club_id} has value {gia_tri}; only gold (60), silver (30) or bronze (10) are allowed."
  },
  "fa_huy_chuong_trung_gia_tri": {
    "vi": "{student_id}: buổi {buoi} có hai CLB cùng huy chương {gia_tri}. Mỗi loại huy chương chỉ dùng một lần mỗi buổi.",
    "en": "{student_id}: session {buoi} has two clubs with the same medal ({gia_tri}). Each medal can be used once per session."
  },
  "fa_huy_chuong_ngoai_nguyen_vong": {
    "vi": "{student_id}: huy chương đặt ở CLB {club_id} nhưng CLB này không nằm trong nguyện vọng.",
    "en": "{student_id}: a medal is placed on club {club_id} but that club isn't in the student's choices."
  },
  "fa_huy_chuong_clb_tu_do": {
    "vi": "{student_id}: CLB {club_id} là CLB Tự do nên không nhận huy chương.",
    "en": "{student_id}: club {club_id} is a Free club, so it can't take a medal."
  },
  "fa_thieu_clb_tu_do_nhom": {
    "vi": "{n} buổi chưa có CLB loại Tự do (ví dụ: {vd}). Mỗi buổi cần ít nhất một CLB Tự do.",
    "en": "{n} session(s) have no Free club (for example: {vd}). Each session needs at least one Free club."
  },
  "fa_clb_thieu_loai_nhom": {
    "vi": "{n} CLB chưa có Loại (ví dụ: {vd}).",
    "en": "{n} club(s) have no Type yet (for example: {vd})."
  },
  "fa_clb_thieu_suc_chua_nhom": {
    "vi": "{n} CLB Giới hạn hoặc Tuyển chọn cần chỉ tiêu lớn hơn 0 (ví dụ: {vd}).",
    "en": "{n} Limited or Selective club(s) need a seat count above 0 (for example: {vd})."
  },
  "fa_clb_thieu_diem_san_nhom": {
    "vi": "{n} CLB Tuyển chọn chưa có điểm sàn (ví dụ: {vd}).",
    "en": "{n} Selective club(s) have no pass mark yet (for example: {vd})."
  },
  "fa_giu_cho_vuot_suc_chua_nhom": {
    "vi": "{n} CLB giữ chỗ nhiều hơn chỉ tiêu (ví dụ: {vd}).",
    "en": "{n} club(s) reserve more seats than their seat count (for example: {vd})."
  },
  "fa_giu_cho_hoc_sinh_la_nhom": {
    "vi": "{n} dòng giữ chỗ sẽ bị bỏ qua vì không có học sinh đó (ví dụ: {vd}).",
    "en": "{n} reserved-seat row(s) will be ignored because the student doesn't exist (for example: {vd})."
  },
  "fa_giu_cho_khong_xep_clb_nhom": {
    "vi": "{n} dòng giữ chỗ sẽ bị bỏ qua vì học sinh chưa xếp CLB đó trong nguyện vọng (ví dụ: {vd}).",
    "en": "{n} reserved-seat row(s) will be ignored because the student didn't rank that club (for example: {vd})."
  },
  "fa_huy_chuong_gia_tri_sai_nhom": {
    "vi": "{n} ô huy chương không phải 60/30/10 (ví dụ: {vd}).",
    "en": "{n} medal cell(s) are not 60/30/10 (for example: {vd})."
  },
  "fa_huy_chuong_trung_gia_tri_nhom": {
    "vi": "{n} trường hợp một học sinh dùng cùng một huy chương hai lần trong một buổi (ví dụ: {vd}).",
    "en": "{n} case(s) of a student using the same medal twice in one session (for example: {vd})."
  },
  "fa_huy_chuong_ngoai_nguyen_vong_nhom": {
    "vi": "{n} huy chương đặt ở CLB không nằm trong nguyện vọng (ví dụ: {vd}).",
    "en": "{n} medal(s) placed on a club that isn't in the student's choices (for example: {vd})."
  },
  "fa_huy_chuong_clb_tu_do_nhom": {
    "vi": "{n} huy chương đặt ở CLB Tự do, nơi không nhận huy chương (ví dụ: {vd}).",
    "en": "{n} medal(s) placed on a Free club, which takes no medals (for example: {vd})."
  },
  "so_nhap_canh_bao_fa_se_loi": {
    "vi": "Không gian làm việc đang ở chế độ FA-DAA: vẫn nhập được sổ này, nhưng lần chạy xếp sẽ bị chặn cho tới khi sửa xong các mục trên (sửa CLB ở Quản lý, hoặc sửa sổ rồi nhập lại).",
    "en": "This workspace uses FA-DAA: the workbook can still be imported, but the allocation run will be blocked until the items above are fixed (edit clubs in Manage, or fix the workbook and import it again)."
  },
  "fa_diem_bo_qua": {
    "vi": "CLB {club_id} (Giới hạn) không xét điểm thi: {n} điểm thi đã được bỏ qua khi xếp.",
    "en": "Club {club_id} (Limited) doesn't use test scores: {n} score(s) were ignored when allocating."
  },
  "fa_clb_dong_thieu_nguoi": {
    "vi": "CLB {club_id} (buổi {buoi}) đã đóng vì chỉ có {thanh_vien} thành viên, thiếu {thieu} so với mức tối thiểu. Đóng CLB thiếu người là cách xấp xỉ, không bảo đảm khai thật nguyện vọng là tối ưu.",
    "en": "Club {club_id} (session {buoi}) was closed because it had only {thanh_vien} members, {thieu} short of its minimum. Closing under-filled clubs is an approximation and doesn't guarantee that ranking truthfully is optimal."
  },
  "bien_ban_chua_boc_tham": {
    "vi": "Chưa có biên bản bốc thăm vì chưa bốc thăm. Hãy chạy xếp một lần (hạt giống được khoá khi chạy) rồi xuất lại.",
    "en": "There is no lottery record yet because no draw has happened. Run the allocation once (the draw is locked when it runs) and export again."
  },
  "fa_can_diem_quyet_tam": {
    "vi": "Chưa bật được xếp theo loại CLB và huy chương vì điểm quyết tâm đang tắt. Huy chương dùng chung bảng điểm quyết tâm: hãy bật điểm quyết tâm (cần ưu tiên theo điểm thi và điểm tính riêng từng CLB) rồi thử lại.",
    "en": "Club-type and medal mode can't be turned on because determination points are off. Medals use the same points table: turn determination points on (this needs score-based priority and per-club scores) and try again."
  },
  "fa_tinh_nang_can_fa": {
    "vi": "Tính năng {khoa} chỉ bật được khi đã bật xếp theo loại {slot_l} và huy chương (FA-DAA). Hãy bật FA-DAA trước.",
    "en": "Feature {khoa} can only be turned on with {slot_l}-type and medal mode (FA-DAA). Turn FA-DAA on first."
  },
  "fa_diem_danh_chua_bat": {
    "vi": "Không gian làm việc này chưa bật điểm danh sau khi xếp.",
    "en": "This workspace doesn't use attendance after allocation."
  },
  "diem_danh_gia_tri_sai": {
    "vi": "Giá trị điểm danh không hợp lệ: chỉ nhận lần sinh hoạt 1, 2, 3 và có mặt, vắng có phép, vắng không phép.",
    "en": "Invalid attendance value: only meetings 1, 2, 3 and present, excused, unexcused are accepted."
  },
  "diem_danh_khong_thuoc_clb": {
    "vi": "{person} {student_id} không thuộc {slot_l} {club_id} nên không điểm danh ở đó được.",
    "en": "{person} {student_id} is not in {slot_l} {club_id}, so attendance can't be recorded there."
  },
  "loi_luu_sau_xep": {
    "vi": "Không lưu được thay đổi sau khi xếp. Hãy thử lại.",
    "en": "Couldn't save the after-allocation change. Try again."
  },
  "fa_vong_2_chua_bat": {
    "vi": "Không gian làm việc này chưa bật vòng 2 sau khi xếp.",
    "en": "This workspace doesn't use a second round after allocation."
  },
  "vong_2_lua_chon_sai": {
    "vi": "Lựa chọn vòng 2 không hợp lệ: {person_l} {student_id} không cần vòng 2, hoặc {slot_l} {club_id} không thuộc buổi này.",
    "en": "Invalid second-round choice: {person} {student_id} doesn't need round 2, or {slot_l} {club_id} isn't in this session."
  },
  "vong_2_da_chay": {
    "vi": "Vòng 2 của buổi này đã chạy rồi (chỉ chạy một lượt).",
    "en": "Round 2 for this session has already run (it runs once)."
  },
  "fa_phan_hoi_chua_bat": {
    "vi": "Không gian làm việc này chưa bật phản hồi của {person_pl}.",
    "en": "This workspace doesn't collect {person} feedback."
  },
  "phan_hoi_gia_tri_sai": {
    "vi": "Câu trả lời phản hồi không hợp lệ: hài lòng từ 1 đến 5, hiểu lý do có hoặc không, và một phần khó nhất trong danh sách.",
    "en": "Invalid feedback answer: satisfaction 1 to 5, understood yes or no, and one hardest part from the list."
  },
  "fa_sau_ket_qua_chua_bat": {
    "vi": "Không gian làm việc này chưa bật nhận phản hồi cũng như khiếu nại sau khi xếp, nên chưa nạp được biểu mẫu Sau khi xem kết quả.",
    "en": "This workspace collects neither feedback nor appeals after allocation, so the after-results form can't be loaded."
  },
  "khieu_nai_khong_co_gio_forms": {
    "vi": "Tệp không có giờ hoàn thành của Forms, nên hạn khiếu nại được tính theo lúc nạp tệp.",
    "en": "The file has no Forms completion time, so the appeal deadline was checked against the time of import."
  },
  "phan_hoi_tep_sai": {
    "vi": "Tệp này không phải tệp xuất của biểu mẫu phản hồi (không thấy cột mã {person_l} và câu hỏi phản hồi).",
    "en": "This file isn't an export of the feedback form (no {person} ID column or feedback question)."
  },
  "phan_hoi_tep_rong": {
    "vi": "Tệp này không có câu trả lời nào (chỉ có hàng tiêu đề hoặc trống). Hãy xuất lại từ biểu mẫu sau khi có người nộp.",
    "en": "This file has no responses (it is empty or only has the header row). Export it again once someone has submitted."
  },
  "fa_khieu_nai_chua_bat": {
    "vi": "Không gian làm việc này chưa bật nhận khiếu nại sau khi xếp.",
    "en": "This workspace doesn't take appeals after allocation."
  },
  "khieu_nai_khong_hop_le": {
    "vi": "Không nhận được khiếu nại: không tìm thấy {person_l} {student_id} hoặc buổi {buoi} chưa có kết quả.",
    "en": "Appeal not accepted: {person} {student_id} not found or session {buoi} has no result yet."
  },
  "khieu_nai_qua_han": {
    "vi": "Đã quá hạn khiếu nại ({so_ngay} ngày từ lúc công bố kết quả).",
    "en": "The appeal window has closed ({so_ngay} days after results were published)."
  },
  "khieu_nai_trung": {
    "vi": "{person} {student_id} đã có một khiếu nại đang chờ xử lý cho buổi này.",
    "en": "{person} {student_id} already has an appeal waiting for this session."
  },
  "khieu_nai_da_xu_ly": {
    "vi": "Khiếu nại này đã được xử lý rồi.",
    "en": "This appeal has already been handled."
  },
  "moi_khong_con_cho": {
    "vi": "Lời mời này không còn chờ trả lời (đã được trả lời, hoặc kết quả xếp của buổi đó đã chạy lại).",
    "en": "This invitation is no longer waiting for an answer (already answered, or that day was re-run)."
  },
  "fa_ly_do_thieu_buoi": {
    "vi": "Buổi {buoi} không có lý do: lần chạy gần nhất của buổi đó không dùng chế độ FA-DAA.",
    "en": "Session {buoi} has no reasons: its latest run did not use FA-DAA mode."
  },
  "fa_chua_co_ly_do": {
    "vi": "Chưa có lý do kết quả. Hãy bật chế độ FA-DAA và chạy xếp trước.",
    "en": "No result reasons yet. Turn on FA-DAA mode and run the allocation first."
  },
  "csv_wp_bo_qua": {
    "vi": "Không gian làm việc này chưa bật điểm quyết tâm: {n} ô điểm quyết tâm trong tệp đã được bỏ qua, không lưu.",
    "en": "This workspace doesn't use commitment points yet: {n} commitment points cell(s) in the file were skipped and not saved."
  },
  "xuat_diem_chuan_loi": {
    "vi": "Không đọc được điểm chuẩn khi xuất: trang \"Điểm chuẩn\" trong tệp đang trống do lỗi. Hãy xuất lại.",
    "en": "The cut-off scores could not be read while exporting: the \"Cut-off scores\" sheet in the file is empty because of the error. Export again."
  },
  "csv_wharton_khoa_giu_nguyen": {
    "vi": "Học sinh {student_id}: điểm quyết tâm đang khoá và học sinh này đã có điểm, nên nguyện vọng và ô chọn thi của học sinh này được giữ nguyên, dòng trong tệp bị bỏ qua. Mở khoá ở thẻ Quản lý rồi nạp lại nếu cần đổi.",
    "en": "Student {student_id}: commitment points are locked and this student already has points, so their rankings and test selection were kept as they are and the file's row was skipped. Unlock them in the Manage tab and import again to change."
  },
  "wharton_chua_bat": {
    "vi": "Không gian làm việc này chưa bật điểm quyết tâm.",
    "en": "Commitment points aren't turned on for this workspace."
  },
  "wharton_ho_so_chua_hop_le": {
    "vi": "{n} {person_l} có hồ sơ điểm quyết tâm chưa hợp lệ, nên chưa chạy xếp. Hãy điền đủ điểm quyết tâm cho những {person_l} này rồi chạy lại: mở thẻ 05 (Quản lý), mục Điểm quyết tâm, sửa điểm của từng {person_l} hoặc bấm \"Phóng cho đủ 100 theo tỉ lệ\".",
    "en": "{n} {person_l}(s) have a commitment points profile that isn't valid yet, so the allocation hasn't run. Fill in their commitment points and run again: open card 05 (Manage), then the Commitment points tab, and edit each {person_l}'s points or click \"Scale to 100 by ratio\"."
  },
  "chua_co_du_lieu_de_chay": {
    "vi": "Chưa có {person_l} hoặc chưa có {slot_l} nào, nên chưa chạy xếp. Hãy nhập dữ liệu ở thẻ Xếp {slot_sl} trước: Sổ nhập CLB hoặc các tệp CSV.",
    "en": "There are no {person_l}(s) or no {slot_l}(s) yet, so the allocation hasn't run. Import the data in the Run allocation tab first: the intake workbook or the CSV files."
  },
  "health_wharton_chua_hop_le": {
    "vi": "{n} {person_l} có hồ sơ điểm quyết tâm chưa hợp lệ, nên lần chạy xếp sẽ bị chặn cho tới khi sửa xong.",
    "en": "{n} {person_l}(s) have a commitment points profile that isn't valid yet, so the allocation will be blocked until it is fixed."
  },
  "health_wharton_vang_thi": {
    "vi": "{n} {person_l} vắng thi một {slot_sl} đã đặt điểm quỹ 1, nên {slot_sl} đó được xét như không thi (điểm quỹ 1 không được tính).",
    "en": "{n} {person_l}(s) missed the test for a {slot_l} they put fund 1 points on, so it is ranked as not tested (the fund 1 points don't count)."
  },
  "error_saving_wharton": {
    "vi": "Không lưu được điểm quyết tâm. Hãy thử lại.",
    "en": "Couldn't save the commitment points. Try again."
  },
  "wharton_da_khoa": {
    "vi": "Điểm quyết tâm đang khoá vì đã chạy xếp. Mở khoá ở thẻ Quản lý để sửa.",
    "en": "Commitment points are locked because the allocation has run. Unlock them in the Manage tab to edit."
  },
  "wharton_mo_khoa_sai_xac_nhan": {
    "vi": "Cần gõ đúng chữ {can_go} để mở khoá sửa điểm quyết tâm.",
    "en": "Type {can_go} exactly to unlock editing of the commitment points."
  },
  "wharton_xoa_sai_xac_nhan": {
    "vi": "Cần gõ đúng chữ {can_go} để xoá điểm quyết tâm của tất cả {person_pl}.",
    "en": "Type {can_go} exactly to delete the commitment points of all {person_pl}."
  },
  "wharton_da_xoa": {
    "vi": "Đã xoá điểm quyết tâm của {n} {person_l}.",
    "en": "Deleted the commitment points of {n} {person_l}(s)."
  },
  "wharton_da_mo_khoa": {
    "vi": "Đã mở khoá. Lần chạy xếp tiếp theo sẽ khoá lại.",
    "en": "Unlocked. The next allocation run will lock them again."
  },
  "error_wharton_quan_ly": {
    "vi": "Không thực hiện được thao tác với điểm quyết tâm. Hãy thử lại.",
    "en": "Couldn't complete that action on the commitment points. Try again."
  },
  "wharton_tom_tat_chua_hop_le": {
    "vi": "{n} {person_pl} có hồ sơ điểm quyết tâm chưa hợp lệ, nên chưa chạy xếp.",
    "en": "{n} {person_pl} have a commitment points profile that isn't valid yet, so the allocation hasn't run."
  },
  "wharton_phong_sai_xac_nhan": {
    "vi": "Cần gõ đúng chữ {can_go} để phóng điểm quyết tâm của {person_pl} chia thiếu hoặc thừa.",
    "en": "Type {can_go} exactly to scale the commitment points of {person_pl} whose split is short or over."
  },
  "wharton_da_phong": {
    "vi": "Đã phóng điểm quyết tâm cho {n} {person_pl}. {m} {person_pl} cần sửa tay.",
    "en": "Scaled the commitment points of {n} {person_pl}. {m} {person_pl} need editing by hand."
  },
  "xuat_chua_co_ket_qua": {
    "vi": "Chưa có kết quả xếp. Chạy xếp trước.",
    "en": "No allocation results yet. Run the allocation first."
  },
  "csv_pref_duplicate_deduped": {
    "vi": "{student_id}: có {slot_sl} bị lặp trong nguyện vọng, phần lặp đã được bỏ.",
    "en": "{student_id}: {slot_la} was listed twice in the preferences. The repeat was removed."
  },
  "csv_thi_bo_buoi_qua_tran": {
    "vi": "{student_id}: {session_l} {buoi} có {count} {slot_sl} dự thi, nhiều hơn mức tối đa {tran}. {session} này chưa được nạp, kể cả {score_l}. Các {session_l} khác vẫn được nạp.",
    "en": "{student_id}: {buoi} has {count} test {slot_pl}, more than the limit of {tran}. This {session_l} wasn't imported, {score_pl} included. The other {session_pl} were."
  },
  "csv_pref_bo_buoi_qua_tran": {
    "vi": "{student_id}: {session_l} {buoi} có {count} nguyện vọng, nhiều hơn mức tối đa {tran}. {session} này chưa được nạp. Các {session_l} khác vẫn được nạp. Sửa {session_l} này rồi nạp lại nếu cần.",
    "en": "{student_id}: {buoi} has {count} preferences, more than the limit of {tran}. This {session_l} wasn't imported. The other {session_pl} were. Fix it and import again if needed."
  },
  "csv_pref_too_many_skipped": {
    "vi": "{student_id}: có {count} nguyện vọng, nhiều hơn mức tối đa {tran}, nên {person_l} này chưa được nạp.",
    "en": "{student_id}: has {count} preferences, more than the limit of {tran}, so this {person_l} wasn't imported."
  },
  "csv_thi_too_many_skipped": {
    "vi": "{student_id}: đăng ký dự thi {count} {slot_sl}, nhiều hơn mức tối đa {tran}, nên {person_l} này chưa được nạp.",
    "en": "{student_id}: signed up to test for {count} {slot_pl}, more than the limit of {tran}, so this {person_l} wasn't imported."
  },
  "csv_unknown_clubs_skipped": {
    "vi": "{student_id}: không tìm thấy các {slot_sl} {club_ids}, nên {person_l} này chưa được nạp.",
    "en": "{student_id}: {slot_pl} {club_ids} weren't found, so this {person_l} wasn't imported."
  },
  "csv_student_missing_skipped": {
    "vi": "{student_id}: chưa có trong danh sách {person_l} nên được bỏ qua. Bật tuỳ chọn tự tạo {person_l} mới để nạp cả mã này.",
    "en": "{student_id}: not in the {person_l} list, so it was skipped. Turn on adding new {person_pl} automatically to include it."
  },
  "scoring_not_per_person": {
    "vi": "Không gian làm việc này chấm {score_l} theo từng {slot_l}, không theo từng {person_l}. Hãy chấm ở danh sách của {slot_l}.",
    "en": "This workspace sets the {score_l} per {slot_l}, not per {person_l}. Score from the {slot_l}'s list instead."
  },
  "scoring_not_per_slot": {
    "vi": "Không gian làm việc này không dùng {score_l} theo từng {slot_l} (chấm theo {person_l}, hoặc chỉ xét nhóm), nên {score_l} chấm ở đây sẽ không được dùng khi xếp. Hãy chấm theo cách của không gian làm việc này.",
    "en": "This workspace doesn't use a {score_l} per {slot_l} (it scores per {person_l}, or ranks by group only), so a {score_l} saved here would be ignored when sorting. Score the way this workspace does."
  },
  "score_not_applicant": {
    "vi": "{student_id}: không có trong danh sách dự thi của {slot_sl} này.",
    "en": "{student_id}: isn't on this {slot_l}'s test list."
  },
  "score_not_a_number": {
    "vi": "{student_id}: {score_l} “{diem_goc}” không phải là số nên chưa được lưu.",
    "en": "{student_id}: the {score_l} “{diem_goc}” isn't a number, so it wasn't saved."
  },
  "score_negative": {
    "vi": "{student_id}: {score_l} “{diem_goc}” là số âm, có thể do gõ thừa dấu trừ. {score} này chưa được lưu.",
    "en": "{student_id}: the {score_l} “{diem_goc}” is negative, probably an extra minus sign. It wasn't saved."
  },
  "health_scoring_none": {
    "vi": "{slot_s} {club_id}: có {n_applicants} {person_l} dự thi nhưng chưa ai được chấm {score_l}. Nếu sắp xếp lúc này, các {person_l} đó chỉ được xét theo số bốc thăm.",
    "en": "{slot} {club_id}: {n_applicants} {person_l}(s) took the test but none have a {score_l} yet. If the allocation runs now, those {person_pl} will be ranked by lottery number only."
  },
  "health_scoring_partial": {
    "vi": "{slot_s} {club_id}: mới chấm {n_scored}/{n_applicants} {person_l}. {n_missing} {person_l} chưa có {score_l} sẽ xếp sau tất cả {person_l} đã có {score_l}.",
    "en": "{slot} {club_id}: {n_scored} of {n_applicants} {person_pl} are scored. The {n_missing} without a {score_l} will rank below every scored {person_l}."
  },
  "health_tested_not_ranked": {
    "vi": "{n} lượt dự thi sẽ không có tác dụng vì {person_l} dự thi một {slot_sl} nhưng không chọn {slot_sl} đó làm nguyện vọng. Ví dụ: {sample}",
    "en": "{n} test sign-up(s) won't count because the {person_l} tested for {slot_la} but didn't list it as a preference. For example: {sample}"
  },
  "health_diem_khong_dang_ky_thi": {
    "vi": "{n} {score_l} chấm không còn ô đăng ký thi đi kèm ({person_l} đã bỏ đăng ký sau khi được chấm). Lần chạy sắp xếp bỏ qua các {score_l} này, và màn hình Nhập {score_l} không hiện chúng. Để dọn: mở {person_l} đó ở thẻ \"Nhập nguyện vọng\" và bấm \"Lưu {slot_sl} dự thi\". Ví dụ: {sample}",
    "en": "{n} {score_l}(s) no longer have a matching test registration (the {person_l} withdrew after being scored). Allocation runs ignore these {score_pl}, and the {score} entry screen does not show them. To clean up: open that {person_l} in the \"Enter preferences\" tab and press \"Save test {slot_pl}\". For example: {sample}"
  },
  "health_thi_qua_tran_buoi": {
    "vi": "{n} {person_l} đăng ký thi quá {tran} {slot_l} trong {session_l} {buoi}, thường do một {slot_l} vừa được chuyển sang {session_l} này ở màn Quản lý {slot_sl}. Thi thêm {slot_l} là được xét ưu tiên ở thêm chỗ, không công bằng với {person_l} khác. Sửa ở màn Nhập nguyện vọng: mở {person_l} đó, bỏ bớt {slot_sl} dự thi của {session_l} này rồi lưu. Ví dụ (số {slot_l} đang thi): {sample}",
    "en": "{n} {person_l}(s) are signed up to test for more than {tran} {slot_pl} on {buoi}, usually because {slot_la} was just moved to this {session_l} in Manage {slot_pl}. Testing for extra {slot_pl} gives them priority in more places, which is unfair to others. Fix it in the Enter preferences tab: open the {person_l}, untick some of this {session_l}'s test {slot_pl} and save. For example ({slot_pl} being tested for): {sample}"
  },
  "health_thi_qua_tran": {
    "vi": "{n} {person_l} đăng ký thi quá {tran} {slot_l}, thường do danh sách {slot_l} vừa được sửa ở màn Quản lý {slot_sl}. Thi thêm {slot_l} là được xét ưu tiên ở thêm chỗ, không công bằng với {person_l} khác. Sửa ở màn Nhập nguyện vọng: mở {person_l} đó, bỏ bớt {slot_sl} dự thi rồi lưu. Ví dụ (số {slot_l} đang thi): {sample}",
    "en": "{n} {person_l}(s) are signed up to test for more than {tran} {slot_pl}, usually because the {slot_l} list was just edited in Manage {slot_pl}. Testing for extra {slot_pl} gives them priority in more places, which is unfair to others. Fix it in the Enter preferences tab: open the {person_l}, untick some test {slot_pl} and save. For example ({slot_pl} being tested for): {sample}"
  },
  "health_vi_pham_clb_suc_chua_sai": {
    "vi": "{n} {slot_l} có sức chứa không hợp lệ (sức chứa phải lớn hơn 0, suất ưu tiên từ 0 tới sức chứa). Sửa ở màn Quản lý {slot_sl}. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} {slot_l}(s) have invalid capacity (capacity must be above 0, priority seats between 0 and capacity). Fix them in Manage {slot_pl}. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_nguyen_vong_hang_sai": {
    "vi": "{n} nguyện vọng có thứ hạng nhỏ hơn 1. Nhập lại nguyện vọng của những {person_l} này. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} preference(s) have a rank below 1. Re-enter these {person_pl}' preferences. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_diem_am": {
    "vi": "{n} {score_l} chấm là số âm. Sửa ở màn Nhập {score_l}. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} {score_l}(s) are negative. Fix them in the {score} entry tab. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_mo_coi_hoc_sinh": {
    "vi": "Bảng {bang} có dữ liệu của {n} mã {person_l} không còn tồn tại. Tạo lại {person_l} có mã đó, hoặc bấm \"Xoá toàn bộ {person_l} (giữ {slot_sl})\" ở màn Quản lý {slot_sl}. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} {person_l} ID(s) that no longer exist. Recreate {person_la} with that ID, or click \"Delete all {person_pl} (keep {slot_pl})\" in Manage {slot_pl}. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_mo_coi_clb": {
    "vi": "Bảng {bang} có dữ liệu của {n} mã {slot_l} không còn tồn tại. Tạo lại {slot_l} có mã đó ở màn Quản lý {slot_sl}. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} {slot_l} ID(s) that no longer exist. Recreate {slot_la} with that ID in Manage {slot_pl}. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_person_score_none": {
    "vi": "Chưa {person_l} nào có {score_l}, trong khi {score_l} được chấm theo từng {person_l}. Nếu sắp xếp lúc này, mọi {person_l} chỉ được xét theo số bốc thăm.",
    "en": "No {person_l} has a {score_l} yet, although the {score_l} is set per {person_l}. If the allocation runs now, everyone will be ranked by lottery number only."
  },
  "health_person_score_missing": {
    "vi": "{n} {person_l} có nguyện vọng nhưng chưa có {score_l}, nên chỉ được xét theo số bốc thăm, sau các {person_l} đã có {score_l}. Ví dụ: {sample}",
    "en": "{n} {person_l}(s) have preferences but no {score_l} yet, so they will be ranked by lottery number only, after those who have one. For example: {sample}"
  },
  "health_tier_missing": {
    "vi": "{n} {person_l} có nguyện vọng nhưng {group_l} để trống hoặc không có trong danh sách {group_l} của luật xếp, nên bị xếp sau cùng. Ví dụ: {sample}",
    "en": "{n} {person_l}(s) have preferences but their {group_l} is empty or isn't in the rules' list, so they will be ranked last. For example: {sample}"
  },
  "health_tiers_empty": {
    "vi": "Luật xếp theo thứ tự {group_l} đang bật nhưng danh sách {group_l} trống, nên không {person_l} nào được ưu tiên hơn ai.",
    "en": "Ranking by {group_l} order is on, but the {group_l} list is empty, so no {person_l} is ranked above another."
  },
  "health_student_no_preferences": {
    "vi": "{n} {person_l} chưa có nguyện vọng nào nên sẽ không được xếp vào {slot_sl} nào. Ví dụ: {sample}",
    "en": "{n} {person_l}(s) have no preferences, so none of them will be placed in {slot_la}. For example: {sample}"
  },
  "health_orphan_student_group": {
    "vi": "Nhóm ưu tiên \"{reserve_group}\" đang gán cho {n} {person_l} nhưng không {slot_sl} nào dùng nhãn này, có thể do gõ sai (ví dụ: {sample}). Các {person_l} này sẽ không được ưu tiên ở đâu. Sửa ở thẻ Quản lý: tìm {person_l}, đánh dấu, để trống ô nhãn rồi bấm \"Gán cho {person_l} đã đánh dấu\".",
    "en": "The priority group \"{reserve_group}\" is given to {n} {person_l}(s) but no {slot_l} uses it, which may be a typo (for example: {sample}). These {person_pl} won't get priority anywhere. To fix it on the Admin tab: find the {person_pl}, tick them, leave the label box empty, and click \"Assign to ticked {person_pl}\"."
  },
  "health_club_reserve_no_group": {
    "vi": "{slot_s} {club_id} có {reserve_capacity} suất ưu tiên nhưng chưa có nhóm ưu tiên, nên các suất này sẽ thành suất thường.",
    "en": "{slot} {club_id} has {reserve_capacity} priority seat(s) but no priority group, so those seats will become regular seats."
  },
  "health_club_group_no_students": {
    "vi": "{slot_s} {club_id} để {reserve_capacity} suất cho nhãn \"{reserve_group}\", nhưng chưa {person_l} nào có nhãn này. Các suất đó sẽ bỏ trống.",
    "en": "{slot} {club_id} keeps {reserve_capacity} seat(s) for the label \"{reserve_group}\", but no {person_l} has that label. Those seats will go unused."
  },
  "health_score_outlier": {
    "vi": "{slot_s} {club_id}: có {n} {score_l} khác hẳn các {score_l} còn lại ({score_l} giữa của {slot_sl} là {trung_vi}). Ví dụ: {sample}. Có thể {score_l} bị gõ nhầm, như 70 thay cho 7,0. Kiểm tra lại ở thẻ Chấm {score_l}.",
    "en": "{slot} {club_id}: {n} {score_l}(s) are far from the rest (the {slot_l}'s middle {score_l} is {trung_vi}). For example: {sample}. A {score_l} may be mistyped, such as 70 instead of 7.0. Check them on the Scoring tab."
  },
  "health_oversubscribed": {
    "vi": "Tổng số chỗ là {n_seats} nhưng có {n_students} {person_l} đã nộp nguyện vọng. Ít nhất {n_short} {person_l} sẽ không có chỗ.",
    "en": "There are {n_seats} seats in total but {n_students} {person_pl} submitted preferences. At least {n_short} {person_l}(s) won't get a seat."
  },
  "health_oversubscribed_chua_khai_buoi": {
    "vi": "Các {slot_l} chưa khai {session_l} có tổng {n_seats} chỗ, trong khi {n_students} {person_l} xếp nguyện vọng vào các {slot_l} này. Ít nhất {n_short} {person_l} chắc chắn không có chỗ ở nhóm này. Các {slot_l} chưa khai {session_l} được xếp chung như một {session_l} riêng. Hãy khai {session_l} cho chúng ở màn Quản lý {slot_sl}, tăng sức chứa, hoặc chấp nhận.",
    "en": "{slot_p} with no {session_l} set have {n_seats} seats in total, but {n_students} {person_l}(s) ranked these {slot_pl}. At least {n_short} {person_l}(s) will certainly get no seat among them. {slot_p} with no {session_l} set are matched together as one separate {session_l}. Set their {session_l} in Manage {slot_pl}, raise capacity, or accept it."
  },
  "health_oversubscribed_buoi": {
    "vi": "{session} {buoi} có tổng {n_seats} chỗ, trong khi {n_students} {person_l} xếp nguyện vọng ở {session_l} này. Ít nhất {n_short} {person_l} chắc chắn không có {slot_l} nào trong {session_l} {buoi}. Chỗ trống ở {session_l} khác không bù được. Hãy tăng sức chứa, thêm {slot_l} cho {session_l} này, hoặc chấp nhận.",
    "en": "{session} {buoi} has {n_seats} seats in total, but {n_students} {person_l}(s) ranked {slot_pl} in this {session_l}. At least {n_short} {person_l}(s) will certainly get no {slot_l} on {buoi}. Free seats in other {session_pl} cannot make up for it. Raise capacity, add {slot_la} to this {session_l}, or accept it."
  },
  "recovery_db_is_healthy": {
    "vi": "Tệp dữ liệu hiện tại vẫn đọc được bình thường, nên phần mềm không đổi tên hay thay thế nó. Lỗi lúc khởi động có lẽ không phải do dữ liệu hỏng, mà thường do thư mục không có quyền ghi hoặc tệp đang được mở ở chương trình khác. Đóng các chương trình khác, chuyển thư mục phần mềm ra chỗ có quyền ghi (ví dụ Desktop), rồi mở lại.",
    "en": "The current data file still reads normally, so it was not renamed or replaced. The startup error is probably not corrupt data. Usually the folder is not writable, or the file is open in another program. Close other programs, move the app folder somewhere writable (for example the Desktop), and open it again."
  },
  "recovery_no_backups": {
    "vi": "Không tìm thấy bản sao lưu nào. Có thể máy này chưa sắp xếp lần nào, hoặc thư mục sao lưu đã bị xoá.",
    "en": "No backups were found. This computer may not have run an allocation yet, or the backup folder was deleted."
  },
  "recovery_all_backups_corrupt": {
    "vi": "Đã thử {n_tried} bản sao lưu nhưng không bản nào mở được.",
    "en": "Tried {n_tried} backup(s), but none could be opened."
  },
  "recovery_restore_failed": {
    "vi": "Không khôi phục được dữ liệu. Hãy thử lại.",
    "en": "Couldn't restore the data. Try again."
  },
  "recovery_restored_from": {
    "vi": "Đã khôi phục từ bản sao lưu {backup_name}. Bỏ qua {n_skipped} bản mới hơn vì không mở được.",
    "en": "Restored from backup {backup_name}. Skipped {n_skipped} newer backup(s) that couldn't be opened."
  },
  "recovery_fresh_created": {
    "vi": "Đã tạo một tệp dữ liệu mới, trống. Tệp cũ được đổi tên và vẫn nằm trong cùng thư mục.",
    "en": "Created a new, empty data file. The old file was renamed and is still in the same folder."
  },
  "so_nhap_khong_phai_so": {
    "vi": "Đây không phải Sổ nhập CLB (cần có hai sheet \"1. {slot_s}\" và \"2. {person}\"). Hãy bấm \"Tải sổ nhập mẫu\", điền vào sổ đó rồi nạp lại.",
    "en": "This isn't a Club Input Workbook (it needs the sheets \"1. {slot_sv}\" and \"2. {person_v}\"). Click \"Download the input workbook\", fill it in and import it again."
  },
  "so_nhap_chi_nhan_xlsx": {
    "vi": "Phần mềm chỉ nhận Sổ nhập CLB (tệp .xlsx). Hãy bấm \"Tải sổ nhập mẫu\", điền vào sổ đó rồi nạp lại.",
    "en": "Only the Club Input Workbook (.xlsx) can be imported. Click \"Download the input workbook\", fill it in and import it again."
  },
  "so_nhap_thieu_sheet": {
    "vi": "Sổ nhập thiếu sheet \"{sheet}\".",
    "en": "The workbook is missing the sheet \"{sheet}\"."
  },
  "so_nhap_thieu_cot": {
    "vi": "Sheet \"{sheet}\" thiếu cột \"{cot}\". Đừng xoá hay đổi tên dòng tiêu đề của sổ.",
    "en": "Sheet \"{sheet}\" is missing the column \"{cot}\". Don't delete or rename the workbook's header row."
  },
  "so_nhap_cot_lech_nhom": {
    "vi": "Sheet \"{sheet}\", cột {cot}: không đúng chỗ trong nhóm \"{nhom}\". Mỗi nhóm có các cột giống nhau, theo đúng thứ tự ở hàng 2 của sổ mẫu. Có thể một cột đã bị chèn hay đổi tên. Hãy tải sổ mẫu và điền lại vào đúng cột. Nếu đây là cột phụ (ví dụ \"Ghi chú\") nằm bên phải nhóm cuối: thêm \"Nguyện vọng 2\" (từ hai nhóm trở lên phần mềm tự bỏ qua cột phụ) hoặc bỏ cột phụ.",
    "en": "Sheet \"{sheet}\", column {cot}: it doesn't belong in the group \"{nhom}\". Every group has the same columns, in the order shown in row 2 of the template. A column may have been inserted or renamed. Download the template and fill it in again in the right columns. If it is an extra column (for example \"Notes\") to the right of the last group: add a second preference group (with two or more groups the extra column is ignored) or remove the extra column."
  },
  "so_nhap_nhom_thieu_cot": {
    "vi": "Sheet \"{sheet}\", nhóm \"{nhom}\" thiếu cột \"{cot}\" mà các nhóm khác có. Mọi nhóm phải có các cột giống nhau. Có thể một cột đã bị xoá. Hãy tải sổ mẫu và điền lại.",
    "en": "Sheet \"{sheet}\", the group \"{nhom}\" is missing the column \"{cot}\" that the other groups have. Every group must have the same columns. A column may have been deleted. Download the template and fill it in again."
  },
  "so_nhap_khong_co_clb": {
    "vi": "Sheet \"{sheet}\" chưa có {slot_l} nào.",
    "en": "Sheet \"{sheet}\" has no {slot_pl} yet."
  },
  "so_nhap_clb_thieu_ten": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: thiếu Tên CLB.",
    "en": "Sheet \"{sheet}\", row {dong}: the {slot_l} name is missing."
  },
  "so_nhap_clb_trung_ten": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: tên {slot_sl} \"{ten}\" đã có ở dòng {dong_truoc}. Mỗi {slot_sl} một tên riêng.",
    "en": "Sheet \"{sheet}\", row {dong}: the {slot_l} name \"{ten}\" is already used on row {dong_truoc}. Each {slot_l} needs its own name."
  },
  "so_nhap_clb_trung_ma": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: Mã CLB \"{ma}\" đã có ở dòng {dong_truoc}.",
    "en": "Sheet \"{sheet}\", row {dong}: the {slot_l} code \"{ma}\" is already used on row {dong_truoc}."
  },
  "so_nhap_chi_tieu_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Chỉ tiêu phải là số nguyên lớn hơn 0, Suất ưu tiên không được lớn hơn Chỉ tiêu (đang ghi: {chi_tieu} / {uu_tien}).",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): seats must be a whole number above 0, and priority seats can't exceed seats (found: {chi_tieu} / {uu_tien})."
  },
  "so_nhap_thieu_ma_hs": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: thiếu Mã HS.",
    "en": "Sheet \"{sheet}\", row {dong}: the {person_l} ID is missing."
  },
  "so_nhap_hs_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: Mã HS {student_id} đã có ở dòng {dong_truoc}. Mỗi {person_l} một dòng.",
    "en": "Sheet \"{sheet}\", row {dong}: {person_l} ID {student_id} is already on row {dong_truoc}. One row per {person_l}."
  },
  "so_nhap_clb_khong_co": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}), NV{k}: không có {slot_sl} nào tên \"{gia_tri}\" ở sheet \"1. {slot_s}\". Hãy chọn tên trong danh sách thả xuống.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}), NV{k}: there is no {slot_l} called \"{gia_tri}\" on sheet \"1. {slot_sv}\". Pick a name from the drop-down list."
  },
  "so_nhap_nv_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): \"{gia_tri}\" được chọn hai lần (NV{k_truoc} và NV{k}).",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): \"{gia_tri}\" is chosen twice (NV{k_truoc} and NV{k})."
  },
  "so_nhap_diem_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}), {score} {k}: \"{gia_tri}\" không phải {score_l}. Ghi một số (vd 8,5), hoặc chữ thi nếu chưa có {score_l}.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}), {score_v} {k}: \"{gia_tri}\" isn't a {score_l}. Enter a number (e.g. 8.5), or the word thi if the {score_l} isn't known yet."
  },
  "so_nhap_diem_sai_che_do": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): có {score_l} ở cột \"{cot}\", nhưng cột này không đúng cách chấm của không gian làm việc (một {score_l} cho cả {person_l}, hoặc một {score_l} cho mỗi {slot_l}). Nạp vào sẽ mất {score_l} mà không báo. Hãy tải sổ mẫu của không gian làm việc này và điền lại vào đúng cột.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): there is a {score_l} in column \"{cot}\", but that column doesn't match how this workspace scores (one {score_l} per {person_l}, or one per {slot_l}). Importing would lose it silently. Download this workspace's template and fill it in again in the right column."
  },
  "so_nhap_diem_ca_nhan_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}), {score}: \"{gia_tri}\" không phải {score_l}. Ghi một số (vd 8,5), hoặc chữ thi nếu chưa có {score_l}.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}), {score}: \"{gia_tri}\" isn't a {score_l}. Enter a number (e.g. 8.5), or the word thi if the {score_l} isn't known yet."
  },
  "so_nhap_diem_khong_nv": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): có {score} {k} nhưng NV{k} trống. {score} phải nằm ngay cạnh {slot_sl} của nó.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): {score_v} {k} is filled but NV{k} is empty. A {score_l} must sit right next to its {slot_l}."
  },
  "loi_nap_so_nhap": {
    "vi": "Không nạp được sổ nhập. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the workbook. Check the file and try again."
  },
  "so_nhap_mau_loi": {
    "vi": "Không tạo được sổ nhập mẫu. Hãy thử lại.",
    "en": "Couldn't create the input workbook. Try again."
  },
  "so_nhap_qua_tran_nv": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): {n} nguyện vọng ở {session_l} {buoi}, tối đa {tran} mỗi {session_l}. Bớt nguyện vọng của {session_l} này.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): {n} preferences in {session_l} {buoi}, at most {tran} per {session_l}. Remove some for this {session_l}."
  },
  "so_nhap_qua_tran_thi": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): thi {n} {slot_sl} ở {session_l} {buoi}, tối đa {tran} mỗi {session_l}. Xoá bớt ô {score} của {session_l} này.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): {n} tested {slot_pl} in {session_l} {buoi}, at most {tran} per {session_l}. Clear some {score_v} cells for this {session_l}."
  },
  "so_nhap_ma_tu_sinh_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): mã tự tạo \"{ma}\" trùng với {slot_sl} ở dòng {dong_truoc}. Điền Mã CLB cho một trong hai dòng.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): the generated code \"{ma}\" clashes with the {slot_l} on row {dong_truoc}. Fill in Mã CLB on one of the two rows."
  },
  "so_nhap_canh_bao_khong_co_clb": {
    "vi": "Sổ này chưa có {slot_l} nào, nên không thêm hay cập nhật {slot_l} nào. {slot_sl} đang có trong phần mềm được giữ nguyên.",
    "en": "This workbook has no {slot_l} yet, so none is added or updated. The {slot_l}(s) already in the app are left as they are."
  },
  "so_nhap_canh_bao_khong_co_hs": {
    "vi": "Sổ này chưa có {person_l} nào, nên không thêm hay cập nhật {person_l} nào. Chưa có nguyện vọng thì chưa xếp được.",
    "en": "This workbook has no {person_l} yet, so none is added or updated. Nothing can be assigned until preferences are in."
  },
  "so_nhap_canh_bao_xoa_diem": {
    "vi": "{n} {score_l} đã chấm trong phần mềm sẽ bị xoá, vì sổ ghi \"thi\" (chưa có {score_l}) ở các ô đó. Muốn giữ {score_l} thì xuất lại dữ liệu đầu vào thành sổ mới rồi sửa trên sổ đó.",
    "en": "{n} {score_l}(s) already entered in the app will be removed, because the workbook says \"thi\" (no {score_l} yet) in those cells. To keep them, export the current input data to a new workbook and edit that one."
  },
  "so_nhap_canh_bao_bo_nhom": {
    "vi": "{n} {person_l} đang có {group} sẽ bị bỏ nhóm, vì ô {group} của những {person_l} đó trong sổ để trống.",
    "en": "{n} {person_l}(s) who currently have a priority group will lose it, because their {group_v} cell in the workbook is empty."
  },
  "so_nhap_canh_bao_clb_ngoai_so": {
    "vi": "{n} {slot_sl} có trong phần mềm nhưng không có trong sổ ({ten}). Chúng vẫn được giữ. Nếu đó là {slot_sl} vừa đổi tên thì giữ nguyên Mã CLB khi đổi tên, rồi xoá {slot_sl} thừa ở thẻ 05.",
    "en": "{n} {slot_l}(s) are in the app but not in the workbook ({ten}). They are kept. If one was just renamed, keep its Mã CLB when renaming, then delete the leftover {slot_l} on tab 05."
  },
  "so_nhap_ma_tu_sinh_trung_clb_da_co": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): mã tự tạo \"{ma}\" trùng mã của {slot_sl} \"{ten_cu}\" đã có trong phần mềm. Nếu đây chính là {slot_sl} đó (đổi tên), điền Mã CLB là {ma_cu}; nếu là {slot_sl} khác, điền một Mã CLB mới.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): the generated code \"{ma}\" is already used by the {slot_l} \"{ten_cu}\" in the app. If this is that {slot_l} (renamed), fill in Mã CLB as {ma_cu}; if it is a different {slot_l}, fill in a new Mã CLB."
  },
  "ws_tat_che_do": {
    "vi": "Chương trình đang mở một tệp dữ liệu riêng (đường dẫn truyền lúc khởi động), nên chức năng không gian làm việc đang tắt.",
    "en": "The program was started with its own data file (a path given at launch), so workspaces are turned off."
  },
  "ws_khong_co": {
    "vi": "Không tìm thấy không gian làm việc \"{slug}\". Có thể nó đã bị xoá hoặc đổi chỗ. Hãy mở lại danh sách.",
    "en": "Workspace \"{slug}\" was not found. It may have been deleted or moved. Reopen the list."
  },
  "ws_du_lieu_sai": {
    "vi": "Không thực hiện được vì thông tin không gian làm việc chưa hợp lệ. Kiểm tra lại các ô đã điền.",
    "en": "This couldn't be done because the workspace details are not valid. Check the fields that were filled in."
  },
  "ws_khong_xoa_dang_mo": {
    "vi": "Không xoá được không gian làm việc \"{slug}\" vì đang mở nó. Hãy mở không gian làm việc khác trước rồi xoá.",
    "en": "Workspace \"{slug}\" can't be deleted because it is open. Open another workspace first, then delete it."
  },
  "ws_cau_hinh_hong": {
    "vi": "Không đọc được cấu hình của không gian làm việc này, nên chưa thể làm việc đó: chạy bằng luật trường học sẽ ra kết quả sai mà không báo. Hãy mở lại không gian làm việc, kiểm tra hoặc đặt lại cấu hình rồi thử lại.",
    "en": "This workspace's settings can't be read, so this can't be done: running with the school rules would give wrong results without any warning. Reopen the workspace, check or reset its settings, then try again."
  },
  "xuat_duong_la_thu_muc": {
    "vi": "Không xuất được vì \"{path}\" là một thư mục có sẵn, không phải tên tệp. Hãy chọn một tên tệp (ví dụ thêm tên tệp vào cuối đường dẫn) hoặc để trống để lưu vào thư mục Tải xuống.",
    "en": "Couldn't export because \"{path}\" is an existing folder, not a file name. Choose a file name (for example add one to the end of the path) or leave it empty to save to the Downloads folder."
  },
  "csdl_dang_ban": {
    "vi": "Cơ sở dữ liệu đang bận vì có thao tác khác đang ghi. Chờ vài giây rồi thử lại.",
    "en": "The database is busy because another operation is writing to it. Wait a few seconds and try again."
  },
  "http_bi_tu_choi": {
    "vi": "Yêu cầu bị từ chối vì thiếu hoặc sai khoá truy cập. Hãy mở lại ứng dụng.",
    "en": "The request was refused because the access key is missing or wrong. Reopen the app."
  },
  "http_khong_co_dich": {
    "vi": "Không có địa chỉ yêu cầu này. Hãy mở lại ứng dụng.",
    "en": "There is no such request address. Reopen the app."
  },
  "http_khong_co_ham": {
    "vi": "Không có chức năng «{ten}». Có thể giao diện và phần mềm khác phiên bản nhau.",
    "en": "There is no function \"{ten}\". The interface and the software may be different versions."
  },
  "http_than_qua_lon": {
    "vi": "Dữ liệu gửi lên quá lớn (tối đa {toi_da_mb} MB). Hãy chia nhỏ tệp rồi thử lại.",
    "en": "The data sent is too large (limit {toi_da_mb} MB). Split the file and try again."
  },
  "ws_loi_khong_ro": {
    "vi": "Không thực hiện được thao tác với không gian làm việc. Hãy thử lại.",
    "en": "Couldn't complete the workspace operation. Try again."
  },
  "forms_duong_chua_chon": {
    "vi": "Chưa chọn đường chuẩn bị đợt. Hãy chọn đường A hoặc đường B.",
    "en": "No preparation path chosen. Choose path A or path B."
  },
  "forms_chua_co_clb": {
    "vi": "Chưa nạp danh sách CLB của đợt. Hãy làm bước 1 (nạp tệp Phiếu thiết lập CLB) trước.",
    "en": "The club list for this round hasn't been loaded. Do step 1 (load the club setup form file) first."
  },
  "forms_chua_co_de": {
    "vi": "Chưa nạp đề thi của đợt. Hãy làm bước 2 (nạp tệp đề) trước.",
    "en": "The exam for this round hasn't been loaded. Do step 2 (load the exam file) first."
  },
  "phieu_clb_tep_sai": {
    "vi": "Tệp Phiếu thiết lập CLB không đọc được hoặc sai dạng.",
    "en": "The club setup form file can't be read or has the wrong format."
  },
  "de_thi_tep_sai": {
    "vi": "Tệp đề thi không đọc được hoặc sai dạng.",
    "en": "The exam file can't be read or has the wrong format."
  },
  "forms_khong_chuyen_duoc": {
    "vi": "Không chuyển được dữ liệu từ biểu mẫu sang phần mềm.",
    "en": "Couldn't convert the form data for the software."
  },
  "forms_tep_khong_nhan_ra": {
    "vi": "Không nhận ra tệp \"{ten}\" là tệp xuất của biểu mẫu nào. Hãy kiểm tra lại tệp.",
    "en": "Couldn't tell which form's export \"{ten}\" is. Check the file."
  },
  "forms_tep_sai_duong": {
    "vi": "Tệp \"{ten}\" không dùng cho đường {duong}. Hãy kiểm tra đã chọn đúng đường chưa.",
    "en": "File \"{ten}\" isn't used on path {duong}. Check that the right path is chosen."
  },
  "forms_tep_sau_ket_qua": {
    "vi": "Tệp \"{ten}\" là biểu mẫu Sau khi xem kết quả, không nạp ở bước này. Hãy nạp nó ở nhóm \"Sau khi công bố kết quả\" sau khi xếp.",
    "en": "File \"{ten}\" is the After-results form; it isn't loaded in this step. Load it in the \"After the results are published\" group after allocation."
  },
  "forms_can_chon_de": {
    "vi": "Tệp \"{ten}\" cần biết đề thi. Hãy chọn đề rồi nạp lại.",
    "en": "File \"{ten}\" needs to know which exam it belongs to. Choose the exam and load it again."
  },
  "forms_thieu_email": {
    "vi": "Thiếu danh sách email và mã học sinh. Hãy nạp tệp này trước.",
    "en": "The email-to-student-ID list is missing. Load that file first."
  },
  "forms_thieu_danh_sach_lop": {
    "vi": "Thiếu danh sách lớp để tạo bộ biểu mẫu.",
    "en": "The class list needed to build the form set is missing."
  },
  "forms_tao_bo_loi": {
    "vi": "Không tạo được bộ biểu mẫu.",
    "en": "Couldn't build the form set."
  },
  "forms_thieu_tep_nap": {
    "vi": "Chưa có tệp nào để nạp. Hãy thả các tệp xuất từ biểu mẫu vào khung.",
    "en": "There are no files to load yet. Drop the files exported from the forms into the box."
  },
  "forms_thieu_tep_dang_ky": {
    "vi": "Chưa có tệp đăng ký cho đường {duong}: đường A cần tệp CSV từ List, đường B cần tệp Excel từ biểu mẫu đăng ký.",
    "en": "No registration file for path {duong}: path A needs the CSV from the List, path B needs the registration form's Excel file."
  },
  "forms_nhieu_tep_list": {
    "vi": "Đường A chỉ nạp một tệp CSV từ List. Hãy bỏ bớt tệp.",
    "en": "Path A loads only one CSV file from the List. Remove the extra files."
  },
  "forms_chua_chuyen_tep": {
    "vi": "Chưa chuyển tệp nào thành Sổ nhập. Hãy nạp tệp ở bước 4 trước.",
    "en": "No files have been converted into an input workbook yet. Load the files in step 4 first."
  },
  "fa_clb_tuyen_chon_chua_co_diem": {
    "vi": "CLB {club_id} (Tuyển chọn) có {so_dang_ky} học sinh đăng ký ({so_nv1} học sinh xếp làm nguyện vọng 1) nhưng chưa có điểm của học sinh nào, nên tất cả sẽ bị loại. Hãy nhập điểm cho CLB này ở thẻ Nhập điểm, hoặc đổi CLB sang loại Giới hạn.",
    "en": "Club {club_id} (Selective) has {so_dang_ky} applicants ({so_nv1} with it as first choice) but no scores at all, so every one of them would be removed. Enter scores for this club in the Scores tab, or change the club to Limited."
  },
  "khieu_nai_hs_khong_co": {
    "vi": "Không nhận được khiếu nại: không tìm thấy {person_l} có mã {student_id}. Hãy kiểm tra lại mã rồi gõ lại.",
    "en": "Appeal not accepted: no {person_l} with ID {student_id} was found. Check the ID and type it again."
  },
  "khieu_nai_chua_co_ket_qua": {
    "vi": "Không nhận được khiếu nại: {person_l} {student_id} chưa có kết quả ở buổi {buoi}.",
    "en": "Appeal not accepted: {person_l} {student_id} has no result for session {buoi} yet."
  },
  "so_nhap_canh_bao_wharton_trong": {
    "vi": "{n} {person_l} (ví dụ {vd}) có từ hai {slot_l} trong cùng một buổi mà chưa điền điểm quyết tâm nào, nên lần chạy xếp sẽ bị chặn. Cách sửa: điền đủ 100 điểm cho mỗi nhóm trong sổ rồi nhập lại, hoặc tắt điểm quyết tâm ở Không gian làm việc → ⋯ → Tính năng sau khi xếp….",
    "en": "{n} {person_l}(s) (for example {vd}) have two or more {slot_l}s in the same session with no commitment points filled in, so the allocation run will be blocked. To fix it: fill in 100 points for each group in the workbook and import again, or turn commitment points off in Workspace → ⋯ → After-allocation features…."
  },
  "phieu_nd_phieu_thieu_cau_2": {
    "vi": "{clb}: chưa trả lời câu 2 (mở thêm nhóm được không): không phân loại được, đã bỏ qua",
    "en": "{clb}: hasn't answered question 2 (can extra groups be opened?), so the club can't be classified: skipped"
  },
  "phieu_nd_phieu_thieu_phong": {
    "vi": "{clb}: CLB mở thêm nhóm được nhưng chưa ghi sức chứa mỗi nhóm: đã bỏ qua",
    "en": "{clb}: the club can open extra groups but no room capacity per group is given: skipped"
  },
  "phieu_nd_phieu_thieu_cho": {
    "vi": "{clb}: CLB không mở thêm nhóm nhưng chưa ghi số chỗ tối đa hợp lệ: đã bỏ qua",
    "en": "{clb}: the club doesn't open extra groups but no valid maximum number of seats is given: skipped"
  },
  "phieu_nd_phieu_moc_sai": {
    "vi": "{clb}: mốc tối thiểu phải là số nguyên từ 1 đến 10: đã bỏ qua",
    "en": "{clb}: the pass mark must be a whole number from 1 to 10: skipped"
  },
  "phieu_nd_phieu_toi_thieu_sai": {
    "vi": "{clb}: số thành viên tối thiểu không hợp lệ: không ghi",
    "en": "{clb}: the minimum number of members is not valid: not recorded"
  },
  "phieu_nd_phieu_tu_do_co_ly_do_gioi_han": {
    "vi": "{clb}: khai Tự do nhưng có ghi lý do giới hạn; CLB bị giới hạn thật không được khai Tự do, cần admin xem lại",
    "en": "{clb}: declared Free but a reason for limiting is given; a club that is really limited can't be declared Free, an admin needs to review it"
  },
  "phieu_nd_phieu_thieu_ly_do": {
    "vi": "{clb}: CLB giới hạn chưa ghi lý do (phòng/dụng cụ/người hướng dẫn)",
    "en": "{clb}: the Limited club has no reason given (room, equipment or instructor)"
  },
  "phieu_nd_phieu_thieu_cau_4": {
    "vi": "{clb}: chưa trả lời câu 4: coi là không cần kỹ năng (Giới hạn)",
    "en": "{clb}: hasn't answered question 4: treated as needing no skill (Limited)"
  },
  "phieu_nd_phieu_thu_thach_khong_tu_cham": {
    "vi": "{clb}: loại thử thách không phải trắc nghiệm: phần mềm không chấm tự động, admin nhập điểm",
    "en": "{clb}: the challenge type is not multiple choice: the software can't mark it automatically, an admin enters the scores"
  },
  "phieu_nd_phieu_thieu_tieu_chi": {
    "vi": "{clb}: CLB Tuyển chọn chưa ghi bảng tiêu chí",
    "en": "{clb}: the Selective club has no criteria table"
  },
  "phieu_nd_phieu_cho_duyet_tuyen_chon": {
    "vi": "{clb}: CLB Tuyển chọn: chờ ban quản lý duyệt trước khi mở cổng",
    "en": "{clb}: Selective club: waiting for management approval before the gate opens"
  },
  "phieu_nd_phieu_nop_nhieu_lan": {
    "vi": "{clb}: nộp phiếu nhiều lần: lấy phiếu cuối cùng",
    "en": "{clb}: submitted the form more than once: the last submission is used"
  },
  "phieu_nd_phieu_mac_dinh_ky_truoc": {
    "vi": "{clb}: chưa nộp phiếu: mặc định Giới hạn với chỉ tiêu kỳ trước",
    "en": "{clb}: hasn't submitted the form: defaults to Limited with last term's quota"
  },
  "phieu_clb_khong_co_clb_hop_le": {
    "vi": "Không có CLB hợp lệ nào trong tệp.",
    "en": "There is no valid club in the file."
  },
  "forms_cot_la": {
    "vi": "{n} cột trong tệp không khớp câu hỏi nào của biểu mẫu nên bị bỏ qua, ví dụ: {vi_du}. Hãy kiểm tra xem chữ câu hỏi trên Forms có bị sửa không.",
    "en": "{n} columns in the file don't match any question of the form and were skipped, for example: {vi_du}. Check whether the question wording was edited in Forms."
  },
  "forms_thieu_ban_do": {
    "vi": "Tệp ghi tên buổi bằng chữ (ví dụ \"Thứ Hai\") nhưng đợt này chưa có đề thi để đối chiếu tên buổi. Hãy nạp đề thi của đợt rồi nạp lại tệp.",
    "en": "The file writes days by name (for example \"Monday\") but this round has no exam file to match the names against. Load the round's exam file, then load this file again."
  },
  "forms_tieu_de_trung": {
    "vi": "Đề thi có hai câu hoặc hai lựa chọn cùng chữ nên không phân biệt được trên biểu mẫu: {chi_tiet} Hãy đổi tên trong đề thi rồi sinh lại biểu mẫu.",
    "en": "The exam file has two questions or two options with the same wording, so they can't be told apart on the form: {chi_tiet} Rename them in the exam file, then generate the form again."
  }
};
