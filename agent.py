from Common import socket_action, common_function
from Common.log import log
import sys
import platform
import os

if 'windows' in platform.platform().lower():
    __OS = 'Windows'
else:
    __OS = 'Linux'


def get_server_ip():
    if os.path.exists(r'c:\temp\ip.txt'):
        with open(r'c:\temp\ip.txt') as f:
            return f.read()
    else:
        log.error('[agent][get server ip]c:\\temp\\ip.txt not exist')
        return '127.0.0.1'


def save_server_ip(ip):
    with open(r'c:\temp\ip.txt', 'w') as f:
        f.write(ip)


sock_agent = socket_action.SocketAgent(50000)
sock_client = socket_action.SocketClient()

if __name__ == '__main__':
    if not os.path.exists(r'c:\temp'):
        os.mkdir(r'c:\temp')
    if len(sys.argv) > 1:
        save_server_ip(sys.argv[1])