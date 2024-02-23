# Script example to populate Postgres DB from CSV

# Imports
from sqlalchemy import create_engine
import pandas as pd
import os
from os.path import join
from dotenv import load_dotenv
import csv
from io import StringIO

load_dotenv(dotenv_path=join(os.getcwd(), "./env.conf"))

# Create connection
user = "postgres"
password = "postgres"
db_host = "localhost"
port = 5432
db_name = "postgres_petit_volume"

db_uri = "postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(
    user, password, db_host, port, db_name
)
connection = create_engine(db_uri)

# CSV importations

## Products summaries


def psql_insert_copy(table, conn, keys, data_iter):
    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ", ".join('"{}"'.format(k) for k in keys).lower()
        print(columns)
        if table.schema:
            table_name = "{}.{}".format(table.schema, table.name)
        else:
            table_name = table.name

        sql = "COPY {} ({}) FROM STDIN WITH CSV".format(table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)


chunksize = 10**6
for chunk in pd.read_csv(
    "./export_products_summaries.csv", sep=";", chunksize=chunksize
):
    # chunk is a DataFrame. To "process" the rows in the chunk:
    chunk.to_sql(
        "products_summaries",
        connection,
        method=psql_insert_copy,
        if_exists="append",
        index=False,
    )

## Product descriptions

productids_summaries = pd.read_csv("./productids_1mois_16aout_16sept.csv", sep=";")
productids_summaries.to_sql(
    name="productids_summaries",
    con=connection,
    schema="public",
    if_exists="append",
    chunksize=int(productids_summaries.__len__() / 10000),
    index=False,
)

## Product categories

category_summaries = pd.read_csv("./category_summaries.csv", sep=";")
category_summaries.to_sql(
    name="category_summaries",
    con=connection,
    schema="public",
    if_exists="append",
    chunksize=int(category_summaries.__len__() / 10000),
    index=False,
)

## Ontology mapping

product_ontology_mapping = pd.read_csv("./product_ontology_mapping.csv", sep=";")
product_ontology_mapping.to_sql(
    name="product_ontology_mapping",
    con=connection,
    schema="summary",
    if_exists="append",
    chunksize=int(product_ontology_mapping.__len__() / 10000),
    index=False,
)

## Stores

store_ids = pd.read_csv("./store_ids.csv", sep=";")
store_ids.to_sql(
    name="store_ids",
    con=connection,
    schema="summary",
    if_exists="append",
    chunksize=int(store_ids.__len__() / 10000),
    index=False,
)

## Addresses

address = pd.read_csv("./address.csv", sep=";")
address.to_sql(
    name="address",
    con=connection,
    schema="summary",
    if_exists="append",
    chunksize=int(address.__len__() / 10000),
    index=False,
)

## Towns

towns = pd.read_csv("./towns.csv", sep=";")
towns.new_insee_code = towns.new_insee_code.astype(str)
towns.new_zip_code = towns.new_zip_code.astype(str)
towns.new_insee_code = towns.new_insee_code.apply(
    lambda val: val.replace(".0", "").zfill(5)
)
towns.new_zip_code = towns.new_zip_code.apply(lambda val: val.replace(".0", ""))
towns.to_sql(
    name="towns",
    con=connection,
    schema="summary",
    if_exists="append",
    chunksize=int(towns.__len__() / 10),
    index=False,
)
