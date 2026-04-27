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

## Risk Assessment

This project reduces risk by shipping only clean integration code, but it cannot
remove all legal or practical risk. The main risk areas are:

- Contract and account risk: Leapmotor's connected-services terms may restrict
  how the official services, app, account, or backend are used. Leapmotor may
  change endpoints, block traffic patterns, suspend accounts, revoke service
  access, or require app-only access. No response from Leapmotor is not consent.
- Copyright and interoperability risk: Interoperability-focused reverse
  engineering is treated differently across jurisdictions and is usually limited
  to what is necessary to make independently developed software interoperate.
  Publishing extracted app code, app assets, certificates, private keys, or
  bypass tools would materially increase the risk.
- Circumvention and security risk: The project must not provide tooling whose
  main purpose is bypassing access controls, extracting non-user-owned secrets,
  defeating licensing checks, or accessing vehicles/accounts without
  authorization.
- Data protection risk: Vehicle state, VIN-linked data, GPS position, charging
  history, route destinations, and diagnostics can be personal data. Users should
  avoid publishing logs and should understand that opt-in third-party forwarding
  such as ABRP sends vehicle data outside Home Assistant.
- Safety risk: Remote commands can affect a real vehicle. Incorrect
  automations, stale state, duplicated commands, or wrong vehicle targeting can
  have practical safety or property consequences.
- Trademark and endorsement risk: The repository may identify compatibility with
  Leapmotor, but must not look official or use Leapmotor branding in a way that
  suggests endorsement.
- Platform risk: GitHub or another hosting provider may remove content or
  restrict the repository if it receives a valid complaint involving private
  information, copyright, trademarks, security abuse, or other policy issues.

## Possible Consequences

For the project maintainer:

- requests from Leapmotor or hosting providers to remove content, logs, assets,
  reverse-engineering details, or the full repository;
- DMCA, private-information, trademark, or terms-of-service complaints;
- loss of GitHub repository access or temporary account restrictions in severe
  platform-policy cases;
- civil claims or legal correspondence if the project publishes protected
  material, secrets, or bypass tooling;
- reputational risk if users leak secrets through issues or if unsafe examples
  cause vehicle actions.

For users:

- Leapmotor account or connected-service access may be restricted, rate-limited,
  suspended, or require reauthentication;
- vehicle functions may stop working if Leapmotor changes APIs, certificates,
  app requirements, or server-side validation;
- publishing diagnostics can expose location history, VINs, tokens, account
  identifiers, or certificate material;
- automations may execute on stale data or wrong assumptions if the vehicle API
  delays updates;
- remote actions may create safety, warranty, insurance, or liability questions
  depending on local law and the user's vehicle terms.

For contributors:

- do not contribute code copied from the Leapmotor app or other proprietary
  sources;
- do not add extracted secrets, private endpoints logs, or test credentials;
- do not add features that increase polling frequency or write to the vehicle
  without a clear safety model and maintainer review.

## Recommended Public Release Position

The safest public position is:

- publish this Home Assistant integration only, not the reverse-engineering
  workspace;
- keep the project non-commercial unless legal review is obtained first;
- keep user secrets and certificate material outside the repository and outside
  public issues;
- document that the integration is unofficial, unsupported by Leapmotor, and
  used at the user's own risk;
- keep defaults conservative: five-minute polling, manual refresh, no hidden
  write actions, and opt-in third-party telemetry;
- remove or redact any issue, diagnostic, or pull request that includes
  credentials, certificates, tokens, VINs, or precise location data;
- respond quickly to credible security or rights-holder complaints, and be ready
  to remove disputed material while preserving independently written code where
  possible.

## Data Protection

Vehicle state, location, odometer, charging, and trip data can be personal data.
This project is designed to run locally in Home Assistant and does not operate a
project-owned cloud service. If a user enables opt-in forwarding to third-party
services, the user is responsible for the data shared with that third party.

## Reference Points

- EU Directive 2009/24/EC, especially Articles 5 and 6, limits software
  decompilation/interoperability use to what is necessary for interoperability.
- Swiss Copyright Act Article 21 permits obtaining interface information for
  independently developed interoperable programs, with limits on use.
- Leapmotor Connect terms describe connected-services account use, vehicle data
  disclosure, user responsibilities, and service limitations.
- GitHub policies treat credentials, tokens, and other high-risk secrets as
  private information that may be removed.
- EU and Swiss data-protection rules treat vehicle and location data as sensitive
  in practice when linked to an identifiable person.
