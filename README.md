# Knowledge Graphs for Data Integration in Retail

This repository accompanying our scientific paper on leveraging Semantic Web technologies for data integration in the retail sector, specifically focusing on the case study of Bimedia. This repository contains the complete codebase for the experiments detailed in our study, including mapping codes, and Jupyter notebooks guiding through the experimentation process.

Our work introduces a comprehensive solution framework for implementing semantic technologies in real-world retail scenarios, addressing the need for a flexible and extensible semantic layer and constructing a Knowledge Graph for modeling complex retail data relationships. Through experimental validation, we aim to demonstrate the practicality and scalability of our approach, offering insights into optimizing operational efficiency and enhancing customer experiences with semantic technologies.

This work is carried out thanks to the support of the [ANRT](https://www.anrt.asso.fr/fr) through the CIFRE (Industrial Agreements for Training through Research) program. The project is supported by [Bimedia](https://www.bimedia.com/) company and [LIAS laboratory (ISAE-ENSMA)](https://www.lias-lab.fr/).

## Repository Organisation

The key directories for experiments are organised as:

* *1_experimental_setup*: contains an example of each of the scripts needed to set up the experiments for our contribution. These files are provided as a support for those with similar projects or for curious individuals looking to learn more.
* *2_experimental_execution*: contains the code related to the experimentation process. It allows us to see the executed queries, etc.
  * *1_experimental_setup/kg_creation_from_csv_file*: two code examples dedicated to crafting a knowledge graph from CSV files. One of the examples addresses a scenario where a CSV file sourced from open data on the internet is utilized, constructing a graph reflecting this data and establishing connections with an already existing graph. The other example pertains to the creation of a graph from multiple CSV files, each representing tables from a relational database exported in this format.
  * *1_experimental_setup/vkg_creation*: all the necessary code for creating a virtual knowledge graph from a relational database (in this case, PostgreSQL).
* *2_experimental_execution/AX_QUERIES*: as many folders as architectures. Each of these folders contains two Jupyter notebooks for executing the three SPARQL queries discussed in our contribution. One notebook targets data sources with small volumes, and the other targets large volumes.

## Requirements

The contribution is developped with the Python programming language. The minimal software requirements for the installation of this package are:

* Python 3
* Jupyter Notebook
* PIP
* Git
* All operating systems that support Python

## Setup

At the root Git repository, execute the following command to install the Python packages required:

```bash
pip install -r requirements.txt .
```

## Running

You have the option to use any of these scripts to create your own semantic web layer. Two possibilities are then available to you, and they are presented in the following subsections.

### Create a native knowledge graph from a database (of any type)

For creating a native knowledge graph from a database, we provided two examples.

* The first example is a brief example for creating a graph based on a CSV file of external data (open data). The code is available in the file *1_experimental_setup/kg_creation_from_csv_file/external_data_kg_creation.ipynb*. In this first example, you will notice the method used to link this data graph containing external data to our data graph, which can be either virtual or native, containing internal data.

* The second example is more comprehensive, in which a set of data is transformed, imported and exported as CSV files from a relational database (one CSV file per table), into a knowledge graph. The code is available in the file *1_experimental_setup/kg_creation_from_csv_file/internal_data_small_volume_kg_creation.ipynb*. These two files will provide you with examples, making it easy for you to adapt this approach to your own data.

### Create a virtual knowledge graph from a database (of any type)

To create the virtual knowledge graphs required for our contributions, we proceeded in 5 major steps, which are:

* Creating and populating a relational database (PostgreSQL in our case). Population is performed using the script *1_populate_db_internal_data_small_volumes.ipynb*.
* Creating the file containing the ontology of the graph we want to create. Generating this file is done using the script *2_create_the_ontology_file.ipynb*.
* Creating the property file to configure the OntopVKG tool, which will be able to connect to the relational database. An example is provided in the file *local_postgres_small_volume.properties*.
* Creating the R2RML mapping script, allowing you to express the mapping rules between the data from your relational database and your ontology. A fairly comprehensive example is provided with the script *vkg_internal_data_mapping_R2RML.ttl*. An important point in this example is the creation of relations between instances.
* Launching the OntopVKG tool using the command provided in the script 3_ontop_vkg_start.ipynb, adapting the parameters with the names of your files.

You can then send SPARQL queries to the local address of Ontop, either through the graphical interface by accessing the address <http://localhost:8080> with your browser, or by sending HTTP requests containing the SPARQL query to the address <http://localhost:8080/sparql> (an example is provided in file *2_experimental_execution/A1_QUERIES/A1_large_volume_queries.ipynb*).

## Software license agreement

Details the license agreement of TME: [LICENSE](LICENSE)

## Historic Contributors (core developers first followed by alphabetical order)

* [Maxime PERROT (core developer)](https://www.lias-lab.fr/members/maximeperrot/) (Bimedia and LIAS/ISAE-ENSMA)
* [Mickael BARON](https://www.lias-lab.fr/members/mickaelbaron/) (LIAS/ISAE-ENSMA)
* [Brice CHARDIN](https://www.lias-lab.fr/members/bricechardin/) (LIAS/ISAE-ENSMA)
* [Stéphane JEAN](https://www.lias-lab.fr/members/stephanejean/) (LIAS/University of Poitiers)
