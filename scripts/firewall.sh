LAN="br-lan"
WAN="eth0.2"
SRV="192.168.161.2:22"
ROU="192.168.96.0/19:192.168.64.2 192.168.160.0/19:192.168.128.2"


C=`/usr/sbin/ebtables -L FORWARD | grep -i '.p ARP.*.j DROP'`
if [ "$C" == "" ] ; then
	echo "Setting ebtables"
	
	/usr/sbin/ebtables -F
	
	for INTF in -i -o ; do
		/usr/sbin/ebtables -A FORWARD "$INTF" "$LAN" -p ARP -j DROP
		
		for PORT in 67 68 ; do
			for TYPE in sport dport ; do
				/usr/sbin/ebtables -A FORWARD "$INTF" "$LAN" -p ip --ip-protocol udp --ip-"$TYPE" "$PORT" -j DROP
			done
		done
	done
fi


while read E ; do
	M=`echo "$E" | awk '{ print $2 }'`
	I=`echo "$E" | awk '{ print $3 }'`
	/usr/sbin/ip neighbor change "$I" lladdr "$M" dev "$LAN" nud permanent
done < /tmp/dhcp.leases


C=`/usr/sbin/iptables -nvL | grep -i '^chain' | tail -n +4`
if [ "$C" != "" ] ; then
	echo "Setting iptables"
	
	/usr/sbin/iptables -F ; /usr/sbin/iptables -X
	/usr/sbin/iptables -t nat -F ; /usr/sbin/iptables -t nat -X
	/usr/sbin/iptables -t mangle -F ; /usr/sbin/iptables -t mangle -X
	/usr/sbin/iptables -t raw -F ; /usr/sbin/iptables -t raw -X
	
	/usr/sbin/iptables -P INPUT ACCEPT
	/usr/sbin/iptables -A INPUT -i lo -j ACCEPT
	/usr/sbin/iptables -A INPUT -p udp --dport 67 -j ACCEPT
	/usr/sbin/iptables -A INPUT -p tcp --dport 22 -j ACCEPT
	/usr/sbin/iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
	/usr/sbin/iptables -A INPUT -j DROP
	
	/usr/sbin/iptables -P FORWARD ACCEPT
	/usr/sbin/iptables -P OUTPUT ACCEPT
	
	if [ "$WAN" != "" ] ; then
		if [ "$SRV" != "" ] ; then
			/usr/sbin/iptables -t nat -A PREROUTING -i "$WAN" -p tcp --dport 443 -j DNAT --to "$SRV"
		fi
		/usr/sbin/iptables -t nat -A POSTROUTING -o "$WAN" -j MASQUERADE
	fi
fi

for ROUTE in $ROU ; do
	SRC=`echo "$ROUTE" | awk -F':' '{ print $1 }'`
	DST=`echo "$ROUTE" | awk -F':' '{ print $2 }'`
	C=`/usr/sbin/ip route | grep -i "$SRC"`
	if [ "$C" == "" ] ; then
		echo "Adding route [$SRC] -> [$DST]"
		
		/usr/sbin/ip route add "$SRC" via "$DST"
	fi
done
