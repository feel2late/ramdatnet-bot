from urllib import response
import requests
import urllib3
urllib3.disable_warnings()
import psycopg2


conn = psycopg2.connect(
  database="postgres", 
  user="postgres", 
  password="psqluser", 
  host="localhost", 
  port="5432"
)
cursor = conn.cursor()


result = requests.get(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/metrics/transfer', verify=False).json()
result = result.get('bytesTransferredByUserId')
for i in result:
    data = round(result.get(i)/1073741824, 3)
    cursor.execute("UPDATE access SET rdn1_data = %s WHERE rdn1_id = %s", (data, i))
    

result = requests.get(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/metrics/transfer', verify=False).json()
result = result.get('bytesTransferredByUserId')
for i in result:
    data = round(result.get(i)/1073741824, 3)
    cursor.execute("UPDATE access SET rdn2_data = %s WHERE rdn2_id = %s", (data, i))


result = requests.get(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/metrics/transfer', verify=False).json()
result = result.get('bytesTransferredByUserId')
for i in result:
    data = round(result.get(i)/1073741824, 3)
    cursor.execute("UPDATE access SET rdn3_data = %s WHERE rdn3_id = %s", (data, i))


conn.commit()
print("Готово")



