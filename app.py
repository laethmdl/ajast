from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# إنشاء قاعدة بيانات وجدول للموظفين
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL,
            years_of_service INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# إضافة موظف جديد
@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    position = request.form['position']
    salary = float(request.form['salary'])
    years_of_service = int(request.form['years_of_service'])

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO employees (name, position, salary, years_of_service)
        VALUES (?, ?, ?, ?)
    ''', (name, position, salary, years_of_service))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# عرض قائمة الموظفين
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

# حساب العلاوات والترقيات
@app.route('/calculate_bonuses')
def calculate_bonuses():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()

    bonuses = []
    for emp in employees:
        emp_id, name, position, salary, years_of_service = emp
        bonus = 0

        # حساب العلاوة السنوية (5% من الراتب لكل 5 سنوات خدمة)
        if years_of_service >= 5:
            bonus += (salary * 0.05) * (years_of_service // 5)

        # الترقية إذا كانت سنوات الخدمة >= 10
        promotion = "نعم" if years_of_service >= 10 else "لا"

        bonuses.append({
            'name': name,
            'position': position,
            'salary': salary,
            'bonus': bonus,
            'promotion': promotion
        })

    conn.close()
    return render_template('bonuses.html', bonuses=bonuses)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)