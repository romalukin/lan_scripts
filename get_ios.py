import sys
from lvs_ssh import start_ssh

def get_ios(sh_ver):
    '''
    Get IOS from switches
    '''
    sh_ver = sh_ver.split('\r\n')
    sh_ver = [i for i in sh_ver if i.rstrip()!='']
    image = 'ios: error'
    model = 'model: error'
    for line in sh_ver:
        #Get the model name
        if line.startswith('Model number'):
            model = line.split()[-1]
        #Get the ios name from 'sh ver'
        if 'System image' in line:
            image = line.split()[-1].split(':')[-1].rstrip('"')
    if image[0] == '/':
        image = image.replace('/', '')
    return model, image

result = []
result_s = []
ssh_res = start_ssh('sh ver')
result = [get_ios(i[1]) for i in ssh_res]
result = sorted(list(set(result)))
for line in result:
    result_s.append('{:25} {}\n'.format(line[0], line[1]))
with open('ios', 'w') as f:
    f.writelines(result_s)
print(result)
