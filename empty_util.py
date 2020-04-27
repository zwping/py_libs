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


def isEmptys(*o):
    for d in o:
        if isNotEmpty(d):
            return False
    return True


def isNotEmptys(*o):
    for d in o:
        if isEmpty(d):
            return False
    return True


def isEmptyII(*o):
    for d in o:
        if isEmpty(d):
            return True
    return False


def isNotEmptyII(*o):
    for d in o:
        if isNotEmpty(d):
            return True
    return False
