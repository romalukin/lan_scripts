'''
Gathers hostnames and port info, prints all information and
writes it in json file with actual time of running programm
'''
import sys
import time
import json
from tabulate import tabulate
sys.path.append('..')
from lvs_ssh_v2 import start_ssh
from pprint import pprint

def get_ip_host(switch_conf:dict)->dict:
    '''
    Gathers ip and hostname from switch_conf dict
    '''
    ip_host = dict()
    for key in switch_conf:
        ip_host[switch_conf[key]['ip']] = key
    return ip_host

def get_port_info(ip:str, sh_int:str)->dict:
    '''
    Gathers port info: name of interface, interface description,
    last input time, last output time, quantity of packets input,
    quantity of input errors, quantity of CRC, quantity of packets
    output, quantity of output errors, quantity of collsiions.
    Returns list of dicts
    '''
    exclude_words = ['Vlan', 'Port-channel', 'Loopback']
    port_list = []
    result_list = []
    result_dict = dict()
    sh_int = sh_int.split('\n')
    #sh_int = [i.rstrip().lstrip() for i in sh_int if i.rstrip()!='']
    #pprint(sh_int)
    for line in sh_int:
        if 'line protocol' in line:
            port = dict()
            port_name = line.split()[0]
            port['interface'] = port_name
            port['description'] = ' '                               #empty description, because some interfaces doesn't have it
        if 'Description' in line:
            port['description'] = line.split()[1]
        if 'Last input' in line:
            port['last input'] = line.split()[2].rstrip(',')
            port['last output'] = line.split()[4].rstrip(',')
        if 'packets input' in line:
            port['packets input'] = int(line.split()[0])
        if 'input errors' in line:
            port['input errors'] = int(line.split()[0])
            port['CRC'] = int(line.split()[3])
        if 'packets output' in line:
            port['packets output'] = int(line.split()[0])
        if 'output errors' in line:
            port['output errors'] = int(line.split()[0])
            port['collisions'] = int(line.split()[3])
            port_list.append(port)
    result_list = port_list.copy()                                  #make a copy for remove lines with exclude_words
    for line in port_list:
        for word in exclude_words:
            if  word in line['interface']:
                result_list.remove(line)
    result_dict[ip] = result_list
    return result_dict

port_info = []
host_port = dict()
sh_int_file = start_ssh(['show run', 'show cdp neigh', 'show int', 'show ver'])                                   #gathering command 'sh_int' output (list(ip, string))
for line in sh_int_file:
    port_info.append(get_port_info(line[0], line[1][2]))               #list of dicts [{ip: [{},{},{}...]}, {ip: [{},{},{}...]} ]
with open('/usr/local/lvs_python/switch_conf.log', 'r') as f:       #file with all information about swithces, I need only 'ip' and 'hostname'
    conf_dict = json.load(f)
ip_host = get_ip_host(conf_dict)
for line in port_info:
    for key_p in line:
        for key in ip_host:
            if key_p == key:
                host_port[ip_host[key]] = line[key_p]               #Serch the ip in ip_host and if it same as ip in port_info make a new dict {hostname: [{},{},{},{}], ...}
timestr = time.strftime('%Y%m%d-%H%M')
with open('get_port_info_log/port_info_{}.json'.format(timestr), 'w') as f:
    json.dump(host_port, f)
for key in host_port:
    print(key)
    print(tabulate(host_port[key], headers = 'keys', tablefmt = 'pipe'))