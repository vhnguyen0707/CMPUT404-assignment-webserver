#  coding: utf-8 
import os
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        request = self.data.decode("utf-8").split(' ')
        try:
            method = request[0]
            path = request[1] 
            http_version = request[2][:8].strip()       # get http version
            other_methods = ["OPTIONS", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT"]        # all methods defined in rfc266 other than GET

            if method == "GET":
                relative_path = "./www" + os.path.normpath(request[1])      #normalize case of pathname
                if http_version == 'HTTP/1.1' and "Host" not in self.data.decode():
                    self.request.sendall(bytearray(f"{http_version} 400 Bad Request\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n", 'utf-8'))

                elif os.path.isdir(relative_path):
                    # when path is an existing directory
                    if path[-1] == '/':
                        try:
                            f = open(f'{relative_path}/index.html', 'r')
                            content = f.read()
                            content_length = len(content)
                            response = f'{http_version} 200 OK\r\nContent-Type: text/html\r\nContent-Length: {content_length}\r\n\r\n{content}'
                            self.request.sendall(bytearray(response, 'utf-8'))
                        except:
                            # error reading file occured
                            self.request.sendall(bytearray(f"{http_version} 500 Internal Server Error\r\n", 'utf-8'))

                    else: 
                        self.request.sendall(bytearray(f'{http_version} 301 Moved Permanently\r\nContent-Type: text/html\r\nConnection:Close\r\nLocation: {path}/\r\n\r\n', 'utf-8'))    
                
                elif os.path.isfile(relative_path):
                    # when path is an existing file
                    try:
                        f = open(f'{relative_path}', 'r')
                        content = f.read()
                        content_length = len(content)
                        content_type = path[path.rfind('.') + 1:len(path)]      # get file extension 
                        response = f'{http_version} 200 OK\r\nContent-Type: text/{content_type}\r\nContent-Length: {content_length}\r\n\r\n{content}'
                        self.request.sendall(bytearray(response, 'utf-8'))
                    except:
                        # error reading file occured
                        self.request.sendall(bytearray(f"{http_version} 500 Internal Server Error\r\n", 'utf-8'))
                else:
                    # not a valid path
                    self.request.sendall(bytearray(f'{http_version} 404 Not Found\r\nContent-Type: text/html\r\nConnection:Close\r\n\r\n', 'utf-8'))


            elif method in other_methods:
                self.request.sendall(bytearray(f"{http_version} 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n", 'utf-8'))
            else: 
                self.request.sendall(bytearray(f"{http_version} 400 Bad Request\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n", 'utf-8'))
        
        except IndexError:
            pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
