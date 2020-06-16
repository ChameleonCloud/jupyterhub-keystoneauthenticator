# keystoneauthenticator

Keystone Authenticator Plugin for JupyterHub

## Usage ##

You can enable this authenticator with the following lines in your
`jupyter_config.py`:

```python
c.JupyterHub.authenticator_class = 'keystone'
```

Users will then be able to log in to JupyterHub with their Keystone username
and password. Additionally, a set of OpenStack RC parameters will be included
in the spawned Notebook server environment, allowing the user to e.g. use CLI
tools or other OpenStack APIs. This is currently done with an unscoped token,
using the 'token' authentication method.

### Required configuration ###

At minimum, the following two configuration options must be set before
the Keystone authenticator can be used:

#### `KeystoneAuthenticator.auth_url` ####

The absolute URL to the Keystone server that will perform the authentication.

### Optional configuration ###

#### `KeystoneAuthenticator.api_version` ####

The Keystone API version to use (uses v3 by default).

#### `KeystoneAuthenticator.region_name` ####

An optional region name to include in the RC parameters, to allow setting a
default region for the user.
