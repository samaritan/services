import os
import logging
import time

import requests

from box import Box
from nameko.extensions import DependencyProvider

logger = logging.getLogger(__name__)

CODEDX_URL_KEY = 'CODEDX_URL'
CODEDX_INTERVAL_KEY = 'CODEDX_INTERVAL'
CODEDX_KEY_KEY = 'CODEDX_KEY'


class CodeDx(DependencyProvider):
    def get_dependency(self, worker_ctx):
        url = self.container.config[CODEDX_URL_KEY]
        key = self.container.config[CODEDX_KEY_KEY]
        interval = self.container.config[CODEDX_INTERVAL_KEY]
        return _CodeDx(url, key, interval)


class _CodeDx:
    def __init__(self, url, key, interval=15):
        self.url = url if url.endswith('/') else f'{url}/'
        self.headers = {'API-Key': key}
        self.interval = interval

    def analyze(self, analysis):
        uri = f'/x/analysis-prep/{analysis.prepId}/analyze'

        response = self._post(uri)
        if response is not None:
            job_id = Box(response).jobId

            done = False
            while not done:
                job = self.get_job(job_id)
                if job.status == 'completed':
                    done = True
                time.sleep(self.interval)
            return True
        return False

    def create_project(self, name):
        if self.exists(name):
            raise Exception(f'Project {name} already exists')

        uri = 'api/projects'
        json = {'name': name}

        if self._put(uri, json):
            return self.get_project(name)
        return None

    def delete_project(self, name):
        project = self.get_project(name)
        if project is None:
            raise Exception(f'No project {name} to delete')

        uri = 'api/projects/{}'.format(project.get('id'))
        return self._delete(uri)

    def exists(self, name):
        return self.get_project(name) is not None

    def get_analysis(self, identifier):
        uri = f'api/analysis-prep/{identifier}'
        return Box(self._get(uri))

    def get_job(self, identifier):
        uri = f'api/jobs/{identifier}'
        return Box(self._get(uri))

    def get_num_findings(self, project):
        uri = 'x/projects/{}/findings/count'.format(project.id)
        json = {'filter': {}}

        return self._post(uri, json=json).get('count')

    def get_findings(self, project):
        findings = None

        num_findings = self.get_num_findings(project)
        if num_findings == 0:
            return findings

        findings = list()
        page, size, index = 1, 2500, 0
        while index < num_findings:
            uri = 'x/projects/{}/findings/table?expand=descriptor'.format(
                project.id
            )
            json = {
                'filter': {}, 'sort': {'by': 'id', 'direction': 'ascending'},
                'pagination': {'page': page, 'perPage': size}
            }
            for finding in self._post(uri, json=json):
                findings.append(Box(finding))

            page += 1
            index += size

        return findings

    def get_project(self, name):
        for project in self.get_projects():
            if project.name == name:
                return project
        return None

    def get_projects(self):
        projects = list()

        for project in self._get('api/projects').get('projects'):
            projects.append(Box(project))

        return projects

    def prepare_analysis(self, project):
        uri = 'x/analysis-prep'
        json = {'projectId': project.id}

        return Box(self._post(uri, json=json))

    def start_analysis(self, analysis):
        uri = f'/x/analysis-prep/{analysis.prepId}/analyze'

        return Box(self._post(uri))

    def upload(self, filepath, analysis):
        uri = 'x/analysis-prep/{}/upload'.format(analysis.prepId)

        with open(filepath, 'rb') as file:
            name = os.path.basename(filepath)
            content_type = 'multipart/form-data'

            files = {'file': (name, file, content_type)}
            response = self._post(uri, files=files)
            if response is not None:
                job_id = Box(response).jobId

                done = False
                while not done:
                    job = self.get_job(job_id)
                    if job.status == 'completed':
                        done = True
                    time.sleep(self.interval)
            return True
        return False

    def _delete(self, uri):
        try:
            url = self.url + uri
            logger.debug('DEL %s', url)
            _ = requests.delete(url, headers=self.headers)
        except requests.exceptions.RequestException as exception:
            logger.info('Failed to get response from Code Dx service')
            logger.error(exception, exc_info=True)
            return False
        return True

    def _get(self, uri, params=None):
        response = None
        try:
            url = self.url + uri
            logger.debug('GET %s', url)
            response = requests.get(url, headers=self.headers, params=params)
        except requests.exceptions.RequestException as exception:
            logger.info('Failed to get response from Code Dx service')
            logger.error(exception, exc_info=True)
        return response.json() if response is not None else None

    def _post(self, uri, json=None, files=None):
        response = None
        try:
            url = self.url + uri
            logger.debug('POST %s', url)
            response = requests.post(
                url, headers=self.headers, json=json, files=files
            )
        except requests.exceptions.RequestException as exception:
            logger.info('Failed to get response from Code Dx service')
            logger.error(exception, exc_info=True)
        return response.json() if response is not None else None

    def _put(self, uri, json=None):
        try:
            url = self.url + uri
            logger.debug('PUT %s', url)
            _ = requests.put(url, headers=self.headers, json=json)
        except requests.exceptions.RequestException as exception:
            logger.info('Failed to get response from Code Dx service')
            logger.error(exception, exc_info=True)
            return False
        return True
