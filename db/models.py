import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum as SAEnum, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class CompanyType(str, enum.Enum):
    ASX200     = "ASX200"
    MNC        = "MNC"
    GOVERNMENT = "GOVERNMENT"


class ScrapingStatus(str, enum.Enum):
    PENDING   = "pending"
    SUCCESS   = "success"
    FAILED    = "failed"
    NOT_FOUND = "not_found"


class Company(Base):
    __tablename__ = "companies"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(255), nullable=False, unique=True)
    website      = Column(String(512), nullable=False)
    sector       = Column(String(128), nullable=True)
    company_type = Column(SAEnum(CompanyType), nullable=False)
    asx_code     = Column(String(10), nullable=True)

    policy = relationship(
        "PrivacyPolicy",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )


class PrivacyPolicy(Base):
    __tablename__ = "privacy_policies"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    company_id      = Column(Integer, ForeignKey("companies.id"), nullable=False, unique=True)
    url             = Column(String(1024), nullable=True)
    content_type    = Column(String(10), nullable=True)
    html_path       = Column(String(512), nullable=True)
    screenshot_path = Column(String(512), nullable=True)
    pdf_path        = Column(String(512), nullable=True)
    text_path       = Column(String(512), nullable=True)
    extracted_text  = Column(Text, nullable=True)
    status          = Column(
        SAEnum(ScrapingStatus),
        nullable=False,
        default=ScrapingStatus.PENDING,
    )
    error_message   = Column(Text, nullable=True)
    scraped_at      = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="policy")
