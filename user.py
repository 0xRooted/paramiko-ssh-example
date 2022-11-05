import paramiko, server, socket, threading, json

from sshdefs import *
from banners import *

def load_config():
    with open("config.json", "r+") as f:
        CONFIG = json.loads(f.read())
    return CONFIG

class user:
    
    # session:paramiko.Transport, channel:paramiko.Channel
    def __init__(self, fd:socket.socket, addr, hostkey:paramiko.RSAKey):
        
        self.fd = fd
        self.session = None
        self.channel = None
        self.ip = addr[0]
        self.port = addr[1]
        self.input = ""
        self.hostkey = hostkey
        self.isAlive = True
        self.backspace_count = 0
        self.history = []
        self.server = None
    
    
    def setup(self):
        self.session = paramiko.Transport(self.fd)
        self.session.set_gss_host(socket.getfqdn(""))
        self.session.load_server_moduli()
        self.session.add_server_key(self.hostkey)
        self.server = server.server()
        self.session.start_server(server=self.server)
        self.channel = self.session.accept(30)
        if self.channel is None:
            self.session.close()
        else:
            self.handler()
    
    def reset_line(self):
        self.channel.send("\033[2K".encode())
    
    def cls(self):
        self.channel.send("\033\143".encode())
    
    def recv(self, prompt:str, formatinput:bool = False, Fullbuff:bool = False):
        
        if Fullbuff:
            self.reset_line()
        
        if Fullbuff:
            self.input = ""
        
        if Fullbuff:
            while True:
                self.reset_line()
                if formatinput:
                    self.channel.send("\r{} ".format(prompt))
                    if len(self.input) > 0:
                        self.channel.send("{}".format(self.input))
                else:
                    self.channel.send("\r{}".format(prompt))
                curr_char = self.channel.recv(1024).decode()
                if len(curr_char) > 1:
                    continue
                elif len(curr_char) == 1:
                    curr_char_hex = ord(curr_char)
                    if curr_char_hex == SSH_KEY_BACKSPACE:
                        if len(self.input) > 0:
                            self.input = self.input[0: -1]
                            continue
                        else:
                            continue
                    if curr_char_hex == SSH_KEY_NEWLINE:
                        return {
                            'buffer': self.input,
                            'length': len(self.input)
                        }
                    if curr_char_hex != SSH_KEY_BACKSPACE or curr_char_hex != SSH_KEY_NEWLINE:
                        self.input += curr_char
                else:
                    continue
        else:
            self.input += curr_char
    
    def handler(self):
        self.cls()
        self.channel.send(DEVIL)
        while self.isAlive:
            CONFIG = load_config()
            ssh_prompt = CONFIG.get('ssh_prompt')
            try:
                buff_data = self.recv(ssh_prompt, formatinput=True, Fullbuff=True)
                buffer = buff_data.get('buffer')
                self.history.append(buffer)
                buffer_len = buff_data.get('length')
                if buffer.lower() == "logout":
                    break
                elif buffer == "clear".lower() or buffer.lower() == "cls":
                    self.cls()
                    self.channel.send(DEVIL)
                elif buffer.lower() == "history":
                    temp = 0
                    for history in self.history:
                        self.channel.send("\r\n[#{}] {}".format(temp, history))
                        temp += 1
                    self.channel.send("\r\n")
                    self.channel.send("[PRESS ANY CHAR TO CLEAR]\r\n")
                    self.channel.recv(1024).decode()
                    self.cls()
            except:
                self.isAlive = False
                self.session.close()
        self.isAlive = False
        self.session.close()