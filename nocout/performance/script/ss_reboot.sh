#!/bin/bash

#Make TESTING=1 if You want to access on UAT
#Make TESTING=0 if You want to access on Production
TESTING=1

KILL=0

MACHINE_NAME=$(echo $1)
IP_ADDRESS=$(echo $2)
DEVICE_TYPE=$(echo $3)

if [[ $TESTING -eq 0 ]]; then
	case "$MACHINE_NAME" in
		"ospf1") SERVER="115.114.79.37"
			;;
		"ospf2") SERVER="115.114.79.38"
			;;
		"ospf3") SERVER="115.114.79.39"
			;;
		"ospf4") SERVER="115.114.79.40"
			;;
		"ospf5") SERVER="115.114.79.41"
			;;
		"pub") SERVER="115.114.85.173"
		        ;;
		"vrfprv") SERVER="10.206.30.15"
			;;
		*) echo "Invalid Machine: $MACHINE_NAME"
			KILL=1
			;;
	esac
elif [[ $TESTING -eq 1 ]]; then
	case "$MACHINE_NAME" in
		"ospf1" | "ospf2" | "ospf3" | "ospf4" | "ospf5" | "pub" | "vrfprv") SERVER="10.133.19.165"
			;;
		*) echo "Invalid Machine: $MACHINE_NAME"
			KILL=1
			;;
	esac
else
	echo "Wrong Environment selected"
	KILL=1
fi


if [[ $KILL -eq 1 ]]; then
	break;
else
	case "$DEVICE_TYPE" in
		"StarmaxSS") TELNET="{
						        echo admin
						        echo admin
						        echo copy rs
						        echo reboot
						        echo exit
						        sleep 2
							} | telnet $IP_ADDRESS"
					ssh -p 5522 $SERVER -t "$TELNET"
							;;

		"CanopySM100SS" | "CanopyPM100SS") TELNET="{
												        echo admin
												        echo admin
												        echo reset
												        echo exit
												        sleep 2
													} | telnet $IP_ADDRESS"
											ssh -p 5522 $SERVER -t "$TELNET"	
																;;

		"Radwin2KBS" | "Radwin2KSS") TELNET="{
										        echo admin
										        echo admin
										        echo reboot
										        echo exit
										        sleep 2
											} | telnet $IP_ADDRESS"
									ssh -p 5522 $SERVER -t "$TELNET"
											;;
		*) echo "Wrong Device Type: $DEVICE_TYPE"
				;;
	esac
fi