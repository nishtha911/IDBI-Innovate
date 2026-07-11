from app.services.base import BaseService
from app.services.mock_data_store import MockDataStore
from typing import Dict, Any

class UPIService(BaseService):
    def __init__(self):
        super().__init__("UPI Service")
        
    async def get_upi_data(self, msme_id: str) -> Dict[str, Any]:
        """Fetches UPI transaction velocity and volume details."""
        await self._simulate_delay()
        profile = MockDataStore.get_profile(msme_id)
        if not msme_id or msme_id == "error_trigger":
            from app.services.base import APIConnectionError
            raise APIConnectionError("UPI Service failed to retrieve transaction stats.", 503)
        return profile["upi"]
