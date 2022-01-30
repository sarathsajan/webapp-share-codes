from oauthlib.oauth2 import WebApplicationClient
import requests
import json


from env_vars.env_vars import ENV_VARS
ENV_VARIABLES = ENV_VARS()

# Configuration
GOOGLE_CLIENT_ID = ENV_VARIABLES["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = ENV_VARIABLES["GOOGLE_CLIENT_SECRET"]
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def login_with_google(request):
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return request_uri

def start_google_authentication(request, code):
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(token_endpoint, authorization_response=request.url, redirect_url=request.base_url, code=code)
    token_response = requests.post(token_url, headers=headers, data=body, auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET))

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        user_data = {
            'unique_id': userinfo_response.json()["sub"],
            'users_email': userinfo_response.json()["email"],
            'picture': userinfo_response.json()["picture"],
            'users_name': userinfo_response.json()["given_name"],
            'msg': True
        }
        return user_data

    else:
        user_data = {'msg': False}
        return user_data