# Nhật ký sử dụng AI trong đề tài phần mềm xếp học sinh vào câu lạc bộ

| Mục | Thông tin |
|---|---|
| **Tác giả đề tài** | Truong (học sinh) |
| **Công cụ AI** | Claude Code của hãng Anthropic. Hai loại: **Opus** dùng để lập kế hoạch, điều phối và kiểm tra lại; **Sonnet** dùng để viết mã theo kế hoạch |
| **Thời gian** | 26/08/2026 đến 10/11/2026 |
| **Nguồn của nhật ký** | Chỉ những ghi chép có sẵn trong kho mã của dự án (tệp bàn giao, nhật ký thay đổi, lịch sử lưu mã). Không lấy từ lịch sử trò chuyện |
| **Bản chi tiết** | `docs/nhat_ky_ai/NHAT_KY_AI.md` (đủ từng phiên, từng lần lưu, dành cho người cần tra cứu) |

Mọi con số kiểm thử nhắc tới trong tài liệu này đều chạy trên **dữ liệu mô phỏng**, không phải khảo sát thật. Nhật ký chỉ ghi lại việc đã làm; phần nhận xét và kết luận về đề tài do học sinh tự viết trong báo cáo.

## 1. Cách đọc tài liệu này

**Một số từ dùng trong tài liệu:**

| Từ | Nghĩa |
|---|---|
| Phiên làm việc | Một lần trò chuyện với AI, từ lúc mở đến lúc đóng |
| Phiên chính | Phiên Truong làm việc trực tiếp với AI để giao việc, bàn kế hoạch, chốt quyết định (trong bản chi tiết gọi là "phiên cha") |
| Phiên phụ | Phiên do phiên chính mở ra để làm một phần việc theo kế hoạch đã duyệt; chỉ được tóm tắt ở đây (bản chi tiết gọi là "phiên con") |
| Lần lưu mã | Một lần ghi thay đổi vào kho mã, có ngày giờ và lời mô tả |
| Nhánh | Một bản sao riêng của mã để làm việc mà không ảnh hưởng bản chính |
| Yêu cầu gộp (PR) | Đề nghị đưa thay đổi từ một nhánh vào bản chính. Chỉ Truong được quyết định gộp |
| Kiểm thử tự động | Các bài kiểm tra máy tự chạy để chắc phần mềm vẫn đúng sau mỗi lần sửa |
| Bất biến | Quy tắc không bao giờ được phá, ví dụ: cùng dữ liệu thì kết quả xếp phải giống hệt nhau |

**Ký hiệu:** chữ đặt trong ngoặc kép kiểu “...” ở mục 5 là **lời nguyên văn** của Truong được lưu trong kho mã. Mọi chỗ khác là **tóm tắt** theo ghi chép, không phải lời nguyên văn.

## 2. Tóm tắt

**Phần học sinh tự viết** (bản gốc đưa lên ngày 26/08/2026): thuật toán xếp chỗ cốt lõi, phần nối giữa giao diện và thuật toán, giao diện ban đầu (trang web, kiểu chữ, mã giao diện) và tệp đóng gói chương trình.

**Phần AI làm** (theo yêu cầu và dưới sự duyệt của Truong):

- Tìm và sửa lỗi, viết bộ kiểm thử tự động.
- Thêm tính năng mới: không gian làm việc nhiều ngành, điểm quyết tâm, lớp của học sinh, làm gọn giao diện, công cụ cho hệ thống Microsoft của trường, cơ chế xếp mới FA-DAA.
- Viết tài liệu hướng dẫn, kế hoạch và báo cáo kiểm tra.

**Vai trò của Truong:** đặt yêu cầu và mục tiêu, viết bản tầm nhìn cho cơ chế mới, duyệt từng kế hoạch, chọn phương án ở các điểm cần quyết định, cho phép hoặc từ chối các ngoại lệ với quy tắc, và quyết định gộp mã vào bản chính.

**Quy mô** (từ 24/10/2026, khi lịch sử lưu mã bắt đầu được giữ trong kho): khoảng 430 lần lưu mã, 70 phiên có ghi tên trong lịch sử lưu, 12 luồng việc có tệp bàn giao.

## 3. Dòng thời gian

| Giai đoạn | Thời gian | Việc chính |
|---|---|---|
| 1 | 26/08 – 06/09 | Sửa lỗi, cho phần mềm chạy được trên Windows |
| 2 | 27/09 – 28/09 | Rà soát thiết kế, làm lại màn hình Kết quả |
| 3 | 08/10 – 10/10 | Đọc, đo và rà soát mã nhiều vòng |
| 4 | 14/10 – 15/10 | Không gian làm việc cho nhiều ngành |
| 5 | 24/10 – 01/11 | Điểm quyết tâm |
| 6 | 02/11 – 03/11 | Lớp của học sinh |
| 7 | 04/11 – 05/11 | Làm gọn giao diện |
| 8 | 05/11 – 06/11 | Kết nối với hệ thống Microsoft của trường |
| 9 | 08/11 – 10/11 | Cơ chế xếp mới FA-DAA (5 đợt chạy đêm) |
| 10 | 10/11 | Lập nhật ký AI này |

## 4. Chi tiết từng giai đoạn

### Giai đoạn 1 — Sửa lỗi, cho phần mềm chạy được trên Windows (26/08 – 06/09)

- **Mục tiêu:** phần mềm của học sinh chạy ổn định, cài được trên máy Windows của trường.
- **Truong yêu cầu:** đưa bản gốc lên ngày 26/08; báo lỗi gặp khi chạy thử (ví dụ: mới cài, mở lần đầu thì báo lỗi không kết nối được) và đặt câu hỏi kiểm tra (chạy trên máy khác có ra cùng kết quả không).
- **AI đã làm:** tìm và sửa khoảng 25 lỗi được đánh số. Ví dụ: chương trình treo sau một lúc mở; ô điểm biến 8,5 thành 85; kết quả bốc thăm phụ thuộc thứ tự nhập học sinh; lỗi tệp cài đặt trên Windows. AI cũng viết bộ kiểm thử, đo thử ở quy mô lớn và sửa phần chữ tiếng Việt còn lẫn tiếng Anh.
- **Kết quả:** ngày 01/09, toàn bộ quy trình nạp dữ liệu → xếp → xuất kết quả chạy được trên Windows.
- **Nguồn:** `BAN_GIAO.md`, mục 2 và 5.

### Giai đoạn 2 — Rà soát thiết kế, làm lại màn hình Kết quả (27/09 – 28/09)

- **Mục tiêu:** mã dễ bảo trì hơn, màn hình Kết quả dễ hiểu hơn cho người quản lý.
- **Truong yêu cầu:** làm lại biểu đồ và thông tin ở phần Kết quả cho thân thiện với người quản lý; đặt tên khác dễ hiểu hơn cho một chỉ số và thêm biểu đồ tròn (nguyên văn ở mục 5).
- **AI đã làm:** lập kế hoạch sửa thiết kế; làm xong 7 việc trong kế hoạch, trong đó có khoá số bốc thăm sau lần chạy đầu, thêm ràng buộc cho cơ sở dữ liệu và gom bản dịch về một nguồn. Ngoài ra AI làm lại màn hình Kết quả, thêm tuỳ chọn xuất dữ liệu và trang hồ sơ học sinh.
- **Kết quả:** kế hoạch và nhật ký từng việc nằm trong `KE_HOACH_SUA_THIET_KE.md` (mục 10 và 11).

### Giai đoạn 3 — Đọc, đo và rà soát mã nhiều vòng (08/10 – 10/10)

- **Mục tiêu:** tìm lỗi còn ẩn trước khi thêm tính năng lớn.
- **AI đã làm:** khoảng 25 vòng rà soát mã liên tiếp. Mỗi vòng tìm từ 6 đến khoảng 20 điểm cần xem; phần lớn được sửa, một số bị bác vì không phải lỗi.
- **Kết quả:** vòng cuối ngày 10/10 không còn tìm thấy lỗi.
- **Nguồn:** `CHANGELOG.md`, các mục ngày 08/10 – 10/10.

### Giai đoạn 4 — Không gian làm việc cho nhiều ngành (14/10 – 15/10)

- **Mục tiêu:** dùng được phần mềm ngoài trường học (công ty, sự kiện…). Mỗi nơi có thư mục, từ ngữ và luật xếp riêng.
- **Truong yêu cầu:** theo yêu cầu của chủ dự án (ghi trong nhật ký thay đổi).
- **AI đã làm:** ghép các phần việc, sửa lỗi sau rà soát, viết công cụ dựng không gian làm việc từ dữ liệu thô, Việt hoá màn hình chọn. AI cũng sửa 24 bài kiểm thử chỉ hỏng trên Windows để gộp được yêu cầu gộp số 1.

### Giai đoạn 5 — Điểm quyết tâm (24/10 – 01/11)

- **Mục tiêu:** mỗi học sinh có một quỹ điểm để đặt vào câu lạc bộ mình muốn nhất, cho thấy em quyết tâm đến đâu.
- **Truong quyết định:** chọn phương án A cho cách tính quỹ điểm (25/10). Yêu cầu làm bước rà soát cuối (28/10). Cho phép **phá quy tắc "kết quả giống hệt bản cũ"** để bật điểm quyết tâm mặc định ở trường học (01/11).
- **Phiên chính:** điều phối, chia việc thành 13 phần nhỏ, kiểm tra từng phần.
- **Phiên phụ:** viết phần lõi, lưu trữ, giao diện, dữ liệu mẫu. Đóng vai người dùng thử để tìm chỗ khó hiểu. Rà soát mã theo 4 tầng (lõi thuật toán, phần xử lý, giao diện, tài liệu) bằng một công cụ tự kiểm mới. Thử tải nặng, rồi sửa lỗi tìm được.

### Giai đoạn 6 — Lớp của học sinh (02/11 – 03/11)

- **Mục tiêu:** mỗi học sinh có lớp (ví dụ 10A1), **chỉ để hiển thị, lọc và xuất danh sách** cho giáo viên chủ nhiệm. Thuật toán xếp không bao giờ đọc thông tin này.
- **Truong quyết định:** duyệt các việc làm thêm ngoài danh sách gốc (03/11); gộp yêu cầu gộp số 7 (04/11).
- **Phiên chính (Opus):** hỏi rõ yêu cầu, viết đề bài, điều phối hai phiên phụ chạy song song, cho hai phiên kiểm tra chéo nhau, chạy kiểm thử toàn bộ.
- **Phiên phụ (Sonnet):** một phiên làm phần nền (lưu lớp, nhập dữ liệu); một phiên làm xuất danh sách theo lớp và giao diện. Thêm cột Lớp vào tệp mẫu.
- **Kết quả:** yêu cầu gộp số 6 được gộp ngày 03/11; số 7 được Truong gộp ngày 04/11.

### Giai đoạn 7 — Làm gọn giao diện (04/11 – 05/11)

- **Mục tiêu:** bớt khối thừa, gom nút, đặt lại tên thẻ, để người dùng ít bị rối.
- **Truong quyết định:** duyệt lần lượt từng lô sửa (lô 0 đến lô 5). Yêu cầu tự huỷ lượt kiểm thử cũ khi có thay đổi mới.
- **Phiên chính:** điều phối theo một quy trình tự động gồm ba vai: điều phối, viết mã, kiểm thử.
- **Phiên phụ:** viết mã từng lô và kiểm thử lại từng lô, sửa các bài kiểm thử chập chờn.

### Giai đoạn 8 — Kết nối với hệ thống Microsoft của trường (05/11 – 06/11)

- **Mục tiêu:** học sinh đăng ký và làm bài thi trên Microsoft Forms của trường, rồi chuyển dữ liệu sang phần mềm xếp chỗ.
- **Truong yêu cầu và quyết định:** yêu cầu lập kế hoạch nghiên cứu các ứng dụng Microsoft (05/11, nguyên văn ở mục 5). Quyết định bài thi tuyển đi theo cách xếp của phần mềm. Duyệt chế độ "chỉ thi" của biểu mẫu (05/11), chạy thử trọn chuỗi bằng một lệnh (06/11), và vòng việc thứ hai.
- **Phiên chính:** đọc tài liệu Microsoft và PowerSchool, soạn phiếu phỏng vấn mang đi gặp nhà trường, lập kế hoạch, chia việc.
- **Phiên phụ:** viết đặc tả sửa ứng dụng đăng ký, cổng thi (mỗi câu lạc bộ một biểu mẫu), bộ công cụ dựng danh sách cho bộ phận IT, hướng dẫn vận hành một đợt, đo mô phỏng có và không có bài thi.
- **Kết quả:** yêu cầu gộp số 13 được gộp ngày 06/11. **Chưa thử trên hệ thống Microsoft thật.**

### Giai đoạn 9 — Cơ chế xếp mới FA-DAA (08/11 – 10/11)

- **Mục tiêu:** làm theo bản tầm nhìn Truong viết ngày 08/11. Câu lạc bộ chia ba loại (tự do, giới hạn, tuyển chọn). Mỗi học sinh có ba huy chương vàng, bạc, đồng cho mỗi ngày. Có điểm sàn, chỗ giữ trước, số thành viên tối thiểu. Mỗi kết quả kèm lý do, và có biên bản bốc thăm.
- **Truong quyết định:**
  - Cho phép một **ngoại lệ có điều kiện** với quy tắc chống gian lận: huy chương mặc định được lấy theo thứ tự nguyện vọng, **nhưng học sinh nào cũng đổi được**.
  - Thêm câu hỏi đổi chỗ huy chương bạc và đồng trên biểu mẫu.
  - Việc cân bằng điểm giữa các đề thi không được chặn quy trình.
  - Hoãn phần "ưu tiên bù" sang học kỳ 2, sau khi có mô phỏng hai kỳ.
  - Duyệt thêm bản Excel của biên bản bốc thăm (10/11).
- **Phiên chính (Opus):** đọc bản tầm nhìn, lập kế hoạch và các điểm cần quyết định, cho một "hội đồng" góp ý, viết hướng dẫn cho từng đợt chạy đêm. Sau mỗi đêm, phiên chính kiểm tra lại: chỉ liệt kê lỗi, không tự sửa.
- **Phiên phụ:** năm đợt chạy đêm, mỗi đợt làm theo danh sách đã duyệt. Một số đợt do bạn cộng tác của Truong chạy trên tài khoản của bạn.

| Đợt | Việc | Kết quả |
|---|---|---|
| Đêm 1 | Phần lõi trên máy kiosk: dữ liệu, kiểm tra trước, huy chương, xếp chỗ, lý do, bảng nhu cầu | 9/9 việc xong, kiểm tra lại: đạt |
| Đêm 2 | Phần Microsoft: phiếu thiết lập câu lạc bộ, biểu mẫu đăng ký, bộ chuyển dữ liệu, đề thi nhiều phiên bản, đặc tả ứng dụng | 6/6 xong, kiểm tra lại: đạt, kèm danh sách sửa |
| Đêm 3 | Sửa lỗi của đêm 2, thêm các màn hình trên kiosk | 16/16 xong, kiểm tra lại: đạt |
| Đêm 4 | Sửa lỗi của đêm 3, biên bản bốc thăm, bộ mô phỏng so sánh | 6/6 xong, kiểm tra lại: đạt, tìm thêm 1 lỗi |
| Đêm 5 | Sửa lỗi của đêm 4, bản Excel của biên bản bốc thăm | 2/2 xong; lượt kiểm tra lại tìm và sửa thêm 2 lỗi |

- **Kết quả:** yêu cầu gộp số 14 được mở ngày 10/11, đang chờ kiểm thử toàn bộ và chờ Truong quyết định gộp. **Chưa thử trên máy kiosk và hệ thống Microsoft thật.**

### Giai đoạn 10 — Lập nhật ký AI này (10/11)

- **Truong yêu cầu:** lập nhật ký sử dụng AI chỉ từ dữ liệu trong kho mã. Lời nhắn của phiên chính được ghi lại, phiên phụ chỉ tóm tắt. Bản cuối phải dễ đọc.
- **AI đã làm:** viết công cụ tự dựng bản chi tiết (`NHAT_KY_AI.md`) từ kho mã, rồi viết bản dễ đọc này.

## 5. Lời của Truong được lưu nguyên văn trong kho mã

Kho mã chỉ lưu đúng lời Truong ở vài chỗ dưới đây. Những chỗ khác chỉ có ghi chép tóm tắt.

| Ngày | Hoàn cảnh | Lời nguyên văn |
|---|---|---|
| 27/09/2026 | Yêu cầu làm lại màn hình Kết quả | “use this skill to redesign charts and information in the Result sector to be more friendly and helpful for the adminstrator. Define done as Renovate and help display data better” |
| 27/09/2026 | Yêu cầu đổi tên một chỉ số | “Suggest other name for “nguyen vong may thi duoc suat” and include any info that can be added and display using a pie chart” |
| 01/09/2026 | Báo lỗi khi chạy thử | “mới cài, mở lần đầu thì thường bị lỗi backend không kết nối được” |
| 01/09/2026 | Câu hỏi kiểm tra kết quả | “chạy trên máy khác có ra cùng kết quả không?” |
| 28/10/2026 | Đợt rà soát điểm quyết tâm | “làm bước cuối” và sau đó “tiếp” |
| 05/11/2026 | Yêu cầu nghiên cứu Microsoft | “viết prompt và lên kế hoạch nghiên cứu cụ thể các app để bổ sung cho architecture hiện có” |
| 08/11/2026 | Bản tầm nhìn cơ chế FA-DAA | Toàn văn trong tệp `docs/ke_hoach/FA_DAA_VISION.md` |

## 6. Giới hạn của nhật ký

- Nhật ký **không** lấy từ lịch sử trò chuyện, nên phần lớn lời nhắn của Truong không có nguyên văn; chỉ có ghi chép tóm tắt mà AI để lại trong kho mã.
- Lịch sử lưu mã chỉ có từ ngày 24/10/2026. Giai đoạn 1 đến 4 dựa vào tài liệu bàn giao và nhật ký thay đổi.
- Kho mã không ghi rõ phiên nào thuộc tài khoản nào (Truong hay bạn cộng tác).
- Mọi con số kiểm thử là dữ liệu mô phỏng.
