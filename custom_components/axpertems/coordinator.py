"""Coordinator : unique propriétaire du port série, alimente toutes les entités."""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .axpert import AxpertClient
from .const import DOMAIN
from .exceptions import AxpertCommandRejectedError, AxpertError

_LOGGER = logging.getLogger(__name__)

QPIRI_REFRESH_SECONDS = 600  # 10 minutes


class AxpertCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll unique du port série ; toutes les entités lisent coordinator.data."""

    def __init__(
        self,
        hass: HomeAssistant,
        port: str,
        baudrate: int,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._client = AxpertClient(port, baudrate=baudrate)
        self._port_open = False
        self._qpiri_cache: dict[str, Any] = {}
        self._last_qpiri_fetch: float = 0.0
        self.supported_max_charging_currents: list[int] = []
        self.supported_max_utility_charging_currents: list[int] = []

    async def async_fetch_supported_currents(self) -> None:
        """QMCHGCR/QMUCHGCR : lu une fois au démarrage pour n'exposer que
        les paliers réellement acceptés par CET onduleur."""
        try:
            self.supported_max_charging_currents = await self.hass.async_add_executor_job(
                self._client.get_supported_max_charging_currents
            )
            self.supported_max_utility_charging_currents = await self.hass.async_add_executor_job(
                self._client.get_supported_max_utility_charging_currents
            )
        except AxpertError as err:
            _LOGGER.warning("Paliers de courant non lus (QMCHGCR/QMUCHGCR) : %s", err)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(self._poll)
        except AxpertError as err:
            # Fermeture RÉELLE du port (pas juste le flag) : sinon l'objet
            # serial.Serial peut rester ouvert dans un état défectueux.
            self._safe_close()
            raise UpdateFailed(str(err)) from err

    def _poll(self) -> dict[str, Any]:
        if not self._port_open:
            self._client.open()
            self._port_open = True

        data = self._client.get_realtime_data()  # QPIGS + QMOD, à chaque cycle

        # QPIRI : au démarrage (cache vide), puis toutes les 10 minutes.
        # Une écriture force un refresh immédiat via _force_qpiri_refresh.
        if not self._qpiri_cache or (time.monotonic() - self._last_qpiri_fetch) > QPIRI_REFRESH_SECONDS:
            self._qpiri_cache = self._client.get_settings()
            self._last_qpiri_fetch = time.monotonic()

        return {**data, **self._qpiri_cache}

    def _force_qpiri_refresh(self) -> None:
        """Invalide le cache QPIRI pour qu'il soit relu au prochain poll —
        utilisé juste après une commande d'écriture (le réglage a changé)."""
        self._qpiri_cache = {}

    async def async_set_output_mode(self, mode: str) -> None:
        try:
            await self.hass.async_add_executor_job(
                self._client.set_output_source_priority, mode
            )
        except AxpertError as err:
            raise UpdateFailed(str(err)) from err
        self._force_qpiri_refresh()
        await self.async_request_refresh()

    async def async_set_charger_priority(self, priority: str) -> None:
        try:
            await self.hass.async_add_executor_job(
                self._client.set_charger_source_priority, priority
            )
        except AxpertCommandRejectedError:
            raise
        except AxpertError as err:
            raise UpdateFailed(str(err)) from err
        self._force_qpiri_refresh()
        await self.async_request_refresh()

    async def async_set_max_charging_current(self, amps: int) -> None:
        try:
            await self.hass.async_add_executor_job(
                self._client.set_max_charging_current, amps
            )
        except AxpertCommandRejectedError:
            raise
        except AxpertError as err:
            raise UpdateFailed(str(err)) from err
        self._force_qpiri_refresh()
        await self.async_request_refresh()

    async def async_set_max_utility_charging_current(self, amps: int) -> None:
        try:
            await self.hass.async_add_executor_job(
                self._client.set_max_utility_charging_current, amps
            )
        except AxpertCommandRejectedError:
            raise
        except AxpertError as err:
            raise UpdateFailed(str(err)) from err
        self._force_qpiri_refresh()
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        await self.hass.async_add_executor_job(self._safe_close)
        await super().async_shutdown()

    def _safe_close(self) -> None:
        self._client.close()
        self._port_open = False