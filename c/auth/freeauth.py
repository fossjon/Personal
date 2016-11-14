#!/usr/bin/python

import crypt
import hashlib
import hmac
import os
import random
import re
import smtplib
import sqlite3
import string
import sys
import time

def sqloexec(sqloobjc, sqlocomd):
	try:
		sqloobjc.execute(sqlocomd)
	except:
		pass

def cleanstr(inputstr):
	outpstri = ""
	charlist = (string.digits + string.uppercase + string.lowercase)
	for inputchr in inputstr:
		if (inputchr in charlist):
			outpstri += inputchr
	return outpstri

def pbkdfsha(s, p):
	i = 1; l = ((256 / 8) * 2); d = ""
	while (len(d) < l):
		c = 0; rounds = 4096; f = ""
		lasthmac = (s + chr((i >> 24) & 0xff) + chr((i >> 16) & 0xff) + chr((i >> 8) & 0xff) + chr((i >> 0) & 0xff))
		while (c < rounds):
			u = hmac.new(p, lasthmac, hashlib.sha1).digest()
			lasthmac = u
			t = ""
			for x in range(0, len(u)):
				if (x >= len(f)):
					f += chr(0)
				t += chr(ord(f[x]) ^ ord(u[x]))
			f = t
			c += 1
		for j in f:
			q = ""
			if (ord(j) < 0x10):
				q = "0"
			if (len(d) < l):
				h = hex(ord(j))
				d += (q + h[2:])
		i += 1
	return d

denystri = "Reject"
authstri = "Accept"

mailuser = ""
mailpass = ""

expstime = int(sys.argv[1])
username = cleanstr(sys.argv[2])
userpass = sys.argv[3]
usercode = ""
regxobjc = re.match("^(.*[^0-9])([0-9]+)$", userpass)
if (regxobjc):
	userpass = str(regxobjc.group(1))
	usercode = str(regxobjc.group(2))
usermail = [""]
mailcode = ""

sqloconn = sqlite3.connect("/opt/freeradius/freeauth.db")
sqlocurs = sqloconn.cursor()

sqloexec(sqlocurs, "CREATE TABLE server (user TEXT, pass TEXT);")
sqloexec(sqlocurs, "CREATE TABLE login (user TEXT, pass TEXT, mail TEXT);")
sqloexec(sqlocurs, "CREATE TABLE token (loginuser TEXT, code TEXT, time INTEGER, exps INTEGER);")

for sqlorowo in sqlocurs.execute("SELECT * FROM server;"):
	mailuser = str(sqlorowo[0])
	mailpass = str(sqlorowo[1])

authflag = 0
for sqlorowo in sqlocurs.execute("SELECT * FROM login WHERE user = '" + username + "';"):
	sqlohash = str(sqlorowo[1])
	sqlomail = str(sqlorowo[2])
	sqloinfo = sqlohash.split("$")
	if (sqloinfo[2] == pbkdfsha(sqloinfo[1], userpass)):
		authflag = 1
		usermail[0] = sqlomail

if (authflag != 1):
	sqloconn.commit()
	sqloconn.close()
	sys.stdout.write(denystri);sys.exit(1)

prestime = int(time.time())
sqlocurs.execute("DELETE FROM token WHERE loginuser = '" + username + "' AND (" + str(prestime) + " - time) >= exps;")

authflag = 0
timelist = []
for sqlorowo in sqlocurs.execute("SELECT * FROM token WHERE loginuser = '" + username + "';"):
	sqlocode = str(sqlorowo[1])
	sqlotime = int(sqlorowo[2])
	if (sqlocode == usercode):
		authflag = 1
	timelist.append(sqlotime)
timelist.sort()

if (authflag == 1):
	sqloconn.commit()
	sqloconn.close()
	sys.stdout.write(authstri);sys.exit(0)

sendcode = 0
if (len(timelist) >= 1):
	if ((prestime - timelist[-1]) >= 60):
		sendcode = 1
else:
	sendcode = 1

if (sendcode == 1):
	for x in range(0, 6):
		mailcode += str(random.randint(0, 9))
	sqlocurs.execute("INSERT INTO token VALUES ('" + username + "', '" + mailcode + "', " + str(prestime) + ", " + str(expstime) + ");")

if ((mailuser != "") and (mailpass != "") and (usermail[0] != "") and (mailcode != "")):
	mailmesg = "\r\n".join([
		"From: " + mailuser,
		"To: " + usermail[0],
		"Subject: Code = " + mailcode,
		"",
		"OTP Auth Delivery"
	])
	
	server = smtplib.SMTP("smtp.gmail.com:587")
	server.ehlo()
	server.starttls()
	server.login(mailuser, mailpass)
	server.sendmail(mailuser, usermail, mailmesg)
	server.quit()

sqloconn.commit()
sqloconn.close()
sys.stdout.write(denystri);sys.exit(1)
