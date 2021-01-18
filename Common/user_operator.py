import os
import platform
import subprocess
import time
import traceback
from Common.log import log
from Common.common_function import kb
if 'windows' in platform.platform().lower():
    __OS = 'Windows'
    import win32net
    import win32netcon
    import win32con
    import win32api
else:
    __OS = 'Linux'


class WinUser:
    def __init__(self, user='test', password='test', **kwargs):
        self.user = user
        self.password = password
        self.domain = kwargs.get('domain', '')
        self.user_info = dict(
            name=self.user,
            password=self.password,
            priv=win32netcon.USER_PRIV_USER,
            home_dir=kwargs.get('home_dir', None),
            comment=kwargs.get('comment', None),
            flag=win32netcon.UF_SCRIPT | win32netcon.UF_DONT_EXPIRE_PASSWD | win32netcon.UF_NORMAL_ACCOUNT,
            script_path=kwargs.get('script_path', None)
        )
        self.group_info = dict(
            domainandname=self.user
        )

    def isExists(self):
        result = win32net.NetUserEnum(None, 0, win32netcon.FILTER_NORMAL_ACCOUNT, 0)
        for user in result[0]:
            if user['name'].upper() == self.user.upper():
                return True
        return False

    def delete_user(self):
        try:
            win32net.NetUserDel(None, self.user)
        except:
            pass

    def add_user(self, ):
        try:
            if self.isExists():
                self.delete_user()
            win32net.NetUserAdd(None, 1, self.user_info)
        except:
            log.info('Add new user [{}] fail, meet exception:\n{}'.format(self.user_info['name'],
                                                                          traceback.format_exc()))
            pass

    def change_password(self, new_password):
        win32net.NetUserChangePassword(None, self.user, self.password, new_password)

    def add_user_to_group(self, group='Administrators'):
        try:
            win32net.NetLocalGroupAddMembers(None, group, 3, [self.group_info])
        except:
            pass

    def set_auto_logon(self):
        root = win32con.HKEY_LOCAL_MACHINE
        key = win32api.RegOpenKeyEx(root, 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon', 0,
                                    win32con.KEY_ALL_ACCESS | win32con.KEY_WOW64_64KEY | win32con.KEY_WRITE)
        win32api.RegSetValueEx(key, "DefaultUserName", 0, win32con.REG_SZ, self.user)
        win32api.RegSetValueEx(key, "DefaultPassWord", 0, win32con.REG_SZ, self.password)
        if self.domain != "":
            win32api.RegSetValueEx(key, "DefaultDomain", 0, win32con.REG_SZ, self.domain)


class LinuxUser:
    def __init__(self, user='admin', password='1', **kwargs):
        self.user = user
        self.password = password
        self.domain = kwargs.get('domain', '')

    @staticmethod
    def current_user():
        s = os.path.exists('/var/run/hptc-admin')
        if s:
            return 'admin'
        else:
            return 'user'

    @staticmethod
    def check_has_root_password():
        s = subprocess.call("hptc-passwd-default --root --check >/dev/null 2>&1", shell=True)
        if s:
            return True
        else:
            return False

    def switch_user(self):
        if self.user == 'user':
            if self.current_user() == 'user':
                log.info("now is user mode")
                return True
            if self.current_user() == 'admin':
                os.popen('hptc-switch-admin')
                time.sleep(2)
                if self.current_user() == 'user':
                    log.info("switch to user mode success")
                    return True
                else:
                    log.error("switch to user mode fail")
                    return False
        if self.user == 'admin':
            if self.current_user() == 'admin':
                log.info("now is admin mode")
                return True
            if self.current_user() == 'user':
                if self.check_has_root_password():
                    os.popen('hptc-switch-admin')
                    time.sleep(2)
                    kb.type_string(self.password)
                    time.sleep(1)
                    kb.tap_key(kb.enter_key)
                    time.sleep(1)
                    if self.current_user() == 'admin':
                        log.info("switch to admin mode success")
                        return True
                    else:
                        kb.tap_key(kb.enter_key)
                        time.sleep(1)
                        kb.type_string('root')
                        time.sleep(1)
                        kb.tap_key(kb.tab_key)
                        time.sleep(1)
                        kb.type_string(self.password)
                        time.sleep(1)
                        kb.tap_key(kb.enter_key)
                        time.sleep(1)
                        if self.current_user() == 'admin':
                            log.info("switch to admin mode success")
                            return True
                        else:
                            log.info("switch to admin mode fail")
                            return False
                else:
                    os.popen('hptc-switch-admin')
                    time.sleep(2)
                    kb.type_string(self.password)
                    time.sleep(1)
                    kb.tap_key(kb.tab_key)
                    time.sleep(1)
                    kb.type_string(self.password)
                    time.sleep(1)
                    kb.tap_key(kb.tab_key)
                    time.sleep(2)
                    if self.current_user() == 'admin':
                        log.info("switch to admin mode success")
                        return True
                    else:
                        log.error("switch to admin mode fail")
                        return False
