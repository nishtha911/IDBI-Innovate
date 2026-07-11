from app.services.base import BaseService
from app.services.mock_data_store import MockDataStore
from typing import Dict, Any

class BankService(BaseService):
    def __init__(self):
        super().__init__("Bank Service")
        
    async def get_bank_data(self, msme_id: str) -> Dict[str, Any]:
        """Fetches bank account balances, ledger transaction aggregates, and KYC status."""
        await self._simulate_delay()
        profile = MockDataStore.get_profile(msme_id)
        if not msme_id or msme_id == "error_trigger":
            from app.services.base import APIConnectionError
            raise APIConnectionError("Bank Statement open API timed out.", 504)
        return profile["bank"]
