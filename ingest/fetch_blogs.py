"""Fetch and clean the AI-Agents-course blog posts listed in
config.AGENTS_BLOG_SOURCES into content/sources/agents_blogs/.

Writes one text file per blog to content/sources/agents_blogs/{slug}.txt.
ingest/index_sources.py then chunks and indexes it under the ai_agents course.

Skips a blog whose .txt already exists — pass --force to refetch everything.

Run:  python -m ingest.fetch_blogs [--force]
"""

import argparse
from html.parser import HTMLParser

import requests

from app import config

SKIP_TAGS = {"script", "style", "nav", "header", "footer", "svg", "noscript"}


class TextExtractor(HTMLParser):
    """Minimal HTML-to-text extractor (stdlib only, no bs4/trafilatura dep)."""

    def __init__(self):
        super().__init__()
        self.chunks = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif tag in ("br", "p", "div", "li", "h1", "h2", "h3", "h4"):
            self.chunks.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth and data.strip():
            self.chunks.append(data.strip())

    def text(self):
        raw = " ".join(self.chunks).replace(" \n ", "\n")
        lines = [ln.strip() for ln in raw.splitlines()]
        return "\n".join(ln for ln in lines if ln)


def fetch_one(source, out_dir, force=False):
    """Fetch one blog post into out_dir/{slug}.txt.

    Returns
    -------
    bool
        True if a file was written, False if skipped (already exists).
    """
    out_path = out_dir / f"{source['slug']}.txt"
    if not force and out_path.exists():
        return False

    resp = requests.get(source["url"], timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    if source["url"].endswith(("/raw", ".md", ".txt")) or "gist.github.com" in source["url"]:
        # gists render as HTML pages by default; fetch the raw markdown instead.
        raw_url = source["url"].rstrip("/") + "/raw"
        resp = requests.get(raw_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        body = resp.text
    else:
        extractor = TextExtractor()
        extractor.feed(resp.text)
        body = extractor.text()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"{source['title']}\n{source['url']}\n\n{body}")
    print(f"  {source['slug']}: {len(body)} chars -> {out_path.relative_to(config.ROOT)}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-fetch even if already saved")
    args = parser.parse_args()

    written = sum(
        fetch_one(source, config.AGENTS_BLOGS_TEXT_DIR, force=args.force)
        for source in config.AGENTS_BLOG_SOURCES
    )
    print(f"\n{written} blog(s) fetched (others already saved).")
    if written:
        print("Next: python -m ingest.index_sources")


if __name__ == "__main__":
    main()
