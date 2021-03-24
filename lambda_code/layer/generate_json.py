import json
import random
import string
import uuid

NO_OF_OBJECTS = 10 * 1000

with open('make_models.json', 'r') as model_fh:
    MAKE_MODEL_DICT = json.load(model_fh)

with open('countries.json', 'r') as country_fh:
    COUNTRY_LIST = json.load(country_fh)

def generate_json():
    json_dict = {}
    for _ in range(0, NO_OF_OBJECTS):
        random_unique_id = str(uuid.uuid4())
        make, model = get_random_make_model()
        json_dict[random_unique_id] = {
            'make': make,
            'model': model,
            'license_plate': generate_license_plate(),
            'origin': {
                'country': random.choice(COUNTRY_LIST),
                'year': random.randrange(1980, 2020)
            }
        }

    with open(f'test_data_{NO_OF_OBJECTS}.json', 'w+') as file_handler:
        json.dump(json_dict, file_handler, indent=4)

def get_random_make_model():
    random_make_model = random.choice(MAKE_MODEL_DICT)
    return random_make_model.get('make'), random_make_model.get('model')

def generate_license_plate():
    """Generate a license plate like XX-123-X or X-123-XX."""
    format_type_long_first = bool(random.getrandbits(1))
    if format_type_long_first:
        first_len = 2
        last_len = 1
    else:
        first_len = 1
        last_len = 2

    first_chars = ''.join(random.choices(string.ascii_uppercase, k=first_len))
    numbers = random.randrange(0, 1000)
    last_chars = ''.join(random.choices(string.ascii_uppercase, k=last_len))

    return f'{first_chars}-{numbers:03d}-{last_chars}'

if __name__ == '__main__':
    generate_json()
