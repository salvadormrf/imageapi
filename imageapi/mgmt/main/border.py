import urllib2
import logging

from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseBadRequest

from api.core import ImageAPI


BORDER_PADDING = 4
BORDER_FILL_COLOR = "white"
BORDER_SIZE = 1
BORDER_COLOR = "#ccc"

logger = logging.getLogger(__name__)

@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def default(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    # instantiate new API
    api = ImageAPI()
    
    try:
        api.open_from_internet(url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    padding_size = request.GET.get("bp", BORDER_PADDING)
    border_size = request.GET.get("bs", BORDER_SIZE)
    fill_color = request.GET.get("bfc", BORDER_FILL_COLOR)
    border_color = request.GET.get("bc", BORDER_COLOR)
    
    # apply border with default values
    api.apply_border(int(padding_size), int(border_size), fill_color, border_color)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response

