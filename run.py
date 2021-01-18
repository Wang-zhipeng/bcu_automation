import ctypes
import os
import time
import sys
import traceback
from Common import email_tool, file_operator, report, socket_action
from Test_Script import common, man
from Common.common_function import OSTool, check_ip_yaml
from Common.log import log
from settings import *

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
additional = {}
if os.path.exists(OSTool.get_current_dir('Test_Data', 'all_additional.yml')):
    origin_additional = file_operator.YamlOperator(OSTool.get_current_dir('Test_Data', 'all_additional.yml')).read()
    additional.update(origin_additional)
if os.path.exists(OSTool.get_current_dir('Test_Data', 'additional.yml')):
    new_additional = file_operator.YamlOperator(OSTool.get_current_dir('Test_Data', 'additional.yml')).read()
    additional.update(new_additional)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except OSError:
        return False


def run_suite(global_dict: dict, file: str, person: man.Man, agent, update_status=True):
    """
    :return:
    """
    if not os.path.exists(file):
        log.error(f'[run][run_suite]Did not find script {file}, please double check')
        return False
    suite_list = file_operator.YamlOperator(file).read()
    for suite in suite_list:
        suite_info, suite_status = list(suite.items())[0]
        if suite_status.upper() == "NORUN":
            run_single_suite(global_dict, file, suite_info, person, agent, update_status)
        else:
            continue


def run_single_suite(global_dict: dict, file: str, suite_info: str, person: man.Man, agent, update_status: bool):
    """
    :param agent:
    :param global_dict:
    :param file:
    :param suite_info:
    :param person:
    :param update_status:
    :return:
    """
    # get additional data, here will merge all_additional.yml and additional.yml
    # if conflict keep data in additional.yml
    ###########################################################################################
    # this value should not get here, will execute many times
    ##############################################################################################
    # begin to run suite
    suite_name, case_name = suite_info.split('__')
    try:
        suite_rs = global_dict[suite_name].start(case_name=case_name, dict_args=additional, man=person, agent=agent)
        log.info(f'[run][run_single_suite]{suite_info} test finished')
        if update_status:
            yaml_obj = file_operator.YamlOperator(file)
            script_list = yaml_obj.read()
            for each in script_list:
                if list(each.keys())[0] == suite_info:
                    each[suite_info] = 'Finished'
            yaml_obj.write(script_list)
    except:
        log.error(f'[run][run_single_suite]{case_name} test fail, meet exception:\n{traceback.format_exc()}',
                  OSTool.get_current_dir('Test_Report', 'img', f'{case_name}_e.jpg'))
        with open(OSTool.get_current_dir('Test_Report', 'debug.log'), 'a') as debug:
            debug.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n{traceback.format_exc()}')
        steps = {
            'step_name': 'case meet exception',
            'result': 'Fail',
            'expect': '',
            'actual': f'{case_name}_e.jpg',
            'note': traceback.format_exc()
        }
        result_file = OSTool.get_current_dir('Test_Report', f'{check_ip_yaml()}.yaml')
        report.ScriptReport(OSTool.get_current_dir('Test_Report',
                                                   '{}.yaml'.format(check_ip_yaml()))).update_case_result(case_name,
                                                                                                          steps)
        yaml_obj = file_operator.YamlOperator(file)
        script_list = yaml_obj.read()
        for each in script_list:
            if list(each.keys())[0] == suite_info:
                each[suite_info] = 'Finished'
        yaml_obj.write(script_list)


def main_workflow():
    # record time at first running
    if not os.path.exists('time.txt'):
        with open('time.txt', 'w') as f_time:
            f_time.write(time.ctime())
    globals_dict = globals()
    if not common.is_controller():
        log.debug('[run-main]Start UUT workflow...')
    else:
        log.info('[run-main]Start Controller workflow...')
        try:
            person = man.Man()
            log.info('[run-main]Successfully create man instance...')
        except:
            log.error('[run-main]Failed to create man instance...')
            return
        common.controller_prepare()
        log.info('[run-main]Init socket client and start controller socket server')
        # here do not validate port, if need add in below method
        # socket agent in controller is for UUT initiative send command to controller
        # socket client: is to initiative send command to UUT
        socket_action.SocketAgent(port=50000).start()
        log.info('[run-main]socket server listener started')
        control_client = socket_action.SocketClient()
        log.info('[run-main]Begin to install agent in UUT using magic key...')
        common.install_agent(man=person, ip=OSTool.get_ip(), _os='wes')
        if not common.check_agent_connected(control_client):
            log.error('[run-main]UUT agent not installed or not started')
            return False
        run_suite(global_dict=globals_dict,
                  file=OSTool.get_current_dir('Test_Data', 'script.yml'),
                  person=person,
                  update_status=True,
                  agent=control_client)
        os.system(f'echo test finished>{OSTool.get_current_dir("flag.txt")}')
    # collect result and send to alm server
    common.collect_report()
    with open('time.txt') as f_time:
        start = f_time.read()
    end = time.ctime()
    report = email_tool.GenerateReport(start, end)
    report.generate()
    zip_file_name = f'{additional.get("platform")}_{additional.get("tester")}.zip'
    mail_list = []
    email_tool.zip_dir(report_name=zip_file_name)
    email_tool.send_mail(mail_list, subject='', text='', attachment=zip_file_name)
    os.remove(zip_file_name)
    os.remove('time.txt')


if __name__ == '__main__':
    if is_admin():
        try:
            log.info("[run]run as admin")
            main_workflow()
        except:
            traceback.print_exc()
            with open(OSTool.get_current_dir('Test_Report', 'debug.log'), 'a') as f:
                f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n{traceback.format_exc()}')
    else:
        log.info("[run]try to run as admin")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
