import sys
sys.path.append('..')
from lvs_ssh_v2 import start_ssh
from pprint import pprint

def check_ios(ios_list, sh_ver):
    '''
    Compare  the image from 'sh ver' and actual image from cisco.com
    '''
    sh_ver = sh_ver.split('\n')
    sh_ver = [i.rstrip().lstrip() for i in sh_ver if i.rstrip()!='']
    image = 'ios: error'
    model = 'model: error'
    hostname = 'hostname: error'
    key_find_model = False
    key_find_hostname = False
    key_find_image = False
    for line in sh_ver:
        #Get the model name from 'sh ver'
        if line.startswith('Model number') or line.startswith('Model Number') and key_find_model == False:
            model = line.split()[-1]
            key_find_model = True
        #Get hostname from 'sh ver'
        if 'uptime' in line and key_find_hostname == False:
            hostname = line.split()[0]
            key_find_hostname = True
        #Get the ios name from 'sh ver'
        if 'System image' in line and key_find_image == False:
            image = line.split()[-1].split(':')[-1].rstrip('"').replace('/', '')
            key_find_image = True
    #Compare
    for line in ios_list:
        if line.startswith(model):
            if line.split()[-1] == image:
                print('{:60} - {:19} {:20} {}'. format('OK', hostname, model, image))
                return 'OK'
            elif line.split()[-1] != image:
                print('NEED UPGRADE to version {:36} - {:19} {:20} {}'.format(line.split()[-1], hostname, model, image))
                return 'NU'
    else:
        print('no information about model {:33} {} {}'.format(model, hostname, image))
        return 'NI'

if __name__ == '__main__':
    result = []
    counter = {'OK' : 0,
               'NU' : 0,
               'NI' : 0}
    #Get 'sh ver' output from cisco switches
    ssh_res=start_ssh(['show run','show cdp neigh','show int','sh ver'])
    #Read 'ios' file and make 'model-ios' list
    with open('ios', 'r') as f:
        f = f.read().split('\n')
    for i in ssh_res:
        result.append(check_ios(f, i[1][3]))
    for i in result:
        counter[i] += 1
    print('OK: {}, NEED UPGRADE: {}, NO INFORMATION: {}'.format(counter['OK'], counter['NU'], counter['NI']))