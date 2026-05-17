"""Database schema definitions for the business database."""

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

# Schema metadata for LLM context
SCHEMA_METADATA = {
    "customers": {
        "description": "Customer information including contact details and loyalty status",
        "columns": ["customer_id", "first_name", "last_name", "email", "phone", "registration_date", "loyalty_points", "customer_tier"]
    },
    "restaurants": {
        "description": "Restaurant details including cuisine type and location",
        "columns": ["restaurant_id", "name", "cuisine_type", "location", "phone", "rating", "price_range"]
    },
    "menu_items": {
        "description": "Menu items with dietary information including vegetarian options",
        "columns": ["item_id", "restaurant_id", "name", "description", "price", "is_vegetarian", "is_vegan", "is_gluten_free", "category"]
    },
    "restaurant_orders": {
        "description": "Restaurant orders with customer, restaurant, and order details",
        "columns": ["order_id", "customer_id", "restaurant_id", "order_date", "total_amount", "status", "delivery_address", "payment_method"]
    },
    "order_items": {
        "description": "Individual items within restaurant orders linking to menu items",
        "columns": ["order_item_id", "order_id", "item_id", "quantity", "unit_price", "special_instructions"]
    },
    "hotels": {
        "description": "Hotel information including ratings and amenities",
        "columns": ["hotel_id", "name", "location", "star_rating", "phone", "amenities"]
    },
    "hotel_bookings": {
        "description": "Hotel booking reservations with dates and pricing",
        "columns": ["booking_id", "customer_id", "hotel_id", "check_in_date", "check_out_date", "room_type", "num_guests", "total_price", "status", "booking_date"]
    },
    "cars": {
        "description": "Car fleet information including availability and rates",
        "columns": ["car_id", "make", "model", "year", "color", "license_plate", "daily_rate", "availability_status", "car_type"]
    },
    "car_rentals": {
        "description": "Car rental transactions with dates and costs",
        "columns": ["rental_id", "customer_id", "car_id", "rental_start_date", "rental_end_date", "actual_return_date", "total_cost", "status", "pickup_location", "dropoff_location"]
    },
    "payments": {
        "description": "Payment transactions across all services",
        "columns": ["payment_id", "customer_id", "amount", "payment_date", "payment_method", "status", "transaction_id", "related_booking_type", "related_booking_id"]
    },
    "reviews": {
        "description": "Customer reviews and ratings for services",
        "columns": ["review_id", "customer_id", "review_type", "related_id", "rating", "comment", "review_date", "is_verified"]
    },
    "promotions": {
        "description": "Promotional offers and discount codes",
        "columns": ["promotion_id", "code", "description", "discount_percentage", "discount_amount", "valid_from", "valid_until", "applicable_services", "min_purchase_amount", "is_active"]
    },
    "customer_promotions": {
        "description": "Customer-specific promotion usage tracking",
        "columns": ["customer_promotion_id", "customer_id", "promotion_id", "used_date", "is_used"]
    },
    "staff": {
        "description": "Employee information and organizational structure",
        "columns": ["staff_id", "first_name", "last_name", "role", "department", "hire_date", "salary", "manager_id"]
    },
    "inventory": {
        "description": "Inventory tracking for supplies and materials",
        "columns": ["inventory_id", "item_name", "category", "quantity", "unit", "reorder_level", "supplier", "last_updated"]
    }
}

# Intent mapping keywords
INTENT_KEYWORDS = {
    "vegetarian": ["restaurant_orders", "menu_items", "order_items"],
    "vegan": ["restaurant_orders", "menu_items", "order_items"],
    "food": ["restaurant_orders", "menu_items", "order_items", "restaurants"],
    "order": ["restaurant_orders", "order_items"],
    "booking": ["hotel_bookings"],
    "reservation": ["hotel_bookings", "restaurant_orders"],
    "rental": ["car_rentals", "cars"],
    "car": ["car_rentals", "cars"],
    "vehicle": ["car_rentals", "cars"],
    "payment": ["payments"],
    "review": ["reviews"],
    "rating": ["reviews", "restaurants", "hotels"],
    "customer": ["customers"],
    "promotion": ["promotions", "customer_promotions"],
    "discount": ["promotions", "customer_promotions"],
    "staff": ["staff"],
    "employee": ["staff"],
    "inventory": ["inventory"],
    "hotel": ["hotel_bookings", "hotels"],
    "restaurant": ["restaurant_orders", "restaurants", "menu_items", "order_items"]
}
