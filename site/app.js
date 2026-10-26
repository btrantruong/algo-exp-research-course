(() => {
  document.documentElement.classList.add("js");
  const tabs = [...document.querySelectorAll("[data-tab]")];
  const panels = [...document.querySelectorAll("[data-panel]")];

  function show() {
    const hash = decodeURIComponent(location.hash.slice(1)) || "home";
    const row = /^lecture-\d+$/.test(hash) ? document.getElementById(hash) : null;
    let target = row ? "schedule" : hash;
    if (!panels.some((p) => p.dataset.panel === target)) target = "home";

    panels.forEach((p) => { p.hidden = p.dataset.panel !== target; });
    tabs.forEach((t) => t.setAttribute("aria-current", t.dataset.tab === target ? "page" : "false"));

    if (row) {
      const detail = row.querySelector("details");
      if (detail) detail.open = true;
      row.scrollIntoView({ block: "center" });
    } else {
      window.scrollTo(0, 0);
    }
  }

  window.addEventListener("hashchange", show);
  show();
})();
