def realIp(request):
    try:
        return request.headers['X-Forwarded-For']
    except Exception:
        try:
            return request.headers['X-Real-IP']
        except Exception:
            return request.remote_addr
