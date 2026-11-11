# Nhật ký sử dụng AI trong đề tài phần mềm xếp học sinh vào câu lạc bộ (bản đầy đủ)

| Mục | Thông tin |
|---|---|
| **Tác giả đề tài** | Truong (học sinh) |
| **Công cụ AI** | Claude Code của hãng Anthropic. Hai loại: **Opus** dùng để lập kế hoạch, điều phối và kiểm tra lại; **Sonnet** dùng để viết mã theo kế hoạch |
| **Thời gian** | 26/08/2026 đến 10/11/2026 |
| **Nguồn của nhật ký** | Chỉ những ghi chép có sẵn trong kho mã của dự án (tệp bàn giao, nhật ký thay đổi, lịch sử lưu mã). Không lấy từ lịch sử trò chuyện |
| **Cấu trúc** | Mục 1–6: bản dễ đọc. Mục 7: đầy đủ chi tiết từng giai đoạn (từng phiên, từng quyết định, từng lần lưu) |

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

## 7. Chi tiết theo giai đoạn (ghi chép gốc trong kho mã)

Phần này giữ **đầy đủ chi tiết** cho người cần tra cứu, xếp theo đúng 10 giai đoạn ở mục 4. Mỗi giai đoạn có tối đa bốn phần: (a) quyết định của Truong ghi trong nhật ký thay đổi; (b) các mục việc trong nhật ký thay đổi; (c) từng phiên theo tệp bàn giao, phiên chính in đậm, phiên phụ thụt vào bên dưới; (d) các phiên có lưu mã. Dòng ghi chép của phiên là **nguyên văn ghi chép AI để lại** (phần lớn bằng tiếng Anh, giữ nguyên để trung thực), không phải lời của Truong.

### Giai đoạn 1 — Sửa lỗi, cho phần mềm chạy được trên Windows (chi tiết)

Giai đoạn này trước khi kho mã giữ lịch sử lưu. Chi tiết từng lỗi (lỗi 13 đến lỗi 25, ngày 30/08 – 06/09) nằm trong `BAN_GIAO.md` mục 2 và mục 5; phần học sinh tự viết và phần AI viết mới nằm ở `BAN_GIAO.md` mục 2.

### Giai đoạn 2 — Rà soát thiết kế, làm lại màn hình Kết quả (chi tiết)

Nhật ký từng việc của giai đoạn này đã có sẵn trong `KE_HOACH_SUA_THIET_KE.md` mục 10 (trạng thái 7 việc kèm lần lưu) và mục 11 (tệp AI viết mới, mã học sinh viết bị sửa). Việc làm lại màn hình Kết quả ghi ở `BAN_GIAO.md` mục 2 (27/09 – 28/09).

### Giai đoạn 3 — Đọc, đo và rà soát mã nhiều vòng (chi tiết)

**(b) Các mục việc trong `CHANGELOG.md` (26 mục):**

- 08/10/2026 — Giai đoạn 0 (chỉ đọc và đo)
- 08/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)
- 08/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

### Giai đoạn 4 — Không gian làm việc cho nhiều ngành (chi tiết)

**(b) Các mục việc trong `CHANGELOG.md` (5 mục):**

- 14/10/2026 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)
- 14/10/2026 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)
- 14/10/2026 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)
- 15/10/2026 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)
- 15/10/2026 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

### Giai đoạn 5 — Điểm quyết tâm (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 25/10/2026 — A13 Điểm Wharton: pipeline tự điền quỹ một CLB trong bộ nhớ (theo quyết định của Truong, cách A)

**(b) Các mục việc trong `CHANGELOG.md` (16 mục):**

- 24/10/2026 — A13 Điểm Wharton (vòng 1: lõi thuật toán và test)
- 24/10/2026 — A13 Điểm Wharton (vòng 2: lưu trữ, nhập liệu, kiosk, pipeline)
- 25/10/2026 — A13.3 Quản lý điểm Wharton
- 25/10/2026 — A13.4 Giao diện Điểm quyết tâm và điểm chuẩn
- 27/10/2026 — A13.5 Sửa 5 việc từ báo cáo đóng vai
- 27/10/2026 — A13.6 Dữ liệu mẫu có Điểm quyết tâm (vòng 6)
- 27/10/2026 — A13.7 Sổ nhập mẫu luôn có cột Điểm quyết tâm
- 28/10/2026 — Z-SOAT Skill `soat-ma`: soát mã trước khi push
- 28/10/2026 — A13.8 Sửa 12 lỗi từ đợt soát A13
- 28/10/2026 — A13.9 Sửa 9 vấn đề từ đợt stress test
- 28/10/2026 — A13.10 Nhãn "Xét điểm thi / Xét điểm quyết tâm" và thiết kế lại màn Điểm chuẩn
- 28/10/2026 — A13.11 Sửa 4 phát hiện N1–N4 của đợt stress test (trên đỉnh A13.9)
- 28/10/2026 — A13.12 Sửa Tầng 4 của đợt soát A13 và toàn bộ mục chặn / nên sửa của đợt soát hệ thống nhập
- 01/11/2026 — Công cụ phiên (ngoài sổ): sửa test tài liệu sau khi rút gọn CLAUDE.md
- 01/11/2026 — A13.13 Điểm quyết tâm (Wharton) BẬT mặc định cho workspace trường học
- 01/11/2026 — A13.13 (phần tiếp theo) CSDL demo thể hiện điểm quyết tâm + vá đường dẫn cứng

**(c) Các phiên theo tệp bàn giao:**

*Nhánh `claude/demo-wharton-va-duong-dan`* — nguồn `docs/phien/claude__demo-wharton-va-duong-dan.md`. Mục tiêu ghi trong tệp: A13.13 (continued), branched from claude/wharton-mac-dinh-bat. Two small jobs from the parent session: 1. Demo DB must show commitment points (Wharton ON by default); `--tat-wharton` rebuilds the old DB. 2. Remove hard-coded `/home/user/truong/...` paths in `du_lieu_test/do_do_dai_nguyen_vong.py`.

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 01/11/2026 · Sonnet: Both jobs done, tests and ruff green

*Nhánh `claude/sleepy-sagan-ly5fx0`* — nguồn `docs/phien/claude__sleepy-sagan-ly5fx0.md`. Mục tiêu ghi trong tệp: Workflow tooling for Claude sessions on this repo (no algorithm change): session handoff files, token-saving rules in CLAUDE.md.

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 01/11/2026 · Sonnet: Built handoff scheme, NO SUBAGENT rule, related-tests-only rule, CLAUDE.md trim
  - Phiên phụ · 01/11/2026 · Sonnet: Rule 11: Opus session creates the branch file from the template

*Nhánh `claude/wharton-mac-dinh-bat`* — nguồn `docs/phien/claude__wharton-mac-dinh-bat.md`. Mục tiêu ghi trong tệp: A13.13: the school workspace default `rules.wharton = True` (commitment points / "Wharton" ON by default). Truong approved breaking invariant 1 for this item (recorded in CHANGELOG + TIEN_DO under A13.13). Invariants 2-8 hold. Out of scope: "template header by vocabulary" (Direction A/B).

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 01/11/2026 · Sonnet: Branch + handoff created
  - Phiên phụ · 01/11/2026 · Sonnet: Implemented A13.13, fixed tests/scripts, parent acceptance suite
  - Phiên phụ · 01/11/2026 · Sonnet: Round 3 (group A after CI) + round 4 (group B, direction c, demo-branch merge, skills, NHAP_TAY)
  - Phiên phụ · 01/11/2026 · Sonnet: Final handoff after round 4: 4 red tests fixed, ruff/soat-ma green, report sent to parent
  - Phiên phụ · 01/11/2026 · Sonnet: Recorded Truong's approval in CHANGELOG; final handoff
  - Phiên phụ · 01/11/2026 · Sonnet: Full handoff rewrite requested by parent (rule 9, context ~538k)
  - Phiên phụ · 01/11/2026 · Sonnet: Handoff re-confirmed (hook fired again); nothing new done
  - Phiên phụ · 01/11/2026 · Sonnet: Session 2 picked up handoff 74ab5bb

**(d) Các phiên có lưu mã (20 phiên, 133 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| C3a1YhqF | 24/10/2026 | 24/10/2026 | 1 | — | e08af78 |
| hz6WMv5u | 24/10/2026 | 25/10/2026 | 12 | A13 | a8b077d 1011f35 fb35974 |
| mCWfrrwL | 25/10/2026 | 25/10/2026 | 6 | A13.3 | 4c448ae dd4a5f3 17497bd |
| JjS1z2mZ | 25/10/2026 | 27/10/2026 | 8 | A13.4 | d85fe2c d54ba04 aa60ebe |
| V9pSwnP8 | 27/10/2026 | 27/10/2026 | 10 | A13.5 | cb53cc0 6ed3718 eb203a7 |
| xJpKsyKc | 27/10/2026 | 27/10/2026 | 1 | — | 11bd6f6 |
| v6DHpVSA | 27/10/2026 | 27/10/2026 | 2 | A13.7, A13.6 | 088573d 2df59ce |
| Mds6oLDe | 27/10/2026 | 28/10/2026 | 8 | Z-SOAT | 77fa953 5ddd516 2ce3af7 |
| gDSHZQp2 | 28/10/2026 | 28/10/2026 | 1 | — | 4b4ac50 |
| CowtT2Bd | 28/10/2026 | 28/10/2026 | 12 | A13.8 | 0f13771 3b80854 f004c35 |
| VBKnzq8m | 28/10/2026 | 28/10/2026 | 17 | A13.11, A13.9 | daff982 77b1cb9 02c3089 |
| zafjmyBa | 28/10/2026 | 28/10/2026 | 5 | — | a2d8b4b c27ff32 167be48 |
| 6bVDyWHg | 28/10/2026 | 28/10/2026 | 6 | A13.10 | 43f3f89 5088334 86f7c65 |
| HdJs6TZX | 28/10/2026 | 28/10/2026 | 18 | A13.12 | b045b42 2f4228d e1f6d56 |
| Lys3VpqX | 29/10/2026 | 29/10/2026 | 4 | A13.14, A13.13 | 578af21 b4ffce3 df3eda1 |
| NsHqeuCE | 01/11/2026 | 01/11/2026 | 5 | CLAUDE.md | cee2940 5fd624b 2367a8c |
| ZS4eiU6U | 01/11/2026 | 01/11/2026 | 13 | A13.13 | 2176ee7 74ab5bb 01ea7cd |
| TfR1eikv | 01/11/2026 | 01/11/2026 | 2 | — | 64e47f5 4fe6f56 |
| nvcVK8a9 | 01/11/2026 | 01/11/2026 | 1 | — | 79c8946 |
| gLEyFJQc | 01/11/2026 | 01/11/2026 | 1 | — | a05fc1e |

### Giai đoạn 6 — Lớp của học sinh (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 03/11/2026 — T1a, T1b (nhánh `claude/epic-knuth-801pkw`; Truong duyệt, bỏ qua sổ đăng ký)
- 03/11/2026 — T4-K3 (ngoài sổ, Truong duyệt 03/11/2026): skill `xu-li-raw-forms` đọc thư mục nhiều phần CSV
- 03/11/2026 — A14-B10 (ngoài sổ, Truong duyệt 03/11/2026): bỏ `DROP COLUMN` ở hai test A14 còn lại
- 03/11/2026 — Z-SOAT-2 (ngoài sổ, Truong duyệt 03/11/2026): `soat-ma` tìm ruff trên PATH

**(b) Các mục việc trong `CHANGELOG.md` (2 mục):**

- 02/11/2026 — A14 — phần B (xuất theo lớp và giao diện lớp)
- 02/11/2026 — A14 — phần A (nền, nhập, API): lớp của học sinh

**(c) Các phiên theo tệp bàn giao:**

*Nhánh `claude/a14-giao-dien`* — nguồn `docs/phien/claude__a14-giao-dien.md`. Mục tiêu ghi trong tệp: A14 part B (export + UI for the student class). Part A (branch claude/a14-lop-hoc-sinh) owns DB column students.class_id, chuan_hoa_lop, `cohort` noun and all class APIs. Part B: Excel sheet "Theo lớp" (always), API export_theo_lop (folder, one .xlsx per class), "Lớp" column after "Họ tên" in several tables, and UI (Manager filter/sort/edit, Results filter/sort/export button, kiosk required class dropdown, workspace…

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 02/11/2026 · Sonnet: export + UI + tests written
  - Phiên phụ · 02/11/2026 · Sonnet: merged A, fixed name clash + filter bug, soat-ma
  - Phiên phụ · 02/11/2026 · Sonnet: tabs 06/07, lang re-render, export cleanup, tests, soat-ma
  - Phiên phụ · 02/11/2026 · Sonnet: cross-review fixes B1-B7 (A merged last)
  - Phiên phụ · 04/11/2026 · Sonnet: Closed docs after PR #6 merge

*Nhánh `claude/a14-lop-hoc-sinh`* — nguồn `docs/phien/claude__a14-lop-hoc-sinh.md`. Mục tiêu ghi trong tệp: A14 "Lớp của học sinh" (part A, backend; part B = branch claude/a14-giao-dien does export + UI). Each student may have a class (e.g. 10H1A) used ONLY for display, sorting, filtering and export for homeroom teachers. The allocation algorithm NEVER reads it. DB: `students.class_id` TEXT, NULL = none. New vocabulary noun `cohort` (vi "Lớp", en "Class"). One shared normaliser `rbda_priority_pipeline.chuan_hoa_lop(raw) -…

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 02/11/2026 · Sonnet: Step 1 base
  - Phiên phụ · 02/11/2026 · Sonnet: Step 2 import/API/docs, old-test fixes, soat-ma
  - Phiên phụ · 03/11/2026 · Sonnet: C1 label re-save, C2 sample files with simulated classes
  - Phiên phụ · 02/11/2026 · Sonnet: Cross-review fixes A1-A6
  - Phiên phụ · 04/11/2026 · Sonnet: Closed docs after PR #6 merge

*Nhánh `claude/dieu-phoi-a14`* — nguồn `docs/phien/claude__dieu-phoi-a14.md`. Mục tiêu ghi trong tệp: A14 "class per student" (Lớp): each student has `students.class_id` used ONLY for display / sort / filter / export to homeroom teachers (GVCN); the allocation never reads it. Opus coordinated two parallel Sonnet sessions (A = base + import + API, B = export + UI + view tabs 06/07), cross-review, fix rounds and final verification.

- **02/11/2026 · Phiên chính · Opus:** Coordinated A14: spec Q&A, prompts, parallel sessions A/B, cross-review, fix rounds, full-suite verification, PR #6 merged, PR #7 opened and green *(handoff at ~400k tokens)*
- **04/11/2026 · Phiên chính · Opus:** PR #7 check-in 1: still green, clean, no reviews; check-in 2 scheduled *(no new work; open a new session)*
- **04/11/2026 · Phiên chính · Opus:** PR #7 merged by Truong (05:52Z); unsubscribed, check-in deleted *(A14 closed)*

*Nhánh `claude/epic-knuth-801pkw`* — nguồn `docs/phien/claude__epic-knuth-801pkw.md`. Mục tiêu ghi trong tệp: Follow-up to A14 (student class). Branch starts from `claude/a14-giao-dien` (fast-forwarded, includes A14 part A + B). Truong's task file (2026-11-03), explicitly overriding the registry rule (rule 1): - T1a: static sample `mau_csv/SO_NHAP_CLB.xlsx` has no "Lớp" column (software-generated sample has it). Add it and make that file the main sample. - T1b: an old workspace whose saved config already has two nouns with…

- **03/11/2026 · Phiên chính · Opus:** ff to a14-giao-dien, wrote plan for T1/T2 *(coordinator session)*
  - Phiên phụ · 03/11/2026 · Sonnet: T1a, T1b, T2 implemented, tests green, pushed
  - Phiên phụ · 03/11/2026 · Sonnet: Fix round 1 (F1-F8) from Opus plan
  - Phiên phụ · 03/11/2026 · Sonnet: Fix round 2 (G1-G3) from Opus plan
  - Phiên phụ · 03/11/2026 · Sonnet: Fix round 3 (snapshot of Sổ guide text)
  - Phiên phụ · 03/11/2026 · Sonnet: Handoff at context limit, round 3 committed
  - Phiên phụ · 03/11/2026 · Sonnet: Final handoff: rounds 1-3 done and reported
  - Phiên phụ · 04/11/2026 · Sonnet: CON-4: T4 design doc and 5 diagrams, rounds 1, 2, 3b pushed (ca9e161); handoff at context limit
- **04/11/2026 · Phiên chính · Opus:** Coordinated T3 (closed), T4 design rounds 1-4, T4-K1 (closed); handoff at context limit *(K2 waits on design round 5 (CON-6))*
- **04/11/2026 · Phiên chính · Opus:** Merged main, resolved 7 conflicts, opened PR #8 (no K2) *(full suite + CI pending at handoff)*
- **04/11/2026 · Phiên chính · Opus:** Fixed PR #8 CI failures from T4-K1 (baac5d0) *(CI on baac5d0 pending at handoff)*

**(d) Các phiên có lưu mã (7 phiên, 68 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| tEybZqXm | 02/11/2026 | 04/11/2026 | 14 | A14 | 804d205 0b0991a c3cd884 |
| e9PkriHi | 02/11/2026 | 04/11/2026 | 22 | A14 | 5ad0f18 45c848b 73d8d05 |
| 8cd64rmp | 03/11/2026 | 04/11/2026 | 7 | — | aa48425 baac5d0 930afcd |
| ngVvTQdq | 03/11/2026 | 03/11/2026 | 10 | — | 8ed0a66 cebfa2c 0e56a1b |
| BydGUj7d | 03/11/2026 | 03/11/2026 | 1 | — | 353d1c4 |
| 9KX6VoZF | 03/11/2026 | 04/11/2026 | 5 | T4 | c50d5c0 ca9e161 10a530e |
| 5ae6dE88 | 03/11/2026 | 03/11/2026 | 9 | Z-SOAT-2, A14-B10, T4, T4-K3 | 373eaf0 fb72a8b 78cb0e7 |

### Giai đoạn 7 — Làm gọn giao diện (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 04/11/2026 — T4-K1 (ngoài sổ, Truong duyệt 03/11/2026): cột `lop` tuỳ chọn từ `hoc_sinh` tới cột Lớp của Sổ
- 04/11/2026 — T3-HT (ngoài sổ, Truong duyệt 04/11/2026): hạ tầng tự động hoá T3 (điều phối + viết mã + soát)
- 04/11/2026 — T3-L0 (ngoài sổ, Truong duyệt 04/11/2026): ba lỗi sản phẩm của nghiên cứu T3 (B1/T3-26, B2/T3-01, B3/T3-42)
- 04/11/2026 — T3-L1 (ngoài sổ, Truong duyệt 04/11/2026): chữ và hiển thị nhỏ (nghiên cứu T3, lô 1)
- 04/11/2026 — CI-HUY (ngoài sổ, Truong yêu cầu 04/11/2026): huỷ lượt CI cũ khi có commit mới
- 04/11/2026 — T3-L2 (ngoài sổ, Truong duyệt 04/11/2026): bớt khối, gom nút (nghiên cứu T3, lô 2)
- 04/11/2026 — T3-L3 (ngoài sổ, Truong duyệt 04/11/2026): tên thẻ, thẻ Kết quả gọn, tải bảng, Điểm chuẩn một nơi, chữ Sổ nhập (nghiên cứu T3, lô 3)
- 04/11/2026 — T3-L4 (ngoài sổ, Truong duyệt 04/11/2026): thứ tự tệp "Tải bảng này", bỏ dòng nhắc chết, Điểm chuẩn gọn
- 05/11/2026 — T3-L5 (ngoài sổ, Truong yêu cầu): Điểm chuẩn cùng nền các thẻ khác, thẻ 05 chỉ ghi "Quản lý"

**(b) Các mục việc trong `CHANGELOG.md` (6 mục):**

- 04/11/2026 — T4-K1 sửa vòng 1 (tester soát fff0f41)
- 04/11/2026 — PR #8: sửa CI sau T4-K1 (Windows báo 4 lỗi ở 5a88060)
- 04/11/2026 — sửa CI main 3c67776: test giao diện A14 chập chờn
- 04/11/2026 — T3-L2 fix2 (điều phối): test bảng lỗi theo nhãn buổi
- 04/11/2026 — T3-L2 fix3 (điều phối): test node chạy được trên Windows
- 04/11/2026 — T3-L3 fix (điều phối): test "chưa có lớp" theo hành vi thật

**(c) Các phiên theo tệp bàn giao:**

*Nhánh `claude/gallant-mendel-uki8j2`* — nguồn `docs/phien/claude__gallant-mendel-uki8j2.md`. Mục tiêu ghi trong tệp: Execute the T3 UI debloat study (`docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`) in four lots, automated by a coordinator + implementer + tester chain (protocol: `docs/phien/T3_GIAO_THUC.md`). Item codes: outside the registry, Truong approved 2026-11-04: `T3-L0`..`T3-L3` (one TIEN_DO row each). Display-only changes except L0 B1/B2 backend guards. Algorithm, `match_results`, `run_history`, STB, CSV column contract: untouc…

- **04/11/2026 · Phiên chính · Opus (điều phối):** Asked Truong 16 decisions, wrote protocol + plan, role-aware hook

*Nhánh `claude/gallant-mendel-uki8j2` (impl)* — nguồn `docs/phien/claude__gallant-mendel-uki8j2__impl.md`. Mục tiêu ghi trong tệp: Implement T3 lots L0..L3 on this branch (spec = "Lot L<n>" in `docs/phien/claude__gallant-mendel-uki8j2.md`; study rows by id: `grep -n "^| T3-26 " docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`).

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 04/11/2026 · Sonnet (viết mã 1): L0 implemented, fix1, fixci1
  - Phiên phụ · 04/11/2026 · Sonnet (viết mã 1): L1 implemented (`0fd4981`), handoff written
  - Phiên phụ · 04/11/2026 · Sonnet (viết mã 3): L2 finished (T3-23, T3-28, T3-21, docs, soat-ma)
  - Phiên phụ · 04/11/2026 · Sonnet (viết mã 3): L2 fix1 (6 tester items, 5 done, T3-32 collapse skipped)
  - Phiên phụ · 04/11/2026 · Sonnet (viết mã 4): L3 implemented (T3-11/16/17/18/19/22/27/31 + tab names)

*Nhánh `claude/gallant-mendel-uki8j2` (tester)* — nguồn `docs/phien/claude__gallant-mendel-uki8j2__tester.md`. Mục tiêu ghi trong tệp: Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

- *(Phiên chính của luồng này không ghi trong tệp; nằm ở luồng điều phối khác)*
  - Phiên phụ · 04/11/2026 · Opus (kiểm thử): L0 review, invariant 1 re-check, 3 screenshots
  - Phiên phụ · 04/11/2026 · Opus (kiểm thử): L0 fix1 re-check
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): L1 + L0fixci1 review, 6 screenshots
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): L1 fix1 re-check
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): L1 fix1 re-check NO BUGS; L2 review
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): Handoff at 200k
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): L2 fix1 re-check, screenshots 01/04/07
  - Phiên phụ · 04/11/2026 · Sonnet (kiểm thử): L3 review, 6 screenshots

**(d) Các phiên có lưu mã (10 phiên, 47 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| yg3WkppJ | 03/11/2026 | 03/11/2026 | 3 | T3 | 0d28de0 7461c0b bfb340f |
| 4MDFqofZ | 04/11/2026 | 04/11/2026 | 2 | T4-K1 | 85d22ce fff0f41 |
| b4CTcC1X | 04/11/2026 | 04/11/2026 | 1 | — | 00372e0 |
| rzrTqFD7 | 04/11/2026 | 04/11/2026 | 1 | — | a16bf16 |
| CeJXaN5S | 04/11/2026 | 04/11/2026 | 21 | T3-L4, T3-L3, T3-L2, fix3, T3, fix2, CI-HUY, T3-HT | b9d4e19 1f5903d 384065a |
| 5pa3nYSD | 04/11/2026 | 04/11/2026 | 9 | T3-L4, T3, T3-L1, T3-L0, fixci1, fix1 | b17ac78 4aa7ab4 7d1e130 |
| uzPors7z | 04/11/2026 | 04/11/2026 | 3 | T3-L0 | a9b56b4 6bd191b c34b3ce |
| zT6ML4Qx | 04/11/2026 | 04/11/2026 | 4 | T3, T3-L2, T3-L1 | fab9f82 9dd8e14 555847d |
| oGYkwnan | 04/11/2026 | 04/11/2026 | 1 | T3-L3 | ad4f227 |
| gz5yriDb | 04/11/2026 | 04/11/2026 | 2 | T3-L3 | 1d5a384 ca81585 |

### Giai đoạn 8 — Kết nối với hệ thống Microsoft của trường (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 05/11/2026 — T4M-NC (ngoài sổ, Truong yêu cầu 05/11/2026): kế hoạch nghiên cứu hệ sinh thái Microsoft của trường
- 05/11/2026 — Z-CLAUDE-GON (ngoài sổ, Truong yêu cầu 05/11/2026; Truong duyệt bản tiếng Anh)
- 05/11/2026 — T4M-Q1, T4M-Q2, T4M-Q3 (Truong duyệt 05/11/2026): chế độ "chỉ thi" của mẫu Microsoft Forms
- 06/11/2026 — T4M-DEMO (Truong duyệt 06/11/2026): chạy thử trọn chuỗi bằng một lệnh
- 06/11/2026 — T4M-NC: Truong duyệt vòng 2

**(b) Các mục việc trong `CHANGELOG.md` (25 mục):**

- 05/11/2026 — T4M-NC GĐ1 + P4: kết quả đọc tài liệu Microsoft / PowerSchool, hợp đồng nhập của kiosk
- 05/11/2026 — T4M-NC chuẩn bị GĐ2: phiếu phỏng vấn in mang theo
- 05/11/2026 — T4M-NC: quyết định thi tuyển theo RB-DA (Truong), thêm NC-23 đến NC-26 và prompt P5
- 05/11/2026 — T4M-NC GĐ3 (tài liệu): hướng dẫn thử môi trường Microsoft + bộ sinh tệp xuất Lists giả
- 05/11/2026 — T4M-NC P5: đường thu điểm thi trên Microsoft (NC-23, 24, 27)
- 06/11/2026 — T4M-NC: kế hoạch tự chạy (S1 đến S4)
- 06/11/2026 — T4M-GOI-TK (bước S2): thiết kế gói nhiều buổi (tiếng Nhật), chỉ tài liệu
- 06/11/2026 — T4M-VH (bước S1): vận hành một đợt xếp CLB, chỉ tài liệu
- 06/11/2026 — T4M-Q1b (trong T4M-Q1 đã duyệt): `--chi-thi` chép Lớp từ Lists vào Sổ nhập
- 06/11/2026 — T4M-Q1b-b (bổ sung của điều phối vào T4M-Q1b): `--co-so` cho `--chi-thi`
- 06/11/2026 — T4M-DO (bước S4): đo mô phỏng có / không bài thi tuyển, chỉ bảng số
- 06/11/2026 — T4M-GD4-V0 (bước S3): nháp v0 kiến trúc Microsoft, chỉ tài liệu
- 06/11/2026 — T4M-M3 (vòng 2, bước R2): đối chiếu hai lần xuất List
- 06/11/2026 — T4M-M1 (vòng 2, R1): đặc tả sửa app ECA sang Top 3 mỗi ngày, chỉ tài liệu
- 06/11/2026 — T4M-M4 (bước R3): hướng dẫn flow gửi Excel theo lớp cho GVCN, chỉ tài liệu
- 06/11/2026 — T4M-NC: thiết kế cổng thi (chọn CLB → mở bài thi → trạng thái → điểm)
- 06/11/2026 — T4M-Q4a, Q4b, Q4c: cổng thi, mỗi CLB một biểu mẫu (vòng 3, bước C1)
- 06/11/2026 — T4M-M5 (vòng 3, bước C2): màn "Thi tuyển" và flow "Đã làm", chỉ tài liệu
- 06/11/2026 — T4M-NC vòng 3: soát C1 (T4M-Q4a/b/c) và C2 (T4M-M5)
- 06/11/2026 — T4M-DEMO-B: `demo_t4m.py --moi-clb` (cách B) và câu hỏi cổng thi cho GĐ2
- 06/11/2026 — T4M-M6 (vòng 4, bước D2): app Top 7, tick chọn thi, điểm quyết tâm; chỉ tài liệu
- 06/11/2026 — T4M-Q5a/b/c (vòng 4, bước D1): bộ chuyển đổi đọc THIk/WPk, dữ liệu giả, `demo_t4m.py --day-du`
- 06/11/2026 — T4M-BK1, BK2 (vòng 5, bước K1): bộ dựng list và công thức Power Fx cho IT
- 06/11/2026 — T4M-BK3, BK4 (vòng 5, bước K2): bảng flow `DaLam_<ClubId>` và lệnh gộp `tao_bo_dung_t4m.py`
- 06/11/2026 — T4M-NC: sửa CI đỏ của PR #13 (3 nguyên nhân do nhánh)

**(c) Các phiên theo tệp bàn giao:**

*Nhánh `claude/upbeat-shannon-g5nnms`* — nguồn `docs/phien/claude__upbeat-shannon-g5nnms.md`. Mục tiêu ghi trong tệp: T4M-NC (outside the 33-item registry; Truong asked 05/11/2026): fit RB-DA into the school's EXISTING Microsoft ecosystem (Power Apps "ECA Registration HVT", M365 A3/A5, PowerSchool sync, IT runs the kiosk). Truong decided the school adopts RB-DA incl. entrance quizzes (Tầng 1) built by our tooling on Microsoft Forms. Plans: `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (research, NC-01..27, prompts P1..P5), `docs/h…

- **05/11/2026 · Phiên chính · Opus:** Explained T4; gathered school profile via 28 questions; wrote T4M research plan + prompts P1..P4 *(No code changed)*
- **05/11/2026 · Phiên chính · Opus:** Slimmed prompts + CLAUDE.md; ran GĐ1 + P4 (web docs read, kiosk import contract) *(Key: DVfT + Developer Plan end 15/11/2026; PowerSchool not an SDS OneRoster provider)*
- **05/11/2026 · Phiên chính · Opus:** Handoff at ~400k context (Stop hook); no new work *(Next: Truong GĐ2 with IT)*
- **05/11/2026 · Phiên chính · Opus+Sonnet:** GĐ2 interview sheet written (by a subagent: rule 10 breach, Truong flagged it; reviewed by Opus); P3 subagent stopped, partial file deleted; P3 moved to a new Sonnet session *(Never use Agent tool; open sessions)*
  - Phiên phụ · 05/11/2026 · Sonnet: GĐ3 doc (P3 amended): guide, fake Lists-export generator, test first (7 red -> green)
- **05/11/2026 · Phiên chính · Opus:** Truong decided: school adopts RB-DA with entrance quizzes (Tầng 1); added NC-23..26 + prompt P5 *(Sonnet P3 session told)*
- **05/11/2026 · Phiên chính · Opus:** P5 research (Forms Quiz, Graph, Quick Import, Power Apps quiz); found mau_forms_thi_clb already covers Forms quiz; results §7; interview sheet +4 Qs *(Proposed T4M-Q1..Q3)*
- **05/11/2026 · Phiên chính · Opus:** Truong approved T4M-Q1..Q3; opened Sonnet session for them *(Order Q1 -> Q2 -> Q3)*
  - Phiên phụ · 05/11/2026 · Sonnet: T4M-Q1..Q3 done: quiz-only converter, quiz-only form generator, teacher note; tests first (27), mutation check found missing 200-boundary case, fixed
- **06/11/2026 · Phiên chính · Opus:** Reviewed T4M-Q1..Q3 (58 related tests pass, ruff clean, default output identical except docx/xlsx core.xml timestamp); Truong approved T4M-DEMO, Sonnet session opened
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-DEMO done: fake quiz-only Forms generator, `demo_t4m.py` one-command chain, README 0b; tests first (11), mutation check found 1 weak test (uppercase emails), fixed
- **06/11/2026 · Phiên chính · Opus:** Truong approved auto chain (bundle design only, GĐ4 v0, auto-run, simulation tables only); wrote T4M_KE_HOACH_TU_DONG.md *(S2 launched)*
- **06/11/2026 · Phiên chính · Opus:** S2 T4M-GOI-TK: bundle design doc (two-phase orchestrator, invariants 1/2/3/4/5/8, week-level counter-example, CSV/schema proposal, A8-GOI-1..3 kiem_nhan, ECA questions) *(Design only; no code; 5 decisions for Truong)*
- **06/11/2026 · Phiên chính · Opus:** Reviewed S0 T4M-DEMO (69 tests pass, demo runs, 3 seeded warnings) and S2 (OK); found Lớp gap -> T4M-Q1b; launched S1, S3, S4, Q1b *(S2 D1-D5 await Truong)*
  - Phiên phụ · 06/11/2026 · Sonnet: S1 T4M-VH done: one-round operations guide for school IT (8 steps)
- **06/11/2026 · Phiên chính · Opus:** Reviewed S1 T4M-VH (OK); added --co-so filter to Q1b scope
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-Q1b: tests first (1 red), converter carries Lớp from Lists into Sổ nhập, demo workaround removed; one old test's expectation updated (test Lists has class 9A1)
  - Phiên phụ · 06/11/2026 · Sonnet: S4 T4M-DO: simulation grid script, tables, tests first; mutation check caught condition A dropping applicant lists (results no longer depended on seed)
- **06/11/2026 · Phiên chính · Opus:** S3 T4M-GD4-V0: draft v0 T4M_MICROSOFT.md (P2 under fallback A; two store branches; matrix filled; item codes T4M-M1..M4; T4-K2 options only) *(Docs only; D1-D5 still pending Truong)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-Q1b-b (orchestrator addition): --co-so filter, tests first (4 red -> green), ops guide steps 4-5
- **06/11/2026 · Phiên chính · Opus:** Reviewed Q1b (OK, test expectation change justified), S3 (OK, cites DO sections not numbers); S4 sent back: table 2 says 15 clubs with tests, de_thi.json has 10 *(Waiting S4 fix, Q1b-b)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-DO review fix: table 2 exam-club count 15 -> 10, method wording, test that B is Tier 1 for exactly the clubs with de_thi, grid rerun
- **06/11/2026 · Phiên chính · Opus:** Reviewed S4 fix (OK) and Q1b-b (OK); chain finished; cancelled check-in; asked Truong pending decisions
- **06/11/2026 · Phiên chính · Opus:** Truong decided D1-D5 (principle), M1/M3/M4, K2-b, round 2; wrote plan §6; launched R1-R3
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M1 (R1): app-edit spec for Top 3 per day, 14 requirements with pass/fail checks
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M4 (R3): flow guide for sending per-homeroom Excel to homeroom teachers; docs only
- **06/11/2026 · Phiên chính · Opus:** Reviewed R1 T4M-M1 (OK); added HDT §9 rows 5.5 (bilingual) and 5.6 (restore) for R10/R12
- **06/11/2026 · Phiên chính · Opus:** Reviewed R3 T4M-M4 (OK; fixed DLP reference NC-16 -> NC-14) *(Waiting R2)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M3 (R2): `doi_chieu_lists.py` list-export diff tool, tests first (17), ops guide step 8
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M3 review fix: raw NV comparison + unknown-code warning headline, tests first (6 red -> green)
- **06/11/2026 · Phiên chính · Opus:** Reviewed R2 fix (raw NV compare, warning headline; my false-negative scenario now caught); round 2 finished; 109 related tests pass, ruff clean, kiem_nhanh 7/7 *(Next needs Truong: GĐ2 interviews)*
- **06/11/2026 · Phiên chính · Opus:** Truong asked for a quiz portal loop; designed T4M_CONG_THI.md (app as portal, one Form per club, BaiThi status list via standard flow, score via converter); proposed Q4a-c, M5 *(Awaiting Truong approval)*
- **06/11/2026 · Phiên chính · Opus:** Truong approved Q4a-c + M5, score level 5a; wrote plan §7; launched C1, C2
- **06/11/2026 · Phiên chính · Opus:** Handoff at ~400k context: rewrote state/next/decisions; round 3 C1, C2 still running; fallback trigger deleted *(New root must poll C1/C2 (they message the old session))*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M5 (C2): Thi tuyển screen spec (§10, R15..R24) + "Đã làm" flow guide; docs only
- **06/11/2026 · Phiên chính · Opus:** Second handoff note: C2 reported DONE (unreviewed); C1 running *(No new work started)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-Q4a/b/c (C1): `--moi-clb` generator, one-club-per-export converter, `--bai-thi` report; tests first (24)
- **06/11/2026 · Phiên chính · Opus:** Third handoff note: C1 also reported DONE (unreviewed) *(Round 3 needs Opus review only)*
- **06/11/2026 · Phiên chính · Opus:** Reviewed round 3 (C1, C2): 134 tests, kiem_nhanh 7/7, outputs identical; added 1 test (mutation survivor), HDT §13 rows 13.1-13.4 (C2 numbering clash); round 3 ticked *(Next: Truong decides PR to main)*
- **06/11/2026 · Phiên chính · Opus:** Truong chose cách B; T4M-DEMO-B: demo --moi-clb (tests first, 4 red -> green, 2 mutations caught), interview sheet B3 IT-15..18 *(Next: PR to main?)*
- **06/11/2026 · Phiên chính · Opus:** Built simulation artifact (cách B); Truong flagged 10 NV / 5 tests / determination points missing; decided 7 NV, tick max 5, points in app (b); wrote plan §8 round 4 *(Launching D1, D2)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-M6 (D2): app spec Top 7, tick max 5, determination-point screen; R25..R38, HDT rows 14.x + section 14; CONG_THI, MICROSOFT, interview sheet
- **06/11/2026 · Phiên chính · Opus:** Updated simulation artifact v2 (Top 7, tick, two funds); reviewed D2 T4M-M6 (OK; R37 no longer counts legit "vắng thi" warnings) *(Waiting D1)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-Q5a/b/c (D1): converter THIk/WPk, fake Lists/Forms with ticks and funds, demo --day-du; tests first (29 red on first run -> all 34 green), 5 mutations caught
- **06/11/2026 · Phiên chính · Opus:** Reviewed D1 T4M-Q5a/b/c: tests green after fixing D2/D1 clash (HDT no longer named `NV3`), demo default and --moi-clb outputs identical to before, --day-du runs; kiosk auto-fills single-club fund (confirmed); round 4 done *(Artifact v3 next)*
- **06/11/2026 · Phiên chính · Opus:** Artifact v4 (demo --day-du numbers); handoff at ~400k context (Stop hook); no new work *(Next: ask Truong about PR to main)*
- **06/11/2026 · Phiên chính · Opus:** Truong asked to recreate the simulation page; asked clarifying questions only (no new work, context full) *(New session: get answers first)*
- **06/11/2026 · Phiên chính · Opus:** Truong wants the simulation as a real Microsoft system; proposed build kit T4M-BK + own prototype before 15/11; no work started *(Ask Truong which path)*
- **06/11/2026 · Phiên chính · Opus:** Truong pointed out he answered earlier; checked §1 of the research plan: path = build kit for IT; NC-02 stays an IT question *(Plan T4M-BK next session)*
- **06/11/2026 · Phiên chính · Opus:** Wrote plan §9 round 5 T4M-BK (build kit for IT: K0 research, K1/K2 Sonnet, K3 review); asked Truong to approve it and the PR to main *(No code; no child sessions)*
- **06/11/2026 · Phiên chính · Opus:** Truong approved T4M-BK + PR: merged main (CHANGELOG both sides, 157 tests pass), opened PR #13; K0 research -> KQ §8; wrote K1/K2 prompts; root session id updated in plan §3 *(Launching K1)*
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-BK1/BK2 (K1): bo_dung_t4m column module (ECA 30 cols), site script (46 actions), sample CSVs + KIEM_COT_ECA.md, 4 Power Fx files k=1..7; tests first, static syntax test caught 3 generator bugs; 3 mutations caught
- **06/11/2026 · Phiên chính · Opus:** Reviewed K1: sent back 2 blocking fixes (accepted 0e8d0ec, launched K2) (site script nesting, addSPField id), 2 minor; corrected §9 decision 1 (Buoi text differs) *(Waiting K1)*
  - Phiên phụ · 06/11/2026 · Sonnet: K1 fixes after Opus review: site script subactions + $schema + addSPField id, Nhan named formula, xfail -> normal test; tests first (5 red), 2 mutations caught
  - Phiên phụ · 06/11/2026 · Sonnet: T4M-BK3/BK4 (K2): flow table + one-command kit (4 folders + zip) + HUONG_DAN_IT.md; tests first (25); 3 mutations caught (1 weak test tightened)
- **06/11/2026 · Phiên chính · Opus:** K3: reviewed K2 979213b (accepted; rule-2 gap noted); round 5 done *(Next: Truong/IT)*
- **06/11/2026 · Phiên chính · Opus:** Fixed PR #13 CI red (3 causes reproduced locally first); flaky UI test from main split off

**(d) Các phiên có lưu mã (23 phiên, 77 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| wSnLDQPq | 05/11/2026 | 05/11/2026 | 2 | — | 2324aaa ceeeef8 |
| F99hYjD7 | 05/11/2026 | 05/11/2026 | 5 | Z-CLAUDE-GON, T4M-NC | b3481d5 fc183e4 fd4d2ee |
| APhazqHY | 05/11/2026 | 06/11/2026 | 21 | T4M-NC, T4M-M4, T4M-M1, P5 | f341694 3b4ef49 790eb4d |
| rNoH558W | 05/11/2026 | 05/11/2026 | 2 | — | 62a0dc7 ec5a580 |
| NUSf436V | 05/11/2026 | 05/11/2026 | 1 | T4M-Q1..Q3 | 6947ec2 |
| AZU8QavQ | 06/11/2026 | 06/11/2026 | 2 | T4M-DEMO | 5416cf3 4c7ad66 |
| gRBbDN1H | 06/11/2026 | 06/11/2026 | 2 | T4M-GOI-TK | 0e65a25 34ccd56 |
| t7851RAL | 06/11/2026 | 06/11/2026 | 1 | T4M-VH | c34c2ad |
| Hsc1FY4u | 06/11/2026 | 06/11/2026 | 3 | T4M-Q1b-b, T4M-Q1b | b6d406d 4f7c4e2 7f9a6bd |
| SZ6wfJsM | 06/11/2026 | 06/11/2026 | 2 | T4M-DO | bf30863 f240afd |
| 7Lajfo3o | 06/11/2026 | 06/11/2026 | 2 | — | a89b0cc ce342ee |
| wrMDXQXg | 06/11/2026 | 06/11/2026 | 1 | T4M-M1 | d78dcc4 |
| na8W6GrA | 06/11/2026 | 06/11/2026 | 1 | T4M-M4 | d8d47c7 |
| MfgeCCPS | 06/11/2026 | 06/11/2026 | 2 | T4M-M3 | 8711ae1 d9d69fc |
| 2dhwkPzs | 06/11/2026 | 06/11/2026 | 1 | T4M-M5 | c4371e4 |
| ACp7Az4F | 06/11/2026 | 06/11/2026 | 2 | T4M-Q4a/b/c | d887988 0b2bbc8 |
| 3oUwVHfW | 06/11/2026 | 06/11/2026 | 11 | T4M-M6, T4M-DEMO-B | 8d2a278 5fa4cc1 5d6654d |
| 2Prtmm9W | 06/11/2026 | 06/11/2026 | 1 | T4M-M6 | 7e31127 |
| JanVM398 | 06/11/2026 | 06/11/2026 | 2 | T4M-Q5a/b/c | befdb1f 7e274d4 |
| ArvejR4i | 06/11/2026 | 06/11/2026 | 9 | T4M-NC, T4M-BK0 | ee81851 28c83dc fe44472 |
| xgM6Qjmx | 06/11/2026 | 06/11/2026 | 2 | T4M-BK1, BK2 | 0e8d0ec 1fb93d0 |
| 1oBj8zhY | 06/11/2026 | 06/11/2026 | 1 | T4M-BK3, BK4 | 979213b |
| LNw3PrRF | 06/11/2026 | 06/11/2026 | 1 | — | 59503b9 |

### Giai đoạn 9 — Cơ chế xếp mới FA-DAA (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 08/11/2026 — FA-KH (quyết định của Truong): ngoại lệ bất biến 2 cho huy chương mặc định, D11 không chặn
- 08/11/2026 — FA-M3 (một phần, Truong duyệt): đặt huy chương trên đường B, đủ 6 cách đặt
- 10/11/2026 — FA-9b: biên bản bốc thăm bản Excel (đêm 5, Truong duyệt)
- 10/11/2026 — FA-CI3: CI Windows cài python-docx (PR #14, Truong chọn)

**(b) Các mục việc trong `CHANGELOG.md` (42 mục):**

- 08/11/2026 — FA-KH: kế hoạch triển khai FA-DAA và tệp chạy đêm (chỉ tài liệu)
- 08/11/2026 — FA-KH (sửa sau soát hội đồng): D1, D3, D4, D5, D9, D11, D12, FA-9
- 08/11/2026 — FA-KH: báo cáo đêm tự đẩy lên GitHub
- 09/11/2026 — FA-1: mô hình dữ liệu FA-DAA (mục cha A13)
- 09/11/2026 — FA-2: kiểm trước khi chạy FA-DAA (mục cha A5)
- 09/11/2026 — FA-3: huy chương một quỹ (mục cha A13)
- 09/11/2026 — FA-4 đến FA-8: chạy FA-DAA, đóng CLB thiếu người, lý do, bảng nhu cầu, tính chất V§13 (mục cha A13, A5, A6, C3, Z6)
- 09/11/2026 — FA-SOAT: Opus soát đêm 1 (mục cha A13)
- 09/11/2026 — FA-M1: Phiếu thiết lập CLB trên Forms và bộ chuyển đổi (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-M2: Biểu mẫu đăng ký đường B (--fa-daa) (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-M3: Bộ chuyển đổi chế độ FA-DAA (đường A và đường B) (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-M4: Đề biến thể, phân tích câu hỏi và cân bằng điểm giữa các đề (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-M5: Đặc tả Power Apps v2 (đường A) và cột list FA-DAA (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-M6: Tài liệu sau khi xếp (kết quả, phản hồi, khiếu nại, nhắc hạn, điểm danh) (đêm 2, TH = chưa thử trên Microsoft thật)
- 09/11/2026 — FA-SOAT2: soát đêm 2 và mở đêm 3 (chỉ tài liệu, chưa sửa lỗi)
- 09/11/2026 — FA-S8: nhập CSV CLB khi FA tắt giữ nguyên dòng (đêm 3)
- 09/11/2026 — FA-S7, FA-S9: xuất lý do chỉ của lần chạy mới nhất; test rollback bảng FA (đêm 3)
- 09/11/2026 — FA-S3: cân bằng đề không dịch điểm khi một phía có ít bài (đêm 3, TH)
- 09/11/2026 — FA-S1: bài thi lại chỉ tính khi lần đầu bị gắn cờ và đúng đề thi lại (đêm 3, TH)
- 09/11/2026 — FA-S5: cảnh báo khi em làm sai đề được giao (đêm 3, TH)
- 09/11/2026 — FA-S2: bỏ câu theo từng đề (đêm 3, TH)
- 09/11/2026 — FA-S4: báo khi không đọc được giờ làm bài (đêm 3, TH)
- 09/11/2026 — FA-S6: bộ sinh biểu mẫu đăng ký đọc Loại CLB từ Sổ nhập CLB (đêm 3, TH)
- 09/11/2026 — FA-S11: ghép email với mã học sinh cho list KetQua (đêm 3, TH)
- 09/11/2026 — FA-S10: sửa dòng đường B trong bảng D8 (đêm 3, chỉ tài liệu)
- 09/11/2026 — FA-UI-1: công tắc "Xếp theo loại CLB và huy chương" khi tạo không gian làm việc (đêm 3)
- 09/11/2026 — FA-UI-2: cột FA trong bảng CLB ở thẻ Quản lý (đêm 3)
- 09/11/2026 — FA-UI-3: bước "Huy chương" ở màn nhập tại chỗ (đêm 3)
- 09/11/2026 — FA-UI-4: câu lý do ở thẻ kết quả và hai nút xuất (đêm 3)
- 09/11/2026 — FA-UI-5: mục hướng dẫn sử dụng "Xếp theo loại CLB và huy chương" (đêm 3, chỉ tài liệu)
- 09/11/2026 — FA-SOAT3: soát đêm 3 và mở đêm 4 (chỉ tài liệu, chưa sửa lỗi)
- 09/11/2026 — FA-N1: lý do theo từng buổi sau khi chạy lại một phần (đêm 4)
- 09/11/2026 — FA-N2: màn nhập tại chỗ lưu huy chương mặc định và đi theo thứ tự mới (đêm 4)
- 09/11/2026 — FA-N3: câu báo rõ khi bật FA mà tắt điểm quyết tâm (đêm 4)
- 09/11/2026 — FA-N4: cảnh báo CLB chỉ có một đề thì không thi lại được (đêm 4)
- 09/11/2026 — FA-9: biên bản bốc thăm có người chứng kiến (đêm 4)
- 09/11/2026 — FA-10: mô phỏng so sánh chế độ cũ và FA-DAA, hành vi hai kỳ của D1 (đêm 4)
- 10/11/2026 — FA-O1: lý do kết quả sắp theo thứ tự ngày (đêm 5)
- 10/11/2026 — FA-P1: biên bản bốc thăm bản Excel không nhận công thức (soát đêm 5)
- 10/11/2026 — FA-P2: nhập tại chỗ, huy chương mặc định vẫn lưu khi người nhập sang em khác giữa lúc lưu (soát đêm 5)
- 10/11/2026 — FA-CI1: sửa CI đỏ của PR #14 (Windows + văn phong)
- 10/11/2026 — FA-CI2: test giao diện T3-19 hết chập chờn (CI Linux PR #14)

**(c) Các phiên theo tệp bàn giao:**

*Nhánh `claude/keen-ride-72sa7t`* — nguồn `docs/phien/claude__keen-ride-72sa7t.md`. Mục tiêu ghi trong tệp: Implement Truong's FA-DAA vision (`docs/ke_hoach/FA_DAA_VISION.md`, 2026-11-08) for real use THIS term at a school of 500-1000 students on the Microsoft ecosystem: club types FREE / LIMITED / SELECTIVE, three medals per day (60/30/10, one fund) replacing the two-fund determination points, pass mark for SELECTIVE, reserved seats, minimum members, fallback to FREE clubs, a reason for every result, demand table for tea…

- **08/11/2026 · Phiên chính · Opus:** Read vision + code (priority, wharton, STB, registry A5/A6/A13/C3, T4M); wrote plan, night-run file, handoff *(No code changed; D1 blocked; D8 waits for GĐ2)*
- **08/11/2026 · Phiên chính · Opus:** Council review applied: D1 reason, D3, D4, D5->FA-9 record, D9, D11, D12 *(Docs only)*
- **08/11/2026 · Phiên chính · Opus:** Truong decisions: D2 invariant-2 exception (CLAUDE.md), path B gold-override question, D11 no-block equating, D1 deferred *(Docs + CLAUDE.md only)*
- **08/11/2026 · Phiên chính · Opus:** Truong: path B second medal question (swap silver/bronze); built `dat_huy_chuong_duong_b`, tests first (19 red -> green), mutation caught 8/19 *(Converter only; not wired; no kiosk/schema/CSV change)*
  - Phiên phụ · 09/11/2026 · Sonnet: FA-0: venv OK; baseline TestTrungKhit 7 passed, test_wharton_pipeline 29 passed, ruff clean
  - Phiên phụ · 09/11/2026 · Sonnet: FA-1: rules.fa_daa, 4 club cols, giu_cho, So nhap/CSV optional cols; tests/test_fa_du_lieu.py (43), related 1673 passed, kiem_nhanh 7/7, mutation caught
  - Phiên phụ · 09/11/2026 · Sonnet: FA-2: kiem_truoc_fa + hooks (pipeline, health); tests/test_fa_kiem_truoc.py (15); related 1823 passed (+1 expected count test, fixed); mutation caught
  - Phiên phụ · 09/11/2026 · Sonnet: FA-3: huy chuong one fund + submit_huy_chuong + pipeline validation; tests/test_fa_huy_chuong.py (20); related 1992 passed; mutation caught (after adding invalid-value cases)
  - Phiên phụ · 09/11/2026 · Sonnet: FA-4..FA-8 (one commit, overlapping files): chay_fa_daa, minimum-members loop, fa_ly_do, demand table + so_sanh_suc_chua.py, property tests; related 4077 passed (+2 fixed: doc code map, COLLATE THU_TU_BUOI); mutations c…
  - Phiên phụ · 09/11/2026 · Sonnet: Night report 2026-11-09: 9/9 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09.md
- **09/11/2026 · Phiên chính · Opus:** Review night 1: GO. Non-UI tests 4981/1 fail/4 skip; fixed `test_van_phong_tu_nhien` (DAA acronym, f9b9031); invariant 1 3x20x2 identical; mutations 5/5; released night 2 in CHAY_DEM_FA_DAA.md *(report bao_cao_dem/2026-11-09_soat_dem1.md; RUNNING line removed)*
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M1: chuyen_phieu_clb.py + PHIEU_THIET_LAP_CLB.md; tests/test_fa_m1_phieu_clb.py 17; related 201 passed; mutation caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M2: bieu_mau.cac_phan_fa + tao_mau_forms --fa-daa; tests/test_fa_m2_forms_dang_ky.py 10 (mutation caught after adding the >3-clubs case); related 263 passed; old modes byte-identical (diff -r); mutation caught; kiem_…
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M3: chuyen_fa_daa (+doc_lists fa, doc_dang_ky_fa_forms, quy_diem_10, co_nhanh_qua); tests/test_fa_m3_chuyen.py 25; related 266 passed; default-mode cells identical; 3 mutations caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M4: phan_tich_cau_hoi.py + tao_mau_forms --bien-the + converter gate (D11); tests/test_fa_m4_phan_tich.py 24; related 330 passed; old modes identical; 5 mutations caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M5: T4M_DAC_TA_SUA_APP §12 (R39-R54) + bo_dung_t4m ECA_FA + tao_bo_dung_t4m --fa-daa; tests/test_fa_m5_bo_dung.py 10; related 208 passed (after scoping old R1..R38 test); default kit byte-identical; 2 mutations caugh…
  - Phiên phụ · 09/11/2026 · Sonnet: FA-M6: docs/he_sinh_thai/FA_SAU_XEP.md (docs only) + tests/test_fa_m6_tai_lieu.py 6; related passed; 2 mutations caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet: Night 2 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem2.md
- **09/11/2026 · Phiên chính · Opus:** Reviewed night 2: GO; 6 new bugs + 4 open night-1 findings + 1 email gap listed as FA-S1..S11 (not fixed, Truong's instruction); wrote plan §6 and night-3 protocol *(Repro: FA-S3, FA-S4; 197 related tests pass)*
  - Phiên phụ · 09/11/2026 · Opus (đêm 3, Truong yêu cầu): FA-S8: CSV club import keeps the row when FA is off; red first, mutation caught
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S7 export latest run only + FA-S9 rollback test; red first; mutations caught (S9: commit before lock -> red)
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S3: N_NHO when either side small; 1 old expectation changed per spec
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S1 retake rule; red first; 2 mutations caught; converter/T4M tests 252 passed
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S5 wrong-variant warning; red first; mutation caught (2 tests)
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S2 --bo-cau per variant; red first; mutation caught
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S4 unreadable quiz times warning; red first; mutation caught
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S6 generator reads club type; red first; mutation caught; without flag diff -r identical
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S11 email join script + EMAIL_MA_HS.csv; red first; mutation caught; new test file (count 217)
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-S10 plan §4 D8 path-B row fixed
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-UI-1 FA switch in workspace wizard; red first (5/5); mutation caught; ws/wharton UI tests 341 passed after fixing 'em' wording
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-UI-2 club table FA columns; red first; mutation caught; related 2334 passed / 1 skipped
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-UI-3 medal step; red first (4/5); swap mutation caught; related 2704 passed / 1 skipped after wording fix
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-UI-4 reasons column + 2 export buttons; red first; mutation caught; related 2526 passed / 1 skipped
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): FA-UI-5 user guide section 15; doc test red first
  - Phiên phụ · 09/11/2026 · Opus (đêm 3): Night 3 report 2026-11-09: 16/16 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem3.md
- **09/11/2026 · Phiên chính · Opus:** Reviewed night 3: GO; repro FA-N1 (partial run drops other days' reasons) and FA-N2 (on-site lazy path saves no medals); kiem_nhanh 7/7; wrote plan §7 and night-4 protocol *(UI tests not rerun (playwright install did not finish))*
- **09/11/2026 · Phiên chính · Opus:** Handoff at ~400k context (Stop hook): rewrote Current state; night 4 released, not started *(Next session: Read CLAUDE.md + this file)*
- **09/11/2026 · Phiên chính · Opus:** Gave Truong a night-4 schedule prompt (23:13/01:13/03:13 VN); no new work (context over limit) *(Report may be named 2026-11-09_dem4.md or 2026-11-10_dem4.md)*
- **09/11/2026 · Phiên chính · Opus:** Night 4 running on collaborator side; wrote chained auto plan (Opus review night 4 -> Sonnet night 5) in Next steps *(No task created by this session)*
- **09/11/2026 · Phiên chính · Opus:** Gave Truong a self-review/self-fix loop prompt (two recurring tasks, stop rules in Next steps 5); no new work *(Context over limit)*
- **09/11/2026 · Phiên chính · Opus:** Answered vision coverage (projected after night 5: P1 ~90 %, P2 ~95 %, P3 ~30-40 %, overall ~75-80 %; gaps: real Microsoft test/D8, full CI + Windows build, P3 features, admin dashboard §11). No night-4 commits on this branch yet at 2026-11-09 ~23:00 *(No new work)*
- **09/11/2026 · Phiên chính · Opus:** Answered: Forms yes (setup form, quizzes, surveys); Power Apps vs Forms-only registration = D8 open; NOT everything in M365 (kiosk + converters run offline on the IT Windows PC, files moved by Excel/CSV) *(No new work)*
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-N1: per-day latest run reasons + warning; tests/test_fa_n1_ly_do_mot_phan.py 3 (red first); related 1955 passed/1 skipped; mutation caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-N2: on-site lazy medals saved + follow re-rank (js hcTheoNguyenVong); tests/test_giao_dien_fa_n2_luu_mac_dinh.py 3 Chromium red first; related UI 63 passed; mutation caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-N3: fa_can_diem_quyet_tam error code; tests/test_fa_n3_loi_diem_quyet_tam.py 5 red first; related fa+ws 2423 passed (1 count test fixed); mutation caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-N4: single-variant club retake warning + guide line; tests/test_fa_n4_mot_de_khong_thi_lai.py 3 red first; converter/forms tests 129 passed; mutation caught; kiem_nhanh 7/7
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-9: fa_bien_ban.py + export_bien_ban_boc_tham + button; tests/test_fa_bien_ban.py 9 + 1 Chromium; related 112 passed; 2 mutations caught; kiem_nhanh 7/7; pure module written before its tests, API/UI tests red first
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): FA-10: du_lieu_test/mo_phong_fa_daa.py tables only; tests/test_mo_phong_fa_daa.py 9; 3 mutations caught after adding 2 tests; module written before tests
  - Phiên phụ · 09/11/2026 · Sonnet (đêm 4): Night 4 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem4.md
- **10/11/2026 · Phiên chính · Opus:** Status check; recorded Truong decisions (auto review, PR after night 5, D8 waits, Excel lottery record approved); ticked FA-9/FA-10 in Plan *(Docs only)*
  - Phiên phụ · 10/11/2026 · Sonnet (soát, chạy tay): Reviewed night 4: GO; repro FA-O1 (reason rows sort `chu_nhat` before `thu_2`); biên bản after partial run OK; related 2276 passed, Chromium 7, kiem_nhanh 7/7; wrote plan §8 and night-5 protocol; scheduled tasks found s…
  - Phiên phụ · 10/11/2026 · Sonnet (đêm 5): FA-O1: reasons sorted with khoa_sap_buoi; test in test_fa_n1_ly_do_mot_phan.py red first; related 2135 passed/1 skipped; mutation caught; ruff clean
  - Phiên phụ · 10/11/2026 · Sonnet (đêm 5): FA-9b: fa_bien_ban.ghi_xlsx + path_xlsx + button/i18n; 5 tests red first + Chromium check; 3 mutations caught (2 unit/API, 1 UI); related 2195 passed/1 skipped; ruff clean; kiem_nhanh 7/7
  - Phiên phụ · 10/11/2026 · Sonnet (đêm 5): Night 5 report 2026-11-10: 2/2 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-10_dem5.md

**(d) Các phiên có lưu mã (8 phiên, 62 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| dsJPAz6x | 09/11/2026 | 09/11/2026 | 5 | FA-BC, FA-4..FA-8, FA-3, FA-2, FA-1 | a80e626 1037920 702b09e |
| ch62p4KC | 09/11/2026 | 09/11/2026 | 3 | FA-SOAT | 50cfa5d f9b9031 33d4fa9 |
| UGSanNrv | 09/11/2026 | 09/11/2026 | 8 | FA-BC, FA-M6, FA-M5, FA-M4, FA-M3, FA-M2, FA-M1 | 3e7d8a7 58bc370 cd1fe46 |
| o8eUqFKt | 09/11/2026 | 09/11/2026 | 9 | FA-KH, FA-SOAT3, FA-SOAT2 | 99d4724 8003e9a 9f740c2 |
| ohi9Fo5P | 09/11/2026 | 09/11/2026 | 17 | FA-BC, FA-UI-5, FA-UI-4, FA-UI-3, FA-UI-2, FA-UI-1, FA-S10, FA-S11 | c962bb8 5bf7a8d 0c8e5f8 |
| PgyEfvMe | 09/11/2026 | 09/11/2026 | 7 | FA-BC, FA-10, FA-9, FA-N3, FA-N4, FA-N2, FA-N1, FA-N0 | 1198ef5 6c7bf4d cf90452 |
| B56GWZ8J | 10/11/2026 | 10/11/2026 | 6 | FA-BC, FA-9b, FA-O1, FA-O0, FA-SOAT | b93b3d0 d9482a7 fff8df5 |
| TsLFG9TZ | 10/11/2026 | 10/11/2026 | 7 | FA-CI3, FA-CI2, FA-CI1, FA-SOAT, FA-P2, FA-P1 | c6e5e6a a7e91e4 45d6c7a |

### Giai đoạn 10 — Lập nhật ký AI này (chi tiết)

**(a) Quyết định của Truong (tiêu đề mục trong `CHANGELOG.md`):**

- 10/11/2026 — AI-LOG: nhật ký AI chỉ từ dữ liệu trong repo (Truong yêu cầu)

**(d) Các phiên có lưu mã (2 phiên, 6 lần lưu):**

| Mã phiên | Từ | Đến | Số lần lưu | Mã mục việc | Lần lưu ví dụ |
|---|---|---|---|---|---|
| 7JUvpaoF | 09/11/2026 | 10/11/2026 | 4 | AI-LOG, FA-KH | c43d4d9 4adc3eb 1300e4a |
| xW9hz2Sq | 10/11/2026 | 10/11/2026 | 2 | AI-LOG | 9644288 e6052ec |

---
Mục 1–6 viết tay từ ghi chép trong kho mã; mục 7 dựng tự động bằng `docs/nhat_ky_ai/dung_nhat_ky_ai.py`.
