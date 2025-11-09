import colorsys
import datetime
import secrets

from flask import Flask, abort, g, request
from skyfield import almanac
from skyfield.api import load, wgs84
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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

    Returns a tuple of (next_dst_change, dst_offset_change) where:
    - next_dst_change: Unix timestamp (int) of the next transition, or None
    - dst_offset_change: Offset change in seconds (int), or None
    """
    try:
        # Search up to 2 years in the future for the next transition
        search_end = current_time + datetime.timedelta(days=730)
        search_time = current_time

        # Get current UTC offset
        current_offset = current_time.utcoffset().total_seconds()

        # Iterate through time to find the next transition
        # We'll check every 6 hours to find when the UTC offset changes
        while search_time < search_end:
            search_time += datetime.timedelta(hours=6)
            next_offset = search_time.astimezone(tzinfo).utcoffset().total_seconds()

            if next_offset != current_offset:
                # Found a transition, now narrow it down
                # Binary search to find the exact transition time
                low = current_time
                high = search_time

                while (high - low).total_seconds() > 60:  # Within 1 minute
                    mid = low + (high - low) / 2
                    mid_offset = mid.astimezone(tzinfo).utcoffset().total_seconds()

                    if mid_offset == current_offset:
                        low = mid
                    else:
                        high = mid

                # The transition happens at 'high'
                transition_time = high
                offset_change = int(next_offset - current_offset)
                transition_timestamp = int(transition_time.timestamp())

                return transition_timestamp, offset_change

        # No transition found in the next 2 years
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
    if "X-Location" not in request.headers:
        abort(400)
    latitude, longitude = request.headers.get("X-Location").split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    g.location = wgs84.latlon(latitude, longitude)


@app.get("/time")
def get_time():
    now = datetime.datetime.now(g.tzinfo)
    next_dst_change, dst_offset_change = get_next_dst_transition(g.tzinfo, now)
    return list(now.timetuple()) + [now.microsecond, next_dst_change, dst_offset_change]


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
