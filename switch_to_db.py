import psycopg2
import sys
sys.path.append('..')
from contextlib import closing
from lvs_ssh_v2 import start_ssh


def switch_to_db(ip:str, sh_ver:str, sh_boot:str):
    sh_ver = sh_ver.split('\n')
    sh_boot = sh_boot.split('\n')
    key_find_hostname = False
    model_list = []
    serial_list = []
    firmware_list = []
    for line in sh_ver:
        #Get the model name from 'sh ver'
        if line.startswith('Model number') or line.startswith('Model Number'):
            model = line.split()[-1]
            model_list.append(model)
        #Get the serial number from 'sh_ver'
        if line.startswith('System serial number') or line.startswith('System serial number'):
            serial = line.split()[-1]
            serial_list.append(serial)
        #Get hostname from 'sh ver'
        if 'uptime' in line and key_find_hostname == False:
            hostname = line.split()[0]
            key_find_hostname = True
    for line in sh_boot:
        if line.startswith('BOOT'):
            firmware = line.split(':')[-1]
            firmware_list.append(firmware)
    conn = psycopg2.connect(dbname='roma_db', user='rlukinskiy', password='invisF1rst')
    with conn:
        with conn.cursor() as cursor:
            for i in range(len(model_list)):
                cursor.execute("INSERT INTO switch (ip_address, hostname, model, serial_number, firmware) VALUES ('{}', '{}', '{}', '{}', '{}')".format(ip ,hostname , model_list[i], serial_list[i], firmware_list[i]))
                print("INSERT INTO switch (ip_address, hostname, model, serial_number, firmware) VALUES ('{}', '{}', '{}', '{}', '{}')".format(ip ,hostname , model_list[i], serial_list[i], firmware_list[i]))
    return

sh_ver = start_ssh(['show ver', 'show boot'])
for line in sh_ver:
    switch_to_db(line[0], line[1][0], line[1][1])