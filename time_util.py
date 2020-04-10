import time


def ctime(millisecond=True):
    """ 当前时间 时间戳
     :param millisecond 毫秒
     """
    t = time.time()
    return int(round(t * 1000)) if millisecond else int(t)


def ctime_str(fm='%Y-%m-%d %H:%M:%S'):
    """ 当前时间 中文 """
    return stime(fm=fm)


def stime(seconds=0, fm='%Y-%m-%d %H:%M:%S'):
    """ 格式化时间戳 """
    return time.strftime(fm, time.localtime(seconds if seconds != 0 else ctime(False)))


def timestamp(stime: str, fm='%Y-%m-%d %H:%M:%S'):
    """ 格式化的时间 转换为 时间戳timestamp """
    return int(time.mktime(time.strptime(stime, fm)))


def utc2ctime(timestamp):
    """ 通用协调时(伦敦)转换为北京时间(东八区) """
    return timestamp + 8 * 60 * 60
