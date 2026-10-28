"""A13.12 — các mục backend của docs/ke_hoach/BAO_CAO_SOAT_NHAP.md. Dữ liệu MÔ PHỎNG dựng trong test.

  1.6/3.3  trang vượt quá tổng số trang được kẹp về trang cuối (danh sách em, bảng điểm, nhật ký);
  3.1      create_student_if_missing: bỏ khoảng trắng đầu/cuối, từ chối mã rỗng, tên mặc định "";
  3.2      delete_club: sao lưu + báo số điểm đã chấm / ô tick thi bị xoá theo (Truong chọn 28/10);
  4.1/4.2  delete_workspace: kiểm "đang mở" trong khoá; xoá chỗ tạm cuối cùng thì db_path vẫn dùng được;
  4.3/4.4  workspace chỉ xét nhóm (tier): lưu / đọc điểm bị từ chối (Truong chọn: chỉ tier);
  4.5      mục chấm điểm có student_id không băm được không làm cả lượt bị từ chối;
  4.6      export_workspace không rơi vào thư mục của workspace khác;
  2.7-2.9  tiện ích dùng chung (bộ nhớ xuất nhận keyword, tên trống không quay về tên có sẵn,
           số âm dạng chuỗi không bị thêm dấu nháy).
"""

import os
import threading
import time

import pytest

import api as api_mod
import api_chung
import api_xuat
import workspace as ws
from _wharton import bat_wharton, dung_clb, dung_hs
from test_ws_luat import _api, _luat


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


# ------------------------------------------------------------------ 1.6 / 3.3: kẹp trang

def test_danh_sach_hoc_sinh_trang_vuot_tong_duoc_kep_ve_trang_cuoi(api):
    for i in range(5):
        assert api.create_student_if_missing("S%d" % i, "Em %d" % i)["ok"]
    kq = api.list_students_admin(page=5, page_size=2)["data"]
    assert kq["page"] == 3 and kq["total_pages"] == 3 and kq["total"] == 5
    assert [r["student_id"] for r in kq["rows"]] == ["S4"]


def test_trang_hop_le_khong_bi_doi(api):
    for i in range(5):
        api.create_student_if_missing("S%d" % i, "Em %d" % i)
    kq = api.list_students_admin(page=2, page_size=2)["data"]
    assert kq["page"] == 2 and [r["student_id"] for r in kq["rows"]] == ["S2", "S3"]
    assert api.list_students_admin(page=0, page_size=2)["data"]["page"] == 1


def test_danh_sach_rong_van_la_trang_1(api):
    kq = api.list_students_admin(page=7, page_size=2)["data"]
    assert kq["page"] == 1 and kq["rows"] == [] and kq["total_pages"] == 1


def test_bang_diem_quyet_tam_trang_vuot_tong_duoc_kep(api):
    bat_wharton(api)
    dung_clb(api, A=5)
    for i in range(5):
        assert api.create_student_if_missing("S%d" % i, "Em %d" % i)["ok"]
        assert api.submit_preferences("S%d" % i, ["A"])["ok"]
    kq = api.list_wharton_admin(page=9, page_size=2)
    assert kq["ok"], kq
    d = kq["data"]
    assert d["page"] == 3 and d["total_pages"] == 3 and [r["student_id"] for r in d["rows"]] == ["S4"]


def test_nhat_ky_trang_vuot_tong_duoc_kep(api):
    bat_wharton(api)
    with api._ket_noi_ghi() as cur:
        for i in range(5):
            api._ghi_nhat_ky_wharton(cur, "quan_ly", "luu", "S%d" % i, None, {"a": i})
    d = api.get_wharton_nhat_ky(page=9, page_size=2)["data"]
    assert d["page"] == 3 and d["total_pages"] == 3 and len(d["rows"]) == 1


# ------------------------------------------------------------------ 3.1: create_student_if_missing

@pytest.mark.parametrize("ma", ["", "   ", None, "\t"])
def test_ma_rong_bi_tu_choi_va_khong_chen_dong(api, ma):
    kq = api.create_student_if_missing(ma, "Tên")
    assert kq["ok"] is False and kq["errors"][0]["code"] == "student_id_required"
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0


def test_ma_va_ten_duoc_bo_khoang_trang_dau_cuoi_va_khong_nhan_doi(api):
    kq = api.create_student_if_missing("  A01 ", None)
    assert kq["ok"] and kq["data"] == {"student_id": "A01", "created": True}
    kq = api.create_student_if_missing("A01", "  Nguyễn An ")
    assert kq["ok"] and kq["data"]["created"] is False        # không thành hai em khác nhau
    with api._ket_noi_doc() as cur:
        assert [tuple(r) for r in cur.execute("SELECT student_id, name FROM students")] == [("A01", "")]


# ------------------------------------------------------------------ 3.2: delete_club

def _clb_co_diem(api):
    dung_clb(api, A=5, B=5)
    dung_hs(api, "S1", "S2", "S3", tick={"S1": ["A"], "S2": ["A"], "S3": ["B"]})
    assert api.submit_club_scores("A", [{"student_id": "S1", "score": 8}, {"student_id": "S2", "score": 6}])["ok"]


def test_xoa_clb_bao_so_diem_va_o_tick_bi_xoa_va_co_ban_sao_luu(api):
    _clb_co_diem(api)
    kq = api.delete_club("A")
    assert kq["ok"], kq
    d = kq["data"]
    assert d["deleted"] is True and d["n_scores_removed"] == 2 and d["n_tests_removed"] == 2
    assert d["backup_path"] and os.path.isfile(d["backup_path"])
    import sqlite3
    con = sqlite3.connect(d["backup_path"])        # bản sao lưu còn điểm cũ
    try:
        assert con.execute("SELECT COUNT(*) FROM club_scores WHERE club_id='A'").fetchone()[0] == 2
    finally:
        con.close()


def test_xoa_clb_khong_co_diem_khong_de_ban_sao_luu_thua(api):
    dung_clb(api, A=5, B=5)
    kq = api.delete_club("B")
    assert kq["ok"] and kq["data"]["n_scores_removed"] == 0 and kq["data"]["n_tests_removed"] == 0
    assert kq["data"]["backup_path"] is None


def test_xoa_clb_van_bi_chan_khi_con_nguyen_vong(api):
    dung_clb(api, A=5)
    dung_hs(api, "S1")
    assert api.submit_preferences("S1", ["A"])["ok"]
    kq = api.delete_club("A")
    assert kq["ok"] is False and kq["errors"][0]["code"] == "cannot_delete_club_referenced"


# ------------------------------------------------------------------ 4.1 / 4.2: delete_workspace

def _hai_ws(goc, tmp_path):
    a = ws.tao(goc, "Hai A", None)
    b = ws.tao(goc, "Hai B", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir(exist_ok=True)
    api = api_mod.PipelineAPI(ws.duong_dan_db(goc, a), thu_muc_xuat=str(xuat),
                              thu_muc_goc_ws=goc, ws_da_chon=False)
    return api, a, b


def test_xoa_workspace_khong_xoa_cai_vua_duoc_mo_chen_ngang(goc, tmp_path):
    """Đua luồng: kiểm "đang mở" xong, trước khi lấy khoá thì một luồng khác mở đúng workspace đó."""
    api, a, _b = _hai_ws(goc, tmp_path)
    ket_qua = []
    api._khoa_ghi.acquire()                       # luồng "mở workspace" đang giữ khoá ghi
    try:
        t = threading.Thread(target=lambda: ket_qua.append(api.delete_workspace(a, "XOA")))
        t.start()
        time.sleep(0.4)                           # luồng xoá đã qua bước kiểm, đang chờ khoá
        api._ws_da_chon = True                    # …và "mở" xong
    finally:
        api._khoa_ghi.release()
    t.join(10)
    assert ket_qua and ket_qua[0]["ok"] is False
    assert ket_qua[0]["errors"][0]["code"] == "ws_khong_xoa_dang_mo"
    assert os.path.isfile(ws.duong_dan_db(goc, a))


def test_xoa_het_workspace_ke_ca_cho_tam_cuoi_db_path_van_dung_duoc(goc, tmp_path):
    api, a, b = _hai_ws(goc, tmp_path)
    assert api.delete_workspace(b, "XOA")["ok"]
    assert api.delete_workspace(a, "XOA")["ok"]          # chỗ tạm cuối cùng (chưa ai chọn)
    assert os.path.isfile(api.db_path), api.db_path
    assert api.get_dashboard_status()["ok"]
    assert [w["name"] for w in ws.danh_sach(goc)] == [ws.TEN_TRUONG_HOC]


# ------------------------------------------------------------------ 4.3 / 4.4: workspace chỉ xét nhóm

def _api_tier(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(priority="tier", tiers=["Cấp 1", "Cấp 2"],
                                    score_scope="per_person"))
    dung_clb(api, A=5)
    dung_hs(api, "S1", tick={"S1": ["A"]})
    return api


def test_tier_luu_diem_theo_nguoi_bi_tu_choi_vi_se_bi_bo_qua(goc, tmp_path):
    api = _api_tier(goc, tmp_path)
    kq = api.submit_person_scores([{"student_id": "S1", "score": 5}])
    assert kq["ok"] is False and kq["errors"][0]["code"] == "scoring_not_per_slot"
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT diem_ca_nhan FROM students WHERE student_id='S1'").fetchone()[0] is None


def test_tier_hai_ham_doc_cham_diem_cung_bi_tu_choi(goc, tmp_path):
    api = _api_tier(goc, tmp_path)
    for kq in (api.get_club_applicants_for_scoring("A"), api.get_scoring_overview()):
        assert kq["ok"] is False and kq["errors"][0]["code"] == "scoring_not_per_slot"


def test_per_person_khong_tier_van_doc_duoc_man_theo_clb_nhu_cu(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    assert api.get_scoring_overview()["ok"]


# ------------------------------------------------------------------ 4.5: student_id không băm được

def test_cham_diem_clb_bo_qua_muc_co_ma_khong_bam_duoc_va_van_luu_muc_dung(api):
    _clb_co_diem(api)
    kq = api.submit_club_scores("A", [{"student_id": ["x"], "score": 5},
                                      {"student_id": {"a": 1}, "score": 5},
                                      {"student_id": "S1", "score": 9}])
    assert kq["ok"], kq
    assert kq["data"]["n_saved"] == 1 and len(kq["data"]["warnings"]) == 2
    assert {w["code"] for w in kq["data"]["warnings"]} == {"score_not_applicant"}


def test_cham_diem_theo_nguoi_bo_qua_muc_co_ma_khong_bam_duoc(goc, tmp_path):
    api = _api(goc, tmp_path, _luat(score_scope="per_person"))
    dung_hs(api, "S1")
    kq = api.submit_person_scores([{"student_id": ["x"], "score": 5}, {"student_id": "S1", "score": 9}])
    assert kq["ok"], kq
    assert kq["data"]["n_saved"] == 1
    assert [w["code"] for w in kq["data"]["warnings"]] == ["student_not_found"]


# ------------------------------------------------------------------ 4.6: export_workspace

def test_export_workspace_khong_roi_vao_thu_muc_cua_workspace_khac(goc, tmp_path, monkeypatch):
    a = ws.tao(goc, "Xuat A", None)
    b = ws.tao(goc, "Xuat B", None)
    monkeypatch.setattr(api_xuat, "thu_muc_tai_ve", lambda: "")
    api = api_mod.PipelineAPI(ws.duong_dan_db(goc, b), thu_muc_xuat=str(tmp_path / "khong_co"),
                              thu_muc_goc_ws=goc)
    kq = api.export_workspace(a)
    assert kq["ok"], kq
    p = os.path.realpath(kq["data"]["path"])
    assert not p.startswith(os.path.realpath(os.path.dirname(ws.duong_dan_db(goc, b))) + os.sep), p
    assert os.path.isfile(p)


# ------------------------------------------------------------------ 2.7 - 2.9: api_chung

def test_bo_nho_trong_luc_xuat_nhan_keyword():
    class Dummy:
        _bo_nho_xuat = {}
        dem = 0

        @api_chung._nho_trong_luc_xuat
        def bao_cao(self, a, page=1):
            Dummy.dem += 1
            return {"a": a, "page": page}

    d = Dummy()
    assert d.bao_cao(1, page=2) == {"a": 1, "page": 2}
    assert d.bao_cao(1, page=2) == {"a": 1, "page": 2} and Dummy.dem == 1        # nhớ theo keyword
    assert d.bao_cao(1, page=3) == {"a": 1, "page": 3} and Dummy.dem == 2        # keyword khác: tính lại
    assert d.bao_cao(1, 2) == {"a": 1, "page": 2}                                # vị trí hợp lệ như cũ


def test_duong_dan_khong_de_khong_tra_ten_da_co_khi_qua_1000_ban(tmp_path):
    goc_ = str(tmp_path / "x.csv")
    open(goc_, "w").close()
    for n in range(2, 1003):
        open(str(tmp_path / ("x (%d).csv" % n)), "w").close()
    ra = api_chung.duong_dan_khong_de(goc_)
    assert not os.path.exists(ra) and ra.endswith("x (1003).csv")


@pytest.mark.parametrize("o,mong", [
    ("-1,5", "-1,5"), ("-3", "-3"), ("-0.25", "-0.25"),
    ("-1+1", "'-1+1"), ("=1+1", "'=1+1"), ("+1", "'+1"), ("@a", "'@a"), ("-", "'-"),
    ("-1,5x", "'-1,5x"), ("- 5", "'- 5"), ("-cmd|' /C calc'!A0", "'-cmd|' /C calc'!A0"),
    ("\t=1", "'\t=1"), ("bình thường", "bình thường"), (7, 7),
])
def test_an_toan_cho_excel_giu_so_am_dang_chuoi_nhung_van_chan_cong_thuc(o, mong):
    assert api_chung._an_toan_cho_excel(o) == mong


# ------------------------------------------------------------------ 1.10: một bản đọc ô duy nhất

def test_api_nhap_dung_chung_ham_doc_o_voi_so_nhap():
    """Sửa dấu phẩy / inf / nan ở một bản mà quên bản kia làm xem trước báo "sẵn sàng" còn nạp thật
    báo lỗi: nên chỉ giữ MỘT bản (A13.12, soát nhập 1.10)."""
    import so_nhap
    from api_nhap import NhapDuLieuMixin
    assert NhapDuLieuMixin._doc_diem is so_nhap.doc_diem
    assert NhapDuLieuMixin._o_excel_thanh_chu is so_nhap.o_thanh_chu
    for x in ("8,5", "8.5", "1,234.5", "inf", "nan", "", "  7 ", "abc"):
        assert NhapDuLieuMixin._doc_diem(x) == so_nhap.doc_diem(x) or x in ("nan",)
