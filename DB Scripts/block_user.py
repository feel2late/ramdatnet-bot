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

while True:
  choice_method = int(input('Блокируем по key_name(1) или user_telegram_id(2)? '))
  if choice_method == 1:
    key_name = input('Введите key_name: ')
    cursor.execute("SELECT rdn1_id, rdn2_id, rdn3_id, blocked FROM access WHERE key_name = %s", (key_name,))
    result = cursor.fetchone()
  elif choice_method == 2:
    user_telegram_id = int(input('Введите user_telegram_id: '))
    cursor.execute("SELECT rdn1_id, rdn2_id, rdn3_id, blocked FROM access WHERE user_telegram_id = %s", (user_telegram_id,))
    result = cursor.fetchone()

  choice = int(input('Выберите действие:\n1 - заблокировать\n2 - разблокировать\nВаш выбор: '))

  rdn1_id = result[0]
  rdn2_id = result[1]
  rdn3_id = result[2]

  if choice == 1:
    requests.put(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
    requests.put(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
    requests.put(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/access-keys/{rdn3_id}/data-limit', json={"limit": {"bytes": 1000000}}, verify=False)
    print(f'ID {rdn1_id}, {rdn2_id}, {rdn3_id} заблокированы')
  elif choice == 2:
    requests.delete(f'https://146.185.251.151:61236/07Tm1I9T_4ZU6pJmzGGCxQ/access-keys/{rdn1_id}/data-limit', verify=False)
    requests.delete(f'https://45.10.43.184:9615/ZQDD1CinJTLL1jP0x0xSSw/access-keys/{rdn2_id}/data-limit', verify=False)
    requests.delete(f'https://89.44.194.176:30514/Cd9H4wI8_x1y965YiJ2ZMg/access-keys/{rdn3_id}/data-limit', verify=False)
    print(f'ID {rdn1_id}, {rdn2_id}, {rdn3_id} разблокированы')
