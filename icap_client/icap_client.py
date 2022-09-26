import socket
import os
import time
from multiprocessing import Pool

content = b"""RESPMOD icap://athena.local/respmod ICAP/1.0
Host: 10.10.64.102
Encapsulated: req-hdr=0, res-hdr=137, res-body=296
X-client-IP: {CLIENTIP}
user-agent: C-ICAP-Client-Library/0.5.9
preview: 10240

GET /origin-resource HTTP/1.1
Host: 10.10.64.102
Accept: text/html, text/plain, image/gif
Accept-Encoding: gzip, compress

HTTP/1.1 200 OK
Date: Mon, 10 Jan 2000 09:52:22 GMT
Server: Apache/1.3.6 (Unix)
ETag: "63840-1ab7-378d415b"
Content-Length: {ContentLength}
content-disposition: attachment; filename="{FILENAME}"

{CONTENTLEN}
{CONTENT}
0

""".replace(b"\n", b"\r\n")


class ICAPClient:

    def __init__(self, stand, threads, files, host="2.2.2.2"):
        self.stand = stand
        self.host = host
        # print('HOST: ', self.host)
        self.threads = threads
        self.files = files
        self.content = content.replace(b"{CLIENTIP}", self.host.encode())
        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.client_socket.connect((stand, 13440))

    def send_files(self, filename):
        time.sleep(2)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.stand, 13440))

        print('Filename is:', filename)
        with open(filename, "rb") as f:
            data = f.read()
            self.content = self.content.replace(b"{CONTENTLEN}", hex(len(data)).encode())
            self.content = self.content.replace(b"{FILENAME}", os.path.basename(filename).encode())
            self.content = self.content.replace(b"{CONTENT}", data)
            self.content = self.content.replace(b"{ContentLength}", str(len(self.content.rsplit(b"\r\n\r\n", 2)[1])).encode())

        # print('Content is: ', self.content)
        client_socket.send(self.content)
        os.remove(filename)
        client_socket.close()

    def execute_send_files(self):
        # for file in self.files:
        #     self.send_files(file)
        with Pool(self.threads) as p:
            p.map(self.send_files, self.files)
        # self.client_socket.close()


