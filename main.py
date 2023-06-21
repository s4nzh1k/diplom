import os
from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from flask_session import Session
import mysql.connector

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Конфигурация подключения к базе данных MySQL
db = mysql.connector.connect(
    host="localhost",
    user="vadim",
    password="",
    database="vchmapplications"
)

@app.route('/')
def index():
    if 'name' in session:
        name = session['name']
        return render_template('index.html', name=name) 
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    password = request.form['pahssword']

    cursor = db.cursor()

    # Проверка существования аккаунта в базе данных
    query = "SELECT COUNT(*) FROM users WHERE name = %s AND password = %s"
    data = (name, password)
    cursor.execute(query, data)
    result = cursor.fetchone()

    # Проверка, является ли аккаунт администратором
    admin_query = "SELECT COUNT(*) FROM users WHERE name = 'administrator' AND password = 'admin1324'"
    cursor.execute(admin_query)
    admin_result = cursor.fetchone()

    if result[0] == 1:
        if admin_result[0] == 1:
            # Если аккаунт администратора, установите сессию и перенаправьте на административную страницу
            session['name'] = name
            return redirect('/admin')
        else:
            # Если аккаунт не администратора, установите сессию и перенаправьте на главную страницу
            session['name'] = name
            return redirect('/')
    else:
        # Если аккаунт не существует или не является администратором, выведите соответствующую ошибку
        error_message = "Неверное имя пользователя или пароль. Если у вас нет аккаунта, зарегистрируйтесь."
        return render_template('/', error_message=error_message)
    
@app.route('/logout')
def logout():
    # Завершение сессии и перенаправление на главную страницу
    session.pop('name', None)
    return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    second_name = request.form['second_name']
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor()

    # Вставка данных в таблицу users
    user_query = "INSERT INTO users (name, second_name, email, password) VALUES (%s, %s, %s, %s)"
    user_data = (name, second_name, email, password)
    cursor.execute(user_query, user_data)

    # Применение изменений в базе данных
    db.commit()

    return redirect('/')

@app.route('/admin')
def admin():
    # Проверка, авторизован ли пользователь под учетной записью администратора
    if 'name' in session and session['name'] == 'administrator':
        cursor = db.cursor()

        # Получение данных из таблицы applications
        cursor.execute("SELECT * FROM applications")
        applications = cursor.fetchall()

        return render_template('admin.html', applications=applications)
    else:
        return redirect('/')

@app.route('/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_application(application_id):
    if request.method == 'GET':
        cursor = db.cursor()

        # Получение данных конкретной заявки
        cursor.execute("SELECT * FROM applications WHERE id = %s", (application_id,))
        application = cursor.fetchone()

        return render_template('edit_application.html', application=application)
    elif request.method == 'POST':
        # Получите данные из формы редактирования заявки
        applicant = request.form['applicant']
        room = request.form['room']
        date = request.form['date']
        priority = request.form['priority']
        desired_date = request.form['desired_date']
        subject = request.form['subject']
        description = request.form['description']
        status = request.form['status']

        cursor = db.cursor()

        # Обновление данных в таблице applications
        update_query = "UPDATE applications SET applicant = %s, room = %s, date = %s, priority = %s, desired_date = %s, subject = %s, description = %s, status = %s WHERE id = %s"
        update_data = (applicant, room, date, priority, desired_date, subject, description, status, application_id)
        cursor.execute(update_query, update_data)

        # Применение изменений в базе данных
        db.commit()

        return redirect('/admin')

@app.route('/submit_application', methods=['POST'])
def submit_application():
    if request.method == 'POST':
        # Получите данные из формы заявки
        applicant = request.form['applicant']
        room = request.form['room']
        date = request.form['date']
        priority = request.form['priority']
        desired_date = request.form['desired_date']
        subject = request.form['subject']
        description = request.form['description']

        # Определение соответствующих русских значений приоритета
        priority_mapping = {
            'low': 'низкий',
            'medium': 'средний',
            'high': 'высокий'
        }

        # Замена английского значения приоритета на русское значение
        priority_ru = priority_mapping.get(priority, '')

        cursor = db.cursor()

        # Вставка данных в таблицу applications
        application_query = "INSERT INTO applications (applicant, room, date, priority, desired_date, subject, description, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        application_data = (applicant, room, date, priority_ru, desired_date, subject, description, 'На рассмотрении')
        cursor.execute(application_query, application_data)

        # Применение изменений в базе данных
        db.commit()

        flash('Заявка успешно отправлена', 'success')
        return redirect('/')

@app.route('/my_applications')
def my_applications():
    if 'name' in session:
        name = session['name']
        user_applications = get_user_applications(name)
        return render_template('my_applications.html', name=name, user_applications=user_applications)
    else:
        return redirect('/')

def get_user_applications(name):
    # Функция для получения заявок пользователя из базы данных
    cursor = db.cursor()

    # Получение данных заявок пользователя
    cursor.execute("SELECT * FROM applications WHERE applicant LIKE %s", (name + '%',))
    user_applications = cursor.fetchall()

    return user_applications

if __name__ == '__main__':
    app.run(debug=True)