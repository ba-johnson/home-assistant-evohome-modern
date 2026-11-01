"""Device registry metadata shared by entities for a controller or zone."""
from homeassistant.helpers import area_registry as ar, entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


def device_info(hass, device, kind: str) -> DeviceInfo:
    """Group entities without changing existing platform unique IDs."""
    device_id = device.id
    if kind == "zone" and device.id == device.tcs.id:
        device_id += "z"
    name = device.location.name if kind == "system" else device.name
    info = DeviceInfo(
        identifiers={(DOMAIN, f"{kind}_{device_id}")},
        manufacturer="Honeywell", name=name,
        model=str(getattr(device, "model", kind)),
    )
    # Reuse the room already assigned to the legacy climate entity as a suggestion.
    # Device registry preserves a user's existing device-area choice.
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("climate", DOMAIN, device_id)
    entity = registry.async_get(entity_id) if entity_id else None
    if entity and entity.area_id:
        area = ar.async_get(hass).async_get_area(entity.area_id)
        if area:
            info["suggested_area"] = area.name
    return info
