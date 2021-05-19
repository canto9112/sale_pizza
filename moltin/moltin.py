import requests
from pprint import pprint


def create_main_image(token, product_id, image_id):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {
                "type": "main_image",
                "id": image_id
    }}

    response = requests.post(f'https://api.moltin.com/v2/products/{product_id}/relationships/main-image',
                             headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def get_file_id(token, file_name, file_url):
    response = requests.get(file_url)
    response.raise_for_status()

    with open(f'{file_name}.jpg', 'wb') as file:
        file.write(response.content)

    headers = {
        'Authorization': f'Bearer {token}'
    }
    files = {
        'public': True,
        'file': open(f'{file_name}.jpg', 'rb')

    }

    response = requests.post('https://api.moltin.com/v2/files', headers=headers, files=files)
    pprint(response.json())
    return response.json()['data']['id']


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