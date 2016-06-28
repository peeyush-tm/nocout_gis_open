#!/bin/sh

KILL=0

MACHINE_NAME=$(echo $1)
IP_ADDRESS=$(echo $2)
DEVICE_TYPE=$(echo $3)
ENV_NAME=$(echo $4)
#BS_IP=$(echo $5)
#MAC_ADDR=$(echo $6)

#echo $MACHINE_NAME, $IP_ADDRESS, $DEVICE_TYPE, $ENV_NAME
rm /omd/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt

#Make TESTING=1 if You want to access on UAT
#Make TESTING=0 if You want to access on Production
TESTING=-1

if [[ "$ENV_NAME" = "omd" ]]; then
	TESTING=1
elif [[ "$ENV_NAME" = "apps" ]]; then
	TESTING=0
else
	echo "Wrong Location"
	KILL=1
fi

#echo $ENV_NAME,$TESTING

USERNAME=`cat /$ENV_NAME/nocout/nocout/nocout/performance/script/idpass.txt | grep $DEVICE_TYPE | awk '{print $2}'`
PASSWORD=`cat /$ENV_NAME/nocout/nocout/nocout/performance/script/idpass.txt | grep $DEVICE_TYPE | awk '{print $3}'`

if [[ "$USERNAME" = "" || "$PASSWORD" = "" ]]; then
	echo "Username or Password not found!!!"
	KILL=1
fi


if [[ $TESTING -eq 0 ]]; then
	case "$MACHINE_NAME" in
		"ospf1") SERVER="tmadmin@115.114.79.37"
			;;
		"ospf2") SERVER="tmadmin@115.114.79.38"
			;;
		"ospf3") SERVER="tmadmin@115.114.79.39"
			;;
		"ospf4") SERVER="tmadmin@115.114.79.40"
			;;
		"ospf5") SERVER="tmadmin@115.114.79.41"
			;;
		"pub") SERVER="tmadmin@115.114.85.173"
		    ;;
		"vrfprv") SERVER="tmadmin@10.206.30.15"
			;;
		*) echo "Invalid Machine: $MACHINE_NAME"
			KILL=1
			;;
	esac
elif [[ $TESTING -eq 1 ]]; then
	case "$MACHINE_NAME" in
		"ospf1" | "ospf2" | "ospf3" | "ospf4" | "ospf5" | "pub" | "vrfprv") SERVER="tmadmin@10.133.19.165"
			;;
		*) echo "Invalid Machine: $MACHINE_NAME"
			KILL=1
			;;
	esac
else
	echo "Wrong Environment selected"
	KILL=1
fi

#echo $SERVER,$USERNAME,$PASSWORD

if [[ $KILL -eq 1 ]]
then
	break;
else
	case "$DEVICE_TYPE" in
		"StarmaxSS") TELNET="{
 					        echo $USERNAME
 					        echo $PASSWORD
 					        echo copy r s
 					        echo reboot
 					        sleep 20 
 					} | telnet $IP_ADDRESS"
 					ssh -p 5522 $SERVER -t -t "$TELNET" > /$ENV_NAME/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt 2>&1
 							;;
		"CanopySM100SS" | "CanopyPM100SS") TELNET="{
 									echo $USERNAME
 									echo $PASSWORD
 									echo reset
 									echo exit
 									sleep 20
							} | telnet $IP_ADDRESS"
							ssh -p 5522 $SERVER -t -t "$TELNET" > /$ENV_NAME/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt 2>&1
 									;;
		"Radwin2KBS" | "Radwin2KSS") TELNET="{
								echo $USERNAME
								echo $PASSWORD
								echo reboot
								echo exit
								sleep 20
							} | telnet $IP_ADDRESS"
							ssh -p 5522 $SERVER -t -t "$TELNET" > /$ENV_NAME/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt 2>&1
									;;
		*) echo "Wrong Device Type: $DEVICE_TYPE"
				;;
	esac
fi


PING="ping $IP_ADDRESS -c 1 | grep "100%""
if [[ `cat /$ENV_NAME/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt | grep -E 'Telsima_ss|Telnet+|admin@'` ]]; then
	echo yes
elif [[ `cat /$ENV_NAME/nocout/nocout/nocout/performance/script/out-$IP_ADDRESS.txt | grep "Login"` ]]; then
	echo no
elif [[ `ssh -p 5522 $SERVER -t -t "$PING"` ]]; then
	echo nr
fi
