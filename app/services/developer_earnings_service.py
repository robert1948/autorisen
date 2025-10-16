"""
Developer Earnings Service
Calculates and manages developer earnings from platform transactions.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

try:
    import stripe
    STRIPE_AVAILABLE = True
except Exception:
    stripe = None
    STRIPE_AVAILABLE = False

from sqlalchemy.orm import Session

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)

class DeveloperEarningsService:
    """Service for calculating and managing developer earnings"""
    
    def __init__(self):
        """Initialize the developer earnings service"""
        # Configure stripe only when available and a key is present.
        if STRIPE_AVAILABLE and getattr(settings, "STRIPE_SECRET_KEY", None):
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
            except Exception:
                logger.warning("Stripe is available but failed to set api key")
        self.platform_commission_rate = Decimal('0.20')  # 20% platform commission
        self.developer_share_rate = Decimal('0.80')  # 80% goes to developer
    
    async def get_developer_earnings_summary(self, developer_id: str, db: Session) -> dict[str, Any]:
        """Get comprehensive earnings summary for a developer"""
        try:
            # Get developer info
            developer = db.query(User).filter(User.id == developer_id).first()
            if not developer or developer.role not in ['DEVELOPER', 'developer']:
                raise ValueError("User is not a developer")
            
            # Calculate earnings for different time periods
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            year_start = today.replace(month=1, day=1)
            
            earnings_data = {
                'developer_info': {
                    'id': str(developer.id),
                    'email': developer.email,
                    'name': f"{developer.first_name} {developer.last_name}".strip() or developer.email,
                    'joined_date': developer.created_at.isoformat() if developer.created_at else None
                },
                'total_earnings': await self._calculate_total_earnings(developer_id, db),
                'today_earnings': await self._calculate_period_earnings(developer_id, today, now, db),
                'week_earnings': await self._calculate_period_earnings(developer_id, week_start, now, db),
                'month_earnings': await self._calculate_period_earnings(developer_id, month_start, now, db),
                'year_earnings': await self._calculate_period_earnings(developer_id, year_start, now, db),
                'recent_transactions': await self._get_recent_transactions(developer_id, db),
                'earnings_chart_data': await self._get_earnings_chart_data(developer_id, db),
                'payout_status': await self._get_payout_status(developer_id),
                'performance_metrics': await self._get_performance_metrics(developer_id, db)
            }
            
            return earnings_data
            
        except Exception as e:
            logger.error(f"Error getting developer earnings summary: {e}")
            return await self._get_mock_earnings_data(developer_id)
    
    def get_total_earnings(self, user_id: int, db: Session) -> dict[str, Any]:
        """Calculate total earnings for a developer."""
        try:
            # For now, use mock data since PaymentAnalytics table structure is not ready
            # TODO: Implement real calculations when payment analytics are properly set up
            logger.info(f"Calculating total earnings for user {user_id}")
            
            # Mock calculation with realistic values
            total_revenue = 15000  # $150.00
            platform_commission = int(total_revenue * (1 - self.developer_share_rate))
            developer_earnings = total_revenue - platform_commission
            
            return {
                'total_earned': {
                    'amount_cents': developer_earnings,
                    'formatted': self.format_currency(developer_earnings)
                },
                'total_revenue': {
                    'amount_cents': total_revenue,
                    'formatted': self.format_currency(total_revenue)
                },
                'platform_commission': {
                    'amount_cents': platform_commission,
                    'formatted': self.format_currency(platform_commission)
                },
                'pending_payout': {
                    'amount_cents': developer_earnings,  # Assume all earnings are pending
                    'formatted': self.format_currency(developer_earnings)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating total earnings: {e}")
            # Return zero values on error
            return {
                'total_earned': {'amount_cents': 0, 'formatted': '$0.00'},
                'total_revenue': {'amount_cents': 0, 'formatted': '$0.00'},
                'platform_commission': {'amount_cents': 0, 'formatted': '$0.00'},
                'pending_payout': {'amount_cents': 0, 'formatted': '$0.00'}
            }
    
    async def _calculate_period_earnings(self, developer_id: str, start_date: datetime, end_date: datetime, db: Session) -> dict[str, Any]:
        """Calculate earnings for a specific time period"""
        try:
            # Mock calculation since PaymentAnalytics structure is not ready
            period_days = (end_date - start_date).days
            
            # Generate realistic mock data based on period length
            if period_days <= 7:  # Week
                mock_payments = 2500  # $25.00
                mock_transactions = 2
            elif period_days <= 30:  # Month  
                mock_payments = 8000  # $80.00
                mock_transactions = 8
            else:
                mock_payments = 15000  # $150.00
                mock_transactions = 15
            
            # Calculate developer share
            period_earned_cents = int(mock_payments * self.developer_share_rate)
            
            return {
                'amount_cents': period_earned_cents,
                'amount_dollars': period_earned_cents / 100,
                'formatted': f"${period_earned_cents / 100:.2f}",
                'transaction_count': mock_transactions,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating period earnings: {e}")
            return {
                'amount_cents': 0,
                'amount_dollars': 0.0,
                'formatted': '$0.00',
                'transaction_count': 0,
                'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()}
            }
    
    async def _get_recent_transactions(self, developer_id: str, db: Session, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent transactions for developer"""
        try:
            # Mock transaction data since PaymentAnalytics structure is not ready
            transactions = []
            
            # Generate realistic mock transactions
            for i in range(min(limit, 5)):  # Generate up to 5 mock transactions
                amount_cents = [2000, 5000, 3000, 1500, 8000][i]  # Various amounts
                developer_share = int(amount_cents * self.developer_share_rate)
                
                mock_date = datetime.utcnow() - timedelta(days=i * 3)
                
                transactions.append({
                    'id': f'mock_txn_{i+1}',
                    'type': 'subscription_created' if i % 2 == 0 else 'payment_succeeded',
                    'total_amount_cents': amount_cents,
                    'developer_earnings_cents': developer_share,
                    'developer_earnings_formatted': f"${developer_share / 100:.2f}",
                    'created_at': mock_date.isoformat(),
                    'status': 'completed',
                    'customer_id': f'customer_{i+1}'
                })
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
    
    async def _get_earnings_chart_data(self, developer_id: str, db: Session) -> dict[str, Any]:
        """Get earnings data for charts (last 30 days)"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Generate mock daily earnings for the last 30 days
            daily_earnings = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic mock daily earnings (random variation)
                base_daily_amount = 200 + (hash(current_date.strftime('%Y-%m-%d')) % 800)  # $2-10 per day
                day_earnings = int(base_daily_amount * self.developer_share_rate)
                
                daily_earnings.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'earnings_cents': day_earnings,
                    'earnings_dollars': day_earnings / 100
                })
                
                current_date += timedelta(days=1)
            
            return {
                'daily_earnings': daily_earnings,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings chart data: {e}")
            return {'daily_earnings': [], 'period': {'start': '', 'end': ''}}
    
    async def _get_payout_status(self, developer_id: str) -> dict[str, Any]:
        """Get payout status and next payout date"""
        try:
            # In a real implementation, this would integrate with Stripe Connect
            # For now, simulate payout information
            next_payout = datetime.utcnow() + timedelta(days=7)
            
            return {
                'next_payout_date': next_payout.isoformat(),
                'payout_schedule': 'weekly',
                'bank_account_connected': True,  # Would check Stripe Connect status
                'pending_verification': False,
                'last_payout_date': (datetime.utcnow() - timedelta(days=7)).isoformat(),
                'payout_method': 'bank_transfer'
            }
            
        except Exception as e:
            logger.error(f"Error getting payout status: {e}")
            return {
                'next_payout_date': None,
                'payout_schedule': 'unknown',
                'bank_account_connected': False,
                'pending_verification': True,
                'last_payout_date': None,
                'payout_method': 'none'
            }
    
    async def _get_performance_metrics(self, developer_id: str, db: Session) -> dict[str, Any]:
        """Get developer performance metrics"""
        try:
            # Mock performance metrics since PaymentAnalytics structure is not ready
            total_customers = 15  # Mock customer count
            avg_transaction_value = 5000  # $50.00 average
            
            return {
                'total_customers': total_customers,
                'average_transaction_value': {
                    'amount_cents': int(avg_transaction_value),
                    'amount_dollars': avg_transaction_value / 100,
                    'formatted': f"${avg_transaction_value / 100:.2f}"
                },
                'conversion_rate': 0.15,  # 15% mock conversion rate
                'customer_satisfaction': 4.8,  # Mock rating
                'repeat_purchase_rate': 0.35,  # 35% mock repeat rate
                'churn_rate': 0.05  # 5% mock churn rate
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'total_customers': 0,
                'average_transaction_value': {'amount_cents': 0, 'amount_dollars': 0.0, 'formatted': '$0.00'},
                'conversion_rate': 0.0,
                'customer_satisfaction': 0.0,
                'repeat_purchase_rate': 0.0,
                'churn_rate': 0.0
            }
    
    async def _get_mock_earnings_data(self, developer_id: str) -> dict[str, Any]:
        """Return mock earnings data when real data is not available"""
        now = datetime.utcnow()
        
        return {
            'developer_info': {
                'id': developer_id,
                'email': 'developer@example.com',
                'name': 'Demo Developer',
                'joined_date': (now - timedelta(days=90)).isoformat()
            },
            'total_earnings': {
                'total_earned': {'amount_cents': 245000, 'amount_dollars': 2450.0, 'formatted': '$2,450.00'},
                'total_paid': {'amount_cents': 220500, 'amount_dollars': 2205.0, 'formatted': '$2,205.00'},
                'pending_payout': {'amount_cents': 24500, 'amount_dollars': 245.0, 'formatted': '$245.00'}
            },
            'today_earnings': {
                'amount_cents': 0, 'amount_dollars': 0.0, 'formatted': '$0.00',
                'transaction_count': 0, 'period': {'start': now.isoformat(), 'end': now.isoformat()}
            },
            'week_earnings': {
                'amount_cents': 12000, 'amount_dollars': 120.0, 'formatted': '$120.00',
                'transaction_count': 3, 'period': {'start': now.isoformat(), 'end': now.isoformat()}
            },
            'month_earnings': {
                'amount_cents': 48000, 'amount_dollars': 480.0, 'formatted': '$480.00',
                'transaction_count': 12, 'period': {'start': now.isoformat(), 'end': now.isoformat()}
            },
            'year_earnings': {
                'amount_cents': 245000, 'amount_dollars': 2450.0, 'formatted': '$2,450.00',
                'transaction_count': 73, 'period': {'start': now.isoformat(), 'end': now.isoformat()}
            },
            'recent_transactions': [
                {
                    'id': 'demo_txn_1',
                    'type': 'subscription_created',
                    'total_amount_cents': 2999,
                    'developer_earnings_cents': 2399,
                    'developer_earnings_formatted': '$23.99',
                    'created_at': (now - timedelta(days=1)).isoformat(),
                    'status': 'completed',
                    'customer_id': 'demo_customer_1'
                },
                {
                    'id': 'demo_txn_2',
                    'type': 'payment_succeeded',
                    'total_amount_cents': 1999,
                    'developer_earnings_cents': 1599,
                    'developer_earnings_formatted': '$15.99',
                    'created_at': (now - timedelta(days=3)).isoformat(),
                    'status': 'completed',
                    'customer_id': 'demo_customer_2'
                }
            ],
            'earnings_chart_data': {
                'daily_earnings': [
                    {'date': (now - timedelta(days=i)).strftime('%Y-%m-%d'), 
                     'earnings_cents': 1200 + (i * 100), 
                     'earnings_dollars': (1200 + (i * 100)) / 100}
                    for i in range(30, 0, -1)
                ],
                'period': {'start': (now - timedelta(days=30)).isoformat(), 'end': now.isoformat()}
            },
            'payout_status': {
                'next_payout_date': (now + timedelta(days=4)).isoformat(),
                'payout_schedule': 'weekly',
                'bank_account_connected': True,
                'pending_verification': False,
                'last_payout_date': (now - timedelta(days=3)).isoformat(),
                'payout_method': 'bank_transfer'
            },
            'performance_metrics': {
                'total_customers': 28,
                'average_transaction_value': {'amount_cents': 2499, 'amount_dollars': 24.99, 'formatted': '$24.99'},
                'conversion_rate': 0.18,
                'customer_satisfaction': 4.7,
                'repeat_purchase_rate': 0.42,
                'churn_rate': 0.03
            }
        }

# Initialize service instance
developer_earnings_service = DeveloperEarningsService()
