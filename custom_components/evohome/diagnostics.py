"""Minimal diagnostics without credentials, tokens, location names, or API bodies."""
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from . import EvoConfigEntry


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: EvoConfigEntry):
    """Expose only operational counters and status, using an allow list."""
    coord = entry.runtime_data.coordinator
    return {
        "entry_version": entry.version,
        "poll_seconds": coord.update_interval.total_seconds(),
        "last_update_success": coord.last_update_success,
        "last_exception_type": type(coord.last_exception).__name__ if coord.last_exception else None,
        "zone_count": len(coord.tcs.zones),
        "has_hot_water": coord.tcs.hotwater is not None,
        "high_precision_enabled": coord.client_v1 is not None,
    }
