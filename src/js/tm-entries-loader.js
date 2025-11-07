document.addEventListener("DOMContentLoaded", () => {
  const list = document.querySelector(".tm-entries");
  if (!list) return;

  let nextUrl = list.dataset.next || null;
  let loading = false;

  // Loading indicator
  const loader = document.getElementById("tm-loader");
  const setLoading = (isLoading) => {
    loading = isLoading;
    if (!loader) return;
    loader.setAttribute("aria-busy", isLoading ? "true" : "false");
  };

  // Sentinel after the list
  const sentinel = document.createElement("div");
  sentinel.id = "tm-sentinel";
  sentinel.style.height = "1px";
  list.after(sentinel);

  const observer = new IntersectionObserver(async (entries) => {
    if (!entries.some(e => e.isIntersecting)) return;
    if (!nextUrl || loading) return;

    setLoading(true);
    try {
      const url = new URL("/translations/load-more/", window.location.origin);
      url.searchParams.set("next", nextUrl);

      const res = await fetch(url.toString(), { headers: { "X-Requested-With": "XMLHttpRequest" } });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);

      // Append HTML fragment with new <li> items
      const tmp = document.createElement("template");
      tmp.innerHTML = data.html.trim();
      const lis = tmp.content.querySelectorAll(".tm-entry");
      if (lis.length === 0) {
        nextUrl = null;
        observer.unobserve(sentinel);
        return;
      }
      lis.forEach(li => list.appendChild(li));

      // Update next URL
      nextUrl = data.next || null;
      if (nextUrl) {
        list.dataset.next = nextUrl;
      } else {
        list.removeAttribute("data-next");
        observer.unobserve(sentinel);
      }
    } catch (err) {
      console.error("Failed to load more results:", err);
      if (loader) loader.querySelector("span:last-child").textContent = "Failed to load. Try scrolling again.";
      observer.unobserve(sentinel);
    } finally {
      setLoading(false);
    }
  }, { rootMargin: "800px 0px" });

  observer.observe(sentinel);
});

// Update TMX and TBX download links based on selected language
document.getElementById('id_language').addEventListener('change', function () {
  const selectedLocale = this.value;
  const tmLink = document.querySelector('.downloads a[href*="translation-memory"]');
  const termLink = document.querySelector('.downloads a[href*="terminology"]');

  if (tmLink) {
    tmLink.href = tmLink.href.replace(/\/[A-Za-z0-9-]+\.all-projects\.tmx$/, `/${selectedLocale}.all-projects.tmx`);
  }

  if (termLink) {
    termLink.href = termLink.href.replace(/\/[A-Za-z0-9-]+\.tbx$/, `/${selectedLocale}.tbx`);
  }
});
