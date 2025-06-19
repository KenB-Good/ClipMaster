
"""
Stream monitoring service wrapper
"""
import asyncio
from typing import Dict, Any, Optional
from databases import Database

from app.twitch.stream_monitor import StreamMonitor
import logging

logger = logging.getLogger(__name__)

class StreamMonitorService:
    def __init__(self):
        self.active_monitors: Dict[str, StreamMonitor] = {}
    
    async def start_monitoring(
        self, 
        integration_id: str, 
        db: Database,
        auto_capture: bool = True,
        chat_monitoring: bool = True
    ) -> bool:
        """Start monitoring for an integration"""
        try:
            if integration_id in self.active_monitors:
                logger.warning(f"Monitoring already active for integration {integration_id}")
                return False
            
            # Create and start monitor
            monitor = StreamMonitor(integration_id, db)
            self.active_monitors[integration_id] = monitor
            
            # Start monitoring in background
            asyncio.create_task(
                monitor.start_monitoring(
                    auto_capture=auto_capture,
                    chat_monitoring=chat_monitoring
                )
            )
            
            logger.info(f"Stream monitoring started for integration {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring for {integration_id}: {e}")
            if integration_id in self.active_monitors:
                del self.active_monitors[integration_id]
            return False
    
    async def stop_monitoring(self, integration_id: str) -> bool:
        """Stop monitoring for an integration"""
        try:
            if integration_id not in self.active_monitors:
                logger.warning(f"No active monitoring for integration {integration_id}")
                return False
            
            monitor = self.active_monitors[integration_id]
            await monitor.stop_monitoring()
            
            del self.active_monitors[integration_id]
            
            logger.info(f"Stream monitoring stopped for integration {integration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring for {integration_id}: {e}")
            return False
    
    def get_monitoring_status(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get monitoring status for an integration"""
        if integration_id not in self.active_monitors:
            return None
        
        monitor = self.active_monitors[integration_id]
        return monitor.get_monitoring_stats()
    
    def get_all_monitoring_status(self) -> Dict[str, Dict[str, Any]]:
        """Get monitoring status for all active integrations"""
        status = {}
        for integration_id, monitor in self.active_monitors.items():
            status[integration_id] = monitor.get_monitoring_stats()
        return status
    
    async def stop_all_monitoring(self):
        """Stop all active monitoring"""
        for integration_id in list(self.active_monitors.keys()):
            await self.stop_monitoring(integration_id)
    
    def get_active_count(self) -> int:
        """Get count of active monitors"""
        return len(self.active_monitors)

# Global instance
stream_monitor_service = StreamMonitorService()
