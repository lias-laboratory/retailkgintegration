# Script example to launch OntopVKG

# Imports
import subprocess
import os

# Ontop vkg start command (this command can be executed in your terminal after OntopVKG installation)

commande_str = "ontop endpoint -m ./vkg_internal_data_mapping_R2RML.ttl -t ./products_and_sales_ontology.xml -p ./local_postgres_small.properties"

p = subprocess.Popen(commande_str.split(" "), stdout=subprocess.PIPE, cwd=os.getcwd())
