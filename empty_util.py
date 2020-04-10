def isEmpty(o):
    if o is None:
        return True
    elif type(o) is str and len(o) == 0:
        return True
    elif type(o) is tuple and len(o) == 0:
        return True
    elif type(o) is dict and len(o) == 0:
        return True
    elif type(o) is list and len(o) == 0:
        return True
    elif type(o) is set and len(o) == 0:
        return True
    else:
        return o is None


def isNotEmpty(o):
    return not isEmpty(o)
