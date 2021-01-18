from pymouse import PyMouse
from pykeyboard import PyKeyboard
from pyautogui import screenshot
from Common.common_function import *
from Common.picture_operator import wait_element

mouse = PyMouse()
keyboard = PyKeyboard()


def logFile(file, msg):
    """
    :param file:
    :param msg:
    :return:
    """
    with open(file, 'a') as f:
        f.write('[{}]:{}\n'.format(time.ctime(), msg))


def getPlatform():
    """
    :return:  eg:Linux-5.3.6-hp-x86_64-with-ThinPro-7.1.0-None
    """
    return platform.platform()  # [0:10]


def press_keys(keys, wait=0.5):
    keyboard.press_keys(keys)
    time.sleep(wait)


def press_key(key, wait=0.5):
    keyboard.press_key(key)
    time.sleep(0.1)
    keyboard.release_key(key)
    time.sleep(wait)


def press_hotkey(*keys):
    for key in keys:
        keyboard.press_key(key)
        time.sleep(0.02)
    for key in keys:
        keyboard.release_key(key)
        time.sleep(0.02)


def tap_key(key, wait=0.5):
    keyboard.tap_key(key)
    time.sleep(wait)
    return


def type_string(char_string, wait=0.5):
    keyboard.type_string(char_string)
    time.sleep(wait)
    return


def click(x, y, num=1):
    return mouse.click(x, y, n=num)


def get_root_path(path=None, back=False):
    """
    adapt to different scenarios to get path
    :return: abs path
    """
    root = os.path.dirname(os.path.realpath(sys.argv[0]))
    if path:
        if back:
            root = os.path.split(root)[0]
        elif 'dist' in root:
            root = os.path.split(root)[0]
        path = os.path.join(root, path)
    else:
        path = root
    if '.' not in path and path[-1] != "/":
        path = path + '/'
    return path


def check_object_exist(filename, cycle=3, offset=(10, 10), back=False):
    """
    if you want to debug in main,back = True in get_root_path
    """
    path = get_root_path("Test_Data/td_precheck/Thinpro7.1/{}".format(filename), back=back)
    response = wait_element(path, cycle=cycle, offset=offset)
    print(response)
    return response


def into_admin(back=False):
    response1 = check_object_exist("all.png", back=back)
    response2 = check_object_exist("admin_password.png", offset=(60, 10), back=back)
    if response1:
        rs, shape = response1
        click(*rs)
        type_string("1")
        tap_key(keyboard.tab_key, 1)
        type_string("1")
        tap_key(keyboard.enter_key)
    elif response2:
        rs, shape = response2
        click(*rs)
        type_string("1", 0.5)
        tap_key(keyboard.enter_key)
    else:
        path = get_root_path("Test_Report/img", back=back)
        if not os.path.exists(path):
            os.mkdir(path)
        screenshot(get_root_path("Test_Report/img/error_admin.jpg", back=back))
    return


def global_switch_to_admin(loop=3, back=False):
    with os.popen("ls /var/run |grep hptc-admin") as f:
        res = f.read()
    if not res:
        os.popen("hptc-switch-admin")
        into_admin(back=back)
        f = os.popen("ls /var/run |grep hptc-admin")
        if f.read():
            f.close()
            return True
    if loop > 0:
        loop -= 1
        return global_switch_to_admin(loop, back=back)
    return False


def events(testevent, params=None, callbacktest=None, cbparams=None, assertion=True, annotation=None):
    """
    involve two test that if you want to execute some functions like a serious of events
    the method contains a event of logging yaml result
    :param testevent: function, a check test mainly;return a tuple((x,y),(x,y,z))
    :param params: string , a test pic name
    :param callbacktest: function
    :param cbparams:string,we offer a "fromtest" string for you to get the result return from testevent
    :param assertion:boolean that you estimate your result
    :param annotation:tuple:(funcname,picname) if fail, you can customise your error info into yaml note and console
                        eg.
    :return:
    """
    testname = testevent.__name__
    testparams = testevent(params)
    paramsname = params.split(".")[0]
    steps = {'step_name': testname,
             'result': 'PASS',
             'expect': "",  # can be string or pic path
             'actual': '',  # can be string or pic path
             'note': ""}
    if annotation:
        length = len(annotation)
        if callbacktest:
            if length == 2:
                a, b = annotation
                notes = "error in {}, events({},{}) : {}".format(a, testname, params, b)
            elif length == 1:
                a = annotation[0]
                notes = "error in {}, events({},{}) : can't find {}".format(a, testname, params, paramsname)
            else:
                notes = "error ! ,events({},{})".format(testname, params)
        else:
            if length == 2:
                a, b = annotation
                notes = "error in {}, events({},{}) : {}".format(a, testname, params, b)
            elif length == 1:
                a = annotation[0]
                notes = "error in {}, events({},{}) : {} can't work or not matched".format(a, testname, params,
                                                                                           paramsname)
            else:
                notes = "error in, events({},{})".format(testname, params)
    else:
        notes = "error, events({},{}) ".format(testname, params)
    flag = True if testparams else False
    try:
        assert flag == assertion, notes
        print(testname, testparams, assertion, flag)
        if callbacktest:
            if cbparams.lower() == "fromtest":
                return callbacktest(testparams)
            else:
                return callbacktest(cbparams)
    except AssertionError as e:
        log.error('{} {} {} {} exception: \n{}'.format(testname, testparams, assertion, flag, e))
        tname = "{}-{}".format(testname, params)
        path = get_root_path("Test_Report/img")
        if not os.path.exists(path):
            os.mkdir(path)
        screenshot(get_root_path("Test_Report/img/{}.jpg".format(tname)))
        steps['result'] = "Fail"
        steps['actual'] = 'img/' + tname
        steps['note'] = notes
        raise AssertionError(notes + "???")
    finally:
        ip = get_ip()
        path = get_root_path("Test_Report/{}.yaml".format(ip))
        update_cases_result(path, 'check_edocs_app', steps)
    return True


if __name__ == '__main__':
    _path = get_root_path("Test_Report/img")
    if not os.path.exists(_path):
        os.mkdir(_path)
    screenshot(get_root_path("Test_Report/img/{}.jpg".format("name")))
    print("")
