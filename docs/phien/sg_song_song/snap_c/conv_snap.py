# usage: python -I conv_snap.py <tree-root> <out.json> base|coded|plain
# base = pre-SG-12 tree (e729ff1 worktree) with its own coded sample export; coded/plain = HEAD tree with bieu_mau.che_do_giu_ma(True/False)
import sys, os, json, hashlib, tempfile, contextlib
root, out, mode = sys.argv[1:4]
sys.path[:0] = [os.path.join(root, "mau_forms_thi_clb"), root]
import bieu_mau as bm, tao_mau_forms as tm, chuyen_forms_sang_phan_mem as cv, openpyxl
de = bm.doc_de_thi()
cm = bm.che_do_giu_ma(mode == "coded") if hasattr(bm, "che_do_giu_ma") else contextlib.nullcontext()
def dump(p):
    wb = openpyxl.load_workbook(p, data_only=True)
    return {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}
res = {}
with cm, tempfile.TemporaryDirectory() as t:
    x = os.path.join(t, "f.xlsx"); tm.ghi_mau_xuat(de, x, so_hoc_sinh=60)
    kq = cv.chuyen(x, os.path.join(t, "ra"), de)
    res["m1"] = [kq.get("n_hoc_sinh"), [c[2] for c in kq.get("canh_bao", [])], dump(os.path.join(t, "ra", cv.TEN_SO))]
    lists = os.path.join(t, "l.csv")
    sys.path.insert(0, os.path.join(root, "tests"))
    from test_t4m_chi_thi import _ghi_lists
    hs = [("a%d@truong-gia.example.test" % i, "HS %d" % i, {"thu_2": ["clb_covua", "clb_vanhoc"]}) for i in range(5)]
    _ghi_lists(lists, hs, de); ds, _ = cv.doc_lists(lists, de)
    y = os.path.join(t, "ct.xlsx"); tm.ghi_mau_xuat_chi_thi(de, y, ds)
    k2 = cv.chuyen_chi_thi([y], lists, os.path.join(t, "ra2"), de)
    res["chi_thi"] = [k2["n_hoc_sinh"], k2["n_bai_thi"], [c[2] for c in k2["canh_bao"]], dump(os.path.join(t, "ra2", cv.TEN_SO))]
json.dump(res, open(out, "w"), sort_keys=True, default=str)
