def isEmpty(o):
    if o is None:
        return True
    elif type(o) is str and len(o) == 0:
        return True
    elif isinstance(o, tuple) and len(o) == 0:
        return True
    elif isinstance(o, dict) and len(o) == 0:
        return True
    elif isinstance(o, list) and len(o) == 0:
        return True
    elif isinstance(o, set) and len(o) == 0:
        return True
    else:
        return o is None


def isNotEmpty(o):
    return not isEmpty(o)
