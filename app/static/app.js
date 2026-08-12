/**
 * Beyond RAG digital textbook — frontend.
 *
 * Three panes: topic tree (left), rendered concept page (center), RAG chat
 * (right). Talks to the FastAPI backend at /api/*. Markdown is rendered with
 * marked; math ($.../$$..$$) is extracted before marked runs (see
 * protectMath/restoreMath) and rendered directly with katex.renderToString,
 * code with highlight.js, and diagrams with mermaid (```mermaid fences).
 */

/* global marked, katex, hljs, mermaid */

const treeEl = document.getElementById("tree");
const pageEl = document.getElementById("page-content");
const readerEl = document.getElementById("reader");
const searchBox = document.getElementById("search-box");
const searchResultsEl = document.getElementById("search-results");
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");

let TREE = null;
let FLAT = [];            // ordered [{id, title, week}] for prev/next nav
let chatHistory = [];     // [{role, content}] sent back to the server

/**
 * Wire up a draggable divider that resizes a panel by writing a CSS custom
 * property on <html>, persisted in localStorage across visits.
 * @param {object} opts
 * @param {string} opts.resizerId - id of the thin drag-handle element
 * @param {string} opts.panelId - id of the panel element being resized
 * @param {string} opts.cssVar - CSS custom property that controls its grid width
 * @param {string} opts.storageKey - localStorage key to persist the chosen width
 * @param {number} opts.min - minimum panel width in px
 * @param {number} opts.max - maximum panel width in px
 * @param {boolean} [opts.growLeft] - true if dragging left should grow the panel
 *   (e.g. the chat panel, which sits to the right of its resizer)
 * @param {string} opts.activeClass - class added to <body> while dragging (for cursor/highlight CSS)
 */
function makeResizer({ resizerId, panelId, cssVar, storageKey, min, max, growLeft, activeClass }) {
  const resizer = document.getElementById(resizerId);
  const sign = growLeft ? -1 : 1;

  const saved = parseInt(localStorage.getItem(storageKey), 10);
  if (saved) document.documentElement.style.setProperty(cssVar, `${saved}px`);

  resizer.addEventListener("mousedown", (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = document.getElementById(panelId).getBoundingClientRect().width;
    document.body.classList.add(activeClass);

    function onMove(ev) {
      const width = Math.min(max, Math.max(min, startWidth + sign * (ev.clientX - startX)));
      document.documentElement.style.setProperty(cssVar, `${width}px`);
    }
    function onUp() {
      document.body.classList.remove(activeClass);
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
      const width = parseInt(getComputedStyle(document.documentElement).getPropertyValue(cssVar), 10);
      localStorage.setItem(storageKey, width);
    }
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  });
}

makeResizer({
  resizerId: "sidebar-resizer", panelId: "sidebar", cssVar: "--sidebar-width",
  storageKey: "sidebarWidth", min: 220, max: 520, growLeft: false, activeClass: "resizing-sidebar",
});
makeResizer({
  resizerId: "chat-resizer", panelId: "chat-panel", cssVar: "--chat-width",
  storageKey: "chatPanelWidth", min: 280, max: 720, growLeft: true, activeClass: "resizing-chat",
});

mermaid.initialize({ startOnLoad: false, theme: "neutral", fontFamily: "Georgia, serif" });

/**
 * Pull math out of markdown into inert placeholders, so that CommonMark's
 * backslash-escape rule (which silently strips the backslash from \#, \,,
 * \_, \{, \}, \[, \( etc.) never gets a chance to corrupt LaTeX before KaTeX
 * sees it. Recognises both dollar delimiters ($$..$$, $..$) and the
 * ChatGPT-style bracket delimiters (\[..\], \(..\)) some models default to
 * regardless of prompt instructions. Skips fenced ``` code blocks entirely.
 * @param {string} md
 * @param {Array<{display: boolean, expr: string}>} store - filled in-place
 * @returns {string} markdown with math replaced by M<index> tokens
 */
function protectMath(md, store) {
  const stash = (display) => (_, expr) => {
    store.push({ display, expr });
    return `M${store.length - 1}`;
  };
  return md
    .split(/(```[\s\S]*?```)/g)
    .map((part) =>
      part.startsWith("```")
        ? part
        : part
            .replace(/\$\$([\s\S]+?)\$\$/g, stash(true))
            .replace(/\\\[([\s\S]+?)\\\]/g, stash(true))
            .replace(/\$([^\$\n]+?)\$/g, stash(false))
            .replace(/\\\(([\s\S]+?)\\\)/g, stash(false))
    )
    .join("");
}

/**
 * Replace protectMath's placeholder tokens in rendered HTML with real KaTeX markup.
 * @param {string} html
 * @param {Array<{display: boolean, expr: string}>} store
 * @returns {string}
 */
function restoreMath(html, store) {
  return html.replace(/M(\d+)/g, (_, idx) => {
    const { display, expr } = store[Number(idx)];
    try {
      return katex.renderToString(expr, { displayMode: display, throwOnError: false });
    } catch (e) {
      return display ? `$$${expr}$$` : `$${expr}$`;
    }
  });
}

/**
 * Render a markdown string into a container: protect math -> marked -> restore math (KaTeX) -> hljs -> mermaid.
 * @param {HTMLElement} el - target container
 * @param {string} md - markdown source (may contain $..$ / $$..$$ and ```mermaid)
 */
async function renderMarkdown(el, md) {
  const mathStore = [];
  const protectedMd = protectMath(md, mathStore);
  const html = marked.parse(protectedMd, { mangle: false, headerIds: false });
  el.innerHTML = restoreMath(html, mathStore);
  el.querySelectorAll("pre code").forEach((block) => {
    const lang = [...block.classList].find((c) => c.startsWith("language-"));
    if (lang === "language-mermaid") return;
    hljs.highlightElement(block);
  });
  // mermaid fences: replace <pre><code class="language-mermaid"> with rendered
  // SVG, but only for diagrams that actually parse. mermaid.run() does NOT
  // throw on invalid syntax — its default behavior is to render its own
  // inline error graphic (a "bomb" icon) in place of the diagram, which reads
  // as a broken app to the user. Validating with mermaid.parse() first lets
  // us fall back to the plain, readable source block instead of that error
  // graphic when an LLM-generated diagram (occasionally) isn't valid Mermaid.
  const fences = el.querySelectorAll("code.language-mermaid");
  for (const code of fences) {
    const source = code.textContent;
    try {
      await mermaid.parse(source);
      const div = document.createElement("div");
      div.className = "mermaid";
      div.textContent = source;
      code.closest("pre").replaceWith(div);
    } catch (e) {
      console.warn("mermaid syntax error, leaving as plain code block", e);
    }
  }
  try {
    await mermaid.run({ nodes: el.querySelectorAll(".mermaid") });
  } catch (e) {
    console.warn("mermaid render failed", e);
  }
}

/* ── Tree ─────────────────────────────────────────────────────────────── */

/** Build the left navigation from /api/tree. */
async function loadTree() {
  TREE = await (await fetch("/api/tree")).json();
  FLAT = [];
  treeEl.innerHTML = "";
  for (const week of TREE.weeks) {
    const weekDiv = document.createElement("div");
    weekDiv.className = "week";
    const label = document.createElement("button");
    label.className = "week-label";
    label.innerHTML = `<span class="wk">Week ${week.week}</span>${week.title}`;
    label.onclick = () => weekDiv.classList.toggle("collapsed");
    weekDiv.appendChild(label);
    const body = document.createElement("div");
    body.className = "week-body";
    for (const topic of week.topics) {
      const t = document.createElement("div");
      t.className = "topic-label";
      t.textContent = topic.title;
      body.appendChild(t);
      for (const c of topic.concepts) {
        FLAT.push({ id: c.id, title: c.title, week: week.week });
        const a = document.createElement("a");
        a.className = "concept";
        a.dataset.id = c.id;
        a.textContent = c.title;
        a.href = `#${c.id}`;
        body.appendChild(a);
      }
    }
    weekDiv.appendChild(body);
    treeEl.appendChild(weekDiv);
  }
}

/**
 * Load and render one concept page into the center pane.
 * @param {string} id - page id (e.g. "w1-semantic-search")
 */
async function showPage(id) {
  const r = await fetch(`/api/page/${encodeURIComponent(id)}`);
  if (!r.ok) { pageEl.innerHTML = `<p class="loading">Page not found: ${id}</p>`; return; }
  const p = await r.json();

  document.querySelectorAll(".concept.active").forEach((e) => e.classList.remove("active"));
  const link = document.querySelector(`.concept[data-id="${CSS.escape(id)}"]`);
  if (link) link.classList.add("active");

  const idx = FLAT.findIndex((f) => f.id === id);
  const prev = idx > 0 ? FLAT[idx - 1] : null;
  const next = idx >= 0 && idx < FLAT.length - 1 ? FLAT[idx + 1] : null;

  pageEl.innerHTML = "";
  const crumb = document.createElement("div");
  crumb.className = "crumb";
  crumb.textContent = `Week ${p.week} · ${p.topic}`;
  const h1 = document.createElement("h1");
  h1.textContent = p.title;
  const summary = document.createElement("p");
  summary.className = "pagesummary";
  summary.textContent = p.summary || "";
  const body = document.createElement("div");
  pageEl.append(crumb, h1, summary, body);
  await renderMarkdown(body, p.markdown);
  attachEquationCitations(body, p.equation_citations || []);

  const nav = document.createElement("div");
  nav.className = "pagenav";
  nav.innerHTML =
    (prev ? `<a href="#${prev.id}">← ${prev.title}</a>` : "<span></span>") +
    (next ? `<a href="#${next.id}">${next.title} →</a>` : "<span></span>");
  pageEl.appendChild(nav);
  readerEl.scrollTo({ top: 0 });
}

/**
 * Inject a small "source" citation right after each rendered display
 * equation, index-aligned with the page's own $$...$$ blocks (one per
 * .katex-display element, in document order — see ingest/link_equations.py).
 * Clickable and opens in a new tab when a video timestamp is available;
 * otherwise a plain (non-interactive) reference to the PDF section.
 * @param {HTMLElement} container - the rendered page body
 * @param {Array<{title:string,section:string,kind:string,url:?string}|null>} citations
 */
function attachEquationCitations(container, citations) {
  const blocks = container.querySelectorAll(".katex-display");
  blocks.forEach((block, i) => {
    const c = citations[i];
    if (!c) return;
    const badge = document.createElement("div");
    badge.className = "eq-citation";
    if (c.kind === "transcript" && c.url) {
      const a = document.createElement("a");
      a.href = c.url;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = `${c.title} — ${c.section}`;
      badge.appendChild(a);
    } else {
      badge.textContent = `source: ${c.title} — ${c.section}`;
    }
    block.insertAdjacentElement("afterend", badge);
  });
}

/* ── Semantic search ─────────────────────────────────────────────────── */

/** Run /api/search and show hits in the sidebar (replacing the tree). */
async function runSearch(q) {
  searchResultsEl.innerHTML = `<p class="loading">Searching…</p>`;
  treeEl.classList.add("hidden");
  searchResultsEl.classList.remove("hidden");
  try {
    const r = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const { hits } = await r.json();
    searchResultsEl.innerHTML = `<span class="back">← back to contents</span>`;
    searchResultsEl.querySelector(".back").onclick = clearSearch;
    for (const h of hits) {
      const d = document.createElement("div");
      d.className = "hit";
      d.innerHTML = `<div class="t">${h.title}</div><div class="s">${h.section} · ${h.score}</div><div class="x">${h.text.slice(0, 140)}…</div>`;
      d.onclick = () => { location.hash = h.page_id; clearSearch(); };
      searchResultsEl.appendChild(d);
    }
  } catch (e) {
    searchResultsEl.innerHTML = `<p class="loading">Search failed: ${e}</p>`;
  }
}

/** Restore the tree after a search. */
function clearSearch() {
  searchResultsEl.classList.add("hidden");
  treeEl.classList.remove("hidden");
  searchBox.value = "";
}

searchBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && searchBox.value.trim()) runSearch(searchBox.value.trim());
  if (e.key === "Escape") clearSearch();
});

/* ── Chat ─────────────────────────────────────────────────────────────── */

/**
 * Append a chat bubble.
 * @param {"user"|"assistant"} role
 * @param {string} md - message content (markdown for assistant)
 * @param {Array<{kind:string,week:number,title:string,section:string,url:?string}>} [sources]
 * @param {string} [searchQuery] - the cleaned-up query actually used for retrieval,
 *   shown subtly so a bad query rewrite is visible rather than a silent miss
 * @returns {HTMLElement} the message element
 */
function addMessage(role, md, sources, searchQuery) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (role === "assistant") {
    renderMarkdown(bubble, md);
  } else {
    bubble.textContent = md;
  }
  if (searchQuery) {
    const q = document.createElement("div");
    q.className = "searched-for";
    q.textContent = `searched: “${searchQuery}”`;
    bubble.appendChild(q);
  }
  if (sources && sources.length) {
    const s = document.createElement("div");
    s.className = "sources";
    const seen = new Set();
    sources.forEach((h, i) => {
      const key = `${h.title}#${h.section}`;
      if (seen.has(key)) return;
      seen.add(key);
      const a = document.createElement("a");
      // titles already self-describe their kind (e.g. "Week 2 Recap",
      // "Week 1 Lesson Plan — ...", "Week 3 Summary Class (video)") — no
      // need for a redundant kind prefix here.
      if (h.kind === "transcript" && h.url) {
        a.href = h.url;
        a.target = "_blank";
        a.rel = "noopener";
      } else {
        a.href = "#";
        a.onclick = (e) => e.preventDefault();
      }
      a.textContent = `[${i + 1}] ${h.title} — ${h.section}`;
      s.appendChild(a);
    });
    bubble.appendChild(s);
  }
  msg.appendChild(bubble);
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return msg;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = chatInput.value.trim();
  if (!q) return;
  chatInput.value = "";
  chatSend.disabled = true;
  addMessage("user", q);
  const thinking = addMessage("assistant", "Retrieving and thinking…");
  thinking.classList.add("thinking");
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, history: chatHistory }),
    });
    if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
    const { answer, sources, search_query } = await r.json();
    thinking.remove();
    addMessage("assistant", answer, sources, search_query);
    chatHistory.push({ role: "user", content: q }, { role: "assistant", content: answer });
    chatHistory = chatHistory.slice(-10);
  } catch (err) {
    thinking.remove();
    addMessage("assistant", `⚠️ ${err.message}`);
  } finally {
    chatSend.disabled = false;
    chatInput.focus();
  }
});

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

/* ── Routing ─────────────────────────────────────────────────────────── */

window.addEventListener("hashchange", () => {
  const id = location.hash.slice(1);
  if (id) showPage(id);
});

(async function init() {
  await loadTree();
  const first = location.hash.slice(1) || (FLAT[0] && FLAT[0].id);
  if (first) showPage(first);
})();
