# Create your views here.
import os
import logging
import tempfile
import fontforge
import lxml.html
import urllib2
from urlparse import urlparse

from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.forms.util import ErrorList
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.utils import safe_download
from mgmt.main.forms.fonts import FontMergerForm, FontConverterForm, FaviconGetterForm
from mgmt.main.utils import create_cache_key

MAX_UL_FILESIZE = 3*1024*1024

logger = logging.getLogger(__name__)


@require_GET
def simple_page(request, template):
    return render_to_response(template, {}, context_instance=RequestContext(request))


@require_http_methods(["GET", "POST"])
def font_converter(request):
    
    # display page form
    if request.method == 'GET':
        form = FontConverterForm()
    
    # accepts for fonts and returns a merged font
    if request.method == 'POST':
        form = FontConverterForm(request.POST, request.FILES)
        
        if form.is_valid():
            f1 = request.FILES['font']
            
            try:
                if f1.size > MAX_UL_FILESIZE:
                    form.errors['file'] = ErrorList([("File too large!")])
                else:
                    # handle uploaded file
                    ff1 = handle_uploaded_file(f1)
                    font_extension = ".%s" % form.cleaned_data["format"]
                    
                    # create temporary file
                    temp_file = tempfile.NamedTemporaryFile("wb", suffix=font_extension, delete=False)
                    
                    # try to merge fonts
                    try:
                        convert_font(ff1.name, temp_file.name)
                    except EnvironmentError as e:
                        form.errors['file'] = ErrorList([("Invalid font file!")])
                    else:
                        # prepare response
                        f = open(temp_file.name)
                        resp = HttpResponse(mimetype="application/font")
                        resp['Content-Disposition'] = 'attachment; filename=final%s' % font_extension
                        resp.write(f.read())
                        
                        # return font
                        return resp
            finally:
                # clean files
                if "f1" in locals() and not isinstance(f1, InMemoryUploadedFile):
                    os.remove(f1.name)
                
                for lvar in ["ff1", "temp_file"]:
                    if lvar in locals():
                        f = locals()[lvar]
                        try:
                            os.remove(f.name)
                        except:
                            logger.debug("Unable to remove file %s" % f.name)
    
    data = {"form": form}
    return render_to_response("fontconvert.html", data, context_instance=RequestContext(request))


@require_http_methods(["GET", "POST"])
def font_merger(request):
    
    # display page form
    if request.method == 'GET':
        form = FontMergerForm()
    
    # accepts for fonts and returns a merged font
    if request.method == 'POST':
        form = FontMergerForm(request.POST, request.FILES)
        if form.is_valid():
            f1 = request.FILES['font1']
            f2 = request.FILES['font2']
            
            try:
                if f1.size > MAX_UL_FILESIZE or f2.size > MAX_UL_FILESIZE:
                    form.errors['file'] = ErrorList([("File too large!")])
                else:
                    # handle uploaded file
                    ff1 = handle_uploaded_file(f1)
                    ff2 = handle_uploaded_file(f2)
                    
                    # merge fonts
                    temp_file = tempfile.NamedTemporaryFile("wb", suffix=".ttf", delete=False)
                    
                    # try to merge fonts
                    try:
                        merge_fonts(ff1.name, ff2.name, temp_file.name)
                    except EnvironmentError as e:
                        form.errors['file'] = ErrorList([("Invalid font file!")])
                    else:
                        # prepare response
                        f = open(temp_file.name)
                        resp = HttpResponse(mimetype="application/x-font-ttf")
                        resp['Content-Disposition'] = 'attachment; filename=merged.ttf'
                        resp.write(f.read())
                        
                        # return font
                        return resp
            finally:
                # clean files
                if "f1" in locals() and not isinstance(f1, InMemoryUploadedFile):
                    os.remove(f1.name)
                if "f2" in locals() and not isinstance(f2, InMemoryUploadedFile):
                    os.remove(f1.name)
                
                for lvar in ["ff1", "ff2", "temp_file"]:
                    if lvar in locals():
                        f = locals()[lvar]
                        try:
                            os.remove(f.name)
                        except:
                            logger.debug("Unable to remove file %s" % f.name)
    
    data = {"form": form}
    return render_to_response("fontmerge.html", data, context_instance=RequestContext(request))


def handle_uploaded_file(f):
    temp_file = tempfile.NamedTemporaryFile("wb", delete=False)
    logger.debug("Saving upload file to %s" % temp_file.name)
    
    for chunk in f.chunks():
        temp_file.write(chunk)
    temp_file.close()
    
    return temp_file


def convert_font(path1, final_path):
    logger.debug("Converting font: %s to %s" % (path1, final_path))
    
    try:
        f = fontforge.open(path1)
        f.generate(final_path)
    finally:
        if "f" in locals() and hasattr(f, "close"):
            try:
                f.close()
            except:
                logger.debug("Failed to close merge_fonts")


def merge_fonts(path1, path2, final_path):
    logger.debug("Merging fonts: %s and %s to %s" % (path1, path2, final_path))
    
    try:
        f = fontforge.open(path1)
        f.mergeFonts(path2)
        f.generate(final_path)
    except Exception as e:
        logger.exception("Unable to merge fonts")
        raise e
    finally:
        if "f" in locals() and hasattr(f, "close"):
            try:
                f.close()
            except:
                logger.debug("Failed to close merge_fonts")


@require_GET
def favicon_getter(request):
    data = {"links": []}
    form = FaviconGetterForm(request.GET) if "url" in request.GET else FaviconGetterForm()
    
    if form.is_valid():
        url = form.cleaned_data["url"].strip()
        cache_key = create_cache_key({"url": url, "type": "favicon"})
        
        # try to get from cache
        links = cache.get(cache_key)
        if links is not None:
            logger.debug("found in cache match for %s" % url)
            data["links"] = links
        else:
            # first try to get from hardcode url
            # hostname + favicon.ico
            u = urlparse(url)
            common_favicon_url = "http://" + u.hostname + "/favicon.ico"
            
            try:
                safe_download(common_favicon_url)
            except urllib2.HTTPError as e:
                logger.debug("could not find favicon on %s reason: %s" % (common_favicon_url, e))
            except:
                logger.exception("could not find favicon on %s" % common_favicon_url)
            else:
                data["links"].append(common_favicon_url)
            
            # if direct link does not work, lets try to download html
            if not data["links"]:
                logger.debug("trying to find favicon from HMTL")
                
                try: # download html
                    html = safe_download(url)
                except urllib2.HTTPError as e:
                    logger.debug("could not find favicon on %s reason: %s" % (url, e))
                except:
                    logger.exception("could not find favicon on %s" % url)
                else:
                    try: # parse html
                        doc = lxml.html.fromstring(html)
                    except:
                        logger.exception("could not parse HTML from %s" % url)
                    else:
                        doc.make_links_absolute("http://" + u.hostname)
                        
                        # look for favicons
                        links = doc.xpath("//link")
                        # append to list
                        for l in links:
                            _url = l.attrib.get("href")
                            if "favicon.ico" in _url:
                                data["links"].append(_url)
            
            # put on cache for 1h
            cache.set(cache_key, data["links"], 3600)
         
    data["form"] = form
    return render_to_response("favicongetter.html", data, context_instance=RequestContext(request))

