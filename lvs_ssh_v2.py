import netdev,time,asyncio,socket,os
from tqdm import tqdm
from getpass import getpass


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


async def sshing(ip:str,user:str,passwd:str,cmd_list:list,sem)->list:
    '''
    SSH to IP with USER and PASSWORD uses transform to give IP and MASK VLAN 50
    '''
    async with sem:
        try:
            async with netdev.create(host=ip,device_type='cisco_ios',username=user,password=passwd) as ios:
                result =[await ios.send_command(cmd, strip_command=True) for cmd in cmd_list]
            return [ip,result]
        except:
            print ('-=WARNING=- Cant connect to device. PLEASE CHECK USERNAME,HOSTNAME,COMMAND '+ip)
            return [ip,'CANT_CONNECT']

async def ssh_gathering(ip_list:list, user:str, passwd:str, ssh_cmd:list)->list:
    '''
    Gather results of async SSHing.
    '''
    sem=asyncio.Semaphore(50)
    coroutines = [sshing(ip,user,passwd,ssh_cmd,sem) for ip in ip_list]
    tasks= [asyncio.create_task(coroutine) for coroutine in coroutines]
    for future in tqdm(tasks, total=len(ip_list)):
        await future
    results = [await task for task in tasks]
    #results =await asyncio.wait(tasks)
    return results

def start_ssh(cmd_list:list)->list:
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
    ip_list=[TCP_connect(ip,22,0.7) for ip in ip_list]
    ip_list=[i for i in ip_list if i!='']
    print ('Getting information from hosts via SSH - STARTED')
    results = asyncio.run(ssh_gathering(ip_list, user, passwd,cmd_list))
    print ('Getting information from hosts via SSH - DONE')
    return results
