import win32com.client


class ALM:
    def __init__(self):
        self.map_dict = {}
        self.full_lab_sub_folder_list = []
        self.full_instance_list = []
        self.td = win32com.client.Dispatch("TDApiOle80.TDConnection")

    def login(self, url, user_name, password):
        self.td.InitConnection(url)
        self.td.Login(user_name, password)
        if self.td.LoggedIn:
            return True
        else:
            return False

    def login_test(self, url, username, password):
        # url = "https://alm-3.pro.azc.ext.hp.com/qcbin/"
        self.td.InitConnectionWithApiKeyEx(url, username, password)
        if self.td.LoggedIn:
            print('login success')
            return True
        else:
            return False

    def get_domain_list(self):
        return self.td.VisibleDomains

    def get_project_list_in_domain(self, domain):
        return self.td.VisibleProjects(domain)

    def connect(self, domain, project):
        self.td.Connect(domain, project)
        if self.td.Connected:
            print(self.td.ProjectName, self.td.DomainName)
            return True
        else:
            return False

    def get_current_project(self):
        return self.td.ProjectName

    def get_current_domain(self):
        return self.td.DomainName

    def __get_test_lab_sub_folder(self, parent_path):
        test_set_folder_factory = self.td.TestSetTreeManager
        test_set_folder = test_set_folder_factory.NodeByPath(parent_path)
        if test_set_folder.count > 0:
            return test_set_folder.SubNodes
        else:
            return False

    def get_test_lab_sub_folder_recursively(self, folder_path):
        sub_folders_list = self.__get_test_lab_sub_folder(folder_path)
        if sub_folders_list is not False:
            self.full_lab_sub_folder_list.extend(sub_folders_list)
            for node in sub_folders_list:
                self.get_test_lab_sub_folder_recursively(node.path)
        return self.full_lab_sub_folder_list

    def get_test_set_list(self, test_lab_folder_path):
        test_set_folder_factory = self.td.TestSetTreeManager
        test_set_folder = test_set_folder_factory.NodeByPath(test_lab_folder_path)
        test_set_factory = test_set_folder.TestSetFactory
        test_set_list = test_set_factory.NewList("")
        return test_set_list

    def get_test_set_by_id(self, test_set_id):
        test_set_factory = self.td.TestSetFactory
        test_set = test_set_factory.Item(test_set_id)
        return test_set

    def get_test_instance_list(self, test_set):
        test_instance_factory = test_set.TSTestFactory
        test_instance_list = test_instance_factory.NewList("")
        return test_instance_list

    def get_instance_by_id(self, test_instance_id):
        test_instance_factory = self.td.TSTestFactory
        test_instance = test_instance_factory.Item(test_instance_id)
        return test_instance

    def update_instance_execution_result(self, test_instance_id, status, build_version):
        instance = self.get_instance_by_id(test_instance_id)
        if status in ['Passed', 'Failed']:
            instance.Status = status
            instance['TC_USER_TEMPLATE_02'] = 'N'
            instance['TC_USER_01'] = build_version
        else:
            instance.Status = status
            instance['TC_USER_01'] = build_version
        instance.Post()

    def update_instance_execution_status(self, test_instance_id, responsible_tester):
        instance = self.get_instance_by_id(test_instance_id)
        # instance['TC_USER_TEMPLATE_02'] = 'N'
        instance['TC_TESTER_NAME'] = responsible_tester
        instance.Post()

    def get_regression_case(self, test_set, tester):
        test_instance_factory = test_set.TSTestFactory
        # Regression = Y
        test_instance_filter_regression = test_instance_factory.Filter
        test_instance_filter_regression['TC_USER_TEMPLATE_02'] = 'Y'
        test_instance_filter_regression['TC_TESTER_NAME'] = tester
        test_instance_regression_list = test_instance_filter_regression.NewList()
        return test_instance_regression_list

    def get_unfinished_case(self, test_set, tester):
        test_instance_factory = test_set.TSTestFactory
        # Regression = N, Status not Passed or Failed
        test_instance_filter_unfinished = test_instance_factory.Filter
        test_instance_filter_unfinished['TC_USER_TEMPLATE_02'] = 'N'
        test_instance_filter_unfinished['TC_STATUS'] = 'Not Passed And Not Failed'
        test_instance_filter_unfinished['TC_TESTER_NAME'] = tester
        test_instance_unfinished_list = test_instance_filter_unfinished.NewList()
        return test_instance_unfinished_list

    def __get_table_column_by_label(self, table, label):
        field_list = self.td.Fields(table)
        find_label = False
        for field in field_list:
            field_property = field.Property
            if field_property.UserLabel == label:
                find_label = True
                return field_property.DBColumnName
        if find_label is False:
            print("Can't find the property {}".format(label))
            return False

    def map_column_label(self, label_list):
        map_column_label_dict = {}
        for label in label_list:
            map_column_label_dict.update(
                {label: self.__get_table_column_by_label("Test", label)})
        return map_column_label_dict

    def get_testset_filter_by_label(self, label_name):
        field_list = self.td.Fields('CYCLE')
        for field in field_list:
            field_property = field.Property
            if field_property.UserLabel == label_name:
                return field_property.DBColumnName

    def get_instance_filter_by_label(self, label_name):
        # Last Run On Build' -> TC_USER_01
        field_list = self.td.Fields('TESTCYCL')
        for field in field_list:
            field_property = field.Property
            if field_property.UserLabel == label_name:
                return field_property.DBColumnName

    def get_test_instance_property(self, test_instance_path, test_instance_set_name, test_instance):
        current_case_property_dict = self.get_test_case_property(test_instance.testid)
        instance_property_dict = {
            "test_instance_path": test_instance_path,
            "test_set_name": test_instance_set_name,
            "test_instance_id": test_instance.id,
            "test_instance_status": test_instance.status,
            "test_instance_test_id": test_instance.testid,
            "test_instance_test_name": test_instance.testname,
            "test_instance_L1": current_case_property_dict["L1"],
            "test_instance_L2": current_case_property_dict["L2"],
            "test_instance_L3": current_case_property_dict["L3"],
            "test_instance_L4": current_case_property_dict["L4"]
        }
        return instance_property_dict

    def get_test_case_by_id(self, test_case_id):
        test_factory = self.td.TestFactory
        test_filter = test_factory.Filter
        test_filter["TS_TEST_ID"] = test_case_id
        test_list = test_filter.NewList()
        test_case = test_list[0]
        return test_case

    def get_test_case_property(self, test_case_id):
        test_factory = self.td.TestFactory
        test_filter = test_factory.Filter
        test_filter["TS_TEST_ID"] = test_case_id
        test_list = test_filter.NewList()
        test_case = test_list[0]
        case_property_dict = {
            "test_id": test_case.ID,
            "test_name": test_case.Name,
            "L1": test_case.Field(self.map_dict.get("L1 Feature")),
            "L2": test_case.Field(self.map_dict.get("L2 Feature")),
            "L3": test_case.Field(self.map_dict.get("L3 Feature")),
            "L4": test_case.Field(self.map_dict.get("L4 Feature"))
        }
        return case_property_dict

    def get_design_step(self, test_case_obj):
        step_factory = test_case_obj.DesignStepFactory
        step_filter = step_factory.Filter
        step_list = step_filter.NewList()
        step_property = []
        for step in step_list:
            step_property.append([step.StepName, step.EvaluatedStepDescription, step.EvaluatedStepExpectedResult])
        return step_property

    def create_test_set(self, test_set_path, test_set_name, uut_list, paraeters):
        test_set_folder_factory = self.td.TestSetTreeManager
        test_set_folder = test_set_folder_factory.NodeByPath(test_set_path)
        test_set_factory = test_set_folder.TestSetFactory
        set_filter = test_set_factory.Filter
        set_filter['CY_CYCLE'] = test_set_name
        test_set_list = set_filter.NewList()
        if test_set_list.Count > 0:
            print('Test Set {} already exist'.format(test_set_name))
            return test_set_list[0]
        else:
            print('No existing test set, start creating new test set: {}'.format(test_set_name))
            config_data = test_set_name.split('_')
            config = '{}_{}'.format(config_data[0], config_data[1])
            new_test_set = test_set_factory.AddItem(None)
            new_test_set.Name = test_set_name
            new_test_set[self.get_testset_filter_by_label('UUT')] = uut_list
            new_test_set[self.get_testset_filter_by_label('Parameters')] = paraeters
            new_test_set[self.get_testset_filter_by_label('Config')] = config
            new_test_set.Post()
            print('Successfully create new test set: {}'.format(test_set_name))
            return new_test_set

    def get_test_case_by_filter(self, project_path, **case_filters):
        test_factory = self.td.TestFactory
        test_filter = test_factory.Filter
        test_filter['TS_SUBJECT'] = '^' + project_path + '^'    # To iterate folder recursively
        for item in case_filters:
            # Handle None value as first priority
            if case_filters[item] is None:
                test_filter[item] = ''
            # To avoid value include space
            elif item in ['TS_USER_01', 'TS_USER_02', 'TS_USER_03', 'TS_USER_04'] and " " in case_filters[item]:
                test_filter[item] = '"{}"'.format(case_filters[item])
            else:
                test_filter[item] = case_filters[item]
        case_list = test_filter.NewList()
        return case_list

    def fill_instance_to_test_set(self, test_set, test_case, execution_priority, automation, responsible_tester):
        test_instance_factory = test_set.TSTestFactory
        new_instance = test_instance_factory.AddItem(test_case)
        new_instance['TC_USER_TEMPLATE_02'] = 'N'
        new_instance['TC_USER_TEMPLATE_01'] = execution_priority
        test_value = self.get_instance_filter_by_label('Automate_Run')
        new_instance[self.get_instance_filter_by_label('Automate_Run')] = automation
        if not responsible_tester or responsible_tester == "":
            new_instance.Post()
        else:
            new_instance['TC_TESTER_NAME'] = responsible_tester
            new_instance.Post()
        return new_instance

    def disconnect(self):
        self.td.Disconnect()
        print('disconnect sucess')


if __name__ == "__main__":
    a = ALM()
    a.login_test("https://alm-3.pro.azc.ext.hp.com/qcbin/", 'apikey-rkbetpipopmkaqbjshhf', 'dadhppdkeolendjn')
    a.connect('THIN_CLIENT', 'Linux')
    test_set = a.get_test_set_by_id('7404')
    for i in a.get_test_instance_list(test_set):
        print(i.Name)
    a.disconnect()
