"""
Live news feed fetcher for the Magnum ecosystem — zero API keys.

Reads data/config/watchlist.json (companies + topics), queries Google News
RSS for each one (free, keyless, publicly documented technique — no
official-newsroom RSS feed was found to actually work: see the _notes
field in watchlist.json for the two guessed feed URLs that turned out to
be dead), and writes a deduplicated, normalized list of news items to
data/raw/news/raw_items.json.

Usage:
    python3 fetch_competitor_news.py

Designed to be run on a schedule (cron / Task Scheduler / GitHub Action)
every 30-60 minutes — not continuously. It's a single pass: fetch, parse,
dedupe, write, exit.

Known, honest limitations (see README section this script is documented
under for the full list):
  - Google News RSS's <link> is a Google redirect URL, not the publisher's
    real URL — confirmed empirically (not just theoretically) by test-
    running this script: Google's redirect isn't a real HTTP 3xx, it's a
    client-side hop, so a plain HEAD-follow-redirects attempt just returns
    the same URL with tracking parameters appended, or nothing. That
    attempt was in an earlier version of this script and was removed after
    that test — resolving the true publisher URL would need a headless
    browser, which is out of scope for a keyless, stdlib-only script. The
    `link` field is still fully clickable for a human reader; it's just
    not the canonical article URL for programmatic use.
  - Google News RSS has no official rate-limit documentation. This script
    is polite by design (one request per company/topic per run, meant to
    run at most every 15-30 minutes) but isn't guaranteed stable long-term
    — if Google changes this endpoint's behavior, this script breaks and
    needs revisiting, same as any scraping-adjacent technique.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "data" / "config" / "watchlist.json"
OUT_PATH = BASE_DIR / "data" / "raw" / "news" / "raw_items.json"

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
USER_AGENT = "Mozilla/5.0 (compatible; MagnumNewsFetcher/1.0; +https://github.com/sheersh-star/frozen_market_stage1)"
REQUEST_TIMEOUT_S = 12
DELAY_BETWEEN_REQUESTS_S = 1.5  # politeness — this is a scraping-adjacent technique, not a documented API


def load_watchlist():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_query_url(query, lang="en-GB", country="GB"):
    params = {"q": query, "hl": lang, "gl": country, "ceid": f"{country}:{lang.split('-')[0]}"}
    return f"{GOOGLE_NEWS_RSS}?{urllib.parse.urlencode(params)}"


def fetch_xml(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
        return resp.read()


def domain_of(url):
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return re.sub(r"^www\.", "", netloc)
    except Exception:
        return ""


def parse_pubdate(raw):
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def parse_feed(xml_bytes, matched_label, matched_type):
    items = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return items

    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        guid_el = item.find("guid")
        pubdate_el = item.find("pubDate")
        source_el = item.find("source")

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        guid = (guid_el.text or "").strip() if guid_el is not None else link
        published = parse_pubdate(pubdate_el.text if pubdate_el is not None else None)

        source_name = (source_el.text or "").strip() if source_el is not None else ""
        source_url = source_el.get("url", "") if source_el is not None else ""

        # Google appends " - Source Name" to the title; strip it since <source> already has this cleanly
        if source_name and title.endswith(f" - {source_name}"):
            title = title[: -(len(source_name) + 3)].strip()

        if not title or not link:
            continue

        items.append({
            "guid": guid,
            "title": title,
            "link": link,
            "link_type": "google_news_redirect",
            "published": published,
            "source_name": source_name,
            "source_domain": domain_of(source_url) if source_url else "",
            "matched_entities": [matched_label] if matched_type == "company" else [],
            "matched_topics": [matched_label] if matched_type == "topic" else [],
        })
    return items


def dedupe_and_merge(all_items):
    by_guid = {}
    for it in all_items:
        key = it["guid"] or it["link"]
        if key in by_guid:
            existing = by_guid[key]
            for field in ("matched_entities", "matched_topics"):
                for v in it[field]:
                    if v not in existing[field]:
                        existing[field].append(v)
        else:
            by_guid[key] = it
    return list(by_guid.values())


def tag_source_type(item, companies):
    """official if this item's source_domain matches a known official_domain
    for ANY matched entity; aggregator otherwise. Independent of whether the
    item was found via a company query or a topic query — a topic-query hit
    from a company's own domain is still 'official'."""
    if not item["source_domain"]:
        item["source_type"] = "unknown"
        return
    for c in companies:
        for od in c.get("official_domains", []):
            if od in item["source_domain"]:
                item["source_type"] = "official"
                return
    item["source_type"] = "aggregator"


def main():
    watchlist = load_watchlist()
    companies = watchlist["companies"]
    topics = watchlist["topics"]

    all_items = []
    errors = []

    queries = [(c["name"], c["query"], "company") for c in companies] + \
              [(t["name"], t["query"], "topic") for t in topics]

    for label, query, qtype in queries:
        url = build_query_url(query)
        try:
            xml_bytes = fetch_xml(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            errors.append({"label": label, "query": query, "error": str(e)})
            time.sleep(DELAY_BETWEEN_REQUESTS_S)
            continue
        items = parse_feed(xml_bytes, label, qtype)
        all_items.extend(items)
        time.sleep(DELAY_BETWEEN_REQUESTS_S)

    merged = dedupe_and_merge(all_items)
    for item in merged:
        tag_source_type(item, companies)

    merged.sort(key=lambda it: it["published"] or "", reverse=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "watchlist_companies": [c["name"] for c in companies],
        "watchlist_topics": [t["name"] for t in topics],
        "query_errors": errors,
        "items": merged,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    official_count = sum(1 for it in merged if it["source_type"] == "official")
    print(f"Wrote {OUT_PATH}")
    print(f"  {len(merged)} unique items ({official_count} from official domains)")
    print(f"  {len(errors)} query errors" + (f": {errors}" if errors else ""))


if __name__ == "__main__":
    main()
