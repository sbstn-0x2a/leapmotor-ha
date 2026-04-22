"""Diagnostics support for the Leapmotor integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_REDACTED = "**REDACTED**"
_SENSITIVE_KEYS = {
    "password",
    "operation_password",
    "account_p12_password",
    "token",
    "refreshToken",
    "refresh_token",
    "base64Cert",
    "sign",
    "signIkm",
    "signSalt",
    "signInfo",
    "gigyaSessionToken",
    "gigyaSessionSecret",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return sanitized diagnostics for support."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    vehicles = {}
    if coordinator and coordinator.data:
        for vin, vehicle_data in (coordinator.data.get("vehicles") or {}).items():
            vehicle = vehicle_data.get("vehicle") or {}
            status = vehicle_data.get("status") or {}
            remote = vehicle_data.get("remote_control") or {}
            vehicles[_redact_vin(vin)] = {
                "vehicle": {
                    "vin": _redact_vin(vin),
                    "car_id": vehicle.get("car_id"),
                    "car_type": vehicle.get("car_type"),
                    "nickname": vehicle.get("nickname"),
                    "is_shared": vehicle.get("is_shared"),
                },
                "status": {
                    "vehicle_state": status.get("vehicle_state"),
                    "is_parked": status.get("is_parked"),
                    "is_locked": status.get("is_locked"),
                    "raw_lock_status_code": status.get("raw_lock_status_code"),
                    "raw_charge_status_code": status.get("raw_charge_status_code"),
                    "raw_drive_status_code": status.get("raw_drive_status_code"),
                    "raw_vehicle_state_code": status.get("raw_vehicle_state_code"),
                    "last_vehicle_timestamp": status.get("last_vehicle_timestamp"),
                },
                "remote_control": remote,
            }

    client = getattr(coordinator, "client", None) if coordinator else None
    static_cert = getattr(client, "static_cert", None)
    static_key = getattr(client, "static_key", None)
    return {
        "entry": _redact(
            {
                "title": entry.title,
                "data": dict(entry.data),
                "options": dict(entry.options),
            }
        ),
        "client": {
            "user_id": getattr(client, "user_id", None),
            "app_cert_present": Path(static_cert).exists() if static_cert else None,
            "app_key_present": Path(static_key).exists() if static_key else None,
            "account_cert_loaded": bool(getattr(client, "account_cert_file", None)),
            "account_p12_password_source": getattr(client, "account_p12_password_source", None),
            "operation_password_configured": bool(getattr(client, "operation_password", None)),
            "last_api_results": getattr(client, "last_api_results", {}),
        },
        "vehicles": vehicles,
    }


def _redact(value: Any) -> Any:
    """Recursively redact secrets from diagnostics."""
    if isinstance(value, dict):
        return {
            key: _REDACTED if str(key) in _SENSITIVE_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _redact_vin(vin: str) -> str:
    """Redact VIN while keeping enough suffix for support correlation."""
    if not vin:
        return ""
    return f"***{str(vin)[-6:]}"
