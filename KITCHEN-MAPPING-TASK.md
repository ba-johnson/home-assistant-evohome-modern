# Kitchen zone import and mapping — 1 November 2026

Inspect the user's updated Honeywell zone configuration, refresh only Evohome
if required, and identify Kitchen by vendor zone ID. Keep a distinct Dining Room
zone intact. Back up current registries/dashboard, map the kitchen thermostat,
reset button, measured-temperature sensor and device to the Kitchen area, and
include the thermostat on the existing Home HVAC view if absent. Validate IDs,
readings and source/device/area relationships without changing heating settings.

Result: the new vendor Kitchen zone was discovered by an Evohome-only reload;
Dining Room remained a distinct zone. Kitchen climate, reset and measured sensor
are now mapped to the existing Kitchen area, the area's temperature source is
selected, and the Home HVAC thermostat grid includes Kitchen. All 34 pre-existing
IDs/areas were preserved. No temperatures or schedules changed. Dashboard config
was saved/read back; browser rendering was not verified.
