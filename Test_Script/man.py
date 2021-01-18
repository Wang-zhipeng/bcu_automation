import time
import yaml
from Common.common_function import get_current_dir
from Test_Script import Organ_HAND_MagicKey, Kernel_ERROR, Organ_HAND_STM32
from Common.log import log

interval_1 = 0.3
interval_2 = 1
interval_3 = 3
threshold = 0.95


class ManCFG:
    def __init__(self):
        """
        instantiated camera/magic key/video card
        """
        yaml_path = get_current_dir('Test_Data', 'man_config.yml')
        with open(yaml_path) as F:
            config_dict = yaml.safe_load(F)
        try:
            self.man_config = config_dict['1']
        except KeyError:
            raise Kernel_ERROR.ManSiteError()

    def magic_key(self):
        if self.man_config[1][0] == 'MagicKey':
            try:
                return Organ_HAND_MagicKey.MagicKey(self.man_config[1][1])
            except Exception:
                raise Kernel_ERROR.MagicKeyNotExistError()
        elif self.man_config[1][0] == 'Null':
            return None
        else:
            return None

    def stm32_key(self):
        if self.man_config[1][2] == 'STM32':
            try:
                return Organ_HAND_STM32.Hand(self.man_config[1][3])
            except Exception:
                raise Kernel_ERROR.STM32NotExistError()
        elif self.man_config[1][2] == 'Null':
            return None
        else:
            return None


class Man:
    def __init__(self):
        """
        Encapsulation of Key and camera
        hand: magic key
        hand_aid: stm32 key
        """
        self.mc = ManCFG()
        self.magic_key = self.mc.magic_key()
        self.smt32_key = self.mc.stm32_key()

    def __push_key(self, kn, hand_type='HAND'):
        # hand: magic key
        # hand_aid: smt32 key
        if hand_type == 'HAND':
            self.magic_key.key(kn)
        elif hand_type == 'HAND_AID':
            self.smt32_key.key(kn)

    def press_key(self, key_name, n=1, hand_type='HAND'):
        """
        :param key_name:
        :param n: count
        :param hand_type
        :return:
        """
        for i in range(n):
            log.info('Push The Key : [' + str(key_name) + ']')
            self.__push_key(key_name, hand_type)

    def press_key_delay(self, key_name, delay=interval_3, hand_type='HAND'):
        # delay seconds after press a key
        log.info('Push The Key : [{}] and Delay {}'.format(str(key_name), delay))
        self.__push_key(key_name, hand_type)
        time.sleep(delay)

    def press_key_list(self, key_list, t=interval_2, hand_type='HAND'):
        for key_name in key_list:
            log.info('Push The Key : [' + str(key_name) + ']')
            self.__push_key(key_name, hand_type)
            time.sleep(t)

    def input_string(self, string, hand_type='HAND'):
        log.info('Enter The Text : [' + string + ']')
        for i in string:
            self.__push_key(i, hand_type)
