"""Dimming schedule for TP-Link Kasa HS220 model dimmer switch used in my
bathroom in my 2021-2022 NYC apartment. Needed a script for this because none
of the apps/services I tried (Kasa, Alexa, Yonomi) allow setting dimmer
brightness without also turning the switch on at the same time.

Intended to be used on a cron job that runs every minute like:
* * * * * /Users/hliddiard/Developer/smarthome/bin/python3 /Users/hliddiard/Developer/smarthome/repo/tplink/bathroom_dimmer.py >> /Users/hliddiard/Developer/smarthome/repo/cron.log 2>&1
"""

import asyncio
from datetime import datetime, date

from astral import LocationInfo
from astral.sun import sun
from kasa import SmartDimmer


HOST = "192.168.0.19"
HALF_HOUR_IN_MS = 60*30*1000
TIME_FORMAT = "%H:%M"


def get_schedule():
    """Returns today's schedule based on current sunrise and sunset times
    """
    location = LocationInfo(
        "New York City",
        "United States",
        "America/New_York",
        40.7, # lat
        -73.9 # lon
    )

    s = sun(location.observer, date=date.today(), tzinfo=location.timezone)
    sunrise = s["sunrise"].strftime(TIME_FORMAT)
    sunset = s["sunset"].strftime(TIME_FORMAT)

    # map from 24-hour time to brightness level (0-100)
    return {
        "02:00": 1,
        sunrise: 100,
        sunset: 67,
        "22:30": 33,
        "23:30": 10
    }


async def main():
    current_time = datetime.now().strftime(TIME_FORMAT)
    schedule = get_schedule()
    print(f"\nCurrent time: {current_time}")

    if current_time in schedule:
        brightness = schedule[current_time]
        print(f"Time in schedule; setting brightness {brightness}")

        # https://python-kasa.readthedocs.io/en/latest/smartdimmer.html
        dimmer = SmartDimmer(HOST)
        # await update to get access to current props before modifying
        await dimmer.update()

        await dimmer.set_brightness(brightness, transition=HALF_HOUR_IN_MS)
        print(f"Started transition to brightness {brightness} at {current_time}")
    else:
        print("Time not in schedule; exiting")


if __name__ == "__main__":
    asyncio.run(main())
