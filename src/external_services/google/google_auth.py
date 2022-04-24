import functools
import flask
from authlib.integrations.requests_client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from ..common import get_credentials, store_credentials, get_service_keys, AUTH_STATE_KEY, AUTH_TOKEN_KEY

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE = 'openid email profile https://www.googleapis.com/auth/calendar.readonly'

AUTH_REDIRECT_URI = "http://127.0.0.1:5000/google/auth"
BASE_URI = "http://127.0.0.1:5000"

SERVICE_NAME = "google_auth"

app = flask.Blueprint(SERVICE_NAME, __name__)


def is_logged_in():
    return True if AUTH_TOKEN_KEY in get_credentials(SERVICE_NAME).keys() else False


def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    oauth2_tokens = get_credentials(SERVICE_NAME)[AUTH_TOKEN_KEY]
    app_keys = get_service_keys(SERVICE_NAME)

    return google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=app_keys["client_id"],
                client_secret=app_keys["client_secret"],
                token_uri=ACCESS_TOKEN_URI)


def get_user_info():
    credentials = build_credentials()

    oauth2_client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)

    return oauth2_client.userinfo().get().execute()


def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = flask.make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)


@app.route('/google/login')
@no_cache
def login():
    app_keys = get_service_keys(SERVICE_NAME)
    session = OAuth2Session(app_keys["client_id"], app_keys["client_secret"],
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.create_authorization_url(AUTHORIZATION_URL)

    session_store = {AUTH_STATE_KEY: state}
    store_credentials(SERVICE_NAME, session_store)

    return flask.redirect(uri, code=302)


@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    app_keys = get_service_keys(SERVICE_NAME)
    req_state = flask.request.args.get('state', default=None, type=None)
    session_get = get_credentials(SERVICE_NAME)

    if req_state != session_get[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(app_keys["client_id"], app_keys["client_secret"],
                            scope=AUTHORIZATION_SCOPE,
                            state=session_get[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)

    oauth2_tokens = session.fetch_access_token(
                        ACCESS_TOKEN_URI,
                        authorization_response=flask.request.url)

    session_store = {AUTH_STATE_KEY: session_get[AUTH_STATE_KEY],
                     AUTH_TOKEN_KEY: oauth2_tokens}
    store_credentials(SERVICE_NAME, session_store)

    return flask.redirect(BASE_URI, code=302)


@app.route('/google/logout')
@no_cache
def logout():
    store_credentials(SERVICE_NAME, {})

    return flask.redirect(BASE_URI, code=302)
