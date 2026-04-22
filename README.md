# leapmotor-ha

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
- Native Home Assistant lock entity
- Device tracker from vehicle GPS position
- Remote-control buttons for supported actions
- Options flow for vehicle PIN and update interval
- Redacted diagnostics export
- Multi-language translations
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

Expected local files inside `custom_components/leapmotor/`:

- `app_cert.pem`
- `app_key.pem`

They can be copied manually or pasted into the setup/options form if you already
have legitimate certificate material. The setup/options form also supports
uploading the certificate/key files directly.

Without these files, direct authentication fails by design.

## Installation

1. Copy `custom_components/leapmotor` into your Home Assistant config directory under `config/custom_components/leapmotor`.
2. Provide the required local `app_cert.pem` and `app_key.pem` files in that directory, or upload/paste them during setup.
3. Restart Home Assistant.
4. Add the `Leapmotor` integration from `Settings -> Devices & services`.

## Configuration

- Email and password are required
- App certificate and app private key are required, but are not included in this repository
- Vehicle PIN is optional for setup
- Without the Vehicle PIN, the integration works in read-only mode
- Remote-control actions stay unavailable until a Vehicle PIN is configured

## Repository Layout

- `custom_components/leapmotor` - Home Assistant custom integration and backend/auth layer

## Roadmap

1. Validate the single-component public install end-to-end on Home Assistant.
2. Improve local certificate provisioning without publishing certificate material.
3. Keep investigating a future login path that does not need local app certificate material.

## Legal

This project is not affiliated with or endorsed by Leapmotor.

## License

MIT. See [LICENSE](LICENSE).
