"""Saures custom component integration for Home Assistant"""
from urllib import request, parse
import json

import voluptuous as vol

import logging

from homeassistant.helpers import config_validation as cv

from homeassistant.const import(
     ATTR_ATTRIBUTION, CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS,
     VOLUME_LITERS, ENERGY_WATT_HOUR, CONF_NAME)
from .const import DEFAULT_NAME, DOMAIN, CONF_URL


_LOGGER = logging.getLogger(__name__)

_LOGGER.debug('Start__init__')

SENSOR_TYPES = {
    1: [None, VOLUME_LITERS, 'mdi:speedometer-slow'],  # Cold water meter (l)
    2: [None, VOLUME_LITERS, 'mdi:speedometer-slow'],  # Hot water meter (l)
    3: [None, VOLUME_LITERS, 'mdi:speedometer-slow'],  # Gas meter (l)
    4: ['moisture', None, None],  # Leak sensor
    5: ['temperature', TEMP_CELSIUS, None],  # Temperature sensor(celsius)
    6: ['opening', None, None],  # Valve opening sensor
    7: ['power', ENERGY_WATT_HOUR, 'mdi:speedometer-slow'],  # Heat meter(wth)
    8: ['power', ENERGY_WATT_HOUR, 'mdi:speedometer-slow'],  # Electricity(wth)
    9: ['connectivity', None, None],  # Dry contact
    10: [None, None, 'mdi:valve'],  # Position of valve
               }

_LOGGER.debug('DOMAIN:' + DOMAIN)
_LOGGER.debug('CONF_NAME: ' + CONF_NAME)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Your controller/hub specific code."""
    _LOGGER.debug('Setup__init__')
    conf_name = config[DOMAIN][CONF_NAME]  # Get platform name from config
    username = config[DOMAIN][CONF_USERNAME]  # Get password from config
    password = config[DOMAIN][CONF_PASSWORD]  # Get user name from config

    """Setup Saures Object and get all sensors into it"""
    ss = Saures(username, password)
    if ss.SID is None:
        _LOGGER.error("Check, name(e-mail) or password is not correct!")
        # Input data were not correct. Sensor will not set.
        return False
    if ss.allsensors is None:
        _LOGGER.error("Check, comunication Saures device to server!")
        # Saures sensor not connected to server. Sensor will not set.
        return False

    _LOGGER.debug('nsensors: ' + str(ss.allsensors[0]))
    _LOGGER.debug('bsensors: ' + str(ss.allsensors[1]))
    _LOGGER.debug('values: ' + str(ss.allsensors[2]))

    """Send datata to platforms (sensor, bynary_sensor)"""
    hass.data[DOMAIN] = {
        'conf_name': conf_name,
        'link': CONF_URL + 'meter/meters' + '?sid=' +
        ss.SID + '&flat_id=' + str(ss.flat),
        'nsensors': ss.allsensors[0],
        'bsensors': ss.allsensors[1],
        'values': ss.allsensors[2],
                        }

    """Starting platforms sensors"""
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('binary_sensor', DOMAIN, {}, config)
    return True


class Saures:
    def __init__(self, userID, PassID):
        """Inisialize connection to Saures server """
        self.userID = userID
        self.PassID = PassID
        self.SID = self.getSID()
        self.flat = self.getflat()
        self.allsensors = self.getsensors()

    def getSID(self):
        """Make POST request to Saures server """
        # Collect data for request
        reqstr = {'email': self.userID, 'password': self.PassID}
        # Convert data for request
        convstr = parse.urlencode(reqstr).encode()
        # Send POST request to Saures server
        req = request.urlopen(CONF_URL + 'auth/login', convstr)
        # Get josn with correct encoding
        saures_json = json.loads(req.read().decode('utf-8-sig'))
        # Check if server responce is 'OK'
        if saures_json['status'] != 'ok':
            _LOGGER.debug('NO SID. Check name(e-mail) and password!')
            return None
        # Get SID data from josn
        saures_sid = saures_json['data']['sid']
        _LOGGER.debug('SID: OK')
        return saures_sid

    def getflat(self):
        """Make GET request to Saures server """
        if self.SID is None:
            return None
        # Send GET request to Saures server
        reqstr = request.urlopen(CONF_URL + 'company/flats' + '?sid=' +
                                 str(self.SID))
        # Get josn with correct encoding
        saures_json = json.loads(reqstr.read().decode('utf-8-sig'))
        # Get flat ID from josn
        saures_flat_id = saures_json['data']['flats'][0]['id']
        _LOGGER.debug('Flat ID: OK')
        return saures_flat_id

    def getsensors(self):
        """Make GET request to Saures server """
        if (self.SID or self.flat) is None:
            return None
        # Send GET request to Saures server
        saures_req = request.urlopen(CONF_URL + 'meter/meters' + '?sid=' +
                                     self.SID + '&flat_id=' + str(self.flat))
        # Get josn with correct encoding
        saures_json = json.loads(saures_req.read().decode('utf-8-sig'))
        _LOGGER.debug('Server responce: ' + str(saures_json))
        dev = [[], [], {}]
        if saures_json['status'] != 'ok':
            _LOGGER.debug('Saures status: ' + str(saures_json['status']))
            return None
        # Check all sensors connected to Saures
        for json_data in saures_json['data']['sensors'][0]['meters']:
            # If it is not binary sensor
            if json_data['type']['number'] in {1, 2, 3, 5, 7, 8, 10}:
                dev[0].append([json_data['input'], json_data['type']['number'],
                              json_data['meter_name']])
                dev[2][json_data['input']] = json_data['value']
                i = 0
                for electr_data in json_data['vals']:
                    # If sensor have more then one value (3 phase sensor)
                    i += 1
                    dev[0].append([10*json_data['input']+i,
                                  json_data['type']['number'],
                                  json_data['meter_name']+'_('+str(i)+')'])
                    dev[2][10 * json_data['input'] + i] = electr_data['value']
            elif json_data['type']['number'] in {4, 6, 9}:
                # If it is binary sensor
                dev[1].append([json_data['input'],
                               json_data['type']['number'],
                               json_data['meter_name']])
                dev[2][json_data['input']] = json_data['value']
        return dev
