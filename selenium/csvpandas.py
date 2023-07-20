# %%
import pandas as pd
df = pd.read_csv('../output20230719-141040.csv',delimiter=';')


df['sqm'] = df['sqm'].str.replace(' m²','').astype(float)
df['perm'] = df['perm'].str.replace(' zł/m²','').str.replace(' ','').fillna(-1).astype(int)
df['price'] = df['price'].str.replace(' zł','').str.replace('Zapytaj o cenę','-1').str.replace(' ','').fillna(-1).astype(int)
df['rooms'] = df['rooms'].str.replace(r' pokoje| pokoi| pokój','',regex=True).astype(int)
df['id'] = df['link'].str[-7:]


# %%

# %%
from geopy.geocoders import Nominatim
def geolocate():
    geolocator = Nominatim(user_agent="http")
    def ll(adress:str):
        try:
            adress = adress.lower().replace('ul.','')
            print(adress)
            x = geolocator.geocode(adress,country_codes='pl')
            return (x.latitude,x.longitude)
        except:
            pass
    df['geo'] = df['where'].apply(ll)
# geolocate()
# %%
