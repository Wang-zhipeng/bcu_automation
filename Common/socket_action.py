import json
import os
import socket
import threading
import traceback
from Common.log import log

encoding = 'utf-8'
BUFFSIZE = 2048


class AgentAction(threading.Thread):
    """Agent logic according client's command"""
    def __init__(self, socket_conn: socket.socket):
        super().__init__()
        self.__sock = socket_conn

    def run(self):
        while True:
            if not self.__sock:
                log.info('[Agent Action]Connection break...')
                break
            data = self.__sock.recv(BUFFSIZE)
            if not data:
                log.info('[Agent Action]Receive nothing from client.')
                self.__sock.sendall('Fail,Receive nothing from client'.encode(encoding))
                continue
            string = data.decode(encoding)
            log.debug("[Agent Action]Content from client: {}.".format(string))
            string_list = string.split(':', 1)
            if string.upper() == 'BYE':
                log.info("[Agent Action]Agent Connection Closed")
                self.__sock.close()
                break
            elif string_list[0].strip().upper() == 'CMD':
                script = string_list[1].strip()
                run_result = self.run_scripts(script)
                log.debug(f'[Agent Action][run]Agent execute cmd: {script} result: {run_result}')
                if run_result is False:
                    self.__sock.sendall('Fail,run scripts fail'.encode(encoding))
                elif len(run_result) > 0:
                    result_str = '\n'.join(run_result)
                    self.__sock.sendall('Pass,{}'.format(result_str).encode(encoding))
                else:
                    self.__sock.sendall('Fail,run scripts done with no return value'.encode(encoding))
                continue
            elif string_list[0].strip().upper() == 'DEPLOY':
                head_info: dict = json.loads(string_list[1])
                file_path = head_info.get('remote_path')
                file_size = head_info.get('file_size')
                self.__sock.sendall('get file info, begin to download'.encode(encoding))
                recv_len = 0
                if os.path.exists(file_path):
                    os.remove(file_path)
                f = open(file_path, 'ab')
                while recv_len < file_size:
                    recv_msg = self.__sock.recv(BUFFSIZE)
                    f.write(recv_msg)
                    recv_len += len(recv_msg)
                f.close()
                self.__sock.sendall('Success'.encode(encoding))
                continue
            elif string_list[0].strip().upper() == 'CAPTURE':
                file_name = string_list[1]
                with open(file_name, 'rb') as f:
                    size = len(f.read())
                    dirc = {
                        'file_name': file_name,
                        'file_size': size
                    }
                head_info = json.dumps(dirc)  # convert dict to string
                self.__sock.sendall(f'{head_info}'.encode(encoding))
                with open(file_name, 'rb') as f_local:
                    data = f_local.read()
                    self.__sock.sendall(data)
            else:
                log.info('[Agent Action]Invalid message {}.'.format(string))
                self.__sock.sendall('Fail,Invalid message from client'.encode(encoding))
                continue

    @staticmethod
    def run_scripts(scripts):
        try:
            result = os.popen(scripts).readlines()
            return result
        except:
            log.error('[Agent Action]Run scripts meet exception:\n{}'.format(traceback.format_exc()))
            return False


class ClientAction:
    def __init__(self, socket_conn):
        self.__sock = socket_conn


class SocketAgent(threading.Thread):
    """ Socket agent server, all logic depends on AgentAction"""
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(0)

    def run(self):
        log.info("[Socket Agent]Socket Agent Listener started.")
        while 1:
            try:
                client_socket, client_addr = self.sock.accept()
                log.info("[Sokcet Agent]Accept a connect from client {}.".format(client_addr))
                agent_action = AgentAction(client_socket)
                agent_action.start()
            except:
                log.error('[Socket Agent][Run]Socket meet exception:\n{}'.format(traceback.format_exc()))


class SocketClient:
    """class of socket client"""
    def __init__(self):
        self.__sock = socket.socket()

    def connect(self, ip, port):
        """
        connect to socket server according ip and port
        :param ip: socket server bind ip
        :param port: socket server bind port
        :return: None
        """
        log.info('[Socket Client]Begin to connect: host: {}-{}'.format(ip, port))
        try:
            self.__sock = socket.socket()
            self.__sock.connect((ip, port))
            log.info('[Socket Client]Successfully connect to host: {}-{}'.format(ip, port))
        except:
            log.info("[Socket Client]Socket Connect Error: \n{}".format(traceback.format_exc()))

    def send_command(self, command):
        """
        send command to socket server, return command execute result
        :param command: windows command, linux command
        :return: command execute result
        """
        command = f'cmd:{command}'
        try:
            log.info('[Socket Client]Send command: {}'.format(command))
            self.__sock.sendall(command.encode(encoding))
            data = self.__sock.recv(BUFFSIZE)
            log.debug('[Socket Client]get response from agent: \n{}'.format(data.decode(encoding)))
            return data.decode(encoding)
        except:
            log.info('[Socket Client]Failed to Send command: {},'
                     'Exception:\n{}'.format(command, traceback.format_exc()))
            return None

    def deploy_file(self, local_path, remote_path):
        """
        send file to socket server
        :param local_path: full path of located file
        :param remote_path: save as full path in agent server
        :return: feed back from agent server
        """
        try:
            log.info(f'[Socket Client][deploy file] Begin to send file {local_path}')
            with open(local_path, 'rb') as f:
                size = len(f.read())
                dirc = {
                    'local_path': local_path,
                    'remote_path': remote_path,
                    'file_size': size
                }
            head_info = json.dumps(dirc)  # convert dict to string
            self.__sock.sendall(f'deploy:{head_info}'.encode(encoding))
            log.debug('[Socket Client][deploy file]send file head information to agent')
            if self.__sock.recv(BUFFSIZE).decode(encoding) == 'get file info, begin to download':
                with open(local_path, 'rb') as f_local:
                    data = f_local.read()
                    self.__sock.sendall(data)
                    return self.__sock.recv(2048).decode(encoding)
            else:
                log.error('[Socket Client][deploy file] Fail to deploy '
                          'file because agent does not receive file information')
                return "Fail, agent doesn't get file information"
        except:
            log.error(f'[Socket Client][deploy file] Fail becuase exception:\n{traceback.format_exc()}')
            return False

    def capture_file(self, local_path, remote_path):
        """
        get file from agent server
        :param local_path: save as located full path
        :param remote_path: Full path of file in agent server
        :return: get file result
        """
        if os.path.exists(local_path):
            os.remove(local_path)
        try:
            log.info(f'[Socket Client][capture file] Begin to capture file {remote_path}')
            self.__sock.sendall(f'capture:{remote_path}'.encode(encoding))
            file_info = json.loads(self.__sock.recv(BUFFSIZE).decode(encoding))
            file_size = file_info.get('file_size', 0)
            log.debug(f'[Socket Client][capture file]get head info from agent: {file_info}')
            recv_len = 0
            f = open(local_path, 'ab')
            while recv_len < file_size:
                recv_msg = self.__sock.recv(BUFFSIZE)
                f.write(recv_msg)
                recv_len += len(recv_msg)
            f.close()
            if os.path.exists(local_path):
                log.info(f'[Socket Client][capture file]successfully capture file {local_path} from agent')
                return 'Pass, capture finished'
            else:
                log.error(f'[Socket Client][capture file]Failed capture file {local_path} from agent')
                return 'Fail, local file not exist'
        except:
            log.error(f'[Socket Client][capture file] Fail becuase exception:\n{traceback.format_exc()}')
            return False

    def close(self):
        """
        1. disconnect connection from agent
        2. close client connection
        :return: NOne
        """
        self.__sock.sendall('bye'.encode(encoding))
        self.__sock.close()
        log.info('[Socket Client]client request disconnect from server')
