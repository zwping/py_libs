def secure_str(s: str, *filter):
    """ 安全字符 - 解决存储后比对不正确情况
    :param s 原始字符串
    :param filter 自定义过滤条件
    :return 安全字符串
    """
    s = s.strip()
    secure = [
        '\u200b',  # 零宽字符
    ]
    for d in secure:
        s = s.replace(d, '')
    for d in filter:
        s = s.replace(d, '')
    return s
