#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Matthew Sheydwasser
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse
import json

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        """ 
        Gets a list containing host and port from url
        If url does not contain port, use default HTTP port 80

        Input: an address url
        Output: (host, port)
        """

        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port

        if not port:
            port = 80

        return [host, port]


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        """ 
        Parses the responses code given the response data

        Input: Response data
        Output: Response code
        """

        return int((self.get_headers(data)[0]).split(' ')[1])

    def get_headers(self,data):
        """ 
        Parses the responses headers given the response data

        Input: Response data
        Output: Response headers
        """

        return data.split('\r\n')[:-2]

    def get_body(self, data):
        """ 
        Parses the responses body given the response data

        Input: Response data
        Output: Response body
        """

        return data.split('\r\n')[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        """ 
        Creates a GET request to the given URL

        Input: URL
        Output: The servers response to our request
        """

        # get path, host, port, parsed from url
        parsed = urlparse(url)
        path = parsed.path
        host_port = self.get_host_port(url)
        
        # if not path supplied, use default
        if path == '':
            path = '/'

        # request being sent, setting path and host
        request = f"GET {path} HTTP/1.0\r\nHost: {host_port[0]}\r\n\r\n"
        
        # connect to host, send request, and recieve the response data
        self.connect(host_port[0], host_port[1])
        self.sendall(request)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)
        
        # shutdown socket and close connection
        self.socket.shutdown(socket.SHUT_WR)
        self.close()
    
        # return the response code and body from the server
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        """ 
        Creates a GET request to the given URL

        Input: URL
        Output: The servers response to our request
        """

        # get path, host, port, parsed from url
        parsed = urlparse(url)
        path = parsed.path
        host_port = self.get_host_port(url)
        
        # if not path supplied, use default
        if path == '':
            path = '/'

        # initialize parameters and length of body
        # Adjust parameters into proper format: 'name=John&occupation=deer+hunter'
        # replace '\r', '\n', ' ' characters for encoding
        params = ''
        length = 0
        if bool(args):
            for each in args:
                if len(params) != 0:
                    params+='&'
                params += each + '='
                value = (args[each]).replace('\r', '%0D').replace('\n', '%0A').replace(' ', '+')
                params += value
            length = len(params)
        

        # create request, setting path, host, content-type/length, and the body
        headers = f"POST {path} HTTP/1.0\r\nHost: {host_port[0]}\r\n"
        headers += f"Content-Type: application/x-www-form-urlencoded\r\n"
        headers += f"Content-Length: {length}\r\n\r\n"
        headers += f"{params}\r\n"
    
        # connect to host, send request, and recieve the response data
        self.connect(host_port[0], host_port[1])
        self.sendall(headers)
        data = self.recvall(self.socket)
        body = self.get_body(data)
        code = self.get_code(data)

        # shutdown socket and close connection
        self.socket.shutdown(socket.SHUT_WR)
        self.close()

        # return the response code and body from the server
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
