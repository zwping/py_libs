import functools
import time
import traceback

import requests
from flask import Response
from requests.adapters import HTTPAdapter

from config import app
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
                i("方法执行超时(%.2fs) %s --- %s --- %s" %
                  (min_time, func.__name__, args, int(t * 1000)))
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
                result = response(501, 'service error',
                                  is_response=False) if ob is None else ob
                if isinstance(result, type(response(is_response=False))):
                    result['extra'] = '%s() %s (501-2)' % (str(func.__name__), error_e)
                    return result
                return error_e

        return wrapper

    return decorator


def loop_call_func(loop_size=30):
    """ 死循环调用某个方法，多用于爬虫未知异常情况 ( go爬虫不会出现崩溃情况? )
    __call_size 属于参数关键词
    :param func 理论上是一个异步，不然很容易造成OutOfMemory
    :param loop_size 默认允许30次奔溃
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kw):
            __call_size = kw.get('__call_size')
            if isNotEmpty(__call_size) and __call_size >= loop_size:
                kw.pop('__call_size')
                return func(*args, **kw)
            try:
                if isNotEmpty(__call_size):
                    kw.pop('__call_size')
                return func(*args, **kw)
            except Exception as e:
                i('死循环 Exception??%s' % e)
                if isEmpty(__call_size):
                    __call_size = 0
                __call_size += 1
                kw.update({'__call_size': __call_size})
                time.sleep(1)
                return wrapper(*args, **kw)

        return wrapper

    return decorator


def base_http():
    """ requests请求封装
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            # url = ''.join(list(args))
            headers = kw['headers'] if 'headers' in kw else None
            params = kw['params'] if 'params' in kw else None
            body = kw['body'] if 'body' in kw else None

            opt = kw['opt'] if 'opt' in kw else {}

            if 'max_retries' not in opt:
                opt['max_retries'] = 3  # 默认重连3次
            if 'json' not in opt:
                opt['json'] = True  # 默认转换为json
            if 'kw' not in opt:
                opt['kw'] = {}  # 请求kw参数包装对象kw={'timeout':1,'proxies': {'http':'xxx'}...}
            # if headers:
            #     opt['kw'].update({'headers': headers})
            # if params:
            #     opt['kw'].update({'params': params})
            # if body:
            #     opt['kw'].update({'body': body})

            if 'timeout' not in opt['kw']:
                opt['kw'].update({'timeout': 10})  # 该请求框架应用于spider

            requests_session = requests.Session()
            requests_session.mount('http://', HTTPAdapter(max_retries=opt['max_retries']))
            requests_session.mount('https://', HTTPAdapter(max_retries=opt['max_retries']))
            opt.update({'requests_session': requests_session})
            kw.update({'opt': opt})
            try:
                stime = ctime()
                r = func(*args, **kw)
                if opt.get('log'):  # 是否打印日志
                    i('HTTP %s: %s %s %s毫秒' % (r.request.method,
                                               r.request.url, r.status_code, (ctime() - stime)))
                    if headers:
                        i('headers: %s' % headers)
                    if body:
                        i('body: %s' % body)
                    if params:
                        i('params: %s' % params)
                if 'encoding' in opt:
                    r.encoding = opt['encoding']
                if opt.get('original'):  # 返回最原始的
                    return r
                elif opt.get('bare'):  # 默认不裸露响应结果(response包装)
                    return r.json() if opt['json'] else r.text
                elif r.status_code == 200:
                    return response(result=r.json() if opt['json'] else r.text, is_response=False)  # 默认返回包装值
                else:
                    return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text), is_response=False)
            except Exception as e:
                i(e)
                import traceback
                return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)

        return wrapper

    return decorator


def sqlalchemy_ctx():
    """ sql alchemy context异常处理
    建议在执行整个业务流程前添加 with context():
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except Exception as e:
                i('sql alchemy ctx error??? %s' % e)
                with app.app_context():
                    return func(*args, **kw)

        return wrapper

    return decorator
