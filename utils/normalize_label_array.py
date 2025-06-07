def normalize_label_array(label_array: list):
    # Remove duplicates by converting to a set and back to a list
    unique_labels = sorted(set(label_array))
    
    return "|".join(unique_labels)

def extract_labels_from_string(label_string: str):
    # Split the string by '|' and remove any leading/trailing whitespace
    labels = [label.strip() for label in label_string.split('|') if label.strip()]
    
    return labels