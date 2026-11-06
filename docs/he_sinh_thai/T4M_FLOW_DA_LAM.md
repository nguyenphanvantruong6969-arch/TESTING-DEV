# T4M. Flow "Đã làm bài": ghi trạng thái thi vào list BaiThi (T4M-M5)

> Chỉ tài liệu (06/11/2026). Chưa thử trên Power Automate thật: mọi bước nhãn **TH**, tên hành động và biểu thức nhãn **GĐ**. Giới hạn nhãn **ĐXM** (`T4M_KET_QUA_TAI_LIEU.md` NC-13, §7.1, đọc 05/11/2026). Số ước tính nhãn **ƯL**. Không có dữ liệu thật, tenantId, URL, tên người.
> Thiết kế tổng thể: `T4M_CONG_THI.md`. Màn trong app: `T4M_DAC_TA_SUA_APP.md` §10. Mức điểm **5a**: flow **không** chép điểm.

## 1. Việc của flow và nguyên tắc
1. Mỗi biểu mẫu thi (một CLB) có **một flow giống nhau**: khi có bài nộp thì thêm **một dòng** vào list `BaiThi`. Chỉ vậy.
2. **Chỉ connector chuẩn:** Microsoft Forms và SharePoint. Không HTTP, không connector tuỳ biến (Premium).
3. Forms connector chỉ có trigger *When a new response is submitted* và hai hành động đọc *Get form details*, *Get response details*; Standard trong Power Automate (KQ §7.1, ĐXM). Điểm Quiz không có trong dữ liệu trả về (nguồn cộng đồng, TT-CXM): flow **không** đọc điểm, đúng mức 5a.
4. **Chủ flow là tài khoản dịch vụ của IT** (NC-13): chủ rời tổ chức thì flow về hồ sơ Low; 90 ngày không chạy có thể bị tắt. Có tài khoản dịch vụ hay không: **HỎI-IT**.
5. Flow không chạm kiosk, không đọc đáp án, không ghi vào list `ECA`.

## 2. Đầu vào cần có trước
| Thứ | Nguồn | Ghi chú |
|---|---|---|
| Biểu mẫu thi từng CLB | Giáo viên CLB, dựng từ tệp Quick Import (`tao_mau_forms.py --moi-clb`, T4M-Q4a) | Settings: Record name BẬT, One response per person BẬT, Show results TẮT |
| List `BaiThi` | IT tạo | Cột: `Email` (văn bản), `ClubId` (văn bản), `ResponseId` (văn bản), `NopLuc` (ngày giờ). Học sinh chỉ đọc hoặc không có quyền; chỉ tài khoản dịch vụ ghi (HỎI-IT) |
| `Form Id` của từng biểu mẫu | Biểu mẫu cá nhân: chọn trong trình đơn thả xuống của trigger. **Biểu mẫu nhóm (Teams): dán tay Form Id** (KQ §7.1, ĐXM) | Ghi vào bảng đối chiếu ở §4 |
| Quyền | Tài khoản dịch vụ phải **mở được** biểu mẫu (là chủ hoặc được chia sẻ quyền chủ) | Biểu mẫu do giáo viên sở hữu: nhờ giáo viên chia sẻ **Collaborate** cho tài khoản dịch vụ, hoặc IT sở hữu mọi biểu mẫu (HỎI-IT, T4M_CONG_THI.md §3) |

## 3. Flow mẫu (GĐ, TH)

Tên: `DaLam_<ClubId>`. Chạy tự động, không cần ai bấm.

| # | Hành động | Cấu hình | Ghi chú |
|---|---|---|---|
| 1 | Forms **When a new response is submitted** | `Form Id` = biểu mẫu của CLB | Trigger kiểu webhook, báo gần như ngay (T4M_CONG_THI.md §4.4; ĐXM bảng throttling của connector) |
| 2 | Forms **Get response details** | `Form Id` như bước 1; `Response Id` = giá trị động từ trigger | Trả `responder` (email), `submitDate` (GĐ tên trường) |
| 3 | SharePoint **Get items** (list `BaiThi`) | Lọc OData `ResponseId eq '<id>'` (so bằng, uỷ quyền được); Top Count = 1 | Chống dòng trùng khi trigger chạy lại (GĐ). Bước tuỳ chọn: bỏ đi nếu muốn đúng 3 hành động |
| 4 | Điều kiện: số mục của bước 3 bằng 0 | | Có rồi thì dừng, không ghi lần hai |
| 5 | SharePoint **Create item** (list `BaiThi`) | `Email` = chữ thường của `responder` (hàm `toLower`); `ClubId` = **hằng chữ cố định** của flow này (vd. `clb_x`); `ResponseId` = giá trị bước 2; `NopLuc` = `submitDate` | `ClubId` đặt cứng theo biểu mẫu nên không phụ thuộc tiêu đề câu hỏi |
| 6 | (Nhánh lỗi, §6) khi bước 2 hoặc 5 lỗi | Run after: has failed | Ghi nhật ký, báo IT |

Lưu ý:
- `ClubId` phải **trùng chính xác** mã trong `CLB.csv` và trong ô `NV` (cùng chuỗi, không dấu cách thừa). Sai mã thì app không thấy "Đã làm" (R17 của `T4M_DAC_TA_SUA_APP.md`).
- Email chữ thường để khớp `Lower(User().Email)` ở app và để bộ chuyển đổi (đọc theo email chữ thường) đối chiếu được.
- Flow **không** đọc câu trả lời và **không** lưu điểm: dòng `BaiThi` không chứa nội dung bài làm.

## 4. Nhân flow cho nhiều biểu mẫu
1. Dựng và **thử trọn** một flow mẫu (§7), rồi **Save as** (bản sao) hoặc **Export > Package (.zip)** rồi Import cho các CLB còn lại (TH: tên tuỳ chọn theo giao diện lúc làm).
2. Mỗi bản sao đổi đúng **hai thứ**: `Form Id` ở bước 1 và 2, và hằng `ClubId` ở bước 5. Không đổi gì khác.
3. Giữ bảng đối chiếu (bản của IT, không đưa vào kho mã):

| Flow | ClubId | Form Id | Chủ biểu mẫu | Đã thử (ngày) |
|---|---|---|---|---|
| `DaLam_<ClubId>` | | | | |

4. Soát sau khi nhân: mỗi `Form Id` xuất hiện **đúng một lần**; mỗi `ClubId` có đúng một flow (hai flow cùng biểu mẫu sẽ ghi dòng trùng).
5. Mỗi biểu mẫu một flow (trigger nhận một Form Id, ĐXM): 10 CLB có thi = 10 flow. Số CLB có thi hiện tại: `de_thi.json` (10 CLB theo `T4M_DO_MO_PHONG.md`).

## 5. Hạn mức (ĐXM) và ước tính (ƯL)
| Giới hạn | Số | Ước tính cho đợt (ƯL) |
|---|---|---|
| Hồ sơ Low, Office 365 (NC-13) | 6.000 yêu cầu mỗi người mỗi 24 giờ; chuyển tiếp 10.000 mỗi flow | Tính theo **chủ flow**: mọi flow của một tài khoản dịch vụ **cộng dồn** |
| Connector Forms | 300 lệnh mỗi 60 giây | Xa mức nếu bài nộp rải đều |
| Hành động mỗi bài nộp | | **3 đến 4** (trigger tính 0 hoặc 1: chưa rõ, GĐ; Get details; [Get items]; Create item) |
| Tổng | | 1.500 em × 2 bài = 3.000 bài; × 3 = **9.000**, × 4 = **12.000** hành động cả đợt |

- Nếu cả đợt mở **nhiều ngày**: chia ra mỗi ngày dưới 6.000 là vừa. Nếu học sinh nộp dồn trong **một ngày** (vd. sát hạn), 9.000 đến 12.000 **vượt** 6.000 (ƯL): flow bị chậm hoặc bị điều tiết, dòng `BaiThi` đến muộn.
- Giảm: (a) bỏ bước 3 và 4 (kiểm trùng; còn 3 hành động); (b) hai tài khoản dịch vụ, mỗi tài khoản chủ một nửa số flow (HỎI-IT, có thể cần giấy phép); (c) đặt hạn thi rải nhiều ngày theo CLB hoặc theo khối; (d) chấp nhận trễ rồi dùng đường thủ công §8.
- Số thật chỉ có sau chạy thử: đo ở §7, điền vào HDT; **không** coi số ước tính là số đo.

## 6. Xử lý lỗi
1. **Cấu hình mỗi hành động:** thử lại tự động (retry policy mặc định/mũ) cho bước 2 và 5 (TH).
2. **Nhánh lỗi (Run after: has failed)** của bước 2 và 5: SharePoint **Create item** vào list `NHAT_KY_DA_LAM` (`ClubId`, `ResponseId`, giờ, "lỗi"); không chứa email hay nội dung bài. Nếu chính việc ghi nhật ký cũng lỗi thì dựa vào lịch sử chạy của flow.
3. **Báo IT:** một email tóm tắt hằng ngày từ flow riêng (tuỳ chọn) hoặc IT xem **Run history** mỗi sáng trong đợt mở.
4. **Flow bị tắt** (90 ngày không chạy, chủ rời, DLP): bài nộp trong lúc tắt **không bù lại tự động** (GĐ). Việc phải làm: bật lại trước đợt; soát danh sách flow "On" ngày mở; sau đợt đối chiếu §8.
5. **DLP (NC-14):** Forms và SharePoint đều Standard; nếu chính sách trường xếp vào hai nhóm không trộn được thì flow bị treo/cách ly. **HỎI-IT trước khi dựng.** Không nhờ admin nới DLP chỉ cho flow này; nếu bị chặn thì dùng §8.
6. **Trễ trạng thái:** app có nút Làm mới (mục 10.2 của đặc tả app); học sinh nộp xong mà chưa thấy "Đã làm" thì chờ rồi bấm lại. Việc thi không phụ thuộc trạng thái (Forms đã ghi bài).

## 7. Thử (TH, chưa làm)
- Môi trường thử (NC-02): một biểu mẫu thử, một list `BaiThi_THU`, tài khoản thử; **không** dùng biểu mẫu hay dữ liệu thật.
- Pass: nộp 1 bài thì có **đúng 1 dòng** với `Email` chữ thường, `ClubId` đúng, `NopLuc` hợp lý; nộp 3 bài từ 3 tài khoản thì 3 dòng; thử ghi thất bại cố ý thì có dòng nhật ký.
- Đo: thời gian từ lúc nộp đến lúc dòng xuất hiện (ghi vào bảng kết quả, HDT); số hành động thật mỗi bài (so với §5).
- Fail: ghi nguyên văn thông báo lỗi.

## 8. Đường thủ công (không cần flow)
Khi flow không chạy được hoặc để đối chiếu cuối đợt:
1. Với mỗi biểu mẫu: **Responses > Open in Excel** (ĐXM), lưu mỗi CLB một tệp.
2. Chạy bộ chuyển đổi `--chi-thi` trên các tệp đó (T4M-Q4b: mỗi tệp một CLB).
3. Nếu có list `BaiThi` (chạy flow một phần): xuất CSV và chạy với `--bai-thi BaiThi.csv` (T4M-Q4c): báo bài có ở list mà thiếu ở tệp xuất và ngược lại. Báo cáo này **không đổi điểm**.
4. Không có list `BaiThi`: app không hiện "Đã làm"; nút Làm bài luôn hiện (phương án lui, `T4M_CONG_THI.md` §7) và kiểm bài thiếu bằng tệp xuất. Bài đã nộp vẫn được chấm đủ vì bộ chuyển đổi đọc thẳng từ tệp xuất.

## 9. Việc chờ (ngoài tài liệu này)
NC-02 (môi trường thử); có tài khoản dịch vụ và ai sở hữu biểu mẫu (HỎI-IT); DLP (NC-14); số bài nộp dồn một ngày thật; tên trường thật của *Get response details* (kiểm khi dựng, GĐ).
