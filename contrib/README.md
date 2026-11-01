# Focused Home Assistant Core contribution

`core-reset-dhw.patch` returns hot water to its schedule when the system reset
button is pressed. Some controllers support native AutoWithReset, but that
command alone left a DHW override active in the live pilot. The patch explicitly
resets DHW after the controller and refreshes state even after partial failure.

It changes one implementation file, updates the existing service-path test to
expect the DHW reset, and adds three regression cases (with/without hot water
and failure cleanup). It does not include the UI migration or temperature sensors.

Validated against Core commit `d6e25b0c2cb2eea0eb7b7f61691801fbf4a70a99`
(`2026.12.0.dev0`), Python 3.14.10, vendor `evohome-async==3.1.0`:

- Full Evohome suite: **169 passed**, **163 snapshots passed**.
- Mypy: **10 source modules passed**, using Core's configuration.
- Ruff check/format: passed on the three changed files.
- The new regression fails without the fix and passes with it; patch reverse
  application was checked against the validated tree.

The focused fix was independently applied to a pristine pinned-source export
with a fresh Git index. Its full suite again passed 169 tests/163 snapshots,
and every applicable changed-file hook passed, including mypy, HA Pylint,
formatting and spelling. No Core commit was made. This is not whole-Core CI.

From a matching Core checkout with its development environment set up:

```sh
git apply /path/to/core-reset-dhw.patch
uv run --no-sync pytest tests/components/evohome
uv run --no-sync mypy --follow-imports=silent homeassistant/components/evohome
```

Generate English translations using Core's documented development setup before
tests. The patch retains upstream licence/ownership and needs human review; it
has not been submitted upstream.

The [unsubmitted PR draft](core-reset-pr-draft.md) preserves the pinned upstream
template, including its unchecked human-review attestations. A reviewer should
check these four behaviours against the three-file patch:

- Reset heating first, then explicitly reset hot water when present.
- Skip the hot-water command on systems without it.
- Refresh HA state even if a command fails, while preserving the error.
- Keep the existing button and service path; the tests require both reset calls.

This fix does not establish the cause of unexpected overrides or resolve the
separate individual-zone target-propagation issue.

Both patches apply and reverse cleanly against pristine pinned source, and their
changed files exactly match their tested trees. The portable result is recorded
in [patch-delivery-verification.json](patch-delivery-verification.json).

## Full migration review patch

`core-modernization-v3.patch` is an alternative, larger patch against the same
Core commit. It includes the DHW reset fix: apply one patch, not both.

The migration adds UI setup, YAML import and repairs, reauthentication,
entry-owned runtime/token storage, measured room-temperature sensors and device
metadata while preserving existing entity IDs and areas. It retains current
Core's vendor 3.1.0 APIs and hourly schedule caching. Upstream ownership and
requirements are preserved; HACS packaging is excluded.
New setups use fixed polling; imported legacy polling settings are retained.
The patch includes Core's generated config-flow and integration registrations.

Verified with Python 3.14.10 and vendor 3.1.0:

- Complete Evohome suite: **197 tests and 163 snapshots passed**.
- Config flow: **100% line and branch coverage**, 18 tests.
- Mypy: **14 source modules passed**; Ruff and current Core Hassfest passed.
- Every applicable upstream hook passed on the contribution files, including
  HA's Pylint checks, code spelling, formatting and generated registrations.
  The isolated Alpine environment used system Node 24 for the pinned hook
  definitions; the downloaded Node binary was incompatible with musl.
- Patch reverse application checked against the tested tree.

This remains a review candidate. Whole-Core CI and human review are
separate gates; overnight pilot observation and standalone zone-reset target
behaviour remain open. The current-Core migration has not been deployed to the
older live pilot. Do not install this patch as a custom-component update.

The broader all-files hook run completed: formatting initially changed files
that were subsequently corrected, while mypy/Pylint also reported dependency
API mismatches elsewhere in the older base environment. Final contribution-file
hooks pass. No claim of a clean whole-Core development environment is made.

The upstream [AI policy](https://github.com/home-assistant/core/blob/d6e25b0c2cb2eea0eb7b7f61691801fbf4a70a99/AI_POLICY.md)
requires contributors to review and understand their changes before submission.
