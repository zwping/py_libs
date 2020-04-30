from libs.empty_util import isNotEmpty


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


def cget(ob, k, defV=None):
    """ 获取未知对象的值
    :param ob 可能是个dict
    :param k key
    :param defV 默认值
    """
    if isNotEmpty(ob) and isinstance(ob, dict):
        return ob.get(k)
    else:
        return defV
