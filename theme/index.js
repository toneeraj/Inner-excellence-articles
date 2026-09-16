/* The collection is filtered in the page — no requests, no index to rebuild.
   Everything here is enhancement: with scripting off the full list still
   renders and the controls stay hidden (see .js-only in index.css). */
(function () {
  var shell = document.querySelector("[data-collection]");
  if (!shell) return;

  var input   = document.getElementById("q");
  var tally   = document.getElementById("tally");
  var empty   = document.getElementById("empty");
  var clear   = document.getElementById("clear");
  var entries = [].slice.call(shell.querySelectorAll(".entries > li"));
  var facets  = [].slice.call(shell.querySelectorAll(".facets button"));
  var total   = entries.length;
  var pillar  = "all";

  function words() {
    var q = input.value.toLowerCase().trim();
    return q ? q.split(/\s+/) : [];
  }

  function matches(li, terms) {
    if (pillar !== "all" && li.getAttribute("data-pillar") !== pillar) return false;
    var hay = li.getAttribute("data-search") || "";
    for (var i = 0; i < terms.length; i++) {
      if (hay.indexOf(terms[i]) === -1) return false;
    }
    return true;
  }

  function label(n) {
    if (n === total) return total + " article" + (total === 1 ? "" : "s");
    return n + " of " + total;
  }

  function remember() {
    if (!window.history || !history.replaceState) return;
    var params = [];
    if (input.value.trim()) params.push("q=" + encodeURIComponent(input.value.trim()));
    if (pillar !== "all") params.push("pillar=" + encodeURIComponent(pillar));
    history.replaceState(null, "", params.length
      ? location.pathname + "?" + params.join("&")
      : location.pathname);
  }

  function apply() {
    var terms = words(), shown = 0;
    entries.forEach(function (li) {
      var ok = matches(li, terms);
      li.hidden = !ok;
      if (ok) shown++;
    });
    facets.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-pillar") === pillar);
    });
    tally.textContent = label(shown);
    empty.hidden = shown !== 0;
    shell.classList.toggle("is-filtered", shown !== total);
    remember();
  }

  input.addEventListener("input", apply);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { input.value = ""; apply(); }
  });

  facets.forEach(function (button) {
    button.addEventListener("click", function () {
      var next = button.getAttribute("data-pillar");
      pillar = (pillar === next) ? "all" : next;   // click the active one to undo it
      apply();
    });
  });

  clear.addEventListener("click", function () {
    input.value = "";
    pillar = "all";
    apply();
    input.focus();
  });

  /* "/" jumps to the search box, the way it does everywhere else */
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea") return;
    e.preventDefault();
    input.focus();
    input.select();
  });

  /* a filtered view is a shareable link, so read one back on arrival */
  var query = new URLSearchParams(location.search);
  if (query.get("q")) input.value = query.get("q");
  if (query.get("pillar")) {
    var wanted = query.get("pillar");
    facets.forEach(function (b) {
      if (b.getAttribute("data-pillar") === wanted) pillar = wanted;
    });
  }
  apply();
})();
