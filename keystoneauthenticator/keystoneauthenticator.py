from jupyterhub.auth import Authenticator
from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.identity import v3
from tornado import gen
from traceback import format_exc
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
                           unscoped=True)
        sess = session.Session(auth=auth)

        try:
            token = sess.get_auth_headers()['X-Auth-Token']
        except Unauthorized:
            return None

        try:
            project_response = sess.get('{}/auth/projects'.format(self.auth_url))
            projects = project_response.json()['projects']
            projects = [p for p in projects if p['enabled'] and p['name'] != 'openstack']
        except Exception as exc:
            self.log.error('Failed to get project list for user {}'.format(username))
            self.log.debug(format_exc())
            projects = []

        userdict = {'name': username}
        userdict['auth_state'] = auth_state = {}
        auth_state['auth_url'] = self.auth_url
        auth_state['os_token'] = token

        if projects:
            auth_state['project_name'] = projects[0]['name']
        else:
            self.log.warn('Could not select default project for user {}'.format(username))

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
