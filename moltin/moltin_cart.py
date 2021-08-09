import requests


def get_cart(token, cart_name):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_items(token, cart_name):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(f'https://api.moltin.com/v2/carts/{cart_name}/items', headers=headers)
    response.raise_for_status()
    return response.json()


def clean_cart(token, cart_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_id}/items', headers=headers)
    response.raise_for_status()


def add_product_to_cart(token, product_id, cart_name, quantity):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json',
               'X-MOLTIN-CURRENCY': 'RUB'}

    data = {'data': {'id': product_id,
                     'type': 'cart_item',
                     'quantity': int(quantity)}}

    response = requests.post(f'https://api.moltin.com/v2/carts/{cart_name}/items',
                             headers=headers,
                             json=data)
    response.raise_for_status()
    return response.json()


def delete_product_in_cart(token, cart_name, product_id):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(f'https://api.moltin.com/v2/carts/{cart_name}/items/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()