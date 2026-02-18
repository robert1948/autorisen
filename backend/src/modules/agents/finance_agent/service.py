"""
Finance Agent Service

Core business logic for the Finance Agent including LLM integration,
financial analysis, compliance checking, and forecasting.
"""

import time
import logging
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from backend.src.db import models

from .schemas import FinanceAgentTaskInput, FinanceAgentTaskOutput, FinancialInsight
from .knowledge_base import FinanceKnowledgeBase

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the CapeControl Finance Agent — a professional AI assistant for \
financial analysis, forecasting, and compliance on the CapeControl platform.

Your expertise covers:
1. **Financial Analysis**: Cash flow, profitability, ratios, KPI tracking
2. **Budget Forecasting**: Revenue projections, cost planning, scenario analysis
3. **Compliance**: IFRS, tax regulations, South African financial compliance
4. **Risk Assessment**: Liquidity, credit, market, and operational risk
5. **Reporting**: Financial dashboards, KPI frameworks, management reporting
6. **Invoice & Payments**: Processing automation, accounts payable/receivable

Communication style:
- Be precise, data-driven, and professional
- Always qualify statements about financial projections with appropriate caveats
- Include specific metrics and benchmarks where relevant
- Highlight both risks and opportunities
- Provide actionable recommendations with clear priorities

Important disclaimers:
- Always note that AI analysis should be validated by qualified finance professionals
- Financial projections are estimates and not guarantees
- Compliance advice is general guidance and should be verified with legal/tax advisors"""

USER_PROMPT_TEMPLATE = """Financial Query: {query}

Analysis Type: {analysis_type}
Currency: {currency}
Time Period: {time_period}

Relevant Financial Knowledge:
{knowledge}

Please provide:
1. A clear, professional analysis addressing the query
2. Key financial insights with severity levels
3. Actionable recommendations
4. Risk factors to consider
5. Any compliance notes relevant to South African businesses"""


class FinanceAgentService:
    """Service class for Finance Agent operations."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022",
    ):
        self.openai_client = (
            AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        )
        self.model = model
        self.knowledge_base = FinanceKnowledgeBase()

    async def process_query(
        self,
        input_data: FinanceAgentTaskInput,
        *,
        db: Session | None = None,
        user: models.User | None = None,
    ) -> FinanceAgentTaskOutput:
        """Process a financial query and generate analysis."""
        start_time = time.time()

        try:
            context = input_data.context or {}
            context["analysis_type"] = input_data.analysis_type

            relevant_docs = await self.knowledge_base.search(
                query=input_data.query, context=context, limit=4
            )

            knowledge_text = "\n".join(
                f"- {doc.title}: {doc.content}" for doc in relevant_docs
            ) or "No specific financial knowledge matched."

            user_prompt = USER_PROMPT_TEMPLATE.format(
                query=input_data.query,
                analysis_type=input_data.analysis_type or "general",
                currency=input_data.currency or "ZAR",
                time_period=input_data.time_period or "not specified",
                knowledge=knowledge_text,
            )

            ai_response = await self._call_llm(user_prompt)

            # Generate insights based on analysis type
            insights = self._generate_insights(input_data.analysis_type, relevant_docs)

            # Get compliance notes
            compliance_notes = self.knowledge_base.get_compliance_notes(
                "za" if input_data.currency == "ZAR" else "international"
            )

            # Risk factors
            risk_factors = self._assess_risks(input_data)

            # Recommendations
            recommendations = self._generate_recommendations(
                input_data.analysis_type, relevant_docs
            )

            processing_time = int((time.time() - start_time) * 1000)

            return FinanceAgentTaskOutput(
                response=ai_response,
                insights=insights,
                recommendations=recommendations,
                risk_factors=risk_factors,
                compliance_notes=compliance_notes[:3],
                next_steps=self._get_next_steps(input_data.analysis_type),
                confidence_score=self._calculate_confidence(relevant_docs, ai_response),
                processing_time_ms=processing_time,
            )

        except Exception as e:
            log.error("FinanceAgent error: %s", e)
            processing_time = int((time.time() - start_time) * 1000)
            return FinanceAgentTaskOutput(
                response=(
                    "I can provide general financial guidance based on the information available. "
                    "For specific financial analysis, please ensure you provide relevant data context. "
                    "Always validate AI-generated financial analysis with qualified professionals."
                ),
                insights=[],
                recommendations=["Consult with a qualified financial advisor for specific guidance"],
                risk_factors=[],
                compliance_notes=[],
                next_steps=["Provide more context for a detailed analysis"],
                confidence_score=0.3,
                processing_time_ms=processing_time,
            )

    async def _call_llm(self, user_prompt: str) -> str:
        """Call the LLM provider."""
        if self.anthropic_client and "claude" in self.model:
            try:
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text
            except Exception as e:
                log.warning("Anthropic call failed: %s", e)

        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini" if "claude" in self.model else self.model,
                    max_tokens=1500,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                log.error("OpenAI call also failed: %s", e)

        return (
            "Based on standard financial analysis frameworks, I'd recommend reviewing "
            "your key financial metrics including cash flow ratios, profitability margins, "
            "and working capital position. Please provide specific financial data for a "
            "more detailed analysis."
        )

    def _generate_insights(
        self, analysis_type: Optional[str], docs: list
    ) -> List[FinancialInsight]:
        """Generate financial insights based on the analysis type."""
        insights = []

        type_insights = {
            "forecasting": FinancialInsight(
                category="forecasting",
                title="Rolling Forecast Recommended",
                detail="Implement 12-month rolling forecasts for more accurate projections. "
                "Include best, base, and worst-case scenarios.",
                severity="info",
            ),
            "budgeting": FinancialInsight(
                category="budgeting",
                title="Zero-Based Budgeting Opportunity",
                detail="Consider zero-based budgeting for discretionary expenses to identify "
                "optimization opportunities and reduce unnecessary spending.",
                severity="info",
            ),
            "compliance": FinancialInsight(
                category="compliance",
                title="Regulatory Calendar Review",
                detail="Ensure all upcoming SARS submissions and IFRS reporting deadlines "
                "are calendared with adequate preparation time.",
                severity="warning",
            ),
            "risk": FinancialInsight(
                category="risk",
                title="Currency Exposure Assessment",
                detail="ZAR volatility requires active currency risk management for any "
                "international transactions or USD-denominated obligations.",
                severity="warning",
            ),
            "reporting": FinancialInsight(
                category="reporting",
                title="KPI Dashboard Setup",
                detail="Implement automated financial KPI tracking covering profitability, "
                "liquidity, efficiency, and leverage ratios.",
                severity="info",
            ),
        }

        if analysis_type and analysis_type in type_insights:
            insights.append(type_insights[analysis_type])

        # Always add a general data quality insight
        insights.append(
            FinancialInsight(
                category="data_quality",
                title="Validate Input Data",
                detail="AI-generated financial analysis is only as good as the input data. "
                "Ensure data completeness and accuracy before acting on recommendations.",
                severity="info",
            )
        )

        return insights

    def _assess_risks(self, input_data: FinanceAgentTaskInput) -> List[str]:
        """Assess relevant financial risks."""
        risks = []

        if input_data.currency == "ZAR":
            risks.append("ZAR exchange rate volatility may impact foreign-denominated costs")

        if input_data.analysis_type == "forecasting":
            risks.append("Forecast accuracy depends on macroeconomic stability")
            risks.append("South African load shedding may impact operational projections")

        if input_data.analysis_type == "risk":
            risks.append("Concentration risk in key revenue streams")
            risks.append("Interest rate changes affecting debt service costs")

        if not risks:
            risks.append("General economic uncertainty should be factored into financial decisions")

        return risks

    def _generate_recommendations(
        self, analysis_type: Optional[str], docs: list
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = {
            "forecasting": [
                "Implement monthly rolling forecasts with variance analysis",
                "Build scenario models for key business drivers",
                "Track forecast accuracy to improve future projections",
            ],
            "budgeting": [
                "Review and challenge each budget line item from zero base",
                "Allocate contingency reserves for unexpected expenses",
                "Align budget targets with strategic objectives",
            ],
            "compliance": [
                "Maintain a regulatory submission calendar with alerts",
                "Schedule quarterly compliance reviews",
                "Document all compliance procedures and controls",
            ],
            "risk": [
                "Establish risk appetite thresholds for key risk categories",
                "Implement hedging strategies for material FX exposures",
                "Conduct quarterly risk assessments and update risk register",
            ],
            "reporting": [
                "Automate recurring financial reports to reduce manual effort",
                "Set up real-time KPI dashboards for management visibility",
                "Standardize reporting formats across business units",
            ],
        }
        return recommendations.get(analysis_type or "general", [
            "Review key financial metrics regularly",
            "Ensure financial reporting is timely and accurate",
            "Maintain adequate cash reserves for operational needs",
        ])

    def _get_next_steps(self, analysis_type: Optional[str]) -> List[str]:
        """Get next steps based on analysis type."""
        return [
            "Review the analysis and validate key assumptions",
            "Share findings with relevant stakeholders",
            "Implement recommended actions by priority",
            "Schedule follow-up analysis to track progress",
        ]

    def _calculate_confidence(self, docs: list, response: str) -> float:
        """Calculate confidence score."""
        score = 0.4
        if docs:
            score += min(len(docs) * 0.1, 0.25)
        if len(response) > 300:
            score += 0.1
        if len(response) > 600:
            score += 0.1
        return min(score, 1.0)
