"""Shared entity naming helpers for Leapmotor."""

from __future__ import annotations

from typing import Any


def build_vehicle_display_name(vehicle: dict[str, Any]) -> str:
    """Return a stable, user-friendly vehicle device name."""
    nickname = vehicle.get("nickname")
    car_type = vehicle.get("car_type") or "Vehicle"
    vin = vehicle.get("vin") or ""
    vin_suffix = str(vin)[-6:] if vin else ""

    if nickname:
        return f"Leapmotor {nickname}"
    if vin_suffix:
        return f"Leapmotor {car_type} {vin_suffix}"
    return f"Leapmotor {car_type}"
