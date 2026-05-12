import random
import logging
import urllib3
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(config.USER_AGENTS)})
    return session


def make_session() -> requests.Session:
    return _make_session()


@retry(
    stop=stop_after_attempt(config.MAX_RETRIES + 1),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    reraise=True,
)
def fetch_url(url: str, session: requests.Session) -> requests.Response:
    session.headers.update({"User-Agent": random.choice(config.USER_AGENTS)})
    response = session.get(
        url,
        timeout=config.REQUEST_TIMEOUT,
        verify=False,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response


def head_url(url: str, session: requests.Session) -> requests.Response | None:
    try:
        session.headers.update({"User-Agent": random.choice(config.USER_AGENTS)})
        r = session.head(
            url,
            timeout=config.HEAD_TIMEOUT,
            verify=False,
            allow_redirects=True,
        )
        if r.status_code == 405:
            r = session.get(
                url,
                timeout=config.HEAD_TIMEOUT,
                verify=False,
                allow_redirects=True,
                stream=True,
            )
            r.close()
        return r
    except Exception as exc:
        log.debug(f"HEAD failed for {url}: {exc}")
        return None
