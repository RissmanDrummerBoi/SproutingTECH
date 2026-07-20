"""
Client for the TerraClim API (https://api.terraclim.co.za).

TerraClim provides interpolated raster climate layers for South Africa,
queryable by point or polygon. Relevant to us: daily reference
evapotranspiration (`data_type=eto`, `extent=sa`).

Important — TerraClim does NOT provide actual evapotranspiration (ETa).
ETa here is modeled from ETo × a grapevine crop coefficient
(see crop_coefficients.py) and calibrated against FruitLook / pressure-bomb
readings where available. That mirrors how growers already reason about it.

Confirmed from TerraClim's public docs (api.terraclim.co.za/docs/):
  - Auth: a bearer token issued by TerraClim (email hello@terraclim.co.za).
    The docs don't publish the exact header scheme — this client assumes
    `Authorization: Token <token>` (the DRF TokenAuthentication convention).
    If your token rejects that, check the header TerraClim's onboarding
    email specifies and adjust AUTH_SCHEME below — it's the only place
    that needs to change.
  - Endpoints referenced in their docs: /detail/point/, /detail/polygon/,
    /detail/nearest/, /detail/poly_agg/ — those are documentation pages;
    the actual query endpoints live under /api/v1/. This client targets
    /api/v1/point/, which is the standard REST convention for their
    structure, but confirm against /api/v1/redoc/ once you have a token
    (that page needs a browser — it didn't render over a plain fetch).
  - Rate limits: 5 requests/sec burst, 50 requests/day sustained, and a
    daily-resolution query is capped at 15 days per request. This client
    chunks date ranges and throttles accordingly.
  - Points: WKT `POINT(lon lat)` (WGS84), up to 10 points per query.
"""
import os
import time
from collections import deque
from datetime import date, timedelta
from typing import Optional

import requests

BASE_URL = os.getenv("TERRACLIM_BASE_URL", "https://api.terraclim.co.za")
AUTH_SCHEME = os.getenv("TERRACLIM_AUTH_SCHEME", "Token")  # see note above

MAX_POINTS_PER_QUERY = 10
MAX_DAYS_PER_QUERY = 15
BURST_LIMIT_PER_SEC = 5
DAILY_QUERY_LIMIT = 50


class TerraClimRateLimitError(RuntimeError):
    pass


class TerraClimClient:
    def __init__(self, token: Optional[str] = None, base_url: str = BASE_URL):
        self.token = token or os.getenv("TERRACLIM_API_TOKEN")
        if not self.token:
            raise RuntimeError(
                "TERRACLIM_API_TOKEN not set. Request a token from "
                "hello@terraclim.co.za and add it to your .env file."
            )
        self.base_url = base_url.rstrip("/")
        self._recent_calls = deque()   # timestamps, for burst limiting
        self._calls_today = 0
        self._calls_today_date = date.today()

    # -- rate limiting -----------------------------------------------
    def _throttle(self):
        now = time.monotonic()
        while self._recent_calls and now - self._recent_calls[0] > 1.0:
            self._recent_calls.popleft()
        if len(self._recent_calls) >= BURST_LIMIT_PER_SEC:
            time.sleep(1.0 - (now - self._recent_calls[0]))
        self._recent_calls.append(time.monotonic())

        if date.today() != self._calls_today_date:
            self._calls_today_date = date.today()
            self._calls_today = 0
        if self._calls_today >= DAILY_QUERY_LIMIT:
            raise TerraClimRateLimitError(
                f"Hit TerraClim's {DAILY_QUERY_LIMIT}/day query limit. "
                "Try again tomorrow, or batch fewer blocks per call."
            )
        self._calls_today += 1

    # -- date chunking -------------------------------------------------
    @staticmethod
    def _chunk_date_range(start: date, end: date, max_days=MAX_DAYS_PER_QUERY):
        chunk_start = start
        while chunk_start <= end:
            chunk_end = min(chunk_start + timedelta(days=max_days - 1), end)
            yield chunk_start, chunk_end
            chunk_start = chunk_end + timedelta(days=1)

    @staticmethod
    def _chunk_points(points, size=MAX_POINTS_PER_QUERY):
        for i in range(0, len(points), size):
            yield points[i : i + size]

    # -- API call --------------------------------------------------------
    def _get(self, path: str, params: dict):
        self._throttle()
        headers = {"Authorization": f"{AUTH_SCHEME} {self.token}"}
        resp = requests.get(f"{self.base_url}{path}", params=params, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_daily_eto(
        self, points: list[tuple[float, float]], start: date, end: date
    ) -> dict:
        """
        points: list of (lat, lon) tuples, one per vineyard block, in the
        same order you want results returned.

        Returns: {point_index: {iso_date: eto_mm}}

        NOTE ON RESPONSE PARSING: the exact JSON shape TerraClim returns
        isn't confirmed from their public docs (their query-examples page
        needs a live token + browser to render). This method normalizes a
        few plausible shapes (a list of per-point series, or a flat list
        of {point, date, value} records) — if your account's response
        looks different, the `_normalize_response` method below is the
        only place that needs adjusting.
        """
        results: dict[int, dict] = {i: {} for i in range(len(points))}

        for point_batch_start in range(0, len(points), MAX_POINTS_PER_QUERY):
            batch = points[point_batch_start : point_batch_start + MAX_POINTS_PER_QUERY]
            wkt = ",".join(f"POINT({lon} {lat})" for lat, lon in batch)

            for chunk_start, chunk_end in self._chunk_date_range(start, end):
                data = self._get(
                    "/api/v1/point/",
                    params={
                        "point": wkt,
                        "data_type": "eto",
                        "extent": "sa",
                        "time_scale": "daily",
                        "start_date": chunk_start.isoformat(),
                        "end_date": chunk_end.isoformat(),
                    },
                )
                for local_idx, day_values in self._normalize_response(data, len(batch)).items():
                    results[point_batch_start + local_idx].update(day_values)

        return results

    @staticmethod
    def _normalize_response(data, n_points: int) -> dict[int, dict]:
        """Best-effort normalization — adjust to match your account's actual schema."""
        out: dict[int, dict] = {i: {} for i in range(n_points)}

        if isinstance(data, list) and data and isinstance(data[0], dict) and "series" in data[0]:
            # shape: [{"point_index": 0, "series": [{"date": "...", "value": ...}, ...]}, ...]
            for entry in data:
                idx = entry.get("point_index", 0)
                for point_ in entry.get("series", []):
                    out[idx][point_["date"]] = point_["value"]
            return out

        if isinstance(data, list) and data and isinstance(data[0], dict) and "date" in data[0]:
            # shape: flat list of {"point_index": 0, "date": "...", "eto": ...}
            for rec in data:
                idx = rec.get("point_index", 0)
                out[idx][rec["date"]] = rec.get("eto", rec.get("value"))
            return out

        raise ValueError(
            "Unrecognized TerraClim response shape — inspect the raw payload "
            "and update TerraClimClient._normalize_response to match it: "
            f"{str(data)[:500]}"
        )
