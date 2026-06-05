"""Curated Salesforce-adjacent KB scraper.

Polite-fetches a hand-maintained list of URLs (URLS below), parses the HTML,
converts the main content to markdown, and writes each page to
``rag/knowledge_base/scraped/<slug>.md`` with a YAML frontmatter header
(``source_url``, ``scraped_at``, ``title``). Failures (non-200, JS-rendered
SPAs, non-HTML content) are logged to ``data/scrape_failures.json`` so you
can review and iterate the URL list.

The retriever (``rag.retrieval.build_index``) picks up scraped files
automatically via its recursive glob, so once this script runs the new docs
participate in BM25 retrieval on the next query.

Run::

    uv run python scripts/scrape_salesforce_kb.py            # all URLs
    uv run python scripts/scrape_salesforce_kb.py --limit 3  # smoke-test
    uv run python scripts/scrape_salesforce_kb.py --force    # overwrite

Edit the ``URLS`` list below to add or remove sources.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

REPO_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = REPO_ROOT / "rag" / "knowledge_base" / "scraped"
FAILURES_PATH = REPO_ROOT / "data" / "scrape_failures.json"

USER_AGENT = (
    "mgt449-sdr-kt-agent (educational scrape; non-commercial; UCSD class project)"
)
DELAY_SECONDS = 1.0
TIMEOUT = 15
MIN_BODY_CHARS = 500  # below this we assume the page is JS-rendered

# Curated seed URLs. Edit to add or remove sources. The scraper handles
# failures gracefully — non-200, JS-rendered, or short-body pages are logged
# to data/scrape_failures.json so you can review and iterate.
URLS: list[str] = [
    # Sales methodologies + qualification frameworks (Wikipedia — static, stable)
    "https://en.wikipedia.org/wiki/MEDDIC",
    "https://en.wikipedia.org/wiki/SPIN_selling",
    "https://en.wikipedia.org/wiki/BANT",
    "https://en.wikipedia.org/wiki/Cold_calling",
    "https://en.wikipedia.org/wiki/Sales_development_representative",
    "https://en.wikipedia.org/wiki/Solution_selling",
    "https://en.wikipedia.org/wiki/Customer_relationship_management",
    "https://en.wikipedia.org/wiki/Salesforce",
    "https://en.wikipedia.org/wiki/Lead_generation",
    "https://en.wikipedia.org/wiki/Sales_process_engineering",
    "https://en.wikipedia.org/wiki/Sales_qualification",
    # Salesforce.com sales-resource pages (may be JS — failures get logged)
    "https://www.salesforce.com/sales/engagement-platform/what-is-sdr/",
    "https://www.salesforce.com/sales/sales-development/sales-development-representative/",
    "https://www.salesforce.com/sales/engagement-platform/cold-calling/",
    "https://www.salesforce.com/sales/sales-development/sales-cadence/",
    "https://www.salesforce.com/sales/objection-handling/",
    # Trailhead modules referenced in trailhead_module_catalog.md (likely JS — best-effort)
    "https://trailhead.salesforce.com/content/learn/modules/sales-cloud-basics",
    "https://trailhead.salesforce.com/content/learn/modules/service-cloud-basics",
]


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", (text or "").lower())
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:80] or "untitled"


def extract_title(soup: BeautifulSoup, fallback: str) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    if h1 and h1.text:
        return h1.text.strip()
    return fallback


def extract_body_html(soup: BeautifulSoup) -> str:
    """Drop chrome (nav/footer/scripts) and keep the main content tag."""
    for tag in soup(
        ["script", "style", "nav", "footer", "header", "noscript", "form", "aside"]
    ):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return str(main)


def fetch_one(url: str) -> tuple[str | None, str | None, str | None]:
    """Return ``(markdown, title, error)``. Exactly one of markdown/error is set."""
    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=TIMEOUT,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        return None, None, f"request_error: {exc}"
    if r.status_code != 200:
        return None, None, f"http_{r.status_code}"
    content_type = r.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        return None, None, f"non_html_content_type: {content_type}"
    soup = BeautifulSoup(r.text, "html.parser")
    title = extract_title(soup, fallback=url)
    body_html = extract_body_html(soup)
    md = markdownify(body_html, heading_style="ATX").strip()
    if len(md) < MIN_BODY_CHARS:
        return None, title, f"insufficient_content (only {len(md)} chars; likely JS-rendered)"
    return md, title, None


def write_kb_entry(path: Path, *, title: str, url: str, body: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    content = (
        "---\n"
        f"source_url: {url}\n"
        f"scraped_at: {now}\n"
        f"title: {title}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"_Source: {url}_\n\n"
        f"{body}\n"
    )
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scrape curated Salesforce-adjacent docs into rag/knowledge_base/scraped/"
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing scraped files")
    parser.add_argument("--limit", type=int, default=None, help="Stop after N URLs (smoke-test)")
    args = parser.parse_args()

    KB_DIR.mkdir(parents=True, exist_ok=True)
    FAILURES_PATH.parent.mkdir(parents=True, exist_ok=True)

    successes: list[dict] = []
    failures: list[dict] = []

    urls = URLS[: args.limit] if args.limit else URLS
    print(f"Scraping {len(urls)} URLs (delay {DELAY_SECONDS}s)…\n")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}", flush=True)
        try:
            md, title, err = fetch_one(url)
        except Exception as exc:  # noqa: BLE001
            md, title, err = None, None, f"unhandled_exception: {exc}"

        if err:
            print(f"   x  {err}", flush=True)
            failures.append({"url": url, "error": err, "title": title})
            time.sleep(DELAY_SECONDS)
            continue

        slug = slugify(title) if title else slugify(url)
        out_path = KB_DIR / f"{slug}.md"
        if out_path.exists() and not args.force:
            print(f"   .  exists (use --force to overwrite): {out_path.relative_to(REPO_ROOT)}", flush=True)
        else:
            write_kb_entry(out_path, title=title, url=url, body=md)
            print(f"   ok wrote {out_path.relative_to(REPO_ROOT)} ({len(md)} chars)", flush=True)
        successes.append(
            {
                "url": url,
                "title": title,
                "path": str(out_path.relative_to(REPO_ROOT)),
                "chars": len(md),
            }
        )
        time.sleep(DELAY_SECONDS)

    print()
    print(f"Summary: {len(successes)} succeeded, {len(failures)} failed")
    if failures:
        FAILURES_PATH.write_text(json.dumps(failures, indent=2), encoding="utf-8")
        print(f"Failure log: {FAILURES_PATH.relative_to(REPO_ROOT)}")
        for f in failures:
            print(f"  - {f['url']}: {f['error']}")

    return 0 if successes else 1


if __name__ == "__main__":
    raise SystemExit(main())
