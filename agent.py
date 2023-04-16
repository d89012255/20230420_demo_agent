
from random import randint
import random
import time
import socket
from socket import SHUT_RDWR
import os, binascii
import sys
import hashlib
import random
import string
import logging
from datetime import datetime

import hashlib 
import time


### first step -> opc ua server and opa ua client do authentication ###
### second step -> opa ua client connect to opc ua server to get data ###

FORMAT = '%(asctime)s$%(name)s$%(levelname)s$%(message)s'
DB_IP_static = "127.0.0.1" 
AS_IP_static = "127.0.0.1"
AGENT_IP_static = "127.0.0.1"
AGENT_NAME = "福裕五軸CNC加工機"
DB_NAME = "db"

def send_sendor_data():
    host_sensor = DB_IP_static
    port_sensor = 36242
    client_sensor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sensor.connect((host_sensor, port_sensor))
    now_time = (datetime.now()).strftime("%m_%d_%Y, %H:%M:%S")
    temperature = 13
    humidity = 23
    noise = 94
    data = "福裕五軸CNC加工機$"+str(now_time)+"$"+str(temperature)+"$"+str(humidity)+"$"+str(noise)
    client_sensor.sendall(data.encode())
    client_sensor.close()
def read_file():
    with open('cnc.txt','r',encoding='utf-8') as f:
        line = f.readlines()

    parameters = ""
    host = DB_IP_static
    #host = "192.168.3.242"
    port = 37878
    ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl.connect((host, port))
    for i in range(len(line)-1):
        parameters += str(line[i])

    ctrl.send(parameters.encode())
    ctrl.close()

################### Start Register ###################
print('part1 : Register')

################### DB connect to device ###################
#store IDs
print('DB has connected with device')
#host_ctrl = "192.168.50.214"
host_ctrl = AGENT_IP_static
port_ctrl = 30101
router_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router_ctrl.bind((host_ctrl, port_ctrl)) 
router_ctrl.listen(10)
while(True):

        hmac1_par1 = 0
        hmac1_par2 = 0

        connect_ctrl, address_ctrl = router_ctrl.accept()
        

        ctrl_msg = str(connect_ctrl.recv(1024), encoding = 'utf-8') #string,IDs = ip
        # 要檢查的檔案路徑
        filepath = "./cnc.txt"
        # 檢查檔案是否存在
        if os.path.isfile(filepath):
                os.remove(filepath)
        fp = open(filepath,'a',encoding='utf-8')
        db_ip = ctrl_msg
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+ctrl_msg+'$'+host_ctrl+'$'+str(port_ctrl)+'$socket connect$success.\n$')
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+ctrl_msg+'$'+host_ctrl+'$'+str(port_ctrl)+'$get communication key$success.\n$')

################### device connect to AS ###################
        #host_as = "192.168.3.133"
        host_as = AS_IP_static
        port_as = 33123
        print('device wants to connect with AS!')
        router_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        router_as.connect((host_as, port_as))
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+host_as+'$'+str(port_as)+'$socket connect$success.\n$')
        daynum1 = datetime.now()
        daynum1 = str(daynum1)
        
        print('device sends IDs to AS.') 
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+host_as+'$'+str(port_as)+'$send db ID to AS$finished.\n$')
        hmac1_par1 = ctrl_msg
        ctrl_msg = ctrl_msg+'~'+AGENT_NAME

        router_as.send(ctrl_msg.encode())
        print('device gets proof result from AS.\nIs that DB a legal equipment?')
        as_msg = str(router_as.recv(1024), encoding = 'utf-8')
        router_as.close()
        print(ctrl_msg)

        '''try:
                router_as.shutdown(socket.SHUT_RDWR)
        except(socket.error, OSError, ValueError):
                pass'''

        ks = AGENT_IP_static
        hmac1_par2 = ks
        #AS has proofed that DB is legal
        if as_msg == 'y':
                print('\033[92mYes ! That DB is legal !\033[0m')
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+host_as+'$'+host_ctrl+'$'+str(port_as)+'$get db identify result$legal.\n$')

                
                connect_ctrl.send(ks.encode())
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+db_ip+'$'+str(port_ctrl)+'$send device key$finished.\n$')

        else:
                print('\033[91mNo ! That DB is illegal !\033[0m')
                print('\033[5;31;47m We will send warning message to user.\033[0m')

                connect_ctrl.send(as_msg.encode())
                fp.close()
                host_warning = DB_IP_static
                warning_port = 36543

                warning_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                warning_as.connect((host_warning, warning_port))
                
                daynum = datetime.now()
                daynum = str(daynum)

                
                warning = daynum+'$'+db_ip+'$'+host_ctrl+'$'+str(port_ctrl)+'$'+'illegal device$1'

                warning_as.send(warning.encode())
                warning_as.close()

                as_email_host = AS_IP_static
                as_email_port = 31345

                email_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                email_as.connect((as_email_host, as_email_port))                
                daynum = datetime.now()
                daynum = str(daynum)
                             
                email = warning
                email_as.send(email.encode())
                email_as.close()


                continue
        #AS proof device
        ctrl_msg = str(connect_ctrl.recv(1024), encoding = 'utf-8') #string,IDs = ip
        if ctrl_msg == 'y':
                print("this device is legal")
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+db_ip+'$'+host_ctrl+'$'+str(port_ctrl)+'$get device identify result$success.\n$')
                
        else:
                print("this device is illegal")
                fp.close()
                continue

                
################### Part2 Permission ###################
        #host_as = "192.168.3.133"
        host_as = DB_IP_static
        port_as = 33127
        print('device wants to connect with AS!')
        router_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        router_as.connect((host_as, port_as))
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+host_as+'$'+str(port_as)+'$socket connect$success.\n$')
        daynum1 = datetime.now()
        daynum1 = str(daynum1)

        print('device sends IDs to AS.') 
        ctrl_msg = hmac1_par1+'~'+AGENT_NAME
        router_as.send(ctrl_msg.encode())
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+host_as+'$'+str(port_as)+'$ask as permission$success.\n$')
        print('device gets proof result from AS.\n')
        as_msg = str(router_as.recv(1024), encoding = 'utf-8')


        #ks = 'a1sdz2xcw3erg4rt'
        #AS has proofed that DB is legal
        if as_msg == 'y':

                print('\033[92mYes ! That DB is allow !\033[0m')
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+host_as+'$'+host_ctrl+'$'+str(port_as)+'$get permission result$legal.\n$')
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                
                connect_ctrl.send(as_msg.encode())
                fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+db_ip+'$'+str(port_ctrl)+'$send permission result$success.\n$')

        else:
                print('\033[91mNo ! That DB is not allow !\033[0m')
                print('\033[5;31;47m We will send warning message to user.\033[0m')

                fp.close()
                host_warning = DB_IP_static
                warning_port = 36543
                warning_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                warning_as.connect((host_warning, warning_port))
    
                daynum = datetime.now()
                daynum = str(daynum)
    
                warning = daynum+'$'+db_ip+'$'+host_ctrl+'$'+str(port_ctrl)+'$'+'illegal permission$2'
                warning_as.send(warning.encode())
                warning_as.close()

                as_email_host = AS_IP_static
                as_email_port = 31345

                email_as = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                email_as.connect((as_email_host, as_email_port))                
                daynum = datetime.now()
                daynum = str(daynum)
                             
                email = warning
                email_as.send(email.encode())
                email_as.close()
                
                connect_ctrl.send(as_msg.encode())
                continue

################### Start Authentication ###################
        print('part3 : Authentication')
#device gets HMAC1 data from DB
        HMAC1_1 = str(connect_ctrl.recv(1024), encoding = 'utf-8')
        time.sleep(0.00001)
        daynum = datetime.now()
        daynum = str(daynum)
        fp.write(daynum+'$root$INFO$'+db_ip+'$'+host_ctrl+'$'+str(port_ctrl)+'$get HMAC1$success.\n$')
        print('device gets HMAC1 from DB!')

        
        #Calculate HMAC1 to proof that DB is correct to be communicate
        HMAC1_2 = hmac1_par1+hmac1_par2+DB_NAME
        HMAC1_2 = hashlib.sha256(str(HMAC1_2).encode("utf-8")).hexdigest()
        print('HMAC1 from DB : ',HMAC1_1)
        print('HMAC1 from device : ',HMAC1_2)

        if HMAC1_2 == HMAC1_1:
                time.sleep(0.00001)
                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+db_ip+'$none$none$verified with HMAC1$legal device.\n$')
                #device sends HMAC2 to OPC UA Client
                para2 =hmac1_par2+ hmac1_par1 +AGENT_NAME
                print(para2)
                HMAC2 = hashlib.sha256(str(para2).encode("utf-8")).hexdigest()
                print(HMAC2)
                #print('HMAC2 data : ',HMAC2)
                #print('Handshake2(s to c) -> OPC UA Server sends HMAC2 to OPC UA Client!')
                time.sleep(0.00001)

                daynum = datetime.now()
                daynum = str(daynum)
                fp.write(daynum+'$root$INFO$'+host_ctrl+'$'+db_ip+'$'+str(port_ctrl)+'$send HMAC2$fnished.\n$')
                
                connect_ctrl.send(HMAC2.encode())
                #router_as.close()
        else:
                temp = 'n'

                

                #router_as.close()
                connect_ctrl.send(temp.encode())
                fp.close()
                continue
        HMAC2_result = str(connect_ctrl.recv(1024), encoding = 'utf-8')
        if(HMAC2_result=="data_please"):
               send_sendor_data()
               time.sleep(0.00001)

               daynum = datetime.now()
               daynum = str(daynum)
               fp.write(daynum+'$root$INFO$'+db_ip+'$'+host_ctrl+'$'+str(port_ctrl)+'$get HMAC2 compare result$success.\n$')

        fp.close()
        read_file()
        

        
