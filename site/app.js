(() => {
  document.documentElement.classList.add("js");
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const panels = [...document.querySelectorAll("[data-panel]")];

  function show() {
    const hash = decodeURIComponent(location.hash.slice(1)) || "home";
    const row = /^lecture-\d+$/.test(hash) ? document.getElementById(hash) : null;
    // any other element id (e.g. #readings, a Resources section) opens its tab and expands it
    const anchor = !row && hash ? document.getElementById(hash) : null;
    const owner = anchor && anchor.closest("[data-panel]");
    let target = row ? "schedule" : owner ? owner.dataset.panel : hash;
    if (!panels.some((p) => p.dataset.panel === target)) target = "home";

    panels.forEach((p) => { p.hidden = p.dataset.panel !== target; });
    tabs.forEach((t) => t.setAttribute("aria-current", t.dataset.tab === target ? "page" : "false"));

    if (row) {
      const detail = row.querySelector("details");
      if (detail) detail.open = true;
      row.scrollIntoView({ block: "center" });
    } else if (owner) {
      for (let d = anchor.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
      anchor.scrollIntoView({ block: "start" });
    } else {
      window.scrollTo(0, 0);
    }
  }

  window.addEventListener("hashchange", show);
  show();
})();
