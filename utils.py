def md5Encryption(s):
    import hashlib
    m = hashlib.md5()
    m.update(str(s).encode(encoding='UTF-8'))
    return m.hexdigest()
