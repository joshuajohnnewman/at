def ok(status=201):
    """
    Produces a standard empty response
    :param status: status code to return
    :return: tuple containing response dictionary and status code
    """
    return {'status': 'ok'}, status


def abort(status, message=None):
    from flask_restful import abort as flask_abort
    flask_abort(status, errors=[message])
