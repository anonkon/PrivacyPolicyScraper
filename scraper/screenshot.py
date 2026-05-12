import logging
from pathlib import Path

log = logging.getLogger(__name__)


def take_screenshot(url: str, output_path: Path, browser=None) -> bool:
    """
    Take a full-page screenshot.  Pass a shared Playwright browser to avoid
    spawning a new Chromium process for every company.
    """
    _owns_browser = browser is None
    _pw = None
    try:
        if _owns_browser:
            from playwright.sync_api import sync_playwright
            _pw = sync_playwright().start()
            browser = _pw.chromium.launch(headless=True)

        from playwright.sync_api import TimeoutError as PWTimeout
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(1500)
            page.screenshot(path=str(output_path), full_page=True)
            return True
        except PWTimeout:
            log.warning(f"Screenshot timeout for {url}, trying viewport-only")
            try:
                page.screenshot(path=str(output_path), full_page=False)
                return True
            except Exception:
                return False
        except Exception as exc:
            log.warning(f"Screenshot page error for {url}: {exc}")
            return False
        finally:
            try:
                ctx.close()
            except Exception:
                pass
    except Exception as exc:
        log.error(f"Screenshot failed for {url}: {exc}")
        return False
    finally:
        if _owns_browser:
            try:
                if browser:
                    browser.close()
                if _pw:
                    _pw.stop()
            except Exception:
                pass
