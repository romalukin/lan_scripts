import json
import os


def check_parameter(first:dict, last:dict, param: str)->dict:
    '''
    compares two dicts with parameter
    '''
    report = dict()
    limit = 300
    for hostname in last:
        temp = dict()
        temp_list = []
        for i in range(len(last[hostname])):
            try:
                if last[hostname][i][param] != first[hostname][i][param]:
                    dif = last[hostname][i][param] - first[hostname][i][param]
                    if abs(dif) > limit and dif > 0:
                        interface = last[hostname][i]['interface']
                        temp[interface] = '{} -> {} (difference {})'.format(first[hostname][i][param], last[hostname][i][param], dif)
                    elif abs(dif) > limit and dif < 0:
                        interface = last[hostname][i]['interface']
                        temp[interface] = 'interface has been cleared, {} -> {} (difference {})'.format(first[hostname][i][param], last[hostname][i][param], abs(dif))
            except KeyError:
                print('need more information about {}'.format(hostname))
            except IndexError:
                print('количество хостов не совпадает {} != {}')
        temp_list.append(temp)
        report[hostname] = temp_list
    report = {key: report[key] for key in report if report[key] != [{}]}
    return report

def overall(result:dict, err_list:list, error:str):
    '''
    prints report
    '''
    if len(err_list) == 0:
        print('Нет информации по ', error)
        return
    if error == 'CRC':
        print('Ошибки CRC - следует проверить патчкорд')
    elif error == 'collisions':
        print('Коллизии - следует проверить режим дуплекса')
    elif error == 'input errors':
        print('input errors')
    elif error == 'output errors':
        print('output errors')
    i = 1
    for num in err_list:
        for hostname in result[error]:
            for intf in result[error][hostname]:
                for line in intf:
                    if num == int(intf[line].split()[-1].rstrip(')')):
                        print('{:2}. {:20} {} {}'.format(i, hostname, line, intf[line]))
                        i += 1

info = []
result = dict()
check = ['input errors', 'CRC', 'output errors', 'collisions' ]
path = '/usr/local/lvs_python/get_port_info_log'

if os.path.exists(path):                                       #looking for json files and get first and last file to compare
    check_files = [f for f in os.listdir(path) if f.startswith('port_info')]
    check_files = sorted(check_files)
    del check_files[1:len(check_files)-1]
for file_log in check_files:
    file_log = '/usr/local/lvs_python/get_port_info_log/{}'.format(file_log)
    with open(file_log, 'r') as f:
        info.append(json.load(f))
first, last = info
for line in check:                                             #call function check_parameter for errors we want to check
    result[line] = dict()
    result[line].update(check_parameter(first, last, line))
crc = []                                                       #getting errors result to sort them for overall
collisions = []
input_err = []
output_err = []
for problem in result:
    for hostname in result[problem]:
        for intf in result[problem][hostname]:
            for line in intf:
                if problem == 'CRC':
                    crc.append(intf[line])
                if problem == 'collisions':
                    collisions.append(intf[line])
                if problem == 'input errors':
                    input_err.append(intf[line])
                if problem == 'output errors':
                    output_err.append(intf[line])
crc = sorted([int(line.split()[-1].rstrip(')')) for line in crc], reverse = True)
collisions = sorted([int(line.split()[-1].rstrip(')')) for line in collisions], reverse = True)
input_err = sorted([int(line.split()[-1].rstrip(')')) for line in input_err], reverse = True)
output_err = sorted([int(line.split()[-1].rstrip(')')) for line in output_err], reverse = True)
print('Период времени c {} по {}'.format(check_files[0].split('_')[2].split('.')[0], check_files[1].split('_')[2].split('.')[0]))
overall(result, crc, 'CRC')                                    #call function overall to print report
overall(result, collisions, 'collisions')
overall(result, input_err, 'input errors')
overall(result, output_err, 'output errors')