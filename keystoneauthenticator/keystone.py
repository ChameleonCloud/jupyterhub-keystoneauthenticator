import logging

from keystoneauth1 import session
from keystoneauth1.exceptions.http import Unauthorized
from keystoneauth1.identity import v3
from traceback import format_exc

class Client():
    def __init__(self, auth_url, username=None, password=None,
                 token=None, user_domain_id='default', log=None):
        self.auth_url = auth_url

        if log is not None:
            self.log = log
        else:
            self.log = logging.getLogger(__name__)

        if token is not None:
            auth = v3.Token(auth_url=self.auth_url, token=token, unscoped=True)
        elif (username is not None and password is not None):
            auth = v3.Password(auth_url=self.auth_url,
                               username=username,
                               password=password,
                               user_domain_id=user_domain_id,
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
            project_response = (
                self.session.get('{}/auth/projects'.format(self.auth_url)))
            projects = project_response.json()['projects']
            projects = [p for p in projects if p['enabled'] and p['name'] != 'openstack']
        except Exception:
            self.log.error('Failed to get project list')
            self.log.debug(format_exc())
            projects = []

        return projects

    def get_project_domain(self, project):
        try:
            # Need to make scoped request in order to get the domain associated
            # with the requested project
            domain_auth = v3.Token(auth_url=self.auth_url,
                                   token=self.get_token(),
                                   project_id=project['id'])
            domain_session = session.Session(auth=domain_auth)
            domain_response = (
                domain_session.get(
                    '{}/domains/{}'.format(self.auth_url,
                                           project['domain_id'])))
            domain = domain_response.json()['domain']
        except Exception:
            self.log.error(
                'Failed to lookup domain for project={}'.format(project['id']))
            self.log.debug(format_exc())
            domain = None

        return domain
