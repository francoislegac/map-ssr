from bokeh.plotting import figure, show
from bokeh.io import curdoc
import geopandas as gpd
from bokeh.models import GeoJSONDataSource, ColumnDataSource
from shapely.geometry import Point

# prepare some data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

geometry = [Point(xy) for xy in zip([3,3],[4,4])]
#etablissement = gpd.GeoDataFrame(coordght.drop(['longitude', 'latitude'], axis=1), crs=CRS, geometry=geometry)

df = gpd.GeoDataFrame(
    dict(A=[4,5], B=[4,4], x=['s', 'v'], y=['u', 't']),
)
source = ColumnDataSource(data=df)
print(source.data)

# create a new plot with a title and axis labels
p = figure(title="Simple line example", x_axis_label="x", y_axis_label="y")

# add a line renderer with legend and line thickness
circle = p.circle('A', 'B', source= source, legend_label="Temp.", line_width=2)


# show the results
curdoc().add_root(p)