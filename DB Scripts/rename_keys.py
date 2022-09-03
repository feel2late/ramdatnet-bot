from urllib import response
import requests
import urllib3
urllib3.disable_warnings()
import data


num = 1000
for i in range(1012, 1353):
    name = 'user' + str(num)
    result = requests.put(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{i}/name', json={"name": f"{name}"}, verify=False)
    num += 1
    print('RDN1:', i, '/ 1352')

num = 1000
for i in range(1012, 1353):
    name = 'user' + str(num)
    result = requests.put(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{i}/name', json={"name": f"{name}"}, verify=False)
    num += 1
    print('RDN2:', i, '/ 1352')

num = 1000
for i in range(1005, 1347):
    name = 'user' + str(num)
    result = requests.put(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/access-keys/{i}/name', json={"name": f"{name}"}, verify=False)
    num += 1
    print('RDN3:', i, '/ 1346')

print(result.status_code)


