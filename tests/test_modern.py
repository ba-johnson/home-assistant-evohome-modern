"""Offline tests using the real HA runtime; no Honeywell credentials or network."""
from datetime import timedelta
import logging
from pathlib import Path
import tempfile
from types import SimpleNamespace, MappingProxyType
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntries, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant import loader
from homeassistant.helpers import entity_registry as er, area_registry as ar, device_registry as dr
import evohomeasync2 as evo
import evohomeasync as evo_v1

from custom_components.evohome import async_setup, async_setup_entry, async_unload_entry
from custom_components.evohome.config_flow import EvohomeConfigFlow, EvohomeOptionsFlow
from custom_components.evohome.coordinator import EvoDataUpdateCoordinator
from custom_components.evohome.storage import TokenManager


class ModernTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.hass = HomeAssistant(self.temp.name)
        self.hass.config_entries = ConfigEntries(self.hass, {})
        self.hass.config.skip_pip = True
        loader.async_setup(self.hass)
        dr.async_setup(self.hass)
        await dr.async_load(self.hass)
        await er.async_load(self.hass)
        await ar.async_load(self.hass)
        self.loc = SimpleNamespace(id="location-test", name="Test home")
        self.system = SimpleNamespace(id="controller-test", hotwater=None, location=self.loc)
        self.loc.gateways = [SimpleNamespace(systems=[self.system])]
        self.rows = [(0, self.loc, self.system)]
        self.credentials = {"username": "test@example.invalid", "password": "test-only"}

    async def asyncTearDown(self):
        await self.hass.async_stop(force=True)
        self.temp.cleanup()

    def entry(self):
        return ConfigEntry(version=1, minor_version=1, domain="evohome", title="Test home",
            data={**self.credentials, "location_id": self.loc.id, "system_id": self.system.id},
            source="user", unique_id="location-test_controller-test", options={},
            discovery_keys=MappingProxyType({}), subentries_data=[])

    def flow(self):
        f = EvohomeConfigFlow()
        f.hass = self.hass
        f.context = {"source": "user"}
        f.flow_id = "offline-flow"
        return f

    async def test_user_flow_and_stable_ids(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(return_value=self.rows)):
            result = await f.async_step_user(self.credentials)
        self.assertEqual(result["step_id"], "controller")
        result = await f.async_step_controller({"system_id": self.system.id})
        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(result["data"]["system_id"], self.system.id)
        self.assertEqual(result["data"]["location_id"], self.loc.id)
        self.assertEqual(result["options"]["scan_interval"], 300)

    async def test_invalid_credentials_are_not_saved(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(side_effect=evo.BadUserCredentialsError("invalid"))):
            result = await f.async_step_user(self.credentials)
        self.assertEqual(result["errors"], {"base": "invalid_auth"})
        self.assertEqual(self.hass.config_entries.async_entries("evohome"), [])

    async def test_network_error_can_retry(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(side_effect=TimeoutError)):
            result = await f.async_step_user(self.credentials)
        self.assertEqual(result["errors"], {"base": "cannot_connect"})

    async def test_no_systems(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(return_value=[])):
            result = await f.async_step_user(self.credentials)
        self.assertEqual(result["reason"], "no_systems")

    async def test_duplicate_setup_blocked(self):
        f = self.flow()
        with patch.object(f, "_async_current_entries", return_value=[self.entry()]):
            result = await f.async_step_user()
        self.assertEqual(result["reason"], "single_instance_allowed")

    async def test_yaml_repair_cleared_once_legacy_yaml_is_removed(self):
        with patch("custom_components.evohome.async_setup_services"), \
             patch("custom_components.evohome.ir.async_delete_issue") as delete_issue:
            self.assertTrue(await async_setup(self.hass, {}))
        delete_issue.assert_called_once_with(self.hass, "evohome", "yaml_imported")

    async def test_import_keeps_controller_and_conservative_polling(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(return_value=self.rows)):
            result = await f.async_step_import({**self.credentials, "scan_interval": 60})
        self.assertEqual(result["type"], "create_entry")
        self.assertEqual(result["data"]["system_id"], self.system.id)
        self.assertEqual(result["options"]["scan_interval"], 180)

    async def test_import_wrong_location_fails(self):
        f = self.flow()
        with patch.object(f, "_async_discover", AsyncMock(return_value=self.rows)):
            result = await f.async_step_import({**self.credentials, "location_idx": 9})
        self.assertEqual(result["reason"], "no_systems")

    async def test_reauth_cannot_switch_controller(self):
        f = self.flow()
        with patch.object(f, "_get_reauth_entry", return_value=self.entry()), \
             patch.object(f, "_async_discover", AsyncMock(return_value=[])):
            result = await f.async_step_reauth_confirm(self.credentials)
        self.assertEqual(result["errors"], {"base": "wrong_controller"})

    async def test_reauth_updates_existing_entry(self):
        f = self.flow()
        entry = self.entry()
        with patch.object(f, "_get_reauth_entry", return_value=entry), \
             patch.object(f, "_async_discover", AsyncMock(return_value=self.rows)), \
             patch.object(f, "async_update_reload_and_abort", return_value={"type": "abort"}) as update:
            await f.async_step_reauth_confirm(self.credentials)
        update.assert_called_once_with(entry, data_updates=self.credentials)

    async def test_ephemeral_token_manager_does_not_write(self):
        manager = TokenManager(self.hass, "test", "test", MagicMock(), store_key=None)
        await manager._load_cache_from_store()
        self.assertIsNone(manager._store)
        self.assertTrue(manager._store_initialized)

    async def test_setup_and_unload_use_real_config_entry_contract(self):
        entry = self.entry()
        fake = MagicMock()
        fake.async_config_entry_first_refresh = AsyncMock()
        with patch("custom_components.evohome.async_get_clientsession", return_value=MagicMock()), \
             patch("custom_components.evohome.EvoDataUpdateCoordinator", return_value=fake) as cls, \
             patch.object(self.hass.config_entries, "async_forward_entry_setups", AsyncMock()) as forward, \
             patch.object(self.hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True)) as unload:
            self.assertTrue(await async_setup_entry(self.hass, entry))
            self.assertIs(entry.runtime_data.coordinator, fake)
            self.assertIs(cls.call_args.kwargs["config_entry"], entry)
            fake.async_config_entry_first_refresh.assert_awaited_once()
            forward.assert_awaited_once()
            self.assertTrue(await async_unload_entry(self.hass, entry))
            unload.assert_awaited_once()

    def coordinator(self, client):
        return EvoDataUpdateCoordinator(self.hass, logging.getLogger("test"), client,
            name="test", update_interval=timedelta(seconds=300), location_idx=0,
            location_id=self.loc.id, system_id=self.system.id, config_entry=self.entry())

    async def test_controller_selected_by_id_after_location_order_changes(self):
        other = SimpleNamespace(id="other", gateways=[])
        client = SimpleNamespace(update=AsyncMock(), locations=[other, self.loc])
        coord = self.coordinator(client)
        await coord._async_setup()
        self.assertIs(coord.loc, self.loc)
        self.assertIs(coord.tcs, self.system)

    async def test_auth_failure_requests_reauth(self):
        coord = self.coordinator(SimpleNamespace(update=AsyncMock(side_effect=evo.BadUserCredentialsError("invalid"))))
        with self.assertRaises(ConfigEntryAuthFailed):
            await coord._async_setup()

    async def test_command_error_is_not_reported_as_success(self):
        coord = self.coordinator(MagicMock())
        fail = AsyncMock(side_effect=evo.EvohomeError("test failure"))
        with self.assertRaises(HomeAssistantError):
            await coord.call_client_api(fail())

    async def test_reset_button_calls_system_reset(self):
        from custom_components.evohome.button import EvoSystemResetButton
        coord = self.coordinator(MagicMock())
        coord.call_client_api = AsyncMock()
        coord.async_request_refresh = AsyncMock()
        self.system.reset = AsyncMock()
        button = EvoSystemResetButton(coord, self.system)
        await button.async_press()
        self.system.reset.assert_called_once()
        self.system.reset.return_value = None
        # Await the coroutine forwarded to the fake coordinator to avoid a leak.
        await coord.call_client_api.call_args.args[0]
        self.assertEqual(button.unique_id, "controller-test_reset")

    async def test_system_reset_explicitly_clears_hot_water_override(self):
        from custom_components.evohome.button import EvoSystemResetButton
        coord = self.coordinator(MagicMock())
        async def await_api(coro, **kwargs):
            return await coro
        coord.call_client_api = AsyncMock(side_effect=await_api)
        coord.async_request_refresh = AsyncMock()
        self.system.reset = AsyncMock()
        self.system.hotwater = SimpleNamespace(reset=AsyncMock())
        await EvoSystemResetButton(coord, self.system).async_press()
        self.system.reset.assert_awaited_once()
        self.system.hotwater.reset.assert_awaited_once()
        coord.async_request_refresh.assert_awaited_once()

    async def test_system_reset_dhw_failure_reaches_caller_and_refreshes_state(self):
        from custom_components.evohome.button import EvoSystemResetButton
        coord = self.coordinator(MagicMock())
        coord.async_request_refresh = AsyncMock()
        self.system.reset = AsyncMock()
        self.system.hotwater = SimpleNamespace(reset=AsyncMock(
            side_effect=evo.EvohomeError("DHW reset failed")))
        with self.assertRaises(HomeAssistantError):
            await EvoSystemResetButton(coord, self.system).async_press()
        self.system.hotwater.reset.assert_awaited_once()
        coord.async_request_refresh.assert_awaited_once()

    async def test_options_schema_enforces_polling_bounds(self):
        flow = EvohomeOptionsFlow()
        flow.hass = self.hass
        with patch.object(type(flow), "config_entry", new_callable=lambda: property(lambda _: self.entry())):
            result = await flow.async_step_init()
        schema = result["data_schema"]
        self.assertEqual(schema({"scan_interval": 300}), {"scan_interval": 300})
        with self.assertRaises(Exception):
            schema({"scan_interval": 1})

    async def test_temperature_sensor_is_area_compatible_and_not_the_setpoint(self):
        from custom_components.evohome.sensor import EvoTemperatureSensor
        coord = self.coordinator(MagicMock())
        coord.last_update_success = True
        zone = SimpleNamespace(id="zone-test", name="Test room", temperature=18.0,
            target_heat_temperature=5.0, tcs=self.system)
        sensor = EvoTemperatureSensor(coord, zone)
        self.assertEqual(sensor.native_value, 18.0)
        self.assertEqual(sensor.device_class, "temperature")
        self.assertEqual(sensor.state_class, "measurement")
        self.assertEqual(sensor.native_unit_of_measurement, "\u00b0C")
        self.assertTrue(sensor.available)
        self.assertEqual(sensor.unique_id, "zone-test_temperature")
        coord.temps[zone.id] = 18.4
        self.assertEqual(sensor.native_value, 18.4)
        coord.temps[zone.id] = 0.0
        self.assertEqual(sensor.native_value, 0.0)
        coord.temps.clear()
        zone.temperature = None
        self.assertFalse(sensor.available)
        self.assertIsNone(sensor.native_value)
        zone.temperature = float("nan")
        self.assertFalse(sensor.available)

    async def test_temperature_sensor_unavailable_when_polling_fails(self):
        from custom_components.evohome.sensor import EvoTemperatureSensor
        coord = self.coordinator(MagicMock())
        coord.last_update_success = False
        zone = SimpleNamespace(id="zone-test", name="Test", temperature=18.0, tcs=self.system)
        self.assertFalse(EvoTemperatureSensor(coord, zone).available)

    async def test_high_precision_auth_failure_clears_stale_readings(self):
        coord = self.coordinator(MagicMock())
        coord.temps = {"zone-test": 18.4}
        coord.client_v1 = SimpleNamespace(update=AsyncMock(
            side_effect=evo_v1.BadUserCredentialsError("invalid")))
        await coord._update_v1_api_temps()
        self.assertIsNone(coord.client_v1)
        self.assertEqual(coord.temps, {})

    async def test_real_flow_manager_loads_custom_integration(self):
        (Path(self.temp.name) / "custom_components").symlink_to(
            Path(__file__).resolve().parents[1] / "custom_components", target_is_directory=True)
        with patch.object(EvohomeConfigFlow, "_async_discover", AsyncMock(return_value=self.rows)), \
             patch.object(self.hass.config_entries, "async_setup", AsyncMock(return_value=True)):
            result = await self.hass.config_entries.flow.async_init("evohome", context={"source": "user"})
            self.assertEqual(result["step_id"], "user")
            result = await self.hass.config_entries.flow.async_configure(result["flow_id"], self.credentials)
            self.assertEqual(result["step_id"], "controller")
            result = await self.hass.config_entries.flow.async_configure(result["flow_id"], {"system_id": self.system.id})
            self.assertEqual(result["type"], "create_entry")
            await self.hass.async_block_till_done()
        self.assertEqual(len(self.hass.config_entries.async_entries("evohome")), 1)

    async def test_registry_adopts_legacy_entity_without_renaming(self):
        registry = er.async_get(self.hass)
        old = registry.async_get_or_create("climate", "evohome", "zone-test",
            suggested_object_id="test_room")
        entry = self.entry()
        with patch.object(self.hass.config_entries, "async_setup", AsyncMock(return_value=True)):
            await self.hass.config_entries.async_add(entry)
        adopted = registry.async_get_or_create("climate", "evohome", "zone-test",
            config_entry=entry, suggested_object_id="new_room")
        self.assertEqual(adopted.entity_id, old.entity_id)
        self.assertEqual(adopted.config_entry_id, entry.entry_id)

    async def test_temperature_sensor_inherits_legacy_room_suggestion(self):
        from custom_components.evohome.sensor import EvoTemperatureSensor
        area = ar.async_get(self.hass).async_create("Test room")
        registry = er.async_get(self.hass)
        climate = registry.async_get_or_create("climate", "evohome", "zone-test")
        registry.async_update_entity(climate.entity_id, area_id=area.id)
        coord = self.coordinator(MagicMock())
        zone = SimpleNamespace(id="zone-test", name="Test", temperature=18.0, tcs=self.system)
        sensor = EvoTemperatureSensor(coord, zone)
        self.assertEqual(sensor.device_info["suggested_area"], "Test room")

    async def test_diagnostics_do_not_include_credentials_or_identifiers(self):
        from custom_components.evohome.diagnostics import async_get_config_entry_diagnostics
        import json
        entry = self.entry()
        coord = self.coordinator(MagicMock())
        coord.tcs = SimpleNamespace(zones=[], hotwater=None)
        entry.runtime_data = SimpleNamespace(coordinator=coord)
        output = json.dumps(await async_get_config_entry_diagnostics(self.hass, entry))
        for forbidden in ["test@example.invalid", "test-only", "controller-test", "location-test"]:
            self.assertNotIn(forbidden, output)

    async def test_migrated_climate_and_dhw_have_own_names_and_keep_their_areas(self):
        from custom_components.evohome.climate import EvoZone, EvoController
        from custom_components.evohome.water_heater import EvoDHW
        import json
        names=json.loads((Path(__file__).resolve().parents[1] /
            'custom_components/evohome/strings.json').read_text())['entity']
        entry=self.entry()
        with patch.object(self.hass.config_entries,'async_setup',AsyncMock(return_value=True)):
            await self.hass.config_entries.async_add(entry)
        registry=er.async_get(self.hass)
        area=ar.async_get(self.hass).async_create('Test room')
        for domain,kind,cls in [('climate','zone',EvoZone),('climate','controller',EvoController),
                                ('water_heater','dhw',EvoDHW)]:
            uid='naming-'+kind
            legacy=registry.async_get_or_create(domain,'evohome',uid,original_name='Test room')
            registry.async_update_entity(legacy.entity_id,area_id=area.id)
            device=dr.async_get(self.hass).async_get_or_create(config_entry_id=entry.entry_id,
                identifiers={('evohome',uid)},name='Test room')
            broken=registry.async_get_or_create(domain,'evohome',uid,config_entry=entry,
                device_id=device.id,has_entity_name=False,original_name='Test room')
            self.assertTrue(er._has_own_area_without_own_name(self.hass,broken))
            model=object.__new__(cls)
            own_name=names[domain][model.translation_key]['name']
            fixed=registry.async_get_or_create(domain,'evohome',uid,config_entry=entry,
                device_id=device.id,has_entity_name=model.has_entity_name,original_name=own_name)
            self.assertFalse(er._has_own_area_without_own_name(self.hass,fixed))
            self.assertEqual(fixed.entity_id,legacy.entity_id)
            self.assertEqual(fixed.area_id,area.id)
            self.assertEqual(er.async_get_unprefixed_name(self.hass,fixed),own_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
