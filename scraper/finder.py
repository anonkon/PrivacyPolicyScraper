import re
import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import config
from scraper.fetcher import head_url, fetch_url

log = logging.getLogger(__name__)

_PRIVACY_KEYWORDS = [
    "privacy policy",
    "privacy statement",
    "privacy notice",
    "data protection",
    "personal information",
    "privacy",
]

_FOOTER_CLASS_RE = re.compile(r"footer", re.IGNORECASE)


def _base_url(website: str) -> str:
    p = urlparse(website)
    return f"{p.scheme}://{p.netloc}"


def _is_same_or_known_host(url: str, base: str) -> bool:
    parsed = urlparse(url)
    base_host = urlparse(base).netloc
    if parsed.netloc == base_host:
        return True
    if parsed.netloc in config.KNOWN_POLICY_HOSTS:
        return True
    # allow subdomains of the same base domain
    base_domain = ".".join(base_host.split(".")[-2:])
    return parsed.netloc.endswith(base_domain)


def _is_pdf_url(url: str, response: requests.Response | None = None) -> bool:
    if url.lower().rstrip("?").endswith(".pdf"):
        return True
    if response is not None:
        ct = response.headers.get("Content-Type", "")
        if "application/pdf" in ct:
            return True
    return False


def _probe_patterns(base: str, session: requests.Session) -> str | None:
    for pattern in config.PRIVACY_URL_PATTERNS:
        candidate = base.rstrip("/") + pattern
        r = head_url(candidate, session)
        if r is None:
            continue
        if r.status_code in range(200, 400):
            final_url = r.url
            log.debug(f"Pattern match: {candidate} -> {final_url}")
            return final_url
    return None


def _links_from_soup(soup: BeautifulSoup, base_url: str, session: requests.Session) -> str | None:
    candidate_sets = []

    footer = soup.find("footer")
    if footer:
        candidate_sets.append(footer.find_all("a", href=True))

    for el in soup.find_all(class_=_FOOTER_CLASS_RE):
        candidate_sets.append(el.find_all("a", href=True))
    for el in soup.find_all(id=_FOOTER_CLASS_RE):
        candidate_sets.append(el.find_all("a", href=True))

    for nav in soup.find_all("nav"):
        candidate_sets.append(nav.find_all("a", href=True))

    candidate_sets.append(soup.find_all("a", href=True))

    seen = set()
    for links in candidate_sets:
        for a in links:
            href = a.get("href", "").strip()
            text = a.get_text(strip=True).lower()
            href_lower = href.lower()

            matched = any(kw in text or kw in href_lower for kw in _PRIVACY_KEYWORDS)
            if not matched:
                continue

            full_url = urljoin(base_url, href)
            if full_url in seen:
                continue
            seen.add(full_url)

            if not _is_same_or_known_host(full_url, base_url):
                continue

            log.debug(f"Link candidate: {full_url} (text={a.get_text(strip=True)[:60]})")
            return full_url

    return None


def find_privacy_policy_url(company_website: str, session: requests.Session) -> tuple[str | None, str | None]:
    """
    Returns (url, content_type) where content_type is 'html' or 'pdf', or (None, None).
    """
    base = _base_url(company_website)

    # Phase 1: direct URL probing
    url = _probe_patterns(base, session)
    if url:
        ct = "pdf" if _is_pdf_url(url) else "html"
        return url, ct

    # Phase 2: homepage parsing
    try:
        r = fetch_url(company_website, session)
        soup = BeautifulSoup(r.text, "lxml")
        url = _links_from_soup(soup, company_website, session)
        if url:
            ct = "pdf" if _is_pdf_url(url) else "html"
            return url, ct
    except Exception as exc:
        log.warning(f"Homepage fetch failed for {company_website}: {exc}")

    # Phase 2b: try base URL if company_website had a path
    if base != company_website.rstrip("/"):
        try:
            r = fetch_url(base, session)
            soup = BeautifulSoup(r.text, "lxml")
            url = _links_from_soup(soup, base, session)
            if url:
                ct = "pdf" if _is_pdf_url(url) else "html"
                return url, ct
        except Exception:
            pass

    return None, None
