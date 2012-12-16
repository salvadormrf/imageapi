import os
import urllib2
import logging
import simplejson
import math
import Image

from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseBadRequest

from api.core import ImageAPI
from api.object_detection import detect_face_and_eyes_from_pil_image
from utils import create_cache_key
from mgmt.settings import STATICFILES_DIRS



IMG_PATH = STATICFILES_DIRS[0]

TROLL_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'troll.png')
PEDOBEAR_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'pedobear.png')
CECILIA_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'cecilia.png')
DOG_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'dog.png')

WATERMARK_TEXT_SIZE = 14
WATERMARK_TEXT_COLOR = "white"
WATERMARK_TEXT = u"\uf072 www.trollaface.com"

logger = logging.getLogger(__name__)



def get_center_point(x, y, w, h):
    return ((x+w/2), y+h/2)

def get_angle(x1, y1, x2, y2):
    rad = math.atan2(y2-y1, x2-x1)
    return math.degrees(rad)

@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def border(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    api, faces = _get_eyes(request, url)
    
    """
    for face in faces:
        x, y, w, h = face[0]
        api.rectangle(x, y, w, h, color=None, border_color="red")
    """
    
    # load troll mage
    troll_img = Image.open(DOG_IMG_PATH)
    
    for f in faces:
        eyes = f['eyes']
        x, y, w, h = f['position'][0]
        api.rectangle(x, y, w, h, color=None, border_color="red")
        
        api.line(x+w/2, y, x+w/2, y+h, line_color="blue")
        api.line(x, y+h/2, x+w, y+h/2, line_color="blue")
        
        rotation_degrees = None
        
        # sort eyes by the max number of neigbours
        # limit to 2 neighbours
        # must be on top of face ????
        sorted_eyes = sorted(eyes, key=lambda e: e[1])[:2]
        
        for ((ex, ey, ew, eh), en) in sorted_eyes:
            api.rectangle(ex, ey, ew, eh, color=None, border_color="yellow")
            
            # draw line between eyes
            if len(sorted_eyes) == 2:
                e0x, e0y, e0w, e0h  = sorted_eyes[0][0]
                e1x, e1y, e1w, e1h  = sorted_eyes[1][0]
                
                p0 = get_center_point(e0x, e0y, e0w, e0h)
                p1 = get_center_point(e1x, e1y, e1w, e1h)
                
                rotation_degrees = get_angle(p0[0], p0[1], p1[0], p1[1])
                
                api.line(p0[0], p0[1], p1[0], p1[1], line_color="cyan")
        
        
        
        # deduce other missing eye
        # deduce mouth position
        if rotation_degrees not None:
            pass
        
        """
        box = (x, y, x + w, y + h)
        api.paste_overlay_into(troll_img, box)
        """
        
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response




















def _get_eyes(request, url):    
    cache_key = create_cache_key({"url": url, "type": "eyes"})
    
    # try to get from cache
    faces = cache.get(cache_key)
    print faces
    
    # download image from internet
    api = ImageAPI()
    api.open_from_internet(url)
    
    if faces is not None:
        logger.debug("found faces in cache for %s" % url)
    else:
        # identify faces
        faces = detect_face_and_eyes_from_pil_image(api.image)
        
        # put on cache for 1h
        cache.set(cache_key, faces, 3600)
    return api, faces

