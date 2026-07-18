"""Sélecteurs pilotant l'onduleur directement via le coordinator."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import AxpertCoordinator
from .entity import AxpertEntity
from .protocol import CHARGER_PRIORITY_COMMANDS, OUTPUT_MODE_COMMANDS

OPTIONS = list(OUTPUT_MODE_COMMANDS)
CHARGER_OPTIONS = list(CHARGER_PRIORITY_COMMANDS)

_PRIORITY_TO_OPTION = {
    "Utility first": "E2C", "Solar first": "SOLAIRE", "SBU first": "BATTERIE",
}
_CHARGER_PRIORITY_TO_OPTION = {
    "Utility first": "E2C", "Solar first": "SOLAIRE",
    "Solar and utility": "MIXTE", "Solar only": "SOLAIRE_SEUL",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: AxpertCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            AxpertOutputModeSelect(coordinator),
            AxpertChargerPrioritySelect(coordinator),
            AxpertMaxChargingCurrentSelect(coordinator),
            AxpertMaxUtilityChargingCurrentSelect(coordinator),
        ]
    )


class AxpertOutputModeSelect(AxpertEntity, SelectEntity):
    _attr_options = OPTIONS
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator: AxpertCoordinator) -> None:
        super().__init__(coordinator, "output_mode")
        self._attr_name = "Axpert Output Mode"

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        priority = self.coordinator.data["qpiri"].get("output_source_priority")
        return _PRIORITY_TO_OPTION.get(priority)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_output_mode(option)


class AxpertChargerPrioritySelect(AxpertEntity, SelectEntity):
    _attr_options = CHARGER_OPTIONS
    _attr_icon = "mdi:battery-charging-100"

    def __init__(self, coordinator: AxpertCoordinator) -> None:
        super().__init__(coordinator, "charger_priority")
        self._attr_name = "Axpert Charger Priority"

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        priority = self.coordinator.data["qpiri"].get("charger_source_priority")
        return _CHARGER_PRIORITY_TO_OPTION.get(priority)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_charger_priority(option)


class AxpertMaxChargingCurrentSelect(AxpertEntity, SelectEntity):
    _attr_icon = "mdi:current-dc"

    def __init__(self, coordinator: AxpertCoordinator) -> None:
        super().__init__(coordinator, "max_charging_current_select")
        self._attr_name = "Axpert Max Charging Current"

    @property
    def options(self) -> list[str]:
        return [str(v) for v in self.coordinator.supported_max_charging_currents] or ["0"]

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data["qpiri"].get("max_charging_current")
        return str(int(value)) if value is not None else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_max_charging_current(int(option))


class AxpertMaxUtilityChargingCurrentSelect(AxpertEntity, SelectEntity):
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator: AxpertCoordinator) -> None:
        super().__init__(coordinator, "max_utility_charging_current_select")
        self._attr_name = "Axpert Max Utility Charging Current"

    @property
    def options(self) -> list[str]:
        return [str(v) for v in self.coordinator.supported_max_utility_charging_currents] or ["0"]

    @property
    def current_option(self) -> str | None:
        if self.coordinator.data is None:
            return None
        value = self.coordinator.data["qpiri"].get("max_ac_charging_current")
        return str(int(value)) if value is not None else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_max_utility_charging_current(int(option))