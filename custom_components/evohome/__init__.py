"""Support for (EMEA/EU-based) Honeywell TCC systems.

Such systems provide heating/cooling and DHW and include Evohome, Round Thermostat, and
others.

Note that the API used by this integration's client does not support cooling.
"""

from dataclasses import dataclass
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
import logging
from typing import Final

import evohomeasync as ec1
import evohomeasync2 as ec2
import probatio

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_LOCATION_IDX,
    DOMAIN,
    SCAN_INTERVAL_DEFAULT,
    SCAN_INTERVAL_MINIMUM,
)
from .coordinator import EvoDataUpdateCoordinator
from .services import async_setup_services
from .storage import TokenManager

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA: Final = probatio.Schema(
    {
        DOMAIN: probatio.Schema(
            {
                probatio.Required(CONF_USERNAME): cv.string,
                probatio.Required(CONF_PASSWORD): cv.string,
                probatio.Optional(CONF_LOCATION_IDX, default=0): cv.positive_int,
                probatio.Optional(
                    CONF_SCAN_INTERVAL, default=SCAN_INTERVAL_DEFAULT
                ): probatio.All(
                    cv.time_period, probatio.Range(min=SCAN_INTERVAL_MINIMUM)
                ),
            }
        )
    },
    extra=probatio.ALLOW_EXTRA,
)


@dataclass
class EvoData:
    """Entry-owned runtime data."""

    coordinator: EvoDataUpdateCoordinator


type EvoConfigEntry = ConfigEntry[EvoData]
PLATFORMS = [Platform.CLIMATE, Platform.BUTTON, Platform.WATER_HEATER, Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register actions and start a read-only legacy configuration import."""
    async_setup_services(hass)
    if DOMAIN in config:
        data = dict(config[DOMAIN])
        data[CONF_SCAN_INTERVAL] = int(data[CONF_SCAN_INTERVAL].total_seconds())
        hass.async_create_task(hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}, data=data,
        ))
    else:
        ir.async_delete_issue(hass, DOMAIN, "yaml_imported")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: EvoConfigEntry) -> bool:
    """Set up this controller without writing to the heating system."""
    manager = TokenManager(
        hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD],
        async_get_clientsession(hass), store_key=f"{DOMAIN}.{entry.entry_id}",
    )
    coordinator = EvoDataUpdateCoordinator(
        hass, _LOGGER, ec2.EvohomeClient(manager), name=f"{DOMAIN}_coordinator",
        update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, 300)),
        location_idx=entry.data.get(CONF_LOCATION_IDX, 0),
        location_id=entry.data["location_id"], system_id=entry.data["system_id"],
        config_entry=entry, client_v1=ec1.EvohomeClient(manager),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = EvoData(coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: EvoConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: EvoConfigEntry) -> bool:
    """Unload platforms and coordinator listeners without restarting HA."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EvoConfigEntry) -> None:
    """Remove only this entry's cached credentials."""
    from homeassistant.helpers.storage import Store
    from .const import STORAGE_VER
    await Store(hass, STORAGE_VER, f"{DOMAIN}.{entry.entry_id}").async_remove()
