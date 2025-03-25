place_mapping = {
    "mappings": {
        "properties": {
            "id": {
                "type": "integer",
            },
            "name": {
                "type": "text",
            },
            "long": {
                "type": "float"
            },
            "lat": {
                "type": "float"
            },
            "type": {
                "type": "string",
            },
            "properties": {
                "type": "string",
            },
            "price": {
                "type": "float",
            },
            "place_vector": {
                "type": "dense_vector",
                "dims": 1024,
                "index": True,
                "similarity": "l2_norm"
            }
        }
    }
}
