"""OAuth2 client credentials flow for Warcraft Logs API."""

import time
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN_URL = "https://www.warcraftlogs.com/oauth/token"


class WCLAuth:
    def __init__(self):
        self.client_id = os.getenv("WCL_CLIENT_ID")
        self.client_secret = os.getenv("WCL_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise EnvironmentError(
                "WCL_CLIENT_ID and WCL_CLIENT_SECRET must be set in .env"
            )
        self._token: str | None = None
        self._token_expiry: float = 0.0

    def get_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 300:
            return self._token

        for attempt in range(4):
            try:
                resp = httpx.post(
                    TOKEN_URL,
                    data={"grant_type": "client_credentials"},
                    auth=(self.client_id, self.client_secret),
                    timeout=30,
                )
                if resp.status_code in (502, 503, 504) and attempt < 3:
                    time.sleep(3 ** attempt)
                    continue
                resp.raise_for_status()
                break
            except httpx.TimeoutException:
                if attempt == 3:
                    raise
                time.sleep(3 ** attempt)
        data = resp.json()
        self._token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 3600)
        return self._token
