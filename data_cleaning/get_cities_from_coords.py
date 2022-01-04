from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError
import pandas as pd
import numpy as np
from pprint import pprint

key = '10b7706b5b8241a3b35272609a27e797'
geocoder = OpenCageGeocode(key)
coordfile_path = 'data4/all_coord.csv'

df = pd.read_csv(coordfile_path, index_col=0)
df.reset_index(inplace=True)

states, municipalities, postcodes, villages, cities = [], [], [], [], []
try:
    for i in range(df.shape[0]):
        lat = df.loc[i, 'latitude']
        lng = df.loc[i, 'longitude']
        ad = df.loc[i, 'adresse']
        print(f'{ad}; {lat}; {lng}')
        result = geocoder.reverse_geocode(lat, lng)
        #pprint(result)
        try:
            state = result[0]['components']['state']
            states.append(state)
        except:
            states.append(np.nan)
        try:
            municipality = result[0]['components']['municipality']
            municipalities.append(municipality)
        except:
            municipalities.append(np.nan)        
        try:
            postcode = result[0]['components']['postcode']
            postcodes.append(postcode)  
        except:
            postcodes.append(np.nan)             
        try:
            village = result[0]['components']['village']
            villages.append(village)
        except:
            villages.append(np.nan)
        try:
            city = result[0]['components']['city']
            cities.append(city)
        except:
            cities.append(np.nan)

except RateLimitExceededError as ex:
    print(ex)

tmp = pd.DataFrame({
    'departement':states,
    'municipalite':municipalities,
    'code_postal':postcodes,
    'village':villages,
    'ville':cities
})

pd.concat([df, tmp], axis=1).to_csv('data4/coord_with_cities.csv')