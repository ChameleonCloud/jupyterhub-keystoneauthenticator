from .keystoneauthenticator import KeystoneAuthenticator

import getpass
import os

k = KeystoneAuthenticator()
k.auth_url = os.getenv('OS_AUTH_URL', 'https://keystone.example.com:5000/v3')
username = input('Username: ')
passwd = getpass.getpass()
data = dict(username=username, password=passwd)
rs = k.authenticate(None, data)

print(rs.result())
