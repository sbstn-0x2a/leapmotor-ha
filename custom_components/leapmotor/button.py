"""Button entities for Leapmotor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import LeapmotorApiError
from .const import (
    DOMAIN,
    REMOTE_CTL_AC_SWITCH,
    REMOTE_CTL_BATTERY_PREHEAT,
    REMOTE_CTL_FIND_CAR,
    REMOTE_CTL_QUICK_COOL,
    REMOTE_CTL_QUICK_HEAT,
    REMOTE_CTL_SUNSHADE,
    REMOTE_CTL_TRUNK,
    REMOTE_CTL_WINDSHIELD_DEFROST,
    REMOTE_CTL_WINDOWS,
)
from .coordinator import LeapmotorDataUpdateCoordinator
from .entity_helpers import build_vehicle_display_name


@dataclass(frozen=True, slots=True)
class ButtonSpec:
    """Description of one exposed remote-control button."""

    action: str
    translation_key: str
    icon: str
    method_name: str


BUTTON_SPECS: tuple[ButtonSpec, ...] = (
    ButtonSpec(
        action=REMOTE_CTL_TRUNK,
        translation_key="open_trunk",
        icon="mdi:car-back",
        method_name="open_trunk",
    ),
    ButtonSpec(
        action=REMOTE_CTL_FIND_CAR,
        translation_key="find_vehicle",
        icon="mdi:bullhorn",
        method_name="find_vehicle",
    ),
    ButtonSpec(
        action=REMOTE_CTL_SUNSHADE,
        translation_key="sunshade_action",
        icon="mdi:blinds-open",
        method_name="control_sunshade",
    ),
    ButtonSpec(
        action=REMOTE_CTL_BATTERY_PREHEAT,
        translation_key="battery_preheat",
        icon="mdi:battery-charging",
        method_name="battery_preheat",
    ),
    ButtonSpec(
        action=REMOTE_CTL_WINDOWS,
        translation_key="windows",
        icon="mdi:window-open",
        method_name="windows",
    ),
    ButtonSpec(
        action=REMOTE_CTL_AC_SWITCH,
        translation_key="ac_switch",
        icon="mdi:air-conditioner",
        method_name="ac_switch",
    ),
    ButtonSpec(
        action=REMOTE_CTL_QUICK_COOL,
        translation_key="quick_cool",
        icon="mdi:snowflake",
        method_name="quick_cool",
    ),
    ButtonSpec(
        action=REMOTE_CTL_QUICK_HEAT,
        translation_key="quick_heat",
        icon="mdi:fire",
        method_name="quick_heat",
    ),
    ButtonSpec(
        action=REMOTE_CTL_WINDSHIELD_DEFROST,
        translation_key="windshield_defrost",
        icon="mdi:car-defrost-front",
        method_name="windshield_defrost",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Leapmotor buttons."""
    coordinator: LeapmotorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[LeapmotorActionButton] = []
    for vin in coordinator.data.get("vehicles", {}):
        for spec in BUTTON_SPECS:
            entities.append(LeapmotorActionButton(coordinator, vin, spec))
    async_add_entities(entities)


class LeapmotorActionButton(CoordinatorEntity[LeapmotorDataUpdateCoordinator], ButtonEntity):
    """Leapmotor remote-control button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LeapmotorDataUpdateCoordinator,
        vin: str,
        spec: ButtonSpec,
    ) -> None:
        super().__init__(coordinator)
        self.vin = vin
        self.spec = spec
        self._attr_translation_key = spec.translation_key
        self._attr_icon = spec.icon
        self._attr_unique_id = f"{vin}_{spec.action}"

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
        """Return button availability."""
        return super().available and bool(self.coordinator.client.operation_password)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return control metadata."""
        vehicle = self.vehicle_data["vehicle"]
        remote = self.vehicle_data.get("remote_control") or {}
        return {
            "vin": self.vin,
            "action": self.spec.action,
            "operation_password_configured": bool(self.coordinator.client.operation_password),
            "last_remote_action": remote.get("action"),
            "last_remote_status": remote.get("status"),
            "last_remote_success": remote.get("success"),
            "last_remote_updated_at": remote.get("updated_at"),
            "last_remote_error": remote.get("error"),
            "car_type": vehicle.get("car_type"),
            "is_shared": vehicle.get("is_shared"),
        }

    async def async_press(self) -> None:
        """Execute the configured remote-control action."""
        method = getattr(self.coordinator.client, self.spec.method_name)
        try:
            result = await self.hass.async_add_executor_job(method, self.vin)
        except LeapmotorApiError as exc:
            self.coordinator.record_remote_action(
                self.vin,
                self.spec.action,
                success=False,
                error=str(exc),
            )
            raise HomeAssistantError(str(exc)) from exc
        self.coordinator.record_remote_action(
            self.vin,
            self.spec.action,
            success=True,
            result=result,
        )
        await self.coordinator.async_request_refresh()
