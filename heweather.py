from datetime import datetime, timedelta
import logging
import requests
from requests.exceptions import (
    ConnectionError as ConnectError, HTTPError, Timeout)
import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_PRECIPITATION, ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_TIME, ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED, PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (
    CONF_API_KEY, CONF_ID, TEMP_CELSIUS, TEMP_FAHRENHEIT)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'HeWeather'

ATTRIBUTION = "Powered by HeWeather"

MAP_CONDITION = {
    # 多云
    'cloudy': [101, 102, 103],
    # 雾
    'fog': [500, 501, 502, 503, 504, 509, 510, 511, 512, 513, 514, 515],
    # 冰雹
    'hail': [304],
    # 闪电
    'lightning': [],
    # 🌧闪电
    'lightning-rainy': [],
    # 大部多云
    'partlycloudy': [],
    # 暴雨
    'pouring': [310, 311, 312, 316, 317, 318],
    # 雨
    'rainy': [300, 301, 302, 303, 305, 306, 307, 308, 309, 313, 314, 315, 399],
    # 雪
    'snowy': [400, 401, 402, 403, 405, 406, 407, 408, 409, 410, 499],
    # 雨夹雪
    'snowy-rainy': [404],
    # 晴
    'sunny': [100],
    # 风
    'windy': [200,202,203,204,205,206,207,208,209,210,211,212,213],
    #
    # 'windy-variant': [958, 959, 960, 961],
    # 其他
    'exceptional': [104,201,507,508,900,901,999],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_ID): cv.string,
})

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)


def setup_platform(hass, config, add_entities, discovery_info=None):
    api_key = config.get(CONF_API_KEY)
    id = config.get(CONF_ID)

    heweather = WeatherData(api_key, id)
    add_entities([HeWeather(heweather)], True)


class HeWeather(WeatherEntity):

    def __init__(self, heweather):
        self._he_currently = None
        self._he_forcasting = None
        self._he_weather = heweather

    @property
    def attribution(self):
        return ATTRIBUTION

    @property
    def name(self):
        return self._he_currently.get('HeWeather6')[0].get('basic').get('location')

    @property
    def temperature(self):
        return int(int(self._he_currently.get('HeWeather6')[0].get('now').get('fl')))

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def humidity(self):
        return round(int(self._he_currently.get('HeWeather6')[0].get('now').get('hum')), 2)

    @property
    def wind_speed(self):
        return self._he_currently.get('HeWeather6')[0].get('now').get('wind_spd')

    @property
    def wind_bearing(self):
        return self._he_currently.get('HeWeather6')[0].get('now').get('wind_dir')

    @property
    def pressure(self):
        return self._he_currently.get('HeWeather6')[0].get('now').get('pres')

    @property
    def visibility(self):
        return self._he_currently.get('HeWeather6')[0].get('now').get('vis')

    @property
    def condition(self):
        code = self._he_currently.get('HeWeather6')[0].get('now').get('cond_code')
        # ['sunny'] k for k, v in MAP_CONDITION.items() if int(code) in v
        # [k for k, v in MAP_CONDITION.items() if int(code) in v][0] ----> sunny
        return [k for k, v in MAP_CONDITION.items() if int(code) in v][0]

    @property
    def forecast(self):
        data = []

        for i in range(3):
            code = self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('cond_code_d')
            w_data = {
                ATTR_FORECAST_TIME:
                    self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('date'),
                ATTR_FORECAST_TEMP:
                    int(self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('tmp_max')),
                ATTR_FORECAST_TEMP_LOW:
                    int(self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('tmp_min')),
                ATTR_FORECAST_PRECIPITATION:
                    self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('pcpn'),
                ATTR_FORECAST_WIND_SPEED:
                    self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('wind_spd'),
                ATTR_FORECAST_WIND_BEARING:
                    self._he_forcasting.get('HeWeather6')[0].get('daily_forecast')[i].get('wind_dir'),
                ATTR_FORECAST_CONDITION:
                    [k for k, v in MAP_CONDITION.items() if int(code) in v][0],
            }
            _LOGGER.error("TEST" + [k for k, v in MAP_CONDITION.items() if int(code) in v][0])
            data.append(w_data)
        return data

    def update(self):
        self._he_weather.update()
        self._he_currently = self._he_weather.currently
        self._he_forcasting = self._he_weather.forecast_data


class WeatherData:

    def __init__(self, key, city):
        self.key = key
        self.city = city
        self._url = "https://free-api.heweather.com/s6/weather/now"
        self._weather_forcasting_url = "https://free-api.heweather.com/s6/weather/forecast"
        self._params = {"location": city, "key": key}
        self.currently = None
        self.forecast_data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            now_weather = requests.post(self._url, self._params)
            self.currently = now_weather.json()

            today_weather = requests.post(self._weather_forcasting_url, self._params)
            self.forecast_data = today_weather.json()

        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            _LOGGER.error("Unable to connect to HeWeather. %s", error)
