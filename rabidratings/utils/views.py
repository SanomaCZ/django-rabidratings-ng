import json
from django.http import HttpResponse


def HttpResponseJson(data, status_code=None, *args, **kwargs):
    response = HttpResponse(json.dumps(data), content_type='application/json', *args, **kwargs)
    if status_code is not None:
        response.status_code = status_code
    return response
