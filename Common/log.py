import os
import sys
import time
import yaml
from mss import mss


def capture_screen(file_name):
    dir_path = os.path.dirname(file_name)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with mss() as capture:
        capture.shot(mon=-1, output=file_name)
    return file_name


def get_current_dir(*args):
    """
    :param args: use like os.path.join(path, *path)
    :return: absolute path
    For Linux OS
    """
    current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if args:
        path = os.path.join(current_path, *args)
    else:
        path = current_path
    return "/".join(path.split("\\"))


class __Logging:
    def __init__(self, output=True, divide='Hour'):
        """
        :param output: default when logging file also print msg, if False will not print
        :param divide: default create new log file every hour, if value == 'day', create file every day
        """
        self.__report_path = os.path.join(get_current_dir(), 'Test_Report')
        self.__log_path = os.path.join(self.__report_path, 'log')
        self.divide = divide
        if not os.path.exists(self.__report_path):
            os.mkdir(self.__report_path)
        if not os.path.exists(self.__log_path):
            os.mkdir(self.__log_path)
        self.style = '\033[1;31;1m#msg#\033[0m'
        self.print = output

    def log(self, rank, _log):
        # dynamic refresh file name according time each hour
        if self.divide.lower() == 'day':
            log_name = time.strftime("%Y-%m-%d", time.localtime()) + ".log"
        elif 'mb' in self.divide.lower():
            log_name = time.strftime("%Y-%m-%d-%H-%M", time.localtime()) + ".log"
            file_size = int(self.divide.lower().replace('mb', ''))
            if os.path.getsize(log_name) > file_size * 1024 * 1024:
                log_name = time.strftime("%Y-%m-%d-%H-%M", time.localtime()) + ".log"
        else:
            log_name = time.strftime("%Y-%m-%d-%H", time.localtime()) + ".log"
        log_file_path = os.path.join(self.__log_path, log_name)
        if not os.path.exists(self.__log_path):
            os.makedirs(self.__log_path)

        cur_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print_msg = "{} \t {} \t {}".format(cur_time, rank, _log)
        line = "[{}] \t".format(cur_time) + print_msg + '\n'

        if not os.access(log_file_path, os.F_OK):
            with open(log_file_path, "w", encoding='utf-8') as f:
                f.writelines(line)
        else:
            with open(log_file_path, "a", encoding='utf-8') as f:
                f.writelines(line)

        if self.print:
            print(self.style.replace('#msg#', print_msg))


class Logger(__Logging):
    def __init__(self, output=True):
        super().__init__(output=output)
        self.log_level = self.__read_debug_level()

    @staticmethod
    def __analyze_name(name):
        file_name = name
        if os.path.exists(file_name):
            name, ext = os.path.splitext(file_name)
            file_name = name + time.strftime("%H%M%S", time.localtime()) + ext
        return file_name

    @staticmethod
    def __read_debug_level():
        config_path = get_current_dir('Test_Data', 'td_common', 'global_config.yml')
        if not os.path.exists(config_path):
            return 3  # error level
        else:
            with open(config_path) as f:
                return int(yaml.safe_load(f)['log']['log_level'])

    def info(self, msg, name=''):
        if self.log_level > 2:
            rank = '[INFO]'
            self.style = '\033[1;21;1m#msg#\033[0m'
            self.log(rank, msg)
            if name != '':
                capture_screen(self.__analyze_name(name))

    def warning(self, msg, name=''):
        if self.log_level > 1:
            self.style = '\033[1;33;1m#msg#\033[0m'
            rank = '[WARNING]'
            self.log(rank, msg)
            if name != '':
                capture_screen(self.__analyze_name(name))

    def error(self, msg, name=''):
        if self.log_level > 0:
            self.style = '\033[1;31;1m#msg#\033[0m'
            rank = '[ERROR]'
            self.log(rank, msg)
            if name != '':
                capture_screen(self.__analyze_name(name))

    def debug(self, msg, name=''):
        if self.log_level > 3:
            self.style = '\033[1;21;1m#msg#\033[0m'
            rank = '[DEBUG]'
            self.log(rank, msg)
            if name != '':
                capture_screen(self.__analyze_name(name))


log = Logger()
