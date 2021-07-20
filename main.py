import os

import requests
from environs import Env
from geopy import distance
from slugify import slugify

import json
import moltin.moltin_file
import moltin.moltin_flow
from moltin.moltin_authentication import get_authorization_token
from moltin.moltin_product import get_product_id


def get_json(json_file):
    with open(json_file, "r") as file:
        return json.load(file)


def save_image(file_name, file_url, folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    response = requests.get(file_url)
    response.raise_for_status()

    with open(f'{folder_name}/{file_name}.jpg', 'wb') as file:
        file.write(response.content)


def create_pizzerias_field(token, flow_id):
    pizzeria_field = [{'name': 'Address',
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
                       'description': 'Широта пиццерии'},
                      {'name': 'Courier',
                       'slug': 'courier',
                       'field_type': 'integer',
                       'description': 'id курьера в телеграм'}
                      ]
    for field in pizzeria_field:
        moltin.moltin_flow.create_fields(token, field['name'], field['slug'], field['field_type'], field['description'], flow_id)


def create_customer_field(token, flow_id):
    pizzeria_field = [{'name': 'Address',
                       'slug': 'address',
                       'field_type': 'string',
                       'description': 'Адрес клиента'},
                      {'name': 'ID telegram',
                       'slug': 'id_telegram',
                       'field_type': 'string',
                       'description': 'ID telegram'},
                      {'name': 'Longitude',
                       'slug': 'longitude',
                       'field_type': 'float',
                       'description': 'Долгода адреса'},
                      {'name': 'Latitude',
                       'slug': 'latitude',
                       'field_type': 'float',
                       'description': 'Широта адреса'}]
    for field in pizzeria_field:
        moltin.moltin_flow.create_fields(token, field['name'], field['slug'], field['field_type'], field['description'], flow_id)


def add_customer(token, flow_slug):
    moltin.moltin_flow.create_entry(token, flow_slug, 'address', 'id_telegram', 1.0, 2.0)


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
        save_image(slug, image_url, name_folder)
        image_id = moltin.moltin_file.get_file_id(token, slug, name_folder)
        moltin.moltin_file.create_main_image(token, product_id, image_id)


def add_entries(token, flow_slug):
    addresses = get_json('json/addresses.json')
    for address_pizzeria in addresses:
        address = address_pizzeria['address']['full']
        alias = address_pizzeria['alias']
        lat = address_pizzeria['coordinates']['lat']
        lon = address_pizzeria['coordinates']['lon']
        moltin.moltin_flow.create_entry(token, flow_slug, address, alias, lat, lon, 335031317)


def get_distation(lat_pizzeria, lon_pizzeria, lat_user, lon_user):
    newport_ri = (lat_pizzeria, lon_pizzeria)
    slantsy = (59.11779, 28.088145)
    distance_user = distance.distance(newport_ri, slantsy).m
    return distance_user


if __name__ == '__main__':
    env = Env()
    env.read_env()

    images_folder = 'images'

    moltin_client_id = env('MOLTIN_CLIENT_ID')
    moltin_client_secret = env('MOLTIN_CLIENT_SECRET')
    moltin_access_token = get_authorization_token(moltin_client_id, moltin_client_secret)

    pizzerias_flow_name = 'Pizzerias'
    pizzerias_flow_slug = 'Pizzerias_flow'
    pizzerias_flow_description = 'Пиццерии'

    customer_flow_name = 'Customer'
    customer_flow_slug = 'Customer_flow'
    customer_flow_description = 'Покупатель'

    pizzerias_flow_id = moltin.moltin_flow.create_flow(moltin_access_token,
                                                       pizzerias_flow_name,
                                                       pizzerias_flow_slug,
                                                       pizzerias_flow_description)

    customer_flow_id = moltin.moltin_flow.create_flow(moltin_access_token,
                                                      customer_flow_name,
                                                      customer_flow_slug,
                                                      customer_flow_description)

    create_pizzerias_field(moltin_access_token, pizzerias_flow_id)
    create_customer_field(moltin_access_token, customer_flow_id)
    add_entries(moltin_access_token, pizzerias_flow_slug)
    # customer = moltin.moltin_flow.create_customer(moltin_access_token, 'pizzerias', 'address2', '123', 1.0, 2.0)
    # pprint(customer)
    # all_entries = moltin.moltin_flow.get_all_entries(moltin_access_token, 'pizzerias')
    #
    # print(min(all_pizzerias, key=get_pizzerias_distance))
    #
    #
    # add_product(moltin_access_token, images_folder)
    # flow_id, flow_slug = moltin.moltin_flow.get_flow_id(moltin_access_token)
    # create_field(moltin_access_token, flow_id)


    # # delete images
    # path = os.path.join(os.path.abspath(os.path.dirname(__file__)), images_folder)
    # shutil.rmtree(path)