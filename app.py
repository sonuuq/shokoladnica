from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # нужен для session

BOOKINGS_FILE = 'bookings.json'
USERS_FILE = 'users.json'

def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_bookings(data):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# создаём users.json если нет
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

bookings = load_bookings()

@app.route('/')
def home():
    if 'user' in session:
        if session['user'] == 'admin@shoko.com':
            return redirect('/admin')
        return redirect('/booking')
    return render_template('welcome.html')  # новая страница выбора

@app.route('/booking')
def booking():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html', user=session['user'])


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/confirmation')
def confirmation():
    if 'user' not in session:
        return redirect('/login')
    name = request.args.get('name')
    date = request.args.get('date')
    time = request.args.get('time')
    guests = request.args.get('guests')
    table = request.args.get('table')
    return render_template('confirmation.html', name=name, date=date, time=time, guests=guests, table=table)

@app.route('/book_table', methods=['POST'])
def book_table():
    if 'user' not in session:
        return jsonify({'message': 'Not logged in'}), 401

    global bookings
    booking_data = request.get_json()
    requested_table = booking_data['table']
    requested_date = booking_data['date']
    requested_time = booking_data['time']
    requested_datetime = datetime.strptime(f"{requested_date} {requested_time}", "%Y-%m-%d %H:%M")

    for booking in bookings:
        if booking['table'] == requested_table and booking['date'] == requested_date:
            existing_time = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
            time_diff = abs((existing_time - requested_datetime).total_seconds()) / 3600
            if time_diff < 2:
                return jsonify({'message': 'This table is not available at that time.'}), 400

    bookings.append(booking_data)
    save_bookings(bookings)
    return jsonify({'message': 'Booking successful!'}), 200

# ===== REGISTRATION =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        email = request.form['email']
        password = request.form['password']
        if email in users:
            return render_template('register.html', error="User already exists.")
        users[email] = generate_password_hash(password)
        save_users(users)
        return redirect('/login')
    return render_template('register.html')

# ===== LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        email = request.form['email']
        password = request.form['password']
        if email in users and check_password_hash(users[email], password):
            session['user'] = email
            if email == 'admin@shoko.com':
                return redirect('/admin')
            return redirect('/')
        return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ===== ADMIN PANEL =====
@app.route('/admin')
def admin():
    if session.get('user') != 'admin@shoko.com':
        return "Access denied", 403
    return render_template('admin.html', bookings=bookings)

# ===== RUN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=port == 5000)






