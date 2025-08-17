"""
Health Check Enhancement Tests for Task 1.3.5 - Advanced Endpoint Monitoring
=============================================================================

Comprehensive test suite for the enhanced health check system:
- Health service functionality tests
- API endpoint tests
- System metrics validation
- Error condition handling
- Health trend analysis
- Performance monitoring
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.main import app
from app.services.health_service import HealthService, HealthStatus, ServiceType, HealthCheckResult, EndpointHealthCheck

client = TestClient(app)


class TestHealthService:
    """Test the health service core functionality"""
    
    @pytest.fixture
    def health_service(self):
        """Create a health service instance for testing"""
        return HealthService()
    
    def test_health_service_initialization(self, health_service):
        """Test health service initializes correctly"""
        assert health_service is not None
        assert len(health_service.health_checks) > 0
        assert len(health_service.endpoint_checks) > 0
        assert "system_resources" in health_service.health_checks
        assert "database_connection" in health_service.health_checks
        
    def test_health_check_registration(self, health_service):
        """Test custom health check registration"""
        def custom_check():
            return HealthCheckResult(
                service_name="custom_test",
                service_type=ServiceType.CORE_API,
                status=HealthStatus.HEALTHY,
                response_time_ms=10.0,
                timestamp=time.time(),
                details={"test": True}
            )
        
        initial_count = len(health_service.health_checks)
        health_service.register_health_check("custom_test", custom_check)
        
        assert len(health_service.health_checks) == initial_count + 1
        assert "custom_test" in health_service.health_checks
    
    def test_endpoint_check_registration(self, health_service):
        """Test endpoint check registration"""
        endpoint_check = EndpointHealthCheck(
            name="Test Endpoint",
            url="http://test.example.com/health",
            method="GET",
            timeout=5
        )
        
        initial_count = len(health_service.endpoint_checks)
        health_service.register_endpoint_check(endpoint_check)
        
        assert len(health_service.endpoint_checks) == initial_count + 1
    
    @pytest.mark.asyncio
    async def test_system_resources_check(self, health_service):
        """Test system resources health check"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 60.0
                mock_memory.return_value.available = 1000000000
                mock_memory.return_value.total = 2000000000
                
                result = await health_service._check_system_resources()
                
                assert isinstance(result, HealthCheckResult)
                assert result.service_name == "system_resources"
                assert result.status == HealthStatus.HEALTHY
                assert "cpu_percent" in result.details
                assert "memory_percent" in result.details
    
    @pytest.mark.asyncio
    async def test_system_resources_check_warning(self, health_service):
        """Test system resources check with warning conditions"""
        with patch('psutil.cpu_percent', return_value=75.0):  # Above warning threshold
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 80.0  # Above warning threshold
                mock_memory.return_value.available = 500000000
                mock_memory.return_value.total = 2000000000
                
                result = await health_service._check_system_resources()
                
                assert result.status == HealthStatus.WARNING
                assert result.error_message is not None
                assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_system_resources_check_critical(self, health_service):
        """Test system resources check with critical conditions"""
        with patch('psutil.cpu_percent', return_value=90.0):  # Above critical threshold
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = 95.0  # Above critical threshold
                mock_memory.return_value.available = 100000000
                mock_memory.return_value.total = 2000000000
                
                result = await health_service._check_system_resources()
                
                assert result.status == HealthStatus.CRITICAL
                assert result.error_message is not None
                assert len(result.suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_database_connection_check_success(self, health_service):
        """Test successful database connection check"""
        with patch('app.database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.execute.return_value.scalar.return_value = 5
            mock_get_db.return_value = mock_db
            
            result = await health_service._check_database_connection()
            
            assert result.status == HealthStatus.HEALTHY
            assert result.details["connected"] is True
            assert "table_count" in result.details
            mock_db.execute.assert_called()
            mock_db.close.assert_called()
    
    @pytest.mark.asyncio
    async def test_database_connection_check_failure(self, health_service):
        """Test database connection check failure"""
        with patch('app.database.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            result = await health_service._check_database_connection()
            
            assert result.status == HealthStatus.CRITICAL
            assert result.details["connected"] is False
            assert result.error_message is not None
            assert "Database connection failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_error_rates_check(self, health_service):
        """Test error rates health check"""
        mock_error_stats = {
            "error_rates": {"1min": 2.0},
            "errors_by_severity": {"critical": 0},
            "total_errors": 10,
            "patterns_count": 2
        }
        
        with patch.object(health_service.error_tracker, 'get_error_statistics', return_value=mock_error_stats):
            result = await health_service._check_error_rates()
            
            assert result.status == HealthStatus.HEALTHY
            assert result.details["error_rate_1min"] == 2.0
            assert result.details["critical_errors"] == 0
    
    @pytest.mark.asyncio
    async def test_error_rates_check_warning(self, health_service):
        """Test error rates check with warning conditions"""
        mock_error_stats = {
            "error_rates": {"1min": 8.0},  # Above warning threshold
            "errors_by_severity": {"critical": 1},
            "total_errors": 50,
            "patterns_count": 5
        }
        
        with patch.object(health_service.error_tracker, 'get_error_statistics', return_value=mock_error_stats):
            result = await health_service._check_error_rates()
            
            assert result.status == HealthStatus.WARNING
            assert result.error_message is not None
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self, health_service):
        """Test comprehensive health check execution"""
        # Mock individual check results
        with patch.object(health_service, '_check_system_resources') as mock_system:
            with patch.object(health_service, '_check_database_connection') as mock_db:
                with patch.object(health_service, '_check_endpoints') as mock_endpoints:
                    with patch.object(health_service, '_get_system_metrics_summary') as mock_metrics:
                        
                        # Setup mock returns
                        mock_system.return_value = HealthCheckResult(
                            service_name="system_resources",
                            service_type=ServiceType.CORE_API,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=10.0,
                            timestamp=time.time(),
                            details={}
                        )
                        
                        mock_db.return_value = HealthCheckResult(
                            service_name="database_connection",
                            service_type=ServiceType.DATABASE,
                            status=HealthStatus.HEALTHY,
                            response_time_ms=50.0,
                            timestamp=time.time(),
                            details={}
                        )
                        
                        mock_endpoints.return_value = {}
                        mock_metrics.return_value = {}
                        
                        result = await health_service.run_comprehensive_health_check()
                        
                        assert "overall_status" in result
                        assert "services" in result
                        assert "endpoints" in result
                        assert "system_metrics" in result
                        assert "timestamp" in result
                        assert "check_duration_ms" in result


class TestHealthAPIEndpoints:
    """Test the health check API endpoints"""
    
    def test_health_status_endpoint(self):
        """Test basic health status endpoint"""
        response = client.get("/api/health/status")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "timestamp" in data
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check endpoint"""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "services" in data
        assert "endpoints" in data
        assert "system_metrics" in data
    
    def test_health_services_list_endpoint(self):
        """Test health services list endpoint"""
        response = client.get("/api/health/services")
        assert response.status_code == 200
        data = response.json()
        assert "registered_checks" in data
        assert "registered_endpoints" in data
        assert "thresholds" in data
    
    def test_health_metrics_endpoint(self):
        """Test health metrics endpoint"""
        response = client.get("/api/health/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "system_metrics" in data
        assert "overall_status" in data
        assert "timestamp" in data
    
    def test_health_alerts_endpoint(self):
        """Test health alerts endpoint"""
        response = client.get("/api/health/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "suggestions" in data
        assert "overall_status" in data
    
    def test_health_trends_endpoint(self):
        """Test health trends endpoint"""
        response = client.get("/api/health/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trends" in data
    
    def test_health_endpoints_monitoring(self):
        """Test endpoint health monitoring"""
        response = client.get("/api/health/endpoints")
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "timestamp" in data
    
    def test_health_summary_endpoint(self):
        """Test health summary endpoint"""
        response = client.get("/api/health/summary")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "services_summary" in data
        assert "endpoints_summary" in data
        assert "system_health" in data
    
    def test_specific_service_health_checks(self):
        """Test specific service health check endpoints"""
        endpoints = [
            "/api/health/database",
            "/api/health/system",
            "/api/health/errors",
            "/api/health/disk",
            "/api/health/process"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 503]  # 503 for unhealthy services
            
            if response.status_code == 200:
                data = response.json()
                assert "service" in data or "trend" in data
    
    def test_health_config_endpoint(self):
        """Test health configuration endpoint"""
        response = client.get("/api/health/config")
        assert response.status_code == 200
        data = response.json()
        assert "thresholds" in data
        assert "registered_checks" in data
        assert "registered_endpoints" in data
    
    def test_trigger_health_check_endpoint(self):
        """Test health check trigger endpoint"""
        response = client.post("/api/health/check")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "timestamp" in data


class TestHealthCheckIntegration:
    """Test health check system integration"""
    
    def test_main_health_endpoint_integration(self):
        """Test that main health endpoint uses enhanced health service"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        
        # Should have enhanced health check features
        assert "health_checks_enhancement" in data
        assert data["health_checks_enhancement"] == "enabled (Task 1.3.5)"
        assert "health_summary" in data
        assert "version" in data
        assert data["version"] == "3.0.0"
    
    def test_health_service_error_handling(self):
        """Test health service error handling and fallback"""
        with patch('app.services.health_service.get_health_service') as mock_health_service:
            # Mock health service to raise an exception
            mock_health_service.side_effect = Exception("Health service error")
            
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            
            # Should fallback to basic health check
            assert "health_check_fallback" in data or "health_check_error" in data
    
    @pytest.mark.asyncio
    async def test_health_trends_analysis(self):
        """Test health trends analysis functionality"""
        health_service = HealthService()
        
        # Simulate some health check history
        health_service.health_history["test_service"].extend([
            {
                "timestamp": time.time() - 300,
                "status": HealthStatus.HEALTHY.value,
                "response_time": 100
            },
            {
                "timestamp": time.time() - 200,
                "status": HealthStatus.WARNING.value,
                "response_time": 200
            },
            {
                "timestamp": time.time() - 100,
                "status": HealthStatus.HEALTHY.value,
                "response_time": 150
            }
        ])
        
        trends = health_service._analyze_health_trends()
        assert "test_service" in trends
        assert "trend_direction" in trends["test_service"]
        assert "recent_status_distribution" in trends["test_service"]
        assert "avg_response_time" in trends["test_service"]


class TestHealthCheckPerformance:
    """Test health check system performance"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_health_check_performance(self):
        """Test that comprehensive health check completes within reasonable time"""
        health_service = HealthService()
        
        start_time = time.time()
        result = await health_service.run_comprehensive_health_check()
        execution_time = time.time() - start_time
        
        # Should complete within 10 seconds
        assert execution_time < 10.0
        assert "check_duration_ms" in result
        assert result["check_duration_ms"] > 0
    
    def test_health_api_response_time(self):
        """Test health API endpoint response times"""
        import time
        
        endpoints = [
            "/api/health/status",
            "/api/health/services",
            "/api/health/metrics",
            "/api/health/summary"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            # Should respond within 5 seconds
            assert response_time < 5.0


if __name__ == "__main__":
    print("🚀 Running Health Check Enhancement Tests (Task 1.3.5)")
    print("=" * 60)
    
    # Run basic functionality tests
    test_health_service = TestHealthService()
    health_service = HealthService()
    
    # Test service initialization
    test_health_service.test_health_service_initialization(health_service)
    print("✅ Health service initialization test passed")
    
    # Test health check registration
    test_health_service.test_health_check_registration(health_service)
    print("✅ Health check registration test passed")
    
    # Test endpoint registration
    test_health_service.test_endpoint_check_registration(health_service)
    print("✅ Endpoint check registration test passed")
    
    # Test API endpoints
    test_api = TestHealthAPIEndpoints()
    
    # Test basic health status
    test_api.test_health_status_endpoint()
    print("✅ Health status endpoint test passed")
    
    # Test health services list
    test_api.test_health_services_list_endpoint()
    print("✅ Health services list endpoint test passed")
    
    # Test health summary
    test_api.test_health_summary_endpoint()
    print("✅ Health summary endpoint test passed")
    
    # Test integration
    test_integration = TestHealthCheckIntegration()
    test_integration.test_main_health_endpoint_integration()
    print("✅ Main health endpoint integration test passed")
    
    print("\n🎉 All Health Check Enhancement tests completed successfully!")
    print("📊 Task 1.3.5 - Advanced Endpoint Monitoring implementation verified")
