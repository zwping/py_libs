# 导入依赖包
import functools

from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from libs.response_standard import response
from libs.db import DB
from libs.empty_util import isEmpty, isNotEmpty

# from spider.service_log import service_log

SECRET_KEY = 'zwping'


def ctoken(data, expires=604800):
    """ 生成token
    :param 需要存入token的数据
    :param expires (秒) 过期时间 60 * 60 * 24 * 7 7天
     """
    # 第一个参数是内部的私钥，不可外泄
    # 第二个参数是有效期(秒)
    s = Serializer(SECRET_KEY, expires_in=expires)
    # 接收用户id转换与编码
    token = s.dumps({"data": data}).decode("ascii")
    return token


def vtoken(token):
    """ 校验token """

    # 参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(SECRET_KEY)
    try:
        # 转换为字典
        data = s.loads(token)
        return data['data']
    except Exception:
        return None


def login_token(verify=True, analysis_token=False):
    """ 效验token
     request请求参数中token key为token
     :param verify 校验token
     :param analysis_token 解析token，如果解析，增加参数用于接收解析数据
     """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if not verify:
                return func(*args, **kw)
            try:
                token = request.form['token'] if isNotEmpty(request.form) else ''
                if isEmpty(token) or isEmpty(DB.retrieve("select * from user_log where log='%s'" % token)):
                    return response(406, '登录信息已过期-1')
                if analysis_token:
                    token = vtoken(token)
                    if isEmpty(token):
                        return response(406, '登录信息已过期-2')
                    else:
                        kw.update({'token': token})
                return func(*args, **kw)
            except Exception:
                import traceback
                # service_log('token效验出错1', traceback.format_exc())
                return response(400, '参数错误-1', traceback.format_exc())

        return wrapper

    return decorator
