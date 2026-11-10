# Báo cáo soát mã: FA-DAA đêm 5 và hai bản sửa của soát đêm 5 (skill `soat-ma`, 2026-11-10)

Chỉ báo cáo, không sửa mã (luật 2 của skill). Bốn tầng làm liền một lượt theo yêu cầu của Truong (bước 3 của lượt giao
2026-11-10), không dừng chờ "tiếp" sau từng tầng. Dữ liệu thử là dữ liệu MÔ PHỎNG.

## Phạm vi
- Diff: `89e3e5c..HEAD` (FA-O1 fff8df5, FA-9b d9482a7, FA-P1 32cb8c8, FA-P2 399aafd), mã: 10 tệp, +246 / −19 dòng.
  Toàn nhánh so với `origin/main` là 85 tệp, +10.228 dòng: vượt ngưỡng 40 hàm của mục 2, và đêm 1–4 đã có bốn bản soát
  riêng (`docs/phien/bao_cao_dem/*_soat_dem*.md`), nên em thu về khoảng đêm 5. Soát toàn nhánh là việc của CI khi mở PR.
- Hàm cũ bị chạm, lần một bậc (17):
  - Tầng 1: không có (diff không chạm `rbda_priority_pipeline.py`, `fa_daa.py`, `fa_ly_do.py`, `api.py`); chỉ gọi `khoa_sap_buoi`.
  - Tầng 2: `_doc_ly_do_moi_nhat`, `get_ly_do_ket_qua`, `_export_ly_do_da_khoa`, `_export_bien_ban_da_khoa`, `_duong_xuat`,
    `duong_dan_khong_de`, `fa_bien_ban.tao_ban_ghi`, `fa_bien_ban.ghi_xlsx`, `_an_toan_cho_excel`, `so_excel.Trang.o`.
  - Tầng 3: `chayXuat`, `selectFallbackStudent`, `boChonHocSinhDuPhong`, `renderHuyChuongStep`, `hcTheoNguyenVong`,
    `hcCapNhatNhac`, `lamMoiBuoc3`.
- Mốc test: test liên quan 2.222 đạt / 1 bỏ qua (trước sửa); sau sửa: 157 test giao diện chạm thẻ Nhập tại chỗ và Kết quả
  đạt, 0 bỏ qua; `test_fa_bien_ban.py` + `test_giao_dien_fa_ket_qua.py` + `test_export_ket_qua.py` 48 đạt.
- `kiem_nhanh.py --co-so origin/main`: **7/7 ĐẠT** (trước và sau hai bản sửa).

## Tầng 1: lõi thuật toán
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 1.1 bất biến 2 | ĐẠT | Diff không chạm khoá ưu tiên; `test_fa_tinh_chat.py` (hoán vị nguyện vọng) nằm trong 2.222 đạt |
| 1.3 tắt tính năng → đường cũ | ĐẠT | `kiem_trung_khit` seed 1..20: 60/60 ca trùng khít với `origin/main` |
| 1.4, 1.5, 1.6 | không áp dụng | Không có hàm lựa chọn, bộ kiểm ổn định hay luật hoà mới |
| 1.7 bất biến 3 | ĐẠT | Không đổi số bốc thăm; biên bản chỉ ĐỌC `stb_number` |

Phát hiện: không có. Kết luận tầng: **Đạt**.

## Tầng 2: backend
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 2.1 bất biến 5 | không áp dụng | Đêm 5 không chạm pipeline ghi |
| 2.2 bất biến 4 | ĐẠT | `khong_sua_nhat_ky` ĐẠT |
| 2.3 bất biến 6 | ĐẠT (có ghi chú) | Lỗi xuất trả `{ok: false, errors: [{code, params}]}`; nhưng mã là `error_exporting_csv` cho tệp HTML/Excel (có từ FA-9) |
| 2.4 bất biến 7 | không áp dụng | Không đổi lược đồ hay cột CSV |
| 2.8 đường dẫn xuất | ĐẠT (có ghi chú) | Đường tương đối về Tải xuống, tuyệt đối đúng chỗ, không ghi đè; tên cặp HTML/Excel có thể lệch (FA-P5 của soát đêm 5) |
| 2.10 xuất khi chưa có kết quả | ĐẠT | `bien_ban_chua_boc_tham`, `fa_chua_co_ly_do` có test |

Phát hiện:
| # | Mức | Tệp | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| SM-1 | nên sửa | `fa_bien_ban.py` | `ghi_xlsx` | Không lọc ký tự openpyxl cấm (ký tự điều khiển), khác `so_excel.Trang.o` (gọi `lam_sach`). Lần xuất biên bản hỏng cả lượt, tệp HTML đã ghi thì nằm lại, lỗi báo "CSV". Trước FA-9b, bản HTML xuất được | Tên workspace `"Kỳ\x01một"` (cấu hình nhận) → `export_bien_ban_boc_tham` trả `error_exporting_csv` / `IllegalCharacterError`; thư mục còn `bb.html` | Cho chuỗi qua `so_excel.lam_sach` (hoặc ghi qua `Trang.o`) trong `ghi_xlsx` | đã tái hiện |

Mức "nên sửa" (thang của skill: sai ở trường hợp hiếm). Tương ứng mức **nhỏ** của thang soát đêm: tên kiểu này chỉ đến từ dán
chữ hay tệp .zip, lỗi hiện ra chứ không im lặng, và tệp HTML vẫn có.

Bốn khía cạnh: bảo mật: chèn công thức đã sửa (FA-P1), SQL vẫn tham số hoá; hiệu năng: `_doc_ly_do_moi_nhat` một truy vấn mỗi
buổi (không N+1 theo học sinh), sắp O(n log n); đúng đắn: SM-1; bảo trì: hai bộ dựng biên bản (HTML, Excel) dùng chung
`tao_ban_ghi`, tốt.

Điểm tốt: một bản ghi, hai bộ dựng (đúng spec §8); test API kiểm cùng mã băm ở cả hai tệp.

Kết luận tầng: **Đạt, 1 nên sửa**.

## Tầng 3: giao diện (Chromium thật qua `browser_host`)
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 3.1 `ok=false` | ĐẠT | `chayXuat` ghi dòng `xuat_kq_loi` với `trErrs`; mở khoá nút cả khi lỗi |
| 3.2 XSS | ĐẠT | Thông báo xuất đi qua `textContent`; diff không thêm `innerHTML` |
| 3.3 bấm đúp | ĐẠT | `khoa.dangXuat` chặn lần xuất thứ hai; nút lưu nguyện vọng qua `khiBan` |
| 3.4 kiosk không lộ em khác | ĐẠT | FA-P2: màn hình HS2 không bị vẽ lại bằng dữ liệu HS1 (test kiểm nhãn và danh sách xếp hạng của HS2) |
| 3.6 chữ tiếng Anh | ĐẠT | `xuat_kq_bien_ban` EN có `{path_xlsx}` và JS điền; `i18n_khoa` ĐẠT |

Phát hiện:
| # | Mức | Tệp | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| SM-2 | nhỏ | `tests/test_giao_dien_fa_n2_luu_mac_dinh.py` | `test_sang_em_khac_giua_luc_luu_van_luu_huy_chuong_em_truoc` | Chờ cứng `wait_for_timeout(800)` (cùng kiểu với hai test cũ của tệp, 500 ms) thay vì chờ điều kiện | Máy CI chậm có thể đọc CSDL trước khi `submit_huy_chuong` về | Chờ tới khi `#fbHuyChuongStep` của HS2 vẽ xong hoặc hỏi API trong vòng lặp có hạn | suy luận (5 lần liền đều đạt) |

Kết luận tầng: **Đạt, 1 nhỏ**.

## Tầng 4: vệ sinh, tài liệu, test
| Mục | Kết quả | Bằng chứng |
|---|---|---|
| 4.1 mã chết, `ruff` | ĐẠT | `ruff check .` sạch; không hàm mới không ai gọi |
| 4.2 i18n | ĐẠT | `chu_cam`, `i18n_khoa`, `ma_loi_js`, `i18n_loi_khop` ĐẠT |
| 4.3 tài liệu | ĐẠT | CHANGELOG và TIEN_DO có FA-O1, FA-9b, FA-P1, FA-P2; không thêm tệp test nên số tệp ở `CLAUDE_CHI_TIET.md` không đổi |
| 4.4 đột biến | ĐẠT | 7/7 bị bắt: FA-O1 bỏ khoá ngày; FA-9b ô SHA-256 sai, bỏ `path_xlsx` ở JS; FA-P1 bỏ dòng ép kiểu; FA-P2 trả lại điều kiện `sid !== currentFallbackStudent`, trả lại `conMo &&` ở nút. Hoàn tác, `git status` sạch sau mỗi lần |
| 4.4 chập chờn | ĐẠT | Hai ca FA-P2 chạy 5 lần liền: 10/10 đạt |
| 4.4 bỏ qua im lặng | ĐẠT | Chỉ 1 ca bỏ qua có lý do (V§13.12, D1 hoãn); CI có bước "Soat khong co test giao dien nao bi bo qua" |

Phát hiện:
| # | Mức | Tệp | Hàm | Vấn đề | Đường xảy ra | Đề xuất sửa | Chắc chắn? |
|---|---|---|---|---|---|---|---|
| SM-3 | nhỏ | `.claude/skills/soat-ma/scripts/kiem_nhanh.py` | `main` | `--so-seed N > 5` bị cắt im lặng về 5 (= FA-P7) | `--so-seed 20` in "15 ca (3 bộ × 5 seed)" | Sinh thêm seed khi N > 5, hoặc báo lỗi | đã tái hiện |

Kết luận tầng: **Đạt, 1 nhỏ**.

## Danh sách sửa đầy đủ (chưa sửa, chờ Truong)
| Việc | Nguồn | Trạng thái |
|---|---|---|
| SM-1 lọc ký tự cấm trong `ghi_xlsx` | tầng 2 | Đề xuất |
| SM-2 thay chờ cứng bằng chờ điều kiện | tầng 3 | Đề xuất |
| SM-3 / FA-P7 `--so-seed` | tầng 4 | Đề xuất |
| FA-P3..FA-P6 | soát đêm 5 | Đề xuất (nhỏ) |

Không còn mục nào mức trung trở lên (FA-P1, FA-P2 đã sửa và soát lại).
