# Migration and rollback acceptance plan

The first private live pilot completed import, entity preservation, reset-all,
entry reload, actual rollback and config-entry-only startup on 1 November 2026.
Natural schedule-transition observation is still in progress. The procedure
below remains an acceptance plan for additional installations, not a claim that
every listed compatibility/recovery case has been covered.

The custom integration uses the existing `evohome` domain. Once installed and
HA restarted, it **shadows the built-in integration**. Do not run another
Evohome controller integration with the same domain or assume they coexist.

Before activation, make a full HA backup and timestamped copies of:

- `configuration.yaml` and any included file containing Evohome configuration.
- `.storage/core.config_entries`, `.storage/core.entity_registry`,
  `.storage/core.device_registry`, `.storage/core.area_registry`.
- `.storage/evohome` and any `.storage/evohome.*` token stores.
- The relevant Lovelace storage/configuration.
- Any existing `custom_components/evohome` directory.

Keep token stores and config-entry backups private. Read/write these through HA
APIs where possible; never overwrite active registry storage while HA runs.

First test against a disposable HA instance with vendor API calls mocked.
Require the complete suite, flow coverage, lint, type and packaging checks to
pass. Check successful setup/unload/reload and verify that setup, refresh and
options changes never send heating commands.

For the live pilot, retain the YAML entry initially so the import can identify
the same location/controller. Expect one config entry and a repair notice.
Compare every pre-existing entity ID and room assignment. Verify all reset
buttons, zone and controller modes, hot water, schedules and measured sensors.
Check that new sensors are selectable as area temperature entities and that
unavailable zones do not show fabricated zero temperatures. Verify service
failure reporting and reauthentication without changing to another controller.

Only after those checks should the backed-up legacy `evohome:` YAML section be
removed. UI setup replaces credentials in YAML, but HA still stores account
credentials locally in its config-entry store; this is not an encrypted secret
vault. Do not delete unrelated YAML or expose backups publicly.

For rollback, stop HA through the supported management interface, restore the
pre-activation full backup (including YAML and registries), and remove/restore
the custom integration to its prior state. Start HA and compare the original
entities and heating controls against the captured baseline. A YAML-only
restore is insufficient after config-entry/entity/device registry migration.

Exact shell paths and commands must be recorded privately against the actual
activation backup. The private pilot retained a full backup plus exact config
and registry copies, and exercised selective integration/configuration rollback.
It did not exercise a complete disaster restore of the full backup archive.
