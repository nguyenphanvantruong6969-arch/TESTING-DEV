"""SG-10 (M2): CLB Tự do (FA) không có giới hạn chỗ -> `get_club_fill_stats` đánh dấu `tu_do`, để màn kết quả
hiện số thành viên + "không giới hạn chỗ" thay vì "150%", và ô "Chỗ còn trống" bỏ CLB Tự do. Không FA: không đổi.

Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test.
"""

from _fa import bat_fa, dung_fa_clb, dung_hs_fa


def _dung_fa(api, so_hs=12):
    bat_fa(api)
    dung_fa_clb(api, G=(3, "GIOI_HAN"), T=(5, "TU_DO"))   # T lưu chỉ tiêu 5 nhưng sẽ có nhiều em hơn
    ids = [f"HS{i:03d}" for i in range(1, so_hs + 1)]
    dung_hs_fa(api, *ids, nv={i: ["T"] for i in ids})
    assert api.run_pipeline(seed=7)["ok"]


def _theo_ma(api):
    return {c["club_id"]: c for c in api.get_club_fill_stats()["data"]}


def test_clb_tu_do_co_co_tu_do_va_nhieu_hon_chi_tieu_luu(api):
    _dung_fa(api)
    t, g = _theo_ma(api)["T"], _theo_ma(api)["G"]
    assert t["tu_do"] is True
    assert t["matched"] == 12 and t["capacity"] == 5     # 240% nếu tính theo chỉ tiêu lưu: con số vô nghĩa
    assert g["tu_do"] is False


def test_tong_cho_trong_loai_clb_tu_do(api):
    _dung_fa(api)
    ds = api.get_club_fill_stats()["data"]
    gioi_han = [c for c in ds if not c["tu_do"]]
    assert [c["club_id"] for c in gioi_han] == ["G"]
    assert sum(max(0, c["capacity"] - c["matched"]) for c in gioi_han) <= 3


def test_khong_fa_khong_co_tu_do(api):
    api.create_or_update_club("clb_a", "CLB A", capacity=2)
    ds = api.get_club_fill_stats()["data"]
    assert ds and all(c["tu_do"] is False for c in ds)


def _dung_fa_hai_clb(api):
    """12 em: 6 khai G (chỉ tiêu 3), 6 khai T (Tự do, chỉ tiêu lưu 5). G có người khai -> ti_le_choi có số."""
    bat_fa(api)
    dung_fa_clb(api, G=(3, "GIOI_HAN"), T=(5, "TU_DO"))
    ids = [f"HS{i:03d}" for i in range(1, 13)]
    dung_hs_fa(api, *ids, nv={i: (["G", "T"] if n < 6 else ["T"]) for n, i in enumerate(ids)})
    assert api.run_pipeline(seed=7)["ok"]


def test_ti_le_choi_none_cho_clb_tu_do(api):
    _dung_fa_hai_clb(api)
    m = _theo_ma(api)
    assert m["T"]["ti_le_choi"] is None
    assert m["G"]["ti_le_choi"] == 2.0                  # 6 đăng ký / chỉ tiêu 3
    # "Chọi cao nhất" (giá trị None xếp cuối): T không đứng đầu
    ds = sorted(api.get_club_fill_stats()["data"], key=lambda c: -(c["ti_le_choi"] if c["ti_le_choi"] is not None else -1))
    assert ds[0]["club_id"] == "G"


def test_get_danh_sach_clb_co_tu_do(api):
    _dung_fa(api)
    assert api.get_danh_sach_clb("T")["data"]["tu_do"] is True
    assert api.get_danh_sach_clb("G")["data"]["tu_do"] is False


def test_get_danh_sach_clb_khong_fa_tu_do_false(api):
    api.create_or_update_club("clb_a", "CLB A", capacity=2)
    assert api.get_danh_sach_clb("clb_a")["data"]["tu_do"] is False


def _chu_xuat(api, tmp_path):
    from openpyxl import load_workbook
    p = str(tmp_path / "so.xlsx")
    api._ghi_so_excel(p, api._du_lieu_xuat())
    wb = load_workbook(p)
    return {ws.title: [[str(c) for c in r if c is not None] for r in ws.iter_rows(values_only=True)]
            for ws in wb.worksheets}


def test_xuat_clb_tu_do_khong_ghi_12_tren_5(api, tmp_path):
    _dung_fa(api)
    tat_ca = _chu_xuat(api, tmp_path)
    van = "\n".join(" | ".join(r) for dong in tat_ca.values() for r in dong)
    assert "12/5" not in van and "240" not in van
    assert "Đã xếp 12 · không giới hạn chỗ" in van     # đầu khối "Theo CLB"
    # dòng CLB T trong trang Thống kê: sức chứa "không giới hạn chỗ", tỉ lệ lấp đầy trống
    dong_t = [r for dong in tat_ca.values() for r in dong if r and "T" in r and "không giới hạn chỗ" in r]
    assert dong_t


def test_xuat_clb_gioi_han_giu_nguyen(api, tmp_path):
    _dung_fa(api)
    van = "\n".join(" | ".join(r) for dong in _chu_xuat(api, tmp_path).values() for r in dong)
    assert "/3 chỗ" in van                              # CLB G vẫn "Đã xếp x/3 chỗ"
