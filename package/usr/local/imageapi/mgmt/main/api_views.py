import logging

from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def api_dispatcher(request, **kwargs):
    
    # TODO error handling
    version = int(kwargs["version"])
    module_str = kwargs["module"]
    method_str = kwargs["method"]
    format_str = kwargs["format"]
    
    if format_str:
        # http://localhost:8080/api/v1/face/faces.json maps to face.faces_json
        method_str = "%s_%s" % (method_str, format_str)
    
    try:
        # dymanically load module
        module = __import__(module_str, globals(), locals())
        # get method handler
        m = getattr(module, method_str)
    except:
        logger.exception("Problem occurred")
        return HttpResponseBadRequest("BAD REQUEST")
    
    return m(request)



























































