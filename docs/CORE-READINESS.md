# Core contribution readiness — 1 November 2026

This is a downstream experimental integration, not an approved Core contribution.

Completed against HA 2026.10.4:

- 35 offline tests using the real HA runtime, plus Ruff and Hassfest checks.
- 100% line and branch coverage for `config_flow.py`, enforced by CI.
- Discovery uses configuration-only retrieval and no persistent token store.
- Polling tests check status/schedule reads without heating-control calls.
- Error/retry paths, YAML import conflicts, controller identity, reauthentication,
  options/reload, legacy entity adoption and temperature metadata are covered.
- One live migration, selective rollback and config-entry-only startup.
- Actual phone dashboard reset-all cleared a permanent override; the vendor app
  and a subsequent HA refresh confirmed the original target and FollowSchedule.

Open acceptance work:

- Complete the bounded natural schedule observation. One natural hot-water
  transition has been captured; overnight heating transitions remain pending.
- Reproduce standalone zone reset with timed vendor/HA reads. A successful mode
  change alone is insufficient proof that the effective target has converged.
- Load source naming defaults at the next planned live restart and recheck
  entity IDs, areas and repair warnings. Persisted registry names already work.
- Exercise installation/update through HACS on a disposable installation.
- Port tests into Core's pytest fixtures and integration test paths; run Core
  type checking and tests against the actual current contribution checkout.
  Runtime-unit-test coverage is not a substitute for that review.

Proposed contribution order (not submitted):

1. Correct system reset behaviour for hot water, with a focused regression test.
2. Config-entry lifecycle, config flow, reauthentication and legacy YAML import,
   preserving entity IDs/services and agreeing deprecation with the maintainer.
3. Measured temperature sensor platform and device/entity metadata, reviewing
   migration and naming separately.

Retain upstream licensing/attribution. Core patches belong under
`homeassistant/components/evohome` and `tests/components/evohome`. Remove the
custom-package version/HACS metadata and avoid changing Core codeowners to the
downstream owner. No maintainer message or upstream PR has been sent.

References:

- https://contributors.home-assistant.io/core/integrations/config-flow/
- https://contributors.home-assistant.io/core/development/testing/
