from Common.flowcontrolbase import *
from Common.report import ScriptReport #update_cases_result, new_cases_result
from Common.log import log, capture_screen


class ResultHandler(ResultControl):
    flag = None
    event_method_name = None
    error_msg = None
    success_msg = None
    capture = True

    def __init__(self, case_name):
        super().__init__(case_name)
        self.__report = ScriptReport(self.yml_path)
        self.__report.new_case_result(self.case_name)

    def update_class_property(self, **kwargs):
        self.flag = kwargs.get("return", False)
        self.event_method_name = kwargs.get("event_method").__name__
        self.error_msg = kwargs.get("error_msg", {})
        self.success_msg = kwargs.get("success_msg", {})
        self.capture = kwargs.get("capture", True)

    def __update_result(self):
        step = {'step_name': '',
                'result': 'PASS',
                'expect': '',
                'actual': '',
                'note': ''}
        step.update({'step_name': self.event_method_name})
        if not self.flag:
            if self.capture:
                path = get_current_dir(
                    "Test_Report/img/{}__{}_exception.png".format(self.case_name, self.event_method_name))
                capture_screen(path)
            step.update({'result': 'Fail',
                         'expect': self.error_msg.get("expect", ""),
                         'actual': self.error_msg.get("actual", ""),
                         'note': '{}_exception.png'.format(self.event_method_name) if self.capture else ""})
        else:

            step.update(self.success_msg)
        self.__report.update_case_result(self.case_name, step)
        return

    def start(self):
        return self.__update_result()


class CallBackHandler(CallBack):
    __instance = None
    callback = None
    callback_params = {}
    self_callback = True
    inherit = None
    do_callback = None
    do_callback_if_fail = None
    flag = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.self_callback = True

    def update_class_property(self, **kwargs):
        self.flag = kwargs.get("return", False)
        self.callback = kwargs.get("callback", None)
        self.callback_params = kwargs.get("callback_params", {})
        self.inherit = kwargs.get("inherit", False)
        self.do_callback = kwargs.get("do_callback", True)
        self.do_callback_if_fail = kwargs.get("do_callback_if_fail", False)

    def __callback(self, **kwargs):
        if self.self_callback:
            self.callback(self, **kwargs)
        else:
            self.callback(**kwargs)

    def __exec_callback(self):
        double_check_flag = True if self.flag else False
        if self.do_callback and double_check_flag:
            if self.inherit and self.flag:
                assert isinstance(self.flag, dict), \
                    "return value of function: " \
                    "{} must be a dict!!".format(self.callback.__name__.replace("callback", ""))
                self.__callback(**self.flag)
            elif self.callback:
                self.__callback()
        elif self.do_callback_if_fail and not double_check_flag:
            self.__callback()
        return double_check_flag

    def start(self):
        return self.__exec_callback()


class CaseFlowHandler(FlowHandler):
    callback_instance = None
    result_process_instance = None

    def __init__(self, case_name=None, **kwargs):
        case_name = case_name if case_name else self.__class__.__name__
        self.callback_instance = CallBackHandler()
        self.result_process_instance = ResultHandler(case_name)
        self.events_dic_list = []

    def __generate_events_dic_list(self):
        cls_dic = self.__class__.__dict__
        events = list(filter(lambda x: "_" not in x[0] and "callback" not in x.lower(), cls_dic))
        for i in events:
            map_list = {}
            event_method = cls_dic.get(i)
            map_list.update({"event_method": event_method})
            callback_name = "{}_callback".format(i)
            callback = cls_dic.get(callback_name)
            if callback:
                map_list.update({"callback": callback})
            self.events_dic_list.append(map_list)
        print(self.events_dic_list)
        return

    def __exec_event(self, **event):
        event_method = event.get("event_method")
        res = event_method(self)
        if not res:
            log.error('{} {}'.format(event_method.__name__,
                                     "return None is deprecated!!(you could return {'flag': False})"))
            return {}
        return res

    def start(self):
        self.__generate_events_dic_list()
        event_generator = self.get_event()
        while True:
            try:
                event = next(event_generator)
                res = self.__exec_event(**event)
                event.update(res)
                self.result_process_instance.update_class_property(**event)
                self.result_process_instance.start()
                self.callback_instance.update_class_property(**event)
                response = self.callback_instance.start()
                stop = event.get("stop", True)
                if stop and not response:
                    print(event, "break")
                    break
            except StopIteration:
                break


class CaseFlowHandler2(FlowHandler):
    def __init__(self, case_name=None, **kwargs):
        case_name = case_name if case_name else self.__class__.__name__
        self.callback_instance = CallBackHandler()
        self.callback_instance.self_callback = False
        self.result_process_instance = ResultHandler(case_name)
        self.events_dic_list = []

    def add_event(self, event_method, callback: object = None, **kwargs):
        map_list = {}
        map_list.update({"event_method": event_method})
        if callback:
            map_list.update({"callback": callback})
        self.events_dic_list.append(map_list)

    def __exec_event(self, **event):
        event_method = event.get("event_method")
        res = event_method()
        if not res:
            log.error('{} {}'.format(event_method.__name__,
                                     "return None is deprecated!!(you could return {'flag': False})"))
            return {}
        return res

    def start(self):
        print(self.events_dic_list)
        event_generator = self.get_event()
        while True:
            try:
                event = next(event_generator)
                res = self.__exec_event(**event)
                event.update(res)
                self.result_process_instance.update_class_property(**event)
                self.result_process_instance.start()
                self.callback_instance.update_class_property(**event)
                response = self.callback_instance.start()
                stop = event.get("stop", True)
                if stop and not response:
                    log.warning("Stop manually at {}".format(event.get("event_method")))
                    break
            except StopIteration:
                break


if __name__ == '__main__':
    """copy out the Common"""
