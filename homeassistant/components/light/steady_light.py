"""
Light entities wrapper that doesn't allow flickering

For more information about this platform, please refer to the documentation at
https://home-assistant.io/components/steady_light/ TODO HOW TO GET URL?
"""
import logging
import voluptuous as vol

from typing import Any
from homeassistant.core import State, callback
from homeassistant.components.light import (
    Light, PLATFORM_SCHEMA)
from homeassistant.components import light
from homeassistant.const import (
    STATE_ON,
    ATTR_ENTITY_ID,
    CONF_NAME,
    CONF_ENTITY_ID,
    STATE_UNAVAILABLE
)
from homeassistant.helpers.typing import HomeAssistantType, ConfigType
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.protect_against_flickering import stready
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Steady Light'
CONF_MIN_DUR = 'min_cycle_duration'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MIN_DUR, default=15): vol.All(cv.time_period, cv.positive_timedelta),
    vol.Required(CONF_ENTITY_ID): cv.entity_domain(light.DOMAIN)
})


async def async_setup_platform(hass: HomeAssistantType, config: ConfigType,
                               async_add_entities,
                               discovery_info=None) -> None:
    """Initialize Steady Light platform."""
    entity_id = config[CONF_ENTITY_ID]
    wrapped_entity = hass.data[light.DOMAIN].get_entity(entity_id)
    min_cycle_duration = config.get(CONF_MIN_DUR)
    async_add_entities([SteadyLight(config.get(CONF_NAME),
                                    wrapped_entity,
                                    min_cycle_duration)], True)


@steady(("async_turn_on", "async_turn_off"))
class SteadyLight(Light):
    """ Wraps a light to protect it against flickering. """

    def __init__(self, name: str, light_entity, min_cycle_duration, *args, **kwargs) -> None:
        """Initialize Steady Light."""
        super().__init__(*args, **kwargs)
        self._name = name
        self._light_entity = light_entity
        self._steady_decorator.min_cycle_duration = min_cycle_duration

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    async def async_turn_on(self, **kwargs):
        """Forward the turn_on command to the switch in this light switch."""
        return await self._light_entity.async_turn_on(**kwargs)

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        _LOGGER.error("Steady Light can be only turned on in an async way.")
        raise NotImplementedError()

    async def async_turn_off(self, **kwargs):
        """Forward the turn_off command to the switch in this light switch."""
        return await self._light_entity.async_turn_off(**kwargs)

    def turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        _LOGGER.error("Steady Light can be only turned off in an async way.")
        raise NotImplementedError()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._light_enitity, name)
