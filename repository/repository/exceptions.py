from nameko.exceptions import registry

def remote_error(exception_path):
    def wrapper(exception_type):
        registry[exception_path] = exception_type
        return exception_type
    return wrapper


@remote_error('project.exceptions.NotFound')
class ProjectNotFound(Exception):
    pass


class NotCloned(Exception):
    pass


class CommitNotFound(Exception):
    pass
