from django.views.decorators.http import require_GET
from django.http import HttpResponse
from django.views.decorators.cache import cache_control

from api.core import ImageAPI

PLACEHOLDER_MIN_WIDTH = 1
PLACEHOLDER_MIN_HEIGHT = 1

PLACEHOLDER_MAX_WIDTH = 1000
PLACEHOLDER_MAX_HEIGHT = 1000

PLACEHOLDER_DEFAULT_WIDTH = 260
PLACEHOLDER_DEFAULT_HEIGHT = 180

PLACEHOLDER_BG_COLOR = "#cccccc"
PLACEHOLDER_TEXT_COLOR = "#969696"

@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def default(request):
    # GET params
    params = request.GET
    
    # get image width, check limits
    w = min(int(params.get('w', PLACEHOLDER_DEFAULT_WIDTH)), PLACEHOLDER_MAX_WIDTH)
    h = min(int(params.get('h', PLACEHOLDER_DEFAULT_HEIGHT)), PLACEHOLDER_MAX_HEIGHT)
    
    # check minimum values
    w = max(w, PLACEHOLDER_MIN_WIDTH)
    h = max(h, PLACEHOLDER_MIN_HEIGHT)
    
    # create placeholder image
    api = ImageAPI()
    api.create_image(w, h, PLACEHOLDER_BG_COLOR)
    
    # placeholder text
    text = params.get('t', "%s x %s" % (w, h))
    
    # calculate best font size
    font_size_auto = min(min(w/4, h/4), 40)
    font_size = int(params.get('ts', font_size_auto))
    
    # write on center middle
    api.write_on_center(text, font_size, PLACEHOLDER_TEXT_COLOR)
    
    # write to response
    response = HttpResponse (mimetype="image/png")
    api.image.save(response, "PNG")
    return response

