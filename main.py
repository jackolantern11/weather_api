import logging
import requests
from retry import retry


""" 
Python Script to Fetch Overnight Weather Forcast, and send discord notification if temperature will
drop below 35 F. 

Data Source: National Weather Service 
(Free API Access - https://www.weather.gov/documentation/services-web-api)

"""

# Set Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console & stream handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
fh = logging.FileHandler(filename='weather.log')
fh.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)


# API Info
api_urls_dict = {"point_url": "https://api.weather.gov/points/36.35,-94.28"}

# Execute API Request
@retry(exceptions=ValueError, tries=3, delay=5)
def execute_api_request(request_type: str, url: str, headers: dict, data: dict) -> requests.request:
    response = requests.request(request_type, url=url, headers=headers, data=data)
    check_api_response(response_code=response.status_code, api_url=url)
    return response

@retry(exceptions=ValueError, tries=3, delay=5)
def send_discord_notification(msg: str) -> requests.request:
    from discordwebhook import Discord
    
    # Retry to send notification on failure
    # Send Notification (regardless of temperature)
    discord = Discord(url="https://discord.com/api/webhooks/1216423056499802162/o-OE5fN2AK7OAmB0CQBlfOpEYDPMvJbGuR5ngsKEyEJw26knRihster2cmMCS5-eapOJ")
    response = discord.post(content=f"{msg}")
    logger.info(f"Discord Post Result: {response.status_code}")

    # Check api response from discord:
    check_api_response(response.status_code, 'discord')

    return response

# Check API Response
def check_api_response(response_code: int, api_url: str) -> bool:
    
    if response_code not in {200, 201, 204}:
        logger.warning(f"Request to {api_url} Failed! Status Code: {response_code}")
        raise ValueError
    
    else:
        logger.info(f"Request to {api_url} Successful! Status Code: {response_code}")
        return True


# Main Processing Function:
def weather_script(**kwargs):
    import pendulum
    import pandas as pd

    # Request Data for Centerton, AR (based on LAT/LONG)
    point_reponse = execute_api_request("GET", url=api_urls_dict['point_url'], headers={}, data={})

    try:
        api_urls_dict['forecast_hourly'] = point_reponse.json()['properties']['forecastHourly']

    except:
        logger.error(f"Hourly Forcast URL Missing From {api_urls_dict['point_url']}. Exiting Script.")
        exit()

    # Request Forecast for Centerton, AR
    forcast_response = execute_api_request("GET", url=api_urls_dict['forecast_hourly'], headers={}, data={})
    
    # Check Forcast last updated time:
    try:
        last_updated_str = forcast_response.json()['properties']['updated']

    except:
        logger.error(f"API Missing Last Updated! Check API Docs for Last Updated. Exiting Script.")
        exit()

    last_updated_dt = pendulum.parse(last_updated_str)
    now_dt = pendulum.now('UTC')
    updated_diff = now_dt.diff(last_updated_dt).in_minutes()
    logger.info(f"Last Updated: {last_updated_dt}")
    logger.info(f"Current Time: {now_dt}")
    logger.info(f"Minutes Since Last Update: {updated_diff}")

    # Exit Script if weather is too old...
    if updated_diff > 120:
        logger.warning(f"Weather was last updated more than 2 hours ago! Sending failure notification...")
        send_discord_notification(f"Failed to pull recent weather data...")
        exit()

    # Transform to Pandas DF 
    forcast_df = pd.DataFrame(forcast_response.json()['properties']['periods'])[['startTime', 'endTime', 'temperature']].head(14)
    logger.debug(f"Forecast Head: \n {forcast_df.to_markdown()}")

    # Get min / max temperature
    min_temp = forcast_df['temperature'].min()
    max_temp = forcast_df['temperature'].max()
    logger.info(f"Min Temperature: {min_temp} - Max Temperature: {max_temp}")

    # Determine if notification is required:
    if min_temp < 35:
        logger.info(f"Temperature Close to Freezing. Drip faucets!")
        send_discord_notification(f"Cold temperatures tonight. Drip Faucets!\n Min: {min_temp} F \n Max: {max_temp} F")

    else:
        logger.info(f"Temperature Range Okay... Will Not Send Notification.")


# Start Script:
if __name__ == "__main__":
    logger.info(f"Weather Script Starting!")
    weather_script()
    logger.info(f"Weather Script Finished!")