import requests
from flask import session
from backend.config import config

def get_authorization_url(state):
    params = {
        'client_id': config.OAUTH_CLIENT_ID,
        'redirect_uri': config.OAUTH_REDIRECT_URI,
        'response_type': 'code',
        'state': state
    }
    url = f"{config.OAUTH_AUTHORIZE_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return url

def exchange_code_for_token(code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.OAUTH_REDIRECT_URI,
        'client_id': config.OAUTH_CLIENT_ID,
        'client_secret': config.OAUTH_CLIENT_SECRET
    }
    response = requests.post(config.OAUTH_TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(config.OAUTH_USERINFO_URL, headers=headers)
    response.raise_for_status()
    return response.json()
