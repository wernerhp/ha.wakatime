"""
A platform that provides information about stats in wakatime.

For more details on this component, refer to the documentation at
https://github.com/hudsonbrendon/sensor.wakatime
"""
import logging

import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from aiohttp import BasicAuth
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity

CONF_API_KEY = "api_key"

ICON = "mdi:clock-time-five-outline"

BASE_URL = "https://wakatime.com/api/v1/{}"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor platform."""
    api_key = config["api_key"]
    session = async_create_clientsession(hass)
    name = "Wakatime"
    async_add_entities([WakatimeSensor(api_key, name, session)], True)


class WakatimeSensor(Entity):
    """Wakatime.com Sensor class"""

    def __init__(self, api_key, name, session):
        self._state = 0
        self._api_key = api_key
        self.session = session
        self._name = name
        self._languages = []

    async def async_update(self):
        """Update sensor."""
        _LOGGER.debug("%s - Running update", self._name)
        try:
            async with async_timeout.timeout(10, loop=self.hass.loop):
                response = await self.session.get(
                    BASE_URL.format("users/current/stats/last_7_days"),
                    headers={"Authorization": f"Basic {self._api_key}"},
                )
                stats = await response.json()

                self._state = stats["data"]["created_at"]

                self._languages = [language for language in stats["data"]["languages"]]

        except Exception as error:
            _LOGGER.debug("%s - Could not update - %s", self._name, error)

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def state(self):
        """State."""
        return self._state

    @property
    def languages(self):
        """Languages."""
        return [
            i
            for n, i in enumerate(self._languages)
            if i not in self._languages[n + 1 :]
        ]

    @property
    def icon(self):
        """Icon."""
        return ICON

    @property
    def device_state_attributes(self):
        """Attributes."""
        return {
            "name": self.name,
            "languages": self.languages,
        }

