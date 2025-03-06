import logging
from weather_api.api_wrapper import Point, GridPoint
from retry import retry

# Set Logger:
logger = logging.getLogger('weather')
logger.setLevel(logging.INFO)

# create console & stream handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
fh = logging.FileHandler(filename='weather.log')
fh.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(levelname)-8s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(fh)


@retry(exceptions=ValueError, tries=3, delay=5)
def send_discord_notification(msg: str):
    from discordwebhook import Discord
    
    # Retry to send notification on failure
    # Send Notification (regardless of temperature)
    discord =  discord = Discord(url="https://discord.com/api/webhooks/1216423056499802162/o-OE5fN2AK7OAmB0CQBlfOpEYDPMvJbGuR5ngsKEyEJw26knRihster2cmMCS5-eapOJ")
    response = discord.post(content=f"{msg}")
    response.raise_for_status()
    logger.info(f"Discord Post Result: {response.status_code}")

    return response


def check_freezing_temps(**kwargs):

    # Define Point
    point = Point.create_from_api(lat=36.35, lon=-94.28)
    gridpoint = GridPoint.create_from_point(point=point)
    
    # Get twelve hour forecast
    twelve_hr_forecast = gridpoint.get_hourly_forecast_periods_df().head(12)

    # # Validate Data in Recently Updated:
    # minutes_since_last_update = twelve_hr_forecast.last_updated_from_current_time()
    # logger.info(f"Minutes since last update {minutes_since_last_update}")
    
    # # Exit Script if weather is too old:
    # if minutes_since_last_update > 120:
    #     logger.warning(f"Weather was last updated more than 2 hours ago! Sending failure notification...")
    #     send_discord_notification(f"Failed to pull recent weather data...")
    #     exit()

    # Get min / max temperature
    min_temp = twelve_hr_forecast['temperature'].min()
    max_temp = twelve_hr_forecast['temperature'].max()
    logger.info(f"{min_temp = } - {max_temp = }")

    # Determine if notification is required:
    if min_temp < 35:
        logger.info(f"Temperature Close to Freezing. Drip faucets!")
        send_discord_notification(f"Cold temperatures tonight. Drip Faucets!\n {min_temp = } F \n {max_temp = } F")

    else:
        logger.info(f"Temperature Range Okay... Will Not Send Notification.")


# Start Script:
if __name__ == "__main__":
    print(f"Weather Script Starting!")
    check_freezing_temps()
    print(f"Weather Script Finished!")