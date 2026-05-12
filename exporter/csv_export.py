import logging
import pandas as pd
from sqlalchemy import text
import config
from db.session import get_session, _engine

log = logging.getLogger(__name__)


def export_all() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with _engine.connect() as conn:
        companies_df = pd.read_sql(
            text("""
                SELECT
                    c.id,
                    c.name,
                    c.website,
                    c.sector,
                    c.company_type,
                    c.asx_code,
                    p.status        AS policy_status,
                    p.url           AS policy_url,
                    p.content_type,
                    p.scraped_at
                FROM companies c
                LEFT JOIN privacy_policies p ON p.company_id = c.id
                ORDER BY c.company_type, c.name
            """),
            conn,
        )

        policies_df = pd.read_sql(
            text("""
                SELECT
                    p.id            AS policy_id,
                    c.name          AS company_name,
                    c.company_type,
                    c.asx_code,
                    p.url,
                    p.content_type,
                    p.status,
                    p.scraped_at,
                    p.extracted_text
                FROM privacy_policies p
                JOIN companies c ON c.id = p.company_id
                ORDER BY c.company_type, c.name
            """),
            conn,
        )

    companies_path = config.OUTPUT_DIR / "companies.csv"
    policies_path  = config.OUTPUT_DIR / "privacy_policies.csv"

    companies_df.to_csv(companies_path, index=False, encoding="utf-8-sig")
    policies_df.to_csv(policies_path,   index=False, encoding="utf-8-sig")

    log.info(f"Exported {len(companies_df)} companies -> {companies_path}")
    log.info(f"Exported {len(policies_df)} policies  -> {policies_path}")
