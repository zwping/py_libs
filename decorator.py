import functools
import traceback

from flask import Response

from libs.empty_util import isNotEmpty


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

            # from spider.service_log import service_log
            # if t > min_time:
            #     service_log("方法执行超时(%.2fs)" % min_time, "%s --- %s --- %s" % (func.__name__, args, int(t * 1000)))
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
            print("%s%s方法执行时间为:%s" % (
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
                __send_mail_2_up_service(error_e, func, error_e)
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
                __send_mail_2_up_service(err_mail, func, error_e)
                from libs.response_standard import response
                result = response(501, 'service error', is_response=False) if ob is None else ob
                if isinstance(result, type(response(is_response=False))):
                    result['extra'] = '%s() %s (501-2)' % (str(func.__name__), error_e)
                    return result
                return error_e

        return wrapper

    return decorator


def __send_mail_2_up_service(err_mail, func, error_e):
    pass
    # if err_mail:
    #     from libs.mail import send_mail
    #     from libs.db import DB
        # from config.constant_sql import ConstantSql
        # mails = DB.retrieve(ConstantSql.Sub.TRY_EXCEPT)
        # from libs.empty_util import isNotEmpty
        # if isNotEmpty(mails):
        #     send_mail([m[0] for m in mails], 'oneself 代码内部崩溃通知 501-2',
        #               '%s() -- %s' % (func.__name__, error_e))
    # from spider.service_log import service_log
    # service_log('try_except_of_decorator', '%s() %s (501-2)' % (func.__name__, error_e))


def delayed_load(func, delayed=3):
    import threading
    t = threading.Timer(delayed, func)
    t.setDaemon(True)  # 设置子线程守护主线程
    t.start()

# def delayed_load(delayed=10):
#     """ 延迟加载 """
#
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kw):
#             import threading
#             t = threading.Timer(delayed, func(*args, **kw))
#             t.setDaemon(True)  # 设置子线程守护主线程
#             t.start()
#
#         return wrapper
#
#     return decorator
