import requests


def get_image_url(token, file_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


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