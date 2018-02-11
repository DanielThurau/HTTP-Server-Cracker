import pexpect
conn = pexpect.spawn("telnet 128.114.59.215 5123")
conn.sendline("passepartout")
