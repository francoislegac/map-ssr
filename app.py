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

departement = gpd.read_file('data/departement_files/bourgogne_fc.shp')
departement_source = GeoJSONDataSource(geojson=departement.to_json())
CRS = departement.crs
coordght = pd.read_csv('data/coordght.csv', index_col=0)
geometry = [Point(xy) for xy in zip(coordght.longitude, coordght.latitude)]
etablissement = gpd.GeoDataFrame(coordght.drop(['longitude', 'latitude'], axis=1), crs=CRS, geometry=geometry)
etablissement_source = GeoJSONDataSource(geojson=etablissement.to_json())
source = GeoJSONDataSource(geojson=etablissement.copy().to_json())

p = figure(
    title='New test map',
    x_axis_location=None, 
    y_axis_location=None,
    #sizing_mode='stretch_width',
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
    source=source,
    color='red', 
    size=6,
    hover_color='yellow'
)


TOOLTIPS = [
    ('(x, y)', '($x, $y)'),
    ('etablissement', '@etablissement'),
    ('lieu', '@lieu'),
    ('ght', '@nom_ght')
]

ht = HoverTool(
    tooltips= TOOLTIPS,
    renderers = [circles]
)

p.tools.append(ht)

ght_names = coordght.nom_ght.drop_duplicates().sort_values().tolist()
ght_names.append('ALL')
select = Select(title="GHT:", value=ght_names[-1], options=ght_names)

ght_callback = CustomJS(args=dict(static_source=etablissement_source, source= source), code="""
        const static_data = static_source.data;
        var data = source.data;
        const n = static_data.nom_ght.length;
        const widget_value = cb_obj.value;
        
        //reinitilize source data
        for (const key in data){
            data[key] = [];
        }
        if(widget_value == 'ALL') {
            for (let i=0; i < n; i++){
                for (const key in static_data){
                        data[key].push(static_data[key][i])
                    }
                }
        }    
        else{
            //get the data related to the selected etablissement
            for (let i=0; i < n; i++){
                if(static_data.nom_ght[i] == widget_value){
                    for (const key in static_data){
                        data[key].push(static_data[key][i])
                    }
                }
            }          
        }
        source.change.emit();
    """)
select.js_on_change('value', ght_callback)

etab_names = coordght.etablissement.drop_duplicates().tolist()
mc = MultiChoice(value=[etab_names[0]], options=etab_names)

flux = pd.read_csv('data/flux.csv', index_col=0)
static_flux_source = ColumnDataSource(flux)
flux_source = ColumnDataSource(flux.copy())
#etablissement, specialite, provenance, effectif_transfert
columns = [
    TableColumn(field='effectif_transfert', title='Effectif') #formatter=
]
data_table = DataTable(source=flux_source, columns=columns) #width=400, height=280)

etab_callback = CustomJS(args=dict(static_source=etablissement_source, source= source, mc=mc, 
                                   static_flux_source= static_flux_source, 
                                   flux_source=flux_source, etab_names=etab_names), code="""
        const static_data = static_source.data;
        var data = source.data;
        const static_flux_data = static_flux_source.data;
        var flux_data = flux_source.data;
        const n = static_data.nom_ght.length;
        
        //reinitialize source data
        for (const key in data){
            data[key] = [];
        }
        
        //reinitialize flux source data
        for (const key in flux_data){
            flux_data[key] = [];
        }
        
        /*
        //case the is nothing in the multiplechoice
        if (mc.value.lenght == 0){
            mc.value = etab_names
        }
        */
        
        
        //we retrieve the selected etablissement(s) name(s) in the multiplechoice
        //const widget_value = cb_obj.value;
        var widget_value
        
        //loop over all the etablissements into the multiple choices
        for (let j=0; j < mc.value.length; j++){
            widget_value = mc.value[j]
            //get the data related to the selected etablissement
            for (let i=0; i < n; i++){
                if(static_data.etablissement[i] == widget_value){
                    for (const key in static_data){
                        data[key].push(static_data[key][i])
                    }
                }
            }
            //for the flux
            for (let j=0; mc.value.length;j++){
                for(let i=0; i<static_flux_data.etablissement.length;i++){
                    for(const key in static_flux_data){
                        flux_data[key].push(static_flux_data[key][i])
                    }
                }
            }
        }
        
        flux_source.change.emit();
        source.change.emit();
    """)
mc.js_on_change('value', etab_callback)

#define layout
widgets = column(select, mc, data_table)
layout = row(p, widgets)

#show(layout)
curdoc().add_root(layout)
