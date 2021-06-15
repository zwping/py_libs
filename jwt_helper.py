from typing import Tuple
import jwt
import time
import datetime
import json


def encode_token(origin_data: json, secret_key: str, algorithm = 'HS256', exp = None, extra = {}) -> (bool, str):
    """
    payload: 
        iss (issuer)：签发人
        exp (expiration time)：过期时间
        sub (subject)：主题
        aud (audience)：受众
        nbf (Not Before)：生效时间
        iat (Issued At)：签发时间
        jti (JWT ID)：编号
    """
    payload = {
        'iss': 'zwping', 
        'iat': datetime.datetime.now(), 
        'exp': exp if exp else datetime.datetime.now() + datetime.timedelta(days=365),
        'data': origin_data, 
    }
    if extra:
        payload.update(extra)   # 覆盖
    try:
        return True, jwt.encode(payload, secret_key, algorithm)
    except Exception as e:
        return False, e

def decode_token(token, secret_key, algorithm = 'HS256', **kwargs) -> (bool, json):
    try:
        return True, jwt.decode(token, secret_key, algorithm, kwargs)
    except Exception as e:
        return False, e
