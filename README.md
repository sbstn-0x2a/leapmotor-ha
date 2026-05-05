# leapmotor-ha

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kerniger&repository=leapmotor-ha&category=integration)

Unofficial Home Assistant integration for Leapmotor vehicles.

## Status

This repository is the cleaned public version of the project.

It intentionally does not contain:

- client certificates
- private keys
- captured tokens
- account data
- research logs
- reverse-engineering workfiles

## Features

- Home Assistant custom integration
- Read-only vehicle entities
- Static vehicle image entity from the official vehicle picture package
- Mileage/energy-history summary sensors
- Native Home Assistant lock entity for remote lock/unlock actions
- Charge-cable plugged-in state and active-charging state
- Door and trunk open states
- Window, skylight, gear, speed, battery temperature, PTC power, and range-mode
  diagnostics from APK-verified status signals
- Device tracker from vehicle GPS position
- Remote-control buttons for supported actions
- Native Home Assistant services for supported remote actions
- Send destination to vehicle navigation via Home Assistant service
- Optional ABRP Generic Telemetry live-data push
- Setup/options flow for vehicle PIN, update interval, and optional ABRP token
- Redacted diagnostics export
- Multi-language translations
- Multi-vehicle support for main-account and shared-car vehicles
- HACS and Home Assistant brand/icon assets
- Single Custom Component package with entity layer and backend/auth layer

## Important

- Unofficial project
- Use at your own risk
- No liability for account restrictions, API changes, failed commands, vehicle side effects, or any other consequence
- Remote-control actions should only be used deliberately and in a safe vehicle state

## Security

For legal and security reasons, this repository does not include the static app
certificate material required by the current login path.

The public install target is one Home Assistant Custom Component:

- `custom_components/leapmotor`

Internal architecture:

- the Home Assistant integration manages entities, config flow, and UI
- the backend/auth layer manages login, session, certificate, vehicle data, and command calls

Current reality:

- the integration code still supports direct login with local certificate files
- the internal backend path covers login, vehicle list, status, and remote commands
- additional read-only calls cover total mileage and charging-plan details

Expected local files for persistent storage:

- `/config/leapmotor/app_cert.pem`
- `/config/leapmotor/app_key.pem`

They can be copied manually or pasted into the setup/options form if you already
have legitimate certificate material. The setup/options form also supports
uploading the certificate/key files directly. Uploaded/pasted files are stored
outside `custom_components`, so HACS updates do not remove them.

Without these files, direct authentication fails by design.

## Installation

### HACS

Fast path:

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kerniger&repository=leapmotor-ha&category=integration)

Manual HACS path:

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose `Custom repositories`.
3. Add this repository URL:

   ```text
   https://github.com/kerniger/leapmotor-ha
   ```

4. Select `Integration` as the repository type and add it.
5. Search for `Leapmotor` in HACS and install it.
6. Restart Home Assistant.
7. Add the `Leapmotor` integration from `Settings -> Devices & services`.
8. During setup, upload/paste the required certificate/key material. Uploaded
   or pasted values are stored as `/config/leapmotor/app_cert.pem` and
   `/config/leapmotor/app_key.pem`. Alternatively, place both files there
   before setup.

Included release screenshots:

- `docs/screenshots/01-hacs-custom-repository.png`: HACS custom repository
  dialog with `https://github.com/kerniger/leapmotor-ha` and type `Integration`.
- `docs/screenshots/02-hacs-leapmotor-installed.png`: Leapmotor visible as an
  installed HACS integration.
- `docs/screenshots/03-add-integration.png`: Home Assistant add-integration
  search result for `Leapmotor`.
- `docs/screenshots/04-certificate-step.png`: certificate upload/paste step.
- `docs/screenshots/05-account-step.png`: account, Vehicle PIN, update
  interval, and optional ABRP fields.
- `docs/screenshots/06-device-overview.png`: created Leapmotor device with
  sensor, binary sensor, lock, button, number, image, and tracker entities.

Do not publish screenshots containing VINs, account email addresses, tokens,
certificate contents, precise home location, or other personal data.

### Manual

1. Copy `custom_components/leapmotor` into your Home Assistant config directory under `config/custom_components/leapmotor`.
2. Provide the required local files as `/config/leapmotor/app_cert.pem` and `/config/leapmotor/app_key.pem`, or upload/paste them during setup.
3. Restart Home Assistant.
4. Add the `Leapmotor` integration from `Settings -> Devices & services`.

## Configuration

- Email and password are required
- App certificate and app private key are required, but are not included in this repository
- A dedicated second Leapmotor account with the vehicle shared to it is
  recommended. Using the same account in Home Assistant and the official app
  can log the app out when the integration authenticates.
- Vehicle PIN is optional for setup
- ABRP live data is optional during setup; users only need their ABRP Generic Token
- Without the Vehicle PIN, the integration works in read-only mode
- Most remote-control actions stay unavailable until a Vehicle PIN is configured
- `send_destination` does not require the Vehicle PIN, matching the observed app flow
- Remote-control actions have a short cooldown to reduce accidental duplicate commands
- If multiple vehicles are available, entities are created per VIN and services can target a vehicle by `vin` or a Leapmotor `entity_id`
- The charging sensor reports active charging only. Plugged-in but stopped/idle
  sessions stay `off`; use the separate charge-cable sensor for plugged-in
  state.
- Lock state follows the app home-screen state using validated signal `1298`
  (`1=locked`, `0=unlocked`). Signal `47` is not used for lock state.
- Diagnostic lock-state sensors expose the source, age, and raw signal code so
  users can distinguish fresh cloud data, stale data, and temporary
  remote-control overrides.

## Known Limitations

- This is an unofficial cloud integration and can break if Leapmotor changes
  authentication, endpoint behavior, rate limits, or signal semantics.
- The current public login path requires user-provided app certificate material.
  The integration does not generate, bundle, fetch, or download these files.
- The Leapmotor backend is polled, not streamed. Values can lag behind the real
  vehicle state; use the `Last refresh` sensor and diagnostic age attributes
  when automations depend on freshness.
- A second Leapmotor account with the vehicle shared to it is strongly
  recommended. Using the same account in Home Assistant and the official app can
  log the app out.
- Remote-control availability can vary by model, account rights, shared-car
  permissions, vehicle state, and backend policy. Unsupported or rejected
  commands are surfaced through entity attributes and diagnostics.
- Multi-vehicle support is implemented per VIN, but model-specific backend
  behavior can still differ. If one vehicle has entities but no data, export
  diagnostics and check the per-vehicle status response.
- Entity IDs are intentionally kept in stable English form. Display names follow
  the Home Assistant language where translations are available.

## Services

The integration exposes Home Assistant services under `leapmotor.*`. All
vehicle-targeted services accept either `vin` or an existing Leapmotor
`entity_id`; `vin` is safest when multiple vehicles are configured.

| Service | PIN required | Purpose | Extra fields |
|---|---:|---|---|
| `leapmotor.lock` | yes | Lock the vehicle | none |
| `leapmotor.unlock` | yes | Unlock the vehicle | none |
| `leapmotor.trunk_open` / `trunk_close` | yes | Open/close trunk | none |
| `leapmotor.find_car` | yes | Horn/find-vehicle action | none |
| `leapmotor.windows_open` / `windows_close` | yes | Open/close windows | optional `value` 0-100 |
| `leapmotor.sunshade_open` / `sunshade_close` | yes | Open/close sunshade | optional `value` 0-10 |
| `leapmotor.ac_switch` | yes | Climate off | none |
| `leapmotor.quick_cool` | yes | Start quick-cool profile | none |
| `leapmotor.quick_heat` | yes | Start quick-heat profile | none |
| `leapmotor.windshield_defrost` | yes | Start windshield defrost profile | none |
| `leapmotor.battery_preheat` | yes | Start battery preheat | none |
| `leapmotor.set_charge_limit` | yes | Set charge limit | `charge_limit_percent` 1-100 |
| `leapmotor.send_destination` | no | Send navigation destination | `name`, `latitude`, `longitude`, optional `address` |
| `leapmotor.export_diagnostics` | no | Write redacted support JSON | optional `filename` |

Window and sunshade `value` fields are optional. Omitting them keeps the
previous full open/close behavior.

### Service Examples

Send a destination to the vehicle navigation:

```yaml
action: leapmotor.send_destination
data:
  entity_id: device_tracker.c10_location
  name: Bern Bahnhof
  address: Bahnhofplatz, Bern, Schweiz
  latitude: 46.94809
  longitude: 7.43914
```

Set the charge limit to 85 percent:

```yaml
action: leapmotor.set_charge_limit
data:
  entity_id: number.c10_set_charge_limit
  charge_limit_percent: 85
```

Start quick heating when the car is plugged in on a cold morning:

```yaml
trigger:
  - platform: time
    at: "06:45:00"
condition:
  - condition: numeric_state
    entity_id: sensor.c10_interior_temperature
    below: 8
  - condition: state
    entity_id: binary_sensor.c10_charge_cable_plugged_in
    state: "on"
action:
  - action: leapmotor.quick_heat
    data:
      entity_id: sensor.c10_battery
```

Vent the vehicle by partially opening the windows:

```yaml
action: leapmotor.windows_open
data:
  entity_id: sensor.c10_battery
  value: 30
```

Lock the vehicle if it still appears unlocked after a refresh:

```yaml
trigger:
  - platform: state
    entity_id: lock.c10_lock
    to: unlocked
    for: "00:10:00"
condition:
  - condition: state
    entity_id: sensor.c10_lock_state_source
    state: raw_signal_1298
action:
  - action: leapmotor.lock
    data:
      entity_id: lock.c10_lock
```

Export diagnostics for support:

```yaml
action: leapmotor.export_diagnostics
data:
  filename: leapmotor-diagnostics.json
```

## ABRP Live Data

ABRP telemetry is optional and disabled by default. During setup, enable
`ABRP live data` and enter the `ABRP Generic Token` from the ABRP vehicle
live-data setup. Users do not need to request or enter an ABRP API key.

## evcc

The integration does not require a dedicated evcc API adapter. evcc can read the
vehicle data through Home Assistant's existing entities.

Recommended Home Assistant entities:

- `sensor.<vehicle>_battery` for state of charge
- `sensor.<vehicle>_range` or `sensor.<vehicle>_live_range` for remaining range
- `binary_sensor.<vehicle>_charge_cable_plugged_in` for cable/plug state
- `binary_sensor.<vehicle>_charging` for active charging only
- `sensor.<vehicle>_charging_connection` for detailed state:
  `unplugged`, `plugged_in`, `charging`, `finished`
- `sensor.<vehicle>_charging_power` for charging power
- `sensor.<vehicle>_charging_current` and `sensor.<vehicle>_charging_voltage`
  for raw electrical values
- `sensor.<vehicle>_odometer` for mileage

State interpretation:

- `binary_sensor.<vehicle>_charging = on` means confirmed active charging.
- `binary_sensor.<vehicle>_charge_cable_plugged_in = on` and
  `binary_sensor.<vehicle>_charging = off` means the vehicle is plugged in but
  not actively charging.
- `sensor.<vehicle>_charging_connection = finished` means the cable is still
  connected and the backend reports a completed/idle charging session.
- Use the `Last refresh` sensor to check data freshness before relying on the
  values for automation.

The Leapmotor cloud is polled, not streamed. For load management, prefer evcc
or wallbox measurements as the real-time electrical source and use Leapmotor
entities mainly for SOC, range, plug state, and vehicle-side diagnostics.

## Diagnostics

In addition to the regular vehicle entities, the integration exposes:

- redacted config-entry diagnostics for support/export
- `leapmotor.export_diagnostics` to write an anonymized support JSON file under
  `/config/leapmotor`, including interpreted status values and raw APK signal
  values keyed by signal id
- last remote-action status and error details
- last API update status and error classification
- optional raw candidate status signals for future mapping work

## Troubleshooting

### HACS does not show the integration

- Confirm the repository was added as type `Integration`, not `Plugin` or
  `Theme`.
- Restart Home Assistant after installation or update.
- If HACS reports `No manifest.json`, make sure the custom repository points to
  the repository root `https://github.com/kerniger/leapmotor-ha`, not to a
  branch subfolder or ZIP contents.
- Clear browser/app cache if the logo or name still looks stale after an
  update.

### Certificate upload or login fails

- The required files are `app_cert.pem` and `app_key.pem`.
- Upload/paste them during setup, or place them before setup as
  `/config/leapmotor/app_cert.pem` and `/config/leapmotor/app_key.pem`.
- Do not place them only under `custom_components/leapmotor`; HACS updates can
  replace that folder. The integration tries to migrate older files from there,
  but `/config/leapmotor` is the persistent location.
- The certificate file must contain a `BEGIN CERTIFICATE` PEM block. The key
  file must contain a `PRIVATE KEY` PEM block.
- If the setup form reports `Missing app certificate/private key`, re-open
  options or setup and upload/paste both files again.

### The official app gets logged out

Create a second Leapmotor account, share the vehicle to that account in the
official app, and use the shared account in Home Assistant. This avoids Home
Assistant and the mobile app competing for the same account session.

### Entities are unavailable or stale

- Press the `Refresh data` button and check the `Last refresh` sensor.
- Check the integration log for authentication/API errors.
- Run `leapmotor.export_diagnostics` and inspect the anonymized JSON under
  `/config/leapmotor`.
- For lock/vehicle state issues, check `lock_state_source`,
  `lock_state_age_seconds`, `raw_lock_status_code`, and the vehicle-state
  diagnostic attributes.
- For charging issues, compare `charging`, `charge_cable_plugged_in`, and
  `charging_connection`.

### Remote-control actions are unavailable

- Configure the Vehicle PIN in the integration options.
- Confirm the account has the required vehicle rights, especially for shared
  vehicles.
- Wait for the short remote-action cooldown before repeating a command.
- Review `last_remote_status`, `last_remote_error`, and the diagnostics export.

## Special Thanks

Special thanks to [Toxo666](https://github.com/Toxo666) for validating and
sharing additional Leapmotor raw-signal mappings across charging, doors,
climate, heating, seating, range, and diagnostics.

## FAQ

### Why does the logo not show immediately?

Home Assistant and browser caches can keep old integration brand assets for a
while. After installing or updating, restart Home Assistant and hard-refresh the
browser or app. The repository includes brand assets both for HACS and for the
local custom integration package.

### Why are app_cert.pem and app_key.pem not included?

They are app-level client certificate material required by the current login
path. Publishing them would expose reusable authentication material. Users must
provide legitimate local certificate material themselves.

### Where are app_cert.pem and app_key.pem stored?

Uploaded or pasted certificate files are stored under `/config/leapmotor/`.
This folder is outside `custom_components`, so HACS updates do not remove the
files. Older installs that still have the files in
`config/custom_components/leapmotor/` are copied to the persistent folder
automatically when possible.

### Can the integration generate these certificates?

No. Self-generated certificates are not useful unless the Leapmotor backend
trusts them. The integration can import existing PEM files, but it cannot create
valid backend-trusted app certificates.

### I cannot retrieve the certificates. What can I do?

At the moment there is no built-in public, rootless, user-friendly certificate
retrieval flow. The known working setup still requires legitimate app client
certificate material supplied by the user. The integration does not include or
download these files automatically. Community resources may discuss compatible
PEM certificate/key material, but users must review and decide themselves
whether using such material is acceptable for their setup.

### Why do range and odometer not show `.00`?

Whole kilometer values are exposed as integers so Home Assistant displays
`123 km` instead of `123.00 km`. Values with real decimals are preserved.

## Repository Layout

- `custom_components/leapmotor` - Home Assistant custom integration and backend/auth layer

## Roadmap

- Keep improving status mapping across more Leapmotor models.
- Keep investigating a future login path that does not need local app certificate material.
- Add more write features only after the exact app request, safety model, and permission behavior are verified.

## Legal

This project is not affiliated with or endorsed by Leapmotor.
See [LEGAL.md](LEGAL.md) and [SECURITY.md](SECURITY.md) before publishing logs,
diagnostics, or modified builds.

## License

MIT. See [LICENSE](LICENSE).
