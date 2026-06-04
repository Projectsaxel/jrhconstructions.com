(function () {
  var root = document.querySelector(".jrh-blog-list");
  if (!root) return;

  var filters = root.querySelectorAll(".jrh-blog-filter");
  var items = root.querySelectorAll(".jrh-blog-card[data-category]");
  if (!filters.length || !items.length) return;

  function setActive(category) {
    filters.forEach(function (btn) {
      btn.classList.toggle("is-active", btn.dataset.category === category);
    });
    items.forEach(function (item) {
      item.hidden = category !== "all" && item.dataset.category !== category;
    });
  }

  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var category = btn.dataset.category || "all";
      setActive(category);
      var url = new URL(window.location.href);
      if (category === "all") url.searchParams.delete("category");
      else url.searchParams.set("category", category);
      history.replaceState(null, "", url.pathname + url.search);
    });
  });

  var params = new URLSearchParams(window.location.search);
  var initial = params.get("category") || "all";
  var valid = initial === "all";
  if (!valid) {
    filters.forEach(function (btn) {
      if (btn.dataset.category === initial) valid = true;
    });
  }
  setActive(valid ? initial : "all");
})();
