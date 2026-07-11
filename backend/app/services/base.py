import asyncio
from app.core.config import settings

class ServiceError(Exception):
    """Base exception for all service adapters."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class APIConnectionError(ServiceError):
    """Raised when there is an issue connecting to the upstream API."""
    pass

class BaseService:
    def __init__(self, service_name: str):
        self.service_name = service_name

    async def _simulate_delay(self):
        """Simulates latency of remote API calls based on config."""
        if settings.ENABLE_MOCK_DELAY and settings.MOCK_DELAY_SECONDS > 0:
            await asyncio.sleep(settings.MOCK_DELAY_SECONDS)
