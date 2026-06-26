/* Lightweight i18n for GrekAI Skills 4 All — EN / HE with RTL.
 * No build step, no deps. Exposes window.I18N.
 *   I18N.lang()            -> "en" | "he"
 *   I18N.t(key)            -> UI string for the active language (falls back to EN, then key)
 *   I18N.loc(obj, field)   -> obj[field + "_" + lang] || obj[field]  (content fallback)
 *   I18N.set(lang)         -> persist + reload
 *   I18N.dir()             -> "rtl" | "ltr"
 * On DOMContentLoaded it applies <html lang/dir>, mounts the toggle into
 * #lang-switch, and translates any [data-i18n] / [data-i18n-html] elements.
 */
(function () {
  var STRINGS = {
    en: {
      // catalog
      filterAll: "All",
      soonSuffix: "soon",
      viewSkill: "View skill",
      demo: "Demo",
      showMore: "more",
      showLess: "less",
      emptyCat: "No items in this category yet.",
      contributeHtml: "Open source — <strong>fork it, build your own skill, open a PR.</strong> " +
        "Copy <code>skills/_template/</code>, add an entry to <code>skills.json</code>, and send it back.",
      footerCatalogHtml: "Manifest-driven · add a folder + an entry in <code>skills.json</code> to register a new item. " +
        '· by <a href="https://set4u.biz" target="_blank" rel="noopener">Set4u</a> ' +
        '· <a href="https://set4u.biz" target="_blank" rel="noopener">💖 Sponsor</a>',
      // community buttons
      fork: "Fork", star: "Star", proposePr: "Propose a PR", discuss: "Discuss", comment: "Comment",
      contribute: "Contribute",
      // status badges
      status_live: "live", status_soon: "soon", status_beta: "beta", status_wip: "wip",
      // skill page
      backAll: "← All skills",
      loading: "Loading…",
      skillPrefix: "Skill",
      install: "Install",
      installHintHtml: "Add this skill to your <strong>global</strong> Claude skills folder " +
        "(<code>~/.claude/skills/</code>) so it's available in every project — or swap the target for a repo's " +
        "<code>.claude/skills/</code> to scope it to one project:",
      altSummaryHtml: "No <code>npx</code>? Use git sparse-checkout instead",
      howToUse: "How to use",
      readme: "README",
      copy: "Copy", copied: "Copied!", copyFailed: "Copy failed",
      viewSource: "View source on GitHub",
      openDemo: "Open demo",
      readmeLoading: "Loading README…",
      noReadme: "No README found.",
      viewOnGitHub: "View on GitHub",
      footPartOf: "Part of", footBy: "by", sponsor: "Sponsor",
      // errors
      failCatalog: "Failed to load catalog",
      noSkill: "No skill specified",
      notFoundPre: 'Skill "', notFoundPost: '" not found',
      backToCatalog: "back to the catalog"
    },
    he: {
      filterAll: "הכול",
      soonSuffix: "בקרוב",
      viewSkill: "צפו בכישור",
      demo: "דמו",
      showMore: "עוד",
      showLess: "פחות",
      emptyCat: "אין עדיין פריטים בקטגוריה זו.",
      contributeHtml: "קוד פתוח — <strong>עשו פיצול, בנו כישור משלכם, פתחו PR.</strong> " +
        "העתיקו את <code>skills/_template/</code>, הוסיפו רשומה ל-<code>skills.json</code> ושִלחו בחזרה.",
      footerCatalogHtml: "מבוסס מניפסט · הוסיפו תיקייה + רשומה ב-<code>skills.json</code> כדי לרשום פריט חדש. " +
        '· מאת <a href="https://set4u.biz" target="_blank" rel="noopener">Set4u</a> ' +
        '· <a href="https://set4u.biz" target="_blank" rel="noopener">💖 חסות</a>',
      fork: "פיצול", star: "כוכב", proposePr: "הציעו PR", discuss: "דיון", comment: "תגובה",
      contribute: "תרומה",
      status_live: "פעיל", status_soon: "בקרוב", status_beta: "בטא", status_wip: "בעבודה",
      backAll: "כל הכישורים →",
      loading: "טוען…",
      skillPrefix: "כישור",
      install: "התקנה",
      installHintHtml: "הוסיפו את הכישור הזה לתיקיית הכישורים <strong>הגלובלית</strong> של Claude " +
        "(<code>~/.claude/skills/</code>) כדי שיהיה זמין בכל פרויקט — או החליפו את היעד ל-" +
        "<code>.claude/skills/</code> של מאגר כדי להגביל אותו לפרויקט אחד:",
      altSummaryHtml: "אין <code>npx</code>? השתמשו ב-git sparse-checkout במקום",
      howToUse: "איך משתמשים",
      readme: "README",
      copy: "העתקה", copied: "הועתק!", copyFailed: "ההעתקה נכשלה",
      viewSource: "צפו במקור ב-GitHub",
      openDemo: "פתחו דמו",
      readmeLoading: "טוען README…",
      noReadme: "לא נמצא README.",
      viewOnGitHub: "צפו ב-GitHub",
      footPartOf: "חלק מתוך", footBy: "מאת", sponsor: "חסות",
      failCatalog: "טעינת הקטלוג נכשלה",
      noSkill: "לא צוין כישור",
      notFoundPre: "הכישור „", notFoundPost: "” לא נמצא",
      backToCatalog: "חזרה לקטלוג"
    }
  };

  function lang() {
    try { var l = localStorage.getItem("lang"); if (l === "he" || l === "en") return l; } catch (e) {}
    return "en";
  }
  function dir() { return lang() === "he" ? "rtl" : "ltr"; }
  function t(key) {
    var L = lang();
    return (STRINGS[L] && STRINGS[L][key] != null) ? STRINGS[L][key]
         : (STRINGS.en[key] != null ? STRINGS.en[key] : key);
  }
  function loc(obj, field) {
    if (!obj) return "";
    var v = obj[field + "_" + lang()];
    return (v != null && v !== "") ? v : (obj[field] != null ? obj[field] : "");
  }
  // Translate a status value (e.g. "live"); unknown values pass through unchanged.
  function status(v) {
    if (!v) return "";
    var k = "status_" + v, s = t(k);
    return s === k ? v : s;
  }
  function set(l) {
    try { localStorage.setItem("lang", l); } catch (e) {}
    location.reload();
  }
  function applyDoc() {
    var el = document.documentElement;
    el.lang = lang();
    el.dir = dir();
  }
  function applyStatic(root) {
    root = root || document;
    root.querySelectorAll("[data-i18n]").forEach(function (n) { n.textContent = t(n.getAttribute("data-i18n")); });
    root.querySelectorAll("[data-i18n-html]").forEach(function (n) { n.innerHTML = t(n.getAttribute("data-i18n-html")); });
  }
  function mountToggle() {
    var el = document.getElementById("lang-switch");
    if (!el) return;
    var L = lang();
    el.innerHTML =
      '<button type="button" data-l="en" class="langbtn' + (L === "en" ? " langbtn--active" : "") + '">EN</button>' +
      '<button type="button" data-l="he" lang="he" class="langbtn' + (L === "he" ? " langbtn--active" : "") + '">עברית</button>';
    el.setAttribute("dir", "ltr"); // keep EN | עברית order stable in both directions
    el.querySelectorAll(".langbtn").forEach(function (b) {
      b.addEventListener("click", function () { if (b.getAttribute("data-l") !== L) set(b.getAttribute("data-l")); });
    });
  }

  window.I18N = { lang: lang, dir: dir, t: t, loc: loc, status: status, set: set, applyDoc: applyDoc, applyStatic: applyStatic, mountToggle: mountToggle };

  function init() { applyDoc(); mountToggle(); applyStatic(); }
  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
