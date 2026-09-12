// clothing search engine - frontend logic
// vanilla javaScript, modular and framework-free

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "search") {
    initSearchPage();
  } else if (page === "documents") {
    initDocumentsPage();
  }
});

// // // // // // 
// Initialize the main Search page (index.html)
// // // // // // 

function initSearchPage() {
  let currentMode = "free";

  const modeButtons = document.querySelectorAll(".mode-btn");
  const searchForm = document.getElementById("search-form");
  const queryInput = document.getElementById("query-input");
  const kInput = document.getElementById("k-input");
  const searchBtn = document.getElementById("search-btn");
  const alertBox = document.getElementById("alert-box");
  const resultsList = document.getElementById("results-list");
  const emptyState = document.getElementById("empty-state");
  const searchStats = document.getElementById("search-stats");

  // Handle mode toggle clicks
  modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const selectedMode = btn.dataset.mode;
      if (selectedMode !== currentMode) {
        setSearchMode(selectedMode);
      }
    });
  });

  function setSearchMode(mode) {
    currentMode = mode;

    modeButtons.forEach((btn) => {
      if (btn.dataset.mode === mode) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    if (mode === "proximity") {
      kInput.classList.remove("hidden");
      kInput.required = true;
    } else {
      kInput.classList.add("hidden");
      kInput.required = false;
    }

    if (searchStats) {
      searchStats.classList.add("hidden");
      searchStats.textContent = "";
    }

    hideAlert();
  }

  // Handle search submission
  searchForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    const query = queryInput.value.trim();
    if (!query) {
      showAlert("Please enter a search term.");
      return;
    }

    // Client-side quick validations
    if (currentMode === "phrase") {
      const words = query.split(/\s+/).filter(Boolean);
      if (words.length !== 2) {
        showAlert("Phrase search requires exactly two terms (e.g. 'cotton shirt').");
        return;
      }
    }

    if (currentMode === "proximity") {
      const words = query.split(/\s+/).filter(Boolean);
      if (words.length !== 2) {
        showAlert("Proximity search requires two terms in the query field (e.g. 'cotton shirt').");
        return;
      }
      const kVal = parseInt(kInput.value, 10);
      if (isNaN(kVal) || kVal <= 0) {
        showAlert("Please provide a valid positive integer for 'k'.");
        return;
      }
    }

    await performSearch(query, currentMode);
  });

  async function performSearch(query, mode) {
    searchBtn.disabled = true;
    resultsList.innerHTML = "";
    emptyState.classList.add("hidden");
    if (searchStats) {
      searchStats.classList.add("hidden");
      searchStats.textContent = "";
    }

    let url = "";
    if (mode === "free") {
      url = `/search?q=${encodeURIComponent(query)}&k=10`;
    } else if (mode === "phrase") {
      url = `/phrase?q=${encodeURIComponent(query)}`;
    } else if (mode === "proximity") {
      const kVal = kInput.value.trim();
      url = `/proximity?q=${encodeURIComponent(query)}&k=${encodeURIComponent(kVal)}`;
    }

    try {
      const startTime = performance.now();
      const res = await fetch(url);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        const message = errorData.detail || `Server returned error ${res.status}`;
        showAlert(message);
        return;
      }

      const data = await res.json();
      const elapsed = (performance.now() - startTime).toFixed(1);

      if (data && data.length > 0 && searchStats) {
        searchStats.textContent = `Retrieved ${data.length} result${data.length === 1 ? "" : "s"} in ${elapsed} ms across 100 indexed documents.`;
        searchStats.classList.remove("hidden");
      }

      renderResults(data, mode);

      // Check if Free Text query terms have zero discriminative power (IDF = 0)
      if (mode === "free" && data.length > 0 && data[0].score === 0) {
        showAlert("Notice: Searched terms appear in 100% of documents (IDF = 0), providing no discriminative ranking.");
      }

    } catch (err) {
      showAlert("Failed to execute search. Please check the network connection.");
    } finally {
      searchBtn.disabled = false;
    }
  }

  function renderResults(results, mode) {
    resultsList.innerHTML = "";

    if (!results || results.length === 0) {
      emptyState.classList.remove("hidden");
      return;
    }

    emptyState.classList.add("hidden");

    results.forEach((item) => {
      const card = document.createElement("article");
      card.className = "card";

      // Top bar: title and score (if VSM)
      const topDiv = document.createElement("div");
      topDiv.className = "card-top";

      const title = document.createElement("h2");
      title.className = "card-title";
      title.textContent = item.title || item.doc_id;
      topDiv.appendChild(title);

      if (mode === "free" && item.score !== undefined) {
        const scoreBadge = document.createElement("span");
        scoreBadge.className = "badge-score";
        scoreBadge.textContent = `Score: ${Number(item.score).toFixed(4)}`;
        topDiv.appendChild(scoreBadge);
      }

      card.appendChild(topDiv);

      // Meta: doc_id and category
      const metaDiv = document.createElement("div");
      metaDiv.className = "card-meta";

      const docIdBadge = document.createElement("span");
      docIdBadge.className = "badge-docid";
      docIdBadge.textContent = item.doc_id;

      const categoryBadge = document.createElement("span");
      categoryBadge.className = "badge-category";
      categoryBadge.textContent = item.category || "General";

      metaDiv.appendChild(docIdBadge);
      metaDiv.appendChild(categoryBadge);
      card.appendChild(metaDiv);

      // Positional evidence for phrase and proximity searches
      if ((mode === "phrase" || mode === "proximity") && item.positions) {
        const posSection = document.createElement("div");
        posSection.className = "positional-section";

        const posTitle = document.createElement("div");
        posTitle.className = "positional-title";
        posTitle.textContent = "Positions";
        posSection.appendChild(posTitle);

        const list = document.createElement("ul");
        list.className = "positional-list";

        for (const [term, pos] of Object.entries(item.positions)) {
          const li = document.createElement("li");
          li.innerHTML = `<span class="pos-term">${escapeHtml(term)}</span> &rarr; <span class="pos-value">${pos}</span>`;
          list.appendChild(li);
        }

        if (item.distance !== undefined) {
          const distLi = document.createElement("li");
          distLi.className = "pos-distance";
          distLi.textContent = `distance = ${item.distance}`;
          list.appendChild(distLi);
        }

        posSection.appendChild(list);
        card.appendChild(posSection);
      }

      resultsList.appendChild(card);
    });
  }

  function showAlert(msg) {
    alertBox.textContent = msg;
    alertBox.style.display = "block";
  }

  function hideAlert() {
    alertBox.textContent = "";
    alertBox.style.display = "none";
  }
}
// // // // // // 
// Initialize the Documents Browser page (documents.html)
// // // // // // 

function initDocumentsPage() {
  const summaryEl = document.getElementById("docs-summary");
  const listEl = document.getElementById("documents-list");
  const errorEl = document.getElementById("docs-error");

  async function loadDocuments() {
    try {
      const res = await fetch("/docs_info");
      if (!res.ok) {
        throw new Error(`Failed to load documents (HTTP ${res.status})`);
      }

      const docs = await res.json();
      summaryEl.textContent = `Showing ${docs.length} documents`;
      renderDocumentCards(docs);
    } catch (err) {
      summaryEl.textContent = "Could not load documents.";
      errorEl.textContent = err.message || "An error occurred while fetching documents.";
      errorEl.classList.remove("hidden");
    }
  }

  function renderDocumentCards(docs) {
    listEl.innerHTML = "";

    docs.forEach((doc) => {
      const card = document.createElement("article");
      card.className = "card";

      const topDiv = document.createElement("div");
      topDiv.className = "card-top";

      const title = document.createElement("h2");
      title.className = "card-title";
      title.textContent = doc.title || doc.doc_id;
      topDiv.appendChild(title);

      card.appendChild(topDiv);

      const metaDiv = document.createElement("div");
      metaDiv.className = "card-meta";

      const docIdBadge = document.createElement("span");
      docIdBadge.className = "badge-docid";
      docIdBadge.textContent = doc.doc_id;

      const categoryBadge = document.createElement("span");
      categoryBadge.className = "badge-category";
      categoryBadge.textContent = doc.category || "General";

      metaDiv.appendChild(docIdBadge);
      metaDiv.appendChild(categoryBadge);
      card.appendChild(metaDiv);

      // Render tokens as gray outlined chips
      if (doc.tokens && doc.tokens.length > 0) {
        const tokensContainer = document.createElement("div");
        tokensContainer.className = "tokens-container";

        const tokensLabel = document.createElement("div");
        tokensLabel.className = "tokens-label";
        tokensLabel.textContent = `Processed Tokens (${doc.tokens.length})`;
        tokensContainer.appendChild(tokensLabel);

        const chipsList = document.createElement("div");
        chipsList.className = "tokens-list";

        doc.tokens.forEach((token) => {
          const chip = document.createElement("span");
          chip.className = "token-chip";
          chip.textContent = token;
          chipsList.appendChild(chip);
        });

        tokensContainer.appendChild(chipsList);
        card.appendChild(tokensContainer);
      }

      listEl.appendChild(card);
    });
  }

  loadDocuments();
}

// // // // // // 
// Escapes HTML characters for safe innerHTML injection
// // // // // // 

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
