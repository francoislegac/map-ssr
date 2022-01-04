# Mapping of health facilities specialized in SSR (Soins de Suite et de Réadaptation)

## Overview
This project is a small app designed to help health specialists to take the right decisions. It is build using the python library Bokeh that makes it simple to create interactive plots triggering python callbacks. The app has been deployed with Heroku mainly to save time. 
The tool allows the user to get a broader view of the distribution of health facilities in the Bourgogne-Franche-Comté region. 
The data come from the following website: https://www.scansante.fr/flux-entre-etablissements-orfee 

The tool is available at the following address:  https://desolate-tundra-15287.herokuapp.com/
 

## Description of the files

### Data structure

```bash
├───app
│   │   app.py
│   │   Procfile
│   │   requirements.txt
│   └───data
│       │   coordght.csv
│       │   flux.csv
│       │   
│       └───departement_files
│           │   
│           └───patches departements france
│                   
└───data cleaning
    │   api_key_geocoding.txt
    │   get_cities_from_coords.py
    │   
    ├───data versions after cleaning
    │           
    ├───initial documents
    │       Cartographie SSR 2 23112021.xlsx
    │       Coordonnées Etablissement SSR.xlsx
    │       
    └───jupyter notebooks
```
**app**

- `app.py:` the main python file describing the tool
- `Procfile:` a file to provide necessary parameters to deploy the app 
- `requirements.txt:` straightforward
- `data:` folder containing the required data (after cleaning) and the departement patches to display the departements on the map. Note that we have kept the patches for all the departements in case we would like to extend this tool to another region. 

**data cleaning**

- `api_key_geocoding.txt:` the api to access the API that help us to retrieve the city and other geo infos from the coordinates.
- `get_cities_from_coords.py:` the python script to get the geo infos from the coordinates 
- `data versions afters cleaning:` are just checkpoint of the data after each cleaning steps
- `initial documents:` the raw excel after getting the data from the source
- `jupyter notebooks:` a folder with the notebooks used to clean the data



