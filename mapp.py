from elasticsearch import Elasticsearch,helpers
import csv

es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'KZ2yaUbgf-wVS7bbY*g1'))
index_name = "lambdalog"

if not es.indices.exists(index=index_name):

    # Define the mapping for the index
    mapping = {
        "properties": {
            "mimetype": {
                "type": "text",
                "analyzer": "standard"
            },
            "timestamp": {
                "type": "date",
                "format": "yyyy-MM-dd"
            },
            "statuscode": {
                "type": "integer"
            },
            "filename": {
                "type": "text",
                "analyzer": "standard"
            },
            "loglevel":{
                "type":"text"
            }
        }
    }
    # Create the index with the mapping
    es.indices.create(index=index_name, mappings=mapping)

# Open the CSV file
with open(r'C:\Users\hith6\OneDrive\Desktop\lambda_test\log.csv', 'r') as csvfile:
    # Create a CSV reader object
    reader = csv.DictReader(csvfile)
    # Use the bulk() method to index the data
    actions = []
    for row in reader:
        actions.append({
            "_index": index_name,
            "_source": {
                "mimetype": row["mimetype"],
                "timestamp": row["timestamp"],
                "statuscode": int(row["statuscode"]),
                "filename": row["filename"],
                "loglevel":row["loglevel"]
            }
        })
    helpers.bulk(es, actions, index_name)



print("Successfully indexed data from CSV file into Elasticsearch.")
