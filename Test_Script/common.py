import os
import shutil
import time
import traceback
from Common import file_transfer
from Common.common_function import OSTool
from Common.file_operator import TxtOperator, YamlOperator
from Common.ui_automation import getElementByType
from Common.log import log


def __get_element_mapping():
    """
    # element format:
    # define name:"name":automationid:controltype
    # eg.: OKButton:"OK":Button----->By name
    #      CancelButton:btnCancel:Button----->By automationId
    :param filepath: ElementlibPath
    :return: element
    """
    mappingDict = {}
    lines = TxtOperator(OSTool.get_current_dir('Test_Data', 'elementLib.ini')).get_lines()
    for line in lines:
        if line[0] == '#':
            continue
        items = line.strip().split(":", 1)
        mappingDict[items[0]] = items[1]
    return mappingDict


def get_element(name, regex=True, **kwargs):
    # name is defined name, format: defined name:"Name"/AutomationId:ControlType
    elementId = __get_element_mapping()[name].split(':')[0]
    control_type = __get_element_mapping()[name].split(':')[1].upper()
    if elementId.startswith('"') and elementId.endswith('"'):
        if regex:
            return getElementByType(control_type, RegexName=elementId.replace('"', ''), **kwargs)
        else:
            return getElementByType(control_type, Name=elementId.replace('"', ''), **kwargs)
    else:
        return getElementByType(control_type, AutomationId=elementId, **kwargs)


def check_agent_connected(sock):
    try:
        sock.connect('15.83.247.71', 10101)
        print('cmd result:', sock.send_command('dir z: /w'))
        time.sleep(3)
        sock.close()
        return True
    except:
        return False


def install_agent(man, ip, _os):
    # install agent
    log.info('[common]local {} install agent in os: {} using {}'.format(ip, _os, man))
    # start agent


def controller_prepare():
    log.info('[common]begin to prepare controller ')
    # clear report


def is_controller():
    # windows/wes, this will represent controller or thin client
    if os.path.exists(r'c:\windows\sysnative\hpramdiskcpl.exe'):
        return False
    else:
        return True


def collect_report():
    """
    collect report and send to ALM server for automated return result to ALM
    alm need addition.yml(case<->alm information), ip.yml(cases result)
    :return:
    #By: balance
    """
    # expect only ip.yml exist in test_report
    global_conf = YamlOperator(OSTool.get_current_dir('Test_Data', 'td_common', 'global_config.yml')).read()
    ftp_svr = global_conf['alm_ftp']['server']
    ftp_user = global_conf['alm_ftp']['username']
    ftp_pass = global_conf['alm_ftp']['password']
    ftp_path = global_conf['alm_ftp']['report_path']
    result_file = OSTool.get_folder_items(OSTool.get_current_dir('Test_Report'), file_only=True, filter_name='.yaml')[0]
    log.info(f'[common][collect result]Get result file: {result_file}')
    prefix = time.strftime("test_%m%d%H%M%S", time.localtime())
    log.info('[common][collect result]Copy additional.yml and ip.yml to test report')
    shutil.copy(OSTool.get_current_dir('Test_Data', 'additional.yml'),
                OSTool.get_current_dir('Test_Report', '{}_add.yml'.format(prefix)))
    shutil.copy(OSTool.get_current_dir('Test_Report', result_file),
                OSTool.get_current_dir('Test_Report', '{}_result.yml'.format(prefix)))
    try:
        ftp = file_transfer.FTPUtils(ftp_svr, ftp_user, ftp_pass)
        ftp.change_dir(ftp_path)
        ftp.upload_file(OSTool.get_current_dir('Test_Report', '{}_result.yml'.format(prefix)), '{}_result.yml'.format(prefix))
        ftp.upload_file(OSTool.get_current_dir('Test_Report', '{}_add.yml'.format(prefix)), '{}_add.yml'.format(prefix))
        ftp.close()
        log.info('[common][collect result]upload report to ftp server')
    except:
        log.error('[common][collect result]FTP Fail Exception:\n{}'.format(traceback.format_exc()))


class BCUConfig:
    def __init__(self, file):
        """
        Config data expect orderly
        :param file:
        """
        self.file = file
        self.config = self.__analyze_config()

    def __analyze_config(self):
        result = {}
        with open(self.file) as f:
            data = f.readlines()
        temp_key = ''
        for line in data:
            if line[0] == '	' or line[0] == ';':
                result[temp_key].append(line.strip())
            else:
                temp_key = line.strip()
                result[temp_key] = []
        return result

    def __save_data(self):
        result = ''
        for k, v in self.config.items():
            result = result + k + '\n'
            for i in v:
                if i and ';' == i[0]:
                    result = result + i + '\n'
                else:
                    result = result + '\t' + i + '\n'
        with open(self.file, 'w') as f:
            f.write(result)

    def enable(self, key: str, value: str, match=False):
        data = self.config[key]
        result = []
        for item in data:
            if match:
                if value.upper() == item.upper():
                    result.append('*' + item)
                elif item[0] == '*':
                    result.append(item[1:])
                else:
                    result.append(item)
            else:
                if value.upper() in item.upper():
                    result.append('*' + item)
                elif item[0] == '*':
                    result.append(item[1:])
                else:
                    result.append(item)
        self.config[key] = result
        self.__save_data()

    def reorder(self, key, value, index):
        data = self.config[key]
        for item in data:
            if value.upper() in item.upper():
                data.remove(item)
                data.insert(index - 1, item)
                break
        self.config[key] = data
        self.__save_data()


if __name__ == '__main__':
    a = BCUConfig(r'Z:/WorkSpace3/BIOS_BCU_Automation/test_utility/test.txt')
    print(a.enable('Clear BIOS Event Log', 'clear', True))
    a.reorder('HBMA Priority List', 'HP External Adapter', 2)
