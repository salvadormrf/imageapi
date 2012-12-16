import urllib2
from cStringIO import StringIO

MAX_DL_FILESIZE = 3*1024*1024
READ_CHUNK_SIZE = 8192


def safe_download(url, maxfilesize=MAX_DL_FILESIZE):
    """ downloads safely files from internet """
    
    file_size_dl = 0
    output = StringIO()
    
    # do request
    response = urllib2.urlopen(url)
    
    # try to get file size from headers
    meta = response.info()
    cl = meta.getheaders("Content-Length")
    if cl:
        file_size = int(cl[0])
        if file_size_dl >= MAX_DL_FILESIZE:
            raise Exception("File is too big")
    
    try:
        
        while True:
            # read a chunck of data
            buffer = response.read(READ_CHUNK_SIZE)
            if not buffer:
                break
            
            # append
            file_size_dl += len(buffer) 
            output.write(buffer)
            
            # check downloaded size
            if file_size_dl >= MAX_DL_FILESIZE:
                raise Exception("File is too big")
    finally:
        data = output.getvalue()
        output.close()
    
    return data

