"""
By: balance
封装ALM->ALM_ACTION， 支持：
1。通过caseID来更新结果
2。通过caseName来更新结果 （name为关键字）
3。获取test set 下的所有instance
ALM URL和API Key已固定
用此方法需要传入domain和project
"""
from Common.alm import ALM
from Common.log import log


class ALM_Action:
    def __init__(self, domain='THIN_CLIENT', project='Linux'):
        self.alm_ins = ALM()
        self.url = "https://alm-3.pro.azc.ext.hp.com/qcbin/"
        self.username = 'apikey-rkbetpipopmkaqbjshhf'
        self.password = 'dadhppdkeolendjn'
        self.domain = domain
        self.project = project

    def login(self):
        self.alm_ins.login_test(self.url, self.username, self.password)
        self.alm_ins.connect(self.domain, self.project)

    def update_case_by_instance(self, instance, status, build_version='123456'):
        if status.upper() == 'PASS':
            status = 'Passed'
        elif status.upper() == 'FAIL':
            status = 'Failed'
        instance.Status = status
        instance[self.alm_ins.get_instance_filter_by_label('Last Run On Build')] = build_version
        instance.Post()

    def update_case_by_id(self, instance_id, status, build_version='123456'):
        instance = self.alm_ins.get_instance_by_id(instance_id)
        if instance:
            self.update_case_by_instance(instance, status, build_version)
            return True
        else:
            log.error("[return-to-alm][update-case-by-name]Do not found cases ID {} in ALM".format(instance_id))
            return False

    def update_case_by_name(self, name, cases_list, status, build_version='123456'):
        instance = self.filter_instance_by_name(name, cases_list)
        if instance:
            self.update_case_by_instance(instance, status, build_version)
            return True
        else:
            log.error("[return-to-alm][update-case-by-name]Do not found cases name {} in ALM".format(name))
            return False

    def get_cases_list(self, test_set_id):
        test_set = self.alm_ins.get_test_set_by_id(test_set_id)
        return self.alm_ins.get_test_instance_list(test_set)

    @staticmethod
    def filter_instance_by_name(name, cases_list):
        # before run this function must provide cases list by get_cases_list()
        for case in cases_list:
            if name in case.Name:
                return case

    def logoff(self):
        self.alm_ins.disconnect()
