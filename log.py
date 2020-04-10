from config import app


def i(log):
    # print('-------------- log i START---------------')
    if app.config['LOG']:
        print('============== %s ==============' % log)
    # print('-------------- log i END  ---------------')
