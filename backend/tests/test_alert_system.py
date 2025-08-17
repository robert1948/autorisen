"""
Integration Tests for Alert System (Task 1.3.6)
=================================================

Comprehensive tests for alert system functionality:
- Alert rule management
- Alert generation and lifecycle
- Notification channel testing
- Alert system integration
- Performance and reliability testing
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.alert_service import (
    get_alert_system,
    AlertRule,
    AlertSeverity,
    AlertType,
    AlertChannel,
    AlertStatus,
    NotificationChannel
)


class TestAlertSystem:
    """Test alert system core functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.alert_system = get_alert_system()
        self.client = TestClient(app)
        
        # Clear any existing alerts for clean testing
        self.alert_system.active_alerts.clear()
        self.alert_system.alert_history.clear()
    
    def test_alert_system_initialization(self):
        """Test alert system initializes with default rules and channels"""
        assert len(self.alert_system.alert_rules) > 0
        assert len(self.alert_system.notification_channels) > 0
        
        # Check for key default rules
        assert "high_error_rate" in self.alert_system.alert_rules
        assert "system_health_critical" in self.alert_system.alert_rules
        assert "high_cpu_usage" in self.alert_system.alert_rules
        
        # Check for default channels
        assert "log" in self.alert_system.notification_channels
        assert "email" in self.alert_system.notification_channels
        assert "webhook" in self.alert_system.notification_channels
    
    @pytest.mark.asyncio
    async def test_create_alert(self):
        """Test alert creation"""
        # Create a simple alert
        alert_id = await self.alert_system.create_alert(
            rule_name="high_error_rate",
            title="Test Alert",
            description="This is a test alert",
            source_data={"error_rate": 15.0}
        )
        
        assert alert_id is not None
        assert alert_id in self.alert_system.active_alerts
        
        alert = self.alert_system.active_alerts[alert_id]
        assert alert.title == "Test Alert"
        assert alert.description == "This is a test alert"
        assert alert.status == AlertStatus.ACTIVE
        assert alert.source_data["error_rate"] == 15.0
    
    @pytest.mark.asyncio
    async def test_alert_cooldown(self):
        """Test alert cooldown mechanism"""
        rule_name = "high_error_rate"
        
        # Create first alert
        alert_id1 = await self.alert_system.create_alert(
            rule_name=rule_name,
            title="First Alert",
            description="First test alert"
        )
        
        assert alert_id1 is not None
        
        # Try to create second alert immediately (should be blocked by cooldown)
        alert_id2 = await self.alert_system.create_alert(
            rule_name=rule_name,
            title="Second Alert",
            description="Second test alert"
        )
        
        assert alert_id2 is None  # Should be None due to cooldown
        assert len(self.alert_system.active_alerts) == 1
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        """Test alert acknowledgment"""
        # Create alert
        alert_id = await self.alert_system.create_alert(
            rule_name="high_error_rate",
            title="Test Alert",
            description="Test acknowledgment"
        )
        
        # Acknowledge alert
        success = await self.alert_system.acknowledge_alert(alert_id, "test_user")
        assert success
        
        alert = self.alert_system.active_alerts[alert_id]
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """Test alert resolution"""
        # Create alert
        alert_id = await self.alert_system.create_alert(
            rule_name="high_error_rate",
            title="Test Alert",
            description="Test resolution"
        )
        
        # Resolve alert
        success = await self.alert_system.resolve_alert(alert_id)
        assert success
        
        # Alert should be removed from active alerts
        assert alert_id not in self.alert_system.active_alerts
        
        # Alert should be in history
        history_alert = None
        for alert in self.alert_system.alert_history:
            if alert.id == alert_id:
                history_alert = alert
                break
        
        assert history_alert is not None
        assert history_alert.status == AlertStatus.RESOLVED
        assert history_alert.resolved_at is not None
    
    def test_add_custom_alert_rule(self):
        """Test adding custom alert rule"""
        custom_rule = AlertRule(
            name="custom_test_rule",
            alert_type=AlertType.CUSTOM,
            severity=AlertSeverity.WARNING,
            condition="custom_metric > threshold",
            threshold=100.0,
            duration=60,
            channels=[AlertChannel.LOG],
            tags=["custom", "test"]
        )
        
        self.alert_system.add_alert_rule(custom_rule)
        assert "custom_test_rule" in self.alert_system.alert_rules
        
        rule = self.alert_system.alert_rules["custom_test_rule"]
        assert rule.name == "custom_test_rule"
        assert rule.alert_type == AlertType.CUSTOM
        assert rule.threshold == 100.0
    
    def test_add_notification_channel(self):
        """Test adding custom notification channel"""
        custom_channel = NotificationChannel(
            name="custom_webhook",
            channel_type=AlertChannel.WEBHOOK,
            config={
                "url": "https://example.com/webhook",
                "headers": {"Authorization": "Bearer test-token"}
            },
            enabled=True
        )
        
        self.alert_system.add_notification_channel(custom_channel)
        assert "custom_webhook" in self.alert_system.notification_channels
        
        channel = self.alert_system.notification_channels["custom_webhook"]
        assert channel.name == "custom_webhook"
        assert channel.channel_type == AlertChannel.WEBHOOK
        assert channel.config["url"] == "https://example.com/webhook"
    
    def test_condition_evaluation(self):
        """Test alert condition evaluation"""
        rule = self.alert_system.alert_rules["high_error_rate"]
        
        # Test condition that should trigger
        data_trigger = {"error_rate": 15.0}
        assert self.alert_system._evaluate_condition(rule, data_trigger) == True
        
        # Test condition that should not trigger
        data_no_trigger = {"error_rate": 5.0}
        assert self.alert_system._evaluate_condition(rule, data_no_trigger) == False
    
    def test_get_active_alerts_filtering(self):
        """Test active alerts filtering"""
        # This test would need alerts to be created first
        # Using pytest fixture or setup would be ideal
        alerts = self.alert_system.get_active_alerts()
        assert isinstance(alerts, list)
        
        # Test filtering by severity
        critical_alerts = self.alert_system.get_active_alerts(severity=AlertSeverity.CRITICAL)
        assert isinstance(critical_alerts, list)
        
        # Test filtering by type
        error_alerts = self.alert_system.get_active_alerts(alert_type=AlertType.ERROR_RATE)
        assert isinstance(error_alerts, list)
    
    def test_alert_statistics(self):
        """Test alert statistics generation"""
        stats = self.alert_system.get_alert_statistics()
        
        assert "active_alerts" in stats
        assert "total_rules" in stats
        assert "enabled_rules" in stats
        assert "notification_channels" in stats
        assert "enabled_channels" in stats
        assert "severity_counts" in stats
        assert "type_counts" in stats
        assert "status_counts" in stats
        assert "recent_alerts_24h" in stats
        assert "alert_history_size" in stats
        
        assert isinstance(stats["active_alerts"], int)
        assert isinstance(stats["total_rules"], int)


class TestAlertNotifications:
    """Test alert notification system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.alert_system = get_alert_system()
    
    def test_log_notification(self):
        """Test log notification channel"""
        from app.services.alert_service import Alert
        
        test_alert = Alert(
            id="test_log_alert",
            rule_name="test_rule",
            alert_type=AlertType.CUSTOM,
            severity=AlertSeverity.INFO,
            title="Test Log Alert",
            description="Testing log notification",
            timestamp=datetime.utcnow()
        )
        
        success = self.alert_system._send_log_notification(test_alert)
        assert success == True
    
    @pytest.mark.asyncio
    async def test_email_notification_no_config(self):
        """Test email notification without configuration"""
        from app.services.alert_service import Alert
        
        test_alert = Alert(
            id="test_email_alert",
            rule_name="test_rule",
            alert_type=AlertType.CUSTOM,
            severity=AlertSeverity.WARNING,
            title="Test Email Alert",
            description="Testing email notification",
            timestamp=datetime.utcnow()
        )
        
        # Email channel without proper config should return False
        email_channel = self.alert_system.notification_channels["email"]
        original_config = email_channel.config.copy()
        
        # Clear email config
        email_channel.config["smtp_username"] = ""
        email_channel.config["to_emails"] = []
        
        success = await self.alert_system._send_email_notification(test_alert, email_channel)
        assert success == False
        
        # Restore original config
        email_channel.config = original_config
    
    @pytest.mark.asyncio
    async def test_webhook_notification_no_url(self):
        """Test webhook notification without URL"""
        from app.services.alert_service import Alert
        
        test_alert = Alert(
            id="test_webhook_alert",
            rule_name="test_rule",
            alert_type=AlertType.CUSTOM,
            severity=AlertSeverity.ERROR,
            title="Test Webhook Alert",
            description="Testing webhook notification",
            timestamp=datetime.utcnow()
        )
        
        # Webhook channel without URL should return False
        webhook_channel = self.alert_system.notification_channels["webhook"]
        original_config = webhook_channel.config.copy()
        
        # Clear webhook URL
        webhook_channel.config["url"] = ""
        
        success = await self.alert_system._send_webhook_notification(test_alert, webhook_channel)
        assert success == False
        
        # Restore original config
        webhook_channel.config = original_config


class TestAlertAPI:
    """Test alert system API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer test-token"}  # Mock auth
    
    def test_get_alert_status(self):
        """Test alert system status endpoint"""
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.get("/api/v1/alerts/status", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "status" in data
            assert "statistics" in data
            assert "monitoring_active" in data
    
    def test_get_active_alerts(self):
        """Test get active alerts endpoint"""
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.get("/api/v1/alerts/active", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "alerts" in data
            assert "count" in data
            assert "timestamp" in data
            assert isinstance(data["alerts"], list)
    
    def test_get_alert_rules(self):
        """Test get alert rules endpoint"""
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.get("/api/v1/alerts/rules", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "rules" in data
            assert "count" in data
            assert isinstance(data["rules"], list)
            assert len(data["rules"]) > 0
    
    def test_create_alert_rule(self):
        """Test create alert rule endpoint"""
        new_rule = {
            "name": "api_test_rule",
            "alert_type": "custom",
            "severity": "warning",
            "condition": "test_metric > threshold",
            "threshold": 50.0,
            "duration": 60,
            "channels": ["log"],
            "enabled": True,
            "tags": ["api", "test"]
        }
        
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.post(
                "/api/v1/alerts/rules",
                json=new_rule,
                headers=self.headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "message" in data
            assert "rule_name" in data
            assert data["rule_name"] == "api_test_rule"
    
    def test_get_notification_channels(self):
        """Test get notification channels endpoint"""
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.get("/api/v1/alerts/channels", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "channels" in data
            assert "count" in data
            assert isinstance(data["channels"], list)
            assert len(data["channels"]) > 0
    
    def test_get_alert_statistics(self):
        """Test get alert statistics endpoint"""
        with patch('app.core.auth.get_current_user', return_value={"username": "test"}):
            response = self.client.get("/api/v1/alerts/statistics", headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "statistics" in data
            assert "timestamp" in data
            
            stats = data["statistics"]
            assert "active_alerts" in stats
            assert "total_rules" in stats
            assert "enabled_rules" in stats


class TestAlertIntegration:
    """Test alert system integration with other components"""
    
    def setup_method(self):
        """Setup test environment"""
        self.alert_system = get_alert_system()
    
    @pytest.mark.asyncio
    async def test_health_service_integration(self):
        """Test alert system integration with health service"""
        # Mock health service to return degraded status
        with patch('app.services.health_service.get_health_service') as mock_health:
            mock_health_service = Mock()
            mock_health_service.run_comprehensive_health_check = AsyncMock(return_value={
                "overall_status": "degraded",
                "system_metrics": {
                    "cpu": {"percent": 85.0},
                    "memory": {"percent": 90.0},
                    "disk": {"percent": 75.0}
                },
                "application": {
                    "database_connected": True
                }
            })
            mock_health.return_value = mock_health_service
            
            # Check alert conditions (this would normally run in background)
            await self.alert_system._check_alert_conditions()
            
            # Verify that high CPU/memory alerts might be triggered
            # (depends on alert rules and thresholds)
    
    @pytest.mark.asyncio
    async def test_error_tracker_integration(self):
        """Test alert system integration with error tracker"""
        # Mock error tracker to return high error rate
        with patch('app.services.error_tracker.get_error_tracker') as mock_error:
            mock_error_tracker = Mock()
            mock_error_tracker.get_error_statistics = Mock(return_value={
                "error_rates": {"1min": 15.0},  # High error rate
                "errors_by_severity": {"critical": 2},
                "total_errors": 50
            })
            mock_error.return_value = mock_error_tracker
            
            # Check alert conditions
            await self.alert_system._check_alert_conditions()
            
            # High error rate should potentially trigger alerts


class TestAlertPerformance:
    """Test alert system performance and reliability"""
    
    def setup_method(self):
        """Setup test environment"""
        self.alert_system = get_alert_system()
    
    @pytest.mark.asyncio
    async def test_concurrent_alert_creation(self):
        """Test concurrent alert creation"""
        async def create_test_alert(i):
            return await self.alert_system.create_alert(
                rule_name="high_error_rate",
                title=f"Concurrent Test Alert {i}",
                description=f"Testing concurrent creation {i}"
            )
        
        # Create 10 concurrent alerts (first should succeed, others blocked by cooldown)
        tasks = [create_test_alert(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Only first alert should succeed due to cooldown
        successful_alerts = [r for r in results if r is not None and not isinstance(r, Exception)]
        assert len(successful_alerts) <= 1
    
    def test_large_number_of_rules(self):
        """Test performance with large number of alert rules"""
        # Add many alert rules
        for i in range(100):
            rule = AlertRule(
                name=f"performance_test_rule_{i}",
                alert_type=AlertType.CUSTOM,
                severity=AlertSeverity.INFO,
                condition="test_metric > threshold",
                threshold=float(i),
                duration=60,
                channels=[AlertChannel.LOG]
            )
            self.alert_system.add_alert_rule(rule)
        
        # Verify all rules are added
        assert len(self.alert_system.alert_rules) >= 100
        
        # Test statistics performance
        start_time = datetime.utcnow()
        stats = self.alert_system.get_alert_statistics()
        end_time = datetime.utcnow()
        
        # Should complete quickly even with many rules
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0  # Should complete in less than 1 second
        assert stats["total_rules"] >= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
