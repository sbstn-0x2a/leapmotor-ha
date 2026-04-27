"""ABRP telemetry push support."""

from __future__ import annotations

import json
import time
from typing import Any

import requests

ABRP_TELEMETRY_URL = "https://api.iternio.com/1/tlm/send"
ABRP_TIMEOUT_SECONDS = 10


class AbrpTelemetryError(Exception):
    """ABRP telemetry submission failed."""


def build_abrp_telemetry(vehicle_data: dict[str, Any]) -> dict[str, Any]:
    """Build an ABRP Generic telemetry payload from normalized vehicle data."""
    status = vehicle_data.get("status") or {}
    location = vehicle_data.get("location") or {}
    charging = vehicle_data.get("charging") or {}

    telemetry: dict[str, Any] = {
        "utc": int(time.time()),
        "soc": _to_float(status.get("battery_percent")),
        "est_battery_range": _to_float(status.get("remaining_range_km")),
        "is_charging": bool(charging.get("is_charging")),
        "odometer": _to_float(status.get("odometer_km")),
        "speed": 0,
    }

    lat = _to_float(location.get("latitude"))
    lon = _to_float(location.get("longitude"))
    if (
        lat is not None
        and lon is not None
        and not (lat == 0 and lon == 0)
        and not location.get("location_is_stale")
    ):
        telemetry["lat"] = lat
        telemetry["lon"] = lon

    current = _to_float(charging.get("charging_current_a"))
    voltage = _to_float(charging.get("charging_voltage_v"))
    if current is not None:
        telemetry["current"] = current
    if voltage is not None:
        telemetry["voltage"] = voltage

    return {key: value for key, value in telemetry.items() if value is not None}


def send_abrp_telemetry(
    *,
    api_key: str,
    token: str,
    telemetry: dict[str, Any],
) -> dict[str, Any]:
    """Submit one telemetry sample to ABRP."""
    if not api_key.strip() or not token.strip():
        raise AbrpTelemetryError("ABRP API key and token are required.")
    if telemetry.get("soc") is None:
        raise AbrpTelemetryError("ABRP telemetry requires a state of charge.")

    response = requests.post(
        ABRP_TELEMETRY_URL,
        params={
            "api_key": api_key.strip(),
            "token": token.strip(),
            "tlm": json.dumps(telemetry, separators=(",", ":")),
        },
        timeout=ABRP_TIMEOUT_SECONDS,
    )
    text = response.text
    try:
        payload = response.json()
    except ValueError as exc:
        raise AbrpTelemetryError(f"Bad ABRP response: HTTP {response.status_code} {text}") from exc

    if response.status_code >= 400 or payload.get("status") != "ok":
        raise AbrpTelemetryError(f"ABRP rejected telemetry: HTTP {response.status_code} {text}")

    return {
        "http_status": response.status_code,
        "status": payload.get("status"),
        "missing": payload.get("missing"),
        "response": payload,
    }


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
