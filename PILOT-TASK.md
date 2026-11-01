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
- 27 offline tests, lint and Hassfest passed after the naming-repair fix.

Still pending: natural schedule-transition acceptance. A bounded 26-hour,
read-only observer is recording transitions; no heating commands are sent.
Browser rendering/tap acceptance was not verified. The initial public release
is an experimental prerelease. No catalogue submission or maintainer message
has been created.

A direct-zone temporary override was accepted. The immediate zone-reset target
assertion did not pass even though the reported mode subsequently cleared; the
original target was explicitly restored and verified. Target propagation after a
zone-only reset remains an investigation item for stable-release readiness.

The later naming-repair task cleared twelve live repairs using persistent,
room-qualified entity names. IDs and areas were unchanged. Correct source naming
defaults are installed for the next normal restart; the repair itself did not
need another restart. See NAMING-REPAIR-TASK.md.

Private paths, backup IDs, rollback commands and observations are recorded
outside this distributable repository in the infrastructure investigation files.
