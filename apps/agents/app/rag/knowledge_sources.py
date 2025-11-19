"""
Knowledge Base Sources for RAG Population.

This module defines authoritative sources for populating the RAG knowledge base
with tax laws, policies, regulations, and business guidance.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentSource:
    """Represents a knowledge source for RAG ingestion."""

    url: str
    title: str
    category: str  # tax, legal, policy, business
    jurisdiction: str  # US, IN, UK, EU, global
    doc_type: str  # pdf, html, api
    priority: int = 1  # 1=high, 2=medium, 3=low


# US Tax & Policy Sources
US_TAX_SOURCES = [
    DocumentSource(
        url="https://www.irs.gov/pub/irs-pdf/p334.pdf",
        title="IRS Publication 334 - Tax Guide for Small Business",
        category="tax",
        jurisdiction="US",
        doc_type="pdf",
        priority=1,
    ),
    DocumentSource(
        url="https://www.irs.gov/pub/irs-pdf/p535.pdf",
        title="IRS Publication 535 - Business Expenses",
        category="tax",
        jurisdiction="US",
        doc_type="pdf",
        priority=1,
    ),
    DocumentSource(
        url="https://www.irs.gov/pub/irs-pdf/p542.pdf",
        title="IRS Publication 542 - Corporations",
        category="tax",
        jurisdiction="US",
        doc_type="pdf",
        priority=1,
    ),
    DocumentSource(
        url="https://www.irs.gov/pub/irs-pdf/p970.pdf",
        title="IRS Publication 970 - Tax Benefits for Education",
        category="tax",
        jurisdiction="US",
        doc_type="pdf",
        priority=2,
    ),
    DocumentSource(
        url="https://www.irs.gov/businesses/small-businesses-self-employed/business-structures",
        title="IRS Business Structures Guide",
        category="legal",
        jurisdiction="US",
        doc_type="html",
        priority=1,
    ),
]

# India Tax & Policy Sources
INDIA_TAX_SOURCES = [
    DocumentSource(
        url="https://www.incometax.gov.in/iec/foportal/help/individual/return-applicable-1",
        title="Income Tax India - Individual Returns Guide",
        category="tax",
        jurisdiction="IN",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.gst.gov.in/help/usermanuals",
        title="GST India - User Manuals",
        category="tax",
        jurisdiction="IN",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.startupindia.gov.in/content/sih/en/tax-exemption.html",
        title="Startup India - Tax Exemption Scheme",
        category="policy",
        jurisdiction="IN",
        doc_type="html",
        priority=1,
    ),
]

# UK Tax & Policy Sources
UK_TAX_SOURCES = [
    DocumentSource(
        url="https://www.gov.uk/topic/business-tax/corporation-tax",
        title="UK Corporation Tax Guidance",
        category="tax",
        jurisdiction="UK",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2024-to-2025",
        title="UK Employer Tax Rates and Thresholds",
        category="tax",
        jurisdiction="UK",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.gov.uk/set-up-business",
        title="UK Set Up a Business Guide",
        category="legal",
        jurisdiction="UK",
        doc_type="html",
        priority=1,
    ),
]

# Business & Strategy Sources
BUSINESS_STRATEGY_SOURCES = [
    DocumentSource(
        url="https://www.sba.gov/business-guide",
        title="SBA Business Guide",
        category="business",
        jurisdiction="US",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.sba.gov/business-guide/plan-your-business/write-your-business-plan",
        title="SBA - How to Write a Business Plan",
        category="business",
        jurisdiction="US",
        doc_type="html",
        priority=1,
    ),
    DocumentSource(
        url="https://www.sba.gov/funding-programs/loans",
        title="SBA Funding and Loans",
        category="business",
        jurisdiction="US",
        doc_type="html",
        priority=1,
    ),
]

# Legal & Compliance Sources
LEGAL_SOURCES = [
    DocumentSource(
        url="https://www.sec.gov/education/smallbusiness",
        title="SEC Small Business Resources",
        category="legal",
        jurisdiction="US",
        doc_type="html",
        priority=2,
    ),
    DocumentSource(
        url="https://www.law.cornell.edu/wex/contract",
        title="Cornell Law - Contract Law",
        category="legal",
        jurisdiction="US",
        doc_type="html",
        priority=2,
    ),
]


def get_all_sources() -> List[DocumentSource]:
    """Get all knowledge sources."""
    return (
        US_TAX_SOURCES
        + INDIA_TAX_SOURCES
        + UK_TAX_SOURCES
        + BUSINESS_STRATEGY_SOURCES
        + LEGAL_SOURCES
    )


def get_sources_by_category(category: str) -> List[DocumentSource]:
    """Get sources filtered by category."""
    return [s for s in get_all_sources() if s.category == category]


def get_sources_by_jurisdiction(jurisdiction: str) -> List[DocumentSource]:
    """Get sources filtered by jurisdiction."""
    return [s for s in get_all_sources() if s.jurisdiction == jurisdiction]


def get_high_priority_sources() -> List[DocumentSource]:
    """Get high priority sources (priority=1)."""
    return [s for s in get_all_sources() if s.priority == 1]
