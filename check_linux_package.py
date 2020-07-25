###Checks presence of package on system
 
import subprocess
 
def get_platform_packages():
    '''Gets the pakcage name and version depending on the Linux distribution'''
 
    try:
        result = subprocess.run(['dpkg', '-l'], stdout=subprocess.PIPE)
        dist = 'debian'
    except:
        result = subprocess.run(['rpm', '-qa'], stdout=subprocess.PIPE)
        dist = 'rhel'
 
    if dist == 'debian':
        name_version = []
        result = result.stdout.decode('utf-8')
        result = result.split('\n')
        for line in result:
            if line.startswith('i'):
                name_version.append('{}-{}'.format(line.split()[1], line.split()[2]))
    elif dist == 'rhel':
        result = result.stdout.decode('utf-8')
        name_version = result.split('\n')
 
    return name_version
 
if __name__ == '__main__':
    packages = get_platform_packages()
    pack = input('Enter package name: ')
    for line in packages:
        if pack in line:
            print(line)
            break
    else:
        print("Can't find this package.")