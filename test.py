import requests
import base64
import json
client_id = '8ba80dca073b4e34b02623d29e1dba58'
client_secret = 'ae0b13267a5b4bf0a0eb243086f98c47'
headers = {'Authorization': 'Basic ' + (base64.b64encode((client_id + ':' + client_secret).encode())).decode()}
data = {'grant_type': 'client_credentials'}
resp0 = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers)
resp = json.loads(resp0.content.decode())
# token = resp0['access_token']