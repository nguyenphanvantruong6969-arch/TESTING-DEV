# Mẫu Microsoft Forms — Đăng ký CLB và thi tuyển theo buổi

Một biểu mẫu duy nhất đi hết bốn việc: học sinh **xếp nguyện vọng CLB theo
từng buổi** (Thứ Hai → Thứ Sáu), **chọn CLB muốn thi**, **làm luôn đề thi**
của CLB vừa chọn, và bài được **chấm tự động**. Tệp Excel Forms xuất ra đi
qua bộ chuyển đổi để thành **Sổ nhập CLB** (`SO_NHAP_CLB.xlsx`) — đúng một tệp
phần mềm nạp được — kèm bảng điểm.

## Luồng học sinh đi qua

```
Thông tin (mã HS, họ tên)
│
├─ Thứ Hai · Nguyện vọng ── Ranking: kéo thả CLB của Thứ Hai (bận thì bỏ qua)
│   ├─ Dự thi CLB Cờ vua?  ── Có ──► Đề thi Cờ vua (5 câu) ─┐
│   │                        Không ─────────────────────────┤
│   ├─ Dự thi CLB Văn học? ◄─────────────────────────────────┘
│   │                        Có ──► Đề thi Văn học ─┐
│   │                        Không ─────────────────┤
├─ Thứ Ba · Nguyện vọng ◄───────────────────────────┘
│   └─ …  (lặp lại cho Thứ Ba, Thứ Tư, Thứ Năm, Thứ Sáu)
└─ Nộp
```

Mỗi buổi có 3 CLB, trong đó 2 CLB tổ chức thi và 1 CLB không thi. CLB không
thi chỉ xuất hiện trong câu nguyện vọng. Tổng cộng: **26 phần, 67 câu hỏi**,
10 đề thi, mỗi đề 5 câu × 2 điểm = **thang 10**.

## Các tệp

| Tệp | Dùng để |
|---|---|
| `de_thi.json` | **Nguồn duy nhất**: buổi, CLB, chỉ tiêu, đề thi, đáp án. Sửa ở đây |
| `NHAP_FORMS_THI_CLB.docx` | Đem **Quick Import** vào Forms để dựng sẵn toàn bộ câu hỏi |
| `CAI_DAT_FORMS.md` | Những gì Quick Import không mang theo: Ranking, rẽ nhánh, đáp án, cài đặt |
| `MAU_XUAT_TU_FORMS.xlsx` | Tệp Forms xuất ra, dựng giả 60 học sinh — để chạy thử trước |
| `chuyen_forms_sang_phan_mem.py` | Excel của Forms → Sổ nhập CLB (`SO_NHAP_CLB.xlsx`) + `BANG_DIEM.xlsx` |
| `tao_mau_forms.py` | Sinh lại `.docx`, `CAI_DAT_FORMS.md`, `MAU_XUAT_TU_FORMS.xlsx` từ `de_thi.json`; hàm `ghi_mau_xuat_chi_thi` dựng tệp Forms chỉ-thi giả cho demo (mục 0b) |
| `MO_PHONG_FORMS.html` | Bản mô phỏng tương tác: mở bằng trình duyệt để thử luồng rẽ nhánh, chấm điểm và xuất tệp trước khi dựng trên Forms |
| `bieu_mau.py` | Phần dùng chung: tên câu hỏi, bố cục, chấm bài |

## 0. Chế độ "chỉ thi" (T4M-Q1..Q3): nguyện vọng ở ứng dụng đăng ký, Forms chỉ có bài thi

Dùng khi nguyện vọng đã nằm ở nơi khác (ví dụ ứng dụng Power Apps + SharePoint List của trường). Biểu mẫu
**không có câu Ranking và không có ô gõ mã HS**; khoá là cột **Email** Forms tự ghi (bật *Record name* và
*Only people in my organization*), đổi về chữ thường rồi ghép với tệp CSV xuất từ List (mô hình rộng:
cột `Email`, `Thu`, `NV1..NVn`, tuỳ chọn `HoTen`; mã CLB trong List phải là `club_id` của `de_thi.json`).

```bash
python mau_forms_thi_clb/tao_mau_forms.py --chi-thi            # CAI_DAT_FORMS_CHI_THI.md + NHAP_FORMS_CHI_THI.docx
python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --chi-thi --lists DANH_SACH.csv --ra ./nap
```

Vượt 200 câu thì sinh `NHAP_FORMS_CHI_THI_1.docx`, `_2.docx`… (tách theo buổi) và truyền nhiều tệp `.xlsx`
cho bộ chuyển đổi. Sinh lại từ `de_thi.json` không đổi cho ra tệp giống hệt từng byte. Phiếu trùng giữ phiếu
đầu; email lạ bị báo và bỏ; thi CLB không có trong nguyện vọng thì bỏ điểm và báo; không có bài thi nào thì
Sổ nhập chỉ có nguyện vọng, không điểm. Ghi chú một trang cho giáo viên: `GHI_CHU_GIAO_VIEN.md`.
Chế độ mặc định (mục 1 trở xuống) không đổi.

## 0b. Chạy thử trọn chuỗi (T4M-DEMO): một lệnh, ngoại tuyến, để cho giáo viên ECA xem

```bash
python du_lieu_test/demo_t4m.py --ra ./demo_ra            # mặc định 120 học sinh giả
python du_lieu_test/demo_t4m.py --ra ./demo_ra --so-hs 200 --seed 7 --he-so-cho 1
```

Lệnh chạy lần lượt: sinh tệp Lists giả (mã CLB lấy từ `de_thi.json`) → sinh tệp Forms chỉ-thi giả
(Email, câu hỏi, cột Points) → bộ chuyển đổi `--chi-thi` → nạp `SO_NHAP_CLB.xlsx` vào một CSDL **tạm**
và chạy pipeline như phần mềm thật → xuất Excel theo lớp → in tóm tắt. Không đụng `app.db` của workspace nào;
cùng `--seed` cho cùng kết quả. Mọi con số là **dữ liệu mô phỏng**, không phải khảo sát thật.

Chỉ tiêu mẫu trong `de_thi.json` (~42 chỗ mỗi buổi) chỉ đủ cho khoảng 50 em, nên mặc định demo nhân chỉ tiêu
lên cho vừa số em (dòng đầu của tóm tắt nói rõ hệ số; `--he-so-cho 1` giữ nguyên). Tệp `de_thi.json` không đổi.

Ra trong `--ra`: `lists_gia.csv`, `forms_chi_thi_gia.xlsx`, `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx`,
`ket_qua_theo_lop/` (mỗi lớp một tệp Excel).

**Nên cho giáo viên xem:**
1. `lists_gia.csv` và `forms_chi_thi_gia.xlsx`: hai tệp giáo viên sẽ nhận từ SharePoint List và Forms (cột `Email`
   nối hai nơi; email viết hoa lẫn thường vẫn ghép đúng).
2. Phần **cảnh báo** trong tóm tắt (và sheet "Cảnh báo" của `BANG_DIEM.xlsx`): ba loại gài sẵn là phiếu nộp lần
   hai (giữ phiếu đầu), email không có trong List (bỏ phiếu), và bài thi của CLB mà em không xếp nguyện vọng.
3. `BANG_DIEM.xlsx`: điểm chấm lại từ đáp án gốc, kèm chi tiết đúng/sai từng câu.
4. Một tệp trong `ket_qua_theo_lop/`: bản gửi giáo viên chủ nhiệm (không điểm, không số bốc thăm).
5. Dòng tóm tắt: bao nhiêu lượt (em × buổi) vào nguyện vọng 1 và bao nhiêu CLB thuộc Tầng 1 (có thi tuyển).

Bộ chuyển đổi chưa chép cột lớp sang Sổ nhập, nên demo gán lớp từ `lists_gia.csv` bằng `set_student_class`.

## 1. Dựng biểu mẫu (khoảng 30–40 phút)

1. Mở **forms.office.com** bằng tài khoản trường → **Quick import** → chọn
   `NHAP_FORMS_THI_CLB.docx` → chọn dạng **Quiz**. Lỡ nhập thành Form
   thường vẫn dùng được: bộ chuyển đổi tự chấm, chỉ mất phần Forms chấm sẵn
   và bỏ qua được bước 5.
2. **Soát từng câu** sau khi nhập. Microsoft ghi rõ bản tiếng Anh chuyển đổi
   chính xác hơn; lỗi hay gặp là một câu trắc nghiệm biến thành ô văn bản.
   Kiểm cả việc các **phần (section)** đã tách đúng như bảng mục 1 của
   `CAI_DAT_FORMS.md` — thiếu phần nào thì thêm tay (**+ Add new → Section**).
3. **Đổi 5 câu nguyện vọng sang Ranking** — `CAI_DAT_FORMS.md` mục 2.
4. **Đặt 10 chỗ rẽ nhánh** — `CAI_DAT_FORMS.md` mục 3. Chỉ đáp án *"Không"*
   của câu cổng cần đặt; mọi thứ khác Forms tự đi đúng thứ tự.
5. **Tick đáp án + điểm** cho 50 câu đề thi — `CAI_DAT_FORMS.md` mục 4.
6. **Settings** — `CAI_DAT_FORMS.md` mục 5. Hai mục không được bỏ qua:
   **One response per person = BẬT** và **Show results automatically = TẮT**.

> **Giữ nguyên phần `[mã]` ở đầu mỗi câu hỏi.** Forms lấy nguyên văn câu hỏi
> làm tên cột khi xuất Excel; bộ chuyển đổi chỉ đọc phần trong ngoặc vuông.
> Sửa lời câu hỏi thoải mái, nhưng xoá `[thu_2]` hay `[clb_covua-3]` là bộ
> chuyển đổi dừng và báo thiếu câu. Tương tự, lựa chọn trong câu Ranking phải
> giữ phần `(club_id)` ở cuối.

## 2. Soát thử trước khi phát cho học sinh

Tự điền **hai phiếu** — một phiếu thi một CLB, một phiếu chọn *"Không"* ở mọi
câu cổng — rồi làm đủ mục 3 bên dưới trên một cơ sở dữ liệu trống. Chuyển đổi
**không có cảnh báo** và nạp sạch thì mới phát.

Sai cột phát hiện sau khi 300 em đã nộp là 300 dòng sửa tay.

## 3. Sau khi thu: xuất Excel, chuyển đổi, nạp

1. Trong Forms: **Responses → Open in Excel** (hoặc *Download a copy*), lưu
   tệp `.xlsx` về máy.
2. Chạy bộ chuyển đổi:

   ```bash
   python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --ra ./nap
   ```

3. **Đọc hết phần cảnh báo** in ra (cũng có trong sheet *Cảnh báo* của
   `BANG_DIEM.xlsx`).
4. Kéo `SO_NHAP_CLB.xlsx` vào ô nạp ở thẻ **01 · Vận hành sắp xếp**, đối chiếu
   dòng tóm tắt, bấm **Nhập sổ**.

Chạy thử ngay với dữ liệu giả:

```bash
python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py mau_forms_thi_clb/MAU_XUAT_TU_FORMS.xlsx --ra ./nap_thu
```

### `BANG_DIEM.xlsx` có gì

| Sheet | Nội dung |
|---|---|
| **Bảng điểm** | Mỗi học sinh một dòng, mỗi CLB có thi một cột điểm |
| **Chi tiết** | Mỗi bài thi một dòng, đúng (Đ) / sai (S) từng câu, có nạp vào phần mềm hay không |
| **Thống kê đề** | Tỉ lệ làm đúng từng câu — câu nào gần 0% hay 100% là câu cần xem lại |
| **Cảnh báo** | Mọi ô bị bỏ, kèm dòng Excel và mã học sinh |

## 4. Bộ chuyển đổi chấm điểm thế nào

Điểm được **chấm lại** từ đáp án trong `de_thi.json`, không lấy điểm Forms.
Có cột *Points* của Forms (dạng Quiz) thì đem ra **đối chiếu**: lệch nhau
nghĩa là có câu trên Forms đã tick nhầm đáp án — cảnh báo nêu đích danh CLB,
và phải sửa trước khi dùng điểm để xét tuyển.

Chấm theo **nội dung** lựa chọn, không theo vị trí, nên bật *Shuffle options*
cho từng câu đề thi không ảnh hưởng gì.

| Tình huống | Bộ chuyển đổi làm gì |
|---|---|
| Tệp xuất thiếu một câu của mẫu | **Dừng, không ghi tệp nào**, liệt kê mã câu thiếu |
| Em làm bài thi CLB mà **không xếp** CLB đó ở nguyện vọng | Không nạp điểm đó vào phần mềm; vẫn giữ trong `BANG_DIEM.xlsx` |
| Nguyện vọng chứa CLB lạ hoặc CLB của buổi khác | Bỏ riêng ô đó |
| Một mã học sinh nộp hai lần | Giữ **phiếu đầu** — đây là bài thi, nộp lại không được thành làm lại |
| Phiếu không có mã học sinh | Bỏ cả phiếu |

## 5. Những điều cần biết trước

- **Ranking của Forms bắt xếp đủ mọi CLB trong câu.** Em đã chạm vào câu
  nguyện vọng Thứ Hai thì cả ba CLB Thứ Hai đều vào danh sách, theo thứ tự em
  kéo. Em không muốn vào CLB nào thì phải hiểu CLB đó sẽ đứng cuối, không phải
  bị loại. Nói rõ điều này với học sinh.
- **Rẽ nhánh của Forms chỉ đi tới, không quay lui.** Vì vậy mỗi CLB có thi
  phải có một câu cổng riêng; không thể làm kiểu "chọn nhiều CLB rồi lần lượt
  hiện từng đề".
- **Câu cổng là bắt buộc**, kể cả ở buổi em bận — em chọn *"Không"* rồi đi
  tiếp. Câu nguyện vọng thì **không** bắt buộc: bỏ trống = em bận buổi đó.
- **Điểm rất thấp sẽ bị phần mềm báo "điểm lạ".** Phần mềm cảnh báo điểm
  dưới 1/3 trung vị của CLB (chốt để bắt lỗi gõ lệch). Với đề 5 câu, một bài
  0–2 điểm là có thật, không phải gõ nhầm — đọc cảnh báo, đối chiếu sheet
  *Chi tiết*, rồi chạy tiếp.
- **Nhóm dự trữ (`reserve_group`) không thu qua biểu mẫu này** — nhà trường
  tự biết em nào thuộc nhóm chính sách. Muốn dùng suất dự trữ: khai
  `reserve_capacity`/`reserve_group` cho CLB trong `de_thi.json`, và điền cột
  `reserve_group` của học sinh vào `02_chon_CLB_muon_thi.csv` trước khi nạp.
  Ô trống thì phần mềm giữ nguyên nhóm đã có, không xoá.
- **Tổng điểm Forms hiện cho học sinh là tổng mọi đề em đã làm**, không phải
  điểm từng CLB. Điểm từng CLB nằm trong `BANG_DIEM.xlsx`.

## 6. Đổi đề, thêm CLB, đổi số buổi

Sửa `de_thi.json`, rồi:

```bash
pip install python-docx           # chỉ cần để ghi .docx (có trong requirements-dev.txt)
python mau_forms_thi_clb/tao_mau_forms.py
```

`de_thi.json` được soát trước khi sinh; sai thì báo **mọi** chỗ sai và không
ghi gì. Trần giống phần mềm: tối đa **10 CLB mỗi buổi** (trần câu Ranking) và
**5 CLB có thi mỗi buổi**. `dap_an` là số thứ tự lựa chọn đúng, **đếm từ 0**.
Trường sinh hoạt buổi khác (ví dụ chỉ `thu_2`, `thu_4`, `thu_6`): sửa danh
sách `buoi` — mã buổi phải trùng từng ký tự với cột `buoi` của phần mềm.

`tests/test_mau_forms_thi_clb.py` đỏ nếu sửa `de_thi.json` mà quên chạy lại
`tao_mau_forms.py`.

## Dữ liệu thật

`MAU_XUAT_TU_FORMS.xlsx` là tên bịa, máy sinh. Tệp Forms xuất ra của trường
là **dữ liệu thật của học sinh vị thành niên** — không đưa vào kho mã nguồn,
không gửi qua kênh công khai.
