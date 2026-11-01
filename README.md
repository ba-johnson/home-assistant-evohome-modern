# Evohome Modern

Experimental config-entry port of Home Assistant's Honeywell Total Connect
Comfort (Europe) integration, based on Home Assistant Core **2026.10.4** and
`evohome-async>=2.1.0` (tested with 2.1.0). Licensed under Apache 2.0; see [LICENSE](LICENSE).

This is an **experimental alpha**, tested on one private installation. It is
not listed in the default HACS catalogue or approved by Home Assistant.
It uses the same `evohome` domain and **replaces the built-in integration while
installed**. Make a full backup and read [migration and rollback](docs/MIGRATION.md)
before installing it. It is not ready for unattended production deployment.

## Installation for experimental testing

Add `https://github.com/ba-johnson/home-assistant-evohome-modern` to HACS as a
custom repository with category **Integration**, enable prerelease versions,
and select `v0.1.0a2`. Alternatively, copy `custom_components/evohome` into your
HA configuration directory's `custom_components` folder. Back up any existing
directory first. Restart HA to load it, then use Devices & services to configure
Evohome. Existing YAML installations are imported; follow the migration guide
before removing the legacy YAML. The real HACS installer was tested in an empty
HA config, installing a1 and updating to a2; HA discovery and installed content
were verified. The graphical HACS setup path was not exercised.

The integration remains **cloud polling**. A UI config flow does not make the
Honeywell connection local or fix faults in the controller or cloud API.

## Changes in this alpha

- UI sign-in and controller selection, with duplicate-setup prevention.
- Config-entry runtime data and unload/reload support.
- Reauthentication that checks access to the existing controller.
- Polling options, defaulting to 300 seconds and limited to 180–3600 seconds.
- One-time legacy YAML import with a repair notice. Imported intervals below
  180 seconds are raised to 180 seconds to reduce cloud load.
- Existing climate/button/water-heater unique IDs, names, domain and services
  are retained. The intent is to preserve entity IDs and existing dashboards;
  full migration acceptance is still required.
- Per-zone measured-temperature sensors, with `device_class: temperature`,
  `state_class: measurement` and Celsius units.
- Device registry metadata groups climate/reset/temperature entities.
- API command errors are raised to the caller instead of swallowed.
- Stale high-precision readings are discarded when that API rejects authentication,
  so room readings can fall back to the standard API instead of freezing indefinitely.
- The system reset button explicitly clears DHW overrides after the controller
  reset: live testing found that native AutoWithReset alone left DHW overridden.
- Diagnostics expose operational counters, excluding credentials, tokens,
  controller identifiers, room names and raw API payloads.

This alpha supports **one account/controller**, matching the original
integration's scope. Multi-controller support is not implemented.

## Why temperature sensors are needed

The original integration exposes the room reading only as the climate entity's
`current_temperature` attribute. It has no sensor platform. A climate entity
cannot substitute for a standalone temperature sensor in selectors that require
`sensor` entities with the temperature device class.

The new sensor platform uses the same measured temperature source as the climate
entity: the high-precision API reading when available, otherwise the standard
zone temperature. It never uses the target setpoint. Missing or non-finite
measurements and failed coordinator updates make the sensor unavailable.

After a tested installation, assign the sensor/device to its room and select it
as the area's temperature entity. The integration suggests the room already
assigned to the legacy climate entity where available.

After adding or splitting zones on the Honeywell controller, reload the Evohome
config entry in Devices & services to fetch the current zone configuration. The
regular status poll does not rebuild the entity set. The private pilot verified
discovery of an additional zone through an entry reload without restarting HA.

## Development validation

Use a disposable environment matching HA 2026.10.4. These tests use fake account
data and mocked vendor calls; network access can be disabled:

```sh
docker run --rm --network none \
  -v "$PWD:/work:ro" -w /work \
  --entrypoint python \
  ghcr.io/home-assistant/home-assistant:2026.10.4 \
  -m unittest discover -s tests -v
```

Validated on 31 October–1 November 2026 against HA 2026.10.4 / Python 3.14.9:

- **35 offline tests passed**, including the real HA flow manager, legacy entity
  ID adoption, temperature sensor metadata and fallback/unavailability handling.
- Config-flow module line and branch coverage is **100%**. CI enforces that
  threshold. Discovery and polling tests also reject heating-control calls.
  These are downstream runtime tests, not yet ported to Core's pytest fixtures.
- Ruff 0.14.3 checks passed for the component and tests.
- Official Hassfest 2026.10.4 passed with no invalid integrations. Its warning
  about sharing the built-in `evohome` domain is expected and material: this
  custom integration shadows the built-in integration when activated.
- One guarded real-account sign-in/discovery test passed. It allowed GET/HEAD
  and the OAuth token request only, issued no heating commands, and persisted
  no account credentials or tokens.

The checked-in CI workflow repeats the offline tests, lint and Hassfest commands,
enforces config-flow coverage and runs the official HACS packaging validator.
Check the repository's Actions tab for the current GitHub workflow results.

The private pilot verified live YAML import, existing entity preservation, new
area-temperature sensor assignment, reset-all for heating and DHW, config-entry
reload, actual rollback to the built-in integration, and reactivation. Legacy
YAML was then removed and config-entry-only startup was verified after restart.
See [pilot status](PILOT-TASK.md).

Natural schedule-transition observation is still running. The pilot's large
dashboard reset button was exercised on a phone: a permanent 5-degree override
cleared, the vendor app returned to its prior target, and HA subsequently
confirmed FollowSchedule at that target. HA's immediate state can lag the app
until a later refresh. This does not establish standalone zone-reset behaviour.
The HACS installer backend passed clean-install/update checks. A focused
upstream hot-water reset patch passed 169 Core tests and 163 snapshots, plus
Core type checking. The larger migration bundle still needs rebasing onto
current Core's vendor API and schedule caching. This is not a quality-tier or universal
compatibility claim, and the unexplained original 5-degree setpoints have not
been proven to have a single root cause.

Controlled direct-zone tests reported FollowSchedule after clearing an override,
but the effective target did not return to its prior value. The original target
was explicitly restored and read back with FollowSchedule. Standalone zone-reset
target propagation remains a confirmed acceptance failure; schedule mode alone is not proof of
the effective target. This is separate from the successful system reset-all test.

The pilot also exposed own-area/own-name repairs when legacy entities gained
devices. Those repairs were cleared using persisted, room-qualified registry
names without changing IDs or room assignments. Device-relative entity-name
defaults and translations are regression-tested and were verified after an
authorised live restart: all 37 entity IDs/area assignments survived, all 13
climate/hot-water naming defaults loaded, and no repair warnings remained.

See the [focused Core patch](contrib/README.md) and [current readiness](docs/CORE-READINESS.md).

See [Migration and rollback](docs/MIGRATION.md) and
[Publication route](docs/PUBLICATION.md). Do not install this alpha on a live
heating system as though these gates have passed.

## Origin and attribution

The starting code is `homeassistant/components/evohome` from the official
[Home Assistant Core 2026.10.4 source](https://github.com/home-assistant/core/tree/2026.10.4/homeassistant/components/evohome),
maintained upstream by `@zxdavb` and other Home Assistant contributors. This
project preserves their licence and does not imply their endorsement.

`tools/port_baseline.py` records the initial one-time source transformation. It is
historical scaffolding, not an installer or a command to run on the current tree.
