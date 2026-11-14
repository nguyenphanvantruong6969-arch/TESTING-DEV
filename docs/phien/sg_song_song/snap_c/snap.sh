#!/bin/bash
# usage: snap.sh <worktree> <out> [extra generator flag e.g. --giu-ma]  (run in a WORKTREE only: default mode writes into mau_forms_thi_clb/)
W=$1; O=$2; X=$3
mkdir -p "$O"
cd "$W"
PY=${PY:-python}
modes=("" "--fa-daa" "--fa-daa --mot-bieu-mau" "--bien-the" "--chi-thi" "--phan-hoi" "--sau-ket-qua" "--tuan-3")
i=1
for m in "${modes[@]}"; do
  d="$O/m$i"; mkdir -p "$d"
  if [ -z "$m" ]; then
    $PY mau_forms_thi_clb/tao_mau_forms.py $X >/dev/null 2>&1
    cp mau_forms_thi_clb/NHAP_FORMS_THI_CLB.docx mau_forms_thi_clb/MAU_XUAT_TU_FORMS.xlsx mau_forms_thi_clb/CAI_DAT_FORMS.md "$d"/ 2>/dev/null
    cp mau_forms_thi_clb/MAP_*.json "$d"/ 2>/dev/null
    git checkout -- mau_forms_thi_clb/; git clean -fdq mau_forms_thi_clb/
  else
    $PY mau_forms_thi_clb/tao_mau_forms.py $m $X --ra "$d" >/dev/null 2>&1 || echo "mode '$m' exit $?"
  fi
  i=$((i+1))
done
# normalise: unzip office files, drop docProps/core.xml
cd "$O"
for f in $(find . -name '*.xlsx' -o -name '*.docx'); do mkdir -p "$f.d"; unzip -qo "$f" -d "$f.d"; rm -f "$f.d/docProps/core.xml"; rm "$f"; done
