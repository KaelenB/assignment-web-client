#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get the IP address of the host
        address = socket.gethostbyname(self.host)
        
        self.socket.connect((address, self.port))

    def send_to_socket(self, message):
        # Connect to the socket
        self.connect()

        # Send the message
        self.socket.sendall(message)

        # Receive the response
        self.read_response()

        # Close the socket
        self.socket.close()

    def read_response(self):
        # Recieve response
        data = self.recvall()

        # Get the code and body from the response
        self.read_code(data)
        self.read_body(data)

    def read_code(self, data):
        # Get the code after the HTTP version
        match  = re.search(r"(?<=HTTP/[12]\.[01] )\d+", data)

        if match:
            self.code = int(match.group(0))
        else:
            self.code = 500
    
    def read_body(self, data):
        # Get all characters after the last \r\n\r\n
        match = re.search(r"(?<=\r\n\r\n).*", data, re.DOTALL)

        if match:
            self.body = match.group(0)
        else:
            self.body = ""

    def read_url(self, url):
        # Get host, optional port and optional path
        match = re.search(r"http://([^:/]+)(?::(\d+))?(/.*)?", url)

        if match:
            self.host = match.group(1)
            self.port = int(match.group(2)) if match.group(2) != None else 80
            self.path = match.group(3) or "/"
        # Invalid URL
        else:   
            exit()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def GET(self, url, args=None):
        self.read_url(url)
        message = f"GET /{self.path} HTTP/1.1\r\nHost: {self.host}\r\nAccept:*/*\r\nConnection:close\r\n\r\n".encode('utf-8')

        self.send_to_socket(message)

        return HTTPResponse(self.code, self.body)

    def POST(self, url, args=None):
        self.read_url(url)
        content = urllib.parse.urlencode(args) if args != None else ''
        message = f"POST /{self.path} HTTP/1.1\r\nHost: {self.host}\r\nAccept: */*\r\nContent-Length: {len(content)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{content}".encode('utf-8')

        self.send_to_socket(message)

        return HTTPResponse(self.code, self.body)

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
