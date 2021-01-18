from PIL import Image, ImageGrab
from uiautomation import *
import uiautomation
import os
from Common.exception import ElementNotFoundError
from Common.file_operator import TxtOperator
from Common.log import get_current_dir

'''
Some element might mistake recognize automationId or Name:
Minimize: Only Name is useful, AutomationId actually is "" even though we can get the value
'''


def get_element_mapping():
    """
    # element format:
    # define name:"name":automationid:controltype
    # eg.: OKButton:"OK":Button----->By name
    #      CancelButton:btnCancel:Button----->By automationId
    :param filepath: ElementlibPath
    :return: element
    """
    mappingDict = {}
    lines = TxtOperator(get_current_dir('Test_Data', 'elementLib.ini')).get_lines()
    for line in lines:
        if line[0] == '#':
            continue
        items = line.strip().split(":", 1)
        mappingDict[items[0]] = items[1]
    return mappingDict


class Control(uiautomation.Control):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        uiautomation.Control.__init__(self, element=element, searchFromControl=searchFromControl,
                                      searchDepth=searchDepth, searchWaitTime=searchWaitTime,
                                      foundIndex=foundIndex, **searchPorpertyDict)

    def Click(self, ratioX=0.5, ratioY=0.5, simulateMove=False, waitTime=0.1):
        """
        ratioX: float or int, if is int, click left + ratioX, if < 0, click right + ratioX
        ratioY: float or int, if is int, click top + ratioY, if < 0, click bottom + ratioY
        simulateMove: bool, if True, first move cursor to control smoothly
        waitTime: float
        Click(0.5, 0.5): click center
        Click(10, 10): click left+10, top+10
        Click(-10, -10): click right-10, bottom-10
        """
        self.SetFocus()
        x, y = self.MoveCursor(ratioX, ratioY, simulateMove)
        Win32API.MouseClick(x, y, waitTime)

    def get_element(self, name, regex=True, **kwargs):
        # name is defined name, format: defined name:"Name"/AutomationId:ControlType
        elementId = get_element_mapping()[name].split(':')[0]
        control_type = get_element_mapping()[name].split(':')[1].upper()
        if elementId.startswith('"') and elementId.endswith('"'):
            if regex:
                return self.getElementByType(control_type, RegexName=elementId.replace('"', ''), **kwargs)
            else:
                return self.getElementByType(control_type, Name=elementId.replace('"', ''), **kwargs)
        else:
            return self.getElementByType(control_type, AutomationId=elementId, **kwargs)

    def getElementByType(self, controlType, **kwargs):
        # parent: Parent element
        # print(controlType, **kwargs)
        if controlType.upper() == "HYPERLINK":
            return self.HyperlinkControl(**kwargs)
        elif controlType.upper() == 'IMAGE':
            return self.ImageControl(**kwargs)
        elif controlType.upper() == 'CALENDAR':
            return self.CalendarControl(**kwargs)
        elif controlType.upper() == 'CUSTOM':
            return self.CustomControl(**kwargs)
        elif controlType.upper() == 'DOCUMENT':
            return self.DocumentControl(**kwargs)
        elif controlType.upper() == 'GROUP':
            return self.GroupControl(**kwargs)
        elif controlType.upper() == 'HEADER':
            return self.HeaderControl(**kwargs)
        elif controlType.upper() == 'HEADERITEM':
            return self.HeaderItemControl(**kwargs)
        elif controlType.upper() == 'SPINNER':
            return self.SpinnerControl(**kwargs)
        elif controlType.upper() == 'SLIDER':
            return self.SliderControl(**kwargs)
        elif controlType.upper() == 'SEPARATOR':
            return self.SeparatorControl(**kwargs)
        elif controlType.upper() == 'SEMANTICZOOM':
            return self.SemanticZoomControl(**kwargs)
        elif controlType.upper() == 'MENUITEM':
            return self.MenuItemControl(**kwargs)
        elif controlType.upper() == 'MENU':
            return self.MenuControl(**kwargs)
        elif controlType.upper() == 'MENUBAR':
            return self.MenuBarControl(**kwargs)
        elif controlType.upper() == 'TABLE':
            return self.TableControl(**kwargs)
        elif controlType.upper() == 'STATUSBAR':
            return self.StatusBarControl(**kwargs)
        elif controlType.upper() == 'SPLITBUTTON':
            return self.SplitButtonControl(**kwargs)
        elif controlType.upper() == 'THUMB':
            return self.ThumbControl(**kwargs)
        elif controlType.upper() == 'TITLEBAR':
            return self.TitleBarControl(**kwargs)
        elif controlType.upper() == 'TOOLTIP':
            return self.ToolTipControl(**kwargs)
        elif controlType.upper() == "BUTTON":
            return self.ButtonControl(**kwargs)
        elif controlType.upper() == "COMBOX":
            return self.ComboBoxControl(**kwargs)
        elif controlType.upper() == "CHECKBOX":
            return self.CheckBoxControl(**kwargs)
        elif controlType.upper() == "DATAGRID":
            return self.DataGridControl(**kwargs)
        elif controlType.upper() == "DATAITEM":
            return self.DataItemControl(**kwargs)
        elif controlType.upper() == "EDIT":
            return self.EditControl(**kwargs)
        elif controlType.upper() == "LIST":
            return self.ListControl(**kwargs)
        elif controlType.upper() == "LISTITEM":
            return self.ListItemControl(**kwargs)
        elif controlType.upper() == "PANE":
            return self.PaneControl(**kwargs)
        elif controlType.upper() == "RADIOBUTTON":
            return self.RadioButtonControl(**kwargs)
        elif controlType.upper() == "SCROLLBAR":
            return self.ScrollBarControl(**kwargs)
        elif controlType.upper() == "TEXT":
            return self.TextControl(**kwargs)
        elif controlType.upper() == "TREE":
            return self.TreeControl(**kwargs)
        elif controlType.upper() == "TREEITEM":
            return self.TreeItemControl(**kwargs)
        elif controlType.upper() == "WINDOW":
            return self.WindowControl(**kwargs)
        elif controlType.upper() == 'PROGRESSBAR':
            return self.ProgressBarControl(**kwargs)
        elif controlType.upper() == "TAB":
            return self.TabControl(**kwargs)
        elif controlType.upper() == "TABITEM":
            return self.TabItemControl(**kwargs)
        else:
            return Control(**kwargs)


class WindowControl(WindowControl, Control):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        super(WindowControl, self).__init__(element, searchFromControl, searchDepth, searchWaitTime, foundIndex,
                                            **searchPorpertyDict)


class ButtonControl(Control, ButtonControl):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        super(ButtonControl, self).__init__(element, searchFromControl, searchDepth, searchWaitTime, foundIndex,
                                            **searchPorpertyDict)

    def Active(self, waitTime=0.1):
        """
        Toggle or Invoke button with build-in Control instead of Click
        """
        if self.IsTogglePatternAvailable():
            self.SetFocus()
            self.Toggle()
        elif self.IsInvokePatternAvailable() is not None:
            self.SetFocus()
            self.Invoke(waitTime)
        else:
            self.SetFocus()

    def GetStatus(self):
        if not self.Exists(1, 1):
            print("Button not Found, Please Double check your parameter!!")
            return None
        if self.IsTogglePatternAvailable():
            return self.CurrentToggleState()
        else:
            return None

    def Enable(self):
        if not self.Exists(1, 1):
            print("Button not Found, Please Double check your parameter!!")
            return
        if self.IsTogglePatternAvailable():
            if self.CurrentToggleState():
                return
            else:
                # sometimes toggle method will not affect ui except clicking
                # but sometimes button is offscreen, so firstly setfocus
                self.SetFocus()
                self.Refind(maxSearchSeconds=TIME_OUT_SECOND, searchIntervalSeconds=self.searchWaitTime)
                if not self.IsOffScreen and self.IsEnabled:
                    self.Click()
        else:
            print('Button do not support Enable Control or is not shown')

    def Disable(self):
        if not self.Exists(1, 1):
            print("Button not Found, Please Double check your parameter!!")
            return
        if self.IsTogglePatternAvailable():
            if self.CurrentToggleState():
                # sometimes toggle method will not affect ui except clicking
                # but sometimes button is offscreen, so firstly setfocus
                self.SetFocus()
                self.Refind(maxSearchSeconds=TIME_OUT_SECOND, searchIntervalSeconds=self.searchWaitTime)
                if not self.IsOffScreen and self.IsEnabled:
                    self.Click()
            else:
                return
        else:
            print('Button do not support Enable Control or is not shown')


class TextControl(Control, TextControl):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        super(TextControl, self).__init__(element, searchFromControl, searchDepth, searchWaitTime, foundIndex,
                                          **searchPorpertyDict)

    def compareWith(self, obj):
        if not self.Exists():
            print("Text Box not Found, Please Double check your parameter!!")
            return
        if self.Name == obj:
            return True
        else:
            return False

    def contains(self, obj):
        if not self.Exists():
            print("Text Box not Found, Please Double check your parameter!!")
            return
        if str(obj).upper() in self.Name.upper():
            return True
        else:
            return False


class DataGridControl(Control, DataGridControl):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        super(DataGridControl, self).__init__(element, searchFromControl, searchDepth, searchWaitTime, foundIndex,
                                              **searchPorpertyDict)
        self.children = self.__get_children()

    def __get_children(self):
        """
        :return:  child_list
        {'header':
             {'col1_name': 'col1_obj,
              'col2_name': 'clo2_obj',
              'col3_name': 'clo3_obj'},
         'items':
             {'row1_obj':
                  {'rol1_col1_name': 'rol1_col1_obj',
                   'rol1_col2_name': 'rol1_col2_obj',
                   'rol1_col3_name': 'rol1_col3_obj'},
              'row2_obj':
                  {'rol2_col1_name': 'rol2_col1_obj',
                   'rol2_col2_name': 'rol2_col2_obj',
                   'rol2_col3_name': 'rol2_col3_obj'}}}
        """
        child_list = {'header': {}, 'data_items': {}}
        children = self.GetChildren()
        for child in children:
            # get header and its sub items
            # header_item: {header_item_name1: header_item1, header_item_name2: header_item2}
            header_item = {}
            if child.ControlType == ControlType.HeaderControl:
                for item in child.GetChildren():
                    header_item[item.Name] = item
                child_list['header'] = header_item
                break
        for child in children:
            # get DataItems and each sub items
            # items: store all the rows and rows' sub-item
            # sub_items: store each column name and element for one row
            items = {}
            if child.ControlType == ControlType.DataItemControl:
                sub_items = {}
                for item in child.GetChildren():
                    sub_items[item.Name] = item
                items[child] = sub_items
            child_list['data_items'].update(items)
        return child_list

    def refresh_list(self):
        self.children = self.__get_children()

    def page_down(self):
        """
        if datagrid support scroll, set scroll size += verticalViewSize
        :return: if can page down return True, if already 100% or do not support scroll, return False
        """
        default = 100
        if self.CurrentVerticallyScrollable():
            percent = self.CurrentVerticalScrollPercent()
            interval = self.CurrentVerticalViewSize()
            if percent == 100:
                return percent
            end_percent = percent + interval
            if default - end_percent >= interval:
                self.SetScrollPercent(self.CurrentHorizontalScrollPercent(), int(end_percent))
                self.refresh_list()
                return end_percent
            else:
                self.SetScrollPercent(self.CurrentHorizontalScrollPercent(), 100)
                self.refresh_list()
                return 100
        else:
            return 0

    def select(self, name, col=0, scrolls=3):
        """
        :param scrolls:
        :param col: name located col, start from 0
        :param name: name of column1 for each row
        :return: True if success
        """
        child: DataItemControl
        n = 2
        while n:
            for child in list(self.children['data_items'].keys()):
                if name.lower() in child.GetChildren()[col].Name.lower():
                    if child.IsOffScreen:
                        while self.page_down() != 100:  # sometimes hidden items cannot be click, need show item
                            pass
                    if not child.CurrentIsSelected():
                        child.SetFocus()
                        child.Click()
                        return True
            else:
                if self.page_down() == 100:
                    n -= 1
        raise ElementNotFoundError('Element {} Not Found, Please double check'.format(name))

    def unselect(self, name, col=0):
        """
        :param col: name located col, start from 0
        :param name: name of column1 for each row
        :return: None
        """
        flag = False
        for child in list(self.children['data_items'].keys()):
            if name.lower() in child.GetChildren()[col].Name.lower():
                if child.CurrentIsSelected():
                    child.SetFocus()
                    child.Click()
                flag = True
                break
        if not flag:
            raise ElementNotFoundError('Element {} Not Found, Please double check'.format(name))


class ComboBoxControl(Control, ComboBoxControl):
    def __init__(self, element=0, searchFromControl=None, searchDepth=0xFFFFFFFF, searchWaitTime=SEARCH_INTERVAL,
                 foundIndex=1, **searchPorpertyDict):
        super(ComboBoxControl, self).__init__(element, searchFromControl, searchDepth, searchWaitTime, foundIndex,
                                              **searchPorpertyDict)

    def select(self, name, waitTime: int = OPERATION_WAIT_TIME):
        """
        name: str
        options: option of keyword to select items
        waitTime: float
        Show combobox's popup menu and select a item by name.
        This is not a standard API in UIAutomation, here is a workaround.
        It may not work for some comboboxes, such as comboboxes in older Qt version.
        If it doesn't work, you should write your own version Select, or it doesn't support selection at all
        """
        supportExpandCollapse = self.IsExpandCollapsePatternAvailable()
        if supportExpandCollapse:
            self.Expand()
        else:
            # Windows Form's ComboBoxControl doesn't support ExpandCollapsePattern
            self.Click(-10, 0.5, False)
        find = False
        if isinstance(name, list):
            format_name = '.*'.join(name)
            reg_name = f'.*{format_name}.*'
        else:
            reg_name = '.*{}.*'.format(name)
        listItemControl = self.ListItemControl(RegexName=reg_name)

        if listItemControl.Exists(1):
            listItemControl.ScrollIntoView()
            listItemControl.Click(waitTime=waitTime)
            find = True
        else:
            # ComboBox's popup window is a child of root control
            listControl = ListControl(searchDepth=1)
            if listControl.Exists(1):
                listItemControl = listControl.ListItemControl(Name=name)
                if listItemControl.Exists(0, 0):
                    listItemControl.Click(waitTime=waitTime)
                    find = True
        if not find:
            Logger.ColorfulWriteLine('Can\'t find {} in ComboBoxControl'.format(name), ConsoleColor.Yellow)
            raise ElementNotFoundError('Can\'t find {}in ComboBoxControl'.format(name))

    def get_list(self):
        pass


def send_key(key, waitTime=0.1, count=1):
    for t in range(count):
        uiautomation.SendKey(key, waitTime=waitTime)


def getElementByType(controlType, **kwargs):
    # parent: Parent element
    # print(controlType, **kwargs)
    if controlType.upper() == "HYPERLINK":
        return HyperlinkControl(**kwargs)
    elif controlType.upper() == 'IMAGE':
        return ImageControl(**kwargs)
    elif controlType.upper() == 'APPBAR':
        return AppBarControl(**kwargs)
    elif controlType.upper() == 'CALENDAR':
        return CalendarControl(**kwargs)
    elif controlType.upper() == 'CUSTOM':
        return CustomControl(**kwargs)
    elif controlType.upper() == 'DOCUMENT':
        return DocumentControl(**kwargs)
    elif controlType.upper() == 'GROUP':
        return GroupControl(**kwargs)
    elif controlType.upper() == 'HEADER':
        return HeaderControl(**kwargs)
    elif controlType.upper() == 'HEADERITEM':
        return HeaderItemControl(**kwargs)
    elif controlType.upper() == 'SPINNER':
        return SpinnerControl(**kwargs)
    elif controlType.upper() == 'SLIDER':
        return SliderControl(**kwargs)
    elif controlType.upper() == 'SEPARATOR':
        return SeparatorControl(**kwargs)
    elif controlType.upper() == 'SEMANTICZOOM':
        return SemanticZoomControl(**kwargs)
    elif controlType.upper() == 'MENUITEM':
        return MenuItemControl(**kwargs)
    elif controlType.upper() == 'MENU':
        return MenuControl(**kwargs)
    elif controlType.upper() == 'MENUBAR':
        return MenuBarControl(**kwargs)
    elif controlType.upper() == 'TABLE':
        return TableControl(**kwargs)
    elif controlType.upper() == 'STATUSBAR':
        return StatusBarControl(**kwargs)
    elif controlType.upper() == 'SPLITBUTTON':
        return SplitButtonControl(**kwargs)
    elif controlType.upper() == 'THUMB':
        return ThumbControl(**kwargs)
    elif controlType.upper() == 'TITLEBAR':
        return TitleBarControl(**kwargs)
    elif controlType.upper() == 'TOOLTIP':
        return ToolTipControl(**kwargs)
    elif controlType.upper() == "BUTTON":
        return ButtonControl(**kwargs)
    elif controlType.upper() == "COMBOX":
        return ComboBoxControl(**kwargs)
    elif controlType.upper() == "CHECKBOX":
        return CheckBoxControl(**kwargs)
    elif controlType.upper() == "DATAGRID":
        return DataGridControl(**kwargs)
    elif controlType.upper() == "DATAITEM":
        return DataItemControl(**kwargs)
    elif controlType.upper() == "EDIT":
        return EditControl(**kwargs)
    elif controlType.upper() == "LIST":
        return ListControl(**kwargs)
    elif controlType.upper() == "LISTITEM":
        return ListItemControl(**kwargs)
    elif controlType.upper() == "PANE":
        return PaneControl(**kwargs)
    elif controlType.upper() == "RADIOBUTTON":
        return RadioButtonControl(**kwargs)
    elif controlType.upper() == "SCROLLBAR":
        return ScrollBarControl(**kwargs)
    elif controlType.upper() == "TEXT":
        return TextControl(**kwargs)
    elif controlType.upper() == "TREE":
        return TreeControl(**kwargs)
    elif controlType.upper() == "TREEITEM":
        return TreeItemControl(**kwargs)
    elif controlType.upper() == "WINDOW":
        return WindowControl(**kwargs)
    elif controlType.upper() == 'PROGRESSBAR':
        return ProgressBarControl(**kwargs)
    elif controlType.upper() == "TAB":
        return TabControl(**kwargs)
    elif controlType.upper() == "TABITEM":
        return TabItemControl(**kwargs)
    else:
        return Control(**kwargs)


def get_pix(x, y, obj=None):
    """
    :param x: int, x position on screen | element from UIAutomation
    :param y: int, y position on screen | element from UIAutomation
    :param obj: UIAutomation object
        None or element by UIAutomation
        obj=None: get given position pixel in current screen
        obj=element: get given position pixel in element
        x, y out of range will raise exception
    :return: RGB value (r, g, b)
    """
    if obj:
        obj.CaptureToImage('temp_color.jpg')
        obj_img = Image.open('temp_color.jpg')
        pix = obj_img.load()
        obj_img.close()
        os.remove('temp_color.jpg')
        return pix[x, y][:3]
    else:
        img_img = ImageGrab.grab()
        return img_img.getpixel((x, y))


if __name__ == '__main__':
    # a = win32net.NetUserGetInfo(win32net.NetGetAnyDCName(), win32api.GetUserName(), 2)
    e = uiautomation.ButtonControl(Name='Back')
    _pix = get_pix(10, 10, e)
    print(_pix)
