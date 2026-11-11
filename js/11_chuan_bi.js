/* ==========================================================================
   11_chuan_bi.js — thẻ "Chuẩn bị đợt" (FA-M7 G0): chọn đường A / B và khung năm bước.

   Hợp đồng dùng chung (worker A viết, B và C vẽ vào các khung):
     window.ChuanBi = { duong(), dangKyBuoc(so, veFn), lamMoi() }
       duong()            -> "A" | "B" | null (chưa chọn), theo `rules.fa_duong`
       dangKyBuoc(so, fn) -> đăng ký hàm vẽ cho khung #cb-buoc-<so> (1..5); fn(khung) được gọi mỗi lần thẻ mở,
                             mỗi lần đổi đường, và mỗi lần lamMoi(); fn tự xoá và vẽ lại nội dung khung.
       lamMoi()           -> đọc lại đường từ backend rồi vẽ lại mọi khung đã đăng ký.
   Thẻ chỉ hiện khi `FA_BAT` (rules.fa_daa, đặt ở wsApDungCauHinh).
   ========================================================================== */
"use strict";

window.ChuanBi = (() => {
  const SO_BUOC = 5;
  let duongHienTai = null;
  const veBuoc = {};

  function duong() { return duongHienTai; }

  function dangMo() { return currentTabName() === "chuan_bi"; }

  function veMotBuoc(so) {
    const khung = el("cb-buoc-" + so);
    if (!khung || !veBuoc[so]) return;
    clear(khung);
    veBuoc[so](khung);
  }

  function veMoiBuoc() {
    Object.keys(veBuoc).forEach((so) => veMotBuoc(Number(so)));
  }

  function dangKyBuoc(so, veFn) {
    if (!Number.isInteger(so) || so < 1 || so > SO_BUOC || typeof veFn !== "function") return;
    veBuoc[so] = veFn;
    if (dangMo()) veMotBuoc(so);
  }

  function chonONhap() {
    document.querySelectorAll('input[name="cbDuong"]').forEach((o) => {
      o.checked = o.value === duongHienTai;
    });
  }

  function lamMoi() {
    return callApi("get_fa_duong").then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return res; }
      duongHienTai = res.data.duong || null;
      chonONhap();
      veMoiBuoc();
      return res;
    });
  }

  function datDuong(gia_tri) {
    return callApi("dat_fa_duong", gia_tri).then((res) => {
      if (!res.ok) { showErrorToast(res.errors); chonONhap(); return res; }
      duongHienTai = res.data.duong;
      veMoiBuoc();
      return res;
    });
  }

  /* Thẻ hiện khi FA-DAA bật; tắt mà đang đứng ở thẻ này thì về thẻ đầu. */
  function capNhatThe() {
    const nut = document.querySelector('.nav-item[data-tab="chuan_bi"]');
    if (!nut) return;
    nut.hidden = !FA_BAT;
    el("cbGhiChuTat").hidden = FA_BAT;
    el("cbDuongPanel").hidden = !FA_BAT;
    if (!FA_BAT && dangMo()) switchTab("pipeline");
  }

  TAB_LOADERS.chuan_bi = () => { capNhatThe(); if (FA_BAT) lamMoi(); };

  document.querySelectorAll('input[name="cbDuong"]').forEach((o) => {
    o.addEventListener("change", () => { if (o.checked) datDuong(o.value); });
  });

  /* wsApDungCauHinh (js/075_workspace.js) đặt FA_BAT mỗi lần mở / đổi không gian làm việc: móc vào đó để thẻ
     theo cờ, không sửa tệp của người khác. Mọi lời gọi tìm hàm theo tên toàn cục nên thấy bản bọc. */
  const goc = window.wsApDungCauHinh;
  if (typeof goc === "function") {
    window.wsApDungCauHinh = function (cfg) {
      const kq = goc.apply(this, arguments);
      capNhatThe();
      return kq;
    };
  }

  return { duong, dangKyBuoc, lamMoi };
})();
