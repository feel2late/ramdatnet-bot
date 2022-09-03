from urllib import response
import requests
import urllib3
urllib3.disable_warnings()
import data


'''for i in range(1, 336):
    result = requests.put(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/access-keys/{i}/name', json={"name": f"{data2.rdn2[i-1]['name']}"}, verify=False)
print(result.status_code)'''


for i in range(1000):
    requests.post(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/access-keys/', verify=False)
    requests.post(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/', verify=False)
    requests.post(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/', verify=False)
    print(i,'/ 1000')
