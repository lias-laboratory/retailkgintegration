# Experimentation A1 large volume

# Imports
import subprocess
import os
import sparql_dataframe

# Start ontopVKG with a connection to large volume postgres database
commande_str = "ontop endpoint -m ../general/store_mapping_v3_intrerne.ttl -t ../general/products_and_sales_ontology.xml -p ../general/local_postgres_big_volume.properties"

p = subprocess.Popen(commande_str.split(" "), stdout=subprocess.PIPE, cwd=os.getcwd())

endpoint = "http://localhost:8080/sparql"

# Q1 query
q1 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bimedia: <http://test.org/products_and_sales_ontology/>

SELECT ?siret
where {
?store rdf:type bimedia:Store.
?store bimedia:siret ?siret  .     
?store bimedia:is_in_zip_zone ?zipzone.
?zipzone bimedia:zip_code ?zipcode
FILTER (strstarts(str(?zipcode), '17')) 
}
"""

df = sparql_dataframe.get(endpoint, q1)
df.siret = df.siret.astype(int).astype(str)
print(df)

# Q2 query
q2 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bimedia: <http://test.org/products_and_sales_ontology/>

SELECT distinct ?siret
  where {
    ?sale rdf:type bimedia:ProductSell.
    ?sale bimedia:quantity_sold ?quantity.
    ?sale bimedia:is_product ?product.
    ?sale bimedia:date_sold ?date.
    ?sale  bimedia:is_sold_by ?pdv.
    ?product rdfs:label ?productname.
    ?pdv bimedia:siret ?siret  .     
    FILTER (xsd:date(?date) > "2023-08-16"^^xsd:date && xsd:date(?date) < "2023-08-18"^^xsd:date) 
    FILTER contains(lcase(?productname),"coca")    		
    }
"""

df = sparql_dataframe.get(endpoint, q2)
df.siret = df.siret.astype(int).astype(str)
print(df)

# Q3' query
q3p = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bimedia: <http://test.org/products_and_sales_ontology/>

SELECT ?siret ?iris_code (sum(?quantity) as ?sumquantity)
  where {
    ?sale rdf:type bimedia:ProductSell.
    ?sale bimedia:quantity_sold ?quantity.
    ?sale bimedia:is_product ?product.
    ?sale bimedia:date_sold ?date.
    ?product bimedia:is_type_of ?producttype.
    ?producttype bimedia:level_1 ?level1.
    ?sale  bimedia:is_sold_by ?pdv.
    ?pdv bimedia:siret ?siret  .     
    ?pdv bimedia:is_in_iris_zone ?iriszone.
    ?iriszone bimedia:iris_code ?iris_code .
    FILTER (xsd:date(?date) > "2023-08-16"^^xsd:date && xsd:date(?date) < "2023-09-16"^^xsd:date && ?level1="Presse")        		
    }
group by ?siret ?iris_code ?level1 
having (sum(?quantity) > 100)
"""

df = sparql_dataframe.get(endpoint, q3p)
df.siret = df.siret.astype(int).astype(str)
print(df)
