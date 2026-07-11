from app.services.base import BaseService
from app.services.mock_data_store import MockDataStore
from typing import Dict, Any

class GSTService(BaseService):
    def __init__(self):
        super().__init__("GST Service")
        
    async def get_gst_data(self, msme_id: str) -> Dict[str, Any]:
        """Fetches GST returns and turnover history for the specified MSME."""
        await self._simulate_delay()
        profile = MockDataStore.get_profile(msme_id)
        # Raise error if msme_id is empty or invalid specifically for error testing
        if not msme_id or msme_id == "error_trigger":
            from app.services.base import APIConnectionError
            raise APIConnectionError("GST Service failed to retrieve data for target entity.", 503)
        return profile["gst"]
