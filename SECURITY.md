# Security Policy

## Reporting

Please report security issues privately instead of opening a public issue. Public
issues must not include credentials, certificates, tokens, VINs, exact vehicle
locations, or raw diagnostic dumps.

## Secrets

Never commit or upload:

- `app_cert.pem`
- `app_key.pem`
- Leapmotor passwords or vehicle PINs
- API tokens for ABRP, Home Assistant, or other services
- raw API traces containing headers, cookies, VINs, or locations

If a secret was posted publicly, revoke or rotate it immediately where possible.

## Supported Scope

This project supports local Home Assistant use with a user's own Leapmotor
account and vehicle. It does not support credential sharing, bypassing account
controls, extracting third-party secrets, or accessing vehicles that the user is
not authorized to use.

