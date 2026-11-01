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

Repository-wide pre-commit hooks still need running in a Git checkout before
submission. The validation tree was a pinned source archive, so that command
stopped with "Not in a Git repository"; this is not a claim of full Core CI.

From a matching Core checkout with its development environment set up:

```sh
git apply /path/to/core-reset-dhw.patch
uv run --no-sync pytest tests/components/evohome
uv run --no-sync mypy --follow-imports=silent homeassistant/components/evohome
```

Generate English translations using Core's documented development setup before
tests. The patch retains upstream licence/ownership and needs human review; it
has not been submitted upstream. The full migration still needs a separate
rebase onto current Core APIs and schedule caching.

The upstream [AI policy](https://github.com/home-assistant/core/blob/d6e25b0c2cb2eea0eb7b7f61691801fbf4a70a99/AI_POLICY.md)
requires contributors to review and understand their changes before submission.
