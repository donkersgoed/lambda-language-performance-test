import hashlib
import json
import time

def lambda_handler(_event, _context):
    start_time = time.time()

    # Load the file from JSON into memory
    with open('/opt/test_data.json', 'r') as file_handle:
        test_data = json.load(file_handle)

    filtered_list = []
    # For every item, check its license plate. If it has an 'A' in the first
    # section and a 0 in the second section, add it to the list. For example
    # 'AT-001-B' matches, but 'A-924-VW' doesn't.
    for obj in test_data.values():
        license_plate_components = obj['license_plate'].split('-')
        if 'A' in license_plate_components[0] or '0' in license_plate_components[1]:
            # If the license plate matches, add a new field 'make_model_hash'
            # to the object. This field contains the sha256 hash of the make and model.
            obj['make_model_hash'] = hashlib.sha256(
                f"{obj['make']}{obj['model']}".encode()
            ).hexdigest()
            # Add it to the results list
            filtered_list.append(obj)

    # Sort the list on license plate
    sorted_list = sorted(filtered_list, key=lambda k: k['license_plate'])
    # Convert it to a JSON string
    sorted_list_json = json.dumps(sorted_list)
    # Calculate the hash of that JSON string
    result_hash = hashlib.sha256(sorted_list_json.encode()).hexdigest()

    end_time = time.time()
    duration = int((end_time - start_time) * 1000)
    print(
        f'Filtered {len(sorted_list)} from {len(test_data)} source items. '
        f'Result hash: {result_hash}. Duration: {duration} ms.'
    )