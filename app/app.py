import geopandas as gpd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import (GeoJSONDataSource, HoverTool, Div, 
                          Select, RadioGroup, Paragraph, 
                          MultiChoice, CustomJS, ColumnDataSource, DataTable,
                         TableColumn, Dropdown, NumeralTickFormatter, RadioGroup)
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
etablissement = gpd.GeoDataFrame(coordght, crs=CRS, geometry=geometry)
etablissement['x'] = etablissement['geometry'].x
etablissement['y'] = etablissement['geometry'].y
etablissement = etablissement.drop(['geometry'], axis=1)
flux = pd.read_csv('data/flux.csv', index_col=0)

etab_interet_source = ColumnDataSource(data=pd.DataFrame([], columns=etablissement.columns))
etab_provenance_source = ColumnDataSource(data=pd.DataFrame([], columns=etablissement.columns))
etab_sortie_source = ColumnDataSource(data=pd.DataFrame([], columns=etablissement.columns))

p = figure(
    title='Bourgogne-Franche-Comté',
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

c1 = p.circle(
    'x',
    'y',
    source=etab_interet_source,
    color='red', 
    size=10,
    hover_color='green',
    legend_label='Etablissement d\'intérêt',
)

c2 = p.circle(
    'x',
    'y',
    source=etab_provenance_source, 
    color='yellow',
    size=6,
    hover_color='green',
    legend_label='Etablissement de provenance',
)

c3 = p.circle(
    'x',
    'y',
    source = etab_sortie_source,
    color='orange',
    size=6,
    hover_color='green',
    legend_label = 'Etablissement de sortie'
)

t1 = p.text(
    'x',
    'y',
    #color='red',
    text_font_size={'value':'8px'},
    text='etablissement',
    source=etab_interet_source,
)

#define hoover
TOOLTIPS = [
    ('etablissement', '@etablissement'),
    ('lieu', '@lieu'),
    ('ght', '@nom_ght'),
    #('coordonées', '($x, $y)'),
]
ht = HoverTool(
    tooltips= TOOLTIPS,
    renderers = [c1, c2, c3]
)
p.tools.append(ht)

#define ght filter
ght_names = coordght.nom_ght.drop_duplicates().sort_values().tolist()
ght_names.append('--')
ght_names.append('ALL')
select_ght = Select(
    title="GHT :", 
    value=ght_names[-1], 
    options=ght_names,
    width=150,
)

#define multi-choice etablissement widget
etab_names = coordght.etablissement.drop_duplicates().tolist()
mc = MultiChoice(
    title='Etablissement :',
    value=[''], 
    options=etab_names,
    width=300,
)

#define specialite filter
spe_names = flux.specialite.drop_duplicates().sort_values().fillna('Inconnu').tolist()
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
    TableColumn(field='perc_transfert', title='Pourc. transfert') #, formatter=NumeralTickFormatter(format='0 %')),
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
width=300, height=100)

#define vbar
vbar_source = ColumnDataSource(data=dict(specialite=[], effectif_transfert=[], provenance=[]))
TOOLTIPS = [
    #('etablissement', '@etablissement'),
    ('details', '@details')
]

p2 = figure(
    x_range=[], 
    title='Spécialité', 
    width=500,
    toolbar_location=None,
    tooltips = TOOLTIPS,
    height=300,
    y_axis_label='Effectif transfert',
)
p2.vbar(
    x='specialite',
    top='effectif_transfert',
    width=0.4,
    source = vbar_source,
    fill_color= 'salmon',
    line_alpha=.5,
    #width=375,
)
p2.xaxis.major_label_orientation = 1.2

#define radiogroup
LABELS = ['Transferts entrants', 'Transferts sortants']

radio_group = RadioGroup(labels=LABELS, active=0)


#define callbaks
def update_ght(attr, old, new):
    #reinitialize etablissement filter
    mc.value = ['']
    select_spe.value = '--'
    if select_ght.value=='ALL':
        filtre = etablissement.copy()
    else:
        filtre = etablissement.loc[etablissement.nom_ght==select_ght.value, :]
    etab_interet_source.data = filtre

def update_etablissement(attr, old, new):
    #reinitialize ght filter
    select_ght.value = '--'
    select_spe.value = '--'
    #update red point : etablissement d'intérêt
    etab_interet_source.data = etablissement\
    .loc[etablissement.etablissement.isin(mc.value), :]
    #display Etablissements de provenance or Etablissements de sortie on the map
    if radio_group.active == 0:
        #update table
        tmp = flux.loc[flux.etablissement.isin(mc.value), :]
        agg_df = tmp.groupby(['provenance'])['effectif_transfert'].sum().sort_values(ascending=False).reset_index()
        agg_df['perc_transfert'] = round((agg_df['effectif_transfert'] / agg_df['effectif_transfert'].sum())*100,1)
        table_source.data = agg_df.copy()
        #add the satellites on the graph
        satellite_names = tmp['provenance'].drop_duplicates()
        etab_provenance_source.data = etablissement.loc[etablissement.etablissement.isin(satellite_names),:]
        #reinit
        etab_sortie_source.data = etablissement.loc[etablissement.etablissement=='--', ]
        s = 'entrants'
    else:
        #update table
        tmp = flux.loc[flux.provenance.isin(mc.value), :]
        agg_df = tmp.groupby(['etablissement'])['effectif_transfert'].sum().sort_values(ascending=False).reset_index()
        agg_df['perc_transfert'] = round((agg_df['effectif_transfert'] / agg_df['effectif_transfert'].sum())*100,1)
        agg_df = agg_df.rename(columns = {'etablissement':'provenance'})
        table_source.data = agg_df.copy()
        #add the satellites on the graph
        satellite_names = tmp['etablissement'].drop_duplicates()
        etab_sortie_source.data = etablissement.loc[etablissement.etablissement.isin(satellite_names),:]
        #reinit
        etab_provenance_source.data = etablissement.loc[etablissement.etablissement=='--', ]
        s = 'sortants'
    p2.title = 'Spécialité - flux ' + s

    #update vbar
    if radio_group.active == 0:
        agg_df = tmp.groupby(['specialite'], dropna=False).agg(
            effectif_transfert = ('effectif_transfert', 'sum'),
            details = ('provenance', lambda s: '/ '.join(s))
        ).reset_index().sort_values(by='effectif_transfert', ascending=False)
    else:
        agg_df = tmp.groupby(['specialite'], dropna=False).agg(
            effectif_transfert = ('effectif_transfert', 'sum'),
            details = ('etablissement', lambda s: '/ '.join(s))
        ).reset_index().sort_values(by='effectif_transfert', ascending=False)        
    agg_df = agg_df.fillna('?')
    vbar_source.data = agg_df.copy()
    p2.x_range.factors = agg_df['specialite'].tolist()

    


def update_spe(attr, old, new):
    #reinitialize other filters
    mc.value = ['']
    select_ght.value = '--'
    #filter the map by specialite
    names = flux.loc[flux.specialite==select_spe.value,'etablissement'].drop_duplicates()
    filtre = pd.merge(etablissement, names, how='inner')
    etab_interet_source.data = filtre

select_ght.on_change('value', update_ght)
select_spe.on_change('value', update_spe)
mc.on_change('value', update_etablissement)
radio_group.on_change('active', update_etablissement)

#define layout
widgets = column(row(select_ght, mc), row(select_spe, paragraph), radio_group, p2, table)
layout = row(p, widgets)
curdoc().add_root(layout)
curdoc().title = 'Cartographie SSR'