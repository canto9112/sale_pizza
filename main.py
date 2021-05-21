import json
import os
import shutil

from environs import Env
from slugify import slugify

import moltin.moltin_file
import moltin.moltin_flow
from moltin.moltin_authentication import get_authorization_token
from moltin.moltin_product import get_product_id


def get_json(json_file):
    with open(json_file, "r") as file:
        return json.load(file)


def create_field(token, flow_id):
    pizzeria_field = [{'name': 'Adress',
                       'slug': 'address',
                       'field_type': 'string',
                       'description': 'Адрес пиццерии'},
                      {'name': 'Alias',
                       'slug': 'alias',
                       'field_type': 'string',
                       'description': 'Название пиццерии'},
                      {'name': 'Longitude',
                       'slug': 'longitude',
                       'field_type': 'float',
                       'description': 'Долгода пиццерии'},
                      {'name': 'Latitude',
                       'slug': 'latitude',
                       'field_type': 'float',
                       'description': 'Широта пиццерии'}]
    for field in pizzeria_field:
        moltin.moltin_flow.create_fields(token, field['name'], field['slug'], field['field_type'], field['description'], flow_id)


def add_product(token, name_folder):
    pizzas = get_json('json/menu.json')
    for pizza in pizzas:
        name = pizza['name']
        slug = slugify(name)
        sku = str(pizza['id'])
        description = pizza['description']
        currency = 'RUB'
        amount = pizza['price']
        image_url = pizza['product_image']['url']
        product_id = get_product_id(token, name, slug, sku, description, currency, amount)
        image_id = moltin.moltin_file.get_file_id(token, slug, image_url, name_folder)
        moltin.moltin_file.create_main_image(token, product_id, image_id)


def add_entrys(token, flow_slug):
    addresses = get_json('json/addresses.json')
    for address_pizzeria in addresses:
        address = address_pizzeria['address']['full']
        alias = address_pizzeria['alias']
        lat = address_pizzeria['coordinates']['lat']
        lon = address_pizzeria['coordinates']['lon']
        moltin.moltin_flow.create_entry(token, flow_slug, address, alias, lat, lon)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    images_folder = 'images'
    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_access_token = get_authorization_token(moltin_client_id, moltin_client_secret)
    add_product(moltin_access_token, images_folder)

    flow_id, flow_slug = moltin.moltin_flow.get_flow_id(moltin_access_token)
    create_field(moltin_access_token, flow_id)
    add_entrys(moltin_access_token, flow_slug)

    # delete images
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), images_folder)
    shutil.rmtree(path)