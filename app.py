import geopandas as gpd
import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import (GeoJSONDataSource, HoverTool,
                          Select, RadioGroup, Paragraph, 
                          MultiChoice, ColumnDataSource, DataTable,
                         TableColumn, Dropdown)
from shapely.geometry import Point
from bokeh.layouts import row, column

#load background patches (departement patches)
departement = gpd.read_file('data/departement_files/bourgogne_fc.shp')
departement_source = GeoJSONDataSource(geojson=departement.to_json())
#load the file containing the etablissements with their corresponding coordinates
data = pd.read_csv('data/data.csv', index_col=0)
geometry = [Point(xy) for xy in zip(data.longitude, data.latitude)]
data = gpd.GeoDataFrame(data, crs=departement.crs, geometry=geometry)
data['x'] = data['geometry'].x
data['y'] = data['geometry'].y
data = data.drop(['geometry'], axis=1)
#load the flux
flux = pd.read_csv('data/flux.csv', index_col=0)

#initialize the sources for the points on the map
etab_interet_source = ColumnDataSource(data=pd.DataFrame([], columns=data.columns))
etab_provenance_source = ColumnDataSource(data=pd.DataFrame([], columns=data.columns))
etab_sortie_source = ColumnDataSource(data=pd.DataFrame([], columns=data.columns))

_map = figure(
    title='Bourgogne-Franche-Comté',
    x_axis_location=None, 
    y_axis_location=None,
    sizing_mode = 'scale_both',
    width=1200,
    height=750,
)

patches = _map.patches('xs', 
          'ys', 
          source=departement_source,
          fill_color='blue',
          fill_alpha=0.5, 
          line_color="black", 
          line_width=0.5
)

c1 = _map.circle(
    'x',
    'y',
    source=etab_interet_source,
    color='red', 
    size=10,
    hover_color='green',
    legend_label='Etablissement d\'intérêt',
)

c2 = _map.circle(
    'x',
    'y',
    source=etab_provenance_source, 
    color='yellow',
    size=6,
    hover_color='green',
    legend_label='Etablissement de provenance',
)

c3 = _map.circle(
    'x',
    'y',
    source = etab_sortie_source,
    color='orange',
    size=6,
    hover_color='green',
    legend_label = 'Etablissement de sortie'
)

t1 = _map.text(
    'x',
    'y',
    #color='red',
    text_font_size={'value':'8px'},
    text='nom_etab',
    source=etab_interet_source,
)

#define hoover (i.e the small window that appears on mouse-hoover)
TOOLTIPS = [
    ('etablissement', '@nom_etab'),
    ('lieu', '@lieu'),
    ('ght', '@nom_ght'),
    #('coordonées', '($x, $y)'),
]
ht = HoverTool(
    tooltips= TOOLTIPS,
    renderers = [c1, c2, c3]
)
_map.tools.append(ht)

#define ght filter
ght_names = data.nom_ght.drop_duplicates().sort_values().tolist()
ght_names.append('--')
ght_names.append('ALL')
select_ght = Select(
    title="GHT :", 
    value=ght_names[-1], 
    options=ght_names,
    width=150,
)

#define multi-choice etablissement widget
etab_names = data.nom_etab.drop_duplicates().tolist()
mc = MultiChoice(
    title='Etablissement :',
    value=[''], 
    options=etab_names,
    width=300,
)

#define specialite filter
spe_names = flux.specialite.drop_duplicates().sort_values().fillna('Inconnue').tolist()
spe_names.append('--')
select_spe = Select(
    title="Specialité :", 
    value=spe_names[-1], 
    options=spe_names,
    width=150,
)

#define table widget
table_source = ColumnDataSource(data=dict(provance=[], effectif_transfert=[], perc_transfert=[]))
columns = [
    TableColumn(field='provenance', title='Provenance / sortie'),
    TableColumn(field='effectif_transfert', title='Effectif transfert'),
    TableColumn(field='perc_transfert', title='Pourc. transfert')
]
table = DataTable(
    source=table_source, 
    columns=columns,
    width=500,
)

#define paragraph
paragraph = Paragraph(text="""
    Source: https://www.scansante.fr/applications/flux-entre-etablissements-orfee
    """,
    width=300, height=100
)

#define vbar
vbar_source = ColumnDataSource(data=dict(specialite=[], effectif_transfert=[], provenance=[]))
TOOLTIPS = [
    ('details', '@details')
]

vbar_figure = figure(
    x_range=[], 
    title='Spécialité', 
    width=500,
    toolbar_location=None,
    tooltips = TOOLTIPS,
    height=300,
    y_axis_label='Effectif transfert',
)

vbar_figure.vbar(
    x='specialite',
    top='effectif_transfert',
    width=0.4,
    source = vbar_source,
    fill_color= 'salmon',
    line_alpha=.5,
)
#slightly rotate the "specialite" labels
vbar_figure.xaxis.major_label_orientation = 1.2

#define radiogroup
LABELS = ['Transferts entrants', 'Transferts sortants']
radio_group = RadioGroup(labels=LABELS, active=0)

#DEFINE CALLBACKS
def update_ght(attr, old, new):
    '''
    callback to filter by "Groupe Hospitalier (GHT)"
    Note that callback functions must have signature func(attr, old, new)
    '''
    #reinitialize other filters 
    mc.value = ['']
    select_spe.value = '--'
    #filter the original df "etablissement" to get the right data
    if select_ght.value=='ALL':
        filtre = data
    else:
        filtre = data.loc[data.nom_ght==select_ght.value, :]
    etab_interet_source.data = filtre

def update_etablissement(attr, old, new):
    '''
    callback to filter by "établissement"
    Note that callback functions must have signature func(attr, old, new)
    '''
    #reinitialize other filters
    select_ght.value = '--'
    select_spe.value = '--'
    #update the red point "Etablissement d'intérêt"
    etab_interet_source.data = data.loc[data.nom_etab.isin(mc.value), :]

    #we inverse the provenance according to the value selected (Flux entrants / Flux sortants)
    #Flux entrants : nom_etab | provenance | effectif_transfert
    #Flux sortants : provenance | nom_etab | effectif_transfert
    tmp = flux.copy()    
    if radio_group.active==1: tmp = tmp.rename(columns = {'nom_etab':'provenance', 'provenance':'nom_etab'})    
    tmp = tmp.loc[tmp.nom_etab.isin(mc.value), :]
    
    #let's update the table widget
    agg_df = tmp.groupby(['provenance'])['effectif_transfert'].sum().sort_values(ascending=False).reset_index()
    agg_df['perc_transfert'] = round((agg_df['effectif_transfert'] / agg_df['effectif_transfert'].sum())*100,1)
    table_source.data = agg_df
    
    #add the satellites on the map (satellites are either "Etablissement de provenance" or "Etablissement de sortie")
    satellite_names = tmp['provenance'].drop_duplicates()
    if radio_group.active==0:
        etab_provenance_source.data = data.loc[data.nom_etab.isin(satellite_names),:]
        etab_sortie_source.data = data.loc[data.nom_etab=='--', ]
    else:
        etab_sortie_source.data = data.loc[data.nom_etab.isin(satellite_names),:]
        etab_provenance_source.data = data.loc[data.nom_etab=='--', ]
    
    #update vbar
    tmp['specialite'] = tmp['specialite'].fillna('Autre')
    agg_df = tmp.groupby(['specialite'], dropna=False).agg(
        effectif_transfert = ('effectif_transfert', 'sum'),
        details = ('provenance', lambda s: ' | '.join(s.str.capitalize()))
    ).reset_index().sort_values(by='effectif_transfert', ascending=False)
    vbar_source.data = agg_df
    vbar_figure.x_range.factors = agg_df['specialite'].tolist()

def update_spe(attr, old, new):
    '''
    callback to filter by "Spécialité"
    Note that callback functions must have signature func(attr, old, new)
    '''
    #reinitialize other filters
    mc.value = ['']
    select_ght.value = '--'
    #filter the map by specialite
    names = flux.loc[flux.specialite==select_spe.value,'nom_etab'].drop_duplicates()
    filtre = pd.merge(data, names, how='inner')
    etab_interet_source.data = filtre

select_ght.on_change('value', update_ght)
select_spe.on_change('value', update_spe)
mc.on_change('value', update_etablissement)
radio_group.on_change('active', update_etablissement)

#define layout
widgets = column(row(select_ght, mc), row(select_spe, paragraph), radio_group, vbar_figure, table)
layout = row(_map, widgets)
curdoc().title = 'Cartographie SSR'
curdoc().add_root(layout)
