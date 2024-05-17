from datetime import datetime
from pytz import timezone
from starplot import MapPlot, Projection
from starplot.styles import PlotStyle, extensions

tz = timezone("America/Cancun")
dt = datetime(2024, 3, 29, 4, 42, tzinfo=tz)  # July 13, 2023 at 10pm PT

p = MapPlot(
    projection=Projection.ZENITH,
    lat=21.144456544126005,
    lon=-86.82224903064267,
    dt=dt,
    style=PlotStyle().extend(
        extensions.BLUE_MEDIUM,
    ),
    resolution=2600,
)
p.constellations()
p.stars(mag=4.6)

p.export("star_chart_basic.png", transparent=True)
