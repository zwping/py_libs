import functools
import traceback

from flask import Response

from libs.empty_util import isNotEmpty, isEmpty
from libs.log import i


def func_overtime(min_time: float = 2):
    """ 判断方法是否执行超时，并写入服务日志
    :param min_time 默认2秒
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            import time
            start = time.time()
            r = func(*args, **kw)
            t = time.time() - start

            if t > min_time:
                i("方法执行超时(%.2fs) %s --- %s --- %s" % (min_time, func.__name__, args, int(t * 1000)))
            return r

        return wrapper

    return decorator


def func_metric_time(txt=None):
    """ 方法执行时间 """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            import time
            start = time.time()
            r = func(*args, **kw)
            i("%s%s方法执行时间为:%s" % (
                '' if txt is None else '%s ' % txt, func.__name__, '%.3fs' % float(time.time() - start)))
            return r

        return wrapper

    return decorator


def try_except(err_mail=False):
    """ 防止异常 """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception:
                error_e = traceback.format_exc()
                i('try_except %s --- %s' % (func, error_e))
                return error_e

        return wrapper

    return decorator


def api_try_except(ob=None, err_mail=False, is_file=False):
    """ 防止异常
     :param ob 对象 try_except对API的包装，默认为api返回格式
     :param err_mail
     :param is_file
     """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                if is_file:
                    return func(*args, **kw)
                r = func(*args, **kw)
                # The view function did not return a valid response.
                # The return type must be a string, dict, tuple,Response instance, or WSGI callable,
                # but it was a int.
                if isNotEmpty(r) and \
                        (isinstance(r, Response) or
                         isinstance(r, str) or
                         isinstance(r, dict) or
                         isinstance(r, dict) or
                         isinstance(r, tuple)):
                    return r
                raise Exception('返回的数据格式不对%s' % type(r))
            except Exception:
                error_e = traceback.format_exc()
                i('try_except %s --- %s' % (func, error_e))
                from libs.response_standard import response
                result = response(501, 'service error', is_response=False) if ob is None else ob
                if isinstance(result, type(response(is_response=False))):
                    result['extra'] = '%s() %s (501-2)' % (str(func.__name__), error_e)
                    return result
                return error_e

        return wrapper

    return decorator


def loop_call_func():
    """ 死循环调用某个方法，多用于爬虫未知异常情况 ( go爬虫不会出现崩溃情况? )
    __call_size 属于参数关键词
    :param func 理论上是一个异步，不然很容易造成OutOfMemory
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kw):
            __call_size = kw.get('__call_size')
            if isNotEmpty(__call_size) and __call_size >= 30:
                kw.pop('__call_size')
                return func(*args, **kw)
            try:
                if isNotEmpty(__call_size):
                    kw.pop('__call_size')
                return func(*args, **kw)
            except Exception as e:
                i('死循环??%s' % e)
                if isEmpty(__call_size):
                    __call_size = 0
                __call_size += 1
                kw.update({'__call_size': __call_size})
                wrapper(*args, **kw)

        return wrapper

    return decorator
