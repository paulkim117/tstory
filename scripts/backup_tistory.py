#!/usr/bin/env python3
"""Back up public numeric Tistory posts using only Python's standard library."""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import os
import random
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BLOG_BASE_URL = "https://mystock-note.tistory.com"
SITEMAP_URL = f"{BLOG_BASE_URL}/sitemap.xml"
RSS_URL = f"{BLOG_BASE_URL}/rss"
NUMERIC_POST_URL_RE = re.compile(r"^https://mystock-note\.tistory\.com/\d+$")
REQUEST_TIMEOUT_SECONDS = 15
REQUEST_SLEEP_RANGE_SECONDS = (0.5, 1.0)
MAX_POSTS_PER_RUN = int(os.environ.get("TISTORY_BACKUP_MAX_POSTS", "250"))
USER_AGENT = (
    "Mozilla/5.0 (compatible; TistoryBackupBot/1.0; "
    "+https://github.com/paulkim117/tstory)"
)

# This MVP intentionally uses regex-based extraction instead of a full DOM parser.
# Regex cannot perfectly match deeply nested div trees, but these patterns target the
# most common Tistory public article containers and keep the script dependency-free.
ARTICLE_PATTERNS = [
    r"<article\b[^>]*>(.*?)</article>",
    r"<div\b[^>]*class=[\"'][^\"']*article-view[^\"']*[\"'][^>]*>(.*?)</div>",
    r"<div\b[^>]*class=[\"'][^\"']*entry-content[^\"']*[\"'][^>]*>(.*?)</div>",
    r"<div\b[^>]*class=[\"'][^\"']*contents_style[^\"']*[\"'][^>]*>(.*?)</div>",
    r"<div\b[^>]*class=[\"'][^\"']*tt_article_useless_p_margin[^\"']*[\"'][^>]*>(.*?)</div>",
    r"<div\b[^>]*id=[\"']content[\"'][^>]*>(.*?)</div>",
]

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "posts"
SCHEMAS_DIR = ROOT / "schemas"
METADATA_DIR = ROOT / "metadata"
LOGS_DIR = ROOT / "logs"
HISTORY_DIR = LOGS_DIR / "history"


@dataclass
class FetchResult:
    url: str
    status_code: int | None
    text: str = ""
    error: str = ""


@dataclass
class PostBackup:
    post_id: str
    url: str
    title: str
    canonical_url: str
    meta_description: str
    og_title: str
    og_description: str
    published_time: str
    modified_time: str
    body_html: str
    parsed_json_ld: list[Any]
    raw_invalid_json_ld: list[str]
    notes: list[Any] = field(default_factory=list)


@dataclass
class BackupStats:
    run_date: str
    source: str = ""
    total_urls_found: int = 0
    numeric_post_urls: int = 0
    successfully_backed_up: int = 0
    skipped_unchanged: int = 0
    updated: int = 0
    failed: int = 0
    failed_urls: list[tuple[str, str, str]] = field(default_factory=list)


class HeadMetadataParser(HTMLParser):
    """Small stdlib HTML parser for title, meta, canonical, and time tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta: dict[tuple[str, str], str] = {}
        self.canonical_url = ""
        self.time_values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        tag_lower = tag.lower()
        if tag_lower == "title":
            self.in_title = True
        elif tag_lower == "meta":
            content = html_lib.unescape(attrs_dict.get("content", "")).strip()
            for key_attr in ("name", "property"):
                key_value = attrs_dict.get(key_attr, "").strip().lower()
                if key_value and content:
                    self.meta[(key_attr, key_value)] = content
        elif tag_lower == "link":
            rel_values = {part.strip().lower() for part in attrs_dict.get("rel", "").split()}
            if "canonical" in rel_values and attrs_dict.get("href"):
                self.canonical_url = html_lib.unescape(attrs_dict["href"]).strip()
        elif tag_lower == "time":
            value = attrs_dict.get("datetime", "").strip()
            if value:
                self.time_values.append(html_lib.unescape(value))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return html_lib.unescape("".join(self.title_parts)).strip()


def ensure_directories() -> None:
    for directory in [POSTS_DIR, SCHEMAS_DIR, METADATA_DIR, LOGS_DIR, HISTORY_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def fetch_url(url: str, timeout: int = REQUEST_TIMEOUT_SECONDS) -> FetchResult:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:  # noqa: S310 - public fixed URLs only.
            status = response.getcode()
            charset = response.headers.get_content_charset() or "utf-8"
            body = response.read().decode(charset, errors="replace")
            if status != 200:
                return FetchResult(url=url, status_code=status, error=f"HTTP {status}")
            return FetchResult(url=url, status_code=status, text=body)
    except HTTPError as exc:
        return FetchResult(url=url, status_code=exc.code, error=str(exc))
    except URLError as exc:
        return FetchResult(url=url, status_code=None, error=str(exc))
    except Exception as exc:  # noqa: BLE001 - report unexpected network/runtime failures safely.
        return FetchResult(url=url, status_code=None, error=str(exc))


def normalize_post_url(url: str) -> str:
    parsed = urlparse(url.strip())
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def is_numeric_post_url(url: str) -> bool:
    return bool(NUMERIC_POST_URL_RE.match(normalize_post_url(url)))


def extract_locs_from_sitemap(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    urls: list[str] = []
    for elem in root.iter():
        if elem.tag.endswith("loc") and elem.text:
            urls.append(elem.text.strip())
    return urls


def extract_links_from_rss(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    links: list[str] = []
    for elem in root.iter():
        if elem.tag.endswith("link") and elem.text:
            link = elem.text.strip()
            if link.startswith(f"{BLOG_BASE_URL}/"):
                links.append(link)
    return links


def discover_post_urls() -> tuple[str, list[str], list[str]]:
    sitemap_url = os.environ.get("TISTORY_SITEMAP_URL", SITEMAP_URL)
    sitemap_result = fetch_url(sitemap_url)
    if sitemap_result.status_code == 200 and sitemap_result.text:
        try:
            all_urls = extract_locs_from_sitemap(sitemap_result.text)
            return "sitemap.xml", all_urls, filter_numeric_urls(all_urls)
        except ET.ParseError as exc:
            sitemap_result.error = f"sitemap XML parse failed: {exc}"

    rss_url = os.environ.get("TISTORY_RSS_URL", RSS_URL)
    rss_result = fetch_url(rss_url)
    if rss_result.status_code == 200 and rss_result.text:
        try:
            all_urls = extract_links_from_rss(rss_result.text)
            return "rss", all_urls, filter_numeric_urls(all_urls)
        except ET.ParseError as exc:
            rss_result.error = f"rss XML parse failed: {exc}"

    errors = [
        f"sitemap: {sitemap_result.error or sitemap_result.status_code}",
        f"rss: {rss_result.error or rss_result.status_code}",
    ]
    raise RuntimeError("URL discovery failed (" + "; ".join(errors) + ")")


def filter_numeric_urls(urls: list[str]) -> list[str]:
    numeric_urls = {normalize_post_url(url) for url in urls if is_numeric_post_url(url)}
    return sorted(numeric_urls, key=lambda value: int(value.rsplit("/", 1)[-1]))[:MAX_POSTS_PER_RUN]


def parse_head_metadata(html_text: str) -> HeadMetadataParser:
    parser = HeadMetadataParser()
    parser.feed(html_text)
    parser.close()
    return parser


def extract_title(html_text: str) -> str:
    parser = parse_head_metadata(html_text)
    og_title = parser.meta.get(("property", "og:title"), "")
    return og_title or parser.title


def extract_meta_content(html_text: str, key: str, attr_name: str = "name") -> str:
    parser = parse_head_metadata(html_text)
    return parser.meta.get((attr_name.lower(), key.lower()), "")


def extract_canonical(html_text: str) -> str:
    return parse_head_metadata(html_text).canonical_url


def extract_json_ld_blocks(html_text: str) -> list[str]:
    blocks: list[str] = []
    script_pattern = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.IGNORECASE | re.DOTALL)
    for match in script_pattern.finditer(html_text):
        attrs = match.group("attrs")
        if re.search(r"\btype\s*=\s*(['\"])application/ld\+json\1", attrs, flags=re.IGNORECASE):
            blocks.append(html_lib.unescape(match.group("body").strip()))
    return blocks


def extract_json_ld(html_text: str) -> tuple[list[Any], list[str]]:
    parsed_json_ld: list[Any] = []
    invalid_json_ld: list[str] = []
    for raw in extract_json_ld_blocks(html_text):
        if not raw:
            continue
        try:
            parsed_json_ld.append(json.loads(raw))
        except json.JSONDecodeError:
            invalid_json_ld.append(raw)
    return parsed_json_ld, invalid_json_ld


def strip_html_tags(html_text: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", html_text, flags=re.DOTALL)
    return re.sub(r"\s+", " ", html_lib.unescape(without_tags)).strip()


def remove_noise_from_body(body_html: str) -> str:
    cleaned = body_html
    for tag in ["script", "style", "iframe", "noscript", "form"]:
        cleaned = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    noisy_patterns = [
        r"<[^>]*(?:class|id)=[\"'][^\"']*adsbygoogle[^\"']*[\"'][^>]*>.*?</[^>]+>",
        r"<ins\b[^>]*adsbygoogle[^>]*>.*?</ins>",
        r"<div\b[^>]*(?:class|id)=[\"'][^\"']*(?:comment|reply|guestbook)[^\"']*[\"'][^>]*>.*?</div>",
        r"<section\b[^>]*(?:class|id)=[\"'][^\"']*(?:comment|reply|related)[^\"']*[\"'][^>]*>.*?</section>",
        r"<div\b[^>]*(?:class|id)=[\"'][^\"']*(?:related-posts|related_posts|another_category)[^\"']*[\"'][^>]*>.*?</div>",
    ]
    for pattern in noisy_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL)

    cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)
    return cleaned.strip()


def extract_body_html(html_text: str) -> tuple[str, list[str]]:
    candidates: list[tuple[int, str, str]] = []
    notes: list[str] = []
    for pattern in ARTICLE_PATTERNS:
        for match in re.finditer(pattern, html_text, flags=re.IGNORECASE | re.DOTALL):
            body = remove_noise_from_body(match.group(1))
            text_length = len(strip_html_tags(body))
            if text_length >= 80:
                candidates.append((text_length, pattern, body))

    if not candidates:
        notes.append("정규식 본문 후보에서 의미 있는 본문을 찾지 못했습니다.")
        return "", notes

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, pattern, body = candidates[0]
    notes.append(f"본문 regex 패턴 선택: {pattern}")
    return body, notes


def extract_time_value(parser: HeadMetadataParser, candidates: list[tuple[str, str]]) -> str:
    for attr_name, attr_value in candidates:
        value = parser.meta.get((attr_name.lower(), attr_value.lower()), "")
        if value:
            return value
    return parser.time_values[0] if parser.time_values else ""


def post_id_from_url(url: str) -> str:
    return normalize_post_url(url).rsplit("/", 1)[-1]


def parse_post(url: str, html_text: str) -> PostBackup:
    parser = parse_head_metadata(html_text)
    parsed_json_ld, invalid_json_ld = extract_json_ld(html_text)
    body_html, body_notes = extract_body_html(html_text)
    published_time = extract_time_value(
        parser,
        [("property", "article:published_time"), ("property", "og:article:published_time"), ("name", "pubdate")],
    )
    modified_time = extract_time_value(
        parser,
        [("property", "article:modified_time"), ("property", "og:updated_time"), ("name", "lastmod")],
    )
    notes: list[Any] = [*body_notes]
    notes.extend({"invalid_json_ld_raw": raw} for raw in invalid_json_ld)
    return PostBackup(
        post_id=post_id_from_url(url),
        url=normalize_post_url(url),
        title=parser.meta.get(("property", "og:title"), "") or parser.title,
        canonical_url=parser.canonical_url,
        meta_description=parser.meta.get(("name", "description"), ""),
        og_title=parser.meta.get(("property", "og:title"), ""),
        og_description=parser.meta.get(("property", "og:description"), ""),
        published_time=published_time,
        modified_time=modified_time,
        body_html=body_html,
        parsed_json_ld=parsed_json_ld,
        raw_invalid_json_ld=invalid_json_ld,
        notes=notes,
    )


def date_parts_for_post(post: PostBackup, run_date: str) -> tuple[str, str]:
    for value in [post.published_time, post.modified_time, run_date]:
        match = re.search(r"(20\d{2})[-/.](\d{1,2})", value)
        if match:
            return match.group(1), f"{int(match.group(2)):02d}"
    return run_date[:4], run_date[5:7]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_text_if_exists(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def write_if_changed(path: Path, content: str) -> bool:
    if read_text_if_exists(path) == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def stable_existing_backup_date(metadata_path: Path, run_date: str, content_hash: str) -> str:
    if not metadata_path.exists():
        return run_date
    try:
        existing = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return run_date
    if existing.get("content_hash") == content_hash:
        return str(existing.get("backup_date") or run_date)
    return run_date


def render_post_html(post: PostBackup, backup_date: str) -> str:
    return f"""<!--
source: {post.url}
backup_date: {backup_date}
post_id: {post.post_id}
-->
{post.body_html}
"""


def render_schema_json(post: PostBackup) -> str:
    schema_payload: Any = post.parsed_json_ld[0] if len(post.parsed_json_ld) == 1 else post.parsed_json_ld
    return json.dumps(schema_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_metadata_json(post: PostBackup, run_date: str, metadata_path: Path, status: str) -> str:
    content_hash = sha256_text(post.body_html)
    backup_date = stable_existing_backup_date(metadata_path, run_date, content_hash)
    metadata = {
        "post_id": post.post_id,
        "url": post.url,
        "canonical_url": post.canonical_url,
        "title": post.title,
        "meta_description": post.meta_description,
        "og_title": post.og_title,
        "og_description": post.og_description,
        "published_time": post.published_time,
        "modified_time": post.modified_time,
        "backup_date": backup_date,
        "source": "tistory_public_html",
        "status": status,
        "json_ld_count": len(post.parsed_json_ld),
        "body_html_length": len(post.body_html),
        "content_hash": content_hash,
        "notes": post.notes,
    }
    return json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def save_post_backup(post: PostBackup, run_date: str) -> tuple[bool, bool]:
    year, month = date_parts_for_post(post, run_date)
    post_path = POSTS_DIR / year / month / f"{post.post_id}.html"
    schema_path = SCHEMAS_DIR / year / month / f"{post.post_id}.schema.json"
    metadata_path = METADATA_DIR / year / month / f"{post.post_id}.metadata.json"

    content_hash = sha256_text(post.body_html)
    backup_date = stable_existing_backup_date(metadata_path, run_date, content_hash)

    changed = False
    if post.body_html:
        changed = write_if_changed(post_path, render_post_html(post, backup_date)) or changed
    if post.parsed_json_ld:
        changed = write_if_changed(schema_path, render_schema_json(post)) or changed

    status = "published" if post.body_html else "body_extract_failed"
    metadata_json = render_metadata_json(post, run_date, metadata_path, status)
    changed = write_if_changed(metadata_path, metadata_json) or changed
    return changed, bool(post.body_html)


def render_report(stats: BackupStats) -> str:
    lines = [
        "# Tistory Backup Report",
        "",
        f"- Run date: {stats.run_date}",
        f"- Source: {stats.source}",
        f"- Total URLs found: {stats.total_urls_found}",
        f"- Numeric post URLs: {stats.numeric_post_urls}",
        f"- Successfully backed up: {stats.successfully_backed_up}",
        f"- Skipped unchanged: {stats.skipped_unchanged}",
        f"- Updated: {stats.updated}",
        f"- Failed: {stats.failed}",
        "",
        "## Failed URLs",
        "",
        "| URL | Status | Reason |",
        "|---|---:|---|",
    ]
    for url, status, reason in stats.failed_urls:
        safe_reason = reason.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {url} | {status} | {safe_reason} |")
    return "\n".join(lines) + "\n"


def write_reports(stats: BackupStats) -> None:
    report = render_report(stats)
    write_if_changed(LOGS_DIR / "latest-backup-report.md", report)
    if stats.failed > 0 or stats.updated > 0:
        write_if_changed(HISTORY_DIR / f"{stats.run_date}.md", report)


def run_backup() -> int:
    ensure_directories()
    run_date = datetime.now(timezone.utc).date().isoformat()
    stats = BackupStats(run_date=run_date)

    try:
        source, all_urls, post_urls = discover_post_urls()
    except RuntimeError as exc:
        stats.source = "unavailable"
        stats.failed = 1
        stats.failed_urls.append((SITEMAP_URL, "N/A", str(exc)))
        write_reports(stats)
        print(render_report(stats))
        print(str(exc), file=sys.stderr)
        return 0

    stats.source = source
    stats.total_urls_found = len(all_urls)
    stats.numeric_post_urls = len(post_urls)

    for index, url in enumerate(post_urls, start=1):
        result = fetch_url(url)
        if result.status_code != 200:
            stats.failed += 1
            stats.failed_urls.append((url, str(result.status_code or "N/A"), result.error or "non-200 response"))
            continue

        try:
            post = parse_post(url, result.text)
            changed, has_body = save_post_backup(post, run_date)
        except Exception as exc:  # noqa: BLE001 - keep one bad public post from aborting the run.
            stats.failed += 1
            stats.failed_urls.append((url, "200", f"parse/save failed: {exc}"))
            continue

        if has_body:
            stats.successfully_backed_up += 1
            if changed:
                stats.updated += 1
            else:
                stats.skipped_unchanged += 1
        else:
            stats.failed += 1
            stats.failed_urls.append((url, "200", "body extraction failed"))

        if index < len(post_urls):
            time.sleep(random.uniform(*REQUEST_SLEEP_RANGE_SECONDS))

    write_reports(stats)
    print(render_report(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_backup())
