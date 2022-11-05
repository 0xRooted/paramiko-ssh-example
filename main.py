import server, paramiko, threading, os, user, json

def main():
    with open("config.json", "r+") as f:
        CONFIG = json.loads(f.read())
    host = CONFIG.get('host')
    port = CONFIG.get('port')
    key = CONFIG.get('ssh_rsa_key_path')
    RSA_KEY = paramiko.RSAKey(filename=key)
    SERVER = server.server_handle(host, port, RSA_KEY)
    handle_thread = threading.Thread(target=SERVER.hanlder)
    handle_thread.start()
    print('[LOG] - [SSH SERVER STARTED] - [HOST: {}] - [PORT: {}]'.format(host, port))
    handle_thread.join()

main()