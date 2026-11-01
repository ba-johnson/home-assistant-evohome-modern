# Core contribution readiness — 1 November 2026

This is a downstream experimental integration, not an approved Core contribution.

Completed validation:

- 35 offline tests using the real HA runtime, plus Ruff and Hassfest checks.
- 100% line and branch coverage for `config_flow.py`, enforced by CI.
- Discovery uses configuration-only retrieval and no persistent token store.
- Polling tests check status/schedule reads without heating-control calls.
- Error/retry paths, YAML import conflicts, controller identity, reauthentication,
  options/reload, legacy entity adoption and temperature metadata are covered.
- One live migration, selective rollback and config-entry-only startup.
- Actual phone dashboard reset-all cleared a permanent override; the vendor app
  and a subsequent HA refresh confirmed the original target and FollowSchedule.
- Live restart preserved all 37 entity IDs and areas, loaded all 13 climate/DHW
  source naming defaults and left zero active repairs.
- Real HACS clean installation of a1 and update to a2 in a disposable config;
  HA discovery verified, and 21 files matched published content (19 text files
  required line-ending normalisation for comparison). No graphical HACS test.
- A focused DHW reset patch on Core commit
  `d6e25b0c2cb2eea0eb7b7f61691801fbf4a70a99` passed the full Evohome suite:
  169 tests, 163 snapshots, mypy for 10 modules and Ruff. Python 3.14.10 and
  Core's pinned `evohome-async==3.1.0` were used. See `contrib/README.md`.
- The focused fix was independently rechecked on pristine pinned source with
  a fresh Git index: 169 tests/163 snapshots and all applicable changed-file
  hooks pass, including HA Pylint. Both distributable patches apply/reverse
  cleanly and reproduce their validated files exactly. An unsubmitted PR draft
  preserves the upstream template and leaves human attestations unchecked.
- The full migration is now rebased onto the same current Core commit and
  vendor 3.1.0, retaining its hourly schedule cache. The complete Evohome suite
  passes: **197 tests and 163 snapshots**, mypy for 14 source modules, Ruff and
  current Core Hassfest. Config-flow line and branch coverage is 100% (18 tests).
  Migration tests cover existing IDs/areas, hot-water areas, reload/legacy settings,
  measured temperature metadata, failed-poll recovery and token isolation.
  See `contrib/core-modernization-v3.patch`; this is a review patch, not a
  replacement for the published alpha or a claim of current-Core live testing.
- All applicable upstream hooks passed on the contribution files, including
  HA Pylint and generated registrations. New setups use fixed polling; legacy
  YAML polling settings are preserved. See `contrib/README.md` for the isolated
  validation environment's Node runtime adjustment.

Open acceptance work:

- Complete the bounded natural schedule observation. Natural hot-water and
  heating transitions have been captured; the overnight/full observation window
  remains pending. A read-only summary is generated automatically at completion.
- Standalone zone reset was reproduced: mode cleared but effective target did
  not restore. Cleanup restored the recorded target and FollowSchedule. The
  behaviour must be understood/fixed before a stable full-bundle release.
- Complete graphical HACS acceptance if claiming a fully tested UI setup path.
- Complete human review before upstream submission. The broader all-files hook
  run finished but was not clean: earlier formatting/findings were corrected
  in the final patch, and mypy/Pylint also encountered unrelated dependency API
  mismatches in the older base environment. Final contribution-file hooks pass;
  whole-Core CI acceptance remains separate.

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
