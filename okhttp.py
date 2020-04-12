import requests

from libs.decorator import func_overtime
from libs.response_standard import response
from libs.log import i


class HTTP:

    @staticmethod
    @func_overtime(5)
    def get(base_url, path='', params=None, headers=None, json=True):
        if params is None:
            params = []
        try:
            r = requests.get(base_url + path, params=params, headers=headers, timeout=5)  # todo params功能未进行有效的验证
            i("http get : %s%s - %d" % (base_url, path, r.status_code))
            if r.status_code != 200:
                return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text))
            return response(result=r.json() if json else r.text, is_response=False)
        except Exception as e:
            import traceback
            return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)

    @staticmethod
    @func_overtime(5)
    def post(base_url, path='', params=None, headers=None, json=True):
        if params is None:
            params = []
        try:
            r = requests.post(base_url + path, data=params, headers=headers, timeout=5)
            i("http post : %s%s - %d" % (base_url, path, r.status_code))
            if r.status_code != 200:
                return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text))
            return response(result=r.json() if json else r.text, is_response=False)
        except Exception as e:
            import traceback
            return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)
