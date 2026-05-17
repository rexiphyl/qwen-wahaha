"""Database setup script with comprehensive sample data."""
import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

# Import schema directly
DATABASE_SCHEMA = """
-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    registration_date DATE DEFAULT CURRENT_DATE,
    loyalty_points INTEGER DEFAULT 0,
    customer_tier TEXT CHECK(customer_tier IN ('bronze', 'silver', 'gold', 'platinum')) DEFAULT 'bronze'
);

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cuisine_type TEXT,
    location TEXT,
    phone TEXT,
    rating REAL CHECK(rating >= 0 AND rating <= 5),
    price_range TEXT CHECK(price_range IN ('$','$$','$$$','$$$$'))
);

-- Menu items table
CREATE TABLE IF NOT EXISTS menu_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    category TEXT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- Restaurant orders table
CREATE TABLE IF NOT EXISTS restaurant_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    restaurant_id INTEGER,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount REAL NOT NULL,
    status TEXT CHECK(status IN ('pending', 'confirmed', 'preparing', 'delivered', 'cancelled')),
    delivery_address TEXT,
    payment_method TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
);

-- Order items table (linking orders to menu items)
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    item_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    special_instructions TEXT,
    FOREIGN KEY (order_id) REFERENCES restaurant_orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

-- Hotels table
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    star_rating INTEGER CHECK(star_rating BETWEEN 1 AND 5),
    phone TEXT,
    amenities TEXT
);

-- Hotel bookings table
CREATE TABLE IF NOT EXISTS hotel_bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    hotel_id INTEGER,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    room_type TEXT,
    num_guests INTEGER,
    total_price REAL NOT NULL,
    status TEXT CHECK(status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id)
);

-- Cars table
CREATE TABLE IF NOT EXISTS cars (
    car_id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER,
    color TEXT,
    license_plate TEXT UNIQUE,
    daily_rate REAL NOT NULL,
    availability_status TEXT CHECK(availability_status IN ('available', 'rented', 'maintenance')) DEFAULT 'available',
    car_type TEXT CHECK(car_type IN ('economy', 'compact', 'midsize', 'luxury', 'suv', 'van'))
);

-- Car rentals table
CREATE TABLE IF NOT EXISTS car_rentals (
    rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    car_id INTEGER,
    rental_start_date TIMESTAMP NOT NULL,
    rental_end_date TIMESTAMP NOT NULL,
    actual_return_date TIMESTAMP,
    total_cost REAL NOT NULL,
    status TEXT CHECK(status IN ('active', 'completed', 'overdue', 'cancelled')),
    pickup_location TEXT,
    dropoff_location TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    amount REAL NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT CHECK(payment_method IN ('credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash')),
    status TEXT CHECK(status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id TEXT,
    related_booking_type TEXT CHECK(related_booking_type IN ('restaurant', 'hotel', 'car_rental')),
    related_booking_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    review_type TEXT CHECK(review_type IN ('restaurant', 'hotel', 'car')),
    related_id INTEGER,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Promotions table
CREATE TABLE IF NOT EXISTS promotions (
    promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    discount_percentage REAL,
    discount_amount REAL,
    valid_from DATE,
    valid_until DATE,
    applicable_services TEXT,
    min_purchase_amount REAL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Customer promotions table (linking customers to promotions)
CREATE TABLE IF NOT EXISTS customer_promotions (
    customer_promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    promotion_id INTEGER,
    used_date TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id)
);

-- Staff table
CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT,
    department TEXT,
    hire_date DATE,
    salary REAL,
    manager_id INTEGER,
    FOREIGN KEY (manager_id) REFERENCES staff(staff_id)
);

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT,
    quantity INTEGER NOT NULL,
    unit TEXT,
    reorder_level INTEGER,
    supplier TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def setup_database():
    """Create database schema and populate with sample data."""
    
    # Database path - in project root
    db_path = Path(__file__).parent.parent / "business_db.sqlite"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all tables
    cursor.executescript(DATABASE_SCHEMA)
    
    # Insert sample customers
    customers = [
        ("John", "Smith", "john.smith@email.com", "555-0101", 150, "gold"),
        ("Sarah", "Johnson", "sarah.j@email.com", "555-0102", 320, "platinum"),
        ("Mike", "Williams", "mike.w@email.com", "555-0103", 45, "bronze"),
        ("Emily", "Brown", "emily.b@email.com", "555-0104", 280, "gold"),
        ("David", "Jones", "david.j@email.com", "555-0105", 90, "silver"),
        ("Lisa", "Garcia", "lisa.g@email.com", "555-0106", 15, "bronze"),
        ("Robert", "Martinez", "robert.m@email.com", "555-0107", 450, "platinum"),
        ("Jennifer", "Davis", "jennifer.d@email.com", "555-0108", 200, "gold"),
        ("William", "Rodriguez", "william.r@email.com", "555-0109", 60, "silver"),
        ("Maria", "Wilson", "maria.w@email.com", "555-0110", 110, "silver")
    ]
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, email, phone, loyalty_points, customer_tier) VALUES (?, ?, ?, ?, ?, ?)",
        customers
    )
    
    # Insert sample restaurants
    restaurants = [
        ("The Green Leaf", "Vegetarian", "123 Main St", "555-1001", 4.5, "$$"),
        ("Pasta Palace", "Italian", "456 Oak Ave", "555-1002", 4.2, "$$$"),
        ("Burger Barn", "American", "789 Pine Rd", "555-1003", 3.8, "$"),
        ("Sushi Zen", "Japanese", "321 Elm St", "555-1004", 4.7, "$$$$"),
        ("Taco Fiesta", "Mexican", "654 Maple Dr", "555-1005", 4.0, "$$"),
        ("Curry House", "Indian", "987 Cedar Ln", "555-1006", 4.3, "$$")
    ]
    cursor.executemany(
        "INSERT INTO restaurants (name, cuisine_type, location, phone, rating, price_range) VALUES (?, ?, ?, ?, ?, ?)",
        restaurants
    )
    
    # Insert sample menu items (with vegetarian options)
    menu_items = [
        (1, "Caesar Salad", "Fresh romaine with parmesan", 12.99, True, False, True, "Appetizer"),
        (1, "Veggie Burger", "Plant-based patty with veggies", 15.99, True, True, False, "Main"),
        (1, "Grilled Salmon", "Atlantic salmon with herbs", 24.99, False, False, True, "Main"),
        (1, "Mushroom Risotto", "Creamy arborio rice with mushrooms", 18.99, True, False, True, "Main"),
        (2, "Margherita Pizza", "Classic tomato and mozzarella", 16.99, True, False, False, "Main"),
        (2, "Spaghetti Carbonara", "Traditional Italian pasta", 19.99, False, False, False, "Main"),
        (2, "Vegetable Lasagna", "Layers of pasta with veggies", 17.99, True, True, False, "Main"),
        (3, "Classic Burger", "Beef patty with lettuce and tomato", 11.99, False, False, False, "Main"),
        (3, "Veggie Wrap", "Grilled vegetables in tortilla", 9.99, True, True, False, "Main"),
        (3, "Chicken Wings", "Spicy buffalo wings", 13.99, False, False, False, "Appetizer"),
        (4, "Vegetable Tempura", "Lightly battered vegetables", 10.99, True, False, False, "Appetizer"),
        (4, "Salmon Sashimi", "Fresh salmon slices", 22.99, False, False, True, "Main"),
        (4, "Vegetable Sushi Roll", "Cucumber and avocado roll", 8.99, True, True, False, "Main"),
        (5, "Bean Burrito", "Refried beans with cheese", 10.99, True, False, False, "Main"),
        (5, "Chicken Tacos", "Three soft tacos with chicken", 12.99, False, False, False, "Main"),
        (5, "Veggie Quesadilla", "Cheese and vegetable quesadilla", 11.99, True, False, False, "Main"),
        (6, "Palak Paneer", "Spinach with Indian cottage cheese", 16.99, True, False, False, "Main"),
        (6, "Chicken Tikka Masala", "Creamy tomato curry with chicken", 18.99, False, False, False, "Main"),
        (6, "Vegetable Biryani", "Spiced rice with mixed vegetables", 15.99, True, True, False, "Main"),
        (6, "Garlic Naan", "Traditional Indian bread", 4.99, True, False, False, "Side")
    ]
    cursor.executemany(
        "INSERT INTO menu_items (restaurant_id, name, description, price, is_vegetarian, is_vegan, is_gluten_free, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        menu_items
    )
    
    # Insert sample hotels
    hotels = [
        ("Grand Plaza Hotel", "Downtown", 5, "555-2001", "Pool, Spa, Gym, Restaurant"),
        ("Comfort Inn", "Airport Area", 3, "555-2002", "Free Breakfast, WiFi"),
        ("Seaside Resort", "Beach Front", 4, "555-2003", "Beach Access, Pool, Bar"),
        ("Mountain Lodge", "Hills District", 4, "555-2004", "Hiking Trails, Fireplace")
    ]
    cursor.executemany(
        "INSERT INTO hotels (name, location, star_rating, phone, amenities) VALUES (?, ?, ?, ?, ?)",
        hotels
    )
    
    # Insert sample hotel bookings (with dates relative to today)
    today = datetime.now()
    hotel_bookings = []
    for i in range(20):
        customer_id = (i % 10) + 1
        hotel_id = (i % 4) + 1
        check_in = today - timedelta(days=random.randint(1, 30))
        check_out = check_in + timedelta(days=random.randint(1, 5))
        room_type = random.choice(["Standard", "Deluxe", "Suite", "Executive"])
        num_guests = random.randint(1, 4)
        total_price = round(random.uniform(100, 500) * num_guests, 2)
        status = random.choice(["confirmed", "checked_in", "checked_out", "cancelled"])
        hotel_bookings.append((customer_id, hotel_id, check_in.strftime("%Y-%m-%d"), check_out.strftime("%Y-%m-%d"), room_type, num_guests, total_price, status))
    
    cursor.executemany(
        "INSERT INTO hotel_bookings (customer_id, hotel_id, check_in_date, check_out_date, room_type, num_guests, total_price, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        hotel_bookings
    )
    
    # Insert sample cars
    cars = [
        ("Toyota", "Camry", 2023, "Silver", "ABC123", 45.00, "available", "midsize"),
        ("Honda", "Civic", 2022, "Blue", "DEF456", 40.00, "available", "compact"),
        ("Ford", "Explorer", 2023, "Black", "GHI789", 65.00, "rented", "suv"),
        ("BMW", "3 Series", 2024, "White", "JKL012", 85.00, "available", "luxury"),
        ("Nissan", "Altima", 2022, "Red", "MNO345", 42.00, "available", "midsize"),
        ("Jeep", "Wrangler", 2023, "Green", "PQR678", 70.00, "maintenance", "suv"),
        ("Tesla", "Model 3", 2024, "White", "STU901", 90.00, "available", "luxury"),
        ("Chevrolet", "Spark", 2021, "Yellow", "VWX234", 35.00, "available", "economy")
    ]
    cursor.executemany(
        "INSERT INTO cars (make, model, year, color, license_plate, daily_rate, availability_status, car_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        cars
    )
    
    # Insert sample car rentals
    car_rentals = []
    for i in range(15):
        customer_id = (i % 10) + 1
        car_id = (i % 8) + 1
        rental_start = today - timedelta(days=random.randint(1, 20))
        rental_end = rental_start + timedelta(days=random.randint(1, 7))
        actual_return = rental_end + timedelta(hours=random.randint(-5, 10)) if random.random() > 0.2 else None
        total_cost = round(random.uniform(100, 400), 2)
        status = random.choice(["active", "completed", "overdue", "cancelled"])
        car_rentals.append((customer_id, car_id, rental_start.strftime("%Y-%m-%d %H:%M:%S"), rental_end.strftime("%Y-%m-%d %H:%M:%S"), actual_return.strftime("%Y-%m-%d %H:%M:%S") if actual_return else None, total_cost, status, "Downtown", "Downtown"))
    
    cursor.executemany(
        "INSERT INTO car_rentals (customer_id, car_id, rental_start_date, rental_end_date, actual_return_date, total_cost, status, pickup_location, dropoff_location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        car_rentals
    )
    
    # Insert sample restaurant orders
    restaurant_orders = []
    for i in range(30):
        customer_id = (i % 10) + 1
        restaurant_id = (i % 6) + 1
        order_date = today - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        total_amount = round(random.uniform(15, 100), 2)
        status = random.choice(["pending", "confirmed", "preparing", "delivered", "cancelled"])
        delivery_address = f"{random.randint(100, 999)} Street {random.choice(['Ave', 'St', 'Rd', 'Dr'])}"
        payment_method = random.choice(["credit_card", "debit_card", "paypal", "cash"])
        restaurant_orders.append((customer_id, restaurant_id, order_date.strftime("%Y-%m-%d %H:%M:%S"), total_amount, status, delivery_address, payment_method))
    
    cursor.executemany(
        "INSERT INTO restaurant_orders (customer_id, restaurant_id, order_date, total_amount, status, delivery_address, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)",
        restaurant_orders
    )
    
    # Insert sample order items (linking orders to menu items, including vegetarian)
    order_items = []
    for i in range(60):
        order_id = (i % 30) + 1
        item_id = (i % 20) + 1
        quantity = random.randint(1, 3)
        unit_price = round(random.uniform(5, 30), 2)
        special_instructions = random.choice([None, "No onions", "Extra spicy", "Well done", "Light sauce", None, None])
        order_items.append((order_id, item_id, quantity, unit_price, special_instructions))
    
    cursor.executemany(
        "INSERT INTO order_items (order_id, item_id, quantity, unit_price, special_instructions) VALUES (?, ?, ?, ?, ?)",
        order_items
    )
    
    # Insert sample payments
    payments = []
    for i in range(25):
        customer_id = (i % 10) + 1
        amount = round(random.uniform(20, 300), 2)
        payment_date = today - timedelta(days=random.randint(0, 30))
        payment_method = random.choice(["credit_card", "debit_card", "paypal", "bank_transfer", "cash"])
        status = random.choice(["pending", "completed", "failed", "refunded"])
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        booking_type = random.choice(["restaurant", "hotel", "car_rental"])
        booking_id = random.randint(1, 20)
        payments.append((customer_id, amount, payment_date.strftime("%Y-%m-%d %H:%M:%S"), payment_method, status, transaction_id, booking_type, booking_id))
    
    cursor.executemany(
        "INSERT INTO payments (customer_id, amount, payment_date, payment_method, status, transaction_id, related_booking_type, related_booking_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        payments
    )
    
    # Insert sample reviews
    reviews = []
    for i in range(20):
        customer_id = (i % 10) + 1
        review_type = random.choice(["restaurant", "hotel", "car"])
        related_id = random.randint(1, 6)
        rating = random.randint(1, 5)
        comments = [
            "Great experience!",
            "Good value for money",
            "Could be better",
            "Excellent service",
            "Not satisfied with the quality",
            "Highly recommended",
            "Average experience",
            "Will come back again"
        ]
        comment = random.choice(comments)
        is_verified = random.choice([True, False])
        reviews.append((customer_id, review_type, related_id, rating, comment, is_verified))
    
    cursor.executemany(
        "INSERT INTO reviews (customer_id, review_type, related_id, rating, comment, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
        reviews
    )
    
    # Insert sample promotions
    promotions = [
        ("WELCOME10", "Welcome discount for new customers", 10, None, today.strftime("%Y-%m-%d"), (today + timedelta(days=30)).strftime("%Y-%m-%d"), "all", 0, True),
        ("SUMMER20", "Summer special discount", 20, None, today.strftime("%Y-%m-%d"), (today + timedelta(days=60)).strftime("%Y-%m-%d"), "hotel,car_rental", 100, True),
        ("FOODIE15", "Restaurant discount", 15, None, today.strftime("%Y-%m-%d"), (today + timedelta(days=45)).strftime("%Y-%m-%d"), "restaurant", 25, True),
        ("LOYAL25", "Loyalty member exclusive", 25, None, today.strftime("%Y-%m-%d"), (today + timedelta(days=90)).strftime("%Y-%m-%d"), "all", 0, True)
    ]
    cursor.executemany(
        "INSERT INTO promotions (code, description, discount_percentage, discount_amount, valid_from, valid_until, applicable_services, min_purchase_amount, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        promotions
    )
    
    # Insert sample staff
    staff = [
        ("Alice", "Thompson", "Manager", "Operations", "2020-01-15", 75000, None),
        ("Bob", "Anderson", "Chef", "Kitchen", "2021-03-20", 55000, 1),
        ("Carol", "White", "Receptionist", "Front Desk", "2022-06-10", 35000, 1),
        ("Dan", "Harris", "Driver", "Transport", "2021-09-05", 40000, 1),
        ("Eva", "Martin", "Server", "Restaurant", "2023-01-12", 32000, 2)
    ]
    cursor.executemany(
        "INSERT INTO staff (first_name, last_name, role, department, hire_date, salary, manager_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        staff
    )
    
    # Insert sample inventory
    inventory = [
        ("Rice", "Grains", 500, "kg", 100, "Local Suppliers Inc", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Chicken Breast", "Meat", 50, "kg", 10, "Fresh Farms Co", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Tomatoes", "Vegetables", 30, "kg", 5, "Garden Fresh Ltd", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Olive Oil", "Condiments", 20, "liters", 5, "Mediterranean Imports", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Bed Linens", "Hotel Supplies", 100, "sets", 20, "Hospitality Wholesale", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Car Air Freshener", "Car Supplies", 200, "units", 50, "Auto Parts Plus", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ]
    cursor.executemany(
        "INSERT INTO inventory (item_name, category, quantity, unit, reorder_level, supplier, last_updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
        inventory
    )
    
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at {db_path}")
    print("Tables created: customers, restaurants, menu_items, restaurant_orders, order_items, hotels, hotel_bookings, cars, car_rentals, payments, reviews, promotions, customer_promotions, staff, inventory")
    print("Sample data inserted successfully!")


if __name__ == "__main__":
    setup_database()
