"""
scraper.py — Populate ChromaDB with Salesforce SDR knowledge base content.

Usage:
    cd backend && python scraper.py

Strategy:
    1. Try to scrape each URL with requests + BeautifulSoup.
    2. Salesforce help.salesforce.com and Trailhead pages use the Aura/LWR
       JavaScript framework — the HTTP response is a loading-spinner shell
       with zero article content. When scraping yields 0 chunks, fall back to
       GPT-4o to generate accurate synthetic KB content for that topic.
    3. Chunk all content at ~400 tokens (300 words) with 50-token overlap.
    4. Embed via text-embedding-3-small and store in ChromaDB.
    5. Save raw text to data/raw/ as backup.

Requires:
    OPENAI_API_KEY in .env
    pip install requests beautifulsoup4
"""

from __future__ import annotations

import os
import re
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import anthropic
import requests
from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from embeddings import add_documents

# ── Config ────────────────────────────────────────────────────────────────────

# Each entry: (url, topic_label, subtopics_for_fallback_prompt)
SOURCES: list[dict] = [
    {
        "url": "https://help.salesforce.com/s/articleView?id=sf.sales_core.htm",
        "topic": "Salesforce Sales Cloud — Core Features Overview",
        "subtopics": [
            "What Sales Cloud is and why companies buy it",
            "Key objects: Leads, Contacts, Accounts, Opportunities, Activities",
            "How Sales Cloud fits into the SDR-to-AE handoff workflow",
            "Pipeline management, forecasting, and quota tracking",
            "Common Sales Cloud integrations (Outlook, Slack, Zoom, Gong)",
            "How SDRs use Sales Cloud daily: logging calls, updating stages, creating tasks",
        ],
    },
    {
        "url": "https://trailhead.salesforce.com/content/learn/modules/sales-cloud-basics",
        "topic": "Salesforce Trailhead — Sales Cloud Basics Module",
        "subtopics": [
            "CRM fundamentals and why Salesforce dominates enterprise sales",
            "Navigating the Salesforce Lightning UI as a new SDR",
            "The lead-to-opportunity conversion process step by step",
            "Setting up and using Salesforce email and activity tracking",
            "Creating reports and dashboards to track SDR performance",
            "Salesforce mobile app for SDRs on the go",
        ],
    },
    {
        "url": "https://help.salesforce.com/s/articleView?id=sf.leads_def.htm",
        "topic": "Salesforce Leads — Definition, Management, and SDR Best Practices",
        "subtopics": [
            "What a Lead record is and what fields SDRs must fill out",
            "Lead sources: how inbound vs outbound leads differ",
            "Lead status lifecycle: New → Working → Qualified → Converted → Unqualified",
            "Lead scoring and MQL criteria in enterprise Salesforce orgs",
            "Converting a Lead to Contact + Account + Opportunity",
            "Lead assignment rules, round-robin routing, and territory alignment",
            "Common SDR mistakes when managing leads in Salesforce",
        ],
    },
    {
        "url": "https://help.salesforce.com/s/articleView?id=sf.opportunities_def.htm",
        "topic": "Salesforce Opportunities — Definition, Stages, and SDR-to-AE Handoff",
        "subtopics": [
            "What an Opportunity record is and when SDRs create them",
            "Standard opportunity stages: Prospecting, Qualification, Needs Analysis, Value Proposition, Proposal, Negotiation, Closed Won/Lost",
            "MEDDIC and BANT qualification gates mapped to opportunity stages",
            "Setting close dates, amount, and probability fields correctly",
            "The SDR-to-AE handoff: what must be in the opportunity before passing it",
            "Opportunity contact roles: champion, economic buyer, technical evaluator, gatekeeper",
            "Activity logging on opportunities: call notes, emails, next steps",
        ],
    },
]

WORDS_PER_CHUNK = 300  # ≈ 400 tokens
OVERLAP_WORDS = 40  # ≈ 50 tokens
DELAY_SECONDS = 2
MIN_LINE_LEN = 25

HEADERS = {
    "User-Agent": (
        "SDR-KT-Agent/1.0 (UCSD MGT449 class project; educational use only)"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# ── Anthropic client (lazy) ───────────────────────────────────────────────────

_anthropic_client: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set — check .env")
        _anthropic_client = anthropic.Anthropic(api_key=key)
    return _anthropic_client


# ── Robots.txt ────────────────────────────────────────────────────────────────

_robots_cache: dict[str, RobotFileParser] = {}


def _get_robots(base_url: str) -> RobotFileParser:
    if base_url not in _robots_cache:
        rp = RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        try:
            rp.read()
        except Exception:
            pass
        _robots_cache[base_url] = rp
    return _robots_cache[base_url]


def is_allowed(url: str) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return _get_robots(base).can_fetch("*", url)


# ── Fetching & cleaning ───────────────────────────────────────────────────────

_NOISE_TAGS = [
    "nav",
    "footer",
    "header",
    "aside",
    "script",
    "style",
    "noscript",
    "meta",
    "link",
    "iframe",
    "form",
    "button",
]

_NOISE_PATTERNS = re.compile(
    r"nav|header|footer|breadcrumb|sidebar|menu|cookie|banner|social|promo"
    r"|globalNav|siteforce|topNav|sfdcHeader|aura|loading",
    re.I,
)


def _remove_noise(soup: BeautifulSoup) -> None:
    for tag in list(soup(_NOISE_TAGS)):
        tag.decompose()
    # Snapshot the list first — modifying the tree while iterating causes
    # NoneType errors on already-decomposed element references.
    for el in list(soup.find_all(True)):
        if not isinstance(el, Tag) or el.parent is None:
            continue
        cls = " ".join(el.get("class") or [])
        el_id = el.get("id") or ""
        if _NOISE_PATTERNS.search(cls) or _NOISE_PATTERNS.search(el_id):
            el.decompose()


def fetch_text(url: str, session: requests.Session) -> str:
    resp = session.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    _remove_noise(soup)

    root = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id=re.compile(r"content|main|article", re.I))
        or soup.body
        or soup
    )

    raw = (root or soup).get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines()]
    lines = [ln for ln in lines if ln and len(ln) >= MIN_LINE_LEN]
    return "\n".join(lines)


# ── Claude fallback content generator ────────────────────────────────────────

_FALLBACK_SYSTEM = """\
You are a Salesforce expert writing knowledge base articles for an SDR onboarding system.
Write comprehensive, accurate content that a new Salesforce SDR would study during their
first 30 days. Use clear headings (##), bullet points, and specific actionable guidance.
Include exact Salesforce field names, stage names, and terminology SDRs will encounter on
the job. Write in a direct instructional voice — no marketing language."""


def generate_topic_content(topic: str, subtopics: list[str]) -> str:
    """
    Use claude-sonnet-4-6 to generate ~2000 words of SDR KB content for a topic.
    Called only when web scraping yields no usable content (JS-rendered pages).
    """
    subtopic_list = "\n".join(f"- {s}" for s in subtopics)
    prompt = f"""\
Write a comprehensive 2000-word knowledge base article titled: "{topic}"

Cover all of these subtopics in depth:
{subtopic_list}

Format:
- Use ## for section headings
- Use bullet points for lists of items
- Include specific Salesforce field names, button names, and navigation paths where relevant
- Include at least one concrete example or scenario per section
- End with a "Key Takeaways for New SDRs" summary section

Write the full article now:"""

    response = _get_anthropic().messages.create(
        model="claude-sonnet-4-6",
        system=_FALLBACK_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000,
    )
    return response.content[0].text or ""


# ── Chunking ──────────────────────────────────────────────────────────────────


def chunk_text(
    text: str,
    words_per_chunk: int = WORDS_PER_CHUNK,
    overlap_words: int = OVERLAP_WORDS,
) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap_words
    return chunks


# ── Slug helper ───────────────────────────────────────────────────────────────


def url_to_slug(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}{parsed.query}"
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", raw).strip("_")
    return slug[:80]


# ── Per-source pipeline ───────────────────────────────────────────────────────


def process_source(source: dict, session: requests.Session) -> int:
    """
    Try to scrape a URL. If 0 chunks result (JS-rendered page),
    fall back to GPT-4o to generate synthetic KB content for the topic.
    Returns number of chunks stored.
    """
    url = source["url"]
    topic = source["topic"]
    slug = url_to_slug(url)

    # ── Step 1: attempt web scraping ──────────────────────────────────────
    scraped_text = ""
    if is_allowed(url):
        print(f"  Fetching {url} …")
        try:
            scraped_text = fetch_text(url, session)
        except requests.HTTPError as e:
            print(f"  [http {e.response.status_code}] scraping failed")
        except Exception as e:
            print(f"  [scrape error] {e}")
    else:
        print(f"  [robots.txt] scraping disallowed")

    # ── Step 2: fall back to GPT-4o if scraping yielded nothing ──────────
    if scraped_text.strip():
        text = scraped_text
        source_label = slug
        doc_type = "help_article"
        method = "scraped"
    else:
        print(f"  [fallback] Generating synthetic content via GPT-4o for: {topic}")
        text = generate_topic_content(topic, source["subtopics"])
        source_label = slug
        doc_type = "synthetic_kb"
        method = "gpt-4o"

    if not text.strip():
        print(f"  [warn] No content produced — skipping")
        return 0

    # ── Step 3: save raw backup ───────────────────────────────────────────
    raw_path = RAW_DIR / f"{slug}.txt"
    raw_path.write_text(text, encoding="utf-8")

    # ── Step 4: chunk & ingest ────────────────────────────────────────────
    chunks = chunk_text(text)
    if not chunks:
        print(f"  [warn] Chunking produced 0 chunks")
        return 0

    ids = [f"{slug}_{i}_{uuid.uuid4().hex[:6]}" for i in range(len(chunks))]
    add_documents(
        texts=chunks,
        ids=ids,
        source=source_label,
        doc_type=doc_type,
        extra_metadata={"url": url, "topic": topic, "method": method},
    )

    print(f"  ✓ {len(chunks)} chunks stored  [{method}]  → {raw_path.name}")
    return len(chunks)


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("[error] OPENAI_API_KEY not found — add it to sdr-kt-agent/.env")
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    total_chunks = 0

    for i, source in enumerate(SOURCES):
        print(f"\n[{i + 1}/{len(SOURCES)}] {source['topic']}")
        n = process_source(source, session)
        print(f"  Scraped {n} chunks from {source['url']}")
        total_chunks += n

        if i < len(SOURCES) - 1:
            print(f"  Waiting {DELAY_SECONDS}s …")
            time.sleep(DELAY_SECONDS)

    print(f"\n✓ Done. {total_chunks} total chunks stored in ChromaDB.")
    print(f"  Raw text files saved to: {RAW_DIR}")


if __name__ == "__main__":
    main()
