import os
from typing import Any

try:
    from hindsight_client import Hindsight
except ImportError:
    Hindsight = None


class HindsightAdapter:
    """Official Hindsight client adapter.

    The application remains runnable in local demo mode when Hindsight is not
    configured. When HINDSIGHT_URL is set, this adapter uses the official
    Python client and its retain/recall/reflect operations.
    """

    def __init__(self):
        self.base_url = os.getenv("HINDSIGHT_URL", "").strip()
        self.api_key = os.getenv("HINDSIGHT_API_KEY", "").strip()
        self.bank_id = os.getenv("HINDSIGHT_BANK_ID", "mirrorline-demo")
        self.enabled = bool(self.base_url and Hindsight)

        self.client = None
        if self.enabled:
            kwargs = {"base_url": self.base_url}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            self.client = Hindsight(**kwargs)

    def status(self) -> dict[str, Any]:
        return {
            "configured": bool(self.base_url),
            "client_installed": Hindsight is not None,
            "enabled": self.enabled,
            "bank_id": self.bank_id,
        }

    async def retain(self, content: str) -> Any:
        if not self.enabled:
            return None
        return await self.client.aretain(
            bank_id=self.bank_id,
            content=content,
            tags=["mirrorline", "experience"],
        )

    async def recall(self, query: str) -> Any:
        if not self.enabled:
            return None
        return await self.client.arecall(
            bank_id=self.bank_id,
            query=query,
        )

    async def reflect(self, query: str) -> Any:
        if not self.enabled:
            return None
        return await self.client.areflect(
            bank_id=self.bank_id,
            query=query,
        )
