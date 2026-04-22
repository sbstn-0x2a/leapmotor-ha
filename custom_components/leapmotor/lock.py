"""Lock entity for Leapmotor vehicle state and control."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import LeapmotorApiError
from .const import DOMAIN
from .coordinator import LeapmotorDataUpdateCoordinator
from .entity_helpers import build_vehicle_display_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Leapmotor lock entities."""
    coordinator: LeapmotorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LeapmotorVehicleLock(coordinator, vin) for vin in coordinator.data.get("vehicles", {})
    )


class LeapmotorVehicleLock(CoordinatorEntity[LeapmotorDataUpdateCoordinator], LockEntity):
    """Vehicle lock control with clear locked/unlocked semantics."""

    _attr_has_entity_name = True
    _attr_translation_key = "vehicle_lock"

    def __init__(self, coordinator: LeapmotorDataUpdateCoordinator, vin: str) -> None:
        super().__init__(coordinator)
        self.vin = vin
        self._attr_unique_id = f"{vin}_vehicle_lock"
        vehicle = self.vehicle_data["vehicle"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="Leapmotor",
            model=vehicle.get("car_type"),
            name=build_vehicle_display_name(vehicle),
            serial_number=vin,
        )

    @property
    def vehicle_data(self) -> dict[str, Any]:
        """Return current data for this vehicle."""
        return self.coordinator.data["vehicles"][self.vin]

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return super().available and bool(self.vehicle_data["status"].get("is_locked") is not None)

    @property
    def is_locked(self) -> bool | None:
        """Return lock state."""
        value = self.vehicle_data["status"].get("is_locked")
        if value is None:
            return None
        return bool(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful vehicle metadata."""
        vehicle = self.vehicle_data["vehicle"]
        remote = self.vehicle_data.get("remote_control") or {}
        return {
            "vin": self.vin,
            "car_id": vehicle.get("car_id"),
            "car_type": vehicle.get("car_type"),
            "is_shared": vehicle.get("is_shared"),
            "raw_lock_status_code": self.vehicle_data["status"].get("raw_lock_status_code"),
            "lock_state_source": self.vehicle_data["status"].get("lock_state_source", "cloud"),
            "operation_password_configured": bool(self.coordinator.client.operation_password),
            "last_remote_action": remote.get("action"),
            "last_remote_status": remote.get("status"),
            "last_remote_success": remote.get("success"),
            "last_remote_updated_at": remote.get("updated_at"),
            "last_remote_error": remote.get("error"),
        }

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the vehicle."""
        cooldown = self.coordinator.remote_action_cooldown_remaining(self.vin)
        if cooldown:
            raise HomeAssistantError(
                f"Remote action cooldown active. Try again in {cooldown} seconds."
            )
        if not self.coordinator.client.operation_password:
            raise HomeAssistantError(
                "Vehicle PIN is not configured. Read-only lock state is available, "
                "but lock control requires the PIN."
            )
        try:
            result = await self.hass.async_add_executor_job(self.coordinator.client.lock_vehicle, self.vin)
        except LeapmotorApiError as exc:
            self.coordinator.record_remote_action(
                self.vin,
                "lock",
                success=False,
                error=str(exc),
            )
            raise HomeAssistantError(str(exc)) from exc
        self.coordinator.record_remote_action(self.vin, "lock", success=True, result=result)
        self.coordinator.set_lock_state_override(self.vin, True)
        await self.coordinator.async_request_refresh()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the vehicle."""
        cooldown = self.coordinator.remote_action_cooldown_remaining(self.vin)
        if cooldown:
            raise HomeAssistantError(
                f"Remote action cooldown active. Try again in {cooldown} seconds."
            )
        if not self.coordinator.client.operation_password:
            raise HomeAssistantError(
                "Vehicle PIN is not configured. Read-only lock state is available, "
                "but unlock control requires the PIN."
            )
        try:
            result = await self.hass.async_add_executor_job(self.coordinator.client.unlock_vehicle, self.vin)
        except LeapmotorApiError as exc:
            self.coordinator.record_remote_action(
                self.vin,
                "unlock",
                success=False,
                error=str(exc),
            )
            raise HomeAssistantError(str(exc)) from exc
        self.coordinator.record_remote_action(self.vin, "unlock", success=True, result=result)
        self.coordinator.set_lock_state_override(self.vin, False)
        await self.coordinator.async_request_refresh()
