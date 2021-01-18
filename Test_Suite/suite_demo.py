import time
from Common import socket_action
from Common.common_function import OSTool, check_ip_yaml
from Common.report import ScriptReport

report = ScriptReport(OSTool.get_current_dir('Test_Report', '{}.yaml'.format(check_ip_yaml())))


def check_config(agent: socket_action.SocketClient):
    print('begin to send get passowrdd config command')
    agent.connect('15.83.247.71', 10101)
    rs = agent.send_command(r'Z:\WorkSpace3\BIOS_BCU_Automation\Test_Utility\BiosConfigUtility64.exe /get:z:\1.txt')
    print('feedback from server:', rs.split(',', 1))
    time.sleep(4)
    agent.close()
    return [True, 'default']


def set_password(agent: socket_action.SocketClient):
    print('begin to send set password command')
    agent.connect('15.83.247.71', 10101)
    rs = agent.send_command(r'Z:\WorkSpace3\BIOS_BCU_Automation\Test_Utility\BiosConfigUtility64.exe /set:z:\1.txt')
    print('feedback from server:', rs)
    time.sleep(10)
    agent.close()
    time.sleep(10)
    print('socket get response')
    return [True, 'set']


def check_after_reboot():
    print('begin to reboot')
    print('rebooting 10s')
    time.sleep(10)
    return [True, 'check']


def start(case_name, **kwargs):
    report.new_case_result(case_name=case_name, step_names=['check config', 'set_password', 'check result'])
    report.check_step(check_config, case_name, 'check config', agent=kwargs.get('agent'))
    report.check_step(set_password, case_name, 'set_password', agent=kwargs.get('agent'))
    report.check_step(check_after_reboot, case_name, 'check result')

