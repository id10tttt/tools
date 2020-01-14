#!/usr/bin/env bash

#动态端口转发
#
#ssh -D port user@user-ip-address  可以用作sock5 proxy
#
#将服务器上面的端口，映射到本地
#
#ssh –L localhost:local-port:localhost:server-port user@user-ip-address
#
#
#
#将本地的服务，映射到服务器上公网是B，运行服务的机器A，本机C， 通过C主机访问A上面的服务
#
#先将本地[ A ]的服务，映射到服务器 [ B ]
#
#ssh –R localhost:B-port:localhost:A-port user@user-ip-address-B
#
#再在本地[ C ]上面映射服务器[ B ]的端口
#
#ssh –L localhost:C-port:localhost:B-port user@user-ip-address-B
#
#在主机 C 上面访问端口 C-port ，可以访问到 A-port 上面的应用

echo "User name"
read -r user_name

echo "Server IP: "
read -r ip_address

echo "Server port: "
read -r server_port

echo "Local port: "
read -r local_port

ssh -R localhost:"$server_port":localhost:"$local_port" "$user_name"@"$ip_address"
