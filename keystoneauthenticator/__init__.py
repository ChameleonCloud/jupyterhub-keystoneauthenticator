from jupyterhub.auth import Authenticator
from tornado import gen
from traitlets import Unicode

from .keystone import Client

class KeystoneAuthenticator(Authenticator):
    auth_url = Unicode(
        config=True,
        help="""
        Keystone server auth url
        """
    )

    api_version = Unicode(
        '3',
        config=True,
        help="""
        Keystone authentication version
        """
    )

    region_name = Unicode(
        config=True,
        help="""
        Keystone authentication region name
        """
    )

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        client = self._create_client(username=username, password=password)
        token = client.get_token()

        if token is None:
            return None

        auth_state = {}
        openstack_rc = {
            'OS_AUTH_URL': self.auth_url,
            'OS_INTERFACE': 'public',
            'OS_IDENTITY_API_VERSION': self.api_version,
            'OS_AUTH_TYPE': 'token',
            'OS_TOKEN': token,
        }

        if self.region_name:
            openstack_rc['OS_REGION_NAME'] = self.region_name

        projects = client.get_projects()

        if projects:
            default_project = projects[0]
            openstack_rc['OS_PROJECT_NAME'] = default_project['name']
            openstack_rc['OS_PROJECT_DOMAIN_ID'] = default_project['domain_id']
            domain = client.get_project_domain(default_project)
            if domain:
                openstack_rc['OS_PROJECT_DOMAIN_NAME'] = domain['name']
        else:
            self.log.warn(
                ('Could not select default project for user %r, '
                 'no projects found'), username)

        auth_state['openstack_rc'] = openstack_rc

        return dict(
            name=username,
            auth_state=auth_state,
        )

    @gen.coroutine
    def refresh_user(self, user, handler=None):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return True

        try:
            openstack_rc = auth_state.get('openstack_rc', {})
            token = openstack_rc.get('OS_TOKEN')

            if not token:
                self.log.warning((
                    'Could not get OpenStack token from auth_state'))
                return True

            client = self._create_client(token=token)

            # If we can generate a new token, it means ours is still valid.
            # There is no value in storing the new token, as its expiration will
            # be tied to the requesting token's expiration.
            return client.get_token() is not None
        except Exception as err:
            self.log.warning((
                f'Failed to refresh OpenStack token in pre_spawn: {err}'))
            return True

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        """Fill in OpenRC environment variables from user auth state.
        """
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            self.log.error((
                'auth_state is not enabled! Cannot set OpenStack RC '
                'parameters'))
            return
        for rc_key, rc_value in auth_state.get('openstack_rc', {}).items():
            spawner.environment[rc_key] = rc_value

    def _create_client(self, **kwargs):
        return Client(self.auth_url, log=self.log, **kwargs)
