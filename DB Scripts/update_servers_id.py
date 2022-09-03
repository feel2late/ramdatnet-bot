from data import rdn1, rdn2, rdn3
import psycopg2

con = psycopg2.connect(
  database="postgres", 
  user="postgres", 
  password="psqluser", 
  host="localhost", 
  port="5432"
)
cursor = con.cursor()

try:
    for i in range(len(rdn1)):    
        key_name = rdn1[i]['name']
        rdn_accessUrl = rdn1[i]['accessUrl']
        rdn_id = rdn1[i]['id']
        cursor.execute("INSERT INTO access (key_name, rdn1, rdn1_id) VALUES (%s, %s, %s) ON CONFLICT (key_name) DO NOTHING", (key_name, rdn_accessUrl, rdn_id))
        con.commit()
        print(f'В RDN1 добавлен {key_name}. {i} / {len(rdn1)}')
except Exception as exc:
    print('Ошибка добавления RDN1:', exc)

try:
    for i in range(len(rdn2)):    
        key_name = rdn2[i]['name']
        rdn_accessUrl = rdn2[i]['accessUrl']
        rdn_id = rdn2[i]['id']
        cursor.execute("UPDATE access SET rdn2 = %s, rdn2_id = %s WHERE key_name = %s", (rdn_accessUrl, rdn_id, key_name))
        con.commit()
        print(f'В RDN2 добавлен {key_name}. {i} / {len(rdn2)}')
except Exception as exc:
    print('Ошибка добавления RDN2:', exc)

try:
    for i in range(len(rdn3)):    
        key_name = rdn3[i]['name']
        rdn_accessUrl = rdn3[i]['accessUrl']
        rdn_id = rdn3[i]['id']
        cursor.execute("UPDATE access SET rdn3 = %s, rdn3_id = %s WHERE key_name = %s", (rdn_accessUrl, rdn_id, key_name))
        con.commit()
        print(f'В RDN3 добавлен {key_name}. {i} / {len(rdn3)}')
except Exception as exc:
    print('Ошибка добавления RDN3:', exc)    
