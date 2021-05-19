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