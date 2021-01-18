import win32api
import win32con
import os
from Common.log import log


class RegistryTools:
    """
    class instance is only tool for registry operator,
    if want to manage any key or value,
    must get a key instance with method open(path)
    """

    def __init__(self, root='local'):
        if root.upper() == 'LOCAL':
            self.root = win32con.HKEY_LOCAL_MACHINE
        else:
            self.root = win32con.HKEY_CURRENT_USER
        self.flags = win32con.WRITE_OWNER | win32con.KEY_WOW64_64KEY | win32con.KEY_ALL_ACCESS
        self.reg_type = {0: win32con.REG_SZ, 1: win32con.REG_DWORD, 2: win32con.REG_BINARY}

    def open(self, path):
        # return a key
        key = win32api.RegOpenKeyEx(self.root, path, 0, self.flags)
        return key

    def is_key_exist(self, path):
        try:
            return self.open(path)
        except:
            return False

    @staticmethod
    def is_value_exist(key, value):
        try:
            return win32api.RegQueryValueEx(key, value)
        except:
            return False

    @staticmethod
    def list_key(key):
        sub_key_list = []
        if key:
            for sub_key in win32api.RegEnumKeyEx(key):
                # win32api.RegDeleteKeyEx(sub_key)
                sub_key_list.append(sub_key[0])
            return sub_key_list
        else:
            return None

    @staticmethod
    def list_value(key):
        try:
            i = 0
            while 1:
                print(win32api.RegEnumValue(key, i))
                i += 1
        except:
            pass

    def create_key(self, path):
        key, _ = win32api.RegCreateKeyEx(self.root, path, self.flags)
        return key

    def del_key(self, path):
        key = self.open(path)
        m_item = win32api.RegEnumKeyEx(key)
        if not m_item:
            reg_parent, subkey_name = os.path.split(path)  # 获得父路径名字 和自己的名字，而不是路径
            try:
                key_parent = self.open(reg_parent)  # 看这个节点是否可被访问
                win32api.RegDeleteKeyEx(key_parent, subkey_name)  # 删除这个节点
                return
            except Exception as e:
                print("Bently 被拒绝访问")
                return

        for item in win32api.RegEnumKeyEx(key):  # 递归加子节点
            strRecord = item[0]  # 采用key的第一个节点，item里面是元组，获取第一个名字。就是要的子项名字
            newpath = path + '\\' + strRecord
            self.del_key(newpath)

            # 删除父节点
        root_parent, child_name = os.path.split(path)
        try:  # 看这个节点是否可被访问
            current_parent = self.open(root_parent)
            win32api.RegDeleteKeyEx(current_parent, child_name)
        except Exception:
            print("Bently 被拒绝访问")
            return

    def clear_sub_keys(self, path):
        key = self.is_key_exist(path)
        for sub_key in self.list_key(key):
            self.del_key(r'{}\{}'.format(path, sub_key))
        self.close(key)

    def get_value(self, key, value):
        if self.is_value_exist(key, value):
            _value, _type = self.is_value_exist(key, value)
            return _value, _type
        else:
            return None

    def create_value(self, key, value_name, reg_type=0, content=''):
        win32api.RegSetValueEx(key, value_name, 0, self.reg_type[reg_type], content)

    @staticmethod
    def del_value(key, value):
        try:
            win32api.RegDeleteValue(key, value)
        except:
            print('Value {} not Exist'.format(value))

    @staticmethod
    def close(key):
        win32api.RegCloseKey(key)
