"""Platform for Saures binary sensors integration."""
import logging
from homeassistant.helpers.entity import Entity
from .const import DEFAULT_NAME, DOMAIN, CONF_URL
from . import SENSOR_TYPES   # update_sensors

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug('Start__binary_sensor__')


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug('Setup__sensor__')
    conf_name = hass.data[DOMAIN]['conf_name']
    sensors = hass.data[DOMAIN]['bsensors']
    # All data was correct and sensor initialized
    dev = []
    for variable in sensors:
        dev.append(SauresSensor(
                               conf_name, variable[0], variable[2],
                               SENSOR_TYPES[variable[1]][0],
                               SENSOR_TYPES[variable[1]][1],
                               SENSOR_TYPES[variable[1]][2]))
    add_entities(dev, True)


class SauresSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, conf_name, sensor_input, name,
                 sensor_type, units, icon):
        """Initialize the sensor."""
        self._state = None
        self.conf_name = conf_name
        self._name = name
        self._sensor_input = sensor_input
        self._device_class = sensor_type
        self._unit_of_measurement = units
        self._icon = icon

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self.conf_name, self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the unit of measurement."""
        return self._device_class

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Fetch new state data for the sensor."""

        self._state = self.hass.data[DOMAIN]['values'].get(self._sensor_input)

