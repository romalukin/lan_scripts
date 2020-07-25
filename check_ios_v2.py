import sys
sys.path.append('..')
from lvs_ssh_v2 import start_ssh


def standart_ios()->list:
    with open('/usr/local/lvs_python/ios', 'r') as f:
        f = f.read().split('\n')
    return f

def check_ios(ios_list: list, hostname: str, model: str, ios: str)->str:
    '''
    Compare  the image from 'sh ver' and actual image from cisco.com
    '''
    for line in ios_list:
        if line.startswith(model):
            if ios in line:
                print('{:60} - {:19} {:20} {}'. format('OK', hostname, model, ios))
                return 'OK'
            else:
                print('Следует обновить до версии {:36} - {:19} {:20} {}'.format(line.split()[-1], hostname, model, ios))
                return 'NU'
        else:
            print('Нет информации по модели {:33} {} {}'.format(model, hostname, image))
            return 'NI'




    result = []
    counter = {'OK' : 0,
               'NU' : 0,
               'NI' : 0}


    for i in ssh_res:
        result.append(check_ios(f, i[1][3]))
    for i in result:
        counter[i] += 1
    print('OK: {}, НАДО ОБНОВИТЬ: {}, НЕТ ИНФОРМАЦИИ ПО МОДЕЛЯМ: {}'.format(counter['OK'], counter['NU'], counter['NI']))