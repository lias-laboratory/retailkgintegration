# Script example to create ontology schema from Python code

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
import datetime

onto_path.append("./")

# Ontology schema creation

## Initialisation : Creation of the products and sales ontology for internal data

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


## Export

products_and_sales_ontology.save(
    file="products_and_sales_ontology.xml", format="rdfxml"
)
