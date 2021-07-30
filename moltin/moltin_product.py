import requests


def create_product(token, name, slug, sku, description, currency, amount):
    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}

    data = {'data': {'type': 'product',
                     'name': name,
                     'slug': slug,
                     'sku': sku,
                     'description': description,
                     'manage_stock': False,
                     'price':
                     [
                         {
                             'amount': amount,
                             'currency': currency,
                             'includes_tax': True
                         }
                     ],
                     'status': 'live',
                     'commodity_type': "physical"}}

    response = requests.post('https://api.moltin.com/v2/products', headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']['id']


def get_product(token, product_id):
    headers = {
        'Authorization': f'Bearer {token}',
    }

    response = requests.get(f'https://api.moltin.com/v2/products/{product_id}', headers=headers)
    response.raise_for_status()
    return response.json()


def get_all_products(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()
    response = response.json()
    return response['data']
