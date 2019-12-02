"""Platform for Saures sensors integration."""
from urllib import request, parse
import json
import logging

from homeassistant.const import(
     ATTR_ATTRIBUTION, TEMP_CELSIUS, VOLUME_LITERS, ENERGY_WATT_HOUR)

from homeassistant.helpers.entity import Entity
from .const import DEFAULT_NAME, DOMAIN, CONF_URL
from . import SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug('Start__sensor__')


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    _LOGGER.debug('Setup__sensor__')
    conf_name = hass.data[DOMAIN]['conf_name']
    link = hass.data[DOMAIN]['link']
    sensors = hass.data[DOMAIN]['nsensors']
    _LOGGER.debug('link: ' + link)
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
        # return 'Saures example'
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
        if self._sensor_input == self.hass.data[DOMAIN]['nsensors'][0][0]:
            # Send GET request to Saures server
            try:
                saures_req = request.urlopen(self.hass.data[DOMAIN]['link'],
                                             timeout=25)
            except:
                _LOGGER.debug('Update: No')
            else:
                # Get josn with correct encoding
                saures_json = json.loads(saures_req.read().decode('utf-8-sig'))
                dev = {}
                # Update all sensors connected to Saures
                for json_data in saures_json['data']['sensors'][0]['meters']:
                    if json_data['type']['number'] in {1, 2, 3, 5, 7, 8, 10}:
                        # If it is not binary sensor
                        dev[json_data['input']] = json_data['value']
                        i = 0
                        for electr_data in json_data['vals']:
                            # If sensor have more then one value
                            i += 1
                            dev[10 * json_data['input']+i] = electr_data['value']
                    elif json_data['type']['number'] in {4, 6, 9}:
                        # If it is binary sensor
                        dev[json_data['input']] = json_data['value']
                self.hass.data[DOMAIN]['values'] = dev
                _LOGGER.debug('Update: Yes')

        self._state = self.hass.data[DOMAIN]['values'].get(self._sensor_input)
