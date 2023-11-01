from datetime import datetime, date, timedelta

from astral import LocationInfo
from astral.sun import sun


def log(msg):
    """Logs provided messsage with prepended timestamp"""
    timestamp = datetime.now().isoformat(" ", "seconds")
    print(f"[{timestamp}] {msg}")


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
        40.8, # lat
        -74.0 # lon
    )
    schedule = sun(location.observer, date=date.today(), tzinfo=location.timezone)
    events = {}

    for key, value in schedule.items():
        events[key] = format_time(value)
    events["hour_before_sunset"] = schedule["sunset"] + timedelta(hours=1)
    
    return events
