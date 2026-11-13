"""FG-7 (STEP0, spec §3): biểu mẫu "Sau khi xem kết quả" — chỉ liệt kê buổi có CLB trong sổ, tiêu đề riêng, hướng dẫn
bước 4 chỉ đường menu, `--help` không còn mã nội bộ, in thư mục ra tuyệt đối; các chế độ khác GIỮ NGUYÊN từng byte.
Dữ liệu MÔ PHỎNG; mọi việc Forms là TH.

Spec §3 còn một ý "thêm một dòng giải thích vì sao giữ `[tag]` và `(code)`": hướng dẫn hiện đã có bước 5 nói kiosk đọc
theo các mã đó, nên KHÔNG có test riêng cho dòng đó (người làm FG-7 xem lại, ghi vào nhật ký).
"""
import hashlib
import os
import re
import sys

import pytest

import so_nhap

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))
import bieu_mau as bm  # noqa: E402
import tao_mau_forms as tmf  # noqa: E402

# sha256 của cả thư mục đầu ra (tên + nội dung) chụp trên f5e8a41, sinh hai lần giống nhau.
# Byte đầu ra khác nhau theo hệ điều hành (os.name); FG không đổi các chế độ này, nên mỗi nền
# tảng giữ nguyên băm của chính nó (posix: chụp ở STEP0; nt: đầu ra thật ở CI run 43376547591).
# SG-5 cố ý đổi `fa_daa` và `fa_daa_mot`: posix chụp lại; nt chưa có băm mới, nên hai chế độ đó trên nt chỉ
# kiểm BĂM NỘI DUNG (không phụ thuộc hệ điều hành, xem `_bam_noi_dung`), không kiểm băm byte.
_CHE_DO = {
    "fa_daa": ["--fa-daa"],
    "fa_daa_mot": ["--fa-daa", "--mot-bieu-mau"],
    "phan_hoi": ["--phan-hoi"],
    "tuan_3": ["--tuan-3"],
}
_BAM_THEO_HE = {
    "posix": {
        "fa_daa": "172df180d80f257051cda2502ff125378524fa45819ca72a49453000dd64c84d",
        "fa_daa_mot": "a40300e96830dba1ab1a7d45dc243288324fa600738f37ce363174abc71d0f75",
        "phan_hoi": "f4cc8d3f5bd8c560685c455a919ce0a81ffe05e82843498d931ccbe673c8c54a",
        "tuan_3": "eb73af3d5a3a80babec6b30dfbe5e63faf24016c8ec5ea04aece6cad75073e00",
    },
    "nt": {
        "fa_daa": "c9f376b4587ea03aab1be9358964cbad1c67adef31af16c7ca4c68a4c4cbd41f",
        "fa_daa_mot": "143e8f0383a48c30fe93c582518e301cf834b3b9f446953a379e06efeb2ac9bf",
        "phan_hoi": "f624c558d4c5a2fb0ab0b8098a0389c2796d229fe227049be3928d5ba446c773",
        "tuan_3": "ebdfc5ce76d75e799e7588c631467742e6ab15ff5cf736551a25a86de597002c",
    },
}
BAM_GOC = {k: (_CHE_DO[k], _BAM_THEO_HE[os.name][k]) for k in _CHE_DO}


def _bam_cay(thu_muc):
    h = hashlib.sha256()
    for r, _, tep in sorted(os.walk(thu_muc)):
        for t in sorted(tep):
            p = os.path.join(r, t)
            h.update(os.path.relpath(p, thu_muc).replace(os.sep, "/").encode())
            with open(p, "rb") as f:
                h.update(f.read())
    return h.hexdigest()


def _bam_noi_dung(thu_muc):
    """Băm không phụ thuộc hệ điều hành: tên tệp + byte của .md + chữ trong đoạn văn/bảng của .docx (không byte zip)."""
    from docx import Document
    h = hashlib.sha256()
    for r, _, tep in sorted(os.walk(thu_muc)):
        for t in sorted(tep):
            p = os.path.join(r, t)
            h.update(os.path.relpath(p, thu_muc).replace(os.sep, "/").encode())
            if t.endswith(".md"):
                with open(p, "rb") as f:
                    h.update(f.read().replace(b"\r\n", b"\n"))
            elif t.endswith(".docx"):
                d = Document(p)
                for x in d.paragraphs:
                    h.update(x.text.encode() + b"\n")
                for b in d.tables:
                    for dong in b.rows:
                        for o in dong.cells:
                            h.update(o.text.encode() + b"\t")
    return h.hexdigest()


# SG-5: chỉ hai chế độ đăng ký FA-DAA; băm nội dung chụp trên posix, đúng trên cả hai hệ điều hành.
_BAM_NOI_DUNG = {"fa_daa": "7677a8de7d116d65a8d00c3c1f468a0be032baef31200d2670408aab19afad53", "fa_daa_mot": "666e56b2a8fe2521f7a50ba4e5e9abe73c45d89a89469d934946490d337081e6"}


@pytest.mark.parametrize("ten", sorted(BAM_GOC))
def test_che_do_khac_giu_nguyen_tung_byte(ten, tmp_path):
    arg, bam = BAM_GOC[ten]
    assert tmf.main(arg + ["--ra", str(tmp_path)]) == 0
    if ten in _BAM_NOI_DUNG:
        assert _bam_noi_dung(str(tmp_path)) == _BAM_NOI_DUNG[ten]
    if ten in _BAM_NOI_DUNG and os.name == "nt":
        pytest.skip("SG-5: băm byte của %s trên nt chưa chụp lại (đã kiểm băm nội dung ở trên)" % ten)
    assert _bam_cay(str(tmp_path)) == bam


def _so_ba_ngay(tmp_path):
    """Sổ nhập CLB MÔ PHỎNG: chỉ các CLB của thu_2, thu_3, thu_4 trong de_thi.json."""
    de = bm.doc_de_thi()
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": 10, "reserve_capacity": 0,
              "reserve_group": "", "buoi": c["buoi"], "loai": "TU_DO"}
             for c in de["cau_lac_bo"] if c["buoi"] in ("thu_2", "thu_3", "thu_4")]
    p = str(tmp_path / "so_ba_ngay.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, [])
    return p


def _chu_docx(duong):
    from docx import Document
    return [p.text for p in Document(duong).paragraphs]


def test_sau_ket_qua_voi_so_nhap_chi_liet_ke_ngay_co_clb(tmp_path):
    ra = tmp_path / "ra"
    assert tmf.main(["--sau-ket-qua", "--so-nhap-clb", _so_ba_ngay(tmp_path), "--ra", str(ra)]) == 0
    chu = "\n".join(_chu_docx(str(ra / tmf.TEN_DOCX_SAU_KET_QUA)))
    for ma in ("thu_2", "thu_3", "thu_4"):
        assert "(%s)" % ma in chu
    for ma in ("thu_5", "thu_6"):
        assert "(%s)" % ma not in chu


def test_sau_ket_qua_khong_so_nhap_nhu_cu(tmp_path):
    ra = tmp_path / "ra"
    assert tmf.main(["--sau-ket-qua", "--ra", str(ra)]) == 0
    chu = "\n".join(_chu_docx(str(ra / tmf.TEN_DOCX_SAU_KET_QUA)))
    assert all("(%s)" % b["ma"] in chu for b in bm.doc_de_thi()["buoi"])        # đủ 5 ngày như trước


def test_tieu_de_rieng_cho_che_do_sau_ket_qua(tmp_path):
    assert tmf.main(["--sau-ket-qua", "--ra", str(tmp_path)]) == 0
    dong = _chu_docx(str(tmp_path / tmf.TEN_DOCX_SAU_KET_QUA))
    assert dong[0] == "Phản hồi và báo lỗi sau khi xem kết quả"


def test_huong_dan_buoc_4_chi_duong_menu_khong_ten_khoa_cau_hinh(tmp_path):
    assert tmf.main(["--sau-ket-qua", "--ra", str(tmp_path)]) == 0
    with open(tmp_path / tmf.TEN_CAI_DAT_SAU_KET_QUA, encoding="utf-8") as f:
        md = f.read()
    buoc4 = next(d for d in md.splitlines() if d.startswith("4. "))
    assert "Tính năng sau khi xếp" in buoc4
    assert "fa_phan_hoi" not in buoc4 and "fa_khieu_nai" not in buoc4


def test_help_khong_con_ma_noi_bo(capsys):
    with pytest.raises(SystemExit):
        tmf.main(["--help"])
    giup = capsys.readouterr().out
    assert giup
    assert not re.search(r"FA-[A-Z]\w*|GAP-\d+|\bTH\b|đường B|đường A", giup), giup


def test_in_thu_muc_ra_tuyet_doi_o_dong_cuoi(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert tmf.main(["--sau-ket-qua", "--ra", "ra_tuong_doi"]) == 0
    dong_cuoi = [d for d in capsys.readouterr().out.splitlines() if d.strip()][-1]
    assert os.path.abspath(str(tmp_path / "ra_tuong_doi")) in dong_cuoi


@pytest.mark.parametrize("arg", [["--phan-hoi"], ["--tuan-3"], ["--fa-daa"], ["--chi-thi"], ["--moi-clb"]])
def test_moi_che_do_in_thu_muc_ra_tuyet_doi_o_dong_cuoi(arg, tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert tmf.main(arg + ["--ra", "ra_tuong_doi"]) == 0
    dong_cuoi = [d for d in capsys.readouterr().out.splitlines() if d.strip()][-1]
    assert dong_cuoi.endswith(os.path.abspath(str(tmp_path / "ra_tuong_doi")))


def test_che_do_mac_dinh_in_thu_muc_ghi_o_dong_cuoi(tmp_path, capsys, monkeypatch):
    # Chế độ mặc định ghi cạnh tệp tao_mau_forms.py (THU_MUC), không theo --ra; ghi tạm sang thư mục thử.
    monkeypatch.setattr(tmf, "THU_MUC", str(tmp_path / "mac_dinh"))
    os.makedirs(tmf.THU_MUC)
    assert tmf.main([]) == 0
    dong_cuoi = [d for d in capsys.readouterr().out.splitlines() if d.strip()][-1]
    assert dong_cuoi.endswith(os.path.abspath(tmf.THU_MUC))
