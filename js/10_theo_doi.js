/* ==========================================================================
   10_theo_doi.js — theo dõi sau khi xếp (FA gaps, V§9.3), thẻ "Chi tiết và xuất tệp".

   GAP-1: điểm danh 3 buổi đầu. Khung `#diemDanhPanel` chỉ hiện khi `rules.fa_diem_danh` bật
   (get_diem_danh trả bat: false thì ẩn). Đổi một ô -> luu_diem_danh; đủ 2/3 buổi vắng không phép thì
   backend ghi một dòng giải phóng chỗ (không sửa kết quả xếp) và dòng hiện "Đã giải phóng chỗ".
   ========================================================================== */

const DD_TRANG_THAI = [["", ""], ["CO_MAT", "dd_co_mat"], ["VANG_CO_PHEP", "dd_vang_co_phep"],
  ["VANG_KHONG_PHEP", "dd_vang_khong_phep"]];
let ddClbDangChon = "";

function veDiemDanh(d) {
  const chon = el("diemDanhClb");
  clear(chon);
  d.clubs.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.club_id;
    o.textContent = c.buoi ? c.name + " · " + nhanBuoi(c.buoi) : c.name;
    chon.appendChild(o);
  });
  chon.value = d.club_id;
  ddClbDangChon = d.club_id;
  document.querySelectorAll("#diemDanhPanel .dd-cot-buoi").forEach((th) => {
    th.textContent = t("dd_buoi_n", { n: th.dataset.so });
  });
  const body = el("diemDanhBang");
  clear(body);
  const manh = document.createDocumentFragment();
  d.hoc_sinh.forEach((h) => {
    const tr = document.createElement("tr");
    tr.dataset.studentId = h.student_id;
    const oMa = document.createElement("td");
    oMa.textContent = h.student_id;
    const oTen = document.createElement("td");
    oTen.textContent = h.name;
    if (h.da_giai_phong) {
      const tag = document.createElement("span");
      tag.className = "club-tag is-empty dd-giai-phong";
      tag.textContent = t("dd_da_giai_phong");
      oTen.append(" ", tag);
    }
    tr.append(oMa, oTen);
    [1, 2, 3].forEach((so) => {
      const td = document.createElement("td");
      const s = document.createElement("select");
      s.className = "text-input text-input-sm dd-o";
      s.dataset.studentId = h.student_id;
      s.dataset.buoiSo = String(so);
      s.setAttribute("aria-label", h.student_id + " · " + t("dd_buoi_n", { n: so }));
      DD_TRANG_THAI.forEach(([gt, khoa]) => {
        const o = document.createElement("option");
        o.value = gt;
        o.textContent = khoa ? t(khoa) : "";
        s.appendChild(o);
      });
      s.value = h["buoi_" + so] || "";
      td.appendChild(s);
      tr.appendChild(td);
    });
    const oDem = document.createElement("td");
    oDem.textContent = String(h.so_vang_khong_phep);
    tr.appendChild(oDem);
    manh.appendChild(tr);
  });
  body.appendChild(manh);
}

function taiDiemDanh(clubId) {
  return callApi("get_diem_danh", clubId === undefined ? ddClbDangChon : clubId).then((res) => {
    const panel = el("diemDanhPanel");
    const bat = !!(res && res.ok && res.data.bat);
    panel.hidden = !bat;
    if (!bat) return;
    veDiemDanh(res.data);
  });
}

function khoiTaoTheoDoi() {
  el("diemDanhClb").addEventListener("change", (e) => taiDiemDanh(e.target.value));
  el("diemDanhBang").addEventListener("change", (e) => {
    const s = e.target.closest("select.dd-o");
    if (!s) return;
    callApi("luu_diem_danh", ddClbDangChon, s.dataset.studentId, Number(s.dataset.buoiSo), s.value)
      .then((res) => {
        if (!res.ok) showErrorToast(res.errors);
        return taiDiemDanh();
      });
  });
  el("btnXuatDiemDanh").addEventListener("click", () => {
    chayXuat([["xuat_muc_diem_danh", "export_diem_danh", [""],
      (d) => t("xuat_kq_diem_danh", { n: d.n_clb, path: d.path })]], el("diemDanhFeedback"));
  });
}

khoiTaoTheoDoi();
