"""
Dedicated Metrics Provider - Decoupled from business logic

Provides system metrics without coupling to OpsCoordinator.
Uses async executor pattern and caching for efficiency.
"""
import psutil
import asyncio
from datetime import datetime
from typing import Dict, Any


class MetricsProvider:
    """Lightweight metrics provider for telemetry"""
    
    def __init__(self):
        self._cache_ttl = 5
        self._last_metrics = None
        self._last_update = None
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics with caching
        
        Runs psutil in executor to avoid blocking the event loop.
        Caches results for 5 seconds to reduce overhead.
        """
        now = datetime.now()
        
        if (self._last_metrics and self._last_update and 
            (now - self._last_update).total_seconds() < self._cache_ttl):
            return self._last_metrics
        
        loop = asyncio.get_event_loop()
        cpu = await loop.run_in_executor(None, psutil.cpu_percent, 0.5)
        mem = await loop.run_in_executor(None, lambda: psutil.virtual_memory().percent)
        disk = await loop.run_in_executor(None, lambda: psutil.disk_usage('/').percent)
        
        metrics = {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_percent": disk,
            "timestamp": now.isoformat()
        }
        
        self._last_metrics = metrics
        self._last_update = now
        
        return metrics


_metrics_provider = None


def get_metrics_provider() -> MetricsProvider:
    """Get singleton MetricsProvider instance"""
    global _metrics_provider
    if _metrics_provider is None:
        _metrics_provider = MetricsProvider()
    return _metrics_provider
