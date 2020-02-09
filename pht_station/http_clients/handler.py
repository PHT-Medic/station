import types
import werkzeug

_EXCEPTIONS = types.MappingProxyType({
    400: werkzeug.exceptions.BadRequest,
    404: werkzeug.exceptions.NotFound,
    409: werkzeug.exceptions.Conflict
})


def raise_for_status(response):
    exception = _EXCEPTIONS.get(response.status_code)
    if exception:
        raise exception(response)
    return response
