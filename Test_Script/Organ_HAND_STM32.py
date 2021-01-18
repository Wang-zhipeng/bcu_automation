import serial
import yaml
import time
from Test_Script import Kernel_ERROR
from Common.log import log
from Common.common_function import OSTool

YamlPath = OSTool.get_current_dir('Test_Data', 'key_config', 'STM32_KV.yml')


class Hand:
    special_dict_revert = {'Shift+1': '!', 'Shift+2': '@', 'Shift+3': '#', 'Shift+4': '$', 'Shift+5': '%',
                           'Shift+6': '^', 'Shift+7': '&', 'Shift+8': '*', 'Shift+9': '(', 'Shift+0': ')',
                           'Shift+-': '_', 'Shift+=': '+', 'Shift+[': '{', 'Shift+]': '}', 'Shift+\\': '|',
                           'Shift+;': ':', "Shift+'": '"', 'Shift+,': '<', 'Shift+.': '>', 'Shift+/': '?',
                           'Shift+a': "A", "Shift+b": "B", "Shift+c": "C", "Shift+d": "D", "Shift+e": "E",
                           "Shift+f": "F", "Shift+g": "G", "Shift+h": "H", "Shift+i": "I", "Shift+j": "J",
                           "Shift+k": "K", "Shift+l": "L", "Shift+m": "M", "Shift+n": "N", "Shift+o": "O",
                           "Shift+p": "P", "Shift+q": "Q", "Shift+r": "R", "Shift+s": "S", "Shift+t": "T",
                           "Shift+u": "U", "Shift+v": "V", "Shift+w": "W", "Shift+x": "X", "Shift+y": "Y",
                           "Shift+z": "Z", "Shift+`": "~"}

    def __init__(self, hand):
        self.log = log
        self.com = serial.Serial(hand[0], hand[1], hand[2], hand[3], hand[4])
        self.res_dic = {}
        self.property = 'Hand'
        with open(YamlPath) as F:
            self.KV_dict = yaml.safe_load(F)

    def key(self, kn, flag=True, t=-1):
        """
        mui mode is always on by default, STM32 not exits key code:"~",
        so it will be filtered
        :param t:
        :param kn: str, key str defined in XXX_KV.yml
        :param flag: boolean, param that you can control whether open mui mode manually
        """
        if self.res_dic and flag:
            key_string = self.res_dic.get(kn, kn)
            kn = self.special_dict_revert.get(key_string, key_string)
            if kn == "~":
                kn = " "
        try:
            kv = str(self.KV_dict[kn]) + '#'
            self.com.write(kv.encode())
            if t == -1:
                time.sleep(1.3)
            else:
                time.sleep(t)
        except Exception as e:
            print(e)
            raise Kernel_ERROR.STM32FunctionError()
        return

    @staticmethod
    def load_from_yml(file):
        with open(file)as f:
            org_dict = yaml.safe_load(f)
            return org_dict

    def mui_vk_prepare(self, path=""):
        if path:
            self.res_dic = self.load_from_yml(path)
        else:
            self.res_dic = {}
        return
