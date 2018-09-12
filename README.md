# keystoneauthenticator

Keystone Authenticator Plugin for JupyterHub

## Usage ##

You can enable this authenticator with the following lines in your
`jupyter_config.py`:

```python
c.JupyterHub.authenticator_class = 'keystoneauthenticator.KeystoneAuthenticator'
```

### Required configuration ###

At minimum, the following two configuration options must be set before
the LDAP Authenticator can be used:

#### `KeystoneAuthenticator.auth_url` ####

### Optional configuration ###

#### `KeystoneAuthenticator.api_version` ####

#### `KeystoneAuthenticator.region_name` ####
