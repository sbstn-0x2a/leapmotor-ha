"""Config flow for the Leapmotor integration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components.file_upload import process_uploaded_file
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .api import (
    LeapmotorAccountCertError,
    LeapmotorApiClient,
    LeapmotorApiError,
    LeapmotorAuthError,
    LeapmotorMissingAppCertError,
)
from .const import (
    CONF_APP_CERT_FILE,
    CONF_APP_CERT_PEM,
    CONF_APP_KEY_FILE,
    CONF_APP_KEY_PEM,
    CONF_OPERATION_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    STATIC_APP_CERT,
    STATIC_APP_KEY,
)


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_APP_CERT_FILE): selector.FileSelector(
            selector.FileSelectorConfig(accept=".pem,.crt,.cert")
        ),
        vol.Optional(CONF_APP_KEY_FILE): selector.FileSelector(
            selector.FileSelectorConfig(accept=".pem,.key")
        ),
        vol.Optional(CONF_APP_CERT_PEM, default=""): selector.TextSelector(
            selector.TextSelectorConfig(multiline=True)
        ),
        vol.Optional(CONF_APP_KEY_PEM, default=""): selector.TextSelector(
            selector.TextSelectorConfig(multiline=True)
        ),
        vol.Optional(CONF_OPERATION_PASSWORD, default=""): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL_MINUTES): vol.All(
            vol.Coerce(int),
            vol.Range(min=1, max=120),
        ),
    }
)


def _write_pem_if_provided(path: Path, value: str, marker: str, mode: int) -> None:
    pem = value.strip().replace("\\n", "\n")
    if not pem:
        return
    if marker not in pem:
        raise ValueError(f"Invalid PEM content for {path.name}.")
    path.write_text(pem + "\n", encoding="utf-8")
    os.chmod(path, mode)


def _write_uploaded_pem_if_provided(
    hass: HomeAssistant,
    path: Path,
    file_id: str | None,
    marker: str,
    mode: int,
) -> None:
    if not file_id:
        return
    with process_uploaded_file(hass, file_id) as uploaded_path:
        _write_pem_if_provided(
            path,
            uploaded_path.read_text(encoding="utf-8"),
            marker,
            mode,
        )


def save_app_certificate_material(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Persist user-provided app certificate material locally, if supplied."""
    component_dir = Path(__file__).resolve().parent
    _write_uploaded_pem_if_provided(
        hass,
        component_dir / STATIC_APP_CERT,
        data.get(CONF_APP_CERT_FILE),
        "BEGIN CERTIFICATE",
        0o644,
    )
    _write_uploaded_pem_if_provided(
        hass,
        component_dir / STATIC_APP_KEY,
        data.get(CONF_APP_KEY_FILE),
        "PRIVATE KEY",
        0o600,
    )
    _write_pem_if_provided(
        component_dir / STATIC_APP_CERT,
        str(data.get(CONF_APP_CERT_PEM) or ""),
        "BEGIN CERTIFICATE",
        0o644,
    )
    _write_pem_if_provided(
        component_dir / STATIC_APP_KEY,
        str(data.get(CONF_APP_KEY_PEM) or ""),
        "PRIVATE KEY",
        0o600,
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input by doing one read-only data refresh."""
    await hass.async_add_executor_job(save_app_certificate_material, hass, data)
    client = LeapmotorApiClient(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        operation_password=data.get(CONF_OPERATION_PASSWORD) or None,
    )
    try:
        result = await hass.async_add_executor_job(client.fetch_data)
    finally:
        await hass.async_add_executor_job(client.close)

    vehicles = result.get("vehicles") or {}
    return {
        "title": f"Leapmotor ({data[CONF_USERNAME]})",
        "vehicles": len(vehicles),
    }


class LeapmotorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Leapmotor."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return LeapmotorOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except LeapmotorMissingAppCertError:
                errors["base"] = "missing_app_cert"
            except LeapmotorAccountCertError:
                errors["base"] = "account_cert_error"
            except ValueError:
                errors["base"] = "certificate_import_error"
            except LeapmotorAuthError:
                errors["base"] = "invalid_auth"
            except LeapmotorApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
                self._abort_if_unique_id_configured()
                data = {
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_OPERATION_PASSWORD: user_input.get(CONF_OPERATION_PASSWORD) or "",
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                }

                return self.async_create_entry(title=info["title"], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class LeapmotorOptionsFlow(config_entries.OptionsFlow):
    """Handle Leapmotor options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage configurable runtime options."""
        if user_input is not None:
            try:
                await self.hass.async_add_executor_job(
                    save_app_certificate_material,
                    self.hass,
                    user_input,
                )
            except ValueError:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._options_schema(
                        operation_password=self._current_operation_password()
                    ),
                    errors={"base": "certificate_import_error"},
                )
            return self.async_create_entry(
                title="",
                data={
                    CONF_OPERATION_PASSWORD: user_input.get(CONF_OPERATION_PASSWORD) or "",
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        operation_password = self._current_operation_password()
        return self.async_show_form(
            step_id="init",
            data_schema=self._options_schema(operation_password=operation_password),
        )

    def _current_operation_password(self) -> str:
        """Return the configured vehicle PIN, if any."""
        return (
            self._config_entry.options[CONF_OPERATION_PASSWORD]
            if CONF_OPERATION_PASSWORD in self._config_entry.options
            else self._config_entry.data.get(CONF_OPERATION_PASSWORD, "")
        )

    def _options_schema(self, operation_password: str = "") -> vol.Schema:
        """Build the options schema."""
        scan_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES),
        )
        return vol.Schema(
            {
                vol.Optional(CONF_APP_CERT_FILE): selector.FileSelector(
                    selector.FileSelectorConfig(accept=".pem,.crt,.cert")
                ),
                vol.Optional(CONF_APP_KEY_FILE): selector.FileSelector(
                    selector.FileSelectorConfig(accept=".pem,.key")
                ),
                vol.Optional(CONF_APP_CERT_PEM, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(multiline=True)
                ),
                vol.Optional(CONF_APP_KEY_PEM, default=""): selector.TextSelector(
                    selector.TextSelectorConfig(multiline=True)
                ),
                vol.Optional(CONF_OPERATION_PASSWORD, default=operation_password or ""): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=120),
                ),
            }
        )
