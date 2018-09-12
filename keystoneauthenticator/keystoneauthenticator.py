from jupyterhub.auth import Authenticator
from keystoneauth1 import session
from keystoneauth1.identity import v3
from tornado import gen
from traitlets import Unicode

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

        auth = v3.Password(auth_url=self.auth_url,
                           username=username,
                           password=password,
                           user_domain_name='default',
                           project_domain_name='default',
                           unscoped=True)
        sess = session.Session(auth=auth)

        if not sess.get_user_id():
            return None

        userdict = {'name': username}
        userdict['auth_state'] = auth_state = {}
        auth_state['auth_url'] = self.auth_url
        auth_state['os_token'] = sess.get_auth_headers()['X-Auth-Token']

        return userdict

    @gen.coroutine
    def pre_spawn_start(self, user, spawner):
        auth_state = yield user.get_auth_state()
        if not auth_state:
            # auth_state not enabled
            return
        spawner.environment['OS_AUTH_URL'] = auth_state['auth_url']
        spawner.environment['OS_TOKEN'] = auth_state['os_token']
