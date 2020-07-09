from libs.decorator import func_overtime, base_http


class HTTP:

    @staticmethod
    @func_overtime(5)
    @base_http()
    def post(base_url, path='', body: dict = None, headers: dict = None, opt: dict = None):
        """ post请求 引导式开发
        :param base_url 基本请求地址
        :param path 请求路径
        :param body 请求体
        :param headers 请求头
        :param opt 配置选项
                 max_retries 最大重连次数，默认3次
                 bare 是否直接裸露响应结果，不进行response包装
                 json 是否返回json格式
                 encoding 指定网页编码
                 ...
        """
        return opt['requests_session'].post(base_url + path, data=body, headers=headers, **opt['kw'])

    @staticmethod
    @func_overtime(5)
    @base_http()
    def delete(base_url, path='', body: dict = None, headers: dict = None, opt=None):
        """ delete请求 """
        return opt['requests_session'].delete(base_url + path, data=body, headers=headers, **opt['kw'])

    @staticmethod
    @func_overtime(5)
    @base_http()
    def put(base_url, path='', body: dict = None, headers: dict = None, opt=None):
        """ put请求 """
        return opt['requests_session'].put(base_url + path, data=body, headers=headers, **opt['kw'])

    @staticmethod
    @func_overtime(10)
    @base_http()
    def get(base_url: str, path: str = '', params: dict = None, headers: dict = None, opt: dict = None):
        """ get请求 """
        return opt['requests_session'].get(base_url + path, params=params, headers=headers, **opt['kw'])
