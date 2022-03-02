from datetime import date

from astral import LocationInfo
from astral.sun import sun


def format_time(time):
    """Takes datetime and returns 24-hour, zero-padded time in format HH:MM
    """
    return time.strftime("%H:%M")


def get_sun_events():
    """Returns a dict of "sun events" for today in NYC in format HH:MM
    Available values: "dawn", "sunrise", "noon", "sunset", "dusk"
    """
    location = LocationInfo(
        "New York, NY",
        "United States",
        "America/New_York",
        40.7, # lat
        -73.9 # lon
    )
    schedule = sun(location.observer, date=date.today(), tzinfo=location.timezone)
    events = {}

    for key, value in schedule.items():
        events[key] = format_time(value)
    
    return events