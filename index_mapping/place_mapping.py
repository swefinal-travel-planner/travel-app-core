place_mapping = {
    "mappings": {
        "properties": {
            "id": {
                "type": "text",
            },
            "en_name": {
                "type": "text",
            },
            "vi_name": {
                "type": "text",
            },
            "long": {
                "type": "float"
            },
            "lat": {
                "type": "float"
            },
            "en_type": {
                "type": "text",
            },
            "vi_type": {
                "type": "text",
            },
            "en_properties": {
                "type": "text",
            },
            "vi_properties": {
                "type": "text",
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
