import logging
from pathlib import Path
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

_STRIP_TAGS = ["script", "style", "nav", "header", "footer", "noscript", "iframe", "svg"]


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.find_all(_STRIP_TAGS):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # collapse excessive blank lines
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def extract_text_from_pdf(pdf_path: Path) -> str:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages)
    except Exception as exc:
        log.error(f"PDF extraction failed for {pdf_path}: {exc}")
        return ""
