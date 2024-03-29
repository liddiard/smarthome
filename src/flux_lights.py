"""Dimming schedule for Philips WiZ RGBW light bulbs in my 2021-2022 NYC
apartment. Needed a script for this because none WiZ doesn't allow changing
light properties based on "sun events" like sunrise and sunset. It also
doesn't support changing light properties without turning on the light.
Neither does the underlying protocol, it seems, but there's a workaround. See
"Implementation Notes" below for more details.

Intended to be used on a cron job that runs every minute like:
BASE_PATH=/Users/hliddiard/Developer/smarthome
* * * * * "${BASE_PATH}/bin/python3" "${BASE_PATH}/repo/src/flux_lights.py" >> "${BASE_PATH}/repo/cron.log" 2>&1

--------------------
Implementation Notes

In theory we should be able to use:
    await light.send({"method":"setState","params":{"temp":3200}})
to set color temp without turning on the light per comment:
https://github.com/sbidy/pywizlight/issues/40#issuecomment-765810278
However, in testing if the "state" boolean is omitted from params, the light
always turns on. If "state" is set to False AND the light is off AND the
requested color temp is different from the current color temp, this line
raises error:
    pywizlight.exceptions.WizLightConnectionError: 
    Error recieved: {'code': -32603, 'message': 'Internal error'}
So as a workaround, we're allowing an off bulb to turn on to change the
color temp, then immediately turn it off. There's sometimes a brief flash
when this happens, but it's mitigated by setting the bulb's "On fade-in" to
0.5s and "Off fade-out" to 0s.
"""

import asyncio
from datetime import datetime

from pywizlight import wizlight, PilotBuilder, discovery

from utils import log, format_time, get_sun_events


HOSTS = {
    "KITCHEN_CEILING": "192.168.0.15",
    "ENTRYWAY": "192.168.0.16"
}

# https://github.com/sbidy/pywizlight/blob/master/pywizlight/scenes.py
SCENES = {
    "Cozy": 6,
    "Night light": 14
}


def get_schedule(bulb_name):
    """Returns today's schedule based on current sunrise and sunset times
    """
    sun_events = get_sun_events()
    sunrise = sun_events["sunrise"]
    sunset = sun_events["sunset"]

    # map from 24-hour time to color temp (2200-6200 Kelvin) and other props
    # allows adding/overriding schedule entries for specific bulbs
    schedule = {
        "BASE": {
            sunset:  { "colortemp": 2700 },
            "23:00": { "scene": SCENES["Cozy"] },
            "02:00": { "brightness": 1 }
        },
        "KITCHEN_CEILING": {
            sunrise: { "colortemp": 3000, "brightness": 255 }
        },
        "ENTRYWAY": {
            sunrise: { "colortemp": 3000, "brightness": 192 }
        }
    }

    return { **schedule["BASE"], **schedule.get(bulb_name, {}) }


async def main():
    current_time = format_time(datetime.now())

    for bulb_name, bulb_ip in HOSTS.items():
        schedule = get_schedule(bulb_name)

        if current_time not in schedule:
            continue

        adjustments = schedule[current_time]
        log(f"Time {current_time} in schedule; setting adjustments: {adjustments}")

        bulb = wizlight(bulb_ip)
        state = await bulb.updateState()
        is_on = state.get_state()
        await bulb.turn_on(PilotBuilder(**adjustments))
        if not is_on:
            await bulb.turn_off()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
