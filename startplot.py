from datetime import datetime
from pytz import timezone, utc
from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions
from geopy import Nominatim
from timezonefinder import TimezoneFinder


tf = TimezoneFinder()

location = '21.14445477520903, -86.8222992907584'
when = '2023-04-29 04:42'

# get latitude and longitude of our location
locator = Nominatim(user_agent='TellItWithStars')
location = locator.geocode(location, language="es")
lat, lon = location.latitude, location.longitude
# convert date string into datetime object
dt = datetime.strptime(when, '%Y-%m-%d %H:%M')

# define datetime and convert to utc based on our timezone
timezone_str = tf.timezone_at(lng=lon, lat=lat)
# print("Timezone" + timezone_str)
local = timezone(timezone_str)

# get UTC from local timezone and datetime
local_dt = local.localize(dt, is_dst=None)
utc_dt = local_dt.astimezone(utc)

print(f"Observing sky from {location.address} at {local_dt}")

p = MapPlot(
    projection=Projection.ZENITH,
    lat=lat,
    lon=-lon,
    dt=local_dt,
    style=PlotStyle().extend(
        extensions.GRAYSCALE,
    ),
    resolution=2600,
)
p.constellations(labels=None)
p.moon(label="Luna")
p.stars(mag=4.6, labels=None)


p.export("export.png", transparent=True)
p.export("export.svg", transparent=True, format='svg')
