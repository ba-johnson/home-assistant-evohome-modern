# v0.1.0a2 — experimental packaging and test update

This is still an experimental prerelease. It shadows the built-in `evohome`
integration; read the migration/rollback guide and take a full backup first.

Changes since a1:

- 35 offline tests, with 100% config-flow line and branch coverage enforced in CI.
- Additional discovery/polling tests check that heating-control calls are absent.
- Official HACS packaging validation in CI, descriptive repository topics and
  neutral thermostat icons supplied locally in the integration package.
- Updated readiness evidence: a real phone dashboard reset cleared a permanent
  override; the vendor app and later HA refresh confirmed the prior target and
  FollowSchedule. Immediate HA state may lag the vendor app.

No heating-control implementation changes since a1. This release does not
automatically change a running pilot installation.

Still outstanding: full natural schedule observation, standalone zone-reset
target convergence, source naming validation after a planned live restart,
clean HACS installation/update acceptance, and Core-specific pytest/type checks.
The original unexplained 5-degree overrides have no proven single root cause.

Passing HACS validation does not mean default catalogue inclusion or HA Core
approval. No upstream PR or maintainer message has been sent.
