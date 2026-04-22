"""Binary sensor entities for Leapmotor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LeapmotorDataUpdateCoordinator
from .entity_helpers import build_vehicle_display_name


@dataclass(frozen=True, kw_only=True)
class LeapmotorBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Leapmotor binary sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


BINARY_SENSOR_DESCRIPTIONS: tuple[LeapmotorBinarySensorEntityDescription, ...] = (
    LeapmotorBinarySensorEntityDescription(
        key="charging_planned_enabled",
        name="Geplantes Laden",
        icon="mdi:calendar-clock",
        value_fn=lambda data: data["charging"].get("charging_planned_enabled"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Leapmotor binary sensors."""
    coordinator: LeapmotorDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[LeapmotorBinarySensor] = []
    for vin in coordinator.data.get("vehicles", {}):
        entities.extend(
            LeapmotorBinarySensor(coordinator, vin, description)
            for description in BINARY_SENSOR_DESCRIPTIONS
        )
    async_add_entities(entities)


class LeapmotorBinarySensor(
    CoordinatorEntity[LeapmotorDataUpdateCoordinator],
    BinarySensorEntity,
):
    """Leapmotor binary sensor."""

    entity_description: LeapmotorBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: LeapmotorDataUpdateCoordinator,
        vin: str,
        description: LeapmotorBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.vin = vin
        self.entity_description = description
        self._attr_unique_id = f"{vin}_{description.key}"
        vehicle = self.vehicle_data["vehicle"]
        sensor_name = description.name or description.key
        self._attr_has_entity_name = True
        self._attr_name = sensor_name
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
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        value = self.entity_description.value_fn(self.vehicle_data)
        if value is None:
            return None
        return bool(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful vehicle metadata."""
        vehicle = self.vehicle_data["vehicle"]
        return {
            "vin": self.vin,
            "car_id": vehicle.get("car_id"),
            "car_type": vehicle.get("car_type"),
            "is_shared": vehicle.get("is_shared"),
        }
