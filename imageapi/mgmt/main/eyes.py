import os
import urllib2
import logging
import simplejson

import Image

from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseBadRequest

from api.core import ImageAPI
from api.object_detection import detect_eyes_from_pil_image
from utils import create_cache_key
from mgmt.settings import STATICFILES_DIRS

IMG_PATH = STATICFILES_DIRS[0]
TROLL_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'troll.png')
PEDOBEAR_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'pedobear.png')


WATERMARK_TEXT_SIZE = 14
WATERMARK_TEXT_COLOR = "white"
WATERMARK_TEXT = u"\uf072 www.trollaface.com"

logger = logging.getLogger(__name__)


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def blur(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    for face in faces:
        x, y, w, h = face[0]
        api.blur_section(x, y, w, h, blur_times=10)
        api.rectangle(x, y, w, h, color=None)
    
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def border(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    for face in faces:
        x, y, w, h = face[0]
        api.rectangle(x, y, w, h, color=None)
    
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def crop(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    if faces:
        x, y, w, h = faces[-1][0]
        box = (x, y, x + w, y + h)
        api.crop(box)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def eyes_json(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    data = {"faces": [f[0] for f in faces]}
    
    return HttpResponse(simplejson.dumps(data), mimetype="application/json")


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def pedobear(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    # load troll mage
    troll_img = Image.open(PEDOBEAR_IMG_PATH)
    
    for face in faces:
        x, y, w, h = face[0]
        
        # we need more than the face position, so lets give some margin for head
        # very related to image dimensions
        margin_w = int(w / 3.5)
        margin_h = int(h / 2.4)
        
        # increase box dimensions
        w = w + 2 * margin_w
        h = h + margin_h
        
        # update starting cordinates
        y = y - margin_h
        x = x - margin_w
        
        box = (x, y, x + w, y + h)
        api.paste_overlay_into(troll_img, box)

    
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response


@require_GET
@cache_control(must_revalidate=True, max_age=3600)
def troll(request):
    url = request.GET.get("url", "").strip()
    if not url:
        return HttpResponseBadRequest("missing url parameter")
    
    try:
        api, faces = _get_eyes(request, url)
    except urllib2.HTTPError as e:
        logger.debug("could not download image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except ValueError as e: # unknown url type
        logger.debug("could not use image url %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    except IOError as e:
        logger.debug("could not process image from %s reason: %s" % (url, e))
        return HttpResponseBadRequest("invalid url")
    
    # load troll mage
    troll_img = Image.open(TROLL_IMG_PATH)
    
    for face in faces:
        x, y, w, h = face[0]
        box = (x, y, x + w, y + h)
        api.paste_overlay_into(troll_img, box)
    
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response


def _get_eyes(request, url):    
    cache_key = create_cache_key({"url": url, "type": "eyes"})
    
    # download image from internet
    api = ImageAPI()
    api.open_from_internet(url)
    
    # try to get from cache
    faces = cache.get(cache_key)
    if faces is not None:
        logger.debug("found faces in cache for %s" % url)
    else:
        # identify faces
        faces = detect_eyes_from_pil_image(api.image)
        
        # put on cache for 1h
        cache.set(cache_key, faces, 3600)
        
    return api, faces

