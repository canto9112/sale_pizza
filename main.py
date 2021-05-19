import json
from environs import Env
from slugify import slugify

from pprint import pprint
from moltin.moltin_authentication import get_authorization_token
from moltin.moltin_product import crate_product


def get_json(json_file):
    with open(json_file, "r") as file:
        return json.load(file)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    addresses = 'menu.json'

    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_access_token = get_authorization_token(moltin_client_id, moltin_client_secret)

    pizzas = get_json('json/menu.json')
    for pizza in pizzas:
        pprint(pizza)
        name = pizza['name']
        slug = slugify(name)
        sku = str(pizza['id'])
        description = pizza['description']
        currency = 'RUB'
        amount = pizza['price']
        print(slug, sku, description, currency, amount)
        crate_product(moltin_access_token, name, slug, sku, description, currency, amount)
        break