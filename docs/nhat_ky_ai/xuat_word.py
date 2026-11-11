"""Chuyển một tệp nhật ký .md thành .docx dễ đọc (A4, Arial, bảng có viền, số trang).

Chạy: python docs/nhat_ky_ai/xuat_word.py docs/nhat_ky_ai/NHAT_KY_AI_DE_DOC.md docs/nhat_ky_ai/NHAT_KY_AI.docx
Cần pandoc và python-docx.
"""
import subprocess
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# Độ rộng cột (cm) theo chữ ở ô tiêu đề đầu tiên của bảng; khổ chữ 17 cm.
DO_RONG = {
    "Mục": [3.8, 13.2],
    "Từ": [3.6, 13.4],
    "Giai đoạn": [2.2, 3.2, 11.6],
    "Đợt": [1.8, 9.6, 5.6],
    "Ngày": [2.6, 4.0, 10.4],
    "Mã phiên": [2.2, 2.3, 2.3, 1.6, 5.0, 3.6],
}
MAU = RGBColor(0x1F, 0x3A, 0x5F)
CO_CHU = {"Normal": 10.5, "Body Text": 10.5, "First Paragraph": 10.5, "Compact": 10.5,
          "Title": 18, "Heading 1": 16, "Heading 2": 13.5, "Heading 3": 12}


def dat_phong(style, ten="Arial", co=None):
    style.font.name = ten
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), ten)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    if co:
        style.font.size = Pt(co)


def lam_dep(duong_dan):
    d = Document(duong_dan)
    for sec in d.sections:
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2)
        sec.top_margin = sec.bottom_margin = Cm(2)
    for st in d.styles:
        if st.type == 1:  # đoạn
            dat_phong(st, co=CO_CHU.get(st.name))
            if st.name.startswith("Heading") or st.name == "Title":
                st.font.color.rgb = MAU
                st.paragraph_format.keep_with_next = True
            if st.name in ("Body Text", "First Paragraph", "Compact"):
                st.paragraph_format.space_after = Pt(4)
        elif st.type == 2:  # ký tự
            dat_phong(st)
    for st in d.styles:
        if st.name in ("Verbatim Char", "Source Code"):
            dat_phong(st, "Consolas", 9.5)
    for t in d.tables:
        tblPr = t._tbl.tblPr
        vien = OxmlElement("w:tblBorders")
        for canh in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{canh}")
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), "4")
            e.set(qn("w:color"), "A0A0A0")
            vien.append(e)
        cu = tblPr.find(qn("w:tblBorders"))
        if cu is not None:
            tblPr.remove(cu)
        tblPr.append(vien)
        dau = t.rows[0].cells[0].text.strip()
        rong = DO_RONG.get(dau)
        if rong and len(rong) == len(t.columns):
            kieu = OxmlElement("w:tblLayout")
            kieu.set(qn("w:type"), "fixed")
            tblPr.append(kieu)
            for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), rong):
                gc.set(qn("w:w"), str(int(w * 567)))
            for hang in t.rows:
                for o, w in zip(hang.cells, rong):
                    o.width = Cm(w)
        for o in t.rows[0].cells:
            for p in o.paragraphs:
                for r in p.runs:
                    r.bold = True
            nen = OxmlElement("w:shd")
            nen.set(qn("w:val"), "clear")
            nen.set(qn("w:fill"), "E8EEF5")
            o._tc.get_or_add_tcPr().append(nen)
        for hang in t.rows:
            for o in hang.cells:
                for p in o.paragraphs:
                    p.paragraph_format.space_after = Pt(1)
                    for r in p.runs:
                        r.font.size = Pt(9.5)
    for sec in d.sections:
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run()
        for loai, chu in (("begin", None), (None, "PAGE"), ("end", None)):
            if loai:
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), loai)
            else:
                e = OxmlElement("w:instrText")
                e.set(qn("xml:space"), "preserve")
                e.text = chu
            r._r.append(e)
    d.core_properties.title = "Nhật ký sử dụng AI"
    d.save(duong_dan)


def main():
    nguon, dich = sys.argv[1], sys.argv[2]
    subprocess.run(["pandoc", nguon, "-f", "gfm", "-o", dich], check=True)
    lam_dep(dich)
    print(dich)


if __name__ == "__main__":
    main()
