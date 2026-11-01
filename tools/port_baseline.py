"""Historical one-time transform of the pristine baseline; not an installer."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
component = root / "custom_components/evohome"

def edit(name, old, new):
    path = component / name
    text = path.read_text()
    assert old in text, (name, old[:100])
    path.write_text(text.replace(old, new), encoding="utf-8")

edit("__init__.py", "from dataclasses import dataclass", "from dataclasses import dataclass\nfrom datetime import timedelta\nfrom homeassistant.config_entries import ConfigEntry")
edit("__init__.py", "from homeassistant.helpers.discovery import async_load_platform\n", "")
edit("__init__.py", "    EVOHOME_DATA,\n", "")
init = component / "__init__.py"
text = init.read_text().split("@dataclass")[0]
init.write_text(text + '''@dataclass
class EvoData:
    """Entry-owned runtime data."""

    coordinator: EvoDataUpdateCoordinator


type EvoConfigEntry = ConfigEntry[EvoData]
PLATFORMS = [Platform.CLIMATE, Platform.BUTTON, Platform.WATER_HEATER]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register actions and start a read-only legacy configuration import."""
    async_setup_services(hass)
    if DOMAIN in config:
        data = dict(config[DOMAIN])
        data[CONF_SCAN_INTERVAL] = int(data[CONF_SCAN_INTERVAL].total_seconds())
        hass.async_create_task(hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}, data=data,
        ))
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
''', encoding="utf-8")

for name in ["climate.py", "button.py", "water_heater.py"]:
    edit(name, "from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType\n", "from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from . import EvoConfigEntry\n")
    edit(name, "async def async_setup_platform(\n    hass: HomeAssistant,\n    _: ConfigType,\n    async_add_entities: AddEntitiesCallback,\n    discovery_info: DiscoveryInfoType | None = None,\n)", "async def async_setup_entry(\n    hass: HomeAssistant,\n    entry: EvoConfigEntry,\n    async_add_entities: AddEntitiesCallback,\n)")
    edit(name, "    if discovery_info is None:\n        return\n\n    coordinator = hass.data[EVOHOME_DATA].coordinator\n    tcs = hass.data[EVOHOME_DATA].tcs", "    coordinator = entry.runtime_data.coordinator\n    tcs = coordinator.tcs")
    # The registry platform and unique IDs deliberately remain evohome.
    path = component / name
    path.write_text(path.read_text().replace("    EVOHOME_DATA,\n", "").replace("from .const import EVOHOME_DATA\n", "").replace("DOMAIN, EVOHOME_DATA,", "DOMAIN,"), encoding="utf-8")
edit("water_heater.py", "    assert tcs.hotwater is not None  # mypy check", "    if tcs.hotwater is None:\n        return")
edit("climate.py", "        async_dispatcher_connect(self.hass, DOMAIN, self.process_signal)", "        self.async_on_remove(\n            async_dispatcher_connect(self.hass, DOMAIN, self.process_signal)\n        )")

edit("storage.py", "        **kwargs: Any,", "        store_key: str | None = STORAGE_KEY,\n        **kwargs: Any,")
edit("storage.py", "self._store = Store(hass, STORAGE_VER, STORAGE_KEY)", "self._store = Store(hass, STORAGE_VER, store_key) if store_key else None")
edit("storage.py", "cache: _TokenStoreT = await self._store.async_load() or {}", "cache: _TokenStoreT = (await self._store.async_load() or {}) if self._store else {}")
edit("storage.py", "        await self._store.async_save(cache)", "        if self._store:\n            await self._store.async_save(cache)")

edit("coordinator.py", "from homeassistant.core import HomeAssistant", "from homeassistant.core import HomeAssistant\nfrom homeassistant.config_entries import ConfigEntry\nfrom homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError")
edit("coordinator.py", "        location_idx: int,", "        location_idx: int,\n        location_id: str,\n        system_id: str,\n        config_entry: ConfigEntry,")
edit("coordinator.py", "            config_entry=None,", "            config_entry=config_entry,")
edit("coordinator.py", "        self.loc_idx = location_idx", "        self.loc_idx = location_idx\n        self.location_id = location_id\n        self.system_id = system_id")
p = component / "coordinator.py"
t = p.read_text();start=t.index("    # our version of async_config_entry_first_refresh()");end=t.index("    @override\n    async def _async_setup",start);t=t[:start]+t[end:]
start=t.index("        try:\n            self.loc = self.client.locations[self.loc_idx]");end=t.index("\n        if self.logger.isEnabledFor",start)
t=t[:start]+'''        self.loc = next((loc for loc in self.client.locations if loc.id == self.location_id), None)
        if self.loc is None:
            raise UpdateFailed("The configured location is no longer available")
        self.tcs = next((system for gateway in self.loc.gateways for system in gateway.systems
                         if system.id == self.system_id), None)
        if self.tcs is None:
            raise UpdateFailed("The configured controller is no longer available")
'''+t[end:]
t=t.replace("        except ec2.EvohomeError as err:\n            raise UpdateFailed(err) from err", "        except ec2.BadUserCredentialsError as err:\n            raise ConfigEntryAuthFailed from err\n        except ec2.EvohomeError as err:\n            raise UpdateFailed(err) from err")
t=t.replace("        except ec2.ApiRequestFailedError as err:\n            self.logger.error(err)\n            return None", "        except ec2.BadUserCredentialsError as err:\n            raise ConfigEntryAuthFailed from err\n        except ec2.EvohomeError as err:\n            raise HomeAssistantError(\"The Evohome command failed\") from err")
p.write_text(t,encoding="utf-8")

edit("services.py", "    hass: HomeAssistant, coordinator: EvoDataUpdateCoordinator\n", "    hass: HomeAssistant\n")
edit("services.py", "    @verify_domain_control(DOMAIN)\n    async def force_refresh", '''    def get_coordinator() -> EvoDataUpdateCoordinator:
        entries = [e for e in hass.config_entries.async_entries(DOMAIN)
                   if e.state.value == "loaded"]
        if len(entries) != 1:
            raise ServiceValidationError("Exactly one loaded Evohome controller is required")
        return entries[0].runtime_data.coordinator

    @verify_domain_control(DOMAIN)
    async def force_refresh''')
edit("services.py", "        await coordinator.async_refresh()", "        await get_coordinator().async_request_refresh()")
edit("services.py", "        assert coordinator.tcs is not None  # mypy", "        coordinator = get_coordinator()\n        assert coordinator.tcs is not None  # mypy")
# Await commands directly so service failures reach the caller instead of being dispatched.
p=component / "services.py";t=p.read_text();start=t.index("        payload = {",t.index("async def set_system_mode"));end=t.index("\n    hass.services.async_register",start)
t=t[:start]+'''        if call.service == EvoService.RESET_SYSTEM:
            await coordinator.call_client_api(coordinator.tcs.reset())
            return
        from homeassistant.util import dt as dt_util
        until = None
        if SZ_PERIOD in call.data:
            until = dt_util.start_of_local_day() + call.data[SZ_PERIOD]
        elif SZ_DURATION in call.data:
            until = dt_util.now() + call.data[SZ_DURATION]
        await coordinator.call_client_api(coordinator.tcs.set_mode(
            _as_snake_case(call.data[SZ_MODE]),
            until=dt_util.as_utc(until) if until else None,
        ))
'''+t[end:];t=t.replace("from homeassistant.helpers.dispatcher import async_dispatcher_send\n", "");p.write_text(t,encoding="utf-8")

p=component / "manifest.json";m=json.loads(p.read_text());m.update({
    "name":"Evohome Modern (experimental)", "config_flow":True, "single_config_entry":True,
    "version":"0.1.0a1", "documentation":"https://github.com/ba-johnson/home-assistant-evohome-modern",
    "issue_tracker":"https://github.com/ba-johnson/home-assistant-evohome-modern/issues",
    "codeowners":["@ba-johnson"], "integration_type":"hub",
    "requirements":["evohome-async>=2.1.0"],
});m.pop("quality_scale",None);p.write_text(json.dumps(m,indent=2)+"\n",encoding="utf-8")
