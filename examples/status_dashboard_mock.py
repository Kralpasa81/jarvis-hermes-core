import json
from typing import List, Dict

class MonitoringDashboard:
    """Simple status monitoring dashboard mock data generator"""
    
    def generate_system_status(self) -> Dict:
        """Generate mock system status data"""
        return {
            "cpu_usage": "25%",
            "memory_usage": "45%",
            "disk_space": "120GB/500GB",
            "network_status": "connected",
            "last_update": "2024-08-13 11:30:00"
        }
    
    def generate_service_status(self, services: List[str]) -> Dict:
        """Generate mock service status data"""
        status_data = {}
        for service in services:
            status_data[service] = {
                "status": "running" if service != "database" else "stopped",
                "response_time": f"{10 + len(service)}ms",
                "error_count": 0 if service != "payment" else 2
            }
        return status_data
    
    def generate_alerts(self) -> List[Dict]:
        """Generate mock system alerts"""
        return [
            {
                "severity": "high",
                "message": "High memory usage detected",
                "timestamp": "2024-08-13 10:45:00"
            }
        ]
    
    def export_dashboard_data(self):
        """Export all dashboard data as JSON"""
        dashboard = {
            "system_status": self.generate_system_status(),
            "services": self.generate_service_status([
                "web_server", "database", "payment", "cache"
            ]),
            "alerts": self.generate_alerts()
        }
        return json.dumps(dashboard, indent=2)

if __name__ == "__main__":
    dashboard = MonitoringDashboard()
    print(dashboard.export_dashboard_data())