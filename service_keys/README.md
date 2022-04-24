
# Service keys

The OAuth protocol needs client ID and client SECRET that can not be shared via GitHub.
This folder contains the files needed by each service that Replica uses.

Please add your own application keys there :

- ~/service_keys/google_auth.json
- ~/service_keys/strava_auth.json

In each file, put this :

``` json
{
  "client_id": "your client id key here",
  "client_secret": "your client secret key here"
}
```
