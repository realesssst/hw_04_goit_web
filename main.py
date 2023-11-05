import socket
import http.server
import socketserver
import http.client
from threading import Thread
import json
from datetime import datetime
import os

HTTP_PORT = 3000
SOCKET_PORT = 5000

if not os.path.exists('storage'):
    os.makedirs('storage')

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

http_thread = Thread(target=lambda: http.server.test(HandlerClass=MyHandler, port=HTTP_PORT))
http_thread.start()

class UDPServer:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            try:
                message = json.loads(data)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                message_data = {
                    timestamp: {
                        'username': message['username'],
                        'message': message['message']
                    }
                }
                with open('storage/data.json', 'a+') as file:
                    file.seek(0, 2)
                    if file.tell() == 0:
                        file.write(json.dumps(message_data, indent=4))
                    else:
                        file.seek(-1, os.SEEK_END)
                        file.truncate()
                        file.write(',')
                        file.write(json.dumps(message_data, indent=4))
                        file.write('}')
                print(f"Received message: {message['message']} from {message['username']}")
            except json.JSONDecodeError:
                print("Received invalid JSON")

socket_thread = Thread(target=lambda: UDPServer('', SOCKET_PORT).run())
socket_thread.start()

form_action = f'http://localhost:{SOCKET_PORT}'

httpd = socketserver.TCPServer(('localhost', HTTP_PORT), MyHandler)
print(f"Serving at port {HTTP_PORT}")
httpd.serve_forever()
