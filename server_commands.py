import requests
import urllib3
urllib3.disable_warnings()

def set_limit(rdn1_id, rdn2_id):
    requests.put(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
    requests.put(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)

def delete_limit(rdn1_id, rdn2_id):
    requests.delete(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', verify=False)
    requests.delete(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', verify=False)
