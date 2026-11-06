# T4M. Phiếu phỏng vấn (GĐ2) — in ra mang theo

Mã việc: **T4M-NC**, giai đoạn GĐ2 của `T4M_KE_HOACH_NGHIEN_CUU.md`. Câu hỏi gộp từ mục 6 của kế hoạch, mục 4 và cột "Còn hỏi IT" của `T4M_KET_QUA_TAI_LIEU.md`.
Ngày gặp: ____/____/2026 · Người được hỏi (chỉ ghi chức danh): ____________________

## Mục đích và việc cần xin mang về
Buổi gặp nhằm xác định nơi app ECA lưu dữ liệu, quyền hạn của tài khoản và đường đồng bộ từ PowerSchool, để thiết kế bộ chuyển đổi giữa app và kiosk RB-DA. Các câu đánh dấu **CHẶN** là điều kiện để giai đoạn tổng hợp (GĐ4) không phải chạy theo hai nhánh giả định.
Xin mang về:
- [ ] Một tệp xuất mẫu **đã ẩn danh** (xoá tên và email thật).
- [ ] **Tên các cột** của kho dữ liệu (chép tay hoặc ảnh chụp đã che dữ liệu).

**Nhắc về riêng tư:** ghi biên bản ở ngoài kho mã. Chỉ đưa vào kho bản tóm tắt đã ẩn danh. Không commit dữ liệu thật, tenantId, địa chỉ (URL) app hay tên người.

## A. Câu hỏi cho bộ phận IT

### A1. Năm câu CHẶN (nếu IT trả lời chậm, gửi lại riêng 5 câu này theo dự phòng A)

**IT-1. [CHẶN] [NC-01]** App ECA lưu dữ liệu ở đâu: SharePoint List, Excel, Dataverse hay Dataverse for Teams? Cho em xem tên cột được không? Nếu là Dataverse for Teams, trường đã có kế hoạch nâng cấp trước 30/10/2027 chưa?
*Bối cảnh:* Dataverse for Teams không tạo môi trường mới từ 15/11/2026; kho mới thường là SharePoint List.
Trả lời: ______________________________________________________________

**IT-2. [CHẶN] [NC-02]** Tài khoản học sinh có được tạo app, flow, list thử không? Nếu không, thầy cô cấp được môi trường thử (sandbox hoặc managed developer), hoặc thêm em làm đồng sở hữu một bản sao app không?
*Bối cảnh:* Developer Plan ngừng tạo môi trường mới từ 15/11/2026, nên em không tự lập môi trường miễn phí được nữa.
Trả lời: ______________________________________________________________

**IT-3. [CHẶN] [NC-03]** Trường dùng Microsoft 365 A3 hay A5? Có mua thêm Power Apps / Power Automate Premium không?
*Bối cảnh:* gói M365 chỉ có connector chuẩn; Premium, connector tuỳ biến cần giấy phép riêng. Hồ sơ "Low" giới hạn 6.000 yêu cầu mỗi người mỗi ngày.
Trả lời: ______________________________________________________________

**IT-4. [CHẶN] [NC-08]** PowerSchool đồng bộ sang Microsoft 365 bằng đường nào (tệp CSV của School Data Sync, ClassLink, công cụ khác)? Có những thông tin nào: mã học sinh, cơ sở, khối, lớp chủ nhiệm?
*Bối cảnh:* PowerSchool không có trong danh sách nhà cung cấp OneRoster API của School Data Sync, nên đường đồng bộ thật chưa rõ.
Trả lời: ______________________________________________________________

**IT-5. [CHẶN] [NC-16]** Dữ liệu học sinh có được chép ra một máy ngoại tuyến để chạy xếp lớp không? Lưu bao lâu, ai được xem?
*Bối cảnh:* kiosk chạy ngoại tuyến trên máy Windows; cần biết điều kiện bảo vệ dữ liệu của trường.
Trả lời: ______________________________________________________________

### A2. Các câu còn lại

**IT-6. [NC-01, NC-09]** Admin hiện xuất danh sách đăng ký bằng cách nào (nút Export của Lists hay cách khác)? Tệp có giữ dấu tiếng Việt không? Xin một tệp mẫu đã ẩn danh.
*Bối cảnh:* Lists xuất CSV tối đa 30.000 dòng; cách xuất cột Choice, Lookup, Person chưa được tài liệu mô tả.
Trả lời: ______________________________________________________________

**IT-7. [NC-07]** Cấp độ tiếng Nhật của từng học sinh lưu ở đâu (kho app, PowerSchool, Entra)? Đồng bộ tự động hay nhập tay?
*Bối cảnh:* màn hình gói lọc theo cấp độ, nên cấp độ phải có sẵn trong một nguồn mà app đọc được.
Trả lời: ______________________________________________________________

**IT-8. [NC-14]** Tenant có chính sách chặn connector (DLP) không, nhất là SharePoint, Excel Online, Teams, Outlook?
*Bối cảnh:* vi phạm DLP làm app hoặc flow bị treo trong 1 đến 24 giờ.
Trả lời: ______________________________________________________________

**IT-9. [NC-15]** Máy IT có chạy được tệp `.exe` chưa ký số không? Có SmartScreen, Intune hay AppLocker chặn không, hay cần đưa vào danh sách cho phép?
*Bối cảnh:* SmartScreen cảnh báo tệp chưa có danh tiếng; người chạy kiosk là bộ phận IT.
Trả lời: ______________________________________________________________

**IT-10. [NC-20]** Mỗi cơ sở dùng chung một app hay app riêng? Mỗi cơ sở xếp riêng thì dữ liệu tách theo cột nào?
*Bối cảnh:* kiosk xếp từng cơ sở riêng; cần biết bộ lọc Cơ sở hoạt động thế nào.
Trả lời: ______________________________________________________________

**IT-11. [NC-13]** Các flow hiện có do ai sở hữu (tài khoản cá nhân hay tài khoản dịch vụ)?
*Bối cảnh:* flow không chạy 90 ngày có thể bị tắt; chủ flow nghỉ thì flow về hồ sơ Low.
Trả lời: ______________________________________________________________

**IT-12. [NC-12]** Danh sách giáo viên chủ nhiệm (tên, email, lớp) lấy từ đâu?
*Bối cảnh:* kết quả trả theo lớp chủ nhiệm bằng tệp (kiosk có `export_theo_lop`) hoặc Teams/Outlook; cần nguồn danh sách.
Trả lời: ______________________________________________________________

**IT-13. [NC-04]** Các cột bộ lọc của app (Cơ sở, Cấp học, Khối) hiện kiểu gì: chữ, số hay Choice?
*Bối cảnh:* với SharePoint, chỉ một số phép lọc trên cột chữ được uỷ quyền; ngoài đó app chỉ xử lý 500 dòng (tối đa 10.000).
Trả lời: ______________________________________________________________

## B. Câu hỏi cho giáo viên ECA

**ECA-1. [NC-10]** "Khoá" đăng ký làm thế nào? Sau khi khoá còn nhận em đến muộn không?
*Bối cảnh:* kiosk cần biết quy trình để xử lý đăng ký muộn.
Trả lời: ______________________________________________________________

**ECA-2. [bối cảnh]** Khi lớp quá đông, hiện nay thầy cô chia thế nào? Mất bao lâu?
*Bối cảnh:* để so sánh trước và sau khi dùng RB-DA.
Trả lời: ______________________________________________________________

**ECA-3. [đầu vào Sổ nhập]** Chỉ tiêu mỗi lớp, và mỗi cấp tiếng Nhật, là bao nhiêu? Ai quyết định?
*Bối cảnh:* chỉ tiêu là đầu vào bắt buộc của Sổ nhập CLB.
Trả lời: ______________________________________________________________

**ECA-4. [pha 1]** Ngoài tiếng Nhật, còn ECA nào là gói nhiều buổi không?
*Bối cảnh:* gói nhiều buổi không biểu diễn được bằng Sổ nhập hiện tại (mỗi CLB một buổi).
Trả lời: ______________________________________________________________

**ECA-5. [NC-17]** Đổi lớp và rút giữa kỳ xử lý thế nào? Bao lâu xếp lại một lần?
*Bối cảnh:* ảnh hưởng đến thiết kế xử lý thay đổi theo thời gian.
Trả lời: ______________________________________________________________

**ECA-6. [giai đoạn 2]** Thầy cô muốn học sinh xếp hạng mấy nguyện vọng mỗi buổi? (Kế hoạch đề xuất Top 3.)
*Bối cảnh:* app hiện chỉ cho chọn một lựa chọn mỗi buổi, không xếp hạng.
Trả lời: ______________________________________________________________

**ECA-7. [NC-12]** Kết quả gửi giáo viên chủ nhiệm theo dạng nào thì tiện nhất (Excel theo lớp, Teams, email)?
*Bối cảnh:* hiện giáo viên chủ nhiệm là người báo kết quả cho học sinh.
Trả lời: ______________________________________________________________

**ECA-8. [lịch]** Đợt đăng ký tới vào khi nào? Đăng ký mở bao nhiêu ngày?
*Bối cảnh:* để xếp lịch thử với dữ liệu thật.
Trả lời: ______________________________________________________________

### B2. Thi tuyển (quyết định 05/11/2026: trường theo RB-DA)

**ECA-9. [NC-25]** CLB nào sẽ thi? Mỗi CLB thi một biểu mẫu riêng, học sinh mở từ app (cổng thi, Truong chọn 06/11/2026): giáo viên CLB có đồng ý tự giữ biểu mẫu của mình và bấm "Post scores" khi hết đợt không?
*Bối cảnh:* Microsoft Forms Quiz, mỗi CLB một biểu mẫu 5 đến 10 câu, không câu cổng (`T4M_CONG_THI.md`); em chỉ thấy CLB có thi mà em đã chọn trong Top 3; điểm xếp do bộ chuyển đổi chấm lại, ghép qua email trường.
Trả lời: ______________________________________________________________

**ECA-10. [NC-26]** Thi ở đâu, có giám sát không? Mỗi buổi một đề hay dùng chung (lộ đề)? Có thể dùng chế độ Take a Test (máy Windows) không?
*Bối cảnh:* Forms có hẹn giờ, một lần nộp, Take a Test; bài làm ở nhà thì khó công bằng.
Trả lời: ______________________________________________________________

**ECA-11. [NC-26]** Em vắng thi xếp thế nào: sau mọi em có điểm, hay như CLB không thi? Thang điểm bao nhiêu? Ai giữ đề và đáp án?
*Bối cảnh:* hoà điểm phân bằng bốc thăm STB; đáp án phải giữ kín đến hết đợt.
Trả lời: ______________________________________________________________

**IT-14. [NC-23]** Tenant có hạn chế Microsoft Forms không (tắt chia sẻ ngoài, tắt Quick Import, chặn Take a Test)? Giáo viên tạo được Forms dạng Quiz bằng tài khoản trường chứ?
*Bối cảnh:* mỗi người tối đa 400 biểu mẫu tính cả thùng rác; tệp Quick Import phải nằm trên máy, tối đa 10 MB.
Trả lời: ______________________________________________________________

### B3. Cổng thi: câu cho IT (cách B, `T4M_CONG_THI.md`)

**IT-15. [NC-05]** IT có sửa được app ECA để thêm một màn "Thi tuyển" (danh sách CLB có thi kèm nút Làm bài và trạng thái "Đã làm") trên bản sao trước không? Nếu không: chấp nhận trang SharePoint của đợt (danh sách CLB kèm link, khung xem list `BaiThi` lọc [Me]) không?
*Bối cảnh:* đặc tả màn ở `T4M_DAC_TA_SUA_APP.md` §10 (R15 đến R24); phương án lui ở `T4M_CONG_THI.md` §7.
Trả lời: ______________________________________________________________

**IT-16. [NC-23]** Ai sở hữu khoảng 10 đến 20 biểu mẫu thi: một tài khoản chung của IT hay mỗi giáo viên CLB? Có tài khoản nào gần chạm 400 biểu mẫu (tính cả thùng rác) không?
*Bối cảnh:* flow "Đã làm" phải đọc được biểu mẫu; giáo viên rời trường thì biểu mẫu theo tài khoản đó.
Trả lời: ______________________________________________________________

**IT-17. [NC-13]** Có tài khoản dịch vụ làm chủ khoảng 10 đến 20 flow nhỏ "Đã làm" không? Đợt thi mở mấy ngày?
*Bối cảnh:* ước lượng khoảng 9.000 lượt mỗi đợt, hạn mức 6.000 lượt mỗi người mỗi ngày tính cộng dồn theo chủ flow (`T4M_FLOW_DA_LAM.md` §5); mở vài ngày thì vừa, một ngày cao điểm có thể chạm trần.
Trả lời: ______________________________________________________________

**IT-18. [NC-04]** Đặt được list `BaiThi` chỉ đọc với học sinh (chỉ flow ghi) và list `CLB` chỉ đọc không? DLP có cho phép Forms và SharePoint chung một flow không?
*Bối cảnh:* học sinh ghi được `BaiThi` thì tự đánh "Đã làm" được (R24); flow chỉ dùng connector chuẩn.
Trả lời: ______________________________________________________________

## Sau buổi gặp
- [ ] **Mốc C2** (mục 5 của kế hoạch): có sơ đồ cột của kho dữ liệu **hoặc** tệp mẫu đã ẩn danh; có câu trả lời IT-5 (NC-16).
- [ ] Dự phòng áp dụng: [ ] không cần · [ ] **A** (IT chậm quá 1 tuần: gửi lại 5 câu CHẶN IT-1 đến IT-5) · [ ] **B** (không có quyền tạo app hay flow thử: bỏ GĐ3, dùng bản vẽ màn hình, tệp Excel giả, hướng dẫn 1 trang cho IT).
- [ ] Biên bản gốc đã cất ngoài kho; không có tên, email, tenantId hay URL trong bản tóm tắt.
- [ ] Dán vào phiên kế tiếp: **bản tóm tắt ẩn danh** (câu trả lời theo mã NC, sơ đồ cột, kết luận dự phòng A hay B).
