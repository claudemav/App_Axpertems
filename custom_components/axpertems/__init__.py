"""AxpertEMS — intégration Home Assistant native pour onduleurs Axpert/Voltronic."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_BAUDRATE,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    DEFAULT_BAUDRATE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import AxpertCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor", "select"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = AxpertCoordinator(
        hass,
        port=entry.data[CONF_PORT],
        baudrate=entry.data.get(CONF_BAUDRATE, DEFAULT_BAUDRATE),
        scan_interval=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    await coordinator.async_fetch_supported_currents()

    # Le "cerveau" décisionnel est entièrement porté par les automations
    # YAML (packages/axpert_brain_*.yaml). decision.py/engine.py restent
    # dans le dépôt comme référence testée (31 tests) mais ne font plus
    # partie du composant chargé par HA.

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        stored = hass.data[DOMAIN].pop(entry.entry_id)
        await stored["coordinator"].async_shutdown()
    return unload_ok