#!/usr/bin/env python

import requests
import json

#openssl x509 -x509toreq -in certificate.crt -out CSR.csr -signkey privateKey.key

HOME = os.getenv("HOME")
with open(f"{HOME}/pass_info.json","r") as f:
    pass_info = json.load(f)

payload = f'username={pass_info["betfair"]["username"]}&password={pass_info["betfair"]["password"]}'
headers = {'X-Application': 'BOT0', 'Content-Type': 'application/x-www-form-urlencoded'}

resp = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=payload, cert=('client-2048.pem'), headers=headers)

if resp.status_code == 200:
  resp_json = resp.json()
  print(resp_json['loginStatus'])
  print(resp_json['sessionToken'])
else:
  print("Request failed.")
