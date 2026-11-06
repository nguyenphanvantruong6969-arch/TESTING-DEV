# -*- coding: utf-8 -*-
"""T4M-BK1: site script JSON (createSPList + addSPField / addSPFieldXml) cho bốn list.

Cách A và B của `T4M_KET_QUA_TAI_LIEU.md` §8.1. Cột Choice dùng addSPFieldXml (có ID cố định); Text, Number,
DateTime dùng addSPField với internalName = tên trong hợp đồng. Số hành động: áp đồng bộ tối đa 30, không đồng bộ 300.

TH: chưa chạy trên Power Apps / SharePoint (chưa Add-SPOSiteScript / Invoke-PnPSiteScript lần nào).
"""

import json
from xml.sax.saxutils import escape, quoteattr

from . import cot_lists

TRAN_DONG_BO = 30
TRAN_KHONG_DONG_BO = 300


def _xml_choice(ten_list, c):
    return ('<Field Type="Choice" DisplayName=%s Name=%s StaticName=%s ID="{%s}" Required="%s" Format="Dropdown">'
            "<CHOICES>%s</CHOICES></Field>") % (
        quoteattr(c.hien_thi), quoteattr(c.ten), quoteattr(c.ten), cot_lists.guid_cot(ten_list, c.ten),
        "TRUE" if c.bat_buoc else "FALSE", "".join("<CHOICE>%s</CHOICE>" % escape(v) for v in c.lua_chon))


def tao_site_script():
    hanh_dong = []
    for ten_list, cot in cot_lists.TAT_CA.items():
        hanh_dong.append({"verb": "createSPList", "listName": ten_list, "templateType": 100,
                          "subactions": []})
        for c in cot:
            if c.kieu == "Choice":
                hanh_dong.append({"verb": "addSPFieldXml", "schemaXml": _xml_choice(ten_list, c),
                                  "addToDefaultView": True})
            else:
                hanh_dong.append({"verb": "addSPField", "fieldType": c.kieu, "displayName": c.hien_thi,
                                  "internalName": c.ten, "isRequired": c.bat_buoc, "addToDefaultView": True})
    return {"actions": hanh_dong, "bindata": {}, "version": 1}


def dem_hanh_dong(ss):
    return len(ss["actions"])


def kiem_so_hanh_dong(n, in_ra=print):
    """In số hành động; cảnh báo khi > 30 (áp đồng bộ); lỗi khi > 300 (trần áp không đồng bộ)."""
    in_ra("Số hành động của site script: %d" % n)
    if n > TRAN_KHONG_DONG_BO:
        raise ValueError("site script có %d hành động, vượt trần %d" % (n, TRAN_KHONG_DONG_BO))
    if n > TRAN_DONG_BO:
        in_ra("CẢNH BÁO: %d hành động > %d, chỉ áp được theo kiểu không đồng bộ (Settings > Apply a site "
              "template); Invoke-SPOSiteDesign (đồng bộ) sẽ từ chối." % (n, TRAN_DONG_BO))


def ghi(duong, in_ra=print):
    ss = tao_site_script()
    kiem_so_hanh_dong(dem_hanh_dong(ss), in_ra)
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ss, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return ss
