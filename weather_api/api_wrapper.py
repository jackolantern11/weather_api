import requests
import logging

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

    def get_headers(self) -> dict:
        return self.headers

    def get_base_url(self) -> str:
        return self.base_url
    
    def get_point_url(self) -> str:
        return self.get_base_url() + self.point_url
    
    def get_forecast_url(self) -> str:
        return self.get_base_url() + self.hourly_forecast_url
    
class Point:
    def __init__(self, 
                 lon: int, 
                 lat: int, 
                 gridId: str, 
                 gridX: int, 
                 gridY: int):
        
        self.config = Config()
        self.lon = lon
        self.lat = lat
        self.gridId = gridId
        self.gridX = gridX
        self.gridY = gridY

    def get_gridId(self) -> str:
        return self.gridId
    
    def get_gridX(self) -> int:
        return self.gridX
    
    def get_gridY(self) -> int:
        return self.gridY
    
    def get_lon(self) -> int:
        return self.lon
    
    def get_lat(self) -> int:
        return self.lat

    @classmethod
    def create_from_api(cls, lat: int, lon: int):

        config = Config()
        logger.info(f"Fetching Point from API Using Lat={lat}, Lon={lon}")
        response = requests.request('GET', url=config.get_point_url().format(lat=lat, lon=lon), 
                                        headers=config.get_headers())
        logger.info(f"Request Response: {response}")
        
        response.raise_for_status()
        dict = response.json()

        return Point(
            lon=lon,
            lat=lat,
            gridId=dict['properties']['gridId'],
            gridX=dict['properties']['gridX'],
            gridY=dict['properties']['gridY']
        )
    
class GridPoint:
    def __init__(self, 
                 updated: str, 
                 periods: list):
        self.updated = updated
        self.periods = periods

    def get_updated(self) -> str:
        return self.updated
    
    def get_periods(self) -> list:
        return self.periods

    # Reduce & Recreate the Object?
    def get_reduced_forecast(self, hours: int = 12):
        """
        Method to return forcast periods for next 'x' periods. By default 12.
        A period is equivilant to an hour.
        """
        return GridPoint(self.get_updated(), self.get_periods()[0:hours])

    def last_updated_from_current_time(self) -> int:
        import pendulum
        """
        Get number of minutes since weather gridpoint last updated
        """
        last_updated_dt = pendulum.parse(self.get_updated())
        now_dt = pendulum.now('UTC')
        updated_diff = now_dt.diff(last_updated_dt).in_minutes()
        return updated_diff
    
    def get_periods_as_json_list(self) -> list:
        json_list = [period.to_json() for period in self.get_periods()]
        return json_list
    
    def get_periods_as_df(self):
        import pandas as pd
        forcast_df = pd.DataFrame(self.get_periods_as_json_list())[['start_time', 'end_time', 'temperature']]
        return forcast_df 

    @classmethod
    def create_from_api(cls, lat, lon):
        
        # Composition from Config & Point. Gridpoints have a point (sometimes many)
        config = Config()
        point = Point.create_from_api(lat=lat, lon=lon)
        logger.info(f"Fetching Grid Point Data for Grid ID: {point.get_gridId()}")
        response = requests.request('GET', url=config.get_forecast_url().format(gridId=point.get_gridId(),
                                                                              gridX=point.get_gridX(),
                                                                              gridY=point.get_gridY()),
                                                                              headers=config.get_headers())
        logger.info(f"Request Response: {response}")
        
        response.raise_for_status()

        response_json = response.json()
        response_updated = response_json['properties']['updated'] # String
        response_periods = response_json['properties']['periods'] # List

        return GridPoint(
            updated=response_updated,
            periods=[HourlyForecastPeriod.from_json(period) for period in response_periods]
        )

class HourlyForecastPeriod:
    def __init__(self, number: int, name: str, start_time: str, end_time: str, is_daytime: bool,
                 temperature: int, temperature_unit: str, probability_of_precipitation_value: int,
                 probability_of_precipitation_unit: str,
                 dewpoint_value: float, dewpoint_unit: str, relative_humidity_value: int,
                 relative_humidity_unit: str,
                 wind_speed: str, wind_direction: str, icon: str, short_forecast: str,
                 detailed_forecast: str):

        self._number = number
        self._name = name
        self._start_time = start_time
        self._end_time = end_time
        self._is_daytime = is_daytime
        self._temperature = temperature
        self._temperature_unit = temperature_unit
        self._probability_of_precipitation_value = probability_of_precipitation_value
        self._probability_of_precipitation_unit = probability_of_precipitation_unit
        self._dewpoint_value = dewpoint_value
        self._dewpoint_unit = dewpoint_unit
        self._relative_humidity_value = relative_humidity_value
        self._relative_humidity_unit = relative_humidity_unit
        self._wind_speed = wind_speed
        self._wind_direction = wind_direction
        self._icon = icon
        self._short_forecast = short_forecast
        self._detailed_forecast = detailed_forecast

    def get_number(self) -> int:
        return self._number

    def get_name(self) -> str:
        return self._name

    def get_start_time(self) -> str:
        return self._start_time

    def get_end_time(self) -> str:
        return self._end_time

    def is_daytime(self) -> bool:
        return self._is_daytime

    def get_temperature(self) -> int:
        return self._temperature

    def get_temperature_unit(self) -> str:
        return self._temperature_unit

    def get_probability_of_precipitation_value(self) -> int:
        return self._probability_of_precipitation_value

    def get_probability_of_precipitation_unit(self) -> str:
        return self._probability_of_precipitation_unit

    def get_dewpoint_value(self) -> float:
        return self._dewpoint_value

    def get_dewpoint_unit(self) -> str:
        return self._dewpoint_unit

    def get_relative_humidity_value(self) -> int:
        return self._relative_humidity_value

    def get_relative_humidity_unit(self) -> str:
        return self._relative_humidity_unit

    def get_wind_speed(self) -> str:
        return self._wind_speed

    def get_wind_direction(self) -> str:
        return self._wind_direction

    def get_icon(self) -> str:
        return self._icon

    def get_short_forecast(self) -> str:
        return self._short_forecast

    def get_detailed_forecast(self) -> str:
        return self._detailed_forecast

    def to_json(self) -> dict:
        return {
            "number": self.get_number(),
            "name": self.get_name(),
            "start_time": self.get_start_time(),
            "end_time": self.get_end_time(),
            "is_daytime": self.is_daytime(),
            "temperature": self.get_temperature(),
            "temperature_unit": self.get_temperature_unit(),
            "probability_of_precipitation_value": self.get_probability_of_precipitation_value(),
            "probability_of_precipitation_unit": self.get_probability_of_precipitation_unit(),
            "dewpoint_value": self.get_dewpoint_value(),
            "dewpoint_unit": self.get_dewpoint_unit(),
            "relative_humidity_value": self.get_relative_humidity_value(),
            "relative_humidity_unit": self.get_relative_humidity_unit(),
            "wind_speed": self.get_wind_speed(),
            "wind_direction": self.get_wind_direction(),
            "icon": self.get_icon(),
            "short_forecast": self.get_short_forecast(),
            "detailed_forecast": self.get_detailed_forecast()
        }


    @classmethod
    def from_json(cls, json_data):
        number = json_data["number"]
        name = json_data["name"]
        start_time = json_data["startTime"]
        end_time = json_data["endTime"]
        is_daytime = json_data["isDaytime"]
        temperature = json_data["temperature"]
        temperature_unit = json_data["temperatureUnit"]
        probability_of_precipitation_value = json_data["probabilityOfPrecipitation"]["value"]
        probability_of_precipitation_unit = json_data["probabilityOfPrecipitation"]["unitCode"]
        dewpoint_value = json_data["dewpoint"]["value"]
        dewpoint_unit = json_data["dewpoint"]["unitCode"]
        relative_humidity_value = json_data["relativeHumidity"]["value"]
        relative_humidity_unit = json_data["relativeHumidity"]["unitCode"]
        wind_speed = json_data["windSpeed"]
        wind_direction = json_data["windDirection"]
        icon = json_data["icon"]
        short_forecast = json_data["shortForecast"]
        detailed_forecast = json_data["detailedForecast"]
    
        return HourlyForecastPeriod(number, name, start_time, end_time, is_daytime, temperature, temperature_unit,
                probability_of_precipitation_value, probability_of_precipitation_unit, dewpoint_value, dewpoint_unit,
                relative_humidity_value, relative_humidity_unit, wind_speed, wind_direction, icon,
                short_forecast, detailed_forecast)


