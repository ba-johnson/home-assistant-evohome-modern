# Evohome modernisation: first testable alpha

Scope: a prominent reset-all control on the existing Home HVAC dashboard, then
an offline-tested config-entry port of the built-in Evohome integration, based
on Home Assistant 2026.10.4. This repository is the canonical development lane.

Preserve the evohome domain, platform unique IDs, entity names and existing
services. Add UI setup, controller selection, reauthentication, YAML import,
polling options and unload/reload. No live replacement or restart in this task.
No public repository, release, HACS submission or upstream PR until reviewed.

Acceptance: run the development tests against the actual matching HA runtime,
record test limitations, retain upstream licence, and provide migration,
rollback and publication instructions. Live heating acceptance is a separate
activation step after an HA backup and review.

Validated 31 October 2026: 23 offline tests, Ruff and Hassfest passed on the
matching HA runtime. A guarded real-account authentication/discovery test also
passed without heating commands. The saved live reset card and its native target
were checked through HA's API. Browser rendering and the live reset effect have
not been verified. The replacement is still staged; no HA restart or migration
has occurred, and no public repository/PR/release has been created.

The user subsequently authorised the separate live-pilot phase on 1 November.
Its current results and remaining observation gate are in PILOT-TASK.md.
