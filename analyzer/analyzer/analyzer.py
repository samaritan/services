import logging

logger = logging.getLogger(__name__)


def analyze(name, path, codedx):
    if codedx.exists(name):
        codedx.delete_project(name)
    project = codedx.create_project(name)
    analysis = codedx.prepare_analysis(project)
    if analysis is None:
        raise Exception(f'Analysis preparation for {name} failed')
    if not codedx.upload(path, analysis):
        raise Exception(f'Upload of {path} for {name} failed')
    job = codedx.start_analysis(analysis)
    if not job:
        raise Exception(f'Analysis {analysis.prepId} failed')
    return job.jobId
