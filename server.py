import socket
from threading import Thread
import os
import time

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

SERVER = None
IP_ADDRESS = '127.0.0.1'
PORT = 8050
BUFFER_SIZE = 4096
clients = {}

is_dir_exists = os.path.isdir('shared_files')
if(not is_dir_exists):
    os.makedirs('shared_files')

def acceptConnections():
  global SERVER, clients

  while True:
    client, addr = SERVER.accept()
    client_name = client.recv(BUFFER_SIZE).decode().lower()
    clients[client_name] = {
      "client"        : client,
      "address"       : addr,
      "connected_with": "",
      "file_name"     : "",
      "file_size"     : BUFFER_SIZE
    }
    print(f"Connection established with {client_name} : {addr}")

    thread = Thread(target=handleClient, args=(client, client_name))
    thread.start()

def handleClient(client, client_name):
  pass

def setup():
  print("\n\t\t\t\t\t\tIP MESSENGER\n")

  global SERVER, IP_ADDRESS, PORT

  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.bind((IP_ADDRESS, PORT))
  SERVER.listen(100)

  print("\t\t\t\tSERVER IS WAITING FOR INCOMMING CONNECTIONS...\n")

  acceptConnections()

def ftp():
  authorizer = DummyAuthorizer()
  authorizer.add_user("lftpd", "lftpd", ".", perm="elradfmw")

  handler = FTPHandler
  handler.authorizer = authorizer

  ftp_server = FTPServer((IP_ADDRESS, 21), handler)
  ftp_server.serve_forever()

setup_thread = Thread(target=setup)
setup_thread.start()

ftp_thread = Thread(target=ftp)
ftp_thread.start()