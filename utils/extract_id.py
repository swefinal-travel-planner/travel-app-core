def extract_ids_from_string(id_string: str):
    """
    Extracts a list of IDs from a string where IDs are separated by '|'.
    
    Args:
        id_string (str): A string containing IDs separated by '|'.
        
    Returns:
        list: A list of extracted IDs.
    """
    if not id_string:
        return []
    
    # return empty list if not matching the expected format
    if not isinstance(id_string, str) or ';' not in id_string:
        return []

    # Split the string by ';' and remove any leading/trailing whitespace
    ids = [id.strip() for id in id_string.split(';') if id.strip()]

    return ids