#!/usr/bin/env python

# Note: This is a work in progress and doesn't actually do what's on the tin yet.

import re

from hashlib import md5
from socket import socket, AF_INET, SOCK_STREAM

HOST = "64.31.63.226"
PORT = 28022

USERNAME = ""
PASSWORD = ""

class FrozenSynapse():
    def __init__(self, host, port, username, password):
        self.terminator = "\n"

        self.s = socket(AF_INET, SOCK_STREAM)

        self.s.connect((host, port))

        self.send("textcom\tprelogon\n")

        data = self.recv_end(self.s)

        matches = re.search(r"saltRec\t(\d+)", data)

        if not matches:
            self.s.close()

        print "Salt request", matches.group(1)

        password = md5(matches.group(1) + md5(password).hexdigest().upper()).hexdigest().upper()

        self.send("textcom\tlogin\t%s\t%s\t29\n" % (username, password))

        RECEIVING_FILE = False

        while True:
            data = self.recv_end(self.s)

            if RECEIVING_FILE:
                # XXX: No idea what format this is in.
                f = open('output.gz', 'wb')

                f.write(data + "\x00")

                f.close()

                RECEIVING_FILE = False

            if "writefile" in data:
                print "Got a writefile..."

                self.terminator = "\x00"

                RECEIVING_FILE = True

            print 'Received', repr(data)

        self.s.close()

    def recv_end(self, s):
        total_data = []

        while True:
            data = s.recv(1)

            if self.terminator in data:
                total_data.append(data[:data.find(self.terminator)])

                break

            total_data.append(data)

            if len(total_data) > 1:
                last_pair = total_data[-2] + total_data[-1]

                if self.terminator in last_pair:
                    total_data[-2] = last_pair[:last_pair.find(self.terminator)]
                    total_data.pop()

                    break

        return ''.join(total_data)

    def send(self, data):
        print "Sending", repr(data)

        self.s.sendall(data)

f = FrozenSynapse(HOST, PORT, USERNAME, PASSWORD)
