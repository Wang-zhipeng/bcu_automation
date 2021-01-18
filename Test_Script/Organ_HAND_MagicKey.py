import ctypes
import time
import traceback
from Common.exception import MagicKeyFunctionError
from Common.common_function import OSTool
from Common.file_operator import YamlOperator
from Common.log import log


class MagicKey:
    """
    if you want to use mui, please use function mui_vk_prepare(path)
    HAND_MagicKey : device manager  -> human interface devices -> usb input device -> hardware ids -> vid,pid
    """

    def __init__(self, vp):
        self.vid = vp[0]
        self.pid = vp[1]
        self.api = ctypes.windll.LoadLibrary(OSTool.get_current_dir("Test_Utility", "msdk.dll"))
        self.key_handle = self.api.M_Open_VidPid(self.vid, self.pid)
        self.vk_dict_path = OSTool.get_current_dir(r"Test_Data\key_config\MagicKey_KV.yml")
        self.vk_dict = YamlOperator(self.vk_dict_path).read()
        self.res_dic = {}
        self.special_dict = {'!': 'Shift+1', '@': 'Shift+2', '#': 'Shift+3', '$': 'Shift+4', '%': 'Shift+5',
                             '^': 'Shift+6', '&': 'Shift+7', '*': 'Shift+8', '(': 'Shift+9', ')': 'Shift+0',
                             '_': 'Shift+-', '+': 'Shift+=', '{': 'Shift+[', '}': 'Shift+]', '|': 'Shift+\\',
                             'A': 'Shift+a', 'B': "Shift+b", 'C': 'Shift+c', 'D': 'Shift+d', 'E': 'Shift+e',
                             'F': 'Shift+f', 'G': "Shift+g", 'H': 'Shift+h', 'I': 'Shift+i', 'J': 'Shift+j',
                             'K': 'Shift+k', 'L': "Shift+l", 'M': 'Shift+m', 'N': 'Shift+n', 'O': 'Shift+o',
                             'P': 'Shift+p', 'Q': "Shift+q", 'R': 'Shift+r', 'S': 'Shift+s', 'T': 'Shift+t',
                             'U': 'Shift+u', 'V': "Shift+v", 'W': 'Shift+w', 'X': 'Shift+x', 'Y': 'Shift+y',
                             'Z': 'Shift+z',
                             ':': 'Shift+;', '"': "Shift+'", '<': 'Shift+,', '>': 'Shift+.', '?': 'Shift+/'}
        self.special_dict_revert = {'Shift+1': '!', 'Shift+2': '@', 'Shift+3': '#', 'Shift+4': '$', 'Shift+5': '%',
                                    'Shift+6': '^', 'Shift+7': '&', 'Shift+8': '*', 'Shift+9': '(', 'Shift+0': ')',
                                    'Shift+-': '_', 'Shift+=': '+', 'Shift+[': '{', 'Shift+]': '}', 'Shift+\\': '|',
                                    'Shift+;': ':', "Shift+'": '"', 'Shift+,': '<', 'Shift+.': '>', 'Shift+/': '?',
                                    'Shift+a': "A", "Shift+b": "B", "Shift+c": "C", "Shift+d": "D", "Shift+e": "E",
                                    "Shift+f": "F", "Shift+g": "G", "Shift+h": "H", "Shift+i": "I", "Shift+j": "J",
                                    "Shift+k": "K", "Shift+l": "L", "Shift+m": "M", "Shift+n": "N", "Shift+o": "O",
                                    "Shift+p": "P", "Shift+q": "Q", "Shift+r": "R", "Shift+s": "S", "Shift+t": "T",
                                    "Shift+u": "U", "Shift+v": "V", "Shift+w": "W", "Shift+x": "X", "Shift+y": "Y",
                                    "Shift+z": "Z", "Shift+`": "~"}

    def __get_vk_code(self, vk_name):
        if len(vk_name) == 1 and vk_name.isalpha():
            vk_code = self.vk_dict[vk_name.lower()]
        else:
            vk_code = self.vk_dict[vk_name]
        return vk_code

    def __press(self, vk_name, n=1, wait=1):
        vk_code = self.__get_vk_code(vk_name)
        self.api.M_KeyPress2(self.key_handle, vk_code, n)
        time.sleep(wait)  # max delay between two M_KeyPress2 is 600ms

    def __get_caps_state(self):
        caps_dict = {0: 'off', 1: 'on', -1: 'fail'}
        key_caps = self.api.M_CapsLockLedState(self.key_handle)
        return caps_dict[key_caps]

    def __press_key(self, vk_name):
        if vk_name.isalpha() and len(vk_name) == 1:
            caps_state = self.__get_caps_state()
            if vk_name.isupper():
                if caps_state == 'off':
                    self.api.M_KeyPress2(self.key_handle, 20, 1)  # press caps lock
                elif caps_state == 'fail':
                    print('failed to get caps state')
            else:
                if caps_state == 'on':
                    self.api.M_KeyPress2(self.key_handle, 20, 1)  # press caps lock
                elif caps_state == 'fail':
                    print('fail to get caps state')
        self.__press(vk_name)

    def __press_hot_key(self, key_list):
        self.api.M_ReleaseAllKey(self.key_handle)
        for key in key_list:
            key_code = self.__get_vk_code(key)
            self.api.M_KeyDown2(self.key_handle, key_code)
        self.api.M_ReleaseAllKey(self.key_handle)

    def key(self, key_str):  # A
        log.info("Press key: {}".format(key_str))
        if self.res_dic:
            key = key_str  # 1 #A
            key_change = self.special_dict_revert.get(key_str, key_str)  # True： B false ："A"
            key_string = self.res_dic.get(key_change, key_change)  # True: "Shift+q" false :B
            if key_change == key_string:
                key_str = key
            else:
                key_str = key_string

        try:
            key_list = key_str.split('+')
            length = len(key_list)
            if length == 1:
                if key_str in self.special_dict.keys():
                    value = self.special_dict[key_str]
                    self.__press_hot_key(value.split('+'))
                else:
                    self.__press_key(key_str)
            elif length > 1:
                self.__press_hot_key(key_list)
            else:
                print('invalid')
        except:
            log.debug("Error at press key {}, Exception:\n{}".format(key_str, traceback.format_exc()))
            raise MagicKeyFunctionError("Error at press key {}".format(key_str))

    def __mui_string_match(self, string):
        index = 0
        string_li = list(string)
        for i in string_li:
            val = self.res_dic.get(i, i)
            if "shift" in val.lower() and val != i:
                ref = self.special_dict_revert.get(val)
                string_li[index] = ref
            else:
                string_li[index] = val
            index += 1
        string = "".join(string_li)
        return string

    def __check_abs_position(self, x, y):
        rs = self.api.M_ResolutionUsed(self.key_handle, x, y)
        if rs == 0:
            return True
        else:
            return False

    def move_to(self, x, y):
        abs_support = self.__check_abs_position(1600, 900)
        if abs_support:
            self.api.M_MoveTo3(self.key_handle, x, y)
        else:
            print('not support abs')

    def left_click(self, n):
        self.api.M_LeftClick(self.key_handle, n)

    def left_doubleclick(self, n=1):
        self.api.M_LeftDoubleClick(self.key_handle, n)

    def right_click(self, n=1):
        self.api.M_RightClick(self.key_handle, n)

    def mui_vk_prepare(self, path=""):
        if path:
            self.res_dic = YamlOperator(path).read()
        else:
            self.res_dic = {}
        return

    def switch_layout(self):
        self.key("Shift+Alt")
        return
