"""
Error --> Base
1.camera can not be found
2.camera can be found, but doesn't work
3.magic key can not be found
4.magic key send keys failed
5.STM32 can not be found
6.STM32 can be found, but doesn't work
"""
from Common.log import log


class EyeNotExistError(Exception):
    def __init__(self):
        log.error('[!] EyeNotExistError : Program Termination ! ')


class EyeFunctionError(Exception):
    def __init__(self):
        log.error('[!] EyeFunctionError : Program Termination ! ')


# Added by lena
class HandNotExistError(Exception):
    def __init__(self):
        log.error('[!] HandNotExistError : Program Termination ! ')


class VideoCaptureCardFunctionError(Exception):
    def __init__(self):
        log.error('[!] VideoCaptureCardFunctionError : Program Termination ! ')


class MagicKeyNotExistError(Exception):
    def __init__(self):
        log.error('[!] MagicKeyNotExistError : Program Termination ! ')


class MagicKeyFunctionError(Exception):
    def __init__(self):
        log.error('[!] MagicKeyFunctionError : Program Termination ! ')


class STM32NotExistError(Exception):
    def __init__(self):
        log.error('[!] STM32NotExistError : Program Termination ! ')


class STM32FunctionError(Exception):
    def __init__(self):
        log.error('[!] STM32FunctionError : Program Termination ! ')


class ManSiteError(Exception):
    def __init__(self):
        log.error('[!] ManSiteError : Program Termination ! ')
