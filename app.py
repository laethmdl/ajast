from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import sqlite3
import pdfkit

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# إعداد Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نموذج المستخدم
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# إنشاء قاعدة بيانات
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# تحميل المستخدم
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            user_obj = User(user[0])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة!')
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# الصفحة الرئيسية
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

# إضافة موظف جديد
@app.route('/add_employee', methods=['POST'])
@login_required
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
    flash('تم إضافة الموظف بنجاح!')
    return redirect(url_for('index'))

# حساب العلاوات والترقيات
@app.route('/calculate_bonuses')
@login_required
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

# توليد تقرير PDF
@app.route('/generate_report')
@login_required
def generate_report():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    conn.close()

    html_content = render_template('reports.html', employees=employees)
    pdf = pdfkit.from_string(html_content, False)
    return pdf, 200, {'Content-Type': 'application/pdf'}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)