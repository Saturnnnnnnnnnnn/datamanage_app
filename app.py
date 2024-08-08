from flask import Flask, render_template, request, flash, session, redirect, url_for
from datetime import datetime
from mysql.connector import connect
from config import Config
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Секретный ключ для флэш сообщений

# Устанавливаем уровень логирования для Flask и Werkzeug
app.logger.setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def create_connection():
    """
    Создает и возвращает соединение с базой данных MySQL.
    """
    return connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

def create_table():
    """
    Создает таблицу `requests`, если она не существует.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                completed_at DATETIME
            )
        ''')
        conn.commit()

def add_request(data):
    """
    Добавляет новую заявку в таблицу `requests`.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        created_at = datetime.now()
        cursor.execute("INSERT INTO requests (data, created_at) VALUES (%s, %s)", (data, created_at))
        conn.commit()

def fetch_requests():
    """
    Извлекает все заявки из таблицы `requests`.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, data, created_at, completed_at FROM requests")
        requests = cursor.fetchall()
    return requests

def update_request(request_id, new_data):
    """
    Обновляет данные конкретной заявки.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE requests SET data = %s WHERE id = %s", (new_data, request_id))
        conn.commit()
    return cursor.rowcount > 0

def complete_request(request_id):
    """
    Помечает заявку как выполненную.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        completed_at = datetime.now()
        cursor.execute("UPDATE requests SET completed_at = %s WHERE id = %s", (completed_at, request_id))
        conn.commit()
    return cursor.rowcount > 0

def remove_request(request_id):
    """
    Удаляет заявку из таблицы `requests`.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM requests WHERE id = %s", (request_id,))
        conn.commit()
    return cursor.rowcount > 0

def fetch_completed_requests():
    """
    Извлекает все выполненные заявки из таблицы `requests`.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, data, created_at, completed_at FROM requests WHERE completed_at IS NOT NULL")
        requests = cursor.fetchall()
    return requests

def calculate_average_completion_time():
    """
    Расчитывает среднее время выполнения заявок в минутах.
    """
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TIMESTAMPDIFF(MINUTE, created_at, completed_at) as duration FROM requests WHERE completed_at IS NOT NULL")
        durations = cursor.fetchall()
    
    if not durations:
        return "Нет завершенных заявок"
    
    total_duration = sum(duration[0] for duration in durations)  # duration[0] так как duration - это кортеж
    average_duration = total_duration / len(durations)
    return f"{average_duration:.2f} минут"

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'add' in request.form:
            data = request.form['data']
            add_request(data)
            flash('Заявка добавлена успешно!', 'success')

        elif 'update' in request.form:
            request_id = request.form['update_id']
            new_data = request.form['new_data']
            if update_request(request_id, new_data):
                flash('Заявка обновлена успешно!', 'success')
            else:
                flash('Ошибка обновления заявки.', 'error')

        elif 'delete' in request.form:
            request_id = request.form['delete_id']
            if remove_request(request_id):
                flash('Заявка удалена успешно!', 'success')
            else:
                flash('Ошибка удаления заявки.', 'error')

        elif 'complete' in request.form:
            request_id = request.form['complete_id']
            if complete_request(request_id):
                flash('Заявка завершена успешно!', 'success')
            else:
                flash('Ошибка завершения заявки.', 'error')

        elif 'show_requests' in request.form:
            session['show_requests'] = True

        elif 'average_time' in request.form:
            session['show_avg_time'] = True

        elif 'hide_requests' in request.form:
            session.pop('show_requests', None)

        elif 'hide_avg_time' in request.form:
            session.pop('show_avg_time', None)

        return redirect(url_for('home'))

    # Получение значений состояния из сессии
    show_requests = session.get('show_requests', False)
    show_avg_time = session.get('show_avg_time', False)
    requests_html = ""
    average_time_message = ""

    if show_requests:
        requests = fetch_requests()
        requests_html = "<br>".join(
            f"Заявка {req[0]}: {req[1]} (Создана: {req[2]}, Завершена: {req[3]})"
            for req in requests
        )

    if show_avg_time:
        average_time_message = f"Среднее время выполнения заявки: {calculate_average_completion_time()}"

    return render_template(
        'index.html',
        show_requests=show_requests,
        show_avg_time=show_avg_time,
        requests=requests_html,
        average_time_message=average_time_message
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
