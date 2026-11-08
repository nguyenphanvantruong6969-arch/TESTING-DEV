# VISION – Phần mềm xếp học sinh vào CLB (FA-DAA, VISEF 21-03)

> Tài liệu dành cho Claude Code. Mô tả đầy đủ cơ chế, workflow và yêu cầu triển khai đã được thống nhất.
> Phần mềm **đã có lõi Gale–Shapley (student-proposing deferred acceptance)** và **quỹ điểm quyết tâm**. Nhiệm vụ: tinh chỉnh theo spec này, **không viết lại lõi**.

---

## 0. Bối cảnh & ràng buộc

| Mục | Giá trị |
|---|---|
| Quy mô | 500–1000 học sinh, 15–30 CLB, 1 lần xếp mỗi học kỳ |
| Đơn vị xếp | Mỗi **ngày sinh hoạt** là một bài toán xếp riêng; mỗi học sinh tối đa 1 CLB/ngày |
| Thiết bị | Học sinh tự đăng ký và làm thử thách **trên điện thoại, ở nhà, không có người coi** |
| Phạm vi thay đổi | Chỉ sửa phần mềm + chia loại CLB. Không đổi giờ học/quy định trường |
| Thời hạn | Dùng thật **học kỳ này** → ưu tiên thay đổi rẻ, ít rủi ro |
| Người dùng | Học sinh THPT, **lười**, coi CLB là việc ít quan trọng |
| Ngôn ngữ giao diện | Tiếng Việt, **không thuật ngữ kỹ thuật** trên màn hình học sinh/giáo viên |

**Nguyên tắc thiết kế (theo thứ tự ưu tiên):**
1. Cách dễ nhất cũng phải là cách đúng (mặc định tốt, không bắt học sinh tính toán).
2. Ghi thật nguyện vọng không bao giờ bị thiệt (giữ tính chất của Gale–Shapley; không thêm ưu tiên phụ thuộc thứ hạng nguyện vọng ngoài cơ chế huy chương bên dưới).
3. Minh bạch: mọi kết quả có lý do; bốc thăm tái lập được.
4. Không sửa tay kết quả; mọi thay đổi đi qua quy trình trong phần mềm.
5. Đo trước khi tin: mọi tính năng có chỉ số theo dõi.

---

## 1. Thuật ngữ (dùng trong code)

| Thuật ngữ | Ý nghĩa |
|---|---|
| `ClubType.FREE` | CLB Tự do tham gia – không bao giờ từ chối học sinh |
| `ClubType.LIMITED` | CLB Giới hạn chỗ – có số chỗ, không có thử thách |
| `ClubType.SELECTIVE` | CLB Tuyển chọn – có số chỗ và thử thách |
| `Medal` | Huy chương `GOLD`/`SILVER`/`BRONZE` = 60/30/10 điểm quyết tâm |
| `Compensation` | Ưu tiên bù cho học sinh thua bốc thăm ở NV1 kỳ trước |
| `LotteryOrder` | Hoán vị ngẫu nhiên học sinh cho một ngày, sinh từ seed công khai |
| `DemandReview` | Pha giáo viên xem nhu cầu và tăng số chỗ |

---

## 2. Mô hình dữ liệu

```text
Term            { id, name, phase: TermPhase, created_at }
Day             { id, term_id, weekday }

Club            { id, term_id, day_id, name, description_1line, photo_url,
                  type: FREE|LIMITED|SELECTIVE,
                  capacity: int|null,            # null cho FREE
                  room_capacity: int|null,       # FREE: sức chứa mỗi nhóm
                  can_open_groups: bool,         # bắt buộc true với FREE
                  min_members: int,
                  reserved_student_ids: [id],    # ban điều hành / thành viên cũ (công khai số lượng)
                  challenge: Challenge|null,     # bắt buộc với SELECTIVE
                  teacher_id,
                  approved_selective: bool }     # ban quản lý duyệt SELECTIVE

Challenge       { club_id, kind: QUIZ|MEDIA, pass_mark: int (0–10),
                  n_items: 10–15, per_item_seconds: 60, total_minutes: 8–12,
                  item_bank_id, rubric_text (MEDIA), graders_required: 2 (MEDIA) }

Student         { id, school_email, class, grade, homeroom_teacher_id }

Registration    { student_id, day_id, ranked_club_ids: [id],      # thứ tự nguyện vọng
                  medals: {club_id: GOLD|SILVER|BRONZE},          # tối đa 1 huy chương/CLB
                  status: DRAFT|SUBMITTED, updated_at }           # lưu tự động, lần lưu cuối được tính

ChallengeAttempt{ student_id, club_id, item_ids, responses: [{item_id, answer, seconds}],
                  fast_ratio, retake_offered: bool, attempt_no: 1|2,
                  raw_score, final_score: int (0–10)|null, status }

MediaSubmission { student_id, club_id, file_url, grader_scores: [{grader_id, score}], final_score }

LotterySeed     { term_id, day_id, public_source_text, announced_at, seed_hash }
LotteryOrder    { day_id, student_id, rank }                      # rank nhỏ = may hơn

CompensationCredit { student_id, earned_term_id, used_term_id|null }

Allocation      { term_id, day_id, student_id, club_id, group_no|null, run_id }
DecisionLog     { run_id, day_id, student_id, club_id,
                  outcome: ACCEPTED|REJECTED,
                  reason: BELOW_PASS|SCORE|MEDAL|COMPENSATION|LOTTERY|RESERVED|CLUB_CLOSED|NOT_ATTEMPTED,
                  cutoff_snapshot: {score, medal_points, lottery_rank}, rank_in_list }

Feedback        { student_id, term_id, satisfaction 1–5, understood_reason: bool,
                  hardest_part: enum, week3_still_attending: bool|null, week3_want_change: bool|null }
Attendance      { club_id, student_id, session_no 1–3, present: bool, excused: bool }
Waitlist        { club_id, student_id, position }                 # theo LotteryOrder
Appeal          { student_id, term_id, text, kind: DATA_ERROR, status, created_at }  # chỉ trong 3 ngày
```

`TermPhase`: `SETUP → PRECHECK → OPEN → CLOSED → DEMAND_REVIEW → ALLOCATED → PUBLISHED → APPEAL → MONITORING → ARCHIVED`

---

## 3. Workflow tổng

```text
SETUP           Giáo viên điền Phiếu thiết lập CLB (§4.1) → phân loại CLB tự động
PRECHECK        Phần mềm kiểm tra (§4.2); ban quản lý duyệt CLB SELECTIVE
OPEN (≥5 ngày)  Học sinh đăng ký nguyện vọng + huy chương; làm thử thách (§5, §6, §7)
CLOSED          Đóng cổng; học sinh không đăng ký → gán CLB FREE (§8.6)
DEMAND_REVIEW   Giáo viên xem nhu cầu, chỉ được TĂNG chỗ / mở nhóm, 48 giờ (§4.3)
ALLOCATED       Chạy xếp chỗ theo ngày (§8)
PUBLISHED       Học sinh xem kết quả có lý do + 3 câu phản hồi (§9.1)
APPEAL (3 ngày) Khiếu nại chỉ về lỗi dữ liệu (§9.2)
MONITORING      Điểm danh 3 buổi, danh sách chờ, khảo sát tuần 3 (§9.3)
ARCHIVED        Lưu số liệu; tính ưu tiên bù; gợi ý số chỗ kỳ sau (§10)
```

---

## 4. Workflow giáo viên

### 4.1. Phiếu thiết lập CLB (pha SETUP)

5 câu hỏi, giao diện tiếng Việt đơn giản:
1. Ngày, giờ, địa điểm sinh hoạt.
2. CLB có mở thêm nhóm được nếu đông không? Nếu **không**: số chỗ tối đa + lý do (phòng/dụng cụ/người hướng dẫn).
3. Số thành viên tối thiểu để CLB hoạt động.
4. CLB có cần kỹ năng tối thiểu không? Nếu **có**: loại thử thách (trắc nghiệm / video / ảnh), mốc tối thiểu (thang 10), bảng tiêu chí.
5. Danh sách chỗ giữ cho ban điều hành / thành viên cũ (số lượng được công khai).

**Phân loại tự động:**
- Câu 2 = có → `FREE` (`can_open_groups = true`, `capacity = null`, nhập `room_capacity` mỗi nhóm).
- Câu 2 = không, câu 4 = không → `LIMITED`.
- Câu 2 = không, câu 4 = có → `SELECTIVE` (cần `approved_selective = true` từ ban quản lý; mục tiêu ~1/4–1/3 số CLB).

**Quy tắc:**
- Loại CLB khóa khi chuyển sang `OPEN`, không đổi giữa chừng.
- CLB bị giới hạn thật bởi phòng/dụng cụ **không được** khai là `FREE`.
- Giáo viên không nộp phiếu trước hạn → mặc định `LIMITED` với số chỗ kỳ trước (hoặc giá trị admin nhập).
- Từ kỳ thứ hai: hiển thị **gợi ý số chỗ** dựa trên nhu cầu kỳ trước (§10).

### 4.2. Kiểm tra trước khi mở cổng (PRECHECK) – chặn mở cổng nếu fail

- Mỗi ngày có ≥ 1 CLB `FREE`.
- Với mỗi ngày: tổng sức chứa (FREE tính theo `room_capacity × số nhóm tối đa`, hoặc vô hạn nếu mở nhóm không giới hạn) ≥ số học sinh có hoạt động ngày đó.
- Mọi CLB `SELECTIVE` có `challenge` hợp lệ và đã được duyệt.
- Từ kỳ 2: cảnh báo CLB `FREE` dự báo vượt `room_capacity` (cần chuẩn bị nhóm).

### 4.3. Bảng nhu cầu (DEMAND_REVIEW, 48 giờ)

Mỗi giáo viên thấy **chỉ con số, không thấy tên học sinh**:
- Số học sinh chọn CLB làm NV1.
- Số học sinh có CLB trong danh sách.
- Số em đã vượt mốc thử thách (SELECTIVE).
- Số chỗ hiện tại.

Hành động cho phép:
- `LIMITED`/`SELECTIVE`: **chỉ tăng** `capacity` (không được giảm so với số đã khai).
- `FREE`: xác nhận số nhóm sẽ mở.
- Hết 48 giờ không phản hồi → giữ nguyên.

Học sinh **không** thấy số liệu nhu cầu trong lúc đăng ký.

### 4.4. Sau khi xếp
- Điểm danh 3 buổi đầu trên phần mềm (§9.3).
- Xem danh sách thành viên, xuất Excel.

---

## 5. Workflow học sinh (mobile-first)

### 5.1. Đăng ký nguyện vọng (pha OPEN)
- Đăng nhập bằng email trường. Một học sinh = một bản đăng ký mỗi ngày; sửa được đến hết hạn, lần lưu cuối được tính.
- Màn hình chỉ có **một câu hướng dẫn** ở đầu:
  *"Xếp đúng thứ tự em thích. Xếp CLB khó vào lên đầu không làm em mất cơ hội ở CLB sau."*
- Lọc theo ngày. Thứ tự CLB **xáo ngẫu nhiên cho mỗi học sinh**.
- Thẻ CLB: tên, mô tả 1 dòng, lịch, số chỗ, nhãn loại, có thử thách hay không, 1 ảnh.
  - FREE: *"Tự do tham gia – em chắc chắn có chỗ."*
  - LIMITED: *"Giới hạn N chỗ – nếu đông, xét huy chương rồi bốc thăm."*
  - SELECTIVE: *"Tuyển chọn – N chỗ – có thử thách X phút. Dưới mốc M điểm sẽ không được xét."*
- Xếp thứ tự bằng nút ▲▼ (không bắt buộc kéo thả).
- **Bắt buộc tối thiểu 3 nguyện vọng mỗi ngày** (hoặc tất cả nếu ngày đó có ít hơn 3 CLB). Cảnh báo nếu danh sách không có CLB `FREE`: *"Thêm một CLB Tự do để chắc chắn có chỗ."*
- Tự lưu sau mỗi thao tác (DRAFT), mở lại làm tiếp.
- Nộp → màn hình xác nhận + email tóm tắt.

### 5.2. Nhắc hạn
- Thông báo/email: khi mở cổng, còn 2 ngày, còn 3 giờ.
- Học sinh có NV là SELECTIVE chưa làm thử thách: nhắc riêng 2 lần trước hạn.
- Sau 3 ngày nếu tỷ lệ đăng ký < 50%: gửi danh sách học sinh chưa đăng ký cho giáo viên chủ nhiệm (§11).

---

## 6. Cơ chế huy chương (thay "ngôi sao" và "điểm quyết tâm" trên giao diện)

### 6.1. Quy tắc
- Mỗi học sinh có **3 huy chương mỗi ngày**: vàng (60), bạc (30), đồng (10).
- **Gộp chung cho mọi loại CLB trong ngày** (không chia riêng Tuyển chọn / Giới hạn).
- **Mặc định:** gán vàng/bạc/đồng cho 3 CLB `LIMITED`/`SELECTIVE` xếp cao nhất trong danh sách của ngày đó (bỏ qua CLB `FREE` vì không cần huy chương).
- Học sinh được **hoán đổi** huy chương giữa các CLB trong danh sách; **mỗi CLB tối đa 1 huy chương**; không dồn.
- Nếu danh sách có ít hơn 3 CLB không-FREE: huy chương thừa bỏ trống.
- Khi học sinh đổi thứ tự nguyện vọng và **chưa từng chỉnh tay** huy chương → huy chương tự cập nhật theo thứ tự mới. Đã chỉnh tay → giữ nguyên, hiển thị nhắc nhẹ.
- Khi đặt vàng vào CLB SELECTIVE: hiển thị *"Huy chương ở CLB Tuyển chọn chỉ dùng khi bằng điểm, và chỉ khi em vượt mốc."*
- **Không hiển thị** số huy chương mỗi CLB đang nhận trong lúc đăng ký.

### 6.2. Ánh xạ vào phần mềm hiện tại
- Dùng lại engine điểm quyết tâm: **gộp 2 quỹ cũ thành 1 quỹ 100 điểm/ngày**, phân bổ cố định 60/30/10 theo huy chương.
- `medal_points(student, club) ∈ {60, 30, 10, 0}`.
- Chỉ **thứ tự** vàng > bạc > đồng > không có ý nghĩa; giá trị 60/30/10 giữ để tương thích quỹ 100 điểm.

### 6.3. Vì sao chọn (để không bị đổi lại)
Mô phỏng (dữ liệu giả, 300 lần): huy chương có tỷ lệ bốc thăm thấp nhất (57% so với 67% của 1 sao), tỷ lệ vào 1 trong 2 NV đầu cao nhất (63%), và học sinh lười gần bằng học sinh tính toán nhất. Chia điểm tự do: học sinh lười chỉ 5–16% vào NV đầu/top 2 → **không dùng lại chia điểm tự do**. Gộp chung tốt hơn chia riêng (NV1 36% so với 29%).

---

## 7. Thử thách (chỉ CLB SELECTIVE)

### 7.1. Thiết kế
- Chỉ học sinh có CLB đó trong danh sách mới thấy/làm thử thách của CLB đó.
- 8–12 phút, 10–15 câu, ít chữ; có câu **điền đáp số** (không chỉ trắc nghiệm).
- Đầu bài: *"Điểm bài này quyết định thứ tự xét của em vào CLB."*
- Loại `MEDIA`: nộp video ≤ 30 giây hoặc ảnh, quay/chụp ngay trên điện thoại; 2 người chấm độc lập, ẩn tên, lấy trung bình, làm tròn số nguyên.

### 7.2. Chống làm qua loa
- Ghi thời gian từng câu.
- Câu trả lời trong < 10% thời gian trung vị của câu đó (tính trên các bạn khác; với đợt đầu dùng ngưỡng tĩnh do admin đặt) = **trả lời quá nhanh**.
- Hiện nhắc ngay: *"Em trả lời rất nhanh – hãy đọc kỹ câu hỏi."*
- `fast_ratio > 0.3` → `retake_offered = true`, cho làm lại **1 lần** trước hạn. Không làm lại → giữ điểm lần 1.

### 7.3. Chống gian lận (không có người coi)
- Giới hạn thời gian mỗi câu (mặc định 60 giây).
- Ngân hàng câu hỏi: mỗi học sinh một bộ câu khác nhau, **cùng cơ cấu độ khó** (vd. 4 dễ + 4 vừa + 2 khó); xáo thứ tự câu và đáp án.
- Hỏi cách hiểu, không hỏi ghi nhớ (hướng dẫn cho người soạn câu).
- Chỉ 1 lần làm (trừ khi được mời làm lại).
- Lưu sau mỗi câu; mất mạng vào lại làm tiếp; đồng hồ dừng khi mất kết nối.
- Màn hình đầu thông báo: *"Buổi sinh hoạt đầu có phần thử nhanh tương tự."* (chỉ bật nếu CLB xác nhận sẽ làm thật – cờ `first_session_check`).

### 7.4. Chấm và xét
- `final_score`: số nguyên 0–10.
- `final_score < pass_mark` → không được xét CLB đó (`BELOW_PASS`), tự chuyển NV kế tiếp.
- Không làm thử thách trước hạn → `NOT_ATTEMPTED`, xử lý như dưới mốc.
- Trên mốc: **xếp theo điểm** (không dùng Đạt/Chưa đạt, không chia mức). Lý do: mô phỏng cho thấy xếp theo điểm chọn đúng người hơn (69% vs 66% chia mức vs 40% Đạt/Chưa đạt), ít bốc thăm hơn, 0 trường hợp "điểm cao hơn mà trượt".

### 7.5. Phân tích câu hỏi sau khi thi (trước khi xếp)
- Mỗi câu: % đúng; độ phân biệt = % đúng của 1/3 nhóm điểm cao − % đúng của 1/3 nhóm điểm thấp.
- Độ phân biệt < 0 → đánh dấu câu lỗi, admin xác nhận bỏ, **chấm lại cho mọi học sinh**.
- Báo cáo câu > 90% đúng hoặc < 20% đúng để sửa kỳ sau.
- Theo dõi độ lệch giữa 2 người chấm (MEDIA); trung bình > 1,5 điểm → cảnh báo sửa tiêu chí.

---

## 8. Thuật toán xếp chỗ

### 8.1. Khung
- Chạy **riêng cho từng ngày**, student-proposing deferred acceptance (giữ nguyên lõi hiện có).
- Học sinh đề nghị lần lượt theo `ranked_club_ids`.

### 8.2. Khóa ưu tiên tại mỗi CLB (sắp xếp tăng dần, phần tử đầu ưu tiên cao nhất)

```text
SELECTIVE:
  if final_score < pass_mark or not attempted: reject immediately (BELOW_PASS / NOT_ATTEMPTED)
  key = ( -is_reserved, -final_score, -medal_points, -has_compensation, lottery_rank )

LIMITED:
  key = ( -is_reserved, -medal_points, -has_compensation, lottery_rank )

FREE:
  không bao giờ từ chối; capacity = ∞
  sau khi xếp: nếu số thành viên > room_capacity → chia nhóm (group_no) và báo giáo viên
```

- `is_reserved`: học sinh trong `reserved_student_ids` **và** có ghi CLB đó trong danh sách.
- Mỗi lần từ chối ghi `DecisionLog` với lý do = tiêu chí đầu tiên phân biệt học sinh bị loại với học sinh cuối cùng được giữ (`SCORE`, `MEDAL`, `COMPENSATION`, `LOTTERY`, `RESERVED`).

### 8.3. Bốc thăm
- Mỗi ngày **một hoán vị** dùng chung cho mọi CLB của ngày đó.
- Seed từ chuỗi công khai được báo trước (vd. kết quả xổ số ngày X) + `day_id`: `seed = SHA256(public_source_text + "|" + term_id + "|" + day_id)`.
- Hoán vị sinh từ seed bằng PRNG xác định; lưu `LotterySeed` và `LotteryOrder`; chạy lại phải ra đúng kết quả.
- Không ai (kể cả admin) sửa được thứ tự sau khi sinh.
- Học sinh xem được số thứ tự bốc thăm của mình sau khi công bố.

### 8.4. Ưu tiên bù
- Học sinh bị từ chối ở **NV1** với lý do `LOTTERY` trong kỳ T → tạo `CompensationCredit(earned_term=T)`.
- Kỳ T+1: `has_compensation = 1` ở mọi CLB; credit bị **dùng** (gán `used_term_id`) khi nó là tiêu chí quyết định giúp học sinh được nhận. Mỗi credit dùng 1 lần.
- Theo dõi số credit mỗi kỳ (phát hiện lạm dụng).

### 8.5. CLB dưới số tối thiểu
- Sau khi xếp: CLB `LIMITED`/`SELECTIVE` có thành viên < `min_members` → đóng CLB, chạy lại toàn bộ ngày đó **với cùng `LotteryOrder`**, lặp đến khi ổn định. Học sinh bị ảnh hưởng nhận lý do `CLUB_CLOSED`.

### 8.6. Học sinh không đăng ký
- Hết hạn không có bản `SUBMITTED` → gán vào CLB `FREE` của ngày đó (CLB ít người nhất, hòa thì theo `LotteryOrder`); báo học sinh và giáo viên chủ nhiệm.

### 8.7. Học sinh bị từ chối mọi nguyện vọng
- Không xảy ra nếu học sinh có CLB `FREE` trong danh sách. Nếu không có → gán CLB `FREE` còn chỗ của ngày đó + mời tham gia vòng 2 (§9.3).

### 8.8. Tính năng tùy chọn (feature flag, mặc định TẮT)
- `stable_improvement_cycles`: sau DA, tìm vòng đổi chỗ chỉ vi phạm thứ tự bốc thăm (không vi phạm điểm/huy chương/ưu tiên bù) mà mọi người trong vòng đều được NV tốt hơn (Erdil & Ergin, 2008). Chỉ bật nếu mô phỏng cho thấy lợi ích đáng kể.

---

## 9. Sau khi xếp

### 9.1. Màn hình kết quả (PUBLISHED)
Luôn có lý do, sinh từ `DecisionLog`. Mẫu câu:
- Được NV1: *"Em được xếp vào {CLB} – nguyện vọng 1 của em."*
- `SCORE`: *"{CLB} đủ chỗ với các bạn có điểm thử thách cao hơn (điểm chuẩn {x}, em {y})."*
- `MEDAL`: *"Em và các bạn bằng điểm; các bạn có huy chương cao hơn ở {CLB} được xét trước."*
- `LOTTERY`: *"Em bằng {n} bạn khác ở mọi tiêu chí, tranh {k} chỗ cuối; số bốc thăm của em chưa trúng. Em đứng thứ {p} danh sách chờ và có ưu tiên bù kỳ sau."*
- `BELOW_PASS`: *"Em chưa đạt mốc {m} điểm của {CLB}."* + gợi ý cải thiện từ rubric (nếu có).
- `CLUB_CLOSED`: *"{CLB} không đủ thành viên tối thiểu nên tạm không mở kỳ này."*

Ngay dưới kết quả: **3 câu, mỗi câu 1 chạm** – hài lòng 1–5; "Em có hiểu vì sao được xếp như vậy?" có/không; "Phần nào khó nhất?" (chọn: chọn CLB / xếp thứ tự / huy chương / thử thách / không có).

### 9.2. Khiếu nại (APPEAL, 3 ngày)
- Gửi trong phần mềm; chỉ xét **lỗi dữ liệu** (nhập sai, lỗi hệ thống).
- Sửa dữ liệu → chạy lại thuật toán với cùng seed; không sửa tay kết quả.

### 9.3. Theo dõi (MONITORING)
- Giáo viên điểm danh 3 buổi đầu. Vắng **2/3 buổi không phép** → giải phóng chỗ.
- Chỗ trống → mời học sinh đầu danh sách chờ (thứ tự = `LotteryOrder` trong số học sinh bị từ chối ở CLB đó và có ghi CLB đó cao hơn CLB hiện tại).
- Vòng 2: học sinh chưa có CLB mong muốn được chọn trong các chỗ còn trống.
- Tuần 3: thông báo 2 câu – "Em còn đi CLB không?", "Em muốn đổi không?".

---

## 10. Dữ liệu cho kỳ sau (ARCHIVED)
- Nhu cầu mỗi CLB (NV1, tổng lượt ghi, số vượt mốc) → gợi ý `capacity` kỳ sau = nhu cầu NV1 kỳ trước (chặn trên bởi giới hạn giáo viên khai).
- Câu thử thách lỗi, độ lệch người chấm.
- Tỷ lệ học sinh đổi huy chương khỏi mặc định.
- `CompensationCredit` mới.

---

## 11. Dashboard admin & chỉ số

| Chỉ số | Mục tiêu |
|---|---|
| Học sinh không có CLB | 0 |
| Vào NV1 / vào 1 trong 2 NV đầu | Tăng so với kỳ trước |
| Tỷ lệ quyết định bằng dữ liệu vs bốc thăm (từ `DecisionLog`) | Theo dõi; mục tiêu giảm bốc thăm |
| Học sinh từng thua bốc thăm ≥ 1 lần | Theo dõi |
| Tỷ lệ đăng ký sau 3 ngày | ≥ 50% (dưới → báo GVCN) |
| Làm thử thách nghiêm túc (không bị cờ) | > 90% |
| Độ lệch 2 người chấm | < 1,5 điểm |
| Đi đủ 3 buổi đầu | > 85% |
| Hài lòng trung bình | ≥ 3,5/5 |
| Hiểu lý do kết quả | Theo dõi |
| Tỷ lệ đổi huy chương khỏi mặc định | Theo dõi (tăng mạnh → xem lại cơ chế) |

---

## 12. Module mô phỏng (để báo cáo VISEF và kiểm thử)

- Sinh dữ liệu giả: N học sinh, K CLB/ngày, D ngày; mức thích = độ hot chung + sở thích riêng; điểm thử thách = năng lực + nhiễu ±1.
- Ba kiểu hành vi: lười (giữ mặc định), thật lòng, tính toán (chuyển vàng khỏi CLB quá đông). Tỷ lệ cấu hình được.
- **Chế độ so sánh:** cùng dữ liệu, chạy cách cũ (điểm thi + chia 2 quỹ điểm quyết tâm) vs cách mới.
- Xuất: % NV1, % top 2, % không có CLB, % quyết định theo từng lý do, % thua bốc thăm theo kiểu học sinh.
- Tham chiếu kết quả mô phỏng đã chạy (để sanity check, không phải yêu cầu cứng):

| Kịch bản | Dữ liệu quyết định | Bốc thăm | HS từng thua bốc thăm |
|---|---|---|---|
| Cơ chế mới, số chỗ chia đều | 52% | 48% | 49% |
| + Số chỗ khớp nhu cầu | 66% | 34% | 26% |

  Cùng tổng số chỗ, chia theo nhu cầu: NV1 tăng từ ~48% lên ~79% → **bảng nhu cầu (§4.3) là đòn bẩy lớn nhất**.

---

## 13. Tiêu chí chấp nhận (test)

1. Ghi thật thứ tự nguyện vọng là tối ưu khi cố định huy chương (property test: không học sinh nào cải thiện kết quả chỉ bằng cách đổi thứ tự nguyện vọng).
2. Kết quả **ổn định**: không tồn tại cặp (học sinh, CLB) mà học sinh thích CLB hơn chỗ hiện tại và CLB xếp học sinh trên một thành viên hiện có theo khóa §8.2.
3. CLB `FREE` không bao giờ từ chối.
4. Không CLB `LIMITED`/`SELECTIVE` vượt `capacity`.
5. Chạy lại với cùng seed → kết quả giống hệt.
6. Học sinh dưới mốc không bao giờ được nhận vào CLB `SELECTIVE`.
7. Ở CLB `SELECTIVE`, không học sinh nào bị từ chối trong khi một học sinh điểm thấp hơn được nhận.
8. Mỗi CLB nhận tối đa 1 huy chương từ một học sinh; mỗi học sinh tối đa 3 huy chương/ngày.
9. Mọi từ chối có `DecisionLog` với lý do hợp lệ.
10. Giáo viên không giảm được `capacity` trong `DEMAND_REVIEW`; không thấy tên học sinh.
11. Đóng CLB thiếu người → chạy lại hội tụ, không vòng lặp vô hạn.
12. `CompensationCredit` chỉ tạo khi bị từ chối ở NV1 do `LOTTERY`, và chỉ dùng 1 lần.

---

## 14. Ưu tiên triển khai (học kỳ này)

| Ưu tiên | Hạng mục |
|---|---|
| P1 | Câu hướng dẫn 1 dòng, tự lưu, nhắc hạn, tối thiểu 3 NV, huy chương mặc định (§5, §6) |
| P1 | Phiếu thiết lập + phân loại CLB + PRECHECK (§4.1, §4.2) |
| P1 | Bảng nhu cầu cho giáo viên (§4.3) |
| P2 | Thử thách: giới hạn thời gian, ghi thời gian từng câu, cờ trả lời nhanh, ngân hàng câu, xáo câu (§7) |
| P2 | Khóa ưu tiên mới + bốc thăm seed công khai + DecisionLog + màn hình kết quả có lý do + 3 câu phản hồi (§8, §9.1) |
| P3 | Điểm danh, danh sách chờ, vòng 2, khảo sát tuần 3, khiếu nại (§9.2, §9.3) |
| P3 | Ưu tiên bù (có tác dụng từ kỳ 2), gợi ý số chỗ từ kỳ trước (§8.4, §10) |
| P3 | Module mô phỏng + chế độ so sánh (§12) |

---

## 15. Nhật ký quyết định (KHÔNG đưa lại các phương án đã loại)

| Phương án | Quyết định | Lý do |
|---|---|---|
| Chia điểm quyết tâm tự do (2 quỹ × 100) | Loại khỏi giao diện | Học sinh phải đoán người khác; học sinh lười thiệt nặng |
| 1 ngôi sao / ngày | Thay bằng huy chương | Huy chương ít bốc thăm hơn, top 2 cao hơn |
| Huy chương chia riêng theo loại CLB | Loại | Huy chương mất ý nghĩa; NV1 thấp hơn |
| Ưu tiên theo thứ hạng nguyện vọng ("phương án 3") | Loại | Phá tính chất ghi thật không thiệt |
| Chỉ chấm Đạt / Chưa đạt; chia mức điểm theo sai số | Loại | Kém chính xác hơn xếp theo điểm, nhiều bốc thăm hơn |
| Tự chuyển CLB Tự do thành Giới hạn khi đông | Loại | Phá lời hứa "chắc chắn có chỗ"; thay bằng mở thêm nhóm |
| Ai nộp trước được ưu tiên | Loại | Thưởng cho mạng/điện thoại tốt, gây nghẽn |
| Course Match (Wharton) | Không làm kỳ này | 1 CLB/ngày → lợi ích nhỏ; quá phức tạp |
| "Máy đặt sao giùm" (bản đơn giản) | Loại | Mô phỏng cho kết quả kém hơn (dồn cả trường sang NV2) |
| Sao theo tuần | Để sau | +4% hài lòng; cần thêm kiểm chứng |
| Vòng đổi chỗ sau bốc thăm | Feature flag, tắt | Có thể làm lợi cho học sinh tính toán; cần mô phỏng |

---

## 16. Tài liệu tham khảo
- Gale & Shapley (1962) – deferred acceptance.
- Abdulkadiroğlu, Che & Yasuda (2015) – "Expanding Choice in School Choice" (cơ sở cho tín hiệu ưu tiên khi hòa).
- Abdulkadiroğlu, Pathak & Roth (2009) – NYC high school match, single tie-breaking.
- Abdulkadiroğlu, Pathak, Roth & Sönmez (2006) – Boston chuyển sang DA.
- Erdil & Ergin (2008) – stable improvement cycles.
- Budish, Cachon, Kessler & Othman (2017) – Course Match (Wharton).
- Lindner, Lüdtke & Nagy (2019); Wise & Kuhfeld (2019) – trả lời quá nhanh trong bài kiểm tra ít quan trọng.
- Johnson & Goldstein (2003) – sức mạnh của mặc định.
