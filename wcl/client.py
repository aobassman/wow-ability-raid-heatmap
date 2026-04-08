"""GraphQL client for Warcraft Logs API v2 with rate limiting and caching."""

import time
import json
import hashlib
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console

from .auth import WCLAuth

API_URL = "https://www.warcraftlogs.com/api/v2/client"
CACHE_DIR = Path(__file__).parent.parent / ".cache"
POINTS_PER_HOUR = 3600
console = Console(stderr=True)


class WCLClient:
    def __init__(self, cache: bool = True):
        self.auth = WCLAuth()
        self.cache = cache
        self._points_used = 0
        self._window_start = time.time()
        CACHE_DIR.mkdir(exist_ok=True)

    def _cache_path(self, query: str, variables: dict) -> Path:
        key = hashlib.md5(f"{query}{json.dumps(variables, sort_keys=True)}".encode()).hexdigest()
        return CACHE_DIR / f"{key}.json"

    def _load_cache(self, query: str, variables: dict) -> Any | None:
        if not self.cache:
            return None
        path = self._cache_path(query, variables)
        if path.exists():
            return json.loads(path.read_text())
        return None

    def _save_cache(self, query: str, variables: dict, data: Any) -> None:
        if not self.cache:
            return
        path = self._cache_path(query, variables)
        path.write_text(json.dumps(data))

    def _throttle(self) -> None:
        """Pause if approaching rate limit."""
        elapsed = time.time() - self._window_start
        if elapsed >= 3600:
            self._points_used = 0
            self._window_start = time.time()
            return
        if self._points_used >= POINTS_PER_HOUR - 50:
            wait = 3600 - elapsed + 5
            console.log(f"[yellow]Rate limit approaching — waiting {wait:.0f}s[/yellow]")
            time.sleep(wait)
            self._points_used = 0
            self._window_start = time.time()

    def query(self, query: str, variables: dict | None = None) -> dict:
        variables = variables or {}
        cached = self._load_cache(query, variables)
        if cached is not None:
            return cached

        self._throttle()
        token = self.auth.get_token()

        for attempt in range(4):
            try:
                resp = httpx.post(
                    API_URL,
                    json={"query": query, "variables": variables},
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )
                if resp.status_code == 429 and attempt < 3:
                    wait = 60 * (attempt + 1)
                    console.log(f"[yellow]WCL API 429 rate limit — waiting {wait}s (attempt {attempt+1}/4)[/yellow]")
                    time.sleep(wait)
                    continue
                if resp.status_code in (500, 502, 503, 504) and attempt < 3:
                    wait = 2 ** attempt
                    console.log(f"[yellow]WCL API {resp.status_code} — retrying in {wait}s (attempt {attempt+1}/4)[/yellow]")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            except httpx.TimeoutException:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)

        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")

        self._points_used += 1
        self._save_cache(query, variables, data)
        return data

    def query_all_events(
        self,
        report_code: str,
        fight_id: int,
        data_type: str,
        source_id: int | None = None,
        start_time: int = 0,
        end_time: int = 9_999_999,
        filter_expression: str | None = None,
        hostility: int | None = None,
    ) -> list[dict]:
        """Fetch all events from a fight, paginating through all pages."""
        all_events: list[dict] = []
        current_start = start_time

        filter_part = f'filterExpression: "{filter_expression}"' if filter_expression else ""
        source_part = f"sourceID: {source_id}" if source_id is not None else ""
        hostility_part = f"hostilityType: {hostility}" if hostility is not None else ""  # pass "Enemies" or "Friendlies"

        while True:
            q = f"""
            query {{
              reportData {{
                report(code: "{report_code}") {{
                  events(
                    fightIDs: [{fight_id}]
                    dataType: {data_type}
                    startTime: {current_start}
                    endTime: {end_time}
                    {source_part}
                    {hostility_part}
                    {filter_part}
                    limit: 300
                  ) {{
                    data
                    nextPageTimestamp
                  }}
                }}
              }}
            }}
            """
            result = self.query(q)
            events_block = result["data"]["reportData"]["report"]["events"]
            page = events_block.get("data", [])
            all_events.extend(page)

            next_ts = events_block.get("nextPageTimestamp")
            if not next_ts:
                break
            current_start = next_ts

        return all_events
