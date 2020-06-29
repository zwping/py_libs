from libs.decorator import func_overtime, base_http


class HTTP:

    @staticmethod
    @func_overtime(5)
    def post(base_url, path='', body: dict = None, headers: dict = None, opt=None):
        """ post请求
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
        return HTTP.__post(base_url, path, body, headers, opt)

    @staticmethod
    @base_http()
    def __post(base_url, path='', body=None, headers=None, opt=None, requests_session=None):
        return requests_session.post(base_url + path, data=body, headers=headers, timeout=5)

    @staticmethod
    @func_overtime(5)
    def delete(base_url, path='', body: dict = None, headers: dict = None, opt=None):
        """ post请求
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
        return HTTP.__delete(base_url, path, body, headers, opt)

    @staticmethod
    @base_http()
    def __delete(base_url, path='', body=None, headers=None, opt=None, requests_session=None):
        return requests_session.delete(base_url + path, data=body, headers=headers, timeout=5)

    @staticmethod
    @func_overtime(5)
    def put(base_url, path='', body: dict = None, headers: dict = None, opt=None):
        """ post请求
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
        return HTTP.__put(base_url, path, body, headers, opt)

    @staticmethod
    @base_http()
    def __put(base_url, path='', body=None, headers=None, opt=None, requests_session=None):
        return requests_session.put(base_url + path, data=body, headers=headers, timeout=5)

    @staticmethod
    @func_overtime(10)
    def get(base_url, path='', params: dict = None, headers: dict = None, opt=None):
        """ post请求
        :param base_url 基本请求地址
        :param path 请求路径
        :param params 请求参数
        :param headers 请求头
        :param opt 配置选项
                 max_retries 最大重连次数，默认3次
                 bare 是否直接裸露响应结果，不进行response包装
                 json 是否返回json格式
                 encoding 指定网页编码
                 ...
        """
        return HTTP.__get(base_url, path, params, headers, opt)

    @staticmethod
    @base_http()
    def __get(base_url, path='', params=None, headers=None, opt=None, requests_session=None):
        return requests_session.get(base_url + path, params=params, headers=headers, timeout=10)
