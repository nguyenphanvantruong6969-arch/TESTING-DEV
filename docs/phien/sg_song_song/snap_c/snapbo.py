# usage: python -I snapbo.py <tree-root> <outdir> [giu]   -> writes the bo bieu mau (duong A and B) under outdir
import sys, os
root, out = sys.argv[1:3]
sys.path[:0] = [os.path.join(root, "mau_forms_thi_clb"), root]
import bieu_mau as bm, tao_mau_forms as tm
de = bm.doc_de_thi()
def run():
    for d in "AB":
        tm.tao_bo_bieu_mau(de, os.path.join(out, d), duong=d)
if len(sys.argv) > 3:
    with bm.che_do_giu_ma(True): run()
else: run()
