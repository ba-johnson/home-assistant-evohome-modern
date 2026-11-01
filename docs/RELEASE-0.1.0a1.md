# v0.1.0a1 — experimental prerelease

UI configuration and legacy YAML import for Evohome, standalone measured room
temperature sensors, device grouping, scoped token storage, reauthentication,
sanitised diagnostics, and reset-all including hot water.

Based on Home Assistant Core 2026.10.4. Apache 2.0; upstream attribution is in
the README. This project is not endorsed by Honeywell or Home Assistant.

**This custom integration shadows the built-in `evohome` integration.** Back up
your installation and read `docs/MIGRATION.md` before installing. Only one
account/controller is supported. There is no default HACS catalogue listing.
HACS custom-repository installation has not been tested end to end.

Validation: 27 offline tests, Ruff and official Hassfest passed locally against
HA 2026.10.4. One live installation exercised import, existing entity preservation,
temperature sensors, heating/DHW system reset, reload, config-entry-only startup
and actual selective rollback to the built-in integration.

Known limits:

- Full natural schedule observation is still in progress.
- A zone-only reset reported FollowSchedule before its effective target
  converged. Immediate target restoration needs investigation.
- Updated entity-name defaults are tested and installed on the pilot, but have
  not yet been loaded by a restarted live HA process.
- Browser rendering/tap acceptance, type checks, HACS validation and full
  Core-style config-flow coverage remain outstanding.
- The original unexplained 5-degree overrides have no proven single root cause.

This is an alpha for controlled testing, not a stable or quality-tier release.
