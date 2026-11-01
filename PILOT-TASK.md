# Bounded live pilot — 1 November 2026

User authorised activation, restart, entity checks, room-temperature assignment,
reset-all testing, rollback and observation through normal schedule changes.
This is the continuation of the initial alpha task in this canonical repository.

Completed:

- Full pre-pilot HA backup and separate configuration/registry backups.
- Imported legacy YAML into one loaded config entry.
- Preserved all 24 original entity IDs and their room assignments.
- Added ten measured-temperature sensor entities and assigned them as the
  relevant areas' temperature sources.
- Exercised reset-all against the real system: all heating zones follow their
  schedules. Fixed the discovered native-reset/DHW gap and verified that DHW
  also returns to FollowSchedule.
- Successfully reloaded the entry without restarting HA.
- Exercised actual rollback to the built-in integration, verifying the original
  24 entities and no config entry, then reactivated the replacement.
- Removed only the legacy Evohome YAML block and passed the HA config check.
- Restarted again and verified successful config-entry-only startup, preserved
  entities and room-temperature assignments.
- 35 offline tests and lint passed; config-flow line/branch coverage is 100%.
- Actual phone dashboard reset-all cleared a permanent 5-degree override;
  the vendor app and subsequent HA refresh confirmed the previous target and
  FollowSchedule. No test override remains in that zone.

Additional acceptance completed:

- Authorised live restart with timestamped component/config/registry backups.
- All 37 entity IDs and areas preserved; 13 source naming defaults loaded.
- Zero active repairs; Kitchen mapping/sensor and dashboard reset target verified.
- Real HACS installer: clean a1 installation and update to a2 in an empty config,
  with HA discovery and 21 installed files checked. Text content matched after
  accounting for line-ending normalisation; icons matched directly.
- Focused hot-water reset patch validated on current Core: 169 tests, 163
  snapshots, mypy and lint passed. Full migration port remains separate.

Still pending: natural schedule-transition acceptance. A bounded 26-hour,
read-only observer is recording transitions; no heating commands are sent.
The reset card's phone tap path was verified by the pilot user. General browser
rendering acceptance remains limited. The initial public release
is an experimental prerelease. No catalogue submission or maintainer message
has been created.

A direct-zone temporary override was accepted. The immediate zone-reset target
assertion did not pass even though the reported mode subsequently cleared; the
original target was explicitly restored and verified. The repeated standalone
zone-reset test also failed target acceptance after its mode cleared; this
remains a stable-release blocker. Cleanup restored the recorded target and
FollowSchedule. No test override remains.

The later naming-repair task cleared twelve live repairs using persistent,
room-qualified entity names. IDs and areas were unchanged. Correct source naming
defaults were subsequently loaded and verified during the authorised acceptance
restart. See NAMING-REPAIR-TASK.md for the original repair history.

Private paths, backup IDs, rollback commands and observations are recorded
outside this distributable repository in the infrastructure investigation files.

Current-Core migration follow-up (1 November): rebased onto vendor 3.1.0 and
the upstream hourly schedule cache; 198 tests/163 snapshots, 100% config-flow
line/branch coverage, mypy (14 modules), Ruff and Hassfest pass. A separate
portable review patch is under `contrib/`. This does not change the live pilot
or close its standalone zone-reset/overnight acceptance work.
