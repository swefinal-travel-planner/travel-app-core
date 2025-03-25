place_mapping = {
    "mappings": {
        "properties": {
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
                "type": "text",
            },
            "properties": {
                "type": "text",
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
