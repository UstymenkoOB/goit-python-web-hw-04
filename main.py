from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import datetime
import json
import mimetypes
import pathlib
import socket
import urllib.parse


class HttpHandler(BaseHTTPRequestHandler):
    def socket_client(self, data):
        host = socket.gethostname()
        port = 5000
        
        cl_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cl_socket.connect((host, port))

        cl_socket.send(data.encode())

        cl_socket.close()

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.socket_client(data.decode())

        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def server_socket():
    print("Socket server start")
    host = socket.gethostname()
    port = 5000
    
    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv_socket.bind((host, port))
    
    try:
        while True:
            conn, address = serv_socket.recvfrom(1024)
            print(f'Connection from {address}')
            data = conn.decode()
            print(f'Received message: {data}')
            data_parse = urllib.parse.unquote_plus(data)
            data_dict = {key: value for key, value in [
                el.split('=') for el in data_parse.split('&')]}
            mess = dict()
            with open("storage/data.json", "r") as file:
                mess = json.load(file)
            mess[str(datetime.datetime.now())] = data_dict
            with open("storage/data.json", "w") as file:
                json.dump(mess, file)
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        serv_socket.close()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    try:
        print("Start")
        socket_server = Thread(target=server_socket)
        socket_server.start()
        http.serve_forever()

    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
