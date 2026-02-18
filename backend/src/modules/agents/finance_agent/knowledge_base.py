"""
Finance Agent Knowledge Base

In-memory knowledge base with financial analysis templates,
compliance guidelines, and industry-specific financial knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FinanceDocument:
    """A financial knowledge document."""

    id: str
    title: str
    content: str
    category: str
    tags: List[str] = field(default_factory=list)


FINANCE_DOCUMENTS = [
    FinanceDocument(
        id="cash-flow-analysis",
        title="Cash Flow Analysis Framework",
        content="Cash flow analysis examines operating, investing, and financing activities. "
        "Key metrics include Operating Cash Flow Ratio, Free Cash Flow, Cash Conversion Cycle, "
        "and Days Sales Outstanding. Monitor trends over 3-6 month periods for early warning signs. "
        "A healthy business typically maintains OCF/Sales ratio above 0.15.",
        category="analysis",
        tags=["cash-flow", "analysis", "operating", "investing", "financing", "metrics"],
    ),
    FinanceDocument(
        id="budget-forecasting",
        title="Budget Forecasting Methodology",
        content="Budget forecasting combines historical analysis with forward-looking assumptions. "
        "Start with the previous period's actuals, apply growth/contraction factors, and adjust "
        "for known changes. Use rolling forecasts (12-month rolling) for more accurate projections. "
        "Include best-case, base-case, and worst-case scenarios for key line items.",
        category="forecasting",
        tags=["budget", "forecast", "planning", "scenarios", "projections"],
    ),
    FinanceDocument(
        id="compliance-saica",
        title="South African Financial Compliance",
        content="South African companies must comply with IFRS, Companies Act 71 of 2008, "
        "Tax Administration Act, and SARS regulations. Key requirements include annual financial "
        "statements, provisional tax submissions, VAT returns (bi-monthly or monthly depending on "
        "turnover), and PAYE/UIF/SDL submissions. B-BBEE compliance also affects procurement scoring.",
        category="compliance",
        tags=["compliance", "IFRS", "SARS", "south-africa", "tax", "VAT", "B-BBEE"],
    ),
    FinanceDocument(
        id="risk-assessment",
        title="Financial Risk Assessment",
        content="Key financial risks include liquidity risk (inability to meet short-term obligations), "
        "credit risk (counterparty default), market risk (FX, interest rate, commodity price changes), "
        "and operational risk (process failures, fraud). Use Key Risk Indicators (KRIs) and establish "
        "risk appetite thresholds. Currency exposure is critical for SA businesses trading internationally.",
        category="risk",
        tags=["risk", "liquidity", "credit", "market", "operational", "assessment"],
    ),
    FinanceDocument(
        id="kpi-framework",
        title="Financial KPI Framework",
        content="Essential financial KPIs: Revenue Growth Rate, Gross Profit Margin, Operating Margin, "
        "EBITDA Margin, Net Profit Margin, Return on Assets (ROA), Return on Equity (ROE), "
        "Current Ratio, Quick Ratio, Debt-to-Equity Ratio, Interest Coverage Ratio, "
        "Working Capital Ratio, Accounts Receivable Turnover, Inventory Turnover.",
        category="reporting",
        tags=["KPI", "metrics", "reporting", "margins", "ratios", "performance"],
    ),
    FinanceDocument(
        id="invoice-management",
        title="Invoice Processing & Management",
        content="Automated invoice processing reduces errors by 80% and processing time by 60%. "
        "Key steps: data extraction (OCR/AI), validation against POs, three-way matching "
        "(PO-receipt-invoice), approval routing, and payment scheduling. Track metrics like "
        "invoice processing time, exception rate, cost per invoice, and Days Payable Outstanding.",
        category="operations",
        tags=["invoice", "processing", "automation", "payments", "accounts-payable"],
    ),
]


class FinanceKnowledgeBase:
    """Knowledge base for the Finance Agent."""

    def __init__(self):
        self.documents = {d.id: d for d in FINANCE_DOCUMENTS}

    async def search(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[FinanceDocument]:
        """Search financial knowledge base."""
        query_lower = query.lower()
        scored: List[tuple[float, FinanceDocument]] = []

        for doc in FINANCE_DOCUMENTS:
            score = 0.0

            for word in query_lower.split():
                if len(word) < 3:
                    continue
                if word in doc.title.lower():
                    score += 2.0
                if word in doc.content.lower():
                    score += 1.0
                if word in [t.lower() for t in doc.tags]:
                    score += 1.5

            if context:
                analysis_type = context.get("analysis_type", "")
                if isinstance(analysis_type, str) and analysis_type in doc.category:
                    score += 2.0

            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:limit]]

    def get_compliance_notes(self, region: str = "za") -> List[str]:
        """Get compliance notes for a region."""
        if region.lower() in ("za", "south africa", "zar"):
            return [
                "Ensure IFRS compliance for financial statements",
                "Submit VAT returns as per SARS schedule",
                "Maintain B-BBEE scorecard documentation",
                "File provisional tax submissions on time",
                "Comply with Companies Act reporting requirements",
            ]
        return ["Ensure compliance with local financial regulations"]
