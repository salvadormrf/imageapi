import os
import Image
import ImageOps
import ImageDraw
import ImageFont
import ImageFilter
from cStringIO import StringIO
import logging

from mgmt.settings import STATICFILES_DIRS
from utils import safe_download

FONT_PATH = os.path.join(STATICFILES_DIRS[0], 'fonts', 'merged.ttf')


logging.basicConfig()
logger = logging.getLogger(__name__)


class ImageAPI(object):
    original = None
    img = None
    
    def __init__(self):
        #self.img = Image.new("RGB", (100, 100), "#CDEB8B")
        pass
    
    def create_image(self, width, height, bgcolor):
        self.img = Image.new("RGB", (width, height), bgcolor)
    
    @property
    def image(self):
        return self.img
    
    def open_from_local(self, filename):
        self.img = Image.open(filename)
        self.original = self.img

    def open_from_internet(self, url):
        data = safe_download(url)
        self.img = Image.open(StringIO(data))
        self.original = self.img

    def rotate(self, angle):
        self.img = self.img.rotate(angle, resample=Image.BILINEAR, expand=1)
    
    def resize(self, w=None, h=None):
        w = w if w is not None else self.img.size[0]
        h = h if h is not None else self.img.size[1]
        self.img.thumbnail((w, h), resample=Image.BILINEAR)
    
    def crop(self, box):
        self.img = self.img.crop(box)
    
    def paste_overlay(self, overlay_img, box):
        r, g, b, alpha = overlay_img.split()
        self.img.paste(overlay_img, box, mask=alpha)
    
    def paste_overlay_into(self, overlay_img, box):
        x1, y1, x2, y2 = box
        # resize overlay image before pasting                     
        img = overlay_img.resize(((x2 - x1), (y2 - y1)), Image.ANTIALIAS)
        self.paste_overlay(img, (x1, y1))
        
        
    """
    def split(self, band):
        #(red, green, blue).
        r, g, b = self.img.split()
        if band == "r": self.img = r
        if band == "g": self.img = g
        if band == "b": self.img = b
    """
    
    # SHARPEN
    # CONTOUR
    # EMBOSS
    # http://www.pythonware.com/library/pil/handbook/imagefilter.htm
    def blur(self):
        self.img = self.img.filter(ImageFilter.BLUR)
    
    
    def write_on_center(self, string, font_size, font_color, font_path=FONT_PATH):
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(font_path, size=font_size)
        
        # calculate postion to put text on center/middle
        iw, ih = self.img.size
        tw, th = draw.textsize(string, font=font)
        
        x = (iw - tw) / 2
        y = (ih - th) / 2
        
        draw.text((x, y), string, fill=font_color, font=font)

    
    def write_on_bottom_right(self, string, font_size, font_color, font_path=FONT_PATH):
        draw = ImageDraw.Draw(self.img)
        font = ImageFont.truetype(font_path, size=font_size)
        
        # calculate postion to put text on center/middle
        iw, ih = self.img.size
        tw, th = draw.textsize(string, font=font)
        
        x = iw - (tw + 5)
        y = ih - (th + 5)
        
        draw.text((x, y), string, fill=font_color, font=font)
    
    
    def write_text(self, string, x=0, y=0, font_color="black", font_size=10):
        draw = ImageDraw.Draw(self.img)
        
        font = ImageFont.truetype(FONT_PATH, size=font_size)
        draw.text((x, y), string, fill=font_color, font=font)
    

    
    def rectangle(self, x, y, w, h, color="red", border_color="white"):
        draw = ImageDraw.Draw(self.img)
        box = [(x, y), (x+w, y+h)]
        draw.rectangle(box, fill=color, outline=border_color)
    
    def blur_section(self, x, y, w, h, blur_times=10):
        box = (x, y, x + w, y + h)
        ic = self.img.crop(box)
        
        # with the BLUR filter, you can blur a few times to get the effect you're seeking
        for i in range(blur_times):
            ic = ic.filter(ImageFilter.BLUR)
        
        self.img.paste(ic, box)
    
    def line(self, x1, y1, x2, y2, line_color="white"):
        draw = ImageDraw.Draw(self.img)
        draw.line((x1, y1, x2, y2), fill=line_color)
    
    def apply_border(self, padding_size=4, border_size=1, fill_color="white", border_color="#ccc"):
        self.img = ImageOps.expand(self.img, border=padding_size, fill=fill_color)
        self.img = ImageOps.expand(self.img, border=border_size, fill=border_color)
    
    def apply_effects(self, params, filename):
        pass
    
        """
        def transform(self, XXX):
            self.img = self.img.transform((200,200),Image.AFFINE, (2, 2, 2, 2, 2))
        """ 
        """
        if "rotate" in params:
            angle = int(params.get("rotate", 0))
            self.rotate(angle)
        
        if "width" in params and "height" in params:
            w = int(params["width"])
            h = int(params["height"])
            self.resize(w, h)
        else:
            if "width" in params:
                w = int(params["width"])
                self.resize(w, None)
            if "height" in params:
                h = int(params["height"])
                self.resize(None, h)

        if "crop" in params:
            #x1, y1, x2, y2
            l = params["crop"].split(",")
            box = (int(l[0]), int(l[1]), int(l[2]), int(l[3]))
            self.crop(box)
        """
        
        """
        if "rgb" in params:
            band = params["rgb"]
            self.split(band)
        """
        """
        if "blur" in params:
            self.blur()
        """
        
        """
        #url?square=20+23:100x200
        #&bg=cyan&border=2:red
        if 'square' in params:
            v = params['square'].split(":")
            x, y, w, h, color = int(v[0]), int(v[1]), int(v[2]), int(v[3]), v[4]
            self.rectangle(x, y, w, h, color=color)
        """
        
            
        """
        for p in params:
            # blur section 
            if p.startswith("b"):
                v = params[p].split(":")
                x, y, w, h = int(v[0]), int(v[1]), int(v[2]), int(v[3])
                self.blur_section(x, y, w, h, 3)
                # TODO font family and font size
            
            # text 
            if p.startswith("t"):
                v = params[p].split(":")
                x, y, text, color, size = int(v[0]), int(v[1]), v[2], v[3], int(v[4])
                self.write_text(text, x, y, color, size)
                # TODO font family and font size
        """


"""
http://localhost:8080/1.png?
b0=170:126:140:16&
b1=170:150:140:16&
b2=170:200:140:16&
b3=170:224:140:16&
b4=170:250:140:16&
b5=170:298:140:16&
b6=170:324:140:16&
t=174:250:dev.brandmymail.com:black:11
"""













