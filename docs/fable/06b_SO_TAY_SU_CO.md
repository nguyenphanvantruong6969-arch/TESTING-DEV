# Sổ tay sự cố: khi có người làm nhầm trong một đợt xếp CLB (bản nháp)

> Bản nháp 14/11/2026, mục FA-SC. Dành cho IT, giáo viên CLB, giáo viên chủ nhiệm (GVCN) và giáo viên phụ trách ECA.
> Viết theo cách phần mềm ĐANG chạy. Chỗ nào ghi **CHỜ QUYẾT ĐỊNH** là nhà trường chưa chốt luật (D-SC2 đến D-SC7
> trong `06_CRISIS_MEMO.md`); khi đó làm theo cột "Tạm thời".
> Nhãn **TH**: chưa thử trên Microsoft thật. Các con số minh hoạ trong memo là **số liệu mô phỏng**, không phải số thật.

## 1. Bốn nguyên tắc

1. **Trước khi khoá, sửa thoải mái. Sau khi công bố, chỉ sửa lỗi dữ liệu có bằng chứng.** Bằng chứng là thứ hệ thống
   đã ghi (giờ nộp của Forms, dòng cảnh báo của bộ chuyển đổi), không phải lời kể.
2. **Không sửa tay kết quả.** Sai thì sửa dữ liệu đầu vào rồi chạy lại. Bộ số bốc thăm đã khoá được giữ nguyên, lịch sử
   chạy thêm một dòng.
3. **Mỗi lần sửa tay đều ghi vào Nhật ký sự cố** (mẫu ở mục 9): ai, lúc nào, sửa gì, vì sao, ai duyệt.
4. **Đọc hết danh sách cảnh báo.** Hầu hết sự cố dưới đây chỉ lộ ra ở một dòng cảnh báo.

## 2. Trước khi khoá đăng ký

| Dấu hiệu | Kiểm gì | Làm gì | Ai quyết | Nói gì với em |
|---|---|---|---|---|
| Em nói "em thi nhầm CLB" | Trong danh sách cảnh báo của bộ chuyển đổi, tìm email của em: có dòng "làm bài thi nhưng KHÔNG xếp CLB này" và dòng "NOT_ATTEMPTED" cho CLB em định thi | **CHỜ QUYẾT ĐỊNH D-SC2.** Tạm thời: báo giáo viên CLB em định thi; nếu được thi lại thì dùng đề khác, ghi nhật ký | Giáo viên CLB, giáo viên ECA | "Bài em làm ở CLB kia không tính vì em không xếp CLB đó. Thầy cô sẽ báo em có được thi lại không trước ngày …" |
| Em nói "em làm bài rồi mà chưa thấy Đã làm" | Trạng thái có thể chậm vài phút (TH). Giáo viên CLB mở Responses xem có phiếu của em không | Có phiếu: không làm gì. Không có: em làm bài trước hạn | Giáo viên CLB | "Hệ thống đã nhận bài của em" hoặc "Chưa có bài, em làm lại trước …" |
| Phiếu thi có email lạ ("không có trong danh sách đăng ký") | Email đó của ai. Thường là em dùng tài khoản cá nhân | Trước khoá: em đăng nhập tài khoản trường và làm lại nếu Forms còn cho. Nếu không: **CHỜ QUYẾT ĐỊNH D-SC2**, tạm thời giáo viên CLB xác nhận bằng văn bản rồi IT ghi nhật ký | Giáo viên CLB | "Bài thi phải làm bằng tài khoản trường. Thầy cô đang xác nhận bài của em" |
| Em nói "bài của em bị ghi cho bạn khác" (máy chung còn đăng nhập) | Hệ thống **không** tự phát hiện. Hỏi cả hai em; xem giờ nộp so với giờ học | Cả hai em xác nhận trước giáo viên CLB; IT ghi nhật ký. Không tự chuyển điểm khi chỉ một em nói | Giáo viên CLB + giáo viên ECA | "Thầy cô cần cả hai bạn xác nhận. Lần sau nhớ đăng xuất máy chung" |
| Em muốn đổi nguyện vọng, huy chương | Còn hạn không | Còn hạn: em nộp lại, phiếu cuối cùng được tính. Hết hạn: không đổi | Không cần duyệt | "Phiếu nộp cuối cùng trước hạn là phiếu được tính" |
| Em xếp CLB Tự do lên đầu | Hệ thống **không** cảnh báo. CLB Tự do luôn nhận em, nên các nguyện vọng phía dưới không bao giờ được xét | Nhắc cả lớp một câu trước hạn | GVCN | "CLB Tự do luôn nhận em. Chỉ đặt lên đầu nếu đó thật sự là CLB em thích nhất" |
| Em chưa đăng ký (ốm, không có máy) | Danh sách em chưa đăng ký theo lớp (TH) | GVCN nhắc; cho em dùng máy của trường. Hết hạn mà chưa có phiếu: **CHỜ QUYẾT ĐỊNH D-SC5** | GVCN, giáo viên ECA | "Em chưa có phiếu. Em không đăng ký thì sẽ không có tên trong lần xếp" |
| Cán sự CLB (được giữ chỗ) quên xếp CLB của mình | Cảnh báo "giữ chỗ … không xếp CLB đó" (chỉ IT thấy) | Báo giáo viên CLB; em nộp lại trước hạn | Giáo viên CLB | "Em phải xếp CLB của mình trong nguyện vọng thì chỗ giữ mới có hiệu lực" |

## 3. Khi chuyển đổi và nạp dữ liệu (IT)

| Dấu hiệu | Nguyên nhân thường gặp | Làm gì |
|---|---|---|
| Kiosk không cho nhập sổ, lỗi "trùng mã học sinh" | Đường B: một em gõ nhầm mã thành mã của bạn. **Một em gõ sai là cả sổ không nạp được** | Mở tệp đăng ký, tìm hai email cùng một mã; đối chiếu danh sách trường; sửa mã trong tệp xuất, ghi nhật ký; chuyển đổi lại |
| Nạp được nhưng có mã học sinh lạ | Em gõ sai mã, không trùng ai. Hệ thống **không** báo | Trước khi chạy: so cột mã với danh sách trường. Em bị ghi dưới mã sai sẽ không ai tìm thấy kết quả |
| Lần chạy bị chặn: "CLB Tuyển chọn chưa có điểm" | Quên tệp bài thi của CLB đó, hoặc biểu mẫu để Record name TẮT nên phiếu không có email | Xuất lại tệp bài thi; nếu Record name tắt thì bài thi đó không dùng được, báo giáo viên ECA |
| Lần chạy bị chặn vì huy chương của một em | Một giá trị huy chương sai. **Một em sai là cả trường không chạy được** (**CHỜ QUYẾT ĐỊNH D-SC4**) | Sửa em đó ở thẻ Quản lý, chạy lại |
| Rất nhiều dòng "NOT_ATTEMPTED" | Bình thường nếu em không thi. Bất thường nếu cả một CLB | Kiểm tệp bài thi của CLB đó có đủ không |
| Tóm tắt số học sinh không khớp | Nạp nhầm cơ sở, nhầm không gian làm việc | Dừng. Kiểm tên không gian làm việc và `--co-so` trước khi chạy |

Nạp cùng một sổ hai lần không làm hỏng dữ liệu (đã diễn tập trên dữ liệu giả: kết quả giống hệt).

## 4. Trước khi công bố (bảng kiểm, hai người cùng ký)

- [ ] Đã đọc hết cảnh báo của bộ chuyển đổi và của kiosk; mỗi dòng đã có người xử lý hoặc ghi "chấp nhận".
- [ ] Số học sinh trong kiosk = số em trên danh sách trường trừ số em GVCN đã ký "chưa đăng ký".
- [ ] Không có mã học sinh nào ngoài danh sách trường.
- [ ] Chỉ tiêu từng CLB đã được giáo viên CLB đọc lại (gõ 2 thay vì 20 thì phần mềm vẫn chạy và không báo gì).
- [ ] Mọi em đã có lớp. Đường B không hỏi lớp: nếu chưa nạp lớp thì **toàn bộ** kết quả nằm trong `_chua_co_lop.xlsx`
      và không GVCN nào nhận được.
- [ ] Không còn dải vàng "Dữ liệu đã được sửa sau lần chạy gần nhất".
- [ ] Danh sách đã **chốt**: chạy lại sau khi công bố có thể làm em đã có chỗ bị đổi CLB.
- [ ] Tệp email–mã học sinh dùng để ghép kết quả là của đúng đợt này, đúng cơ sở này.
- [ ] Đã sao lưu thư mục không gian làm việc ra một nơi khác máy IT (theo quy định của trường).

## 5. Sau khi công bố

| Dấu hiệu | Kiểm gì | Làm gì | Ai quyết | Nói gì với em |
|---|---|---|---|---|
| Em nói "em bấm nhầm, cho em đổi" | Có bằng chứng do hệ thống ghi không | **CHỜ QUYẾT ĐỊNH D-SC3.** Hiện nay: chỉ nhận lỗi dữ liệu, không nhận "bấm nhầm" | Giáo viên ECA | "Kết quả xếp theo phiếu em nộp cuối cùng trước hạn. Nhà trường chỉ sửa khi dữ liệu bị ghi sai" |
| Em nói "em có thi mà kết quả ghi chưa thi" | Tìm email em trong cảnh báo: phiếu bị bỏ vì email lạ, hay nộp hai lần | Đúng là lỗi dữ liệu: nhận khiếu nại, sửa dữ liệu, chạy lại cùng bộ số bốc thăm, ghi nhật ký | Admin | "Thầy cô đã thấy bài của em bị ghi sai tài khoản; sẽ sửa và báo lại trước ngày …" |
| Khiếu nại gõ sai mã học sinh | Phần mềm chỉ nhận khi khớp đúng một em | GVCN nộp lại giúp em trong hạn 3 ngày | Admin | — |
| Có em đến muộn, cần chạy lại | Chạy `doi_chieu_lists.py` để biết ai thay đổi | Chạy lại; xuất "Thay đổi so với lần chạy trước"; báo GVCN của **từng** em bị đổi trước khi các em nghe từ bạn | Giáo viên ECA quyết có chạy lại không | "Vì có bạn mới, một số chỗ phải xếp lại theo đúng luật. CLB của em đổi từ … sang …" |
| Em không có CLB nào mình chọn, buồn | Xem câu lý do của em | GVCN nói chuyện riêng; chỉ cho em các chỗ còn trống (vòng 2) | GVCN | "Em không làm gì sai. CLB đó nhiều bạn chọn hơn số chỗ. Các chỗ còn trống là …" |

**Cảnh báo về chạy lại (đã diễn tập trên dữ liệu giả):** trường xếp nhiều ngày thì mỗi lần chạy lại mà **số học sinh
thay đổi** (thêm một em muộn, xoá một em), số bốc thăm theo từng ngày của **mọi** em được tính lại. Em đã công bố có thể
đổi CLB dù em mới không tranh chỗ của ai. Vì vậy sau khi công bố: ưu tiên xử lý em muộn bằng chỗ còn trống (vòng 2) hoặc
danh sách chờ; chỉ chạy lại khi giáo viên ECA quyết, và luôn xuất "Thay đổi so với lần chạy trước". Chạy lại với **cùng**
danh sách học sinh (chỉ sửa điểm, nguyện vọng của một em) thì không bị hiện tượng này.

**Không làm:** đổi hạt giống hoặc bấm "Vẽ lại số bốc thăm" giữa đợt; sửa tay kết quả; nhận đổi chỗ hai em tự thoả thuận.

## 6. Điểm danh và danh sách chờ (3 buổi đầu)

Cách phần mềm chạy hiện nay: đổi một ô là **lưu ngay, không hỏi lại**. Ô "vắng không phép" thứ hai của một em sẽ
**giải phóng chỗ của em và mời ngay em đầu danh sách chờ**. Sửa lại ô đó **không** trả chỗ cho em.

| Tình huống | Làm gì |
|---|---|
| Chưa chắc em vắng có phép hay không | Chọn "vắng có phép" hoặc để trống, hỏi GVCN, sửa sau. Không chọn "vắng không phép" khi chưa chắc |
| Đã chọn nhầm và em bị giải phóng chỗ | Dừng, **không** báo em trên danh sách chờ. Báo admin ngay. Admin ghi nhật ký; phần mềm chưa có nút hoàn tác (đề xuất FA-SC-5), nên phải xử lý tay theo quyết định của giáo viên ECA |
| Em ốm 2 buổi đầu | GVCN chuyển giấy phép cho giáo viên CLB **trước** buổi 2 |
| Em đến nhầm CLB hoặc nhầm phòng | Giáo viên CLB thấy "em không có tên" thì báo GVCN ngay trong buổi; không ghi em vắng ở CLB đúng khi chưa hỏi |
| Em được mời từ danh sách chờ | Chỉ admin ghi "nhận / từ chối / hết hạn". Em trả lời bằng một kênh duy nhất, có hạn rõ (**CHỜ QUYẾT ĐỊNH**); nhận rồi thì chỗ cũ của em được mời cho bạn khác ngay |
| Em tự bỏ CLB | Em báo giáo viên CLB; đừng để chỗ trống 2–3 tuần |

## 7. Sự cố máy và hệ thống

| Sự cố | Phần mềm làm gì | Làm gì |
|---|---|---|
| Lỗi hoặc mất điện giữa lần chạy | Không ghi gì; kết quả cũ và lịch sử giữ nguyên (đã diễn tập trên dữ liệu giả) | Mở lại, chạy lại |
| Lỡ xoá không gian làm việc | Chuyển vào thùng rác, không xoá hẳn; không xoá được cái đang mở | Khôi phục từ thùng rác |
| Mất hoặc hỏng máy IT | Không có bản sao ngoài máy trừ khi đã làm ở mục 4 | Khôi phục từ bản sao lưu; báo người phụ trách dữ liệu của trường vì máy có tên và email học sinh |
| Forms hoặc M365 ngừng trong ngày thi | — | Giáo viên ECA lùi hạn bài thi cho **mọi** em, thông báo một lần; không mở riêng cho từng em |
| Gửi nhầm tệp lớp cho người khác | Tệp không có điểm và số bốc thăm, nhưng có tên và CLB của các em | Nhờ người nhận xoá; báo người phụ trách dữ liệu; ghi nhật ký |

## 8. Những câu nên nói trước đợt (GVCN đọc cho lớp)

1. "Xếp đúng thứ tự em thích. Xếp CLB khó lên đầu **không** làm em mất cơ hội ở CLB sau."
2. "CLB Tự do luôn nhận em. Đặt nó lên đầu thì các CLB phía dưới sẽ không được xét."
3. "Muốn vào CLB Tuyển chọn thì phải làm bài thi của **đúng** CLB đó, bằng **tài khoản trường của em**, và bấm Nộp."
4. "Mỗi bài thi chỉ làm một lần. Xem kỹ tên CLB ở đầu bài trước khi bắt đầu."
5. "Phiếu đăng ký nộp cuối cùng trước hạn là phiếu được tính. Hạn là **thứ …, ngày …, … giờ**."
6. "Dùng máy chung thì đăng xuất khi xong."
7. "Sau khi có kết quả, nhà trường chỉ sửa khi dữ liệu bị ghi sai, trong 3 ngày."

## 9. Mẫu Nhật ký sự cố (mỗi sự cố một dòng; IT giữ, không đăng công khai)

| Ngày giờ | Người báo | Học sinh (mã) | Chuyện gì | Bằng chứng | Đã sửa gì | Ai duyệt | Có chạy lại không | Đã báo ai |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## 10. Còn chờ

- Quyết định D-SC2 đến D-SC7 của nhà trường (xem memo mục 9).
- Chưa thử trên Microsoft thật (TH): danh sách em chưa đăng ký, thư nhắc hạn, trạng thái "Đã làm", biểu mẫu khiếu nại.
- Đường A (app Power Apps) không nằm trong kho mã nên sổ tay này chưa kiểm được phần màn hình của app.
