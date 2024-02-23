# Script example to create a simple knowledge graph from CSV file

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
import pandas as pd
from datetime import datetime
import multiprocessing
from tqdm import tqdm
import shutil
from pathlib import Path

onto_path.append("./")

# Ontology schema creation

## Initialisation

### Creation of the open data ontology object
open_data_ontology = get_ontology("http://test.org/open_data_ontology/")
open_data_ontology.set_base_iri(
    "http://test.org/open_data_ontology/", rename_entities=True
)

### Creation of a "fake" products and sales ontology object for the sameAs relation
products_and_sales_ontology = get_ontology(
    "http://test.org/products_and_sales_ontology/"
)

## Open data ontology definition
with open_data_ontology:

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

    class live_in(ObjectProperty, FunctionalProperty):
        domain = [Population]
        range = [IrisZone]

    class has_persons(Population >> PersonGroup):
        pass

    class has_activity(PersonGroup >> Activity):
        pass

    class activity_name(Activity >> str, FunctionalProperty):
        pass

    class has_count(PersonGroup >> float, FunctionalProperty):
        pass

    class has_population(IrisZone >> Population, FunctionalProperty):
        pass

    class is_part_of_pop(PersonGroup >> Population, FunctionalProperty):
        pass

    class iris_code(IrisZone >> str, FunctionalProperty):
        pass


## Products and sales ontology definition (fake)

### Note:  We do not need to redefine all the classes, but just the one we need to create the owl:SameAs relation with the open data ontology
with products_and_sales_ontology:

    class IrisZone(Thing):
        pass


### Note that you can also load the ontology from a file
### onto = get_ontology("file://./my_onto2.xml").load()

# Save the ontology schema as rdfxml
###This file will be imported into our rdf triple store (GraphDB in our case)

open_data_ontology.save(file="augmented_store_data_kg.xml", format="rdfxml")

# Populate the graph

## Load the CSV file as pandas dataframe
df_population = pd.read_csv(
    "./populations.csv", sep=";", dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}
)
df_population["IRIS"] = df_population.IRIS.astype(str)
df_population.columns


## Create the dir of the resulting files
path = "./augmented_store_data_files/"
shutil.rmtree(path, ignore_errors=True)
Path(path).mkdir(parents=True, exist_ok=True)


## Function to avoid ontology schema repetition
def keep_only_individuals(file_path):
    with open(file_path, "r+") as f:
        new_f = f.readlines()
        f.seek(0)
        begin_write = False
        index = 0
        for line in new_f:
            if index < 7:
                f.write(line)
            if not begin_write and "owl:NamedIndividual rdf:about=" in line:
                f.write("\n")
                begin_write = True
                f.write(line)
            elif begin_write:
                f.write(line)
            index += 1
        f.truncate()


## Multiprocessing graph population


### This function will return multiple xml files which can be then imported on a graph hosted in GraphDB (or others triplestore). The creation of multiple files is a good way to keep the file sizes under 200mb (GraphDB has a 200mb file size limit with the free license).
def create_population(chunk):
    first = str(chunk.iloc[0].name)
    open_data_ontology = get_ontology("http://test.org/open_data_ontology/")
    products_and_sales_ontology = get_ontology(
        "http://test.org/products_and_sales_ontology/"
    )
    columns_pop = [
        "P19_POP",
        "P19_POP0002",
        "P19_POP0305",
        "P19_POP0610",
        "P19_POP1117",
        "P19_POP1824",
        "P19_POP2539",
        "P19_POP4054",
        "P19_POP5564",
        "P19_POP6579",
        "P19_POP80P",
        "P19_POP0014",
        "P19_POP1529",
        "P19_POP3044",
        "P19_POP4559",
        "P19_POP6074",
        "P19_POP75P",
        "P19_POP0019",
        "P19_POP2064",
        "P19_POP65P",
        "P19_POPH",
        "P19_H0014",
        "P19_H1529",
        "P19_H3044",
        "P19_H4559",
        "P19_H6074",
        "P19_H75P",
        "P19_H0019",
        "P19_H2064",
        "P19_H65P",
        "P19_POPF",
        "P19_F0014",
        "P19_F1529",
        "P19_F3044",
        "P19_F4559",
        "P19_F6074",
        "P19_F75P",
        "P19_F0019",
        "P19_F2064",
        "P19_F65P",
        "C19_POP15P",
        "C19_POP15P_CS1",
        "C19_POP15P_CS2",
        "C19_POP15P_CS3",
        "C19_POP15P_CS4",
        "C19_POP15P_CS5",
        "C19_POP15P_CS6",
        "C19_POP15P_CS7",
        "C19_POP15P_CS8",
        "C19_H15P",
        "C19_H15P_CS1",
        "C19_H15P_CS2",
        "C19_H15P_CS3",
        "C19_H15P_CS4",
        "C19_H15P_CS5",
        "C19_H15P_CS6",
        "C19_H15P_CS7",
        "C19_H15P_CS8",
        "C19_F15P",
        "C19_F15P_CS1",
        "C19_F15P_CS2",
        "C19_F15P_CS3",
        "C19_F15P_CS4",
        "C19_F15P_CS5",
        "C19_F15P_CS6",
        "C19_F15P_CS7",
        "C19_F15P_CS8",
        "P19_POP_FR",
        "P19_POP_ETR",
        "P19_POP_IMM",
        "P19_PMEN",
        "P19_PHORMEN",
    ]
    with tqdm(total=len(chunk)) as pbar:
        for index, pop in chunk.iterrows():
            with products_and_sales_ontology:
                iris = IrisZone("IrisZone/" + pop["IRIS"])
            with open_data_ontology:
                iris = IrisZone("IrisZone/" + pop["IRIS"])
                population = Population("Population/" + pop["IRIS"])
                iris.has_population = population
                iris.equivalent_to.append(
                    products_and_sales_ontology["IrisZone/" + pop["IRIS"]]
                )
                for column in columns_pop:
                    activity = Activity(column.lower())
                    activity.activity_name = column.lower()
                    try:
                        nb_persons = float(pop[column])
                    except:
                        nb_persons = 0.0
                    person_group = PersonGroup(
                        "PersonGroup/" + pop["IRIS"] + "/" + column.lower()
                    )
                    person_group.has_activity.append(activity)
                    person_group.has_count = nb_persons
                    population.has_persons.append(person_group)
                    person_group.is_part_of_pop = population
                pbar.update(1)
    open_data_ontology.save(
        file="./augmented_store_data_files/onto" + first + ".xml", format="rdfxml"
    )
    keep_only_individuals("./augmented_store_data_files/onto" + first + ".xml")


# chunk is a DataFrame. To "process" the rows in the chunk:
chunk = df_population

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
result = pool.map(create_population, chunks)


# Then you just need to create a graph db repository, import the ontology schema. Then all the files created.
# In our case, we set the base iri as : http://test.org/open_data_ontology/ on the importation form of Graph DB.
# Other parameters where the defaults values.
