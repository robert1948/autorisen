"""
Developer Earnings API Routes
Provides endpoints for developers to view their earnings and performance metrics.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.services.audit_service import AuditEventType, get_audit_logger
from app.services.developer_earnings_service import developer_earnings_service

router = APIRouter(prefix="/api/developer", tags=["developer-earnings"])
logger = logging.getLogger(__name__)

@router.get("/earnings", response_model=dict[str, Any])
async def get_developer_earnings(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive earnings data for the current developer.
    
    Returns earnings summary, recent transactions, performance metrics,
    payout status, and chart data for the authenticated developer.
    """
    audit_logger = get_audit_logger()
    
    try:
        # Verify user is a developer
        user_role = current_user.get('role', '').lower()
        if user_role not in ['developer', 'DEVELOPER']:
            audit_logger.log_security_event(
                db=db,
                event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
                user_id=current_user.get('user_id'),
                additional_data={
                    'attempted_resource': 'developer_earnings',
                    'user_role': user_role,
                    'reason': 'insufficient_permissions'
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Developer role required."
            )
        
        # Get earnings data
        developer_id = current_user.get('user_id')
        earnings_data = await developer_earnings_service.get_developer_earnings_summary(
            developer_id=developer_id,
            db=db
        )
        
        # Log successful access
        audit_logger.log_security_event(
            db=db,
            event_type=AuditEventType.DEVELOPER_EARNINGS_ACCESSED,
            user_id=developer_id,
            success=True,
            additional_data={
                'total_earnings': earnings_data.get('total_earnings', {}).get('total_earned', {}).get('formatted', '$0.00'),
                'access_time': earnings_data.get('developer_info', {}).get('joined_date', 'unknown')
            }
        )
        
        return {
            'success': True,
            'data': earnings_data,
            'message': 'Developer earnings retrieved successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving developer earnings: {e}")
        audit_logger.log_security_event(
            db=db,
            event_type=AuditEventType.DEVELOPER_EARNINGS_ACCESS_FAILED,
            user_id=current_user.get('user_id'),
            success=False,
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve earnings data"
        )

@router.get("/earnings/summary", response_model=dict[str, Any])
async def get_earnings_summary(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a quick earnings summary for dashboard display.
    
    Returns essential earnings metrics without detailed transaction history.
    """
    try:
        # Verify developer role
        user_role = current_user.get('role', '').lower()
        if user_role not in ['developer', 'DEVELOPER']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Developer role required."
            )
        
        developer_id = current_user.get('user_id')
        full_data = await developer_earnings_service.get_developer_earnings_summary(
            developer_id=developer_id,
            db=db
        )
        
        # Return summarized data
        summary = {
            'total_earnings': full_data.get('total_earnings', {}),
            'month_earnings': full_data.get('month_earnings', {}),
            'week_earnings': full_data.get('week_earnings', {}),
            'pending_payout': full_data.get('total_earnings', {}).get('pending_payout', {}),
            'next_payout': full_data.get('payout_status', {}).get('next_payout_date'),
            'performance_overview': {
                'total_customers': full_data.get('performance_metrics', {}).get('total_customers', 0),
                'avg_transaction': full_data.get('performance_metrics', {}).get('average_transaction_value', {}),
                'satisfaction': full_data.get('performance_metrics', {}).get('customer_satisfaction', 0)
            }
        }
        
        return {
            'success': True,
            'data': summary,
            'message': 'Earnings summary retrieved successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving earnings summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve earnings summary"
        )

@router.get("/earnings/transactions", response_model=dict[str, Any])
async def get_recent_transactions(
    limit: int = 20,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent transactions for the developer.
    
    Args:
        limit: Maximum number of transactions to return (default: 20, max: 100)
    """
    try:
        # Verify developer role
        user_role = current_user.get('role', '').lower()
        if user_role not in ['developer', 'DEVELOPER']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Developer role required."
            )
        
        # Validate limit
        if limit > 100:
            limit = 100
        elif limit < 1:
            limit = 20
        
        developer_id = current_user.get('user_id')
        full_data = await developer_earnings_service.get_developer_earnings_summary(
            developer_id=developer_id,
            db=db
        )
        
        transactions = full_data.get('recent_transactions', [])[:limit]
        
        return {
            'success': True,
            'data': {
                'transactions': transactions,
                'total_count': len(transactions),
                'limit': limit
            },
            'message': f'Retrieved {len(transactions)} recent transactions'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recent transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction history"
        )

@router.get("/earnings/chart-data", response_model=dict[str, Any])
async def get_earnings_chart_data(
    days: int = 30,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get earnings data formatted for charts and graphs.
    
    Args:
        days: Number of days of historical data (default: 30, max: 365)
    """
    try:
        # Verify developer role
        user_role = current_user.get('role', '').lower()
        if user_role not in ['developer', 'DEVELOPER']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Developer role required."
            )
        
        # Validate days parameter
        if days > 365:
            days = 365
        elif days < 7:
            days = 7
        
        developer_id = current_user.get('user_id')
        full_data = await developer_earnings_service.get_developer_earnings_summary(
            developer_id=developer_id,
            db=db
        )
        
        chart_data = full_data.get('earnings_chart_data', {})
        
        # Limit data to requested days
        daily_earnings = chart_data.get('daily_earnings', [])
        if len(daily_earnings) > days:
            daily_earnings = daily_earnings[-days:]
        
        return {
            'success': True,
            'data': {
                'daily_earnings': daily_earnings,
                'period_days': days,
                'total_data_points': len(daily_earnings)
            },
            'message': f'Chart data retrieved for {days} days'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chart data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chart data"
        )

@router.get("/payout-status", response_model=dict[str, Any])
async def get_payout_status(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current payout status and setup information.
    
    Returns information about bank account connection, payout schedule,
    pending verification status, and next payout date.
    """
    try:
        # Verify developer role
        user_role = current_user.get('role', '').lower()
        if user_role not in ['developer', 'DEVELOPER']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Developer role required."
            )
        
        developer_id = current_user.get('user_id')
        full_data = await developer_earnings_service.get_developer_earnings_summary(
            developer_id=developer_id,
            db=db
        )
        
        payout_status = full_data.get('payout_status', {})
        
        return {
            'success': True,
            'data': payout_status,
            'message': 'Payout status retrieved successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payout status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payout status"
        )
