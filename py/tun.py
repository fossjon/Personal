#!/usr/bin/python

import os, sys
import ctypes, fcntl, struct
import select, socket, subprocess
import time, random, hashlib

def tclose(sobj):
	try:
		sobj.close()
	except:
		pass

def ksa4(k):
	s = []
	for i in range(0, 256):
		s.append(i)
	j = 0
	l = len(k)
	for i in range(0, 256):
		j = ((j + s[i] + ord(k[i % l])) % 256)
		t = s[i]; s[i] = s[j]; s[j] = t
	return (s, 0, 0)

def arc4(m, k):
	(s, i, j) = k
	l = len(m)
	o = ""
	for x in range(0, l):
		i = ((i + 1) % 256)
		j = ((j + s[i]) % 256)
		t = s[i]; s[i] = s[j]; s[j] = t
		c = s[(s[i] + s[j]) % 256]
		o += chr(ord(m[x]) ^ c)
	k = (s, i, j)
	return (o, k)

def set4(n, k):
	if (n == ""):
		n = (str(time.time()) + ":" + str(random.random()) + "-")
	s = ksa4(n + "s" + k)
	r = ksa4(n + "r" + k)
	(null, s) = arc4("x"*4096, s)
	(null, r) = arc4("x"*4096, r)
	return (n, s, r)

def client(h, p, n, k):
	f = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	f.connect((h, p))
	(enc, k) = arc4(n, k)
	f.send(n + enc)
	return (f, k)

# initialize some common variables
BUFFER_SIZE = 2000
PR_MODE = "client"
PR_HOST = "1.2.3.4"
PR_PORT = 31337
PR_SKEY = "key"
OS_TYPE = sys.platform
IF_CMD = ["/sbin/ifconfig", "tun0", "10.0.0.1", "10.0.0.2", "up"]

# process command line args usage: tun.py mode:[-c,-s] ip:[0.0.0.0] port:[4321] secret:[key]
if (sys.argv[1] == "-s"):
	PR_MODE = "server"
PR_HOST = sys.argv[2]
PR_PORT = int(sys.argv[3])
PR_SKEY = sys.argv[4]

# initialize the clients secret key state
last = 0
(nonce, skey, rkey) = set4("", PR_SKEY)

# define the remote connection socket descriptors - tcp client or tcp server
srv_fd = None
net_fd = None
if (PR_MODE == "client"):
	tmp = IF_CMD[2]
	IF_CMD[2] = IF_CMD[3]
	IF_CMD[3] = tmp
	(net_fd, skey) = client(PR_HOST, PR_PORT, nonce, skey)
else:
	srv_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	srv_fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	srv_fd.bind(("0.0.0.0", PR_PORT))
	srv_fd.listen(1)

# determine how to bring up the tun0 interface - mac or linux
if (OS_TYPE == "darwin"):
	tun_fd = os.open("/dev/tun0", os.O_RDWR)
else:
	TUNSETIFF = 0x400454ca
	IFF_TUN = 0x0001
	IFF_TAP = 0x0002
	IFF_NO_PI = 0x1000
	
	tun_fd = os.open("/dev/net/tun", os.O_RDWR)
	ifr = struct.pack("16sH", "tun0", IFF_TUN | IFF_NO_PI)
	fcntl.ioctl(tun_fd, TUNSETIFF, ifr)
	
	IF_CMD.insert(3, "pointopoint")
subprocess.call(IF_CMD)

# main processing loop for network traffic tunneling
conns = []
while (1):
	#print("loop")
	
	# set the list of available socket descriptors to listen for
	fd_list = [tun_fd]
	if (srv_fd):
		fd_list.append(srv_fd)
	if (net_fd):
		fd_list.append(net_fd)
	for conn in conns:
		fd_list.append(conn)
	
	# select the available fds ready for reading
	rd = select.select(fd_list, [], [])
	
	# loop through each socket now to process each action
	for ready_fd in rd[0]:
		# if we are reading from our tun device then encrypt the message and write it to the network socket
		if (ready_fd == tun_fd):
			packet = os.read(tun_fd, BUFFER_SIZE)
			plen = len(packet)
			if ((plen > 0) and (net_fd)):
				(enc, skey) = arc4(packet, skey)
				smac = str(skey)
				hmac = hashlib.sha256(smac + enc + smac).digest()
				net_fd.send(enc + hmac)
		
		# if the server gets a new client connection then add it to a list to be authenticated next
		if (ready_fd == srv_fd):
			(conn, addr) = srv_fd.accept()
			print("[conn]:new",conn,addr)
			conns.append(conn)
		
		# if we get a network message decrypted and authenticated then write it to our tunnel device
		if (ready_fd == net_fd):
			data = net_fd.recv(BUFFER_SIZE)
			dlen = len(data)
			if (dlen > 0):
				try:
					temp = data[:-32]
					(dec, tkey) = arc4(temp, rkey)
					tmac = str(tkey)
					hmac = hashlib.sha256(tmac + temp + tmac).digest()
					if (hmac == data[-32:]):
						rkey = tkey
						os.write(tun_fd, dec)
					else:
						print("[hmac]:fail",hmac,data[-32:])
				except:
					dlen = 0
			if (dlen < 1):
				tclose(net_fd)
				net_fd = None
		
		# loop through any unauthenticated clients who have sent us data
		tmps = []
		conl = (len(conns) - 1)
		while (conl > -1):
			conn = conns[conl]
			
			# if the connection is ready
			if (ready_fd == conn):
				data = conn.recv(BUFFER_SIZE)
				dlen = len(data)
				indx = data.find("-")
				
				# if they sent us some actual data
				if ((dlen > 0) and (indx > -1)):
					# try to decrypt the nonce and verify an increase in the time
					try:
						temp = float(data.split(":")[0])
					except:
						temp = 0
					(tnonce, trkey, tskey) = set4(data[:indx+1], PR_SKEY)
					(dec, trkey) = arc4(data[indx+1:], trkey)
					
					# if the auth succeeds then setup the new key state and set the new client socket
					if ((temp > last) and (tnonce == dec)):
						print("[auth]:good",conn)
						
						nonce = tnonce
						skey = tskey
						rkey = trkey
						
						tclose(net_fd)
						net_fd = conn
						
						last = temp
						conns[conl] = None
					else:
						dlen = 0
				else:
					dlen = 0
				
				# if the auth failed then remove the client now
				if (dlen < 1):
					print("[auth]:fail",conns[conl])
					tclose(conns[conl])
					conns[conl] = None
			
			if (conns[conl]):
				tmps.append(conns[conl])
			conl -= 1
		
		conns = tmps[:]
