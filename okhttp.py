import requests
from requests.adapters import HTTPAdapter

from libs.decorator import func_overtime
from libs.response_standard import response
from libs.log import i


class HTTP:

    @staticmethod
    @func_overtime(10)
    def get(base_url, path='', params=None, headers=None, json=True, max_retries=3):
        if params is None:
            params = []
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=max_retries))
            s.mount('https://', HTTPAdapter(max_retries=max_retries))
            r = s.get(base_url + path, params=params, headers=headers, timeout=10)
            i("http get : %s%s - %d - %s" % (base_url, path, r.status_code, r.encoding))
            if r.status_code == 200:
                return response(result=r.json() if json else r.text, is_response=False)
            else:
                return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text), is_response=False)
        except Exception as e:
            i(e)
            import traceback
            return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)

    @staticmethod
    @func_overtime(5)
    def post(base_url, path='', params=None, headers=None, json=True, max_retries=3):
        if params is None:
            params = []
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=max_retries))
            s.mount('https://', HTTPAdapter(max_retries=max_retries))
            r = s.post(base_url + path, data=params, headers=headers, timeout=5)
            i("http post : %s%s - %d" % (base_url, path, r.status_code))
            if r.status_code == 200:
                return response(result=r.json() if json else r.text, is_response=False)
            else:
                return response(501, "service error (501)", '%s---%s' % (r.status_code, r.text))
        except Exception as e:
            i(e)
            import traceback
            return response(501, "service error (501-1)", traceback.format_exc(), is_response=False)
