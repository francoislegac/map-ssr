import geopandas as gpd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import (GeoJSONDataSource, HoverTool, Div, 
                          Select, RadioGroup, Paragraph, 
                          MultiChoice, CustomJS, ColumnDataSource, DataTable,
                         TableColumn)
from pprint import pprint
from shapely.geometry import Point
import pandas as pd
from bokeh.layouts import row, column
import numpy as np

departement = gpd.read_file('data/departement_files/bourgogne_fc.shp')
departement_source = GeoJSONDataSource(geojson=departement.to_json())
CRS = departement.crs
coordght = pd.read_csv('data/coordght.csv', index_col=0)
geometry = [Point(xy) for xy in zip(coordght.longitude, coordght.latitude)]
etablissement = gpd.GeoDataFrame(coordght.drop(['longitude', 'latitude'], axis=1), crs=CRS, geometry=geometry)
point_source = GeoJSONDataSource(geojson=etablissement.to_json())
test = GeoJSONDataSource(geojson=
    gpd.GeoDataFrame([], columns=columns, geometry=[])
)

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
    source=point_source,
    color='red', 
    size=6,
    hover_color='yellow'
)

text = p.text(
    'x',
    'y',
    #color='red',
    text_font_size={'value':'5px'},
    text='etablissement',
    source=point_source,
)

#define hoover
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
p.tools.append(ht)

#define ght filter
ght_names = coordght.nom_ght.drop_duplicates().sort_values().tolist()
ght_names.append('--')
ght_names.append('ALL')
select = Select(
    title="GHT:", 
    value=ght_names[-1], 
    options=ght_names,
    width=375,
)

#define multi-choice etablissement widget
etab_names = coordght.etablissement.drop_duplicates().tolist()
mc = MultiChoice(
    value=[''], 
    options=etab_names,
    width=375,
)

#define table widget
flux = pd.read_csv('data/flux.csv', index_col=0)
table_source = ColumnDataSource(flux)
columns = [
    TableColumn(field='etablissement', title='etablissement'),
    TableColumn(field='specialite', title='specialite'),
    TableColumn(field='provenance', title='provenance'),
    TableColumn(field='effectif_transfert', title='effectif_transfert'), #formatter=
]
table = DataTable(
    source=table_source, 
    columns=columns,
    width=375,
)

#define callbaks
def update_ght(attr, old, new):
    #reinitialize etablissement filter
    mc.value = ['']
    #update_etablissement()
    if select.value=='ALL':
        filtre = etablissement
    elif select.value=='--':
        #filtre = gpd.GeoDataFrame([np.nan], columns=etablissement.columns, geometry=etablissement.geometry[0])
        point_source = 
    else:
        filtre = etablissement.loc[etablissement.nom_ght==select.value, :]
    point_source.geojson = filtre.to_json()

def update_etablissement(attr, old, new):
    if mc.value == ['']:
        pass 
    #if type(mc.value) != list: list(mc.value) #not sure is necessary
    else:
        point_source.geojson = etablissement\
        .loc[etablissement.etablissement.isin(mc.value), :].to_json()
        table_source.data = flux.loc[flux.etablissement.isin(mc.value), :]
    #reinitialize ght filter
    #select.value = '--'



select.on_change('value', update_ght)
mc.on_change('value', update_etablissement)

#define layout
widgets = column(select, mc, table)
layout = row(p, widgets)

#show(layout)
curdoc().add_root(layout)
