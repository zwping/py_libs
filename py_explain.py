import abc


class PyExplain(metaclass=abc.ABCMeta):
    """ py文件说明
    统一出处，便于对文件内的功能统计及分类
    """

    @abc.abstractmethod
    def file_explain(self):
        # 当前文件用处
        pass

    @abc.abstractmethod
    def why_func(self):
        # 实现了哪些功能
        pass
