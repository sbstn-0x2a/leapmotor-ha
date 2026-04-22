"""Data coordinator for Leapmotor."""

from __future__ import annotations

from datetime import timedelta
import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LeapmotorApiClient, LeapmotorApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LeapmotorDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Fetch Leapmotor vehicle data."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        client: LeapmotorApiClient,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client
        self._lock_state_overrides: dict[str, tuple[bool, float]] = {}
        self._last_remote_results: dict[str, dict[str, Any]] = {}

    async def _async_update_data(self) -> dict:
        try:
            data = await self.hass.async_add_executor_job(self.client.fetch_data)
        except LeapmotorApiError as exc:
            raise UpdateFailed(str(exc)) from exc
        self._apply_lock_state_overrides(data)
        self._apply_remote_results(data)
        return data

    def set_lock_state_override(
        self,
        vin: str,
        is_locked: bool,
        *,
        ttl_seconds: int = 120,
    ) -> None:
        """Temporarily prefer confirmed remote-control state over stale cloud status."""
        self._lock_state_overrides[vin] = (is_locked, time.time() + ttl_seconds)
        if self.data:
            data = dict(self.data)
            self._apply_single_lock_override(data, vin, is_locked)
            self.async_set_updated_data(data)

    def record_remote_action(
        self,
        vin: str,
        action: str,
        *,
        success: bool,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """Store the last remote-control result for diagnostics and attributes."""
        remote_data = (result or {}).get("data") if isinstance(result, dict) else None
        info = {
            "action": action,
            "success": success,
            "status": "success" if success else "failed",
            "updated_at": time.time(),
            "api_code": (result or {}).get("code") if isinstance(result, dict) else None,
            "api_message": (result or {}).get("message") if isinstance(result, dict) else None,
            "remote_ctl_id": remote_data.get("remoteCtlId") if isinstance(remote_data, dict) else None,
            "error": error,
        }
        self._last_remote_results[vin] = info
        if self.data:
            data = dict(self.data)
            self._apply_single_remote_result(data, vin, info)
            self.async_set_updated_data(data)

    def _apply_lock_state_overrides(self, data: dict[str, Any]) -> None:
        """Apply non-expired optimistic lock states to freshly fetched data."""
        now = time.time()
        expired = [
            vin for vin, (_, expires_at) in self._lock_state_overrides.items()
            if expires_at <= now
        ]
        for vin in expired:
            self._lock_state_overrides.pop(vin, None)

        for vin, (is_locked, _) in self._lock_state_overrides.items():
            self._apply_single_lock_override(data, vin, is_locked)

    def _apply_remote_results(self, data: dict[str, Any]) -> None:
        """Apply remembered remote-control results to freshly fetched data."""
        for vin, info in self._last_remote_results.items():
            self._apply_single_remote_result(data, vin, info)

    @staticmethod
    def _apply_single_lock_override(
        data: dict[str, Any],
        vin: str,
        is_locked: bool,
    ) -> None:
        vehicle_data = (data.get("vehicles") or {}).get(vin)
        if not vehicle_data:
            return
        status = vehicle_data.setdefault("status", {})
        status["is_locked"] = is_locked
        status["lock_state_source"] = "remote_control_confirmed"

    @staticmethod
    def _apply_single_remote_result(
        data: dict[str, Any],
        vin: str,
        info: dict[str, Any],
    ) -> None:
        vehicle_data = (data.get("vehicles") or {}).get(vin)
        if not vehicle_data:
            return
        vehicle_data["remote_control"] = dict(info)
