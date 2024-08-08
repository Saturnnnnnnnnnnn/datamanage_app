import mysql.connector
from config import Config
from datetime import datetime

def create_connection():
    """
    Создает и возвращает соединение с базой данных MySQL.

    Returns:
        mysql.connector.connection.MySQLConnection: Соединение с базой данных.
    """
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    return conn

def create_table():
    """
    Создает таблицу `requests`, если она не существует.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # SQL запрос для создания таблицы
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        data TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        completed_at DATETIME
    )
    '''
    
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def add_request(data):
    """
    Добавляет новую заявку в таблицу `requests`.

    Args:
        data (str): Данные заявки.
    """
    conn = create_connection()
    cursor = conn.cursor()
    created_at = datetime.now()
    
    # SQL запрос для добавления новой заявки
    insert_query = "INSERT INTO requests (data, created_at) VALUES (%s, %s)"
    cursor.execute(insert_query, (data, created_at))
    
    conn.commit()
    conn.close()

def fetch_requests():
    """
    Извлекает все заявки из таблицы `requests`.

    Returns:
        list: Список всех заявок.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # SQL запрос для получения всех заявок
    select_query = "SELECT id, data, created_at, completed_at FROM requests"
    cursor.execute(select_query)
    requests = cursor.fetchall()
    
    conn.close()
    return requests

def update_request(request_id, new_data):
    """
    Обновляет данные конкретной заявки.

    Args:
        request_id (int): ID заявки, которую нужно обновить.
        new_data (str): Новые данные заявки.

    Returns:
        bool: True, если обновление прошло успешно, иначе False.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # SQL запрос для обновления данных заявки
    update_query = "UPDATE requests SET data = %s WHERE id = %s"
    cursor.execute(update_query, (new_data, request_id))
    
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    
    return updated > 0

def complete_request(request_id):
    """
    Помечает заявку как выполненную.

    Args:
        request_id (int): ID заявки, которую нужно пометить как выполненную.

    Returns:
        bool: True, если пометка прошла успешно, иначе False.
    """
    conn = create_connection()
    cursor = conn.cursor()
    completed_at = datetime.now()
    
    # SQL запрос для пометки заявки как выполненной
    complete_query = "UPDATE requests SET completed_at = %s WHERE id = %s"
    cursor.execute(complete_query, (completed_at, request_id))
    
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    
    return updated > 0

def remove_request(request_id):
    """
    Удаляет заявку из таблицы `requests`.

    Args:
        request_id (int): ID заявки, которую нужно удалить.

    Returns:
        bool: True, если удаление прошло успешно, иначе False.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # SQL запрос для удаления заявки
    delete_query = "DELETE FROM requests WHERE id = %s"
    cursor.execute(delete_query, (request_id,))
    
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    return deleted > 0

def fetch_completed_requests():
    """
    Извлекает все выполненные заявки из таблицы `requests`.

    Returns:
        list: Список выполненных заявок.
    """
    conn = create_connection()
    cursor = conn.cursor()
    
    # SQL запрос для получения выполненных заявок
    select_query = "SELECT id, data, created_at, completed_at FROM requests WHERE completed_at IS NOT NULL"
    cursor.execute(select_query)
    requests = cursor.fetchall()
    
    conn.close()
    return requests
