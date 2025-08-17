"""
Database optimization utilities for CapeControl
"""
from sqlalchemy import Index, text
from sqlalchemy.orm import Session
from app.database import engine
from app.models import User, UserProfile


class DatabaseOptimizer:
    """Database optimization and maintenance utilities"""
    
    @staticmethod
    def create_indexes():
        """Create performance indexes for the database"""
        indexes = [
            # User table indexes
            Index('idx_users_email_role', User.email, User.user_role),
            Index('idx_users_created_at', User.created_at),
            Index('idx_users_role_active', User.user_role, User.created_at),
            
            # User profile indexes
            Index('idx_user_profiles_user_id', UserProfile.user_id),
            Index('idx_user_profiles_created', UserProfile.created_at),
        ]
        
        # Create indexes
        for index in indexes:
            try:
                index.create(bind=engine, checkfirst=True)
                print(f"✅ Created index: {index.name}")
            except Exception as e:
                print(f"❌ Failed to create index {index.name}: {e}")
    
    @staticmethod
    def analyze_query_performance(db: Session):
        """Analyze database query performance"""
        # Query to check slow queries (SQLite doesn't have built-in slow query log)
        # This is a placeholder for when we move to PostgreSQL
        queries = [
            "-- Most common user queries",
            "SELECT COUNT(*) as total_users FROM users",
            "SELECT user_role, COUNT(*) as count FROM users GROUP BY user_role",
            "SELECT DATE(created_at) as date, COUNT(*) as registrations FROM users GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30"
        ]
        
        results = {}
        for query in queries:
            if not query.startswith("--"):
                try:
                    result = db.execute(text(query)).fetchall()
                    results[query] = result
                except Exception as e:
                    results[query] = f"Error: {e}"
        
        return results
    
    @staticmethod
    def database_maintenance(db: Session):
        """Perform routine database maintenance"""
        maintenance_tasks = {
            "vacuum": "VACUUM",  # SQLite specific
            "analyze": "ANALYZE",  # Update query planner statistics
        }
        
        results = {}
        for task, sql in maintenance_tasks.items():
            try:
                db.execute(text(sql))
                db.commit()
                results[task] = "✅ Completed"
            except Exception as e:
                results[task] = f"❌ Failed: {e}"
        
        return results


def setup_database_monitoring():
    """Setup database monitoring and alerts"""
    # This would integrate with monitoring systems like:
    # - Query execution time tracking
    # - Connection pool monitoring
    # - Slow query detection
    # - Database size monitoring
    pass


# Configuration for database optimization
DATABASE_OPTIMIZATION_CONFIG = {
    "indexes": {
        "users": ["email", "user_role", "created_at", "email_role_compound"],
        "user_profiles": ["user_id", "created_at"]
    },
    "maintenance": {
        "vacuum_frequency": "weekly",
        "analyze_frequency": "daily",
        "backup_frequency": "daily"
    },
    "monitoring": {
        "slow_query_threshold": 1000,  # milliseconds
        "connection_pool_alerts": True,
        "disk_usage_alerts": True
    }
}
