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

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        password = data['password']

        client = self._create_client(username=username, password=password)
        token = client.get_token()
        projects = client.get_projects()

        userdict = {'name': username}
        userdict['auth_state'] = auth_state = {}
        auth_state['auth_url'] = self.auth_url
        auth_state['os_token'] = token

        if projects:
            auth_state['project_name'] = projects[0]['name']
        else:
            self.log.warn(
                ('Could not select default project for user %r, '
                 'no projects found'), username)

        return userdict

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return
        spawner.environment['OS_AUTH_URL'] = auth_state['auth_url']
        spawner.environment['OS_TOKEN'] = auth_state['os_token']
        spawner.environment['OS_AUTH_TYPE'] = 'token'
        spawner.environment['OS_IDENTITY_API_VERSION'] = '3'

        project_name = auth_state.get('project_name')
        if project_name:
            spawner.environment['OS_PROJECT_NAME'] = project_name

    @gen.coroutine
    def refresh_user(self, user, handler=None):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return True

        token = auth_state['os_token']
        client = self._create_client(token=token)

        # If we can generate a new token, it means ours is still valid.
        # There is no value in storing the new token, as its expiration will
        # be tied to the requesting token's expiration.
        return client.get_token() is not None

    def _create_client(self, **kwargs):
        return Client(self.auth_url, log=self.log, **kwargs)
