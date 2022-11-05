import paramiko, socket, threading, os, user, json

HOSTKEY = None

def load_config():
    with open("config.json", "r+") as f:
        CONFIG = json.loads(f.read())
    return CONFIG

class server_handle:
    
    def __init__(self, ip:str, port:int, hostkey:paramiko.RSAKey):
        global HOSTKEY
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(socket.SOMAXCONN)
        self.host_key = hostkey
        HOSTKEY = hostkey
        self.connections = []
    
    def hanlder(self):
        while True:
            CONFIG = load_config()
            try:
                fd, addr = self.sock.accept()
                new = user.user(fd, addr, self.host_key)
                self.connections.append(new)
                threading.Thread(target=new.setup).start()
                if CONFIG.get('log_ssh_connections'):
                    print("[NEW-CONNECTION]-[IP: {}]-[PORT: {}]".format(addr[0], addr[1]))
            except Exception as e:
                if CONFIG.get('log_ssh_connection_errors'):
                    print('[NEW-ERROR] : {}'.format(e))
    

class server(paramiko.ServerInterface):
    
    def __init__(self):
        global HOSTKEY
        self.event = threading.Event()
        self.host_key = HOSTKEY
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return True

    def check_auth_password(self, username, password):
        CONFIG = load_config()
        if username == CONFIG.get('default_user') and password == CONFIG.get('defualt_password'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True