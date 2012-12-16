import os
import urllib2
import urllib
import logging
import simplejson
import math
import Image

from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseBadRequest

from api.core import ImageAPI
from api.object_detection import detect_face_from_pil_image
from utils import create_cache_key
from mgmt.settings import STATICFILES_DIRS

IMG_PATH = STATICFILES_DIRS[0]
TROLL_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'troll.png')
PEDOBEAR_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'pedobear.png')
CECILIA_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'cecilia.png')
DOG_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'dog.png')
TEST_IMG_PATH = os.path.join(IMG_PATH, 'img', 'meme_faces', 'test.png')


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
    
    api, photos = _get_faces(request, url)
    
    # load troll mage
    troll_img = Image.open(TEST_IMG_PATH)
    
    for photo in photos.get("photos", []):
        photo_width = photo["width"]
        photo_height = photo["height"]
        
        for tag in photo.get("tags", []):
                        
            # face center
            face_center = tag["center"]
            face_center_x = (face_center["x"] * photo_width) / 100.0
            face_center_y = (face_center["y"] * photo_height) / 100.0
            
            face_width = (tag["width"] * photo_width) / 100.0
            face_height = (tag["height"] * photo_height) / 100.0
            
            face_x = int(face_center_x - (face_width/2))
            face_y = int(face_center_y - (face_height/2))
            
            # eye left
            eye_left = tag["eye_left"]
            eye_left_x = (eye_left["x"] * photo_width) / 100.0
            eye_left_y = (eye_left["y"] * photo_height) / 100.0
            
            # eye right
            eye_right = tag["eye_right"]
            eye_right_x = (eye_right["x"] * photo_width) / 100.0
            eye_right_y = (eye_right["y"] * photo_height) / 100.0
            
            # mouth center
            mouth_center = tag["mouth_center"]
            mouth_center_x = (mouth_center["x"] * photo_width) / 100.0
            mouth_center_y = (mouth_center["y"] * photo_height) / 100.0
            
            # nose
            nose = tag["nose"]
            nose_x = (nose["x"] * photo_width) / 100.0
            nose_y = (nose["y"] * photo_height) / 100.0
            
            
            # calculate rotation angle between eyes            
            rotation_degrees = get_angle(eye_right_x, eye_right_y, eye_left_x, eye_left_y)
            
            
            # get distance between eyes, to know the width of the head
            
            
            """
            #margin_w = int(face_width/4)
            margin_y_hair = int(face_width/1.5)
            
            # TODO
            box = (
                   int(face_x), 
                   int(face_y - margin_y_hair), 
                   int(face_x + face_width), 
                   int(face_y + face_height)
                   )
            
            # paste overlay image
            troll_img = troll_img.rotate(-rotation_degrees)
            api.paste_overlay_into(troll_img, box)
            """
            # draw rectangles for found elements
            api.rectangle(face_x, face_y, face_width, face_height, color=None)
            api.rectangle(eye_left_x-2, eye_left_y-2, 4, 4, color="yellow")
            api.rectangle(eye_right_x-2, eye_right_y-2, 4, 4, color="yellow")
            
            api.line(eye_left_x, eye_left_y, eye_right_x, eye_right_y, line_color="cyan")
            api.rectangle(mouth_center_x-2, mouth_center_y-2, 4, 4, color="green")
            api.rectangle(nose_x-2, nose_y-2, 4, 4, color="cyan")
            

    """
    try:
        api, faces = _get_faces(request, url)
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
    """
    
    # add watermark
    api.write_on_bottom_right(WATERMARK_TEXT, WATERMARK_TEXT_SIZE, WATERMARK_TEXT_COLOR)
    
    # write to response
    response = HttpResponse(mimetype="image/png")
    api.image.save(response, "PNG")
    return response




"""
            
            
            #api.rectangle(x-2, y-2, 4, 4, color="red")
            
            
            tag_width = (tag["width"] * photo_width) / 100.0
            tag_height = (tag["height"] * photo_height) / 100.0
            
            box = (int(x-(tag_width/2))-20, int(y-(tag_height/2))-20, 
                   int(x+(tag_width/2))+20, int(y+(tag_height/2))+20)
            
            #api.paste_overlay_into(troll_img, box)
            
            #api.rectangle(x, y, w, h, color=None)
            yaw = tag["yaw"]
            
            if yaw < 0:
                #troll_img = troll_img.rotate(-tag["roll"])
                troll_img =  troll_img.transform(
                                                 troll_img.size, 
                                                 Image.QUAD, 
                                                 (0+yaw, 0, 
                                                  0, troll_img.size[0], 
                                                  troll_img.size[0]+yaw, 250, 
                                                  troll_img.size[0], 0), Image.BILINEAR)
            
            
            api.rectangle(x-(tag_width/2), y-(tag_height/2), tag_width, tag_height, color=None)
"""































def _get_faces(request, url):
    # https://skybiometry.com/Documentation#faces/detect
    API_KEY = "34a71173772b46beb3e854c67e880165"
    API_SECRET = "744bdfcc288e4279bbb1f0fe00767efe"
    API_ENDPOINT = "http://api.skybiometry.com/fc/faces/detect.json"
    
    params = {"api_key": API_KEY, "api_secret": API_SECRET, "urls": url}
    
    call_url = API_ENDPOINT + "?" + urllib.urlencode(params)
    #response = urllib2.urlopen(call_url).read()
    #print response
    
    api = ImageAPI()
    api.open_from_internet(url)
    
    
    response = RESPONSE
    faces = simplejson.loads(response)
    
    return api, faces
    
    
    """
    cache_key = create_cache_key({"url": url, "type": "face"})
    
    # download image from internet
    api = ImageAPI()
    api.open_from_internet(url)
    
    # try to get from cache
    faces = cache.get(cache_key)
    if faces is not None:
        logger.debug("found faces in cache for %s" % url)
    else:
        # identify faces
        faces = detect_face_from_pil_image(api.image)
        
        # put on cache for 1h
        cache.set(cache_key, faces, 3600)
        
    return api, faces
    """






RESPONSE = """
{
    "photos": [{
        "url": "https://fbcdn-sphotos-b-a.akamaihd.net/hphotos-ak-snc6/199335_10151038494017823_510792956_n.jpg",
        "pid": "F@020c088154dff9636a372ac94554cbf3_2b2e45c63a727",
        "width": 960,
        "height": 594,
        "tags": [{
            "tid": "TEMP_F@020c088154dff9636a372ac9174ee810_2b2e45c63a727_47.40_21.72_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.85,
            "height": 6.23,
            "center": {
                "x": 47.4,
                "y": 21.72
            },
            "eye_left": {
                "x": 48.23,
                "y": 19.53
            },
            "eye_right": {
                "x": 46.56,
                "y": 19.53
            },
            "mouth_center": {
                "x": 47.4,
                "y": 23.74
            },
            "nose": {
                "x": 47.5,
                "y": 22.22
            },
            "yaw": -2,
            "roll": 1,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 81
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac92b2e2d32_2b2e45c63a727_75.73_51.35_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.9,
            "height": 7.91,
            "center": {
                "x": 75.73,
                "y": 51.35
            },
            "eye_left": {
                "x": 76.98,
                "y": 49.66
            },
            "eye_right": {
                "x": 74.38,
                "y": 49.49
            },
            "mouth_center": {
                "x": 75.73,
                "y": 53.7
            },
            "nose": {
                "x": 75.62,
                "y": 51.68
            },
            "yaw": 4,
            "roll": -1,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 75
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac93624e2c7_2b2e45c63a727_59.79_20.03_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.85,
            "height": 6.23,
            "center": {
                "x": 59.79,
                "y": 20.03
            },
            "eye_left": {
                "x": 60.73,
                "y": 18.35
            },
            "eye_right": {
                "x": 58.54,
                "y": 19.02
            },
            "mouth_center": {
                "x": 59.9,
                "y": 21.72
            },
            "nose": {
                "x": 59.79,
                "y": 20.2
            },
            "yaw": 2,
            "roll": -8,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 68
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac95a98d569_2b2e45c63a727_52.71_17.85_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.65,
            "height": 5.89,
            "center": {
                "x": 52.71,
                "y": 17.85
            },
            "eye_left": {
                "x": 53.75,
                "y": 16.33
            },
            "eye_right": {
                "x": 52.08,
                "y": 16.33
            },
            "mouth_center": {
                "x": 52.92,
                "y": 19.53
            },
            "nose": {
                "x": 53.02,
                "y": 18.01
            },
            "yaw": -8,
            "roll": 0,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 73
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac95ecd1ff2_2b2e45c63a727_15.31_47.81_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.48,
            "height": 7.24,
            "center": {
                "x": 15.31,
                "y": 47.81
            },
            "eye_left": {
                "x": 16.46,
                "y": 45.79
            },
            "eye_right": {
                "x": 14.17,
                "y": 45.96
            },
            "mouth_center": {
                "x": 15.31,
                "y": 50.0
            },
            "nose": {
                "x": 15.31,
                "y": 48.32
            },
            "yaw": -1,
            "roll": -4,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 73
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac984d32b7c_2b2e45c63a727_33.54_24.75_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.54,
            "height": 5.72,
            "center": {
                "x": 33.54,
                "y": 24.75
            },
            "eye_left": {
                "x": 34.58,
                "y": 23.57
            },
            "eye_right": {
                "x": 32.71,
                "y": 23.23
            },
            "mouth_center": {
                "x": 33.54,
                "y": 26.43
            },
            "nose": {
                "x": 33.65,
                "y": 24.92
            },
            "yaw": -2,
            "roll": 7,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 68
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac98e4a49bc_2b2e45c63a727_67.81_14.81_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.65,
            "height": 5.89,
            "center": {
                "x": 67.81,
                "y": 14.81
            },
            "eye_left": {
                "x": 68.75,
                "y": 13.64
            },
            "eye_right": {
                "x": 66.98,
                "y": 13.47
            },
            "mouth_center": {
                "x": 67.92,
                "y": 16.5
            },
            "nose": {
                "x": 68.02,
                "y": 15.15
            },
            "yaw": -1,
            "roll": 5,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 75
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac99914976e_2b2e45c63a727_79.48_18.86_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.85,
            "height": 6.23,
            "center": {
                "x": 79.48,
                "y": 18.86
            },
            "eye_left": {
                "x": 80.52,
                "y": 17.85
            },
            "eye_right": {
                "x": 78.65,
                "y": 17.51
            },
            "mouth_center": {
                "x": 79.38,
                "y": 20.71
            },
            "nose": {
                "x": 79.58,
                "y": 19.02
            },
            "yaw": 2,
            "roll": 6,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 75
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9a6a51a18_2b2e45c63a727_73.54_24.75_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.65,
            "height": 5.89,
            "center": {
                "x": 73.54,
                "y": 24.75
            },
            "eye_left": {
                "x": 74.27,
                "y": 23.23
            },
            "eye_right": {
                "x": 72.4,
                "y": 23.23
            },
            "mouth_center": {
                "x": 73.33,
                "y": 26.43
            },
            "nose": {
                "x": 73.33,
                "y": 25.25
            },
            "yaw": 6,
            "roll": 0,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 67
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9aa6810f3_2b2e45c63a727_91.04_24.41_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.85,
            "height": 6.23,
            "center": {
                "x": 91.04,
                "y": 24.41
            },
            "eye_left": {
                "x": 91.46,
                "y": 22.9
            },
            "eye_right": {
                "x": 89.27,
                "y": 23.4
            },
            "mouth_center": {
                "x": 89.9,
                "y": 25.93
            },
            "nose": {
                "x": 90.42,
                "y": 25.25
            },
            "yaw": 25,
            "roll": -7,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 73
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9b1dc3729_2b2e45c63a727_61.25_51.52_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.48,
            "height": 7.24,
            "center": {
                "x": 61.25,
                "y": 51.52
            },
            "eye_left": {
                "x": 62.4,
                "y": 49.49
            },
            "eye_right": {
                "x": 60.0,
                "y": 49.49
            },
            "mouth_center": {
                "x": 61.15,
                "y": 53.7
            },
            "nose": {
                "x": 61.15,
                "y": 52.19
            },
            "yaw": 3,
            "roll": -1,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 77
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9bc124574_2b2e45c63a727_44.58_46.97_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.69,
            "height": 7.58,
            "center": {
                "x": 44.58,
                "y": 46.97
            },
            "eye_left": {
                "x": 45.94,
                "y": 45.12
            },
            "eye_right": {
                "x": 43.33,
                "y": 45.29
            },
            "mouth_center": {
                "x": 44.79,
                "y": 49.66
            },
            "nose": {
                "x": 44.69,
                "y": 48.15
            },
            "yaw": 3,
            "roll": -3,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 76
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9cb3d8cdd_2b2e45c63a727_14.69_23.23_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.58,
            "height": 7.41,
            "center": {
                "x": 14.69,
                "y": 23.23
            },
            "eye_left": {
                "x": 16.67,
                "y": 22.05
            },
            "eye_right": {
                "x": 14.27,
                "y": 21.21
            },
            "mouth_center": {
                "x": 15.0,
                "y": 26.09
            },
            "nose": {
                "x": 15.31,
                "y": 24.07
            },
            "yaw": -25,
            "roll": 11,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 71
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9cc217d57_2b2e45c63a727_28.44_53.37_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.69,
            "height": 7.58,
            "center": {
                "x": 28.44,
                "y": 53.37
            },
            "eye_left": {
                "x": 30.0,
                "y": 51.52
            },
            "eye_right": {
                "x": 27.19,
                "y": 51.68
            },
            "mouth_center": {
                "x": 28.54,
                "y": 56.06
            },
            "nose": {
                "x": 28.65,
                "y": 53.7
            },
            "yaw": -2,
            "roll": -2,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 71
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9e0bd12a0_2b2e45c63a727_37.40_16.33_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.65,
            "height": 5.89,
            "center": {
                "x": 37.4,
                "y": 16.33
            },
            "eye_left": {
                "x": 38.23,
                "y": 15.15
            },
            "eye_right": {
                "x": 36.46,
                "y": 14.98
            },
            "mouth_center": {
                "x": 37.4,
                "y": 18.18
            },
            "nose": {
                "x": 37.5,
                "y": 16.5
            },
            "yaw": -3,
            "roll": 3,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 77
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9e366603f_2b2e45c63a727_22.92_26.60_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 3.85,
            "height": 6.23,
            "center": {
                "x": 22.92,
                "y": 26.6
            },
            "eye_left": {
                "x": 24.58,
                "y": 25.42
            },
            "eye_right": {
                "x": 22.4,
                "y": 25.08
            },
            "mouth_center": {
                "x": 23.44,
                "y": 28.45
            },
            "nose": {
                "x": 23.65,
                "y": 27.1
            },
            "yaw": -27,
            "roll": 3,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 76
                }
            }
        }, {
            "tid": "TEMP_F@020c088154dff9636a372ac9ff61e3f9_2b2e45c63a727_90.94_63.80_0_1",
            "recognizable": true,
            "uids": [],
            "confirmed": false,
            "manual": false,
            "width": 4.48,
            "height": 7.24,
            "center": {
                "x": 90.94,
                "y": 63.8
            },
            "eye_left": {
                "x": 92.19,
                "y": 62.29
            },
            "eye_right": {
                "x": 89.69,
                "y": 62.12
            },
            "mouth_center": {
                "x": 90.83,
                "y": 65.82
            },
            "nose": {
                "x": 90.94,
                "y": 64.31
            },
            "yaw": 4,
            "roll": 2,
            "pitch": 0,
            "attributes": {
                "face": {
                    "value": "true",
                    "confidence": 74
                }
            }
        }]
    }],
    "status": "success",
    "usage": {
        "used": 8,
        "remaining": 92,
        "limit": 100,
        "reset_time_text": "Sun, 4 November 2012 01:39:12 +0000",
        "reset_time": 1351993152
    }
}
"""





