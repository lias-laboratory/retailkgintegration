# Script example to create a complexe knowledge graph from CSV file

# Imports
from owlready2 import (
    Imp,
    get_ontology,
    onto_path,
    Thing,
    ObjectProperty,
    FunctionalProperty,
    sync_reasoner_pellet,
    IRIS,
    destroy_entity,
)
import urllib.parse
import datetime
import pandas as pd
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime
import re
import unicodedata
from w3lib.html import replace_entities
import string
import math
import multiprocessing
import gc
import time
from xml.sax.saxutils import escape
import re
from os import listdir
from os.path import isfile, join
from tqdm import tqdm

onto_path.append("./")

# Ontology schema creation

## Initialisation

### Creation of the products and sales ontology for internal data
products_and_sales_ontology = get_ontology(
    "http://test.org/products_and_sales_ontology/"
)
products_and_sales_ontology.set_base_iri(
    "http://test.org/products_and_sales_ontology/", rename_entities=False
)

with products_and_sales_ontology:

    class Store(Thing):
        pass

    class Bakery(Store):
        pass

    class Pub(Store):
        pass

    class TobaccoStore(Store):
        pass

    class Product(Thing):
        pass

    class ProductSell(Thing):
        pass

    class ProductType(Thing):
        pass

    class ProductFamily(Thing):
        pass

    class Merchant(Thing):
        pass

    class Address(Thing):
        pass

    class ZipZone(Thing):
        pass

    class IrisZone(Thing):
        pass

    class Town(Thing):
        pass

    class Population(Thing):
        pass

    class PersonGroup(Thing):
        pass

    class Activity(Thing):
        pass

    class InseeZone(Thing):
        pass

    class live_in(ObjectProperty, FunctionalProperty):
        domain = [Population]
        range = [IrisZone]

    class is_managed_by(ObjectProperty, FunctionalProperty):
        domain = [Store]
        range = [Merchant]

    class is_type_of(ObjectProperty, FunctionalProperty):
        domain = [Product]
        range = [ProductType]

    class is_sorted_on(ObjectProperty, FunctionalProperty):
        domain = [Product]
        range = [ProductFamily]

    class familly_name(ProductFamily >> str, FunctionalProperty):
        pass

    class familly_id(ProductFamily >> str, FunctionalProperty):
        pass

    class sell(ObjectProperty):
        domain = [Store]
        range = [ProductSell]

    class is_sold_by(ObjectProperty, FunctionalProperty):
        domain = [ProductSell]
        range = [Store]

    class is_product(ObjectProperty, FunctionalProperty):
        domain = [ProductSell]
        range = [Product]

    class address(Store >> Address, FunctionalProperty):
        pass

    class enseigne(Store >> str, FunctionalProperty):
        pass

    class siret(Store >> str, FunctionalProperty):
        pass

    class has_persons(Population >> PersonGroup):
        pass

    class has_activity(PersonGroup >> Activity, FunctionalProperty):
        pass

    class activity_name(Activity >> str, FunctionalProperty):
        pass

    class has_count(PersonGroup >> float, FunctionalProperty):
        pass

    class has_population(IrisZone >> Population, FunctionalProperty):
        pass

    class is_part_of_pop(PersonGroup >> Population, FunctionalProperty):
        pass

    class is_near(Population >> Store, FunctionalProperty):
        pass

    class is_in_insee_zone(Store >> InseeZone, FunctionalProperty):
        pass

    class is_in_zip_zone(Store >> ZipZone, FunctionalProperty):
        pass

    class is_in_iris_zone(Store >> IrisZone, FunctionalProperty):
        pass

    class is_in_town(Store >> Town):
        pass

    class quantity_sold(ProductSell >> float, FunctionalProperty):
        pass

    class date_sold(ProductSell >> datetime.date, FunctionalProperty):
        pass

    class type_predicted_level_1(ProductType >> str, FunctionalProperty):
        pass

    class type_predicted_level_2(ProductType >> str, FunctionalProperty):
        pass

    class iris_code(IrisZone >> str, FunctionalProperty):
        pass

    class insee_code(InseeZone >> str, FunctionalProperty):
        pass

    class zip_code(InseeZone >> str, FunctionalProperty):
        pass


# Populate the graph

# Note: For the Graph population, we load CSV files containing data from different tables, we add data to the graph and then export the Graph.
# Sometimes, we need to create several Graph data files which can be then imported on a graph hosted in GraphDB (or others triplestore).
# The creation of multiple files is a good way to keep the file sizes under 200mb (GraphDB has a 200mb file size limit with the free license).
# And multiprocessing speed up a lot the process.

### Towns

#### Load
towns = pd.read_csv("./towns.csv", sep=";")
towns.new_insee_code = towns.new_insee_code.astype(str)
towns.new_zip_code = towns.new_zip_code.astype(str)
towns.new_insee_code = towns.new_insee_code.apply(
    lambda val: val.replace(".0", "").zfill(5)
)
towns.new_zip_code = towns.new_zip_code.apply(lambda val: val.replace(".0", ""))
towns
towns1 = towns[towns.new_town.isnull()]
towns2 = towns[towns.new_town.isnull() == False]

#### Insert data
for index, value in towns.iterrows():
    with products_and_sales_ontology:
        safe_string_iri = urllib.parse.quote_plus(str(value["town"]))
        town = Town("Town/" + safe_string_iri)
        town.label = value["town"]
        town.zip_code = value["zip_code"]


### Partners blacklist

# Note: list of partners to not include in studies for confidentiality and data protection
partners_blacklist = pd.read_csv("./reporting_partners_blacklist.csv", sep=";")
partners_blacklist


### Stores

#### Load
store_ids = pd.read_csv("./store_ids.csv", sep=";")
store_ids.enseigne = store_ids.enseigne.fillna("")
store_ids = store_ids[store_ids.store_id.isin(partners_blacklist) == False]


def safe_value(value, type_value):
    if not pd.isnull(value):
        if type_value == "float":
            return float(value)
        if type_value == "int":
            return int(value)
        return str(value)
    else:
        if type_value == "str":
            return ""
        if type_value == "float":
            return -1
        return ""


#### Insert data
for index, value in store_ids.iterrows():

    with products_and_sales_ontology:
        safe_string_iri = urllib.parse.quote_plus(str(value["store_id"]))
        store = Store("Store/" + safe_string_iri)
        store.label = value["store_id"]
        if not pd.isnull(value["nom"]):
            safe_string_iri = urllib.parse.quote_plus(
                str(value["store_id"]) + value["nom"]
            )
            merchant = Merchant("Merchant/" + safe_string_iri)
            merchant.label = value["nom"]
            store.is_managed_by = merchant
        store.siret = safe_value(value["siret"], "str")
        store.enseigne = safe_value(value["enseigne"], str)

### Addresses

#### Load
addresses = pd.read_csv("./address.csv", sep=";")

#### Insert data
error = 0


with tqdm(total=len(addresses)) as pbar:
    for index, value in addresses.iterrows():
        with products_and_sales_ontology:
            safe_string_iri = urllib.parse.quote_plus(str(value["store_id"]))
            store = IRIS[
                "http://test.org/products_and_sales_ontology/Store/" + safe_string_iri
            ]
            if store:
                insee_zone = IRIS[
                    "http://test.org/products_and_sales_ontology/InseeZone/"
                    + urllib.parse.quote_plus(str(value["insee_code"]))
                ]
                if insee_zone is None:
                    if not pd.isnull(value["insee_code"]):
                        safe_string_iri = urllib.parse.quote_plus(
                            str(value["insee_code"])
                        )
                        insee_zone = InseeZone("InseeZone/" + safe_string_iri)
                        insee_zone.label = value["insee_code"]
                        insee_zone.insee_code = value["insee_code"]
                    store.is_in_insee_zone = insee_zone

                zip_zone = IRIS[
                    "http://test.org/products_and_sales_ontology/ZipZone/"
                    + urllib.parse.quote_plus(str(value["zip_code"]))
                ]
                if zip_zone is None:
                    if not pd.isnull(value["zip_code"]):
                        safe_string_iri = urllib.parse.quote_plus(
                            str(value["zip_code"])
                        )
                        zip_zone = ZipZone("ZipZone/" + safe_string_iri)
                        zip_zone.label = value["zip_code"]
                        zip_zone.zip_code = value["zip_code"]
                    store.is_in_zip_zone = zip_zone

                iris_zone = IRIS[
                    "http://test.org/products_and_sales_ontology/IrisZone/"
                    + urllib.parse.quote_plus(str(value["iris"]))
                ]
                if iris_zone is None:
                    if not pd.isnull(value["iris"]):
                        safe_string_iri = urllib.parse.quote_plus(str(value["iris"]))
                        iris_zone = IrisZone("IrisZone/" + safe_string_iri)
                        iris_zone.label = value["iris"]
                        iris_zone.iris_code = value["iris"]
                    store.is_in_iris_zone = iris_zone
            else:
                error += 1
        pbar.update(1)

print(error)


### Products categories

#### Load
category_summaries = pd.read_csv("./category_summaries.csv", sep=";")
category_summaries = category_summaries[category_summaries.store_id.isnull() == False]
category_summaries.sort_values(by="date", ascending=False, inplace=True)
category_summaries.drop_duplicates(
    subset=["store_id", "id_from_store"], keep="first", inplace=True
)

#### Create multiprocessing results dir
path = "./onto_product_families"
shutil.rmtree(path, ignore_errors=True)
Path(path).mkdir(parents=True, exist_ok=True)


#### Insert data and export
def create_product_families(chunk):
    with tqdm(total=len(chunk)) as pbar:
        # pbar.write('processed: '+multiprocessing.current_process().name )
        first = str(chunk.iloc[0].name)
        products_and_sales_ontology = get_ontology(
            "http://test.org/products_and_sales_ontology/"
        )
        for index, value in chunk.iterrows():
            with products_and_sales_ontology:
                safe_string_iri = urllib.parse.quote_plus(
                    str(value["store_id"]) + "_" + safe_value(value["libelle"], "str")
                )
                familly = ProductFamily("ProductFamily/" + safe_string_iri)
                familly.label = value["store_id"] + "_" + value["libelle"]
                familly.familly_name = safe_value(value["libelle"], "str")
                familly.familly_id = safe_value(value["id_from_store"], "str")
            pbar.update(1)
        products_and_sales_ontology.save(
            file="./onto_product_families/onto" + first + ".xml", format="rdfxml"
        )


# chunk is a DataFrame. To "process" the rows in the chunk:
chunk = category_summaries

# create as many processes as there are CPUs on your machine
num_processes = multiprocessing.cpu_count() - 2

# calculate the chunk size as an integer
chunk_size = int(chunk.shape[0] / num_processes)

# this solution was reworked from the above link.
# will work even if the length of the dataframe is not evenly divisible by num_processes
chunks = [
    chunk.iloc[chunk.index[i : i + chunk_size]]
    for i in range(0, chunk.shape[0], chunk_size)
]


# create our pool with `num_processes` processes
pool = multiprocessing.Pool(processes=num_processes)

# apply our function to each chunk in the list
result = pool.map(create_product_families, chunks)


# Function to avoid ontology schema repetition
def keep_only_individuals(file_path, individual_type):
    with open(file_path, "r+") as f:
        new_f = f.readlines()
        f.seek(0)
        begin_write = False
        index = 0
        for line in new_f:
            if index < 7:
                f.write(line)
            if (
                not begin_write
                and 'owl:NamedIndividual rdf:about="' + individual_type + "/" in line
            ):
                f.write("\n")
                begin_write = True
                f.write(line)
            elif begin_write:
                f.write(line)
            index += 1
        f.truncate()


# Execution of the previous function on all the created files
families_files_dir = "./onto_product_families/"
families_files = [
    f for f in listdir(families_files_dir) if isfile(join(families_files_dir, f))
]

with tqdm(total=len(families_files)) as pbar:
    for filename in families_files:
        path = join(families_files_dir, filename)
        keep_only_individuals(path, "ProductFamily")
        onto2 = get_ontology("file://" + path).load()
        pbar.update(1)


if (
    IRIS[
        "http://test.org/products_and_sales_ontology/ProductFamily/"
        + urllib.parse.quote_plus(
            str(category_summaries.iloc[-1]["store_id"])
            + "_"
            + safe_value(category_summaries.iloc[-1]["libelle"], "str")
        )
    ]
    and IRIS[
        "http://test.org/products_and_sales_ontology/ProductFamily/"
        + urllib.parse.quote_plus(
            str(category_summaries.iloc[0]["store_id"])
            + "_"
            + safe_value(category_summaries.iloc[0]["libelle"], "str")
        )
    ]
):
    print("import ok")

### Product types (identified by ThesaurusBT algorithm)

#### Load
product_ontology_mapping = pd.read_csv(
    "./product_ontology_mapping_6_months.csv", sep=";"
)

#### Insert data
for index, value in (
    product_ontology_mapping[["type_product_predicted_1", "type_product_predicted_2"]]
    .drop_duplicates()
    .iterrows()
):
    with products_and_sales_ontology:
        if not pd.isnull(value["type_product_predicted_1"]) and not pd.isnull(
            value["type_product_predicted_2"]
        ):
            safe_string_iri = urllib.parse.quote_plus(
                value["type_product_predicted_1"]
                + "_"
                + value["type_product_predicted_2"]
            )
            producttype = ProductType("ProductType/" + safe_string_iri)
            producttype.label = (
                value["type_product_predicted_1"]
                + "_"
                + value["type_product_predicted_2"]
            )
            producttype.type_predicted_level_1 = value["type_product_predicted_1"]
            producttype.type_predicted_level_2 = value["type_product_predicted_2"]


## Ontology schema and graph exportation before products and sales importation as rdfxml file

products_and_sales_ontology.save(
    file="./onto_rdf_internal_data_before_products_and_sales.xml", format="rdfxml"
)


## Products definition


### Load
productids_summaries = pd.read_csv("./productids_1mois_16aout_16sept.csv", sep=";")
productids_summaries = productids_summaries[
    productids_summaries.store_id.isnull() == False
]
productids_summaries.sort_values(by="date", ascending=False, inplace=True)
productids_summaries.drop_duplicates(
    subset=["store_id", "category_id_from_store", "barcode"], keep="first", inplace=True
)


### Product Labels cleaning (rdfxml format does not support many encoding)
def supprimer_x(texte):
    texte = re.sub(r"(\d)x(\d)", r"\1\2", texte)
    texte = re.sub(r"(\d)X(\d)", r"\1\2", texte)
    texte = str(repr(texte)).replace("\\x", "").replace("'", "")
    return texte


def strip_accents(text):
    try:
        text = unicode(text, "utf-8")
    except (TypeError, NameError):  # unicode is a default on python 3
        pass
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    return str(text)


def clean_libelle(libelle):
    try:
        libelle = bytearray(libelle, "Windows-1252").decode("unicode_escape", "strict")
        libelle = replace_entities(libelle)

        libelle = strip_accents(libelle)
        # delete dot
        libelle = libelle.replace(".", "")
        # delete dot
        libelle = libelle.replace(".", "")
        # delete coma
        libelle = libelle.replace(",", "")
        # Remove punctuations
        libelle = re.sub("[%s]" % re.escape(string.punctuation), " ", libelle)
        # Remove numbers
        libelle = re.sub(r"\d", "", libelle)
        # lower case
        libelle = libelle.lower()
        # Remove multiple spaces
        libelle = re.sub("\s{2,}", " ", libelle)

        # libelle = re.sub('(^|\s)(sans|non|e|ss)\s',r'\1\2-' ,libelle)
        return libelle.strip()
    except:
        return ""


productids_summaries.libelle = productids_summaries.libelle.apply(clean_libelle)

### Create the dir of the resulting files
path = "./onto_products_data_petit_volume"
shutil.rmtree(path, ignore_errors=True)
Path(path).mkdir(parents=True, exist_ok=True)


### Insert data and export
def create_product(chunk):
    with tqdm(total=len(chunk)) as pbar:
        first = str(chunk.iloc[0].name)
        products_and_sales_ontology = get_ontology(
            "http://test.org/products_and_sales_ontology/"
        )
        with products_and_sales_ontology:
            for index, value in chunk.iterrows():
                familly = IRIS[
                    "http://test.org/products_and_sales_ontology/ProductFamily/"
                    + urllib.parse.quote_plus(
                        str(value["store_id"])
                        + "_"
                        + safe_value(value["libelle_famille"], "str")
                    )
                ]
                type = IRIS[
                    "http://test.org/products_and_sales_ontology/ProductType/"
                    + urllib.parse.quote_plus(
                        safe_value(value["type_product_predicted_1"], "str")
                        + "_"
                        + safe_value(value["type_product_predicted_2"], "str")
                    )
                ]
                safe_string_iri = urllib.parse.quote_plus(
                    value["store_id"] + "_" + value["barcode"]
                )
                product = Product("Product/" + safe_string_iri)
                if safe_value(value["libelle_produit"], "str") != "":
                    decoded = escape(safe_value(value["libelle_produit"], "str"))
                    decoded = bytes(decoded, "utf-8").decode("utf-8")
                    product.label = supprimer_x(decoded)
                product.is_sorted_on = familly
                product.is_type_of = type
                pbar.update(1)
        products_and_sales_ontology.save(
            file="./onto_products_data_petit_volume/onto" + first + ".xml",
            format="rdfxml",
        )


product_descriptions = (
    productids_summaries.rename(columns={"libelle": "libelle_produit"})
    .merge(
        category_summaries[["store_id", "id_from_store", "libelle"]].rename(
            columns={
                "id_from_store": "category_id_from_store",
                "libelle": "libelle_famille",
            }
        ),
        how="inner",
        on=["store_id", "category_id_from_store"],
    )
    .merge(product_ontology_mapping, how="left", on=["store_id", "barcode"])
)

del productids_summaries
del category_summaries
del product_ontology_mapping

# chunk is a DataFrame. To "process" the rows in the chunk:
chunk = product_descriptions

# create as many processes as there are CPUs on your machine
num_processes = multiprocessing.cpu_count() - 2

# calculate the chunk size as an integer
chunk_size = int(chunk.shape[0] / num_processes)

# this solution was reworked from the above link.
# will work even if the length of the dataframe is not evenly divisible by num_processes
chunks = [
    chunk.iloc[chunk.index[i : i + chunk_size]]
    for i in range(0, chunk.shape[0], chunk_size)
]


# create our pool with `num_processes` processes
pool = multiprocessing.Pool(processes=num_processes)


# apply our function to each chunk in the list
result = pool.map(create_product, chunks)

pool.close()
time.sleep(2.5)
pool.join()
gc.collect()


# Execution of the function to avoid ontology schema repetition

products_files_dir = "./onto_products_data_petit_volume/"
products_files = [
    f for f in listdir(products_files_dir) if isfile(join(products_files_dir, f))
]

with tqdm(total=len(products_files)) as pbar:
    for filename in products_files:
        path = join(products_files_dir, filename)
        keep_only_individuals(path, "Product")
        onto2 = get_ontology("file://" + path).load()
        pbar.update(1)


if (
    IRIS[
        "http://test.org/products_and_sales_ontology/Product/"
        + urllib.parse.quote_plus(
            product_descriptions.iloc[-1]["store_id"]
            + "_"
            + product_descriptions.iloc[-1]["barcode"]
        )
    ]
    and IRIS[
        "http://test.org/products_and_sales_ontology/Product/"
        + urllib.parse.quote_plus(
            product_descriptions.iloc[0]["store_id"]
            + "_"
            + product_descriptions.iloc[0]["barcode"]
        )
    ]
):
    print("import ok")

## Product sales

### Load
sales = pd.read_csv("./export_products_summaries_1mois_16aout_17sep.csv", sep=";")
product_descriptions = (
    productids_summaries.rename(columns={"libelle": "libelle_produit"})
    .merge(
        category_summaries[["store_id", "id_from_store", "libelle"]].rename(
            columns={
                "id_from_store": "category_id_from_store",
                "libelle": "libelle_famille",
            }
        ),
        how="inner",
        on=["store_id", "category_id_from_store"],
    )
    .merge(product_ontology_mapping, how="left", on=["store_id", "barcode"])
)
sales = sales.merge(
    product_descriptions[
        [
            "store_id",
            "barcode",
            "libelle_produit",
            "category_id_from_store",
            "libelle_famille",
            "type_product_predicted_1",
        ]
    ],
    how="inner",
    on=["store_id", "barcode"],
)

### Create exportation dir
path = "./onto_sales_data_petit_volume"
shutil.rmtree(path, ignore_errors=True)
Path(path).mkdir(parents=True, exist_ok=True)


### Insert data and export
def create_product_sell(chunk):
    first = str(chunk.iloc[0].name)
    products_and_sales_ontology = get_ontology(
        "http://test.org/products_and_sales_ontology/"
    )
    with products_and_sales_ontology:
        for index, value in chunk.iterrows():
            store = IRIS[
                "http://test.org/products_and_sales_ontology/Store/"
                + urllib.parse.quote_plus(str(value["store_id"]))
            ]
            product = IRIS[
                "http://test.org/products_and_sales_ontology/Product/"
                + urllib.parse.quote_plus(value["store_id"] + "_" + value["barcode"])
            ]
            safe_string_iri = urllib.parse.quote_plus(
                value["store_id"] + "_" + value["barcode"] + "_" + value["date"]
            )
            product_sell = ProductSell("ProductSell/" + safe_string_iri)
            product_sell.label = (
                value["store_id"] + "_" + value["barcode"] + "_" + value["date"]
            )
            product_sell.quantity_sold = value["sum_quantity_product"]
            try:
                date = datetime.strptime(value["date"][:10], "%Y-%m-%d").date()
            except:
                date = None
            if date is not None:
                product_sell.date_sold = date
            product_sell.is_sold_by = store
            product_sell.is_product = product

    products_and_sales_ontology.save(
        file="./onto_sales_data_petit_volume/onto_process_"
        + str(multiprocessing.current_process().name)
        + "_first_row_"
        + first
        + ".xml",
        format="rdfxml",
    )
    keep_only_individuals(
        "./onto_sales_data_petit_volume/onto_process_"
        + str(multiprocessing.current_process().name)
        + "_first_row_"
        + first
        + ".xml",
        "ProductSell",
    )


chunksize = 1.5 * (10**6)

chunks_all = pd.read_csv(
    "./export_products_summaries_1mois_16aout_17sep.csv", sep=";", chunksize=chunksize
)


number_of_rows = sum(
    1 for row in open("./export_products_summaries_1mois_16aout_17sep.csv", "r")
)
number_of_chunks = math.ceil(number_of_rows / chunksize)

with tqdm(total=number_of_chunks) as pbar:
    for chunk in chunks_all:

        # chunk is a DataFrame. To "process" the rows in the chunk:
        chunk = chunk.merge(
            product_descriptions[
                [
                    "store_id",
                    "barcode",
                    "libelle_produit",
                    "category_id_from_store",
                    "libelle_famille",
                ]
            ],
            how="inner",
            on=["store_id", "barcode"],
        )

        # create as many processes as there are CPUs on your machine
        num_processes = multiprocessing.cpu_count()

        # calculate the chunk size as an integer
        chunk_size = int(chunk.shape[0] / num_processes)

        # this solution was reworked from the above link.
        # will work even if the length of the dataframe is not evenly divisible by num_processes
        chunks = [
            chunk.iloc[chunk.index[i : i + chunk_size]]
            for i in range(0, chunk.shape[0], chunk_size)
        ]

        # create our pool with `num_processes` processes
        pool = multiprocessing.Pool(processes=num_processes)

        # apply our function to each chunk in the list
        result = pool.map(create_product_sell, chunks)

        pool.close()
        time.sleep(2.5)
        pool.join()
        gc.collect()
        pbar.update(1)

# 63 minutes for large volume files

### Execution of the function to avoid ontology schema repetition

sales_files_dir = "./onto_sales_data_petit_volume/"
sales_files = [f for f in listdir(sales_files_dir) if isfile(join(sales_files_dir, f))]

with tqdm(total=len(sales_files)) as pbar:
    for filename in sales_files:
        path = join(sales_files_dir, filename)
        keep_only_individuals(path, "ProductSell")
        pbar.update(1)
# 10 minutes


# All the rdfxml files created by this notebook can than be imported to a graph repository.
# For example, you just need to create a graph db repository and import all the .xml files generates.
# In our case, we set the base iri as : http://test.org/products_and_sales_ontology/ on the importation form of Graph DB.
# Other parameters where the defaults values.
