from Common.common_function import get_current_dir, check_ip_yaml


class ResultControl:

    case_name = None
    yml_path = None

    def __init__(self, case_name):
        ip = check_ip_yaml()
        self.yml_path = get_current_dir("Test_Report/{}.yaml".format(ip))
        self.case_name = case_name

    def update_class_property(self):
        """
        abstract method
        :return:
        """
        pass

    def __update_result(self):
        """
        abstract method
        :return:
        """
        pass

    def start(self):
        """
        abstract method
        :return:
        """
        pass


class CallBack:

    def update_class_property(self):
        """abstract method"""
        pass

    def __exec_callback(self):
        """abstract method"""
        return

    def start(self):
        """abstract method"""
        pass


class FlowHandler:
    __com_list = []
    events_dic_list = []

    def __generate_event_list(self):
        """abstract method"""
        pass

    def add_component(self, com):
        if isinstance(com, list):
            self.__com_list.extend(com)
        else:
            self.__com_list.append(com)
        return

    def get_components(self):
        return self.__com_list

    def __exec_event(self, **event):
        """abstract method"""
        pass

    def get_event(self):
        events_iter = iter(self.events_dic_list)
        while True:
            try:
                yield next(events_iter)
            except StopIteration:
                return None

    def start(self):
        """abstract method"""
        pass
