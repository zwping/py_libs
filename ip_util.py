from libs.empty_util import isEmpty


def realIp(request):
    """ 获取请求中的真实ip
    """
    if isEmpty(request):
        return ''
    try:
        return request.headers['X-Forwarded-For']
    except Exception:
        try:
            return request.headers['X-Real-IP']
        except Exception:
            return request.remote_addr
