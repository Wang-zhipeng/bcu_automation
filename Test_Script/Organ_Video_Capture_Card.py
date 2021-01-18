import sys
from ctypes import *
import os
import time
import threading
import platform
from PyQt5 import QtWidgets

from Common import ui_automation
from Common.common_function import OSTool
from Common.log import log


class QWindow(QtWidgets.QWidget):
    dll_p = OSTool.get_current_dir("Test_Utility")
    os.environ['path'] += ';{}'.format(dll_p)
    bit = platform.architecture()[0]
    if bit == '32bit':
        QCAP = CDLL(OSTool.get_current_dir('Test_Utility', 'QCAP.X86.DLL'))
    else:
        QCAP = CDLL(OSTool.get_current_dir('Test_Utility', 'QCAP.X64.DLL'))
    device0 = c_void_p(0)
    m_nVideoWidth = c_ulong(0)
    m_nVideoHeight = c_ulong(0)
    m_dVideoFrameRate = c_double(0.0)
    m_nAudioChannels = c_ulong(0)
    m_nAudioBitsPerSample = c_ulong(0)
    m_nnAudioSampleFrequency = c_ulong(0)
    m_startrecord = False

    # Create the C callable callback
    PF_NO_SIGNAL_DETECTED_CALLBACK = CFUNCTYPE(c_ulong, c_void_p, c_long, c_long, c_void_p)
    PF_SIGNAL_REMOVED_CALLBACK = CFUNCTYPE(c_ulong, c_void_p, c_long, c_long, c_void_p)
    PF_FORMAT_CHANGED_CALLBACK = CFUNCTYPE(c_ulong, c_void_p, c_ulong, c_ulong, c_ulong, c_ulong, c_int, c_double,
                                           c_ulong,
                                           c_ulong, c_ulong, c_void_p)
    PF_VIDEO_PREVIEW_CALLBACK = CFUNCTYPE(c_ulong, c_void_p, c_double, c_void_p, c_ulong, c_void_p)
    PF_AUDIO_PREVIEW_CALLBACK = CFUNCTYPE(c_ulong, c_void_p, c_double, c_void_p, c_ulong, c_void_p)

    QCAP_START_RECORD = CFUNCTYPE(c_ulong, c_void_p, c_uint, c_char_p, c_ulong, c_double, c_double, c_double, c_ulong,
                                  c_char_p)

    def __init__(self):
        log.info("%r" % super(QWindow, self))
        super(QWindow, self).__init__()
        self.setWindowTitle("Preview")
        self.setGeometry(0, 0, 1024, 650)
        self.signal = 0

        def on_no_signal_detected(pDevice, nVideoInput, nAudioInput, pUserData):
            log.info("------------no signal detected callback----------------")
            print(nVideoInput)
            self.signal = 0
            return 0

        def on_signal_removed(pDevice, nVideoInput, nAudioInput, pUserData):
            self.signal = 0
            log.info("------------signal removed callback----------------")
            return 0

        def on_format_changed(pDevice, nVideoInput, nAudioInput, nVideoWidth, nVideoHeight, bVideoIsInterleaved,
                              dVideoFrameRate, nAudioChannels, nAudioBitsPerSample, nAudioSampleFrequency, pUserData):
            log.info("-on_process_format_changed (%d, %d, %d, %d, %d, %f, %d, %d, %d, %r)" % (
                nVideoInput, nAudioInput, nVideoWidth, nVideoHeight, bVideoIsInterleaved, dVideoFrameRate,
                nAudioChannels,
                nAudioBitsPerSample, nAudioSampleFrequency, pUserData))

            global m_nVideoWidth, m_nVideoHeight, m_dVideoFrameRate, m_nAudioChannels, m_nAudioBitsPerSample, m_nnAudioSampleFrequency

            if nVideoWidth != 0 and nVideoHeight != 0:
                m_nVideoWidth = nVideoWidth
                m_nVideoHeight = nVideoHeight
                m_dVideoFrameRate = dVideoFrameRate
                m_nAudioChannels = nAudioChannels
                m_nAudioBitsPerSample = nAudioBitsPerSample
                m_nnAudioSampleFrequency = nAudioSampleFrequency

            return 0

        def on_video_preview(pDevice, dSampleTime, pFrameBuffer, nFrameBufferLen, pUserData):
            self.signal = 1
            return 0

        def on_audio_preview(pDevice, dSampleTime, pFrameBuffer, nFrameBufferLen, pUserData):
            return 0

        self.m_pNoSignalDetectedCB = self.PF_NO_SIGNAL_DETECTED_CALLBACK(on_no_signal_detected)
        self.m_pSignalRemovedCB = self.PF_SIGNAL_REMOVED_CALLBACK(on_signal_removed)
        self.m_pFormatChangedCB = self.PF_FORMAT_CHANGED_CALLBACK(on_format_changed)
        self.m_pVideoPreviewCB = self.PF_VIDEO_PREVIEW_CALLBACK(on_video_preview)
        self.m_pAudioPreviewCB = self.PF_AUDIO_PREVIEW_CALLBACK(on_audio_preview)

        # strName = "CY3014 USB"  # For UB530
        strName = "UB3300 USB"  # For UB570
        # QCAP.QCAP_CREATE(strName.encode('utf-8'), 0, 0, byref(device0), 0, 0)
        # QCAP.QCAP_CREATE(strName.encode('utf-8'), 0, c_int32(widget.winId()), byref(device0), 1, 0)
        self.QCAP.QCAP_CREATE(strName.encode('utf-8'), 0, c_int32(self.winId()), byref(self.device0), 1, 0)
        # QCAP.QCAP_SET_VIDEO_DEFAULT_OUTPUT_FORMAT(device0, 0x32595559, 1920, 1080, 0, c_double(30.0))
        self.QCAP.QCAP_REGISTER_FORMAT_CHANGED_CALLBACK(self.device0, self.m_pFormatChangedCB, None)
        self.QCAP.QCAP_REGISTER_NO_SIGNAL_DETECTED_CALLBACK(self.device0, self.m_pNoSignalDetectedCB, None)
        self.QCAP.QCAP_REGISTER_SIGNAL_REMOVED_CALLBACK(self.device0, self.m_pSignalRemovedCB, None)
        self.QCAP.QCAP_REGISTER_VIDEO_PREVIEW_CALLBACK(self.device0, self.m_pVideoPreviewCB, None)
        self.QCAP.QCAP_REGISTER_AUDIO_PREVIEW_CALLBACK(self.device0, self.m_pAudioPreviewCB, None)
        # QCAP.QCAP_RUN(device0)
        with open('port.txt') as f:
            port = f.read()
            if not port:
                port = 2
            os.remove('port.txt')
            self.QCAP.QCAP_SET_VIDEO_INPUT(self.device0, port)  # For HDMI input
        # QCAP.QCAP_SET_VIDEO_INPUT(device0, 3)  # For DVI-D input
        self.QCAP.QCAP_RUN(self.device0)

    def stop(self):
        if self.device0 != 0:
            self.QCAP.QCAP_STOP(self.device0)
            self.QCAP.QCAP_DESTROY(self.device0)
        self.device0 = c_void_p(0)

    def closeEvent(self, event):
        self.stop()
        self.close()


class SnapshotJPG:
    def __init__(self):
        # pythoncom.CoInitialize()
        log.info("Init snapshot jpg......")
        self.quick_capture_card = None
        self.pic_memory_path = OSTool.get_current_dir('Test_Data', 'video_card')
        self.pic_name = self.pic_memory_path + r'\view.jpg'
        if not os.path.exists(self.pic_memory_path):
            os.makedirs(self.pic_memory_path)

    def check_video(self, wnd, port):
        ui_automation.RadioButtonControl(AutomationId=port).Click()
        time.sleep(3)
        if wnd.Exists():
            print('exist')
            # ui_automation.RadioButtonControl(AutomationId='33001').Click()
            reslotion = ui_automation.TextControl(AutomationId='1019').Name
            if 'no' in reslotion.lower():
                print('not connected')
                return False
            elif '1920 x 0 p' in reslotion.lower():
                print('no signal')
                return False
            else:
                print('connected')
                return True
        else:
            print('uvc not launched')
            return False

    def start(self):
        os.popen(OSTool.get_current_dir('Test_Utility', 'UVC.UTILITY.X86_V1.56.EXE'))
        # name: DVI-D 33003  HDMI 33001
        # ID: 1019 UVC Utility
        time.sleep(3)
        wnd = ui_automation.WindowControl(Name='UVC Utility')
        ports = {'HDMI': '33001', 'DVI': '33003'}
        if not self.check_video(wnd, ports['HDMI']):
            if not self.check_video(wnd, ports['DVI']):
                log.error('Both HDMI and DVI cannot detect signal')
                sys.exit()
            else:
                with open('port.txt', 'w') as f:
                    f.write('3')
        else:
            with open('port.txt', 'w') as f:
                f.write('2')
        if wnd.Exists():
            wnd.Close()
        app = QtWidgets.QApplication(sys.argv)
        self.quick_capture_card = QWindow()
        self.quick_capture_card.show()
        sys.exit(app.exec_())

    def snapshot(self):
        QWindow.QCAP.QCAP_SNAPSHOT_JPG(QWindow.device0, self.pic_name.encode('utf-8'), 100, 1, 0)

    def release(self):
        del self.quick_capture_card
        # pythoncom.CoUninitialize()


if __name__ == '__main__':
    vccard = SnapshotJPG()
    t = threading.Thread(target=vccard.start)
    t.start()
    time.sleep(3)
    vccard.snapshot()
