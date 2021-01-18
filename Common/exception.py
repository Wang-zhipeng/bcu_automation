class FileNotExistError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class ElementNotFoundError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class AnalyzeNameError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class LogonError(Exception):
    """
        LogonError
    """
    pass


class ServerNotExitError(LogonError):
    """
        ClientError
    """
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return "Failed to check the initial destination server:" + self.s


class AuthenticationError(LogonError):
    """
        ClientError
    """
    def __init__(self, s="Authentication failure, check credentials:"
                         "\r\ncheck usr, domain, password"):
        self.s = s

    def __str__(self):
        return self.s


class ClientSeverError(LogonError):
    """
        ClientError
    """
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CertificationError(LogonError):
    """
        ClientError
    """

    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class VDILogonError(LogonError):
    """
    use it if you don't know specific case why fail to logon
    """
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CreateVDIError(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class DeleteVDIError(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class Continue(LogonError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class LogoffError(Exception):
    """
    LogoffError
    """


class SocketError(LogoffError):
    """
    SocketError
    """
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class ConnectionRefused(LogoffError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class LogoffTimeout(LogoffError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class UIAutomationError(Exception):
    """
    UIAutomationError
    """


class UICantFindError(UIAutomationError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class MagicKeyFunctionError(Exception):
    """
    MagicKeyError
    """
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CaptureFlowError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CaptureStartError(CaptureFlowError):
    def __init__(self, s="Capture Start Detect Fail"):
        self.s = s

    def __str__(self):
        return self.s


class PictureCantFind(CaptureFlowError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class RestoreBiosError(CaptureFlowError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class CaseRunningError(Exception):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s


class BiosSetError(CaseRunningError):
    def __init__(self, s=""):
        self.s = s

    def __str__(self):
        return self.s
