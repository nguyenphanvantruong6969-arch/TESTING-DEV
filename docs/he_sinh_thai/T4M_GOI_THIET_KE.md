# T4M-GOI-TK. Thiết kế gói nhiều buổi (tiếng Nhật) — 06/11/2026

Mã việc: **T4M-GOI-TK** (bước S2 của `T4M_KE_HOACH_TU_DONG.md`). **Chỉ thiết kế, không có mã** (Truong 06/11/2026). Mọi con số ước lượng đều ghi "(ước lượng)". Nguồn đã đọc: `T4M_KE_HOACH_NGHIEN_CUU.md` §1; `docs/KE_HOACH_NHIEU_BUOI.md` §2, §5; sổ 33 mục A3, A7, A8, A11, A12, G3; mã `run_rbda_nhieu_buoi`, `verify_stability_tuan`, `sinh_stb_theo_buoi`, `_seed_cua_buoi`, `dau_van_tay_du_lieu`, `run_full_pipeline`, khối giải của `api.py` (bước 4/6), `so_nhap.ma_buoi`.

## 1. Bài toán

- **Gói** = một CLB chiếm một **tập ngày cố định**, vào là đi đủ mọi ngày đó (ví dụ `3A` = `thu_2` + `thu_4` + `thu_5`).
- **Cấp độ** do trường chỉ định cho từng em: là **điều kiện tham gia** (em cấp 3A chỉ được xét vào gói 3A), **không** phải tiêu chí ưu tiên.
- Mỗi em **tối đa một gói**. Ngày gói không chiếm thì em vẫn chọn CLB ngày như hiện nay.
- **Cam kết cả năm**: em đã vào gói ở kỳ trước giữ chỗ; kỳ sau chỉ **trừ vào chỉ tiêu** gói, không xếp lại.
- Vì sao khó: gói tạo **tính bổ trợ** giữa các ngày, phá điều kiện "các buổi độc lập" (`KE_HOACH_NHIEU_BUOI.md` §2). Với bổ trợ, ma trận ổn định toàn tuần có thể không tồn tại; `verify_stability_tuan` (docstring: "không ràng buộc nào nối hai buổi") không còn đúng khi có gói.

## 2. Thiết kế: bộ điều phối hai pha đặt TRÊN pipeline hiện có

Không sửa `run_rbda`, `compute_club_priority`, `club_choice_function`, `verify_stability`, `generate_stb_lottery`. Thêm **một hàm điều phối** (đề xuất tên `run_rbda_co_goi`, tệp mới `goi_nhieu_buoi.py` để không chạm tệp lõi), cùng chữ ký với `run_rbda_nhieu_buoi` cộng hai tham số `goi` và `cam_ket`.

**Bước 0 — tách.** `clubs` chia hai phần: CLB gói (có `goi_buoi` khác rỗng; `buoi` = nhãn dành riêng `goi`) và CLB ngày (còn lại). Không có CLB gói và không có cam kết ⇒ **trả về đúng lời gọi `run_rbda_nhieu_buoi(...)` với đúng các tham số cũ** (nhánh ngắn mạch, xem §3.4).

**Bước 1 — cam kết cả năm.** Với mỗi em trong danh sách cam kết của gói `G`: ghi sẵn `G` cho em; `capacity(G) -= số em cam kết`, `reserve_capacity(G) = min(reserve_capacity, capacity mới)`; bỏ mọi nguyện vọng gói của em đó (em không tham gia pha 1). Chỉ đổi **chỉ tiêu và tập người tham gia**, không đổi thứ tự ưu tiên của ai.

**Bước 2 — lọc điều kiện tham gia.** `prefs_goi[sid] = [g for g in prefs[sid] if g thuộc gói và sid được phép vào g]`. Nguyện vọng gói không hợp lệ bị bỏ **và báo cảnh báo ở bước kiểm dữ liệu** (mã lỗi mới trong `i18n_errors.py`). Lọc nằm ở dữ liệu vào, không nằm trong hàm ưu tiên.

**Pha 1 — DA trên các gói, coi như một buổi giả `goi`.** Gọi `run_rbda(students, clubs_goi, scores_goi, app_goi, prefs_goi, stb_goi, reserve_fn, ...)`, cùng `tier_rank`, `bo_qua_du_tru`, `diem_wharton`. Gói có thi dùng Tầng 1 (−điểm rồi STB), gói không thi dùng Tầng 2 — đúng luật hiện hành. "Tối đa một gói" tự đúng: DA cho mỗi em tối đa một chỗ mỗi buổi.

**Pha 2 — từng ngày như hiện nay.** Với em được gói `G` (pha 1 hoặc cam kết): mọi ngày `d ∈ goi_buoi(G)` bị **khoá** — nguyện vọng ngày `d` của em bị làm rỗng. Em có danh sách rỗng không bao giờ đề nghị, nên tương đương vắng mặt ở ngày đó. Rồi gọi nguyên `run_rbda_nhieu_buoi(students, clubs_ngay, ..., prefs_da_khoa, stb_lottery, ...)`.

**Ghép.** `KetQuaTuan` cũ + `per_buoi["goi"]` (kết quả pha 1) + ngày bị khoá ghi là "thuộc gói G" chứ không ghi `None`.

**Vì sao gói trước, ngày sau.** Gói cần **mọi** ngày của nó còn trống; xếp ngày trước thì em nào có một CLB vào thứ Hai là mất quyền vào gói 3A, tức kết cục buổi khác quyết định ai được xét gói.

### 2.1. Phương án đã cân nhắc và loại

| Phương án | Cách làm | Vì sao loại |
|---|---|---|
| **(a) Gói = CLB của ngày đầu, ghế liên kết** | `3A` nằm trong buổi `thu_2`; em được `3A` thì khoá `thu_4`, `thu_5` ở các lượt sau | Xử lý ngày theo thứ tự và kết cục ngày trước đổi dữ liệu ngày sau: đúng loại phụ thuộc đã bị dán nhãn "bẫy" ở `stb_co_bu` (`KE_HOACH_NHIEU_BUOI.md` §5.3). Phá bất biến của `chi_buoi` (chạy riêng thứ Năm ≠ thứ Năm của lần chạy cả tuần). Gói chỉ cạnh tranh với CLB thứ Hai, không với CLB thứ Tư, thứ Năm mà nó cũng chiếm. |
| **(b) Một thị trường tuần, cầu nhiều đơn vị (A8)** | Em khai thứ tự trên **thời khoá biểu** cả tuần; một thuật toán chung | Có bổ trợ thì hàm lựa chọn không còn thay thế được: ổn định có thể **không tồn tại**; phải viết lại `verify_stability`; cách khai nguyện vọng đổi hẳn. Cỡ XL (sổ, A8). Để dành cho A8. |
| **(c) Trường tự gán gói, phần mềm chỉ trừ chỉ tiêu** | Mọi em gói coi như "cam kết" (bước 1), bỏ pha 1 | Không loại, **giữ làm V0 dự phòng**: là tập con của thiết kế chính (pha 1 rỗng). Đủ nếu tiếng Nhật không bao giờ quá tải (câu hỏi Q3 ở §6). |

## 3. Bảo đảm

### 3.1. Nhãn bắt buộc (bất biến 8)

Không có hàm lựa chọn mới: hai pha dùng nguyên `club_choice_function`, nên **trong từng pha** các bảo đảm cũ còn nguyên (ổn định, tối ưu cho học sinh, khai thật có lợi nhất — với các thứ khác của pha cố định). Nhưng cơ chế ghép hai pha **không** là một DA trên cả tuần. Báo cáo, `run_history` và giao diện phải mang đúng chữ:

> **bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói**

Theo tinh thần A12 (chế độ đo lường): kiểm cặp phá vỡ **trong từng pha** vẫn là chốt chặn (có cặp ⇒ rollback như nay); cặp phá vỡ **toàn tuần** chỉ được **đếm và ghi**, không chặn. Không cần chờ A12: chỉ thêm một chỉ số, không nới chốt nào.

### 3.2. Phản ví dụ: cặp phá vỡ toàn tuần

Hai em `s1`, `s2`; Tầng 2, STB: `s1` trước `s2`. Gói `G` = thứ Hai + thứ Tư, chỉ tiêu 1. CLB ngày `X` (thứ Hai, chỉ tiêu 1). Không CLB nào khác.
- Khai: `s1`: gói `[G]`, thứ Hai `[X]`. `s2`: gói `[G]`, thứ Hai `[X]`.
- Sở thích thật theo tuần của `s1`: `{X}` (thứ Tư trống) tốt hơn `{G}`; nhưng phiếu không có câu nào so gói với CLB ngày, nên `s1` khai `G` là "chấp nhận được".
- Pha 1: `s1` được `G` (STB cao hơn). Pha 2, thứ Hai: `s1` bị khoá, `X` về `s2`.
- Cặp `(s1, X)`: `s1` thích `X` hơn gói đang có; `X` xếp `s1` trên `s2`. **Phá vỡ ở mức tuần**, dù pha 1 và pha 2 đều 0 cặp.
- Cũng là phản ví dụ cho **khai thật**: `s1` không khai gói thì được `X`, tốt hơn.

Hệ quả cho chỉ số đo: phần mềm **không biết** sở thích tuần, nên chỉ đếm được **cặp phá vỡ tiềm năng**: (em có gói `G`, ngày `d ∈ goi_buoi(G)`, CLB `c` của ngày `d` có trong nguyện vọng ngày `d` của em, `c` đang giữ một em có ưu tiên thấp hơn hoặc còn ghế). Đây là **cận trên**; gọi đúng tên "tiềm năng" trong báo cáo.

### 3.3. Phụ thuộc giữa hai pha

- Khai ở pha 2 không ảnh hưởng pha 1. Trong pha 2, với kết quả pha 1 cố định, khai thật vẫn có lợi nhất.
- Khai ở pha 1 ảnh hưởng pha 2 (của chính em và của người khác qua ngày bị khoá) — đó là kênh thao túng ở §3.2. Giảm nhẹ (ngoài phần mềm, câu Q6): phiếu nói rõ "vào gói là bỏ CLB ngày ở các ngày đó".

### 3.4. Không có gói ⇒ trùng khít từng byte (bất biến 1)

- Bộ điều phối kiểm "có CLB gói" và "có cam kết" **trước mọi việc khác**; không có thì trả về **đúng một lời gọi** `run_rbda_nhieu_buoi` với đúng các đối số nó nhận — là hàm đồng nhất theo cấu trúc, không phải "gần giống".
- Dữ liệu cũ không có cột/tệp gói ⇒ không CLB nào có `goi_buoi` ⇒ nhánh trên.
- `dau_van_tay_du_lieu`: phần gói **chỉ được thêm khi có dữ liệu gói** (như cách đã làm với `wharton_bids`), nên dấu vân tay của CSDL cũ giữ nguyên từng byte. Thêm khoá `goi_buoi: None` vào mọi dict `clubs` cũng phải tránh, hoặc chứng minh không đi vào bất kỳ hàm băm/ghi nào.
- Kiểm: 3 bộ dữ liệu × 20 seed, so mọi dòng `match_results` qua đường `api.run_pipeline` (§5, GOI-2 T1).

### 3.5. Chống nội sinh (bất biến 2)

`compute_club_priority` không nhận thêm gì. Ba thứ mới đều nằm **ngoài** thứ tự ưu tiên: (1) cam kết cả năm chỉ trừ chỉ tiêu và loại em khỏi tập tham gia; (2) cấp độ chỉ lọc nguyện vọng ở dữ liệu vào; (3) khoá ngày chỉ làm rỗng nguyện vọng. Không thứ tự ưu tiên nào ở ngày `d` đọc kết cục pha 1 hay thứ hạng nguyện vọng. Lưu ý trung thực: **tập người tham gia** ngày `d` phụ thuộc kết cục pha 1 — đó là ràng buộc khả thi (em không thể ở hai nơi), không phải ưu tiên; phải ghi rõ trong báo cáo.

### 3.6. Bốc thăm (bất biến 3)

- **Một** bộ số đã khoá `stb_goc` cho cả hai pha. Pha 2 dùng nguyên `sinh_stb_theo_buoi` như nay, **chỉ với danh sách buổi ngày** (không có `goi`), nên số mỗi ngày không đổi khi thêm gói — kể cả trường một buổi (không rơi khỏi nhánh ngắn mạch `len(ds_buoi) <= 1`).
- Pha 1 dùng hoán vị vị trí của `stb_goc` theo đúng công thức `stb_ngay`, seed `_seed_cua_buoi(seed, "goi")` (crc32, không `hash()`). Không bốc nguồn ngẫu nhiên mới.
- Em đến muộn: `chen_stb_cho_hoc_sinh_moi` như nay; thứ tự tương đối của em cũ giữ nguyên ở cả hai pha.
- `chi_buoi`: chạy riêng một ngày vẫn **phải chạy đủ pha 1** trước (khoá ngày phụ thuộc pha 1), để "chạy riêng thứ Năm = thứ Năm của lần chạy cả tuần" còn đúng.

### 3.7. Thứ tự pipeline (bất biến 5) và `run_history` (bất biến 4)

Bộ điều phối nằm trọn trong bước "giải"; chốt sanity/verify chạy cho `goi` và cho từng ngày; ghi một giao dịch. `run_history` thêm dòng như mọi lần, kèm số liệu pha 1 và số cặp tiềm năng toàn tuần.

## 4. Dữ liệu

| Chỗ | Đề xuất (tương thích ngược) | Thiếu thì sao |
|---|---|---|
| Sổ nhập, sheet `1. CLB` | Cột `Buổi` nhận giá trị **`Gói`**; thêm cột tuỳ chọn **`Ngày của gói`** (ví dụ "Thứ 2, Thứ 4, Thứ 5", chuẩn hoá bằng `ma_buoi` từng phần) | Không có cột ⇒ không có gói |
| Sổ nhập, sheet mới `Gói` (tuỳ chọn) | `Mã HS · Mã CLB gói · Cam kết cả năm (có/không)`: mỗi dòng là một gói em **được phép** vào; "có" = cam kết từ kỳ trước | Không có sheet ⇒ gói mở cho mọi em, không cam kết |
| Nguyện vọng gói | Theo đúng mẫu cột đã có `<buoi>_pref_k` với buổi `goi`: **`goi_pref_1`, `goi_pref_2`…** (dạng dài: `buoi = goi`) | — |
| CSV `01` (clubs) | Cột tuỳ chọn mới **`goi_buoi`** (`thu_2+thu_4+thu_5`) | Tệp cũ đọc như cũ |
| CSV mới `04_goi.csv` (tuỳ chọn) | `student_id, club_id, cam_ket` | Không có tệp ⇒ không điều kiện, không cam kết |
| SQLite | `clubs.goi_buoi TEXT NULL`; bảng mới `goi_dieu_kien(student_id, club_id, cam_ket, PRIMARY KEY(student_id, club_id))`; qua `di_tru_schema` (idempotent, sao lưu trước) | NULL / bảng rỗng ⇒ nhánh trùng khít |
| `match_results` | Một dòng `(sid, 'goi', G)`; **không** ghi dòng `NULL` cho ngày bị khoá. `export_theo_lop` và tệp xuất **mở rộng** `G` ra các ngày của gói | Khoá chính `(student_id, buoi)` không đổi |

- **Hợp đồng CSV có đổi** (thêm một cột tuỳ chọn và một tệp tuỳ chọn; ba tệp cũ đọc y như cũ). Theo quy tắc 7 và bất biến 7: **Truong quyết** (D2). Phương án thay thế không đổi hợp đồng: ghi ngày ngay trong ô `buoi` ("goi:thu_2+thu_4+thu_5") — bị loại vì bản phần mềm cũ sẽ đọc nó như một buổi lạ **mà không báo lỗi**.
- Nhãn `goi` trở thành **nhãn dành riêng**: trường có buổi tên "goi" ⇒ lỗi kiểm dữ liệu.
- Kiểm dữ liệu mới (mỗi cái một mã lỗi): ngày của gói không phải buổi có thật; gói không có ngày; em cam kết vào gói không có dòng điều kiện; số em cam kết > chỉ tiêu; em có hai dòng cam kết; nguyện vọng gói bị bỏ vì không đủ điều kiện (cảnh báo, không chặn).
- Phía Microsoft (T4M): kho List thêm một dòng mỗi em cho "ngày" `goi` (mô hình rộng: `NV1..NV3` là gói); cấp độ lấy từ nguồn ở NC-07 (HỎI-IT). Màn gói chỉ hiện gói đúng cấp (NC-06, TH).

## 5. Mã mục đề xuất (chờ Truong duyệt — quy tắc 1)

Gói là trường hợp riêng của **A8** (ràng buộc xuyên buổi). Đề xuất ba mục con, làm tuần tự, mỗi mục **test trước**. Cỡ là **ước lượng**.

| Mã | Nội dung | Tệp | Cỡ (ước lượng) |
|---|---|---|---|
| **A8-GOI-1** Dữ liệu | Cột/sheet/tệp ở §4; `di_tru_schema`; đọc/ghi Sổ nhập; mã lỗi kiểm dữ liệu; `tao_i18n_js.py` | `so_nhap.py`, `api_nhap.py`, `rbda_priority_pipeline.py` (schema, `load_from_sqlite`, `dau_van_tay_du_lieu`), `i18n_errors.py` | M, ~250 dòng mã + ~200 dòng test |
| **A8-GOI-2** Bộ điều phối | `run_rbda_co_goi`, khoá ngày, STB pha 1, chỉ số cặp tiềm năng toàn tuần | `goi_nhieu_buoi.py` (mới) | M, ~150 dòng + ~300 dòng test |
| **A8-GOI-3** Nối vào kiosk | Bước giải của `_run_pipeline_da_khoa` gọi bộ điều phối; verify theo pha; ghi `match_results`/`run_history`; nhãn §3.1 trên giao diện và báo cáo; `export_theo_lop` mở rộng gói | `api.py`, `api_xuat.py`, `js/` (nhãn) | M–L, ~200 dòng + ~200 dòng test |

**Kiểm nhận (`kiem_nhan`), viết test đỏ trước:**
- GOI-1 T1: CSDL và Sổ nhập cũ (không gói) nhập ra dữ liệu và dấu vân tay **y hệt** trước. T2: `di_tru_schema` chạy hai lần không đổi gì, có tệp sao lưu. T3: mỗi lỗi kiểm dữ liệu ở §4 có một test và một mã lỗi. T4: buổi tên `goi` bị từ chối.
- GOI-2 T1: không gói ⇒ `run_rbda_co_goi` cho `KetQuaTuan` trùng `run_rbda_nhieu_buoi` trên 3 bộ × 20 seed. T2: không em nào có hai gói; không em nào có CLB ngày ở ngày của gói mình. T3: `verify_stability` = 0 cặp ở pha 1 và ở mỗi ngày pha 2. T4: em không đủ điều kiện không bao giờ vào gói đó (kể cả còn ghế). T5: phản ví dụ §3.2 dựng thành dữ liệu cho đúng **1** cặp tiềm năng, lần chạy **không** bị rollback. T6: thêm gói không đổi `stb_theo_buoi` của bất kỳ ngày nào (trường 1 buổi và 5 buổi). T7: `chi_buoi=["thu_5"]` cho thứ Năm trùng lần chạy cả tuần khi có gói. T8: cam kết: chỉ tiêu giảm đúng số em cam kết; em cam kết giữ gói; đổi dữ liệu kỳ trước (ngoài danh sách cam kết) không đổi kết quả. T9: test canh hiện có về chữ ký `compute_club_priority` và `api.run_pipeline` vẫn đạt.
- GOI-3 T1: đường `api.run_pipeline` không gói trùng từng dòng `match_results` (3 bộ × 20 seed). T2: có gói ⇒ `run_history` thêm đúng một dòng có nhãn §3.1 nguyên chữ và số cặp tiềm năng. T3: lỗi ở pha 1 ⇒ rollback toàn bộ, không dòng nào được ghi. T4: `export_theo_lop` hiện gói ở đủ các ngày của nó.

**Rủi ro.** (1) Dấu vân tay đổi ngầm nếu khoá mới lọt vào dict/hàm băm (§3.4). (2) Nhãn `goi` trùng tên buổi của trường. (3) Mọi chỗ đang lặp `match_results` theo ngày (thống kê, "chưa được xếp", thay đổi so với lần trước `get_thay_doi_ket_qua`) phải hiểu dòng `goi` và ngày bị khoá — dễ sót; cần grep `match_results` trước khi làm GOI-3. (4) G3 (bảo vệ người đã công bố): chạy lại pha 1 có thể đổi gói của em chưa cam kết; trường phải biết điều này trước khi công bố.

## 6. Câu hỏi cho giáo viên ECA (thêm vào `T4M_PHIEU_PHONG_VAN.md` khi Truong duyệt)

1. Có những cấp nào, mỗi cấp học ngày nào? Hai cấp có chung ngày không?
2. Chỉ tiêu mỗi cấp là bao nhiêu? Ai quyết? Có cấp nào nhận thêm ở giữa năm?
3. Tiếng Nhật có bao giờ **quá tải** (nhiều em đăng ký hơn chỉ tiêu cấp)? Nếu không bao giờ, phương án (c) là đủ.
4. Cấp của em lưu ở đâu, ai gán em mới học? (NC-07)
5. "Cam kết cả năm" nghĩa chính xác: kỳ 2 có được rút không; rút thì ghế có mở lại không?
6. Phiếu có thể thêm một câu "vào gói là bỏ CLB các ngày đó" không? Có thể hỏi em xếp gói so với CLB ngày không (giảm cặp ở §3.2)?
7. Gói có bài thi đầu vào (Tầng 1) không, hay chỉ xét cấp?
8. Ngoài tiếng Nhật còn hoạt động nào nhiều buổi (đội tuyển, nhạc cụ)? Mỗi cơ sở có gói riêng không?

## 7. Quyết định Truong cần duyệt

- **D1.** Bộ điều phối hai pha (gói trước, ngày sau) và nhãn §3.1; phương án (c) làm V0 dự phòng.
- **D2.** Đổi hợp đồng CSV: cột tuỳ chọn `goi_buoi` + tệp tuỳ chọn `04_goi.csv` + nhãn dành riêng `goi` (quy tắc 7).
- **D3.** Đổi schema: `clubs.goi_buoi`, bảng `goi_dieu_kien`; `match_results` ghi dòng `goi`, không ghi `NULL` ngày bị khoá.
- **D4.** Mã mục: A8-GOI-1..3 (hay mã khác), thứ tự 1 → 2 → 3; chỉ làm sau khi có câu trả lời Q1–Q3 ở §6.
- **D5.** Pha 1 bốc thăm bằng hoán vị riêng của buổi `goi` (đề xuất) hay dùng thẳng `stb_goc`.
