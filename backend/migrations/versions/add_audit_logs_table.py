"""
Database Migration: Add Audit Log Table
=====================================

Task 1.2.6 - Audit Logging: Create audit_logs table for comprehensive event tracking

Revision ID: add_audit_logs_table
Revises: previous_migration
Create Date: 2024-01-20 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_audit_logs_table'
down_revision = 'previous_migration'  # Update this to actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """
    Create audit_logs table with comprehensive event tracking capabilities
    """
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        
        # User and context information
        sa.Column('user_id', sa.String(50), nullable=True, index=True),
        sa.Column('user_email', sa.String(320), nullable=True, index=True),
        sa.Column('user_role', sa.String(50), nullable=True),
        
        # Event classification
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('event_category', sa.String(50), nullable=False, index=True),
        sa.Column('event_level', sa.String(20), nullable=False, default='info'),
        sa.Column('event_description', sa.Text(), nullable=True),
        
        # Request/Response details
        sa.Column('ip_address', sa.String(45), nullable=True, index=True),  # IPv6 support
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('endpoint', sa.String(500), nullable=True),
        sa.Column('http_method', sa.String(10), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        
        # Event outcome
        sa.Column('success', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        
        # Additional data and metadata
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        
        # Security and risk assessment
        sa.Column('risk_score', sa.Integer(), nullable=True, index=True),
        
        # Compliance and data governance
        sa.Column('data_classification', sa.String(50), nullable=True),
        sa.Column('compliance_tags', postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column('retention_policy', sa.String(50), nullable=True, default='standard'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), 
                 server_default=sa.text('CURRENT_TIMESTAMP'), 
                 nullable=False, index=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=True),
        
        # Add foreign key constraint to users table
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], 
                               name='audit_logs_user_id_fkey',
                               ondelete='SET NULL'),
    )
    
    # Create indexes for performance
    
    # Composite indexes for common query patterns
    op.create_index('idx_audit_logs_user_time', 'audit_logs', 
                   ['user_id', 'created_at'])
    
    op.create_index('idx_audit_logs_event_time', 'audit_logs', 
                   ['event_type', 'created_at'])
    
    op.create_index('idx_audit_logs_category_level', 'audit_logs', 
                   ['event_category', 'event_level'])
    
    op.create_index('idx_audit_logs_ip_time', 'audit_logs', 
                   ['ip_address', 'created_at'])
    
    op.create_index('idx_audit_logs_success_risk', 'audit_logs', 
                   ['success', 'risk_score'])
    
    # JSONB GIN index for metadata queries
    op.create_index('idx_audit_logs_metadata_gin', 'audit_logs', 
                   ['metadata'], postgresql_using='gin')
    
    # Partial indexes for failed events and high-risk events
    op.create_index('idx_audit_logs_failed_events', 'audit_logs', 
                   ['created_at', 'user_id', 'ip_address'],
                   postgresql_where=sa.text('success = false'))
    
    op.create_index('idx_audit_logs_high_risk', 'audit_logs', 
                   ['created_at', 'event_type', 'user_id'],
                   postgresql_where=sa.text('risk_score >= 70'))
    
    # Create enum types for event types and levels (optional, for better data integrity)
    
    # Event level enum
    event_level_enum = postgresql.ENUM(
        'debug', 'info', 'warning', 'error', 'critical',
        name='audit_log_level_enum',
        create_type=True
    )
    event_level_enum.create(op.get_bind())
    
    # Event category enum  
    event_category_enum = postgresql.ENUM(
        'authentication', 'authorization', 'security', 'ai_service',
        'profile', 'admin', 'data', 'system', 'request',
        name='audit_event_category_enum',
        create_type=True
    )
    event_category_enum.create(op.get_bind())
    
    # Add check constraints for data validation
    
    # Risk score should be between 0 and 100
    op.create_check_constraint(
        'ck_audit_logs_risk_score_range',
        'audit_logs',
        sa.text('risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)')
    )
    
    # Response time should be positive
    op.create_check_constraint(
        'ck_audit_logs_response_time_positive',
        'audit_logs',
        sa.text('response_time_ms IS NULL OR response_time_ms >= 0')
    )
    
    # HTTP status code should be valid
    op.create_check_constraint(
        'ck_audit_logs_status_code_valid',
        'audit_logs',
        sa.text('status_code IS NULL OR (status_code >= 100 AND status_code <= 599)')
    )
    
    # Create a view for security events (high-risk or failed authentication)
    op.execute("""
        CREATE VIEW security_events_view AS
        SELECT 
            id,
            user_id,
            user_email,
            event_type,
            event_category,
            event_level,
            event_description,
            ip_address,
            user_agent,
            endpoint,
            success,
            error_message,
            metadata,
            risk_score,
            created_at,
            CASE 
                WHEN risk_score >= 80 THEN 'critical'
                WHEN risk_score >= 60 THEN 'high'
                WHEN risk_score >= 40 THEN 'medium'
                ELSE 'low'
            END as threat_level,
            CASE
                WHEN event_type IN ('BRUTE_FORCE_ATTEMPT', 'UNAUTHORIZED_ACCESS', 'SUSPICIOUS_ACTIVITY') THEN true
                WHEN risk_score >= 70 THEN true
                WHEN success = false AND event_category = 'authentication' THEN true
                ELSE false
            END as requires_investigation
        FROM audit_logs
        WHERE 
            event_category IN ('security', 'authentication', 'authorization')
            OR risk_score >= 40
            OR success = false
        ORDER BY created_at DESC;
    """)
    
    # Create a function for automatic risk scoring (can be called from triggers)
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_audit_risk_score(
            p_event_type VARCHAR,
            p_event_category VARCHAR,
            p_success BOOLEAN,
            p_metadata JSONB DEFAULT NULL
        ) RETURNS INTEGER AS $$
        DECLARE
            base_score INTEGER := 0;
            final_score INTEGER;
        BEGIN
            -- Base scores by event type
            CASE p_event_type
                WHEN 'BRUTE_FORCE_ATTEMPT' THEN base_score := 90;
                WHEN 'UNAUTHORIZED_ACCESS' THEN base_score := 85;
                WHEN 'SUSPICIOUS_ACTIVITY' THEN base_score := 80;
                WHEN 'ACCOUNT_LOCKED' THEN base_score := 75;
                WHEN 'PASSWORD_CHANGE' THEN base_score := 30;
                WHEN 'USER_LOGIN_FAILED' THEN base_score := 40;
                WHEN 'USER_LOGIN' THEN base_score := 10;
                WHEN 'AI_CONTENT_FLAGGED' THEN base_score := 60;
                WHEN 'RATE_LIMIT_EXCEEDED' THEN base_score := 50;
                WHEN 'DATA_ACCESS' THEN base_score := 20;
                WHEN 'ADMIN_ACTION' THEN base_score := 40;
                ELSE base_score := 10;
            END CASE;
            
            -- Adjust based on success status
            IF NOT p_success THEN
                base_score := base_score + 20;
            END IF;
            
            -- Adjust based on category
            CASE p_event_category
                WHEN 'security' THEN base_score := base_score + 10;
                WHEN 'authentication' THEN base_score := base_score + 5;
                WHEN 'admin' THEN base_score := base_score + 15;
                ELSE base_score := base_score;
            END CASE;
            
            -- Check metadata for additional risk factors
            IF p_metadata IS NOT NULL THEN
                IF p_metadata ? 'multiple_failures' THEN
                    base_score := base_score + 15;
                END IF;
                
                IF p_metadata ? 'unusual_location' THEN
                    base_score := base_score + 10;
                END IF;
                
                IF p_metadata ? 'threat_indicators' THEN
                    base_score := base_score + 20;
                END IF;
            END IF;
            
            -- Ensure score is within valid range
            final_score := GREATEST(0, LEAST(100, base_score));
            
            RETURN final_score;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to automatically calculate risk scores if not provided
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_log_risk_score_trigger()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.risk_score IS NULL THEN
                NEW.risk_score := calculate_audit_risk_score(
                    NEW.event_type,
                    NEW.event_category,
                    NEW.success,
                    NEW.metadata
                );
            END IF;
            
            -- Set event_timestamp if not provided
            IF NEW.event_timestamp IS NULL THEN
                NEW.event_timestamp := NEW.created_at;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER audit_log_before_insert_trigger
        BEFORE INSERT ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION audit_log_risk_score_trigger();
    """)


def downgrade():
    """
    Remove audit_logs table and related objects
    """
    
    # Drop triggers and functions
    op.execute("DROP TRIGGER IF EXISTS audit_log_before_insert_trigger ON audit_logs;")
    op.execute("DROP FUNCTION IF EXISTS audit_log_risk_score_trigger();")
    op.execute("DROP FUNCTION IF EXISTS calculate_audit_risk_score(VARCHAR, VARCHAR, BOOLEAN, JSONB);")
    
    # Drop view
    op.execute("DROP VIEW IF EXISTS security_events_view;")
    
    # Drop indexes (foreign key indexes are dropped automatically)
    op.drop_index('idx_audit_logs_high_risk', table_name='audit_logs')
    op.drop_index('idx_audit_logs_failed_events', table_name='audit_logs')
    op.drop_index('idx_audit_logs_metadata_gin', table_name='audit_logs')
    op.drop_index('idx_audit_logs_success_risk', table_name='audit_logs')
    op.drop_index('idx_audit_logs_ip_time', table_name='audit_logs')
    op.drop_index('idx_audit_logs_category_level', table_name='audit_logs')
    op.drop_index('idx_audit_logs_event_time', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_time', table_name='audit_logs')
    
    # Drop table
    op.drop_table('audit_logs')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS audit_event_category_enum;")
    op.execute("DROP TYPE IF EXISTS audit_log_level_enum;")
