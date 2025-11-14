import colorsys
import datetime
import os
import secrets
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Flask, abort, g, request
from skyfield import almanac
from skyfield.api import load, wgs84

app = Flask(__name__)

EPH = load("de421.bsp")

SUN_COLOR = 0x201000
MOON_COLOR = 0x001020

MOON_RADIUS_DEGREES = 0.25

MOTD_OPTIONS = [
    "Hello",
    ":)",
    ":o",
    ":(",
    ":|",
    ":D",
    ":*",
    ";)",
    "}:)",
    ":P",
    "XD",
    ">:3",
    "<3",
    "@}->--",
    "o7",
    "\\o/",
    "o_O",
    "O_o",
    "x_X",
    "X_x",
    ">_<",
    "BOO!",
    "qq",
    "._.",
    "^_^",
    "~_~",
]


def get_rand_color():
    rgb = colorsys.hsv_to_rgb(secrets.randbelow(256) / 256, 1, 0x2F / 256)
    red = int(rgb[0] * 256)
    green = int(rgb[1] * 256)
    blue = int(rgb[2] * 256)
    red = (red >> 4) << 4
    green = (green >> 4) << 4
    blue = (blue >> 4) << 4
    color = (red << 16) + (green << 8) + blue
    return color


def get_next_sun_event(event_index=0):
    now = datetime.datetime.now(g.tzinfo)
    now_plus = now + datetime.timedelta(days=1.5)

    ts = load.timescale()
    t_now = ts.from_datetime(now)
    t_now_plus = ts.from_datetime(now_plus)

    get_sun_up = almanac.sunrise_sunset(EPH, g.location)
    times, events = almanac.find_discrete(t_now, t_now_plus, get_sun_up)

    sun_event_str = "SR" if events[event_index] else "SS"
    sun_event_time = times[event_index].astimezone(g.tzinfo) + datetime.timedelta(
        seconds=30
    )
    return "%s %02d:%02d" % (sun_event_str, sun_event_time.hour, sun_event_time.minute)


def get_next_moon_event(event_index=0):
    now = datetime.datetime.now(g.tzinfo)
    now_plus = now + datetime.timedelta(days=1.5)

    ts = load.timescale()
    t_now = ts.from_datetime(now)
    t_now_plus = ts.from_datetime(now_plus)

    get_moon_up = almanac.risings_and_settings(
        EPH, EPH["moon"], g.location, radius_degrees=MOON_RADIUS_DEGREES
    )
    times, events = almanac.find_discrete(t_now, t_now_plus, get_moon_up)

    moon_event_str = "MR" if events[event_index] else "MS"
    moon_event_time = times[event_index].astimezone(g.tzinfo) + datetime.timedelta(
        seconds=30
    )
    return "%s %02d:%02d" % (
        moon_event_str,
        moon_event_time.hour,
        moon_event_time.minute,
    )


def get_sun_state():
    now = datetime.datetime.now(g.tzinfo)
    ts = load.timescale()
    t_now = ts.from_datetime(now)
    sun_is_up = almanac.sunrise_sunset(EPH, g.location)(t_now)
    return "Daytime" if sun_is_up else "Nighttime"


def get_moon_state():
    now = datetime.datetime.now(g.tzinfo)
    ts = load.timescale()
    t_now = ts.from_datetime(now)
    moon_is_up = almanac.risings_and_settings(
        EPH, EPH["moon"], g.location, radius_degrees=MOON_RADIUS_DEGREES
    )(t_now)
    return "Moon up" if moon_is_up else "Moon down"


def get_moon_phase():
    now = datetime.datetime.now(g.tzinfo)
    ts = load.timescale()
    t_now = ts.from_datetime(now)
    angle = int(almanac.moon_phase(EPH, t_now).degrees)
    angle_options = [0, 90, 180, 270, 360]
    closest_match = (
        min(angle_options, key=lambda angle_option: abs(angle_option - angle)) % 360
    )
    return {0: "New Moon", 90: "1st Qtr Mn", 180: "Full Moon", 270: "Lst Qtr Mn"}[
        closest_match
    ]


def get_next_dst_transition(tzinfo, current_time):
    """
    Find the next DST transition for the given timezone.

    Returns a tuple of (next_dst_change, new_utc_offset) where:
    - next_dst_change: Unix timestamp (int) of the next transition, or None
    - new_utc_offset: New UTC offset in seconds (int) after the transition, or None

    Note: Only searches 2 hours ahead since clients poll at least once per hour.
    """
    try:
        # Work in UTC timestamps to avoid timezone ambiguity issues
        current_timestamp = current_time.timestamp()
        search_end_timestamp = (
            current_timestamp + (2 * 3600) + (15 * 60)
        )  # 2h 15m buffer

        # Get current UTC offset
        current_offset = current_time.utcoffset().total_seconds()

        # Iterate through time to find the next transition
        # Check every 15 minutes (900 seconds) to find when the UTC offset changes
        search_timestamp = current_timestamp

        while search_timestamp < search_end_timestamp:
            search_timestamp += 900  # 15 minutes in seconds
            search_time = datetime.datetime.fromtimestamp(search_timestamp, tz=tzinfo)
            next_offset = search_time.utcoffset().total_seconds()

            if next_offset != current_offset:
                # Found a transition, now narrow it down
                # Binary search to find the exact transition time (in timestamps)
                low_ts = search_timestamp - 900  # 15 minutes before
                high_ts = search_timestamp

                while (high_ts - low_ts) > 1:  # Within 1 second
                    mid_ts = (low_ts + high_ts) / 2
                    mid_time = datetime.datetime.fromtimestamp(mid_ts, tz=tzinfo)
                    mid_offset = mid_time.utcoffset().total_seconds()

                    if mid_offset == current_offset:
                        low_ts = mid_ts
                    else:
                        high_ts = mid_ts

                # The transition happens at 'high_ts'
                transition_timestamp = int(high_ts)

                # Only return if transition is within 2 hours from the original current_time
                time_until_transition = transition_timestamp - current_timestamp
                if time_until_transition <= 7200:  # 2 hours in seconds
                    return transition_timestamp, int(next_offset)
                else:
                    return None, None

        # No transition found in the next 2 hours
        return None, None

    except (AttributeError, TypeError):
        # Timezone doesn't support transitions
        return None, None


@app.before_request
def load_timezone():
    timezone = request.headers.get("X-Timezone", "UTC")
    try:
        g.tzinfo = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, IsADirectoryError, ValueError):
        abort(404)


@app.before_request
def load_location():
    latitude, longitude = request.headers.get("X-Location", "40.7,-74.0").split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    g.location = wgs84.latlon(latitude, longitude)


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.get("/time")
def get_time():
    if os.getenv("OVERRIDE_CURRENT_TIME"):
        now = datetime.datetime.fromtimestamp(
            float(os.getenv("OVERRIDE_CURRENT_TIME"))
        ).astimezone(g.tzinfo)
    else:
        now = datetime.datetime.now(g.tzinfo)
    next_dst_change, new_utc_offset = get_next_dst_transition(g.tzinfo, now)
    return [
        int(now.timestamp() * 1000),
        int(now.tzinfo.utcoffset(now).total_seconds()),
        next_dst_change * 1000 if next_dst_change is not None else None,
        new_utc_offset,
    ]


@app.get("/motd")
def get_motd():
    rand_num = secrets.randbelow(8)

    match rand_num:
        case 0:
            return [secrets.choice(MOTD_OPTIONS), get_rand_color()]
        case 1:
            return [get_next_sun_event(), SUN_COLOR]
        case 2:
            return [get_next_sun_event(1), SUN_COLOR]
        case 3:
            return [get_next_moon_event(), MOON_COLOR]
        case 4:
            return [get_next_moon_event(1), MOON_COLOR]
        case 5:
            return [get_sun_state(), SUN_COLOR]
        case 6:
            return [get_moon_state(), MOON_COLOR]
        case 7:
            return [get_moon_phase(), MOON_COLOR]
