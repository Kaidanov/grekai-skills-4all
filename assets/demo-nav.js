/*
 * demo-nav.js — a slim, self-contained nav bar injected into standalone demo pages
 * so a published/shared demo always links back to its source, code, download & docs.
 *
 * Usage (one line before </body> in a demo, loaded by ABSOLUTE url so it works
 * wherever the demo is hosted):
 *   <script src="https://grekai-skills-4all.vercel.app/assets/demo-nav.js"
 *           data-skill-id="trip-planner" data-skill-name="Trip Planner"></script>
 *
 * No dependencies. Injects its own scoped CSS (gsx- prefix) and nudges body
 * padding so it never covers the demo's content. RTL-aware via <html lang>.
 */
(function () {
  var SITE = "https://grekai-skills-4all.vercel.app";
  var REPO = "https://github.com/Kaidanov/grekai-skills-4all";

  var me = document.currentScript;
  if (!me) {
    var ss = document.getElementsByTagName("script");
    for (var i = ss.length - 1; i >= 0; i--) {
      if ((ss[i].src || "").indexOf("demo-nav.js") !== -1) { me = ss[i]; break; }
    }
  }
  var id = (me && me.getAttribute("data-skill-id")) || "";
  var name = (me && me.getAttribute("data-skill-name")) || "GrekAI Skill";
  if (document.getElementById("gsx-demo-nav")) return; // avoid double-inject

  var he = (document.documentElement.lang || "").toLowerCase().indexOf("he") === 0;
  var T = he
    ? { back: "חזרה", skill: "דף הכישור", code: "קוד", dl: "הורדה", docs: "מקור" }
    : { back: "Back", skill: "Skill page", code: "Code", dl: "Download", docs: "Source" };

  var skillUrl = SITE + "/skill?id=" + encodeURIComponent(id);
  var codeUrl = REPO + "/tree/main/skills/" + encodeURIComponent(id);
  var zipUrl = REPO + "/releases/download/skill-downloads/" + encodeURIComponent(id) + ".zip";

  var css =
    "#gsx-demo-nav{position:fixed;top:0;left:0;right:0;z-index:2147483000;" +
    "display:flex;align-items:center;gap:10px;flex-wrap:wrap;" +
    "padding:6px 12px;font:600 13px/1.2 system-ui,Segoe UI,Helvetica,Arial,sans-serif;" +
    "background:rgba(15,18,24,.92);color:#e7ebf2;border-bottom:1px solid #2a3140;" +
    "backdrop-filter:saturate(1.2) blur(6px);-webkit-backdrop-filter:blur(6px);box-sizing:border-box}" +
    "#gsx-demo-nav a{color:#e7ebf2;text-decoration:none;border:1px solid #2a3140;border-radius:7px;" +
    "padding:5px 9px;display:inline-flex;align-items:center;gap:5px;white-space:nowrap}" +
    "#gsx-demo-nav a:hover{border-color:#60a5fa}" +
    "#gsx-demo-nav .gsx-brand{display:flex;align-items:center;gap:8px;border:0;padding:0;margin-inline-end:auto;font-weight:700}" +
    "#gsx-demo-nav .gsx-brand img{width:20px;height:20px;border-radius:4px}" +
    "#gsx-demo-nav .gsx-accent{background:#2563eb;border-color:#2563eb;color:#fff}" +
    "@media(max-width:560px){#gsx-demo-nav .gsx-lbl{display:none}#gsx-demo-nav{gap:6px;padding:6px 8px}}";

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  function a(href, label, opts) {
    opts = opts || {};
    var cls = opts.accent ? ' class="gsx-accent"' : "";
    var tgt = opts.blank ? ' target="_blank" rel="noopener"' : "";
    var dl = opts.download ? ' download' : "";
    return '<a href="' + href + '"' + cls + tgt + dl + '>' +
      (opts.icon ? opts.icon + " " : "") + '<span class="gsx-lbl">' + label + "</span></a>";
  }

  var bar = document.createElement("div");
  bar.id = "gsx-demo-nav";
  bar.setAttribute("dir", he ? "rtl" : "ltr");
  bar.innerHTML =
    '<a class="gsx-brand" href="' + SITE + '" target="_blank" rel="noopener">' +
      '<img src="' + SITE + '/logo.svg" alt="" onerror="this.style.display=\'none\'">' +
      "<span>GrekAI Skills · " + esc(name) + "</span></a>" +
    a("javascript:void(0)", T.back, { icon: "←" }).replace('href="javascript:void(0)"', 'href="#" id="gsx-back"') +
    (id ? a(skillUrl, T.skill, { blank: true }) : "") +
    (id ? a(codeUrl, T.code, { blank: true }) : "") +
    (id ? a(zipUrl, T.dl, { icon: "⬇", download: true, accent: true }) : "") +
    (id ? a(skillUrl + "#readme", T.docs, { blank: true }) : "");

  function mount() {
    if (!document.body) return setTimeout(mount, 30);
    document.body.appendChild(bar);
    // push content down by the bar's height so it isn't covered
    var h = bar.offsetHeight || 40;
    var prev = parseInt(getComputedStyle(document.body).paddingTop, 10) || 0;
    document.body.style.paddingTop = prev + h + "px";
    var back = document.getElementById("gsx-back");
    if (back) back.addEventListener("click", function (e) {
      e.preventDefault();
      if (document.referrer) history.back(); else window.open(SITE, "_blank");
    });
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
