"""
Database Initialization Script
Creates tables for car_rentals, hotel_bookings, payments, and restaurant_orders.
Populates them with rich sample data to help the AI understand intents correctly.
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "business_db.sqlite"

def init_db():
    # Remove existing DB to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Car Rentals Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS car_rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        car_model TEXT NOT NULL,
        rental_date DATE NOT NULL,
        return_date DATE NOT NULL,
        total_cost REAL NOT NULL,
        status TEXT DEFAULT 'active'
    )
    """)

    # 2. Hotel Bookings Table (Crucial for "bookings" intent)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotel_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT NOT NULL,
        room_type TEXT NOT NULL,
        check_in_date DATE NOT NULL,
        check_out_date DATE NOT NULL,
        num_guests INTEGER NOT NULL,
        total_price REAL NOT NULL,
        booking_status TEXT DEFAULT 'confirmed'
    )
    """)

    # 3. Payments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_date DATE NOT NULL,
        status TEXT DEFAULT 'completed'
    )
    """)

    # 4. Restaurant Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        order_time DATETIME NOT NULL,
        total_bill REAL NOT NULL,
        served BOOLEAN DEFAULT 0
    )
    """)

    today = datetime.now()

    # Sample Car Rentals
    cars = [
        ('Alice Johnson', 'Toyota Camry', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=2)).strftime('%Y-%m-%d'), 350.00, 'active'),
        ('Bob Smith', 'Ford Mustang', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=3)).strftime('%Y-%m-%d'), 450.00, 'active'),
        ('Charlie Brown', 'Honda CRV', (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today - timedelta(days=3)).strftime('%Y-%m-%d'), 280.00, 'completed'),
    ]
    cursor.executemany("INSERT INTO car_rentals (customer_name, car_model, rental_date, return_date, total_cost, status) VALUES (?, ?, ?, ?, ?, ?)", cars)

    # Sample Hotel Bookings (With dates relative to "this month")
    hotels = [
        ('John Doe', 'Deluxe Suite', (today - timedelta(days=2)).strftime('%Y-%m-%d'), (today + timedelta(days=3)).strftime('%Y-%m-%d'), 2, 1200.50, 'confirmed'),
        ('Jane Roe', 'Standard Room', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=1)).strftime('%Y-%m-%d'), 1, 450.00, 'checked-in'),
        ('Mike Ross', 'Penthouse', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today - timedelta(days=1)).strftime('%Y-%m-%d'), 4, 3500.00, 'completed'),
        ('Rachel Zane', 'Double Room', (today + timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=4)).strftime('%Y-%m-%d'), 2, 600.00, 'pending'),
        ('Ross Geller', 'Suite', (today - timedelta(days=15)).strftime('%Y-%m-%d'), (today - timedelta(days=10)).strftime('%Y-%m-%d'), 1, 800.00, 'completed'),
    ]
    cursor.executemany("INSERT INTO hotel_bookings (guest_name, room_type, check_in_date, check_out_date, num_guests, total_price, booking_status) VALUES (?, ?, ?, ?, ?, ?, ?)", hotels)

    # Sample Payments
    payments = [
        ('TXN001', 1200.50, 'Credit Card', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'completed'),
        ('TXN002', 45.00, 'Cash', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'completed'),
        ('TXN003', 350.00, 'Debit Card', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'completed'),
        ('TXN004', 99.99, 'PayPal', today.strftime('%Y-%m-%d'), 'pending'),
    ]
    cursor.executemany("INSERT INTO payments (transaction_id, amount, payment_method, payment_date, status) VALUES (?, ?, ?, ?, ?)", payments)

    # Sample Restaurant Orders
    orders = [
        (1, 'Burger', 2, (today - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 24.00, 1),
        (2, 'Pizza', 1, (today - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'), 18.50, 1),
        (3, 'Salad', 3, (today - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'), 35.00, 0),
        (1, 'Pasta', 1, (today - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'), 15.00, 0),
        (4, 'Steak', 2, (today - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'), 65.00, 1),
    ]
    cursor.executemany("INSERT INTO restaurant_orders (table_number, item_name, quantity, order_time, total_bill, served) VALUES (?, ?, ?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DB_PATH}")
    print("Tables created: car_rentals, hotel_bookings, payments, restaurant_orders")
    print("Sample data populated.")

if __name__ == "__main__":
    init_db()
