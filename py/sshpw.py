#!/usr/bin/python
# Usage: ./sshpw.py <password> ssh user@host date
# Description: This is a demo SSH auto password login script via a pseudo tty device (stolen from sshpass - not recommended obviously!)
# Note: This is a rough example script which assumes you have already accepted the fingerprint & have the right password

import os, sys, time

import glob, struct, termios, fcntl, pty

from ctypes import *

try:
	libc = cdll.LoadLibrary(glob.glob("/lib/*-linux-gnu/libc-*.so")[0])
except:
	libc = cdll.LoadLibrary(glob.glob("/usr/lib/libc.dylib")[0])

(master, slave) = pty.openpty()
#fcntl.fcntl(master, fcntl.F_SETFL, os.O_NONBLOCK)

libc.ptsname.restype = c_char_p
name = libc.ptsname(c_int(master))
slavept = -10

ourtty = os.open("/dev/tty", 0)

s = struct.pack("HHHH", 0, 0, 0, 0)
t = fcntl.ioctl(ourtty, termios.TIOCGWINSZ, s)
fcntl.ioctl(master, termios.TIOCSWINSZ, t)

pidn = os.fork()

if (pidn == 0):
	os.setsid()
	slavept = os.open(name, os.O_RDWR)
	os.close(slavept)
	os.close(master)
	os.execvp(sys.argv[2], sys.argv[2:])
	os._exit(0)

else:
	slavept = os.open(name, os.O_RDWR | os.O_NOCTTY)
	print("["+os.read(master, 128)+"]")
	os.write(master, sys.argv[1] + "\r\n")
	print("["+os.read(master, 8)+"]")
	os.wait()
