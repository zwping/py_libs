# 导入依赖包
import functools

from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from config import app
from libs.empty_util import isEmpty
from libs.response_standard import response


def ctoken(data, expires=604800):
    """ 生成token
    :param 需要存入token的数据
    :param expires (秒) 过期时间 60 * 60 * 24 * 7 7天
     """
    # 第一个参数是内部的私钥，不可外泄
    # 第二个参数是有效期(秒)
    s = Serializer(app.config['SECRET_KEY'], expires_in=expires)
    # 接收用户id转换与编码
    token = s.dumps({"data": data}).decode("ascii")
    return token


def vtoken(token):
    """ 校验token """

    # 参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(app.config['SECRET_KEY'])
    try:
        # 转换为字典
        data = s.loads(token)
        return data['data']
    except Exception:
        return None
