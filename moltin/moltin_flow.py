import requests
from pprint import pprint


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
    pprint(response.json())
    response.raise_for_status()
    flow_id = response.json()['data']['id']
    flow_slug = response.json()['data']['slug']
    return flow_id, flow_slug


def get_flow_id(token):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "flow",
                "name": 'Pizzeria',
                "slug": 'pizzerias',
                'description': 'Описание',
                'enabled': True
    }}

    response = requests.post('https://api.moltin.com/v2/flows', headers=headers, json=data)
    response.raise_for_status()
    flow_id = response.json()['data']['id']
    flow_slug = response.json()['data']['slug']
    return flow_id, flow_slug


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


def create_entry(token, flow_slug, address, alias, lat, lon):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}
    data = {"data": {
        "type": "entry",
        "address": address,
        "alias": alias,
        "longitude": lon,
        "latitude": lat
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
    return response.json()['data']['id']


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
    lat = response.json()['data']['latitude']
    lon = response.json()['data']['longitude']
    return lat, lon


