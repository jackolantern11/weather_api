import requests
import logging
import pandas as pd
from collections import namedtuple

logger = logging.getLogger('weather.module')
logger.setLevel(logging.INFO)

class Config:
    def __init__(self):
        
        # Request Headers:
        self.headers = {}

        # URLs:
        self.base_url = 'https://api.weather.gov/'
        self.point_url = 'points/{lat},{lon}'
        self.hourly_forecast_url = 'gridpoints/{gridId}/{gridX},{gridY}/forecast/hourly'
        self.textual_forecast_url = 'gridpoints/{wfo}/{gridX},{gridY}/forecast'

    def get_headers(self) -> dict:
        return self.headers

    def get_base_url(self) -> str:
        return self.base_url
    
    def get_point_url(self) -> str:
        return self.get_base_url() + self.point_url
    
    def get_hourly_forecast_url(self) -> str:
        return self.get_base_url() + self.hourly_forecast_url
    
    def get_textual_forecast_url(self) -> str:
        return self.get_base_url() + self.textual_forecast_url
    
class Point:
    """
    Object representing a lat,lon point. When instatiated from create_from_api, an API request occurs returning
    data about the GridPoint the Point belongs to. This GridPoint data can be used to create a GridPoint object
    and return meaningful data around weather forecasts.
    """

    def __init__(self,
                 lon: int,
                 lat: int,
                 id: str,
                 geometry: dict, 
                 type: str,
                 cwa: str,
                 forecast_office: str,
                 gridId: str,
                 gridX: int,
                 gridY: int,
                 forecast: str,
                 forecast_hourly: str,
                 forecast_grid_data: str,
                 observation_stations: str,
                 relative_location: dict,
                 forecast_zone: str,
                 county: str,
                 fire_weather_zone: str,
                 time_zone: str,
                 radar_station: str
                 ):
        
        self.config = Config()
        self.lon = lon
        self.lat = lat
        self.id = id
        self.geometry = geometry
        self.type = type
        self.cwa = cwa
        self.forecast_office = forecast_office
        self.gridId = gridId
        self.gridX = gridX
        self.gridY = gridY
        self.forecast = forecast
        self.forecast_hourly = forecast_hourly
        self.forecast_grid_data = forecast_grid_data
        self.observation_stations = observation_stations
        self.relative_location = relative_location
        self.forecast_zone = forecast_zone
        self.county = county
        self.fire_weather_zone = fire_weather_zone
        self.time_zone = time_zone
        self.radar_station = radar_station
        # self.hourly_forecast = HourlyForecast()
        # self.textual_forecast = TextualForecast()
    
    def get_lon(self):
        return self.lon
    
    def get_lat(self):
        return self.lat
    
    def get_id(self):
        return self.id
    
    def get_geometry(self):
        return self.geometry
    
    def get_type(self):
        return self.type
    
    def get_cwa(self):
        return self.cwa
    
    def get_forecast_office(self):
        return self.forecast_office
    
    def get_gridId(self):
        return self.gridId
    
    def get_gridX(self):
        return self.gridX
    
    def get_gridY(self):
        return self.gridY
    
    def get_forecast(self):
        return self.forecast
    
    def get_forecast_hourly(self):
        return self.forecast_hourly
    
    def get_forecast_grid_data(self):
        return self.forecast_grid_data
    
    def get_observation_stations(self):
        return self.observation_stations
    
    def get_relative_location(self):
        return self.relative_location
    
    def get_forecast_zone(self):
        return self.forecast_zone
    
    def get_county(self):
        return self.county
    
    def get_fire_weather_zone(self):
        return self.fire_weather_zone
    
    def get_time_zone(self):
        return self.time_zone
    
    def get_radar_station(self):
        return self.radar_station
    
    # Methods for getting forecast data:
    def get_hourly_forecast(self):
        self.hourly_forecast = None

    def get_textual_forecast(self):
        self.textual_forecast = None
    
    def __repr__(self):
        return (f"Point(lon={self.get_lon()!r}, lat={self.get_lat()!r}, id={self.get_id()!r}, "
                f"geometry={self.get_geometry()!r}, type={self.get_type()!r}, "
                f"cwa={self.get_cwa()!r}, forecast_office={self.get_forecast_office()!r}, "
                f"gridId={self.get_gridId()!r}, gridX={self.get_gridX()!r}, gridY={self.get_gridY()!r}, "
                f"forecast={self.get_forecast()!r}, forecast_hourly={self.get_forecast_hourly()!r}, "
                f"forecast_grid_data={self.get_forecast_grid_data()!r}, "
                f"observation_stations={self.get_observation_stations()!r}, "
                f"relative_location={self.get_relative_location()!r}, forecast_zone={self.get_forecast_zone()!r}, "
                f"county={self.get_county()!r}, fire_weather_zone={self.get_fire_weather_zone()!r}, "
                f"time_zone={self.get_time_zone()!r}, radar_station={self.get_radar_station()!r})")

    @classmethod
    def create_from_api(cls, lat: int, lon: int):

        config = Config()
        point_response = requests.request('GET', url=config.get_point_url().format(lat=lat, lon=lon), 
                                        headers=config.get_headers())
        logger.info(f"Fetch Point: {lat = }, {lon = } - {point_response = }")
        point_response.raise_for_status()
        point_response_dict = point_response.json()

        return Point(
            lon=lon,
            lat=lat,
            id=point_response_dict['id'],
            geometry=point_response_dict['geometry'],
            type=point_response_dict['type'],
            cwa=point_response_dict['properties']['cwa'],
            forecast_office=point_response_dict['properties']['forecastOffice'],
            gridId=point_response_dict['properties']['gridId'],
            gridX=point_response_dict['properties']['gridX'],
            gridY=point_response_dict['properties']['gridY'],
            forecast=point_response_dict['properties']['forecast'],
            forecast_hourly=point_response_dict['properties']['forecastHourly'],
            forecast_grid_data=point_response_dict['properties']['forecastGridData'],
            observation_stations=point_response_dict['properties']['observationStations'],
            relative_location=point_response_dict['properties']['relativeLocation'],
            forecast_zone=point_response_dict['properties']['forecastZone'],
            county=point_response_dict['properties']['county'],
            fire_weather_zone=point_response_dict['properties']['fireWeatherZone'],
            time_zone=point_response_dict['properties']['timeZone'],
            radar_station=point_response_dict['properties']['radarStation']
        )


# Only return one of these on request?
"""
Create a point (using lat / lon)
Point has a forecast(s), GridPoint class can also exit, but not nessesarry for current app
"""
class HourlyForecast:

    def __init__(self,
                 updated: str,
                 units: str,
                 forecast_generator: str,
                 update_time: str,
                 valid_times: str,
                 elevation_unit_code: str,
                 elevation_value: str,
                 periods: list            
    ):
        self.updated = updated
        self.units = units
        self.forecast_generator = forecast_generator
        self.update_time = update_time
        self.valid_time = valid_times
        self.elevation_unit_code = elevation_unit_code
        self.elevation_value = elevation_value
        self.periods = periods

    def get_hourly_forecast_df(self) -> pd.DataFrame:
        return None
    
    def get_hourly_forecast_tuples(self) -> list:
        return None

    def get_seconds_since_last_update(self) -> int:
        return None

    @classmethod
    def create_from_api(self, grid_id: str, grid_x: int, grid_y: int):

        config = Config()
        forecast_period = namedtuple("forecast_period", ["number", "name", "startTime", "endTime", "isDaytime",
                                                         "temperature", "temperatureUnit", "temperatureTrend", ""])

        # Save the periods as named tuples, dicts, or seperate class structures. I'm thinking named tuples?
        hourly_forecast_response = requests.request('GET', url=config.get_hourly_forecast_url().format(gridId=grid_id,
                                                                              gridX=grid_x,
                                                                              gridY=grid_y),
                                                                              headers=config.get_headers())
        logger.info(f"{hourly_forecast_response = }")
        hourly_forecast_response.raise_for_status()
        hourly_forecast_dict = hourly_forecast_response.json()

        return HourlyForecast(
            updated=hourly_forecast_dict['properties']['updated'],
            units=hourly_forecast_dict['properties']['units'],
            forecast_generator=hourly_forecast_dict['properties']['forecastGenerator'],
            update_time=hourly_forecast_dict['properties']['updateTime'],
            valid_times=hourly_forecast_dict['properties']['validTimes'],
            elevation_unit_code=hourly_forecast_dict['properties']['elevation']['unitCode'],
            elevation_value=hourly_forecast_dict['properties']['elevation']['value'],
            periods=hourly_forecast_dict['periods']
        )


class TextualForecast:
    # From API method (use in GridPoint)
    # Last Updated Function
    # Get forecast periods: dict / df
    None

# Create object for hourly_forecast, textual_forecast (reduce reliance on dict struct & and allow for methods
# on those classes specifically - example: check last updated time ago since pretty universal for any accessing
# program
class GridPoint:
    """
    Class representing a grid point. This is a 1.5km x 1.5km area composed of various lat, lon points. A GridPoint
    has many points. Each GridPoint also has an hourly_forecast, textual_forecast, numerical_forecast, stations,
    and several potential composite attributes - see the api docs.
    """
    def __init__(self, 
                 hourly_forecast: dict = {},
                 textual_forecast: dict = {}):
        self.hourly_forecast = hourly_forecast
        self.textual_forecast = textual_forecast

    def get_hourly_forecast(self) -> dict:
        return self.hourly_forecast
    
    def get_textual_forecast(self) -> dict:
        return self.textual_forecast

    # Flatten nested json as prepended to column name - from pandas.io.json import json_normalize
    def get_hourly_forecast_periods_df(self) -> pd.DataFrame:
        return pd.json_normalize(data=self.get_hourly_forecast()['properties']['periods'])
    
    def get_textual_forecast_periods_df(self) -> pd.DataFrame:
        return pd.json_normalize(data=self.get_textual_forecast()['properties']['periods'])

    @classmethod
    def create_from_point(cls, point: Point):
        
        config = Config()

        # Hourly Forecast init
        hourly_forecast_response = requests.request('GET', url=config.get_hourly_forecast_url().format(gridId=point.get_gridId(),
                                                                              gridX=point.get_gridX(),
                                                                              gridY=point.get_gridY()),
                                                                              headers=config.get_headers())
        logger.info(f"{hourly_forecast_response = }")
        hourly_forecast_response.raise_for_status()
        hourly_forecast_dict = hourly_forecast_response.json()


        # Hourly Forecast init
        textual_forecast_response = requests.request('GET', url=config.get_textual_forecast_url().format(wfo=point.get_cwa(),
                                                                              gridX=point.get_gridX(),
                                                                              gridY=point.get_gridY()),
                                                                              headers=config.get_headers())
        logger.info(f"{textual_forecast_response = }")
        textual_forecast_response.raise_for_status()
        textual_forecast_dict = textual_forecast_response.json()

        return GridPoint(hourly_forecast_dict, textual_forecast_dict)


