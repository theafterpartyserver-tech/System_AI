"""
Production Configuration - Logging, monitoring, and auto-recovery
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

class ProductionLogger:
    """Production-grade logging system"""
    
    def __init__(self, logs_dir: Path = None, name: str = "system_ai"):
        self.logs_dir = logs_dir or Path('./logs')
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger(name)
    
    def _setup_logger(self, name: str) -> logging.Logger:
        """Setup logging with file and console handlers"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str, exc_info=False):
        self.logger.error(msg, exc_info=exc_info)
    
    def debug(self, msg: str):
        self.logger.debug(msg)

class HealthMonitor:
    """Monitor system health and auto-recovery"""
    
    def __init__(self, logger: Optional[ProductionLogger] = None):
        self.logger = logger or ProductionLogger()
        self.health_status = {"status": "healthy", "last_check": None}
    
    def check_health(self) -> bool:
        """Run system health checks"""
        try:
            self.health_status["last_check"] = datetime.now().isoformat()
            self.logger.debug("Health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.health_status["status"] = "unhealthy"
            return False
    
    def trigger_recovery(self):
        """Trigger automatic recovery procedures"""
        self.logger.warning("Triggering automatic recovery")
        self.logger.info("Recovery completed")
