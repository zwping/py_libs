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
            404 文件不存在 \n
            406 token过期 \n
            501 服务器错误 \n
    :param msg 接口说明信息，多用于API异常时客户端使用
    :param extra 接口额外信息，多用于API异常时服务器使用
    :param result 返回数据
    :param is_response 主要用于约束json顺序
    """
    d = {
        'code': code,
        'msg': msg
    }
    from config import app
    if app.config['DEBUG']:
        d.update({'extra': extra})
    if result is not None:
        d.update({'result': result})
    return Response(json.dumps(d), mimetype='application/json') if is_response else d


def response_error(txt):
    """响应内容不存在"""
    return response(401, str(txt))


def response_error_of_form(form):
    """请求参数错误数据格式"""
    data = []
    for d in form.errors.values():
        data.append(d[0])
    return response(400, ','.join(set(data)))  # set() 去重


def response_list(lists: list, page, perpage, totalNum):
    """ 集合的响应数据格式
     :param lists
     :param perpage 每页数据量
     :param page 当前页数
     :param totalNum 总数
     """
    return {
        'lists': lists,
        'page': page,
        'perpage': perpage,
        'totalPageNum': 0 if len(lists) == 0 else int((totalNum + perpage - 1) / perpage),
        'totalNum': totalNum
    }


def model_response(state: bool, code: int = 200, msg="responds suc", extra='', result=None):
    """ model中的返回值，兼容于api response
    :param state model处理是否成功
    """
    return {
        'state': state,
        'code': code,
        'msg': msg,
        'extra': extra,
        'result': result
    }


def response_model(model: dict):
    """ 将兼容于api response的model返回值转换为api response
    """
    return response(model['code'], model['msg'], model['extra'], model['result'])
