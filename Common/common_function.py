import copy
import locale
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import pyautogui
import pykeyboard
import pymouse
import yaml
from win32com.client import GetObject
from Common.file_operator import YamlOperator
from Common.log import log, get_current_dir

if 'windows' in platform.platform().lower():
    OS = 'Windows'
else:
    OS = 'Linux'
mouse = pymouse.PyMouse()
kb = pykeyboard.PyKeyboard()


def check_ip_yaml():
    ip_yaml_path = get_current_dir('Test_Data', 'ip.yml')
    if os.path.exists(ip_yaml_path):
        with open(ip_yaml_path, encoding='utf-8') as f:
            ip = yaml.safe_load(f)
            if ip:
                return ip[0]
            else:
                return '127.0.0.1'
    else:
        f = open(ip_yaml_path, 'w')
        f.close()
        with open(ip_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump([OSTool.get_ip()], f, default_flow_style=False)
        return OSTool.get_ip()


class OSTool:
    @classmethod
    def get_os_bit(cls):
        wmiobj = GetObject('winmgmts:/root/cimv2')
        operating_systems = wmiobj.ExecQuery("Select * from Win32_OperatingSystem")
        for o_s in operating_systems:
            os_bit = o_s.OSArchitecture
            if '64' in os_bit:
                os_type = 'x64'
            elif '32' in os_bit:
                os_type = 'x86'
            else:
                os_type = 'incorrect_os_type'
            return os_type

    @classmethod
    def get_ip(cls):
        if OS == 'Linux':
            wired_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/eth0/IPv4/status")
            if wired_status == "1":
                sys_eth0_ip = subprocess.getoutput("ifconfig | grep eth0 -A 1 | grep -i 'inet addr'")
                eth0_ip = sys_eth0_ip.strip().split()[1].split(":")[1]
                return eth0_ip
            wireless_status = subprocess.getoutput("mclient --quiet get tmp/NetMgr/wlan0/IPv4/status")
            if wireless_status == "1":
                sys_wlan0_ip = subprocess.getoutput("ifconfig | grep wlan0 -A 1 | grep -i 'inet addr'")
                wlan0_ip = sys_wlan0_ip.strip().split()[1].split(":")[1]
                return wlan0_ip
            else:
                with os.popen("ifconfig") as f:
                    string = f.read()
                    eth0_ip = re.findall(r"eth0.*?inet.*?(\d+\.\d+\.\d+\.\d+).*?lo", string, re.S)
                    if eth0_ip:
                        eth0_ip = eth0_ip[0]
                    else:
                        return
                return eth0_ip
        else:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip

    @classmethod
    def get_platform(cls):
        # platform for TC, eg. T630 mt42
        if OS == 'Linux':
            plat_form = subprocess.getoutput('/usr/bin/hptc-hwsw-id --hw')
            if plat_form == '':
                log.info('plat_form is empty.')
            return plat_form
        else:
            wmi_obj = GetObject(r'winmgmts:\\.\root\cimv2')
            wucol = wmi_obj.ExecQuery("Select Model from Win32_ComputerSystem")
            plat_form = 'Error'
            for s in wucol:
                plat_form = s.Model.lower()
                break
            return plat_form

    @classmethod
    def get_current_dir(cls, *args):
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

    @classmethod
    def get_folder_items(cls, path, **kwargs):
        """
        get folder items without recursion
        :param path: str, support abs path and relative path
        :return:
        safe_mode: if folder not exist, create
        filter_name: get file by filter name
        file_only: ignore folder
        """
        safe_mode = kwargs.get("safe_mode", True)
        filter_name = kwargs.get("filter_name", "")
        file_only = kwargs.get("file_only", False)
        file_path = "/".join(os.path.realpath(path).split("\\"))
        if not os.path.exists(file_path) and safe_mode:
            os.makedirs(file_path)
        file_list = os.listdir(file_path)
        if filter_name:
            filter_name_list = []
            for i in file_list:
                if filter_name.upper() in i.upper():
                    filter_name_list.append(i)
            file_list = filter_name_list
        if file_only:
            for i in copy.deepcopy(file_list):
                dir_path = file_path + "/{}".format(i)
                if os.path.isdir(dir_path):
                    file_list.remove(i)
        return file_list

    @classmethod
    def get_folder_items_recursion(cls, path, **kwargs):
        """
        get all items of current folder and sub folders, except folder start with __ or .
        :param path:
        :param kwargs:
        :return:
        """
        file_list = cls.get_folder_items(path, **kwargs)
        all_file = []
        for i in file_list:
            new_path = os.path.join(path, i)
            if i[:2] == "__" or i[0] == '.':
                continue
            elif os.path.isdir(new_path):
                all_file = all_file + cls.get_folder_items_recursion(new_path, **kwargs)
            else:
                all_file.append(i)
        return all_file

    @classmethod
    def get_resolution(cls):
        return pyautogui.size()

    @classmethod
    def power_shell(cls, command):
        codec = locale.getdefaultlocale()[1]
        log.info('the system codec is {}'.format(codec))
        args = [r"powershell", "-ExecutionPolicy", "Unrestricted"]
        if type(command) == list:
            command = args + command
        else:
            command = args + [command]
        out_byte = subprocess.run(command, stdout=subprocess.PIPE).stdout
        out_str = out_byte.decode(codec)
        return out_str


class AddStartup:
    def __init__(self, name):
        self.__name = name

    def add_startup(self):
        if OS == 'Windows':
            self.add_wes_script_startup(self.__name)
        else:
            self.__add_linux_script_startup(self.__name)

    @staticmethod
    def __create_shortcuts(target_path, name):
        os.system('echo ThePath = "{}">aaa.vbs'.format(target_path))
        os.system('echo lnkname = "{}.lnk">>aaa.vbs'.format(name))
        os.system('echo WS = "Wscript.Shell">>aaa.vbs')
        os.system('echo Set Shell = CreateObject(WS)>>aaa.vbs')
        os.system('echo Set Link = Shell.CreateShortcut(lnkname)>>aaa.vbs')
        os.system('echo Link.TargetPath = ThePath>>aaa.vbs')
        os.system('echo Link.Save>>aaa.vbs')
        os.system('echo Set fso = CreateObject("Scripting.FileSystemObject")>>aaa.vbs')
        os.system('echo f = fso.DeleteFile(WScript.ScriptName)>>aaa.vbs')
        os.system('start aaa.vbs')

    @staticmethod
    def __add_linux_script_startup(script_name):
        src = '/root/auto_start_setup.sh'
        src_auto = get_current_dir("Test_Utility/auto.service")
        dst_auto = "/etc/systemd/system/auto.service"
        dst_wants = "/etc/systemd/system/multi-user.target.wants/auto.service"
        if os.path.exists(src):
            os.remove(src)
        os.system("fsunlock")
        time.sleep(0.2)
        with open('/etc/init/auto-run-automation-script.conf', 'w+') as f:
            f.write("start on lazy-start-40\nscript\n")
            f.write("\t/writable/root/auto_start_setup.sh\nend script\n")
        time.sleep(0.5)
        os.system("chmod 777 /etc/init/auto-run-automation-script.conf")
        os.system('fsunlock')
        time.sleep(0.1)
        bash_script = "#! /bin/bash\nsource /etc/environment\nsource /etc/profile\nexec 2>/root/log.log\n" \
                      "sleep 50\nexport DISPLAY=:0\nfsunlock\ncd /root\n"
        with open('/writable/root/auto_start_setup.sh', 'w+') as s:
            s.write(bash_script)
            res = OSTool.get_folder_items(get_current_dir(), file_only=True)
            if type(script_name) == list:
                for i in script_name:

                    if i in res:
                        s.write("sudo {}\n".format(os.path.join(get_current_dir(), i)))
                    elif '/' in i:
                        s.write("sudo {}\n".format(i))
            else:
                if script_name in res:
                    s.write("sudo {}\n".format(os.path.join(get_current_dir(), script_name)))
                elif '/' in script_name:
                    s.write("sudo {}\n".format(script_name))
        time.sleep(0.2)
        os.system("chmod 777 /writable/root/auto_start_setup.sh")
        time.sleep(0.2)
        if not os.path.exists(dst_auto):
            shutil.copyfile(src_auto, dst_auto)
            time.sleep(1)
            os.system("ln -s {} {}".format(dst_auto, dst_wants))
        return False

    def add_wes_script_startup(self, script_name):
        file_path = r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup'
        items = OSTool.get_folder_items(file_path)
        for i in items:
            log.info("find {} in startup folder".format(i))
            os.remove(file_path + r"\{}".format(i))
        cur_path = os.path.join(get_current_dir(), '{}'.format(script_name))
        log.info(file_path + "  filepath  add_wes_script")
        log.info(cur_path + "  curpath  add_wes_script")
        cmd = r'mklink "{}\{s}" "{}"'.format(file_path, cur_path, s=script_name)
        print(cmd, "cmd")
        log.debug(os.popen(cmd).read())
        if not os.path.exists(file_path + r"\{}".format(script_name)):
            self.__create_shortcuts(cur_path, script_name)
            time.sleep(2)
            # shutil.copy(get_current_dir()+'/'+'{}.lnk'.format(script_name.upper()), startup_path)
            os.system('copy "{}" "{}" /y'.format(cur_path + '.lnk', file_path))
            time.sleep(1)
            if os.path.exists(file_path + '/' + '{}'.format(script_name + '.lnk')):
                log.info('add {} to startup success'.format(file_path + '/' + '{}'.format(script_name + '.lnk')))
            else:
                log.info('add to startup Fail')
                return False
        return True


def case_steps_run_control(steps_list, name, *args, **kwargs):
    temp_folder = get_current_dir('Test_Report', 'temp')
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    case_steps_file = get_current_dir('Test_Report', 'temp', '{}.yaml'.format(name.split('.')[-1]))
    if not os.path.exists(case_steps_file) or all([os.path.exists(case_steps_file),
                                                   isinstance(YamlOperator(case_steps_file).read(), str)]):
        new_list = []
        for s in steps_list:
            step_dict = dict()
            step_dict[s] = "Norun"
            new_list.append(step_dict)
        steps_yml = YamlOperator(case_steps_file)
        steps_yml.write(new_list)
        time.sleep(5)

    steps_yml = YamlOperator(case_steps_file)
    suite_rs = False
    while True:
        new_list2 = steps_yml.read()
        log.info('original step list:')
        log.info(new_list2)
        for step in new_list2:
            step_name, step_status = list(step.items())[0]
            if step_status.upper() == 'NORUN':
                step[step_name] = 'Finished'
                log.info('current step list:')
                log.info(new_list2)
                steps_yml.write(new_list2)
                result = getattr(sys.modules[name], step_name)(*args, **kwargs)
                log.info('current step: {}'.format(step_name))
                log.info('step result: {}'.format(str(result)))
                break
        else:
            break
        if result is False:
            suite_rs = False
            break
        else:
            suite_rs = True
    return suite_rs



