import socket
import os

content = b"""RESPMOD icap://athena.local/respmod ICAP/1.0
Host: 10.10.64.102
Encapsulated: req-hdr=0, res-hdr=137, res-body=296
X-client-IP: {CLIENTIP}
user-agent: C-ICAP-Client-Library/0.5.9
preview: 10240

GET {LINK} HTTP/1.1
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


def icap_client(content=content, host='192.192.192.192', **kwargs):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((kwargs['stand'], kwargs['port']))

    with open(kwargs['item'], "rb") as f:
        data = f.read()
        content = content.replace(b"{CONTENTLEN}", hex(len(data)).encode())
        
    content = content.replace(b"{CLIENTIP}", host.encode())
    content = content.replace(b"{LINK}", f'/{kwargs["desc"][-5:]}'.replace(':', '_').encode())
    content = content.replace(b"{FILENAME}", os.path.basename(kwargs['item']).encode())
    content = content.replace(b"{CONTENT}", data)
    content = content.replace(b"{ContentLength}", str(len(content.rsplit(b"\r\n\r\n", 2)[1])).encode())

    client_socket.send(content)
    client_socket.close()