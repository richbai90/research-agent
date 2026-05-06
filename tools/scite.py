import os
import httpx

from tools.base import BaseTool
from helpers.auth import extract_token_via_browser, invalidate_token


class SciteMCPTool(BaseTool):
    name = "scite_mcp_search"
    description = "Searches scientific literature using Scite's JSON-RPC endpoint."

    def __init__(self):
        self.client = None

    async def setup(self):
        # Initialize a single, reusable HTTP client for the tool's lifecycle
        self.client = httpx.AsyncClient(timeout=30.0)

    async def teardown(self):
        if self.client:
            await self.client.aclose()

    async def _get_valid_token(self) -> str:
        """Retrieves or generates a valid auth token."""
        token = os.getenv("SCITE_AUTH_TOKEN")
        if not token or token == "your_scite_token_here":
            token = await extract_token_via_browser()
        return token

    async def execute(
        self, query: str, limit: int = 15, sort: str = "relevance"
    ) -> str:
        while True:
            token = await self._get_valid_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/call",
                "params": {
                    "name": "search_literature",
                    "arguments": {"term": query, "limit": limit, "sort": sort},
                },
            }

            try:
                response = await self.client.post(
                    "https://api.scite.ai/mcp",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    raise ValueError(f"Scite API Error: {data['error']}")

                return str(data.get("result", data))

            except httpx.HTTPStatusError as e:
                if e.response.status_code in (401, 403):
                    print(
                        f"\n[Error] Token rejected (HTTP {e.response.status_code}). Extracting new token..."
                    )
                    invalidate_token()
                else:
                    print(f"\n[Error] HTTP {e.response.status_code}: {e.response.text}")
                    raise e
            except Exception as e:
                print(f"\n[Error] Connection failed: {e}")
                if "authentication" in str(e).lower() or "401" in str(e):
                    invalidate_token()
                else:
                    raise e
