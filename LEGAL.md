# Legal Notice

This project is an unofficial Home Assistant custom integration for Leapmotor
vehicles. It is not affiliated with, endorsed by, sponsored by, or approved by
Leapmotor or Stellantis.

This notice is not legal advice. It documents the project policy used to reduce
legal, contractual, privacy, and safety risk for public distribution.

## Project Policy

- The repository contains independently written integration code only.
- The repository must not contain Leapmotor APK files, decompiled application
  code, private keys, client certificates, account tokens, vehicle credentials,
  personal data, or captured traffic logs.
- Users must provide their own Leapmotor account credentials and local
  certificate material. Do not open public issues containing credentials,
  certificates, tokens, VINs, precise locations, or raw diagnostics.
- The integration is intended for use with the user's own account and vehicle.
- The default polling behavior must remain conservative. Do not add aggressive
  polling loops or background write actions.
- Remote-control features must be deliberate user-triggered actions. Features
  that change vehicle state should require the same authorization material as
  the official app unless a verified app flow proves otherwise.
- Third-party integrations such as ABRP must be opt-in and use user-supplied
  credentials or tokens.
- Leapmotor names are used only to identify compatibility. Do not use Leapmotor
  logos, official artwork, or wording that suggests endorsement.

## Interoperability Scope

The project is built for interoperability with Home Assistant. Reverse
engineering notes, if any, should be reduced to the minimum endpoint and data
shape information needed to operate this independently written integration.

Do not publish tools or instructions whose primary purpose is to bypass app
security, extract non-user-owned secrets, circumvent licensing checks, or obtain
access to someone else's account, vehicle, or data.

## User Responsibility

By using this integration, users remain responsible for complying with their
local law, their Leapmotor account and connected-services terms, and any
vehicle-safety requirements that apply to remote-control automation.

Leapmotor may change, restrict, or revoke access to its services at any time.
The absence of a response from Leapmotor must not be treated as permission or
approval.

## Data Protection

Vehicle state, location, odometer, charging, and trip data can be personal data.
This project is designed to run locally in Home Assistant and does not operate a
project-owned cloud service. If a user enables opt-in forwarding to third-party
services, the user is responsible for the data shared with that third party.

