from app.services.base import BaseService
from app.services.mock_data_store import MockDataStore
from typing import Dict, Any

class EPFOService(BaseService):
    def __init__(self):
        super().__init__("EPFO Service")
        
    async def get_epfo_data(self, msme_id: str) -> Dict[str, Any]:
        """Fetches EPFO payroll records and employer payment history."""
        await self._simulate_delay()
        profile = MockDataStore.get_profile(msme_id)
        if not msme_id or msme_id == "error_trigger":
            from app.services.base import APIConnectionError
            raise APIConnectionError("EPFO Sandbox API is not reachable.", 503)
        return profile["epfo"]
