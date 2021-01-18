import os
import traceback
import yaml
from Common import common_function
from Common.log import log


class Report:
    def __init__(self, case_name):
        self.result = "Pass"
        self.script_complete_path = common_function.OSTool.get_current_dir()
        self.case_name = case_name
        self.ip = common_function.OSTool.get_ip()
        self.uut_name = self.ip
        self.report_path = self.get_report_path()
        self.steps_value_list = []

    def get_report_path(self):
        report_path = "{0}/Test_Report/{1}.yaml".format(self.script_complete_path, self.ip)
        return report_path

    def reporter(self, step_name='', result='', expect='', actual='', note=''):
        if result.upper() == "FAIL":
            self.result = "FAIL"
        dic = {"step_name": step_name, "result": result, "expect": expect, "actual": actual,
               "note": note}  # The dic of one step
        self.steps_value_list.append(dic)
        return self.steps_value_list

    def generate(self):
        report_data = []
        case_dic = {"case_name": self.case_name, "result": self.result, "steps": self.steps_value_list,
                    "uut_name": self.uut_name}  # The data of one case.
        report_data.append(case_dic)

        if not os.path.exists(self.report_path):
            self.write_data_to_yaml(report_data)  # Write data to yaml file
        else:
            original_data = self.get_original_data()
            if original_data is not None:
                new_data = original_data + report_data
            else:
                new_data = report_data
            self.write_data_to_yaml(new_data)  # Write data to yaml file

    def write_data_to_yaml(self, data):
        with open(self.report_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f)

    def get_original_data(self):
        with open(self.report_path, 'r', encoding='utf-8') as f:
            original_data = yaml.safe_load(f)
            return original_data


class ScriptReport:
    def __init__(self, file):
        self.report_file = file
        if not os.path.exists(self.report_file):
            f = open(self.report_file, 'w')
            f.close()

    def new_case_result(self, case_name, step_names=None):
        if step_names is None:
            step_names = []
        steps = []
        for step_name in step_names:
            steps.append(
                {'step_name': step_name,
                 'result': 'Fail',
                 'expect': '',
                 'actual': '',
                 'note': ''}
            )
        result = [{'case_name': case_name,
                   'uut_name': common_function.check_ip_yaml(),
                   'result': 'Fail',
                   'steps': steps
                   }]
        with open(self.report_file, 'r') as f:
            current_report = yaml.safe_load(f)
        if isinstance(current_report, list):
            for report in current_report:
                if report['case_name'] == case_name:
                    return
            current_report.extend(result)
        else:
            current_report = result
        with open(self.report_file, 'w') as f:
            yaml.safe_dump(current_report, f)

    def update_case_result(self, case_name, step):
        """
        :param file:
        :param case_name:
        :param step: {'step_name': step1, 'result': Pass, 'note': '', expect:'', actual:''}
        :return:
        """
        with open(self.report_file, 'r') as f:
            current_report = yaml.safe_load(f)
        for report in current_report:
            if report['case_name'] == case_name:
                if self.__check_step_exist(report['steps'], step['step_name']):
                    report['steps'] = self.__update_step_result(report['steps'], step)
                    case_status = True
                    for sub_step in report['steps']:
                        if sub_step['result'].upper() == 'FAIL':
                            case_status = False
                            break
                    if case_status:
                        report['result'] = 'Pass'
                    else:
                        report['result'] = 'Fail'
                    break
                else:
                    report['steps'].append(step)
                    case_status = True
                    for sub_step in report['steps']:
                        if sub_step['result'].upper() == 'FAIL':
                            case_status = False
                            break
                    if case_status:
                        report['result'] = 'Pass'
                    else:
                        report['result'] = 'Fail'
                    break

        with open(self.report_file, 'w') as f:
            yaml.safe_dump(current_report, f)

    @staticmethod
    def __update_step_result(steps_rs, step: dict):
        for step_rs in steps_rs:
            if step_rs['step_name'] == step['step_name']:
                step_rs['result'] = step.get('result', step_rs['result'])
                step_rs['expect'] = step.get('expect', step_rs['expect'])
                step_rs['actual'] = step.get('actual', step_rs['actual'])
                step_rs['note'] = step.get('note', step_rs['note'])
                return steps_rs

    @staticmethod
    def __check_step_exist(steps, step_name):
        for step in steps:
            if step['step_name'] == step_name:
                return True
        return False

    def check_step(self, func, case_name, step_name, expect='', note='', **kwargs):
        """
        pass a func(step) to this method, we'll automatically update case result to ip.yaml(file)
        :param note:
        :param expect:
        :param step_name:
        :param case_name:
        :param func: step method, func should return [bool, str], bool: pass fail, str: actual information
        :param kwargs: parameters of method func
        :return:
        """
        try:
            result = func(**kwargs)
        except:
            log.error(f'[report][script_report]{case_name} {step_name} meet exception:\n{traceback.format_exc()}',
                      common_function.OSTool.get_current_dir('Test_Report', 'img', '{}_{}.jpg'.format(case_name, step_name)))
            step = {'step_name': step_name,
                    'result': 'Fail',
                    'expect': expect,
                    'actual': r'img\{}'.format(common_function.OSTool.get_current_dir('Test_Report',
                                                                               'img',
                                                                               '{}_{}.jpg'.format(case_name,
                                                                                                  step_name))),
                    'note': 'meet exception'}
            self.update_case_result(case_name, step)
            return False
        if not result[0]:
            log.error(f'[report][script_report]{result[1]}',
                      common_function.OSTool.get_current_dir('Test_Report', 'img', '{}_{}.jpg'.format(case_name, step_name)))
            step = {'step_name': step_name,
                    'result': 'Fail',
                    'expect': expect,
                    'actual': r'img\{}'.format(common_function.OSTool.get_current_dir('Test_Report',
                                                                               'img',
                                                                               '{}_{}.jpg'.format(case_name,
                                                                                                  step_name))),
                    'note': note}
            self.update_case_result(case_name, step)
            return False
        else:
            log.info(f'[report][script_report]{result[1]}')
            step = {'step_name': step_name,
                    'result': 'Pass',
                    'expect': expect,
                    'actual': result[1],
                    'note': note}
            self.update_case_result(case_name, step)
            return True

    def check_step_reboot(self, case_name, steps: dict):  # steps: {'step_name': method, ..}
        pass
