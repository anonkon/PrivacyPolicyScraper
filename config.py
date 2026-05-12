from pathlib import Path

BASE_DIR    = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
DB_PATH     = BASE_DIR / "data" / "db" / "privacy_scraper.db"
OUTPUT_DIR  = BASE_DIR / "data" / "output"

REQUEST_TIMEOUT = 15
HEAD_TIMEOUT    = 6
MAX_RETRIES     = 1

FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

ENABLE_GOOGLE_FALLBACK = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

PRIVACY_URL_PATTERNS = [
    "/privacy",
    "/privacy-policy",
    "/privacy-statement",
    "/privacy-notice",
    "/legal/privacy",
    "/legal/privacy-policy",
    "/legal/privacy-statement",
    "/about/privacy",
    "/about-us/privacy",
    "/policies/privacy",
    "/policy/privacy",
    "/help/privacy",
    "/support/privacy",
    "/en/privacy",
    "/en-au/privacy",
    "/au/privacy",
    "/terms/privacy",
    "/info/privacy",
    "/security/privacy",
    "/company/privacy",
    "/our-policies/privacy",
    "/privacy-and-security",
    "/data-privacy",
    "/data-protection",
]

KNOWN_POLICY_HOSTS = {
    "privacyportal.onetrust.com",
    "app.onetrust.com",
    "www.iubenda.com",
    "termly.io",
    "app.termly.io",
}
