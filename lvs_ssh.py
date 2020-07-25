from getpass import getpass
from tqdm import tqdm
import asyncio, asyncssh, socket,os
 
 
'''
 
PASTE THIS IN YOUR SCRIPT:
 
import sys
sys.path.append('..')
from lvs_ssh import start_ssh
 
'''
 
 
 
def TCP_connect(ip:str, port:int, delay:float):
#    print('Checking SSH port '+ip)
    TCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPsock.settimeout(delay)
    try:
        TCPsock.connect((ip,port))
        return ip
    except:
        print('Port {} closed on {}'.format(port,ip))
        return ''
 
 
async def sshing(ip:str,user:str,passwd:str,cmd:str,sem)->list:
    '''
    SSH to IP with USER and PASSWORD uses transform to give IP and MASK VLAN 50
    '''
    async with sem:
        try:
            async with asyncssh.connect(ip,username=user,password=passwd,known_hosts=None) as con:
                string = await con.run(cmd, check=True)
#           print ('Get result SSH of '+ip)
            return [ip,string.stdout]
        except:
            print ('-=WARNING=- Cant connect to device. PLEASE CHECK USERNAME,HOSTNAME,COMMAND '+ip)
            return [ip,'CANT_CONNECT']
 
async def ssh_gathering(ip_list:list, user:str, passwd:str, ssh_cmd:str)->list:
    '''
    Gather results of async SSHing.
    '''
    results=list()
    sem=asyncio.Semaphore(400)
    for ip in ip_list:
        task = asyncio.ensure_future(sshing(ip,user,passwd,ssh_cmd,sem))
        results.append(task)
    for future in tqdm(results, total=len(ip_list)):
        await future
    return await asyncio.gather(*results)
 
def start_ssh(cmd:str)->list:
    '''
    Starts gather info from IPs in inventory file via SSH.
    '''
    default_filename='inventory'
    user = input('Input user: ')
    passwd = getpass('Enter password: ')
    ip_file= input('Enter name of file with IP or leave it blank: ')
    if not os.path.exists(ip_file):
        print('-= No such file in directory takin {} =-'.format(default_filename))
        ip_file=default_filename
    with open(ip_file) as inv_file:
        ip_list=inv_file.read().split('\n')
    ip_list=[ip for ip in ip_list if ip.rstrip()!='']
    ip_list=[TCP_connect(ip,22,0.5) for ip in ip_list]
    ip_list=[i for i in ip_list if i!='']
    print ('Getting information from hosts via SSH - STARTED')
    results = asyncio.run(ssh_gathering(ip_list, user, passwd,cmd))
    print ('Getting information from hosts via SSH - DONE')
    return results