#!/usr/bin/env python3

from unittest import TestCase
import socket


def listToString(l):
    conv = []
    if (type(l) == 'tuple'):
        conv = list(l)
    else:
        conv = l
    return ",".join(list(map(lambda x: str(x), conv)))


class ServerTest(TestCase):
    def test_register(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("localhost",  9999))
        public_key = (295, 592, 301, 14, 28, 353, 120, 236)
        message = str(2000) + ',' + listToString(public_key)
        client.send(message.encode('ascii'))
        back = client.recv(1024).decode('ascii')
        self.assertEqual('CONNECTED WITH SERVER#2000', back)
        client.send('END'.encode('ascii'))
        client.close()
