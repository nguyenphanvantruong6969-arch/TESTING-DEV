---
name: tao-workspace-tu-raw
description: Dựng một workspace (không gian làm việc) của phần mềm phân bổ rbda-kiosk, NẠP SẴN dữ liệu, từ dữ liệu raw bất kỳ của khách — bảng Excel/CSV tự do, tệp xuất Google Forms / Microsoft Forms, hai tệp tách rời (danh sách chỗ xếp + danh sách người), hoặc văn bản dán vào chat — cho mọi ngành (công ty, ký túc xá, sự kiện, đề tài, trường học…). Đoán từ vựng (Nhân viên/Dự án/Ngày…) và luật xếp từ dữ liệu rồi hỏi người dùng duyệt, soát chặt, kiểm bằng phần mềm thật, và giao ra tệp .zip "nhập là chạy", Sổ nhập .xlsx và báo cáo soát. Dùng khi người dùng nói "tạo workspace từ dữ liệu", "dựng workspace cho khách", "chuyển file của công ty X thành workspace", "nạp dữ liệu raw vào workspace", "làm file zip workspace", "make a workspace from this data", hoặc đưa một bảng tính kèm yêu cầu tạo không gian làm việc.
---

# Dựng workspace nạp sẵn dữ liệu từ raw

> **Chỉ chạy trong kho mã rbda-kiosk** (script gọi `workspace.py`, `api.py`, `so_nhap.py` của chính
> phần mềm để dựng và kiểm). Lệnh: `python .claude/skills/tao-workspace-tu-raw/scripts/tao_workspace.py`.

Kết quả là ba tệp trong một thư mục **ngoài kho mã**:

| Tệp | Người dùng làm gì |
|---|---|
| `<slug>.zip` | Màn chọn workspace → **Nhập workspace** → mở → bấm chạy. Đã có cấu hình + dữ liệu. |
| `SO_NHAP_<SLUG>.xlsx` | Sổ nhập theo nhãn của workspace (sheet học sinh có hai hàng tiêu đề, dữ liệu từ hàng 3) — sửa tay rồi nạp lại vào **đúng** workspace đó. |
| `BAO_CAO_SOAT.md` | Số liệu, độ chọi từng buổi, giả định đã duyệt, cảnh báo đã cho qua. |

## Nguyên tắc — không thương lượng

1. **Đoán rồi hỏi, không tự quyết.** Mọi vai trò cột, nhãn, luật đều do bạn ĐỀ XUẤT và người dùng
   DUYỆT trước khi dựng. Ghi những gì đã duyệt vào `ghi_chu_gia_dinh` của spec (đi vào báo cáo).
2. **Chỉ tiêu (sức chứa) không bao giờ tự đặt.** Raw thiếu thì hỏi từng chỗ. Script báo
   `thieu_chi_tieu` nếu sót.
3. **Sai một điều là không ghi tệp nào.** Script soát hết rồi mới ghi. Không sửa raw giúp người
   dùng, không "đoán đại" tên chỗ gõ nhầm: script chỉ GỢI Ý ("Có phải: 'Website'?"); bạn hỏi người
   dùng, rồi họ sửa raw — hoặc, nếu họ xác nhận, bạn ghi ánh xạ tường minh vào spec.
4. **Raw là dữ liệu người thật.** Spec, CSV trung gian và đầu ra đặt trong **scratchpad hoặc thư
   mục người dùng chỉ định, ngoài kho git** — script từ chối ghi vào trong một kho git. Không bao giờ
   commit chúng. Không chép tên người thật vào kho mã hay vào tin nhắn commit.
5. **Kiểm bằng phần mềm thật.** Script nạp sổ vào workspace mới, đọc báo cáo sức khoẻ dữ liệu, chạy
   phân bổ thử trên bản sao. Cảnh báo nào cũng chặn, trừ `health_oversubscribed` /
   `health_oversubscribed_buoi` (ít chỗ hơn người — sự thật về độ chọi, ghi vào báo cáo). Cảnh báo
   khác chỉ cho qua khi **người dùng xác nhận đó là sự thật** → `--chap-nhan <mã>`.

## Quy trình

### 1. Gom raw

- Tệp: `.xlsx`, `.xlsm`, `.csv`, `.tsv`, `.txt` (mã hoá UTF-8, UTF-8 BOM, Windows-1258/1252 đều đọc;
  dấu tách `,` `;` tab `|` tự nhận). `.xls` cũ: nhờ người dùng mở Excel lưu lại `.xlsx`.
- **Văn bản dán vào chat**: tự dựng thành CSV trong scratchpad (một dòng tiêu đề, giữ nguyên chữ
  người dùng viết), cho người dùng xem lại bảng đó, rồi đi tiếp như một tệp.

### 2. Soi

```bash
python .claude/skills/tao-workspace-tu-raw/scripts/tao_workspace.py soi <tệp> [<tệp> ...]
```

In từng bảng (mỗi sheet / mỗi CSV): số dòng, từng cột với số ô, số giá trị khác nhau, mẫu, và gợi
ý vai trò (`ma`, `ten`, `nhom_uu_tien`, `buoi`, `chi_tieu`, `suat_uu_tien`, `diem`,
`nguyen_vong_thu_k`, `ma_tran`, `mot_o`, `thu_hang`, `lien_lac`…). Gợi ý chỉ là gợi ý. Đọc kỹ:

- Mã có giá trị lặp → hoặc phiếu nộp lại (Forms), hoặc dạng `dong_dai` (mỗi người nhiều dòng).
- Bảng có tiêu đề không ở dòng 1 (tiêu đề phụ, logo) → `"dong_tieu_de": n` trong `nguon`.
- Cột email / điện thoại / dấu thời gian: không đưa vào workspace.

### 3. Đề xuất và hỏi duyệt (dùng AskUserQuestion, gom 2–4 câu một lượt)

Đề xuất CỤ THỂ, kèm lý do ngắn, phương án khuyên đặt đầu. Những thứ phải chốt:

| Chốt | Gợi ý cách đoán |
|---|---|
| **Dạng nguyện vọng** | xem bảng "Bốn dạng" bên dưới |
| **Cột** mã, tên, nhóm, điểm | từ `soi` |
| **Từ vựng** 5 danh từ (vi + en) | từ ngành: công ty → Nhân viên/Dự án; KTX → Sinh viên/Phòng; sự kiện → Khách/Phiên; đề tài → Sinh viên/Đề tài. `session` là đơn vị THỜI GIAN mà mỗi người được tối đa một chỗ (Buổi/Ngày/Ca/Đợt). |
| **Buổi** | có cột buổi? Không có mà người dùng nói "mỗi người một chỗ" → một buổi (bỏ trống). Nên dùng nhãn thứ trong tuần (Thứ 2…Chủ nhật) — xem "Giới hạn". |
| **Chỉ tiêu** từng chỗ | raw không có → HỎI, không đoán |
| **Luật** | xem bảng "Luật" |
| **Nhóm ưu tiên** | giá trị thô → mã nhóm (`nhom_doi_ten`); nhóm nào được chỗ nào dành bao nhiêu suất |
| **Phiếu trùng** | giữ phiếu đầu hay cuối (`phieu_trung`) — chỉ khi người dùng xác nhận là phiếu nộp lại |
| **Tên workspace** | tên khách / đợt |

### 4. Viết spec (JSON, trong scratchpad) rồi dựng

```bash
python .claude/skills/tao-workspace-tu-raw/scripts/tao_workspace.py dung \
    --spec <scratchpad>/spec.json --ra <thư mục ngoài kho> [--chap-nhan ma1,ma2]
```

Đường dẫn `tep` trong spec tính từ thư mục chứa spec (hoặc đường dẫn tuyệt đối).

Lỗi → script in danh sách `✗ [mã] chi tiết (tệp, sheet, dòng)` và **không ghi gì**. Với mỗi lỗi:
spec sai thì sửa spec; raw sai thì báo người dùng đúng dòng, để họ sửa raw (hoặc xác nhận cách xử
lý), rồi chạy lại. Lặp tới khi sạch.

### 5. Giao

Gửi ba tệp (SendUserFile), tóm tắt: số người / chỗ / buổi, độ chọi từng buổi (từ báo cáo), giả định
đã dùng, cảnh báo đã cho qua, và cách dùng: **Nhập workspace → mở → chạy**. Nhắc: sổ nhập chỉ nạp
được vào workspace có đúng nhãn đó (sheet `1. <chỗ>` / `2. <người>`).

## Bốn dạng nguyện vọng (`nguoi.nguyen_vong.dang`)

| Dạng | Raw trông thế nào | Spec |
|---|---|---|
| `cot_xep_hang` | cột NV1, NV2… (hoặc "Lựa chọn 1", "Top 1"), ô = tên chỗ; có thể kèm cột điểm cạnh từng NV | `"cot": ["NV1","NV2"], "cot_diem": ["Điểm 1", null]` — liệt kê ĐỦ: cột NVk có dữ liệu mà bỏ sót là lỗi `cot_nv_bo_sot` |
| `mot_o` | một ô "A; B; C" (Forms checkbox/ranking xuất gộp). Thứ tự trong ô = thứ tự ưu tiên | `"cot": "Các phiên muốn dự", "tach": ";"` (bỏ `tach` = tự tách theo `;` xuống dòng `\|`, không có thì theo `,`) |
| `dong_dai` | mỗi dòng một lựa chọn: mã người, tên chỗ, thứ hạng[, điểm] | `"cot_cho": "Phòng mong muốn", "cot_hang": "Thứ tự", "cot_diem": null` (bỏ `cot_hang` = theo thứ tự dòng) |
| `ma_tran` | mỗi chỗ một cột, ô = hạng ("1", "Lựa chọn 2", "Hạng 3", "1st choice"). Lưới xếp hạng Google Forms: tiêu đề "Câu hỏi [Tên chỗ]" | `"tien_to": "Xếp hạng đề tài"` (tự nhận mọi cột "Xếp hạng đề tài [X]") hoặc `"cot": {"tiêu đề": "Tên chỗ"}` |

Điểm theo từng chỗ ở cột riêng (vd Forms có "Điểm [Website]"): `nguoi.diem_theo_cho: {"tiêu đề": "Tên chỗ"}`.
Điểm theo người (một số cho cả người, vd điểm rèn luyện): `nguoi.cot.diem` + `rules.score_scope = "per_person"`.

## Luật (`cau_hinh.rules`)

| Khoá | Giá trị | Khi nào |
|---|---|---|
| `max_choices` | 1–20 (mặc định 10) | trần nguyện vọng MỖI BUỔI; đặt ≥ số lựa chọn dài nhất trong raw (script chặn `qua_tran_nv`) |
| `max_tests` | 0–20 hoặc `null` (không giới hạn) | trần số chỗ có điểm mỗi buổi (per_slot). Không có điểm → 0 |
| `priority` | `score` · `tier` · `score+tier` | ai được trước khi tranh một chỗ: điểm (rồi bốc thăm) · nhóm cứng · nhóm rồi điểm |
| `tier_mode` | `reserve` · `strict` | nhóm chỉ hưởng SUẤT DÀNH RIÊNG ở chỗ khai suất (mặc định) · nhóm xếp CỨNG trước (thâm niên, năm cuối…) |
| `score_scope` | `per_slot` · `per_person` | điểm thi từng chỗ · một điểm cho cả người |
| `tiers` | danh sách mã nhóm, tốt nhất đầu tiên | chỉ khi xếp cứng (`strict` hoặc `priority` có `tier`) |

Luật nhóm: `reserve` → mọi nhóm của người phải có chỗ dành suất (không thì `nhom_mo_coi`);
`strict` → mọi nhóm phải nằm trong `tiers` (không thì `nhom_ngoai_tiers`).
`industry`: `school` · `company` · `event` · `custom`.

## Spec đầy đủ

```json
{
  "ten_workspace": "Công ty Bình Minh",
  "cau_hinh": {
    "industry": "company",
    "labels": {
      "person":  {"vi": "Nhân viên",      "en": "Employee"},
      "slot":    {"vi": "Dự án",          "en": "Project"},
      "session": {"vi": "Ngày",           "en": "Day"},
      "group":   {"vi": "Diện ưu tiên",   "en": "Priority group"},
      "score":   {"vi": "Điểm phỏng vấn", "en": "Interview score"}
    },
    "rules": {"max_choices": 5, "max_tests": 2, "priority": "score",
              "tier_mode": "reserve", "score_scope": "per_slot", "tiers": []}
  },
  "cho_xep": {
    "nguon": {"tep": "du_an.xlsx", "sheet": "Danh sách", "dong_tieu_de": 1},
    "cot": {"ten": "Tên dự án", "ma": null, "buoi": "Ngày", "chi_tieu": "Số người",
            "suat_uu_tien": null, "nhom_uu_tien": null},
    "chi_tieu": {"Đào tạo nội bộ": 8},
    "buoi": {"Đào tạo nội bộ": "Thứ 5"},
    "suat_uu_tien": {"Đào tạo nội bộ": [2, "tan_tuyen"]}
  },
  "nguoi": {
    "nguon": {"tep": "dang_ky.csv"},
    "cot": {"ma": "Mã NV", "ten": "Họ và tên", "nhom": "Diện", "diem": null},
    "nhom_doi_ten": {"Tân tuyển": "tan_tuyen"},
    "phieu_trung": null,
    "nguyen_vong": {"dang": "cot_xep_hang", "cot": ["NV1", "NV2", "NV3"],
                    "cot_diem": ["Điểm 1", "Điểm 2", null]},
    "diem_theo_cho": {}
  },
  "ghi_chu_gia_dinh": ["Cột 'Diện' = nhóm ưu tiên; chỉ 'Tân tuyển' được hưởng suất (người dùng duyệt 15/10)"]
}
```

- `cho_xep.nguon` **không bắt buộc**: thiếu thì danh sách chỗ = mọi tên gặp trong nguyện vọng cộng
  mọi chỗ khai trong `cho_xep.chi_tieu`; khi đó `chi_tieu` (và `buoi`, `suat_uu_tien` nếu cần) khai
  hết trong spec.
- Có cả ô raw lẫn spec cho cùng một chỗ: phải bằng nhau (`chi_tieu_mau_thuan`). `buoi` khai cho
  MỌI chỗ hoặc không chỗ nào. Mã chỗ trống → tự sinh từ tên (`so_nhap.tao_ma_clb`).
- Tên chỗ khớp **bỏ hoa/thường và khoảng trắng thừa** (đúng như phần mềm), GIỮ dấu và ngoặc:
  "Bóng đá (nam)" ≠ "Bóng đá (nữ)", "Toán" ≠ "Toan".
- `nguoi.nguyen_vong` có thể không có `nguon` riêng: nguyện vọng luôn đọc từ bảng `nguoi.nguon`.

## Mã lỗi hay gặp

| Mã | Nghĩa | Làm gì |
|---|---|---|
| `thieu_chi_tieu` | chỗ chưa có chỉ tiêu | hỏi người dùng; tên lạ kèm "Có phải…?" thường là gõ nhầm trong raw |
| `cho_khong_co` | nguyện vọng không khớp chỗ nào | hỏi: gõ nhầm (sửa raw) hay chỗ mới (thêm chỗ + chỉ tiêu) |
| `ma_trung` | mã lặp | phiếu nộp lại? → hỏi đầu/cuối → `phieu_trung`; trùng thật → người dùng sửa raw |
| `ma_khac_hoa` | `nv01` và `NV01` | phần mềm coi là hai người → người dùng sửa raw |
| `nv_trung`, `hang_trung`, `hang_sai` | một người chọn một chỗ hai lần / hai chỗ cùng hạng / hạng không đọc được | người dùng sửa raw |
| `ten_mau_thuan`, `nhom_mau_thuan`, `diem_mau_thuan` | dạng `dong_dai`: cùng mã mà các dòng ghi khác tên / nhóm / điểm | người dùng sửa raw |
| `qua_tran_nv`, `qua_tran_thi` | vượt trần mỗi buổi | nâng `max_choices`/`max_tests` (hỏi) hoặc sửa raw |
| `nhom_mo_coi`, `nhom_ngoai_tiers` | nhóm không có tác dụng | thêm suất / sửa `tiers` / `nhom_doi_ten` / bỏ cột nhóm — hỏi |
| `diem_khong_nv`, `diem_sai`, `diem_sai_che_do` | điểm không thuộc nguyện vọng / không phải số / sai `score_scope` | sửa raw hoặc spec |
| `cot_nv_bo_sot` | cột NVk có dữ liệu mà spec không dùng | thêm vào `cot`/`cot_diem` |
| `canh_bao_phan_mem` | phần mềm cảnh báo khi nạp / soát sức khoẻ | đọc câu báo; sửa, hoặc người dùng xác nhận → `--chap-nhan <mã>` |
| `ra_trong_kho_git`, `de_tep` | thư mục ra trong kho git / đã có tệp | chọn thư mục khác |

## Giới hạn hiện tại của phần mềm (nói trước với người dùng)

- **Nhãn buổi ngoài thứ trong tuần** ("Sáng", "Ca 1") được lưu nguyên dạng chữ thường (`sáng`) và
  sắp theo vần chữ cái trên màn hình (`chiều` trước `sáng`). Dùng "Thứ 2…Chủ nhật" khi có thể.
- Sổ nhập của workspace đổi tên sheet, cột nhóm, cột điểm theo nhãn, nhưng các cột khác vẫn là
  "Tên CLB", "Buổi", "Mã HS", và ô gộp "Nguyện vọng k" ở hàng 1 của sheet học sinh (hành vi của
  `so_nhap.py`). Workspace bật **điểm quyết tâm** thì mỗi nhóm có thêm cột "Điểm quyết tâm"; kỹ
  năng này không bắt buộc sinh điểm đó (trong mã gọi là `wharton`).
- Zip **chưa chạy** lần nào: số bốc thăm khoá ở lần chạy đầu của người dùng (đúng bất biến STB).

## Kiểm skill này

`tests/test_skill_tao_workspace.py` — bốn dạng nguyện vọng dựng ra zip nạp và chạy được; raw sai
thì không ghi tệp nào; từ chối ghi vào kho git; cp1258 tổ hợp đọc đúng.
