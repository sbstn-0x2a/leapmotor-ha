# Leapmotor Home Assistant Integration

Custom integration for Leapmotor vehicle data and the verified remote-control path.

## Disclaimer

This is an unofficial reverse-engineered integration. Use it at your own risk.
There is no warranty or liability for account restrictions, API changes, failed
commands, vehicle side effects, or any other consequence of using the
integration. Remote-control actions should only be tested deliberately and with
the vehicle in a safe state.

## Current Scope

This integration creates read-only entities plus remote-control buttons based on
the verified `operatePassword` flow.

Available data includes:

- Battery percentage
- Remaining range
- Odometer
- Vehicle lock as a native Home Assistant lock entity
- Vehicle state as a readable status sensor
- Interior and climate target temperatures
- Charge limit
- Scheduled charging flag as a read-only binary sensor
- Tire pressures
- GPS location as a Home Assistant device tracker
- Remote-control buttons for:
  - Trunk
  - Find vehicle
  - Sunshade
  - Battery preheat
  - A/C switch
  - Quick cool
  - Quick heat
  - Windshield defrost
  - Window action

## Install

Copy the complete folder:

```text
custom_components/leapmotor
```

into your Home Assistant config directory:

```text
config/custom_components/leapmotor
```

Restart Home Assistant, then add the integration from:

```text
Settings -> Devices & services -> Add integration -> Leapmotor
```

## Public Auth Model

This public repository does not ship app certificate material.

Normal setup path:

- install the Custom Component
- provide local `app_cert.pem` and `app_key.pem` in `config/custom_components/leapmotor`, or upload/paste them during setup/options
- configure the integration in Home Assistant

The component itself contains both parts needed at runtime: the Home Assistant
entity layer and the backend/auth layer. No separate add-on is required for the
normal user install path.

## Setup Fields

- Username / email: your Leapmotor account email
- Password: your Leapmotor account password
- App certificate file: required for login; upload it here or leave the field
  empty only if `app_cert.pem` already exists locally.
- App private key file: required for login; upload it here or leave the field
  empty only if `app_key.pem` already exists locally.
- App certificate/private key PEM: fallback paste fields if file upload is not
  convenient.
- Vehicle PIN: optional; leave empty for read-only mode. Remote-control actions
  require this PIN and stay unavailable without it.
- Update interval: default `5` minutes

After setup, the Vehicle PIN and update interval can be changed from the
integration options without recreating the entry.

## Runtime Notes

- Requires `curl` on the Home Assistant host/container.
- Requires Python packages from `manifest.json`: `cryptography` and `requests`.
- The integration uses the same API path verified by the reverse-engineered client.
- Remote-control actions use the verified `operatePassword` flow and require a
  configured Vehicle PIN.
- The account certificate password is derived internally and is no longer asked
  during setup. Known captured values remain as fallback only.
- The integration exposes Home Assistant diagnostics with secrets redacted:
  account state, vehicle metadata, raw status codes, last API codes, and last
  remote-control result.
- A `Last vehicle action` sensor and action attributes show the latest
  remote-control status per VIN.
- The component includes a local `logo.svg` asset for reuse, but Home Assistant
  still does not automatically show local custom-integration brand assets in the
  integration picker. Entity icons are included; the integration logo itself
  only appears automatically for published brands/HACS-style branding flows.
- The current proof set is strongest on the C10. Main-account and shared-car
  handling are both implemented; feature availability may still vary by model,
  especially for climate, sunshade, trunk, and window actions.
