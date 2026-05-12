import logging
from db.models import Company, CompanyType
from data.seeds.asx200 import ASX200_COMPANIES
from data.seeds.mnc import MNC_COMPANIES
from data.seeds.government import GOVERNMENT_ENTITIES

log = logging.getLogger(__name__)


def load_seeds(session) -> int:
    all_seeds = (
        [(c, CompanyType.ASX200)     for c in ASX200_COMPANIES] +
        [(c, CompanyType.MNC)        for c in MNC_COMPANIES] +
        [(c, CompanyType.GOVERNMENT) for c in GOVERNMENT_ENTITIES]
    )

    # Load all existing names in one query to avoid N+1 and mid-loop autoflush
    existing_names = {
        row[0] for row in session.query(Company.name).all()
    }

    added = 0
    for seed, ctype in all_seeds:
        if seed["name"] in existing_names:
            continue
        session.add(Company(
            name         = seed["name"],
            website      = seed["website"],
            sector       = seed.get("sector"),
            company_type = ctype,
            asx_code     = seed.get("asx_code"),
        ))
        added += 1

    session.flush()
    total = session.query(Company).count()
    log.info(f"Seed complete: {total} companies in DB ({added} new)")
    return added
