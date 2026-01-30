#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


from tqdm.auto import tqdm


# In[3]:


import click


# In[4]:


from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')


# In[5]:


url_csv = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'


# In[6]:


url_parquet = 'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet'


# In[7]:


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='ny_taxi', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    pass


# In[8]:


dtype = {
    "LocationID": "Int64",
    "Borough": "string",
    "Zone": "string",
    "service_zone": "string",
}


# In[9]:


df_iter = pd.read_csv(
    url_csv,
    dtype=dtype,
    iterator=True,
    chunksize=100000
)


# In[10]:


first = True

for df_chunk in tqdm(df_iter):

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="taxi_zone_lookup",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="taxi_zone_lookup",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))


# In[11]:


df_parquet = pd.read_parquet(url_parquet, engine='pyarrow')


# In[12]:


df_parquet.to_sql(name='green_trip_data', con=engine, if_exists='replace', index=False)


# In[13]:


print(f"Inserted: {len(df_parquet)} rows total.")

