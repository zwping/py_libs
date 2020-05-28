import functools
import traceback

import requests
from flask import Response
from requests.adapters import HTTPAdapter

from libs.empty_util import isNotEmpty, isEmpty
from libs.log import i
from libs.response_standard import response
from libs.time_util import ctime


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


def try_except(err_mail=False, return_except=True):
    """ 防止异常
     :param err_mail 是否发送崩溃邮件
     :param return_except 是否返回异常信息，(可忽略方法执行过程，只看返回结果(不需要过多的判断异常情况))
     """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception:
                error_e = traceback.format_exc()
                i('try_except %s --- %s' % (func, error_e))
                if return_except:
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


def base_http():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            p = list(args)
            if len(p) != 7:
                raise RuntimeError('base_http参数必须统一顺序(7个参数)')
            requests_session = requests.Session()
            requests_session.mount('http://', HTTPAdapter(max_retries=p[5]))
            requests_session.mount('https://', HTTPAdapter(max_retries=p[5]))
            kw.update({'requests_session': requests_session})
            try:
                stime = ctime()
                r = func(*args, **kw)
                i('HTTP %s: %s %s %s毫秒' % (r.request.method, r.request.url, r.status_code, (ctime() - stime)))
                if p[6]:  # bare
                    return r.json() if p[4] else r.text  # p[4] json
                elif r.status_code == 200:
                    return response(result=r.json() if p[4] else r.text, is_response=False)
                else:
                    return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text), is_response=False)
            except Exception as e:
                i(e)
                import traceback
                return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)

        return wrapper

    return decorator
