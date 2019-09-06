import eventlet

from .models import Churn, LineChurn


def _combine(deltas):
    data = dict()

    items = ((d.commit, p, dd) for d in deltas for (p, dd) in d.deltas.items())
    for (commit, path, delta) in items:
        data[(commit, path)] = {'delta': delta}

    return data


def _get_churn(commit, path, data):
    line = _get_linechurn(data['delta'])
    function = None
    return Churn(commit, path, line=line, function=function)


def _get_linechurn(delta):
    return LineChurn(insertions=delta.insertions, deletions=delta.insertions)


def get_churn(deltas):
    pool = eventlet.GreenPool(100)
    arguments = ((c, p, d) for ((c, p), d) in _combine(deltas).items())
    for churn in pool.starmap(_get_churn, arguments):
        yield churn
