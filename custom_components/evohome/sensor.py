"""Measured zone temperatures, selectable as Home Assistant area sensors."""
from math import isfinite
from typing import TYPE_CHECKING

import evohomeasync2 as evo

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import EvoDataUpdateCoordinator
from .device import device_info
from .entity import is_valid_zone, unique_zone_id

if TYPE_CHECKING:
    from . import EvoConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: EvoConfigEntry,
                           async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Expose a measured temperature for each supported heating zone."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([
        EvoTemperatureSensor(coordinator, zone)
        for zone in coordinator.tcs.zones if is_valid_zone(zone)
    ])


class EvoTemperatureSensor(CoordinatorEntity[EvoDataUpdateCoordinator], SensorEntity):
    """Use the same measured temperature source as the zone climate entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 1
    _attr_has_entity_name = True
    _attr_translation_key = "temperature"

    def __init__(self, coordinator: EvoDataUpdateCoordinator, zone: evo.Zone) -> None:
        super().__init__(coordinator, context=zone.id)
        self._zone = zone
        self._attr_unique_id = f"{unique_zone_id(zone)}_temperature"
        self._attr_device_info = device_info(coordinator.hass, zone, "zone")

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.temps.get(self._zone.id)
        if value is None:
            value = self._zone.temperature
        if value is None or not isfinite(value):
            return None
        return value

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None
