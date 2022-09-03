import psycopg2

con = psycopg2.connect(
  database="postgres", 
  user="postgres", 
  password="psqluser", 
  host="localhost", 
  port="5432"
)

cursor = con.cursor()

question = input("Уверен? Если да, отправь 8 ")
if question == '8':  
  cursor.execute("DELETE FROM access")
  con.commit()
  print("Почистил таблицу")

