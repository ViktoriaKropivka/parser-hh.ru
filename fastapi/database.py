import time
import mysql.connector
from backend import get_links, get_vacancy


def connect_to_db():
    conn = mysql.connector.connect(
        host='db',
        user='root',
        password='password',
        database='vacancies',
    )
    return conn


def create_table(table_name: str):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            sql = f""" 
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT PRIMARY KEY, 
                title VARCHAR(255), 
                salary VARCHAR(255), 
                experience VARCHAR(255), 
                company VARCHAR(255), 
                tags TEXT, 
                url TEXT 
            ) """
            cursor.execute(sql)
        conn.commit()
        print(f"Таблица {table_name} создана")
    except mysql.connector.Error as err:
        print(f"Ошибка подключения к bd: {err}")
    finally:
        conn.close()


def pars_vacancies(criteria: str, table_name: str):
    create_table(table_name)
    data = {}
    for a in get_links(criteria):
        data[a] = get_vacancy(a)
        vac = data[a]
        vac.insert(0, len(data))

        if len(vac) != 7:
            print("Error")
            continue

        time.sleep(1)
        print(f"Добавляем данные в таблицу {table_name}")

        conn = connect_to_db()
        try:
            with conn.cursor() as cursor:
                sql = f"INSERT INTO `{table_name}` VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, tuple(vac))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка подключения к bd: {err}")
        finally:
            conn.close()
        print('sql')
    print("ALL")
    return