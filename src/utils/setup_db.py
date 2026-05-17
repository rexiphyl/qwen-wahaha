"""
Database Setup Script - Creates comprehensive schema with 15+ tables
Dynamically generates sample data relative to current date
"""
import sqlite3
from datetime import datetime, timedelta
import random
from loguru import logger
from src.core.config import Config

def setup_database():
    """Create database with 15+ tables and populate with realistic sample data"""
    
    db_path = Config.DATABASE_PATH
    logger.info(f"Setting up database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Drop existing tables for clean setup (disable foreign keys during drop)
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
    cursor.execute("PRAGMA foreign_keys = ON")
    
    logger.info("Creating tables...")
    
    # 1. Customers table
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        registration_date DATE DEFAULT CURRENT_DATE,
        loyalty_points INTEGER DEFAULT 0,
        is_premium BOOLEAN DEFAULT FALSE
    )
    """)
    
    # 2. Restaurants table
    cursor.execute("""
    CREATE TABLE restaurants (
        restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cuisine_type TEXT,
        address TEXT,
        city TEXT,
        rating REAL DEFAULT 0.0,
        price_range TEXT
    )
    """)
    
    # 3. Menu Items table
    cursor.execute("""
    CREATE TABLE menu_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        is_vegetarian BOOLEAN DEFAULT FALSE,
        is_available BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
    )
    """)
    
    # 4. Restaurant Orders table
    cursor.execute("""
    CREATE TABLE restaurant_orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        restaurant_id INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL,
        status TEXT DEFAULT 'pending',
        delivery_address TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
    )
    """)
    
    # 5. Order Items table
    cursor.execute("""
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_id INTEGER,
        quantity INTEGER DEFAULT 1,
        unit_price REAL,
        subtotal REAL,
        FOREIGN KEY (order_id) REFERENCES restaurant_orders(order_id),
        FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
    )
    """)
    
    # 6. Hotels table
    cursor.execute("""
    CREATE TABLE hotels (
        hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        star_rating INTEGER,
        total_rooms INTEGER,
        amenities TEXT
    )
    """)
    
    # 7. Hotel Bookings table
    cursor.execute("""
    CREATE TABLE hotel_bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        hotel_id INTEGER,
        check_in_date DATE,
        check_out_date DATE,
        room_type TEXT,
        num_guests INTEGER,
        total_price REAL,
        booking_status TEXT DEFAULT 'confirmed',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
    )
    """)
    
    # 8. Cars table
    cursor.execute("""
    CREATE TABLE cars (
        car_id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT,
        year INTEGER,
        color TEXT,
        daily_rate REAL,
        availability_status TEXT DEFAULT 'available',
        vehicle_type TEXT
    )
    """)
    
    # 9. Car Rentals table
    cursor.execute("""
    CREATE TABLE car_rentals (
        rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        car_id INTEGER,
        rental_start_date TIMESTAMP,
        rental_end_date TIMESTAMP,
        total_cost REAL,
        rental_status TEXT DEFAULT 'active',
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (car_id) REFERENCES cars(car_id)
    )
    """)
    
    # 10. Payments table
    cursor.execute("""
    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        amount REAL NOT NULL,
        payment_method TEXT,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        transaction_id TEXT,
        service_type TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    # 11. Reviews table
    cursor.execute("""
    CREATE TABLE reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        service_type TEXT,
        service_id INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        comment TEXT,
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    # 12. Promotions table
    cursor.execute("""
    CREATE TABLE promotions (
        promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        discount_percentage REAL,
        valid_from DATE,
        valid_until DATE,
        applicable_services TEXT
    )
    """)
    
    # 13. Customer Promotions table
    cursor.execute("""
    CREATE TABLE customer_promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        promotion_id INTEGER,
        claimed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        used BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id)
    )
    """)
    
    # 14. Staff table
    cursor.execute("""
    CREATE TABLE staff (
        staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT,
        department TEXT,
        hire_date DATE,
        salary REAL,
        is_active BOOLEAN DEFAULT TRUE
    )
    """)
    
    # 15. Inventory table
    cursor.execute("""
    CREATE TABLE inventory (
        inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT,
        quantity INTEGER DEFAULT 0,
        unit TEXT,
        reorder_level INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    logger.info("Tables created. Inserting sample data...")
    
    # Insert sample data
    today = datetime.now()
    
    # Customers
    customers = [
        ("John", "Doe", "john.doe@email.com", "555-0101", 500, True),
        ("Jane", "Smith", "jane.smith@email.com", "555-0102", 1200, True),
        ("Bob", "Wilson", "bob.wilson@email.com", "555-0103", 300, False),
        ("Alice", "Brown", "alice.brown@email.com", "555-0104", 800, True),
        ("Charlie", "Davis", "charlie.davis@email.com", "555-0105", 150, False),
    ]
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, email, phone, loyalty_points, is_premium) VALUES (?, ?, ?, ?, ?, ?)",
        customers
    )
    
    # Restaurants
    restaurants = [
        ("The Green Leaf", "Vegetarian", "123 Main St", "New York", 4.5, "$$"),
        ("Burger Palace", "American", "456 Oak Ave", "Los Angeles", 4.2, "$"),
        ("Sushi Master", "Japanese", "789 Pine Rd", "Chicago", 4.8, "$$$"),
        ("Pasta Bella", "Italian", "321 Elm St", "Houston", 4.3, "$$"),
        ("Taco Fiesta", "Mexican", "654 Maple Dr", "Phoenix", 4.1, "$"),
    ]
    cursor.executemany(
        "INSERT INTO restaurants (name, cuisine_type, address, city, rating, price_range) VALUES (?, ?, ?, ?, ?, ?)",
        restaurants
    )
    
    # Menu Items (including vegetarian options)
    menu_items = [
        (1, "Caesar Salad", "Fresh romaine lettuce", 12.99, "Salad", True, True),
        (1, "Veggie Burger", "Plant-based patty", 15.99, "Main", True, True),
        (1, "Grilled Salmon", "Atlantic salmon", 24.99, "Main", False, True),
        (2, "Classic Burger", "Beef patty with cheese", 11.99, "Main", False, True),
        (2, "Veggie Wrap", "Grilled vegetables", 10.99, "Main", True, True),
        (3, "Sushi Platter", "Assorted nigiri and rolls", 35.99, "Main", False, True),
        (3, "Vegetable Tempura", "Crispy battered vegetables", 14.99, "Appetizer", True, True),
        (4, "Margherita Pizza", "Tomato, mozzarella, basil", 16.99, "Main", True, True),
        (4, "Spaghetti Carbonara", "Pasta with egg and bacon", 18.99, "Main", False, True),
        (5, "Burrito Bowl", "Rice, beans, salsa", 13.99, "Main", True, True),
    ]
    cursor.executemany(
        "INSERT INTO menu_items (restaurant_id, name, description, price, category, is_vegetarian, is_available) VALUES (?, ?, ?, ?, ?, ?, ?)",
        menu_items
    )
    
    # Restaurant Orders (with dates relative to today)
    orders = []
    for i in range(20):
        cust_id = random.randint(1, 5)
        rest_id = random.randint(1, 5)
        days_ago = random.randint(0, 30)
        order_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        total = round(random.uniform(15, 80), 2)
        status = random.choice(["completed", "completed", "completed", "pending", "cancelled"])
        orders.append((cust_id, rest_id, order_date, total, status, f"{random.randint(1,999)} Street"))
    
    cursor.executemany(
        "INSERT INTO restaurant_orders (customer_id, restaurant_id, order_date, total_amount, status, delivery_address) VALUES (?, ?, ?, ?, ?, ?)",
        orders
    )
    
    # Order Items
    order_items = []
    for order_id in range(1, 21):
        num_items = random.randint(1, 4)
        for _ in range(num_items):
            item_id = random.randint(1, 10)
            qty = random.randint(1, 3)
            price = round(random.uniform(8, 30), 2)
            order_items.append((order_id, item_id, qty, price, round(qty * price, 2)))
    
    cursor.executemany(
        "INSERT INTO order_items (order_id, item_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
        order_items
    )
    
    # Hotels
    hotels = [
        ("Grand Plaza", "Downtown", 5, 200, "Pool, Spa, Gym"),
        ("Comfort Inn", "Airport Area", 3, 100, "Free Breakfast, WiFi"),
        ("Seaside Resort", "Beach Front", 4, 150, "Ocean View, Pool"),
    ]
    cursor.executemany(
        "INSERT INTO hotels (name, location, star_rating, total_rooms, amenities) VALUES (?, ?, ?, ?, ?)",
        hotels
    )
    
    # Hotel Bookings (with dates relative to today)
    bookings = []
    for i in range(15):
        cust_id = random.randint(1, 5)
        hotel_id = random.randint(1, 3)
        check_in = (today + timedelta(days=random.randint(-10, 20))).strftime("%Y-%m-%d")
        check_out = (today + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
        room_type = random.choice(["Standard", "Deluxe", "Suite"])
        guests = random.randint(1, 4)
        price = round(random.uniform(100, 500), 2)
        status = random.choice(["confirmed", "confirmed", "checked-in", "checked-out", "cancelled"])
        bookings.append((cust_id, hotel_id, check_in, check_out, room_type, guests, price, status))
    
    cursor.executemany(
        "INSERT INTO hotel_bookings (customer_id, hotel_id, check_in_date, check_out_date, room_type, num_guests, total_price, booking_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        bookings
    )
    
    # Cars
    cars = [
        ("Toyota", "Camry", 2023, "Silver", 45.0, "available", "Sedan"),
        ("Honda", "CR-V", 2022, "Blue", 55.0, "available", "SUV"),
        ("Ford", "Mustang", 2024, "Red", 85.0, "rented", "Sports"),
        ("Tesla", "Model 3", 2023, "White", 75.0, "available", "Electric"),
        ("Jeep", "Wrangler", 2022, "Black", 65.0, "available", "SUV"),
    ]
    cursor.executemany(
        "INSERT INTO cars (make, model, year, color, daily_rate, availability_status, vehicle_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
        cars
    )
    
    # Car Rentals
    rentals = []
    for i in range(10):
        cust_id = random.randint(1, 5)
        car_id = random.randint(1, 5)
        start_date = (today - timedelta(days=random.randint(0, 20))).strftime("%Y-%m-%d %H:%M:%S")
        end_date = (today + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d %H:%M:%S")
        cost = round(random.uniform(100, 500), 2)
        status = random.choice(["active", "completed", "completed", "upcoming"])
        rentals.append((cust_id, car_id, start_date, end_date, cost, status))
    
    cursor.executemany(
        "INSERT INTO car_rentals (customer_id, car_id, rental_start_date, rental_end_date, total_cost, rental_status) VALUES (?, ?, ?, ?, ?, ?)",
        rentals
    )
    
    # Payments
    payments = []
    for i in range(25):
        cust_id = random.randint(1, 5)
        amount = round(random.uniform(20, 500), 2)
        method = random.choice(["credit_card", "debit_card", "paypal", "cash"])
        pay_date = (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choice(["completed", "completed", "completed", "pending", "failed"])
        trans_id = f"TXN{random.randint(10000, 99999)}"
        service = random.choice(["restaurant", "hotel", "car_rental"])
        payments.append((cust_id, amount, method, pay_date, status, trans_id, service))
    
    cursor.executemany(
        "INSERT INTO payments (customer_id, amount, payment_method, payment_date, status, transaction_id, service_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
        payments
    )
    
    # Reviews
    reviews = []
    for i in range(12):
        cust_id = random.randint(1, 5)
        service = random.choice(["restaurant", "hotel", "car_rental"])
        service_id = random.randint(1, 5)
        rating = random.randint(3, 5)
        comment = random.choice([
            "Great experience!",
            "Very satisfied with the service.",
            "Could be better.",
            "Excellent! Will come again.",
            "Average experience."
        ])
        rev_date = (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        reviews.append((cust_id, service, service_id, rating, comment, rev_date))
    
    cursor.executemany(
        "INSERT INTO reviews (customer_id, service_type, service_id, rating, comment, review_date) VALUES (?, ?, ?, ?, ?, ?)",
        reviews
    )
    
    # Promotions
    promotions = [
        ("Summer Sale", "20% off all services", 20.0, "2026-06-01", "2026-08-31", "all"),
        ("New Customer", "15% off first order", 15.0, "2026-01-01", "2026-12-31", "restaurant"),
        ("Weekend Special", "10% off hotel bookings", 10.0, "2026-01-01", "2026-12-31", "hotel"),
    ]
    cursor.executemany(
        "INSERT INTO promotions (name, description, discount_percentage, valid_from, valid_until, applicable_services) VALUES (?, ?, ?, ?, ?, ?)",
        promotions
    )
    
    # Staff
    staff = [
        ("Michael", "Johnson", "Manager", "Operations", "2023-01-15", 65000, True),
        ("Sarah", "Williams", "Chef", "Kitchen", "2023-03-20", 55000, True),
        ("David", "Martinez", "Receptionist", "Front Desk", "2023-06-10", 35000, True),
        ("Emily", "Garcia", "Driver", "Transportation", "2023-09-05", 40000, True),
    ]
    cursor.executemany(
        "INSERT INTO staff (first_name, last_name, role, department, hire_date, salary, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
        staff
    )
    
    # Inventory
    inventory = [
        ("Tomatoes", "Produce", 50, "kg", 10),
        ("Chicken Breast", "Meat", 30, "kg", 5),
        ("Rice", "Grains", 100, "kg", 20),
        ("Olive Oil", "Condiments", 15, "liters", 3),
        ("Paper Towels", "Supplies", 200, "rolls", 50),
    ]
    cursor.executemany(
        "INSERT INTO inventory (item_name, category, quantity, unit, reorder_level) VALUES (?, ?, ?, ?, ?)",
        inventory
    )
    
    conn.commit()
    conn.close()
    
    logger.info(f"Database setup complete! Created 15 tables with sample data.")
    print(f"✅ Database '{db_path}' created successfully with 15 tables!")

if __name__ == "__main__":
    setup_database()
