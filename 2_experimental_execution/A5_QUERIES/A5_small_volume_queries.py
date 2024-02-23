# %% [markdown]
# # Experimentation A5 small volume

# Imports
import sparql_dataframe

# Note: Start GraphDB external data graph and small internal data graph
endpoint = "http://localhost:7200/repositories/rdf_petit_volumes"

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

# Q3 query
q3 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX bimedia: <http://test.org/products_and_sales_ontology/>
PREFIX open: <http://test.org/open_data_ontology/>

SELECT ?siret ?iriszone ?persongroup ?activity_name ?nb_person  WHERE {#?persongroup ?activity_name ?nb_person
     { SERVICE <repository:rdf_petit_volumes>
      
         {
            SELECT ?siret ?iriszone
            where {
                     {
                        SELECT ?siret ?iriszone ?level1
                        WHERE {
                        ?sale rdf:type bimedia:ProductSell.
                        ?sale bimedia:quantity_sold ?quantity.
                        ?sale bimedia:is_product ?product.
                        ?sale bimedia:date_sold ?date.
                        ?product bimedia:is_type_of ?producttype.
                        ?producttype bimedia:type_predicted_level_1 ?level1.
                        ?sale  bimedia:is_sold_by ?pdv.
                        ?pdv bimedia:siret ?siret.     
                        ?pdv bimedia:is_in_iris_zone ?iriszone.
                        FILTER (xsd:date(?date) > "2023-08-16"^^xsd:date && xsd:date(?date) < "2023-09-16"^^xsd:date && ?level1="Presse")        		
                        }
                        group by ?siret ?iriszone ?level1
                        having (sum(?quantity) > 100)
                     }  
                  }
            }
      }
   ?iris2  owl:sameAs ?iriszone.
   ?iris2 open:has_population ?pop .
   ?pop open:has_persons ?persongroup .
   ?persongroup open:has_count ?nb_person .
   ?persongroup open:has_activity ?activity .
   ?activity open:activity_name ?activity_name .    
   FILTER (?activity_name="c19_f15p_cs3" && ?nb_person > 300)    
}

"""

df = sparql_dataframe.get(endpoint, q3)
df.siret = df.siret.astype(int).astype(str)
print(df)
