#!/usr/bin/python

from __future__ import print_function
import pexpect
import re


ports = ['5028', '5071', '5103', '5123', '5264', '5292', '5338', '5357', '5461', '5541', '5743', '5769', '5784', '5878', '5882', '5897', '5966', '6033', '6034', '6051', '6192', '6291', '6308', '6367', '6428', '6448', '6489', '6585', '6610', '6616', '6652', '6762', '6842', '6942', '6978', '7011', '7029', '7041', '7068', '7138', '7328', '7510', '7694', '7765', '7819', '7829', '7919', '7984', '7992', '8009', '8147', '8152', '8212', '8229', '8248', '8314', '8392', '8441', '8487', '8500', '8511', '8648', '8659', '8665', '8751', '8757', '8763', '8831', '8849', '8914', '8933', '8961', '8966', '9011', '9105', '9111', '9152', '9274', '9392', '9526', '9589', '9631', '9714', '9779', '9890', '9936', '9999']




def find_designated_port(skeleton_key, username, ports, fast=True):
    for i in ports:
        print("Testing username: " + username + " on port: " + str(i) + " STATUS:...", end="")
        child = pexpect.spawn("telnet 128.114.59.215 " + str(i), timeout=0.1)


        child.sendline(skeleton_key)
        # Try to send username after skeleton key
        # if port is broken or down, timeout is set to 5,
        # close child and move on
        try:
            child.expect("Username: ", timeout=0.1)
        except pexpect.exceptions.TIMEOUT:
            print("FAIL")
            child.close()
            continue


        # if skeleton_key accepted, 
        #  send username to the Username:
        child.sendline(username)

        try:
            index = child.expect(["Invalid user, goodbye.",])
            if index == 0:
                print("FAIL")
                child.close()
        except pexpect.exceptions.EOF:
            print("FAIL WITH EOF")
            child.close()
        except pexpect.exceptions.TIMEOUT:
            index = child.expect([re.compile(r"[a-zA-Z0-9]+"), pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT], timeout=0.1)
            if index == 0:
                print("SUCCESS")
                child.close()
                if fast:
                    return i
                else:
                    port = i
            else:
                print("MATCH BUT WITH ", end= '')
                if index == 1:
                    print("FAIL WITH EOF")
                    child.close()
                else:
                    print("FAIL WITH TIMEOUT")
                    child.close()

            print("FAIL WITH TIMEOUT")
            child.close()
    return port


def find_skeleton(port, fast=True):
    f = open("skeletonKeys.txt", "r")

    for line in f.readlines():
        print("Testing skeleton key: " + str(line).strip(' \t\r\n') + " STATUS:...",end='')
        child = pexpect.spawn("telnet 128.114.59.215 " + str(port), timeout=0.1)

        child.sendline(str(str(line).strip(' \t\r\n')))


        try:
            index = child.expect(re.compile(r"Connection"), timeout=0.1)
            print("FAIL")
            child.close()
        except pexpect.exceptions.EOF:
            print("FAIL WITH EOF")
            child.close()
        except pexpect.exceptions.TIMEOUT:
            index = child.expect([re.compile(r"[a-zA-Z0-9]+"), pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT], timeout=0.1)
            if index == 0:
                print("SUCCESS")
                child.close()
                if fast:
                    return str(line).strip(' \t\r\n')
                else:
                    key = str(line).strip(' \t\r\n')
            else:
                print("MATCH BUT WITH ", end= '')
                if index == 1:
                    print("FAIL WITH EOF")
                    child.close()
                else:
                    print("FAIL WITH TIMEOUT")
                    child.close()

            print("FAIL WITH TIMEOUT")
            child.close()

    return key


if __name__ == "__main__":
    key = find_skeleton(ports[0])
    my_port = find_designated_port(key, "dthurau", ports)
    print(my_port)
