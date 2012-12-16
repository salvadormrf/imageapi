import hashlib

def create_cache_key(params):
    m = hashlib.sha1()
    m.update(str(params))
    return m.hexdigest()

