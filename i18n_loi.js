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
    "vi": "Không tải được thống kê suất dự trữ. Hãy thử lại.",
    "en": "Couldn't load the reserve seat summary. Try again."
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
    "vi": "Dòng {line} bị bỏ qua vì {reason} không hợp lệ. Tổng chỗ phải lớn hơn 0 và suất dự trữ không được nhiều hơn tổng chỗ.",
    "en": "Line {line} was skipped because {reason} isn't valid. Total seats must be above 0, and reserve seats can't be more than total seats."
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
    "vi": "Nhãn dự trữ {reserve_group} không khớp với {slot_l} nào, nên {n} {person_l} mang nhãn này sẽ không được xét suất dự trữ. Có thể nhãn đúng là {goi_y}.",
    "en": "The reserve label {reserve_group} doesn't match any {slot_l}, so {n} {person_l}(s) with this label won't be considered for reserve seats. The intended label may be {goi_y}."
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
    "vi": "Không tải được danh sách nhãn dự trữ. Hãy thử lại.",
    "en": "Couldn't load the reserve labels. Try again."
  },
  "error_assigning_reserve_group": {
    "vi": "Không gán được nhãn dự trữ. Hãy thử lại.",
    "en": "Couldn't assign the reserve label. Try again."
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
    "vi": "Tổng chỗ phải lớn hơn 0.",
    "en": "Total seats must be more than 0."
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
    "vi": "Suất dự trữ không được là số âm",
    "en": "Reserve capacity cannot be negative"
  },
  "reserve_capacity_exceeds_capacity": {
    "vi": "Suất dự trữ không được nhiều hơn tổng chỗ.",
    "en": "Reserve seats can't be more than total seats."
  },
  "club_id_required": {
    "vi": "Hãy nhập mã {slot_sl}.",
    "en": "Enter {slot_la} code."
  },
  "cannot_delete_club_referenced": {
    "vi": "Không xoá được {slot_sl} {club_id} vì {slot_sl} này đang có trong {n_prefs} nguyện vọng và {n_matches} kết quả. Hãy xử lý các dữ liệu đó trước.",
    "en": "{slot} {club_id} can't be deleted because it's still in {n_prefs} preference(s) and {n_matches} result(s). Deal with that data first."
  },
  "student_not_found": {
    "vi": "Không tìm thấy {person_l} {student_id}.",
    "en": "{person} {student_id} wasn't found."
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
    "vi": "{slot_s} {club_id} có tổng chỗ bằng 0. Tổng chỗ phải lớn hơn 0.",
    "en": "{slot} {club_id} has 0 seats. Total seats must be more than 0."
  },
  "club_reserve_negative": {
    "vi": "{slot_s} {club_id} có số suất dự trữ âm. Số này phải từ 0 trở lên.",
    "en": "{slot} {club_id} has a negative number of reserved seats. It must be 0 or more."
  },
  "club_reserve_exceeds_capacity": {
    "vi": "{slot_s} {club_id} có suất dự trữ nhiều hơn tổng chỗ.",
    "en": "{slot} {club_id} has more reserve seats than total seats."
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
    "vi": "{slot_s} {club_id} có {count} {person_l} dùng suất dự trữ nhưng chỉ có {reserve_capacity} suất.",
    "en": "{slot} {club_id} has {count} {person_l}(s) in reserve seats but only {reserve_capacity} reserve seat(s)."
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
    "en": "Preference points not fully used: {person_l} {student_id} still has {thieu} point(s) left in fund {quy}."
  },
  "wharton_vuot_ngan_sach": {
    "vi": "{person} {student_id} đặt {tong} điểm quyết tâm ở quỹ {quy}, nhiều hơn {ngan_sach} điểm được phép.",
    "en": "{person} {student_id} placed {tong} preference points in fund {quy}, more than the {ngan_sach} allowed."
  },
  "wharton_diem_khong_hop_le": {
    "vi": "{person} {student_id} đặt “{gia_tri}” điểm quyết tâm cho {slot_sl} {club_id}. Điểm quyết tâm phải là số nguyên từ 0 trở lên.",
    "en": "{person} {student_id} placed “{gia_tri}” preference points on {slot_l} {club_id}. Preference points must be a whole number of 0 or more."
  },
  "wharton_ngoai_tap": {
    "vi": "{person} {student_id} đặt điểm quyết tâm quỹ {quy} cho {slot_sl} {club_id}, nhưng {slot_sl} này không thuộc quỹ {quy} (không có trong nguyện vọng, hoặc sai loại có thi / không thi).",
    "en": "{person} {student_id} placed fund {quy} preference points on {slot_l} {club_id}, but that {slot_l} isn't in fund {quy} (not in the preferences, or the wrong tested / not-tested group)."
  },
  "wharton_tang_lech": {
    "vi": "{person} {student_id} có {score_l} thi ở {slot_sl} {club_id} nhưng chỉ đặt điểm quyết tâm cho {slot_sl} này ở quỹ không thi. Cần chia lại điểm.",
    "en": "{person} {student_id} has a test {score_l} for {slot_l} {club_id} but placed preference points for it only in the not-tested fund. The points need to be split again."
  },
  "wharton_vang_thi": {
    "vi": "{person} {student_id} vắng thi {slot_sl} {club_id}, nên được xét như không thi với {diem} điểm quyết tâm quỹ 2 ({diem_bo} điểm quỹ 1 không được tính).",
    "en": "{person} {student_id} missed the test for {slot_l} {club_id}, so is ranked as not tested with {diem} fund 2 preference point(s) ({diem_bo} fund 1 point(s) not counted)."
  },
  "csv_wp_khong_hop_le": {
    "vi": "Điểm quyết tâm của {person_l} {student_id} ở {slot_sl} {club_id} là “{gia_tri}”, không phải số nguyên từ 0 trở lên. Ô này chưa được lưu.",
    "en": "The preference points for {person_l} {student_id} on {slot_l} {club_id} are “{gia_tri}”, not a whole number of 0 or more. This cell wasn't saved."
  },
  "csv_wp_khong_co_nguyen_vong": {
    "vi": "{student_id}: có điểm quyết tâm ở cột {cot} nhưng ô nguyện vọng cạnh đó để trống. Điểm này chưa được lưu.",
    "en": "{student_id}: there are preference points in column {cot} but the preference cell next to it is empty. Those points weren't saved."
  },
  "csv_wp_bo_qua": {
    "vi": "Không gian làm việc này chưa bật điểm quyết tâm: {n} ô điểm quyết tâm trong tệp đã được bỏ qua, không lưu.",
    "en": "This workspace doesn't use preference points yet: {n} preference points cell(s) in the file were skipped and not saved."
  },
  "wharton_chua_bat": {
    "vi": "Không gian làm việc này chưa bật điểm quyết tâm.",
    "en": "Preference points aren't turned on for this workspace."
  },
  "wharton_ho_so_chua_hop_le": {
    "vi": "{n} {person_l} có hồ sơ điểm quyết tâm chưa hợp lệ, nên chưa chạy xếp. Hãy sửa rồi chạy lại.",
    "en": "{n} {person_l}(s) have a preference points profile that isn't valid yet, so the allocation hasn't run. Fix them and run again."
  },
  "health_wharton_chua_hop_le": {
    "vi": "{n} {person_l} có hồ sơ điểm quyết tâm chưa hợp lệ, nên lần chạy xếp sẽ bị chặn cho tới khi sửa xong.",
    "en": "{n} {person_l}(s) have a preference points profile that isn't valid yet, so the allocation will be blocked until it is fixed."
  },
  "health_wharton_vang_thi": {
    "vi": "{n} {person_l} vắng thi một {slot_sl} đã đặt điểm quỹ 1, nên {slot_sl} đó được xét như không thi (điểm quỹ 1 không được tính).",
    "en": "{n} {person_l}(s) missed the test for a {slot_l} they put fund 1 points on, so it is ranked as not tested (the fund 1 points don't count)."
  },
  "error_saving_wharton": {
    "vi": "Không lưu được điểm quyết tâm. Hãy thử lại.",
    "en": "Couldn't save the preference points. Try again."
  },
  "wharton_da_khoa": {
    "vi": "Điểm quyết tâm đang khoá vì đã chạy xếp. Mở khoá ở thẻ Quản lý để sửa.",
    "en": "Preference points are locked because the allocation has run. Unlock them in the Manage tab to edit."
  },
  "wharton_mo_khoa_sai_xac_nhan": {
    "vi": "Cần gõ đúng chữ {can_go} để mở khoá sửa điểm quyết tâm.",
    "en": "Type {can_go} exactly to unlock editing of the preference points."
  },
  "wharton_xoa_sai_xac_nhan": {
    "vi": "Cần gõ đúng chữ {can_go} để xoá điểm quyết tâm của tất cả {person_pl}.",
    "en": "Type {can_go} exactly to delete the preference points of all {person_pl}."
  },
  "wharton_da_xoa": {
    "vi": "Đã xoá điểm quyết tâm của {n} {person_l}.",
    "en": "Deleted the preference points of {n} {person_l}(s)."
  },
  "wharton_da_mo_khoa": {
    "vi": "Đã mở khoá. Lần chạy xếp tiếp theo sẽ khoá lại.",
    "en": "Unlocked. The next allocation run will lock them again."
  },
  "error_wharton_quan_ly": {
    "vi": "Không thực hiện được thao tác với điểm quyết tâm. Hãy thử lại.",
    "en": "Couldn't complete that action on the preference points. Try again."
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
    "vi": "{n} {score_l} chấm không còn ô đăng ký thi đi kèm ({person_l} đã bỏ đăng ký sau khi được chấm). Lần chạy sắp xếp bỏ qua các {score_l} này, và màn hình Nhập {score_l} không hiện chúng. Để dọn: mở {person_l} đó ở thẻ \"Nhập tại chỗ\" và bấm \"Lưu {slot_sl} dự thi\". Ví dụ: {sample}",
    "en": "{n} {score_l}(s) no longer have a matching test registration (the {person_l} withdrew after being scored). Allocation runs ignore these {score_pl}, and the {score} entry screen does not show them. To clean up: open that {person_l} in the \"Kiosk entry\" tab and press \"Save test {slot_pl}\". For example: {sample}"
  },
  "health_thi_qua_tran_buoi": {
    "vi": "{n} {person_l} đăng ký thi quá {tran} {slot_l} trong {session_l} {buoi}, thường do một {slot_l} vừa được chuyển sang {session_l} này ở màn Quản lý {slot_sl} & dự trữ. Thi thêm {slot_l} là được xét ưu tiên ở thêm chỗ, không công bằng với {person_l} khác. Sửa ở màn Nhập tại chỗ: mở {person_l} đó, bỏ bớt {slot_sl} dự thi của {session_l} này rồi lưu. Ví dụ (số {slot_l} đang thi): {sample}",
    "en": "{n} {person_l}(s) are signed up to test for more than {tran} {slot_pl} on {buoi}, usually because {slot_la} was just moved to this {session_l} in {slot_p} & reserves. Testing for extra {slot_pl} gives them priority in more places, which is unfair to others. Fix it in the Kiosk entry tab: open the {person_l}, untick some of this {session_l}'s test {slot_pl} and save. For example ({slot_pl} being tested for): {sample}"
  },
  "health_thi_qua_tran": {
    "vi": "{n} {person_l} đăng ký thi quá {tran} {slot_l}, thường do danh sách {slot_l} vừa được sửa ở màn Quản lý {slot_sl} & dự trữ. Thi thêm {slot_l} là được xét ưu tiên ở thêm chỗ, không công bằng với {person_l} khác. Sửa ở màn Nhập tại chỗ: mở {person_l} đó, bỏ bớt {slot_sl} dự thi rồi lưu. Ví dụ (số {slot_l} đang thi): {sample}",
    "en": "{n} {person_l}(s) are signed up to test for more than {tran} {slot_pl}, usually because the {slot_l} list was just edited in {slot_p} & reserves. Testing for extra {slot_pl} gives them priority in more places, which is unfair to others. Fix it in the Kiosk entry tab: open the {person_l}, untick some test {slot_pl} and save. For example ({slot_pl} being tested for): {sample}"
  },
  "health_vi_pham_clb_suc_chua_sai": {
    "vi": "{n} {slot_l} có sức chứa không hợp lệ (sức chứa phải lớn hơn 0, suất dự trữ từ 0 tới sức chứa). Sửa ở màn Quản lý {slot_sl} & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} {slot_l}(s) have invalid capacity (capacity must be above 0, reserve seats between 0 and capacity). Fix them in {slot_p} & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
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
    "vi": "Bảng {bang} có dữ liệu của {n} mã {person_l} không còn tồn tại. Tạo lại {person_l} có mã đó, hoặc bấm \"Xoá toàn bộ {person_l} (giữ {slot_sl})\" ở màn Quản lý {slot_sl} & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} {person_l} ID(s) that no longer exist. Recreate {person_la} with that ID, or click \"Delete all {person_pl} (keep {slot_pl})\" in {slot_p} & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_mo_coi_clb": {
    "vi": "Bảng {bang} có dữ liệu của {n} mã {slot_l} không còn tồn tại. Tạo lại {slot_l} có mã đó ở màn Quản lý {slot_sl} & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} {slot_l} ID(s) that no longer exist. Recreate {slot_la} with that ID in {slot_p} & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
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
    "vi": "Nhãn dự trữ \"{reserve_group}\" đang gán cho {n} {person_l} nhưng không {slot_sl} nào dùng nhãn này, có thể do gõ sai (ví dụ: {sample}). Các {person_l} này sẽ không được ưu tiên ở đâu. Sửa ở thẻ Quản lý: tìm {person_l}, đánh dấu, để trống ô nhãn rồi bấm \"Gán cho {person_l} đã đánh dấu\".",
    "en": "The reserve label \"{reserve_group}\" is given to {n} {person_l}(s) but no {slot_l} uses it, which may be a typo (for example: {sample}). These {person_pl} won't get priority anywhere. To fix it on the Admin tab: find the {person_pl}, tick them, leave the label box empty, and click \"Assign to ticked {person_pl}\"."
  },
  "health_club_reserve_no_group": {
    "vi": "{slot_s} {club_id} có {reserve_capacity} suất dự trữ nhưng chưa có nhãn dự trữ, nên các suất này sẽ thành suất thường.",
    "en": "{slot} {club_id} has {reserve_capacity} reserve seat(s) but no reserve label, so those seats will become regular seats."
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
    "vi": "Các {slot_l} chưa khai {session_l} có tổng {n_seats} chỗ, trong khi {n_students} {person_l} xếp nguyện vọng vào các {slot_l} này. Ít nhất {n_short} {person_l} chắc chắn không có chỗ ở nhóm này. Các {slot_l} chưa khai {session_l} được xếp chung như một {session_l} riêng. Hãy khai {session_l} cho chúng ở màn Quản lý {slot_sl} & dự trữ, tăng sức chứa, hoặc chấp nhận.",
    "en": "{slot_p} with no {session_l} set have {n_seats} seats in total, but {n_students} {person_l}(s) ranked these {slot_pl}. At least {n_short} {person_l}(s) will certainly get no seat among them. {slot_p} with no {session_l} set are matched together as one separate {session_l}. Set their {session_l} in {slot_p} & reserves, raise capacity, or accept it."
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
    "vi": "Sheet \"{sheet}\", cột {cot}: không đúng chỗ trong nhóm \"{nhom}\". Mỗi nhóm có các cột giống nhau, theo đúng thứ tự ở hàng 2 của sổ mẫu. Có thể một cột đã bị chèn hay đổi tên. Hãy tải sổ mẫu và điền lại vào đúng cột.",
    "en": "Sheet \"{sheet}\", column {cot}: it doesn't belong in the group \"{nhom}\". Every group has the same columns, in the order shown in row 2 of the template. A column may have been inserted or renamed. Download the template and fill it in again in the right columns."
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
  "so_nhap_canh_bao_xoa_diem": {
    "vi": "{n} {score_l} đã chấm trong phần mềm sẽ bị xoá, vì sổ ghi \"thi\" (chưa có {score_l}) ở các ô đó. Muốn giữ {score_l} thì xuất lại dữ liệu đầu vào thành sổ mới rồi sửa trên sổ đó.",
    "en": "{n} {score_l}(s) already entered in the app will be removed, because the workbook says \"thi\" (no {score_l} yet) in those cells. To keep them, export the current input data to a new workbook and edit that one."
  },
  "so_nhap_canh_bao_bo_nhom": {
    "vi": "{n} {person_l} đang có {group} sẽ bị bỏ nhóm, vì ô {group} của những {person_l} đó trong sổ để trống.",
    "en": "{n} {person_l}(s) who currently have a priority group will lose it, because their {group_v} cell in the workbook is empty."
  },
  "so_nhap_canh_bao_clb_ngoai_so": {
    "vi": "{n} {slot_sl} có trong phần mềm nhưng không có trong sổ ({ten}). Chúng vẫn được giữ. Nếu đó là {slot_sl} vừa đổi tên thì giữ nguyên Mã CLB khi đổi tên, rồi xoá {slot_sl} thừa ở thẻ 04.",
    "en": "{n} {slot_l}(s) are in the app but not in the workbook ({ten}). They are kept. If one was just renamed, keep its Mã CLB when renaming, then delete the leftover {slot_l} on tab 04."
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
  "ws_loi_khong_ro": {
    "vi": "Không thực hiện được thao tác với không gian làm việc. Hãy thử lại.",
    "en": "Couldn't complete the workspace operation. Try again."
  }
};
