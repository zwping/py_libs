from jwt_helper import encode_token, decode_token

securt_key = '1u2893usdf~'

def test_生成JWT_TOKEN():
    state, token = encode_token({'user': 'zwping', 'avatar': 'qq.com/1.jpg'}, securt_key, extra={'iss': 'zwp', 'scopes': 'admin'})
    print(state, token)
    assert state

def test_解析JWT_TOKEN():
    t = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ6d3AiLCJpYXQiOjE2MjM3NTQxODksImV4cCI6MTY1NTI5MDE4OSwiZGF0YSI6eyJ1c2VyIjoiendwaW5nIiwiYXZhdGFyIjoicXEuY29tLzEuanBnIn0sInNjb3BlcyI6ImFkbWluIn0.t9RMLTasd-F8760pLWYLRZk0Bv07vYMSD4DmkUO_hMU'
    state, user = decode_token(t, securt_key)
    print(state, user)
    assert state