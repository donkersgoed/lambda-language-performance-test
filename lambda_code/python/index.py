import hashlib
import json
import os
import time

def lambda_handler(_event, _context):
    t1 = time.time()

    # Load the file from JSON into memory
    file_name = os.environ.get('TEST_DATA_FILE')
    with open(f'/opt/{file_name}', 'r') as file_handle:
        test_data = json.load(file_handle)
    print(f'JSON parsing took {int((time.time() - t1) * 1000)} ms')

    t2 = time.time()
    filtered_list = []
    # For every item, check its license plate. If it has an 'A' in the first
    # section and a 0 in the second section, add it to the list. For example
    # 'AT-001-B' matches, but 'A-924-VW' doesn't.
    for obj in test_data.values():
        license_plate_components = obj['license_plate'].split('-')
        if 'A' in license_plate_components[0] and '0' in license_plate_components[1]:
            # If the license plate matches, add a new field 'make_model_hash'
            # to the object. This field contains the sha256 hash of the make and model.
            obj['make_model_hash'] = hashlib.sha256(
                f"{obj['make']}{obj['model']}".encode()
            ).hexdigest().upper()

            # Add it to the results list
            filtered_list.append(obj)
    print(f'Object filtering took {int((time.time() - t2) * 1000)} ms')

    # Sort the list on license plate
    sorted_list = sorted(filtered_list, key=lambda k: k['license_plate'])
    # Convert it to a JSON string
    sorted_list_json = json.dumps(sorted_list, separators=(',', ':'))
    # Calculate the hash of that JSON string
    result_hash = hashlib.sha256(sorted_list_json.encode()).hexdigest().upper()

    duration = int((time.time() - t1) * 1000)
    print(
        f'Filtered {len(sorted_list)} from {len(test_data)} source items. '
        f'Result hash: {result_hash}. Duration: {duration} ms.'
    )
