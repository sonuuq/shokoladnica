from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.json'

def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_bookings(data):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

bookings = load_bookings()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/confirmation')
def confirmation():
    name = request.args.get('name')
    date = request.args.get('date')
    time = request.args.get('time')
    guests = request.args.get('guests')
    table = request.args.get('table')
    return render_template('confirmation.html', name=name, date=date, time=time, guests=guests, table=table)

@app.route('/book_table', methods=['POST'])
def book_table():
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

# Универсальный запуск для всех сред
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Для Render
    app.run(host='0.0.0.0', port=port, debug=port == 5000)  # Debug только локально





