### 定义一些标准
import json

from flask import Response


def response(code: int = 200, msg="responds suc", extra='', result=None, is_response=True):
    """规范所有请求的响应数据结构

    :param code
            200 成功 \n
            400 参数错误 \n
            401 查询结果为空 \n
            402 数据保存失败 \n
            405 文件不存在 \n
            406 token过期 \n
            501 服务器错误 \n
    :param msg 接口说明信息，多用于API异常时客户端使用
    :param extra 接口额外信息，多用于API异常时服务器使用
    :param result 返回数据
    :param is_response
    """
    # d = OrderedDict()
    # d['code'] = code
    # d['msg'] = msg
    d = {
        'code': code,
        'msg': msg
    }
    from config import app
    if app.config['DEBUG']:
        d.update({'extra': extra})
    if result is not None:
        d.update({'result': result})
    # with app.app_context():
    #     return jsonify(d)
    return Response(json.dumps(d), mimetype='application/json') if is_response else d
    # return d
    # return json.loads(d, object_pairs_hook=OrderedDict)


def response_error(txt):
    """响应内容不存在"""
    return response(401, str(txt))


def response_error_of_form(form):
    """请求参数错误数据格式"""
    values = ''
    for k in form:
        values = "、".join(form[k])
    return response(400, values)


def list_response(data, perpage, page, total):
    """ 集合的响应数据格式
     :param data
     :param perpage 每页数据量
     :param page 当前页数
     :param total 总页数
     """
    return {
        'data': data,
        'perpage': perpage,
        'page': page,
        'total': total
    }