import time

import requests

auth_data = None
token = None


def check_token(token_data):
    now = int(time.time())
    token_expires = token_data['expires']
    return now < token_expires


def get_authorization_token(client_id, client_secret):
    global token
    global auth_data

    if not token or not check_token(auth_data):
        auth_data = get_token_data(client_id, client_secret)
        token = auth_data['access_token']
    return token


def get_token_data(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()
    return response.json()