import geopandas as gpd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import (GeoJSONDataSource, HoverTool, Div, 
                          Select, RadioGroup, Paragraph, 
                          MultiChoice, CustomJS, ColumnDataSource, DataTable,
                         TableColumn, TextInput)
from pprint import pprint
from shapely.geometry import Point
import pandas as pd
from bokeh.layouts import row, column

departement = gpd.read_file('data/departement_files/bourgogne_fc.shp')
departement_source = GeoJSONDataSource(geojson=departement.to_json())
CRS = departement.crs
coordght = pd.read_csv('data/coordght.csv', index_col=0)
geometry = [Point(xy) for xy in zip(coordght.longitude, coordght.latitude)]
etablissement = gpd.GeoDataFrame(coordght.drop(['longitude', 'latitude'], axis=1), crs=CRS, geometry=geometry)
static_etablissement = etablissement.copy()
etablissement_source = GeoJSONDataSource(geojson=etablissement.to_json())

p = figure(
    title='New test map',
    x_axis_location=None, 
    y_axis_location=None,
    #sizing_mode='stretch_width',
    sizing_mode = 'scale_both',
    width=1200,
    height=750,
)

patches = p.patches('xs', 
          'ys', 
          source=departement_source,
          fill_color='blue',
          fill_alpha=0.5, 
          line_color="black", 
          line_width=0.5
)

circles = p.circle(
    'x',
    'y',
    source=etablissement_source,
    #color='red', 
    size=6,
    hover_color='yellow'
)

text = p.text(
    'x',
    'y',
    color='red',
    text_font_size={'value':'10px'},
    text='etablissement',
    source=etablissement_source,
)

TOOLTIPS = [
    ('etablissement', '@etablissement'),
    ('lieu', '@lieu'),
    ('ght', '@nom_ght'),
    ('coordonees', '($x, $y)'),
]

ht = HoverTool(
    tooltips= TOOLTIPS,
    renderers = [circles]
)

text = TextInput(title="title", value='my sine wave')

# Set up callbacks
def update_title(attr, old, new):
    etablissement_source.geojson = etablissement.iloc[:10,:].to_json()
    p.title.text = text.value

text.on_change('value', update_title)


p.tools.append(ht)

ght_names = coordght.nom_ght.drop_duplicates().sort_values().tolist()
ght_names.append('ALL')
select = Select(
    title="GHT:", 
    value=ght_names[-1], 
    options=ght_names,
    width=375,
)

'''
def update_ght(attrname, ):
    pass

select.js_on_change('value', update_ght)
'''




#define layout
widgets = column(text, select)#, mc, data_table)
layout = row(p, widgets)

#show(layout)
curdoc().add_root(layout)
curdoc().title = "XXXX"