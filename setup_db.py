"""
Database Initialization Script
Creates 14+ tables for diverse business use cases to help the AI understand intents correctly.
Populates them with rich sample data including vegetarian options, dates, and various scenarios.
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
        status TEXT DEFAULT 'active',
        fuel_type TEXT DEFAULT 'petrol'
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
        booking_status TEXT DEFAULT 'confirmed',
        special_requests TEXT
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
        status TEXT DEFAULT 'completed',
        currency TEXT DEFAULT 'USD'
    )
    """)

    # 4. Restaurant Orders Table (With is_vegetarian flag)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        order_time DATETIME NOT NULL,
        total_bill REAL NOT NULL,
        served BOOLEAN DEFAULT 0,
        is_vegetarian BOOLEAN DEFAULT 0,
        customer_name TEXT
    )
    """)

    # 5. Employees Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        hire_date DATE NOT NULL,
        salary REAL NOT NULL,
        email TEXT UNIQUE
    )
    """)

    # 6. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        supplier TEXT,
        last_restocked DATE
    )
    """)

    # 7. Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        registration_date DATE,
        loyalty_points INTEGER DEFAULT 0,
        membership_tier TEXT DEFAULT 'bronze'
    )
    """)

    # 8. Orders Table (General E-commerce)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        order_date DATE NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        shipping_address TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # 9. Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        warehouse_location TEXT,
        quantity_available INTEGER NOT NULL,
        last_updated DATE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    # 10. Suppliers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        contact_person TEXT,
        email TEXT,
        phone TEXT,
        country TEXT,
        rating REAL DEFAULT 5.0
    )
    """)

    # 11. Marketing Campaigns Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_name TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        budget REAL NOT NULL,
        channel TEXT NOT NULL,
        conversions INTEGER DEFAULT 0,
        status TEXT DEFAULT 'planned'
    )
    """)

    # 12. Support Tickets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        subject TEXT NOT NULL,
        description TEXT,
        created_date DATE NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        assigned_to TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # 13. Flights Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_number TEXT UNIQUE NOT NULL,
        airline TEXT NOT NULL,
        departure_city TEXT NOT NULL,
        arrival_city TEXT NOT NULL,
        departure_time DATETIME NOT NULL,
        arrival_time DATETIME NOT NULL,
        available_seats INTEGER,
        price REAL NOT NULL
    )
    """)

    # 14. Events Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        venue TEXT NOT NULL,
        event_date DATE NOT NULL,
        ticket_price REAL NOT NULL,
        capacity INTEGER NOT NULL,
        tickets_sold INTEGER DEFAULT 0,
        organizer TEXT
    )
    """)

    today = datetime.now()

    # Sample Car Rentals
    cars = [
        ('Alice Johnson', 'Toyota Camry', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=2)).strftime('%Y-%m-%d'), 350.00, 'active', 'petrol'),
        ('Bob Smith', 'Ford Mustang', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=3)).strftime('%Y-%m-%d'), 450.00, 'active', 'petrol'),
        ('Charlie Brown', 'Honda CRV', (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today - timedelta(days=3)).strftime('%Y-%m-%d'), 280.00, 'completed', 'hybrid'),
        ('Diana Prince', 'Tesla Model 3', (today - timedelta(days=2)).strftime('%Y-%m-%d'), (today + timedelta(days=5)).strftime('%Y-%m-%d'), 550.00, 'active', 'electric'),
    ]
    cursor.executemany("INSERT INTO car_rentals (customer_name, car_model, rental_date, return_date, total_cost, status, fuel_type) VALUES (?, ?, ?, ?, ?, ?, ?)", cars)

    # Sample Hotel Bookings (With dates relative to "this month")
    hotels = [
        ('John Doe', 'Deluxe Suite', (today - timedelta(days=2)).strftime('%Y-%m-%d'), (today + timedelta(days=3)).strftime('%Y-%m-%d'), 2, 1200.50, 'confirmed', 'Late checkout'),
        ('Jane Roe', 'Standard Room', (today - timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=1)).strftime('%Y-%m-%d'), 1, 450.00, 'checked-in', None),
        ('Mike Ross', 'Penthouse', (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today - timedelta(days=1)).strftime('%Y-%m-%d'), 4, 3500.00, 'completed', 'Airport pickup'),
        ('Rachel Zane', 'Double Room', (today + timedelta(days=1)).strftime('%Y-%m-%d'), (today + timedelta(days=4)).strftime('%Y-%m-%d'), 2, 600.00, 'pending', None),
        ('Ross Geller', 'Suite', (today - timedelta(days=15)).strftime('%Y-%m-%d'), (today - timedelta(days=10)).strftime('%Y-%m-%d'), 1, 800.00, 'completed', 'Extra pillows'),
    ]
    cursor.executemany("INSERT INTO hotel_bookings (guest_name, room_type, check_in_date, check_out_date, num_guests, total_price, booking_status, special_requests) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", hotels)

    # Sample Payments
    payments = [
        ('TXN001', 1200.50, 'Credit Card', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'completed', 'USD'),
        ('TXN002', 45.00, 'Cash', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'completed', 'USD'),
        ('TXN003', 350.00, 'Debit Card', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'completed', 'USD'),
        ('TXN004', 99.99, 'PayPal', today.strftime('%Y-%m-%d'), 'pending', 'USD'),
        ('TXN005', 550.00, 'Credit Card', (today - timedelta(days=3)).strftime('%Y-%m-%d'), 'completed', 'EUR'),
    ]
    cursor.executemany("INSERT INTO payments (transaction_id, amount, payment_method, payment_date, status, currency) VALUES (?, ?, ?, ?, ?, ?)", payments)

    # Sample Restaurant Orders (With explicit is_vegetarian flags)
    orders = [
        (1, 'Burger', 2, (today - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 24.00, 1, 0, 'Alice'),
        (2, 'Margherita Pizza', 1, (today - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'), 18.50, 1, 1, 'Bob'),
        (3, 'Caesar Salad', 3, (today - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'), 35.00, 0, 1, 'Charlie'),
        (1, 'Pasta Alfredo', 1, (today - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S'), 15.00, 0, 1, 'Alice'),
        (4, 'Grilled Steak', 2, (today - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'), 65.00, 1, 0, 'Diana'),
        (5, 'Veggie Wrap', 1, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 12.00, 1, 1, 'Eve'),
        (6, 'Mushroom Risotto', 2, (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 28.00, 1, 1, 'Frank'),
        (7, 'Fish Tacos', 1, (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 22.00, 1, 0, 'Grace'),
        (8, 'Vegetable Stir Fry', 3, (today - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'), 30.00, 1, 1, 'Henry'),
        (9, 'Lamb Chops', 1, (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 45.00, 1, 0, 'Ivy'),
        (10, 'Caprese Salad', 2, (today - timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'), 16.00, 1, 1, 'Jack'),
        (2, 'Vegan Burger', 1, (today - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'), 14.00, 1, 1, 'Kate'),
    ]
    cursor.executemany("INSERT INTO restaurant_orders (table_number, item_name, quantity, order_time, total_bill, served, is_vegetarian, customer_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", orders)

    # Sample Employees
    employees = [
        ('Sarah Connor', 'IT', 'Developer', (today - timedelta(days=365)).strftime('%Y-%m-%d'), 85000, 'sarah@company.com'),
        ('James Bond', 'Security', 'Agent', (today - timedelta(days=500)).strftime('%Y-%m-%d'), 95000, 'james@company.com'),
        ('Ellen Ripley', 'Operations', 'Manager', (today - timedelta(days=700)).strftime('%Y-%m-%d'), 110000, 'ellen@company.com'),
        ('Tony Stark', 'R&D', 'Director', (today - timedelta(days=1000)).strftime('%Y-%m-%d'), 250000, 'tony@company.com'),
    ]
    cursor.executemany("INSERT INTO employees (name, department, position, hire_date, salary, email) VALUES (?, ?, ?, ?, ?, ?)", employees)

    # Sample Products
    products = [
        ('Laptop Pro', 'Electronics', 1299.99, 50, 'TechSupply Inc', (today - timedelta(days=10)).strftime('%Y-%m-%d')),
        ('Wireless Mouse', 'Electronics', 29.99, 200, 'TechSupply Inc', (today - timedelta(days=5)).strftime('%Y-%m-%d')),
        ('Office Chair', 'Furniture', 199.99, 30, 'ComfortZone', (today - timedelta(days=20)).strftime('%Y-%m-%d')),
        ('Standing Desk', 'Furniture', 499.99, 15, 'ComfortZone', (today - timedelta(days=15)).strftime('%Y-%m-%d')),
        ('Notebook Set', 'Stationery', 12.99, 500, 'PaperWorld', (today - timedelta(days=2)).strftime('%Y-%m-%d')),
    ]
    cursor.executemany("INSERT INTO products (product_name, category, price, stock_quantity, supplier, last_restocked) VALUES (?, ?, ?, ?, ?, ?)", products)

    # Sample Customers
    customers = [
        ('Alice Johnson', 'alice@email.com', '555-0101', (today - timedelta(days=100)).strftime('%Y-%m-%d'), 150, 'gold'),
        ('Bob Smith', 'bob@email.com', '555-0102', (today - timedelta(days=200)).strftime('%Y-%m-%d'), 80, 'silver'),
        ('Charlie Brown', 'charlie@email.com', '555-0103', (today - timedelta(days=50)).strftime('%Y-%m-%d'), 200, 'platinum'),
        ('Diana Prince', 'diana@email.com', '555-0104', (today - timedelta(days=300)).strftime('%Y-%m-%d'), 500, 'platinum'),
    ]
    cursor.executemany("INSERT INTO customers (name, email, phone, registration_date, loyalty_points, membership_tier) VALUES (?, ?, ?, ?, ?, ?)", customers)

    # Sample Orders
    orders_general = [
        (1, (today - timedelta(days=5)).strftime('%Y-%m-%d'), 1329.98, 'delivered', '123 Main St'),
        (2, (today - timedelta(days=3)).strftime('%Y-%m-%d'), 59.98, 'shipped', '456 Oak Ave'),
        (3, today.strftime('%Y-%m-%d'), 499.99, 'pending', '789 Pine Rd'),
        (4, (today - timedelta(days=10)).strftime('%Y-%m-%d'), 12.99, 'delivered', '321 Elm St'),
    ]
    cursor.executemany("INSERT INTO orders (customer_id, order_date, total_amount, status, shipping_address) VALUES (?, ?, ?, ?, ?)", orders_general)

    # Sample Inventory
    inventory = [
        (1, 'Warehouse A', 45, (today - timedelta(days=1)).strftime('%Y-%m-%d')),
        (2, 'Warehouse A', 180, (today - timedelta(days=1)).strftime('%Y-%m-%d')),
        (3, 'Warehouse B', 28, (today - timedelta(days=2)).strftime('%Y-%m-%d')),
        (4, 'Warehouse B', 12, (today - timedelta(days=2)).strftime('%Y-%m-%d')),
        (5, 'Warehouse C', 480, (today - timedelta(days=1)).strftime('%Y-%m-%d')),
    ]
    cursor.executemany("INSERT INTO inventory (product_id, warehouse_location, quantity_available, last_updated) VALUES (?, ?, ?, ?)", inventory)

    # Sample Suppliers
    suppliers = [
        ('TechSupply Inc', 'John Tech', 'john@techsupply.com', '555-1001', 'USA', 4.8),
        ('ComfortZone', 'Mary Comfort', 'mary@comfortzone.com', '555-1002', 'Canada', 4.5),
        ('PaperWorld', 'Peter Paper', 'peter@paperworld.com', '555-1003', 'UK', 4.2),
    ]
    cursor.executemany("INSERT INTO suppliers (company_name, contact_person, email, phone, country, rating) VALUES (?, ?, ?, ?, ?, ?)", suppliers)

    # Sample Marketing Campaigns
    campaigns = [
        ('Summer Sale', (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today + timedelta(days=20)).strftime('%Y-%m-%d'), 5000.00, 'Social Media', 150, 'active'),
        ('Black Friday', (today + timedelta(days=180)).strftime('%Y-%m-%d'), (today + timedelta(days=185)).strftime('%Y-%m-%d'), 15000.00, 'Email', 0, 'planned'),
        ('New Year Promo', (today + timedelta(days=200)).strftime('%Y-%m-%d'), (today + timedelta(days=210)).strftime('%Y-%m-%d'), 8000.00, 'TV', 0, 'planned'),
    ]
    cursor.executemany("INSERT INTO marketing_campaigns (campaign_name, start_date, end_date, budget, channel, conversions, status) VALUES (?, ?, ?, ?, ?, ?, ?)", campaigns)

    # Sample Support Tickets
    tickets = [
        (1, 'Login Issue', 'Cannot access account', (today - timedelta(days=2)).strftime('%Y-%m-%d'), 'high', 'open', 'Sarah'),
        (2, 'Billing Question', 'Duplicate charge on card', (today - timedelta(days=1)).strftime('%Y-%m-%d'), 'medium', 'in_progress', 'James'),
        (3, 'Feature Request', 'Add dark mode', (today - timedelta(days=5)).strftime('%Y-%m-%d'), 'low', 'closed', 'Ellen'),
        (4, 'Bug Report', 'App crashes on startup', today.strftime('%Y-%m-%d'), 'critical', 'open', 'Sarah'),
    ]
    cursor.executemany("INSERT INTO support_tickets (customer_id, subject, description, created_date, priority, status, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?)", tickets)

    # Sample Flights
    flights = [
        ('AA100', 'American Airlines', 'New York', 'London', (today + timedelta(days=1, hours=10)).strftime('%Y-%m-%d %H:%M:%S'), (today + timedelta(days=1, hours=22)).strftime('%Y-%m-%d %H:%M:%S'), 45, 650.00),
        ('BA200', 'British Airways', 'London', 'Paris', (today + timedelta(days=2, hours=8)).strftime('%Y-%m-%d %H:%M:%S'), (today + timedelta(days=2, hours=10)).strftime('%Y-%m-%d %H:%M:%S'), 30, 200.00),
        ('DL300', 'Delta', 'Los Angeles', 'Tokyo', (today + timedelta(days=5, hours=14)).strftime('%Y-%m-%d %H:%M:%S'), (today + timedelta(days=6, hours=18)).strftime('%Y-%m-%d %H:%M:%S'), 120, 1200.00),
        ('UA400', 'United', 'Chicago', 'Frankfurt', (today + timedelta(days=3, hours=16)).strftime('%Y-%m-%d %H:%M:%S'), (today + timedelta(days=4, hours=8)).strftime('%Y-%m-%d %H:%M:%S'), 80, 850.00),
    ]
    cursor.executemany("INSERT INTO flights (flight_number, airline, departure_city, arrival_city, departure_time, arrival_time, available_seats, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", flights)

    # Sample Events
    events = [
        ('Tech Conference 2026', 'Convention Center', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 299.00, 1000, 450, 'TechEvents Inc'),
        ('Music Festival', 'City Park', (today + timedelta(days=60)).strftime('%Y-%m-%d'), 89.00, 5000, 3200, 'LiveNation'),
        ('Art Exhibition', 'Modern Art Museum', (today + timedelta(days=10)).strftime('%Y-%m-%d'), 25.00, 200, 180, 'City Arts'),
        ('Food & Wine Expo', 'Harbor Center', (today + timedelta(days=45)).strftime('%Y-%m-%d'), 75.00, 800, 600, 'GourmetEvents'),
    ]
    cursor.executemany("INSERT INTO events (event_name, venue, event_date, ticket_price, capacity, tickets_sold, organizer) VALUES (?, ?, ?, ?, ?, ?, ?)", events)

    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DB_PATH}")
    print("Tables created: car_rentals, hotel_bookings, payments, restaurant_orders, employees, products, customers, orders, inventory, suppliers, marketing_campaigns, support_tickets, flights, events")
    print("Sample data populated with 14+ tables for diverse use cases.")

if __name__ == "__main__":
    init_db()
