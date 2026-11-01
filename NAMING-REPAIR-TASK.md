# Pilot naming repair — 1 November 2026

Fix the twelve HA repairs exposed by migrating legacy climate/DHW entities onto
devices. Keep entity IDs and room assignments; provide proper entity-specific
names rather than relying on legacy names equal to the device name. Back up
live registry/repair state and source files before editing, test the real HA
repair predicate, then verify issue removal and runtime metadata after loading
the corrected source. Do not suppress repair issues or alter temperatures.

Result: twelve live repairs cleared automatically after proper registry names
were assigned; persisted names, all IDs and areas verified. 27 tests, lint and
Hassfest passed. The corrected source defaults are installed on disk for the next
normal restart, rather than forcing an outage merely to update naming defaults.
No runtime restart/source-default activation claim is made for this repair.
