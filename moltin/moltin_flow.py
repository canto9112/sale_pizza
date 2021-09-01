import requests


def create_flow(token, name, slug, descriptions):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "flow",
                "name": name,
                "slug": slug,
                'description': descriptions,
                'enabled': True
    }}

    response = requests.post('https://api.moltin.com/v2/flows', headers=headers, json=data)
    response.raise_for_status()
    flow_id = response.json()['data']['id']
    return flow_id


def create_fields(token, name, slug, field_type, description,  flow_id):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "field",
                "name": name,
                "slug": slug,
                'field_type': field_type,
                'description': description,
                'required': True,
                'enabled': True,
                'relationships': {
                    'flow': {
                        'data': {
                            "type": "flow",
                            "id": flow_id
                        }
                    }
                }
    }}

    response = requests.post('https://api.moltin.com/v2/fields', headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def create_entry(token, flow_slug, address, alias, lat, lon, courier_id):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}
    data = {"data": {
        "type": "entry",
        "address": address,
        "alias": alias,
        "longitude": lon,
        "latitude": lat,
        "courier": courier_id
    }}

    response = requests.post(f'https://api.moltin.com/v2/flows/{flow_slug}/entries', headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def create_customer(token, flow_slug, address, alias, lat, lon):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}
    data = {"data": {
        "type": "entry",
        "address": address,
        "id_telegram": alias,
        "longitude": lon,
        "latitude": lat
    }}

    response = requests.post(f'https://api.moltin.com/v2/flows/{flow_slug}/entries', headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_all_entries(token, flow_slug):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    response = requests.get(f'https://api.moltin.com/v2/flows/{flow_slug}/entries', headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_entry(token, flow_slug, entry_id):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    response = requests.get(f'https://api.moltin.com/v2/flows/{flow_slug}/entries/{entry_id}', headers=headers)
    response.raise_for_status()
    coordinates = response.json()
    lat = coordinates['data']['latitude']
    lon = coordinates['data']['longitude']
    return lat, lon
