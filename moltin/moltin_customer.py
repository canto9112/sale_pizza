import requests


def create_customer(token, name, email):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "customer",
                "name": name,
                "email": email}}

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=data)
    response.raise_for_status()
    return response.json()