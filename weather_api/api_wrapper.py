import requests

class Config:
    def __init__(self):
        
        # Request Headers:
        self.headers = {}

        # URLs:
        self.base_url = 'https://api.weather.gov/'
        self.point_url = 'points/{lat},{lon}'
        self.hourly_forecast_url = 'gridpoints/{gridId}/{gridX},{gridY}/forecast/hourly'

    def get_headers(self):
        return self.headers

    def get_base_url(self):
        return self.base_url
    
    def get_point_url(self):
        return self.base_url + self.point_url
    
    def get_forecast_url(self):
        return self.base_url + self.hourly_forecast_url
    
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

    def get_gridId(self):
        return self.gridId
    
    def get_gridX(self):
        return self.gridX
    
    def get_gridY(self):
        return self.gridY

    @classmethod
    def create_from_api(cls, lat: int, lon: int ):

        config = Config()
        response = requests.request('GET', url=config.get_point_url().format(lat=lat, lon=lon), 
                                        headers=config.get_headers())
        
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

    # Reduce & Recreate the Object?
    def get_reduced_forecast(self, hours: int = 12):
        """
        Method to return forcast periods for next 'x' periods. By default 12.
        A period is equivilant to an hour.
        """
        return GridPoint(self.updated, self.periods[0:hours])

    def last_updated_from_current_time(self):
        import pendulum
        """
        Get number of minutes since weather gridpoint last updated
        """
        last_updated_dt = pendulum.parse(self.updated)
        now_dt = pendulum.now('UTC')
        updated_diff = now_dt.diff(last_updated_dt).in_minutes()
        return updated_diff
    
    def get_periods_as_json_list(self):
        json_list = [period.to_json() for period in self.periods]
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
        response = requests.request('GET', url=config.get_forecast_url().format(gridId=point.get_gridId(),
                                                                              gridX=point.get_gridX(),
                                                                              gridY=point.get_gridY()),
                                                                              headers=config.get_headers())
        

        
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
        
        self.number = number
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.is_daytime = is_daytime
        self.temperature = temperature
        self.temperature_unit = temperature_unit
        self.probability_of_precipitation_value = probability_of_precipitation_value
        self.probability_of_precipitation_unit = probability_of_precipitation_unit
        self.dewpoint_value = dewpoint_value
        self.dewpoint_unit = dewpoint_unit
        self.relative_humidity_value = relative_humidity_value
        self.relative_humidity_unit = relative_humidity_unit
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.icon = icon
        self.short_forecast = short_forecast
        self.detailed_forecast = detailed_forecast

    def to_json(self):
            return {
                "number": self.number,
                "name": self.name,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "is_daytime": self.is_daytime,
                "temperature": self.temperature,
                "temperature_unit": self.temperature_unit,
                "probability_of_precipitation_value": self.probability_of_precipitation_value,
                "probability_of_precipitation_unit": self.probability_of_precipitation_unit,
                "dewpoint_value": self.dewpoint_value,
                "dewpoint_unit": self.dewpoint_unit,
                "relative_humidity_value": self.relative_humidity_value,
                "relative_humidity_unit": self.relative_humidity_unit,
                "wind_speed": self.wind_speed,
                "wind_direction": self.wind_direction,
                "icon": self.icon,
                "short_forecast": self.short_forecast,
                "detailed_forecast": self.detailed_forecast
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


