def md5Encryption(s):
    import hashlib
    m = hashlib.md5()
    m.update(str(s).encode(encoding='UTF-8'))
    return m.hexdigest()


def delayed_load(func, delayed=3):
    import threading
    t = threading.Timer(delayed, func)
    t.setDaemon(True)  # 设置子线程守护主线程
    t.start()
