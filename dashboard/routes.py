from pathlib import Path
from flask import Blueprint, render_template, abort, Response, send_file, request, jsonify
import config
from db.models import Company, PrivacyPolicy, ScrapingStatus, CompanyType
from db.session import get_session
from sqlalchemy.orm import joinedload

bp = Blueprint("main", __name__)


def _status_counts(session):
    counts = {s.value: 0 for s in ScrapingStatus}
    counts["total"] = session.query(Company).count()
    for status in ScrapingStatus:
        counts[status.value] = (
            session.query(PrivacyPolicy)
            .filter(PrivacyPolicy.status == status)
            .count()
        )
    counts["pending"] = counts["total"] - sum(
        counts[s.value] for s in ScrapingStatus if s != ScrapingStatus.PENDING
    )
    return counts


@bp.route("/")
def index():
    type_filter = request.args.get("type", "ALL").upper()
    with get_session() as session:
        query = session.query(Company)
        if type_filter != "ALL":
            try:
                query = query.filter(Company.company_type == CompanyType(type_filter))
            except ValueError:
                pass
        companies = (
            query
            .options(joinedload(Company.policy))
            .order_by(Company.company_type, Company.name)
            .all()
        )
        rows = [(c, c.policy) for c in companies]
        counts = _status_counts(session)
        return render_template(
            "index.html",
            rows=rows,
            counts=counts,
            type_filter=type_filter,
            company_types=["ALL"] + [t.value for t in CompanyType],
        )


@bp.route("/company/<int:company_id>")
def company_detail(company_id: int):
    with get_session() as session:
        company = (
            session.query(Company)
            .options(joinedload(Company.policy))
            .filter(Company.id == company_id)
            .first()
        )
        if not company:
            abort(404)
        policy = company.policy
        return render_template("company.html", company=company, policy=policy)


@bp.route("/company/<int:company_id>/raw")
def company_raw(company_id: int):
    with get_session() as session:
        company = session.get(Company, company_id)
        if not company or not company.policy or not company.policy.html_path:
            abort(404)
        path = config.STORAGE_DIR / company.policy.html_path
        if not path.exists():
            abort(404)
        return Response(path.read_text(encoding="utf-8", errors="replace"), mimetype="text/html")


@bp.route("/company/<int:company_id>/screenshot")
def company_screenshot(company_id: int):
    with get_session() as session:
        company = session.get(Company, company_id)
        if not company or not company.policy or not company.policy.screenshot_path:
            abort(404)
        path = config.STORAGE_DIR / company.policy.screenshot_path
        if not path.exists():
            abort(404)
        return send_file(path, mimetype="image/png")


@bp.route("/company/<int:company_id>/pdf")
def company_pdf(company_id: int):
    with get_session() as session:
        company = session.get(Company, company_id)
        if not company or not company.policy or not company.policy.pdf_path:
            abort(404)
        path = config.STORAGE_DIR / company.policy.pdf_path
        if not path.exists():
            abort(404)
        return send_file(path, mimetype="application/pdf")


@bp.route("/company/<int:company_id>/text")
def company_text(company_id: int):
    with get_session() as session:
        company = session.get(Company, company_id)
        if not company or not company.policy or not company.policy.text_path:
            abort(404)
        path = config.STORAGE_DIR / company.policy.text_path
        if not path.exists():
            abort(404)
        return Response(
            path.read_text(encoding="utf-8", errors="replace"),
            mimetype="text/plain; charset=utf-8",
        )


@bp.route("/api/status")
def api_status():
    with get_session() as session:
        counts = _status_counts(session)
        return jsonify(counts)
