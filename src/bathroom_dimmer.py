"""Dimming schedule for TP-Link Kasa HS220 model dimmer switch used in my
bathroom in my 2021-2022 NYC apartment. Needed a script for this because none
of the apps/services I tried (Kasa, Alexa, Yonomi) allow setting dimmer
brightness without also turning the switch on at the same time.

Intended to be used on a cron job that runs every minute like:
BASE_PATH=/Users/hliddiard/Developer/smarthome
* * * * * "${BASE_PATH}/bin/python3" "${BASE_PATH}/repo/src/bathroom_dimmer.py" >> "${BASE_PATH}/repo/cron.log" 2>&1
"""

import asyncio
from datetime import datetime

from kasa import SmartDimmer

from utils import log, format_time, get_sun_events


HOST = "192.168.0.19"
HALF_HOUR_IN_MS = 60*30*1000


def get_schedule():
    """Returns today's schedule based on current sunrise and sunset times
    """
    sun_events = get_sun_events()
    dawn = sun_events["dawn"]
    sunrise = sun_events["sunrise"]
    hour_before_sunset = sun_events["hour_before_sunset"]
    sunset = sun_events["sunset"]

    # map from 24-hour time to brightness level (0-100)
    return {
        "02:00": 10,
        "03:00": 1,
        dawn: 10,
        sunrise: 80,
        hour_before_sunset: 80,
        sunset: 67,
        "23:00": 33,
        "01:00": 20
    }


async def main():
    current_time = format_time(datetime.now())
    schedule = get_schedule()
    # log(f"\nCurrent time: {current_time}")

    if current_time in schedule:
        brightness = schedule[current_time]
        log(f"Time {current_time} in schedule; setting brightness {brightness}")

        # https://python-kasa.readthedocs.io/en/latest/smartdimmer.html
        dimmer = SmartDimmer(HOST)
        # await update to get access to current props before modifying
        await dimmer.update()
        # log(dimmer.state_information)

        await dimmer.set_brightness(brightness) # transition=HALF_HOUR_IN_MS
        log(f"Started transition to brightness {brightness} at {current_time}")

        # if dimmer.state_information['On since'] is None:
        #     log("Switch was off; forcing it to stay off")
        #     await dimmer.turn_off()
    else:
        # log("Time not in schedule; exiting")
        pass


if __name__ == "__main__":
    asyncio.run(main())
