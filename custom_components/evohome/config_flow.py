"""UI setup, legacy import, reauthentication, and options for Evohome."""

from aiohttp import ClientError
import evohomeasync2 as evo
import probatio

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_LOCATION_IDX, DOMAIN
from .storage import TokenManager


class EvohomeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure a single account/controller, matching the legacy scope."""

    VERSION = 1

    async def _async_discover(self, data: dict) -> list[tuple]:
        manager = TokenManager(
            self.hass, data[CONF_USERNAME], data[CONF_PASSWORD],
            async_get_clientsession(self.hass), store_key=None,
        )
        client = evo.EvohomeClient(manager)
        await client.update(dont_update_status=True)
        return [
            (idx, loc, system)
            for idx, loc in enumerate(client.locations)
            for gateway in loc.gateways for system in gateway.systems
        ]

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors = {}
        if user_input is not None:
            try:
                self._systems = await self._async_discover(user_input)
            except evo.BadUserCredentialsError:
                errors["base"] = "invalid_auth"
            except (evo.EvohomeError, ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                if not self._systems:
                    return self.async_abort(reason="no_systems")
                self._credentials = user_input
                return await self.async_step_controller()
        return self.async_show_form(step_id="user", data_schema=probatio.Schema({
            probatio.Required(CONF_USERNAME): str,
            probatio.Required(CONF_PASSWORD): str,
        }), errors=errors)

    async def async_step_controller(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            selected = next((r for r in self._systems if r[2].id == user_input["system_id"]), None)
            if selected is None:
                return self.async_abort(reason="no_systems")
            idx, loc, system = selected
            await self.async_set_unique_id(f"{loc.id}_{system.id}")
            self._abort_if_unique_id_configured()
            if self._async_current_entries():
                return self.async_abort(reason="single_instance_allowed")
            return self.async_create_entry(title=loc.name, data={
                **self._credentials, CONF_LOCATION_IDX: idx,
                "location_id": loc.id, "system_id": system.id,
            }, options={CONF_SCAN_INTERVAL: 300})
        choices = {r[2].id: f"{r[1].name} ({r[2].id})" for r in self._systems}
        return self.async_show_form(step_id="controller", data_schema=probatio.Schema({
            probatio.Required("system_id"): probatio.In(choices),
        }))

    async def async_step_import(self, user_input) -> ConfigFlowResult:
        if self._async_current_entries():
            self._yaml_issue()
            return self.async_abort(reason="single_instance_allowed")
        try:
            systems = await self._async_discover(user_input)
        except evo.BadUserCredentialsError:
            return self.async_abort(reason="invalid_auth")
        except (evo.EvohomeError, ClientError, TimeoutError):
            return self.async_abort(reason="cannot_connect")
        selected = next((r for r in systems if r[0] == user_input.get(CONF_LOCATION_IDX, 0)), None)
        if selected is None:
            return self.async_abort(reason="no_systems")
        idx, loc, system = selected
        await self.async_set_unique_id(f"{loc.id}_{system.id}")
        self._abort_if_unique_id_configured()
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        self._yaml_issue()
        return self.async_create_entry(title=loc.name, data={
            CONF_USERNAME: user_input[CONF_USERNAME],
            CONF_PASSWORD: user_input[CONF_PASSWORD],
            CONF_LOCATION_IDX: idx, "location_id": loc.id, "system_id": system.id,
        }, options={CONF_SCAN_INTERVAL: max(180, user_input.get(CONF_SCAN_INTERVAL, 300))})

    @callback
    def _yaml_issue(self) -> None:
        ir.async_create_issue(self.hass, DOMAIN, "yaml_imported", is_fixable=False,
            severity=ir.IssueSeverity.WARNING, translation_key="yaml_imported")

    async def async_step_reauth(self, entry_data) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> ConfigFlowResult:
        entry = self._get_reauth_entry()
        errors = {}
        if user_input is not None:
            try:
                systems = await self._async_discover({**entry.data, **user_input})
            except evo.BadUserCredentialsError:
                errors["base"] = "invalid_auth"
            except (evo.EvohomeError, ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                if not any(loc.id == entry.data["location_id"] and system.id == entry.data["system_id"]
                           for _, loc, system in systems):
                    errors["base"] = "wrong_controller"
                else:
                    return self.async_update_reload_and_abort(entry, data_updates=user_input)
        return self.async_show_form(step_id="reauth_confirm", data_schema=probatio.Schema({
            probatio.Required(CONF_USERNAME, default=entry.data[CONF_USERNAME]): str,
            probatio.Required(CONF_PASSWORD): str,
        }), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EvohomeOptionsFlow()


class EvohomeOptionsFlow(OptionsFlow):
    """Change polling without YAML; conservative cloud polling minimum."""

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(step_id="init", data_schema=probatio.Schema({
            probatio.Required(CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 300)):
                probatio.All(probatio.Coerce(int), probatio.Range(min=180, max=3600)),
        }))
