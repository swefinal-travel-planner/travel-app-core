trip_mapping = {
    "mappings": {
        "properties": {
            "user_properties": {
                "type": "nested",
                "properties": {
                    "location_attributes": {
                        "type": "keyword",
                        "index": True
                    },
                    "food_attributes": {
                        "type": "keyword",
                        "index": True
                    }
                }
            },
            "trip_properties": {
                "type": "nested",
                "properties": {
                    "vi_location_attributes_labels": {
                        "type": "keyword",
                        "index": True
                    },
                    "vi_food_attributes_labels": {
                        "type": "keyword",
                        "index": True
                    },
                    "en_location_attributes_labels": {
                        "type": "keyword",
                        "index": True
                    },
                    "en_food_attributes_labels": {
                        "type": "keyword",
                        "index": True
                    }
                }
            },
            "trip_items": {
                "type": "nested",
                "properties": {
                    "breakfast_list": {
                        "type": "nested",
                        "properties": {
                            "place_id": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "is_selected": {
                                "type": "boolean"
                            }
                        }
                    },
                    "lunch_dinner_list": {
                        "type": "nested",
                        "properties": {
                            "place_id": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "is_selected": {
                                "type": "boolean"
                            }
                        }
                    },
                    "location_list": {
                        "type": "nested",
                        "properties": {
                            "place_id": {
                                "type": "text"
                            },
                            "score": {
                                "type": "float"
                            },
                            "is_selected": {
                                "type": "boolean"
                            }
                        }
                    }
                }
            }
        }
    }
}