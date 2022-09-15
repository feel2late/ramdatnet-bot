from time import strftime
from typing import Type
from unittest import result
from webbrowser import get
from datetime import timedelta, datetime
import psycopg2


conn = psycopg2.connect(
  database="postgres", 
  user="postgres", 
  password="psqluser", 
  host="localhost", 
  port="5432"
)
cursor = conn.cursor()


def register(user_telegram_id: int, id: int, user_name: str, telegram_username: str, connection_date, shutdown_date, tariff):
    """Добавляем пользователя в БД"""
    cursor.execute('UPDATE access SET user_telegram_id = %s, user_name = %s, telegram_username = %s, connection_date = %s, shutdown_date = %s, tariff = %s WHERE id = %s', (user_telegram_id, user_name, telegram_username, connection_date, shutdown_date, tariff, id))
    conn.commit()


def launched_bot(user_id, current_time):
    cursor.execute("INSERT INTO users (user_telegram_id, joining_date) VALUES (%s, %s) ON CONFLICT (user_telegram_id) DO NOTHING", (user_id, current_time))
    conn.commit()


def get_key(user_telegram_id: int, server: str):
    """Получаем ключи конкретного пользователя по user.id"""
    user_telegram_id = str(user_telegram_id)
    cursor.execute(f"SELECT {server} FROM access WHERE user_telegram_id = %s", (user_telegram_id,))
    return cursor.fetchone()[0]

def is_registered(user_id):
    """Проверяем, зарегистрирован ли пользователь"""
    
    cursor.execute("SELECT key_name FROM access where user_telegram_id = %s", (user_id,))    
    if cursor.fetchone():
        return True
    else:
        return False

def get_first_free_id():
    """Получаем первый свободный id (без пользователя)"""

    cursor.execute("SELECT id FROM access where user_telegram_id IS NULL ORDER BY id")    
    return cursor.fetchone()

def get_joining_date(user_id):
    """Получаем дату регистрации пользователя"""

    cursor.execute("SELECT connection_date FROM access where user_telegram_id = %s", (user_id,))
    return cursor.fetchone()[0]

def when_to_pay(user_id):
    """Возвращает дату следующей оплаты"""
    cursor.execute("SELECT shutdown_date FROM access where user_telegram_id = %s", (user_id,))
    try:
        result = cursor.fetchone()[0]
        
        if not result == 'not_need_to_pay':
            date = result
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            date = date.strftime("%H:%M %d.%m.%Y")
            return date
        else:
            return False
    except TypeError:
        pass    
    

def get_registered_users():
    """Возвращает список зарегистрированных пользователей"""

    cursor.execute("SELECT id, user_telegram_id, user_name, shutdown_date, key_name FROM access WHERE user_telegram_id IS NOT NULL ORDER BY id")
    result = cursor.fetchall()
    message = ''

    for i in range(len(result)):
        message += str(result[i]) + '\n'

    return message

def shutdown_date():
    """Возвращает список айдишников и даты следующей оплаты"""

    cursor.execute("SELECT key_name, shutdown_date FROM access WHERE shutdown_date IS NOT NULL ORDER BY shutdown_date DESC")
    result = cursor.fetchall()
    string = ''
    
    for i in range(len(result)):
        string += str(result[i]) + '\n'
    return string

def get_ids_who_to_pay_soon():
    """Возвращает telegram_id клиентов, у кого до оплаты меньше суток"""

    cursor.execute("SELECT user_telegram_id, shutdown_date FROM access WHERE shutdown_date IS NOT NULL AND shutdown_date NOT IN ('not_need_to_pay') ORDER BY shutdown_date DESC")
    result = cursor.fetchall()
    users = []
    now = datetime.now().replace(microsecond=0)
    future = now + timedelta(days=1)

    for i in range(len(result)):
        if now < datetime.strptime(result[i][1], "%Y-%m-%d %H:%M:%S") < future:
            users.append(result[i][0])
        
    return users

def add_days(id):
    """Добавляет 30 дней к пользованию сервисом"""
    
    cursor.execute("SELECT shutdown_date FROM access where user_telegram_id = %s", (id,))
    try:
        shutdown_date = cursor.fetchone()[0]
    except TypeError:
        message = 'Я вас не узнаю. Вы зарегистрировались, прежде чем оплачивать?'
        return message
    shutdown_date = datetime.strptime(shutdown_date, "%Y-%m-%d %H:%M:%S")
    now = datetime.now().replace(microsecond=0)

    if shutdown_date > now:
        days_left = shutdown_date - now
        day_of_payment = datetime.now().replace(microsecond=0)
        shutdown_date = (now + days_left + timedelta(days=31)).replace(hour=23, minute=59, second=59, microsecond=0)
        
    else:   
        day_of_payment = datetime.now().replace(microsecond=0)
        shutdown_date = day_of_payment.replace(hour=23, minute=59, second=59, microsecond=0) + timedelta(days=31)

    cursor.execute('UPDATE access SET payment_recieved = %s, shutdown_date = %s WHERE user_telegram_id = %s', (day_of_payment, shutdown_date, id))
    conn.commit()

def get_free_keys():
    """Возвращает количество свободных ключей"""

    cursor.execute("SELECT key_name FROM access WHERE telegram_username IS NULL")
    result = cursor.fetchall()
    return len(result)

def was_a_payment(user_id):
    cursor.execute("SELECT payment_recieved FROM access WHERE user_telegram_id = %s", (user_id,))
    result = cursor.fetchone()[0]
    if result == None:
        return False
    else:
        return True

def get_rdn_id_from_user(user_id):
    cursor.execute("SELECT rdn1_id FROM access WHERE user_telegram_id = %s", (user_id,))
    rdn1_id = cursor.fetchone()[0]
    cursor.execute("SELECT rdn2_id FROM access WHERE user_telegram_id = %s", (user_id,))
    rdn2_id = cursor.fetchone()[0]
    cursor.execute("SELECT rdn3_id FROM access WHERE user_telegram_id = %s", (user_id,))
    rdn3_id = cursor.fetchone()[0]
    return rdn1_id, rdn2_id, rdn3_id

def ban():
    """Возвращает telegram_id клиентов, у кого закончился оплаченный период"""

    cursor.execute("SELECT user_telegram_id, shutdown_date FROM access WHERE shutdown_date IS NOT NULL AND shutdown_date NOT IN ('not_need_to_pay') ORDER BY shutdown_date DESC")
    result = cursor.fetchall()
    users = []
    yesterday = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0) - timedelta(days=1)

    for i in range(len(result)):
        if datetime.strptime(result[i][1], "%Y-%m-%d %H:%M:%S") == yesterday:
            users.append(result[i][0])       
    return users

def add_check(user_id, bill_id):
    cursor.execute("INSERT INTO check_paid (user_id, bill_id) VALUES (%s, %s)", (user_id, bill_id))
    conn.commit()

def get_check(bill_id):
    cursor.execute("SELECT * FROM check_paid WHERE bill_id = %s", (bill_id,))
    result = cursor.fetchmany(1)
    if not bool(len(result)):
        return False
    else:
        return result[0]

def delete_check(bill_id):
    return cursor.execute("DELETE FROM check_paid WHERE bill_id = %s", (bill_id,))


def get_tariff(user_id):
    cursor.execute("SELECT tariff FROM access WHERE user_telegram_id = %s", (user_id,))
    tariff = cursor.fetchone()[0]
    return tariff 


def update_flag_blocked(user_id, flag):
    cursor.execute("UPDATE access SET blocked = %s WHERE user_telegram_id = %s", (flag, user_id))
    conn.commit()

def set_tariff(user_id):
    cursor.execute("UPDATE access SET tariff = 200 WHERE user_telegram_id = %s", (user_id,))
    conn.commit()

def get_active_users():
    """Возвращает telegram_id активных клиентов"""

    cursor.execute("SELECT user_telegram_id FROM access WHERE payment_recieved IS NOT NULL OR shutdown_date = 'not_need_to_pay'")
    result = cursor.fetchall()
    users = []
    for i in range(len(result)):
        users.append(result[i][0])
    return users