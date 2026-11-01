# HACS first, upstream when ready

The initial GitHub release is an experimental prerelease, not a stable release
or a submission to the default HACS catalogue. No upstream pull request has
been created. Read the README for the exact validation limits.

## HACS distribution

HACS requires a public GitHub repository with one integration under
`custom_components/<domain>/`. This repository uses `custom_components/evohome`
and includes the upstream licence, manifest, English translations and hacs.json.

Publication and progression checklist:

1. Keep the offline tests, Hassfest and lint passing (these currently pass and
   have repeatable CI commands). Official HACS packaging validation is now in
   CI. Type checks and porting the fully covered downstream config-flow tests
   to Core fixtures remain outstanding for stable/upstream readiness. Verify
   GitHub Actions results after publication.
2. Complete a backed-up live pilot and rollback test. Record precisely which
   HA versions and controller types were actually tested.
3. Review the copied source attribution and licence, and remove credentials,
   private hostnames, addresses, room names, captured logs and backup files.
   The repository's ignored private/backup directories must never be forced in.
4. Create the public GitHub repository at the intended manifest URLs, add an
   accurate description/topics and publish a clearly marked prerelease.
5. Initially distribute it as a HACS **custom repository**. Users can install
   it without waiting for inclusion in the default catalogue. Explain the
   built-in integration shadowing and rollback requirements prominently.
6. Apply for default HACS inclusion only after meeting the current published
   validation and catalogue requirements. Submission is not acceptance.

HACS does not host the code itself; it installs from the public GitHub repo.
No official Honeywell affiliation or Home Assistant endorsement should be implied.

## Home Assistant Core

Evohome already exists in Core, so propose a focused modernisation of that
integration rather than a duplicate integration. Discuss the plan with the
upstream maintainer before proposing a large feature bundle. Any message or PR
to another person is a separate publication action.

Keep the work reviewable in stages: config-entry lifecycle/config flow and
reauthentication; tested YAML import/entity preservation; then standalone
temperature sensors and device metadata. Port code into
`homeassistant/components/evohome` and tests into `tests/components/evohome` in
a Core checkout. Remove HACS-only packaging/version details there.

Core's current rules encourage YAML-only device/service integrations to move
to config flows, with import and repair/deprecation handling. Core requires
complete config-flow test coverage. Existing legacy deprecation dates, modern
climate native-temperature properties and service compatibility must be reviewed
with the maintainer rather than silently changed by a downstream fork.

No Bronze/Silver quality claim is made for this alpha. HACS distribution and
Core inclusion are separate review processes, and neither is guaranteed.

Primary references, checked 31 October 2026:

- [HACS general requirements](https://hacs.dev/docs/publish/start/)
- [HACS integration requirements](https://hacs.dev/docs/publish/integration/)
- [HA YAML-to-config-flow guidance](https://contributors.home-assistant.io/core/integrations/yaml/)
- [HA config flows](https://contributors.home-assistant.io/core/integrations/config-flow/)
- [HA integration quality scale](https://contributors.home-assistant.io/core/quality-scale/)
