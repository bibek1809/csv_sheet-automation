import json

def filter_rows(source_dict, rows_to_keep):
    # Filter rows to keep
    target_dict = {key: value for key, value in source_dict.items() if key in rows_to_keep}

    # Convert target_dict to JSON
    target_json = json.dumps(target_dict)
    
    return json.loads(target_json)
