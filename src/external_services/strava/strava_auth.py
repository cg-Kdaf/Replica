import functools
from http import client
import flask
from authlib.integrations.requests_client import OAuth2Session
from requests import request
from ..common import get_credentials, store_credentials, get_service_keys, AUTH_STATE_KEY, AUTH_TOKEN_KEY

ACCESS_TOKEN_URI = 'https://www.strava.com/oauth/token'
AUTHORIZATION_URL = 'https://www.strava.com/oauth/authorize'
LOGOUT_URL = 'https://www.strava.com/oauth/deauthorize'

AUTHORIZATION_SCOPE = 'activity:read_all'

AUTH_REDIRECT_URI = "http://127.0.0.1:5000/strava/auth"
BASE_URI = "http://127.0.0.1:5000"


SERVICE_NAME = "strava_auth"

app = flask.Blueprint(SERVICE_NAME, __name__)


def is_logged_in():
    return True if AUTH_TOKEN_KEY in get_credentials(SERVICE_NAME).keys() else False


def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    oauth2_tokens = get_credentials(SERVICE_NAME)[AUTH_TOKEN_KEY]

    return oauth2_tokens


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


@app.route('/strava/login')
@no_cache
def login():
    app_keys = get_service_keys(SERVICE_NAME)
    session = OAuth2Session(app_keys["client_id"], app_keys["client_secret"],
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)
    session_store = {AUTH_STATE_KEY: state}
    store_credentials(SERVICE_NAME, session_store)

    return flask.redirect(uri)


@app.route('/strava/auth')
@no_cache
def google_auth_redirect():
    app_keys = get_service_keys(SERVICE_NAME)
    req_state = flask.request.args.get('state', default=None, type=None)
    req_code = flask.request.args.get('code', default=None, type=None)
    session_get = get_credentials(SERVICE_NAME)

    if req_state != session_get[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(app_keys["client_id"], app_keys["client_secret"],
                            code=req_code)

    oauth2_tokens = session.fetch_access_token(ACCESS_TOKEN_URI,
                                               code=req_code,
                                               grant_type="authorization_code",
                                               client_id=app_keys["client_id"],
                                               client_secret=app_keys["client_secret"])

    session_store = {AUTH_STATE_KEY: session_get[AUTH_STATE_KEY],
                     AUTH_TOKEN_KEY: oauth2_tokens}
    store_credentials(SERVICE_NAME, session_store)

    return flask.redirect(BASE_URI)


@app.route('/strava/logout')
@no_cache
def logout():
    creds = build_credentials()
    request("POST", LOGOUT_URL, params=creds)
    store_credentials(SERVICE_NAME, {})

    return flask.redirect(BASE_URI)
