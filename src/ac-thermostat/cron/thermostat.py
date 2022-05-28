import json
import urllib.request
import asyncio

from kasa import SmartPlug

from utils import log


# permissible deviation in degrees Celcius that the temperature may go above
# or below the target thermostat temperature before the AC turns on/off
ALLOWED_DEVIATION_DEGREES = 0.5
ac = SmartPlug("192.168.0.36")

def request(endpoint):
    response = urllib.request.urlopen(f"http://localhost:3000/api/v1/{endpoint}")
    text = response.read()
    return json.loads(text.decode("utf-8"))

def get_thermostat():
    return request("thermostat")

def get_temp():
    return request("temp")


async def main():
    await ac.update()
    thermostat = get_thermostat()
    thermostat_temp = thermostat["temp"]
    current_temp = get_temp()

    # if the thermostat is off, turn off the AC and stop processing rules
    if thermostat["on"] is False:
        if ac.is_on:
            log("Thermostat is off but AC is on, turning AC OFF.")
            await ac.turn_off()
        return

    if ac.is_on and current_temp < thermostat_temp - ALLOWED_DEVIATION_DEGREES:
        log(f"Thermostat: {thermostat_temp}, Current temp: {current_temp}. Turning AC OFF.")
        await ac.turn_off()
    elif ac.is_off and current_temp > thermostat_temp + ALLOWED_DEVIATION_DEGREES:
        log(f"Thermostat: {thermostat_temp}, Current temp: {current_temp}. Turning AC ON.")
        await ac.turn_on()


if __name__ == "__main__":
    asyncio.run(main())