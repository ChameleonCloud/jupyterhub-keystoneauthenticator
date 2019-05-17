from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.identity import v3
from traceback import format_exc

class Client():
    def __init__(auth_url, username=None, password=None, token=None):
        self.auth_url = auth_url

        if token is not None:
            auth = v3.Token(auth_url=self.auth_url, token=token)
        else if (username is not None and password is not None):
            auth = v3.Password(auth_url=self.auth_url,
                                    username=username,
                                    password=password,
                                    user_domain_name='default',
                                    unscoped=True)
        else:
            raise ValueError(
                'Must provide either auth_state or username/password')

        self.session = session.Session(auth=auth)

    def get_token(self):
        try:
            token = self.session.get_auth_headers()['X-Auth-Token']
        except Unauthorized:
            token = None

        return token

    def get_projects(self):
        try:
            project_response = sess.get('{}/auth/projects'.format(self.auth_url))
            projects = project_response.json()['projects']
            projects = [p for p in projects if p['enabled'] and p['name'] != 'openstack']
        except Exception as exc:
            self.log.error('Failed to get project list for user {}'.format(username))
            self.log.debug(format_exc())
            projects = []

        return projects
