import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("security")

class SecurityMonitor:
    """
    Centralized security monitoring component.
    Detects threats based on log patterns and emits alerts.
    """
    def __init__(self):
        # We would typically use Redis or an in-memory DB to track 
        # failed login attempts by IP or user over a time window.
        self._failed_logins: Dict[str, list] = {}
        
    def log_failed_login(self, email: str, ip_address: Optional[str] = None):
        """Track failed logins to detect brute-force attempts."""
        key = ip_address or email
        now = datetime.utcnow()
        
        if key not in self._failed_logins:
            self._failed_logins[key] = []
            
        # Add new attempt and cleanup old ones (e.g. older than 15 mins)
        self._failed_logins[key].append(now)
        self._failed_logins[key] = [t for t in self._failed_logins[key] if (now - t).total_seconds() < 900]
        
        # If more than 10 attempts in 15 mins, trigger alert
        if len(self._failed_logins[key]) >= 10:
            self._trigger_alert("BRUTE_FORCE_DETECTED", {
                "target": email,
                "ip": ip_address,
                "attempts": len(self._failed_logins[key])
            })
            
    def _trigger_alert(self, alert_type: str, details: Dict[str, Any]):
        """Emit high priority security alert."""
        logger.critical(f"SECURITY ALERT [{alert_type}]: {details}")
        # Here we would integrate with PagerDuty, Slack, or email notifications
        
    def log_suspicious_activity(self, user_id: str, activity_type: str, details: str):
        """Log suspicious activities (e.g., accessing resources without permission multiple times)."""
        logger.warning(f"SUSPICIOUS ACTIVITY: User {user_id} - {activity_type}: {details}")

# Global instance
monitor = SecurityMonitor()
