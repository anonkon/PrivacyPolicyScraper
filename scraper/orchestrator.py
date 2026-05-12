import logging
from datetime import datetime
from pathlib import Path
from slugify import slugify

import config
from db.models import Company, PrivacyPolicy, ScrapingStatus, CompanyType
from db.session import get_session
from db.seeder import load_seeds
from scraper.fetcher import make_session, fetch_url
from scraper.finder import find_privacy_policy_url
from scraper.extractor import extract_text_from_html, extract_text_from_pdf
from scraper.screenshot import take_screenshot

log = logging.getLogger(__name__)

_TEXT_LIMIT = 200_000


def _get_or_create_policy(session, company: Company) -> PrivacyPolicy:
    if company.policy:
        return company.policy
    policy = PrivacyPolicy(company_id=company.id, status=ScrapingStatus.PENDING)
    session.add(policy)
    session.flush()
    return policy


def scrape_company(company: Company, session, http_session, browser=None, force: bool = False) -> None:
    policy = _get_or_create_policy(session, company)

    if policy.status == ScrapingStatus.SUCCESS and not force:
        log.info(f"[SKIP]  {company.name}")
        return

    log.info(f"[START] {company.name} ({company.website})")

    try:
        url, content_type = find_privacy_policy_url(company.website, http_session)

        if not url:
            policy.status     = ScrapingStatus.NOT_FOUND
            policy.scraped_at = datetime.utcnow()
            session.commit()
            log.warning(f"[NOT FOUND] {company.name}")
            return

        slug        = slugify(company.name)
        company_dir = config.STORAGE_DIR / "companies" / slug
        company_dir.mkdir(parents=True, exist_ok=True)

        if content_type == "pdf":
            _scrape_pdf(policy, url, company_dir, session, http_session)
        else:
            _scrape_html(policy, url, company_dir, session, http_session, browser=browser)

        log.info(f"[OK]    {company.name} -> {url}")

    except BaseException as exc:
        # BaseException catches KeyboardInterrupt too — re-raise those
        if isinstance(exc, KeyboardInterrupt):
            raise
        try:
            policy.status        = ScrapingStatus.FAILED
            policy.error_message = str(exc)[:1024]
            policy.scraped_at    = datetime.utcnow()
            session.commit()
        except Exception:
            pass
        log.error(f"[FAIL]  {company.name}: {exc}")


def _scrape_html(policy: PrivacyPolicy, url: str, company_dir: Path, session, http_session, browser=None) -> None:
    response  = fetch_url(url, http_session)
    html      = response.text
    html_path = company_dir / "privacy_policy.html"
    html_path.write_text(html, encoding="utf-8", errors="replace")

    text      = extract_text_from_html(html)
    text_path = company_dir / "extracted_text.txt"
    text_path.write_text(text, encoding="utf-8", errors="replace")

    shot_path = company_dir / "screenshot.png"
    take_screenshot(url, shot_path, browser=browser)

    policy.url             = url
    policy.content_type    = "html"
    policy.html_path       = str(html_path.relative_to(config.STORAGE_DIR))
    policy.text_path       = str(text_path.relative_to(config.STORAGE_DIR))
    policy.screenshot_path = str(shot_path.relative_to(config.STORAGE_DIR)) if shot_path.exists() else None
    policy.extracted_text  = text[:_TEXT_LIMIT]
    policy.status          = ScrapingStatus.SUCCESS
    policy.error_message   = None
    policy.scraped_at      = datetime.utcnow()
    session.commit()


def _scrape_pdf(policy: PrivacyPolicy, url: str, company_dir: Path, session, http_session) -> None:
    response = fetch_url(url, http_session)
    pdf_path = company_dir / "privacy_policy.pdf"
    pdf_path.write_bytes(response.content)

    text      = extract_text_from_pdf(pdf_path)
    text_path = company_dir / "extracted_text.txt"
    text_path.write_text(text, encoding="utf-8", errors="replace")

    policy.url            = url
    policy.content_type   = "pdf"
    policy.pdf_path       = str(pdf_path.relative_to(config.STORAGE_DIR))
    policy.text_path      = str(text_path.relative_to(config.STORAGE_DIR))
    policy.extracted_text = text[:_TEXT_LIMIT]
    policy.status         = ScrapingStatus.SUCCESS
    policy.error_message  = None
    policy.scraped_at     = datetime.utcnow()
    session.commit()


def _make_browser():
    try:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        browser = pw.chromium.launch(headless=True)
        return pw, browser
    except Exception as exc:
        log.error(f"Failed to launch Playwright browser: {exc}")
        return None, None


def run_scrape(
    company_type: str | None = None,
    company_filter: str | None = None,
    force: bool = False,
) -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    pw, browser = _make_browser()

    try:
        with get_session() as session:
            load_seeds(session)

            query = session.query(Company)

            if company_type:
                try:
                    ctype = CompanyType(company_type.upper())
                    query = query.filter(Company.company_type == ctype)
                except ValueError:
                    log.error(f"Unknown company type: {company_type}")
                    return

            if company_filter:
                cf = company_filter.strip()
                query = query.filter(
                    (Company.name.ilike(f"%{cf}%")) |
                    (Company.asx_code == cf.upper())
                )

            companies = query.order_by(Company.name).all()
            log.info(f"Scraping {len(companies)} companies (force={force})")

            http_session = make_session()
            counts = {"success": 0, "failed": 0, "not_found": 0, "skipped": 0}

            for i, company in enumerate(companies, 1):
                # Restart browser every 50 companies to prevent memory buildup
                if browser and i > 1 and (i - 1) % 50 == 0:
                    log.info(f"Restarting browser at company {i} to free memory...")
                    try:
                        browser.close()
                        pw.stop()
                    except Exception:
                        pass
                    pw, browser = _make_browser()

                prev_status = company.policy.status if company.policy else None
                scrape_company(company, session, http_session, browser=browser, force=force)

                new_status = company.policy.status if company.policy else None
                if new_status == ScrapingStatus.SUCCESS:
                    if prev_status == ScrapingStatus.SUCCESS and not force:
                        counts["skipped"] += 1
                    else:
                        counts["success"] += 1
                elif new_status == ScrapingStatus.FAILED:
                    counts["failed"] += 1
                elif new_status == ScrapingStatus.NOT_FOUND:
                    counts["not_found"] += 1

                if i % 10 == 0:
                    log.info(
                        f"Progress: {i}/{len(companies)} — "
                        f"success={counts['success']} failed={counts['failed']} "
                        f"not_found={counts['not_found']} skipped={counts['skipped']}"
                    )

        log.info(
            f"Run complete — success: {counts['success']}, "
            f"failed: {counts['failed']}, "
            f"not_found: {counts['not_found']}, "
            f"skipped: {counts['skipped']}"
        )

    finally:
        try:
            if browser:
                browser.close()
            if pw:
                pw.stop()
        except Exception:
            pass
