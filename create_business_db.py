#!/usr/bin/env python3
"""
SQLite Database Creator for Hotel, Restaurant, and Car Rental Businesses
This script creates a comprehensive database with multiple related tables
and populates them with dummy data.
"""

import sqlite3
from datetime import datetime, timedelta
import random

def create_database(db_name="business_db.sqlite"):
    """Create the database and all required tables."""
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # ==================== COMMON TABLES ====================
    
    # 1. Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            city TEXT,
            country TEXT,
            postal_code TEXT,
            registration_date DATE DEFAULT CURRENT_DATE,
            loyalty_points INTEGER DEFAULT 0
        )
    """)
    
    # 2. Employees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            position TEXT NOT NULL,
            department TEXT,
            hire_date DATE,
            salary REAL,
            manager_id INTEGER,
            FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
        )
    """)
    
    # ==================== HOTEL TABLES ====================
    
    # 3. Hotels Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotels (
            hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_name TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            star_rating INTEGER CHECK(star_rating BETWEEN 1 AND 5),
            total_rooms INTEGER,
            phone TEXT,
            email TEXT,
            amenities TEXT,
            check_in_time TIME DEFAULT '14:00',
            check_out_time TIME DEFAULT '11:00'
        )
    """)
    
    # 4. Room Types Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_types (
            room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT NOT NULL,
            description TEXT,
            max_occupancy INTEGER,
            base_price REAL NOT NULL,
            bed_type TEXT,
            room_size_sqft INTEGER
        )
    """)
    
    # 5. Hotel Rooms Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hotel_id INTEGER NOT NULL,
            room_type_id INTEGER NOT NULL,
            room_number TEXT NOT NULL,
            floor INTEGER,
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'occupied', 'maintenance', 'reserved')),
            view_type TEXT,
            FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),
            FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id),
            UNIQUE(hotel_id, room_number)
        )
    """)
    
    # 6. Hotel Bookings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            num_guests INTEGER,
            total_price REAL,
            booking_status TEXT DEFAULT 'confirmed' CHECK(booking_status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show')),
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            special_requests TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (room_id) REFERENCES hotel_rooms(room_id)
        )
    """)
    
    # 7. Hotel Services Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            service_type TEXT CHECK(service_type IN ('room_service', 'spa', 'gym', 'pool', 'parking', 'laundry', 'other'))
        )
    """)
    
    # 8. Hotel Service Usage Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hotel_service_usage (
            usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            quantity INTEGER DEFAULT 1,
            total_charge REAL,
            FOREIGN KEY (booking_id) REFERENCES hotel_bookings(booking_id),
            FOREIGN KEY (service_id) REFERENCES hotel_services(service_id)
        )
    """)
    
    # ==================== RESTAURANT TABLES ====================
    
    # 9. Restaurants Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_name TEXT NOT NULL,
            cuisine_type TEXT,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            rating REAL CHECK(rating BETWEEN 0 AND 5),
            price_range TEXT CHECK(price_range IN ('$','$$','$$$','$$$$')),
            seating_capacity INTEGER,
            opening_hours TEXT
        )
    """)
    
    # 10. Menu Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            description TEXT,
            display_order INTEGER
        )
    """)
    
    # 11. Menu Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            category_id INTEGER,
            item_name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            is_available INTEGER DEFAULT 1,
            preparation_time_minutes INTEGER,
            calories INTEGER,
            is_vegetarian INTEGER DEFAULT 0,
            is_spicy INTEGER DEFAULT 0,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id),
            FOREIGN KEY (category_id) REFERENCES menu_categories(category_id)
        )
    """)
    
    # 12. Restaurant Reservations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            reservation_date DATE NOT NULL,
            reservation_time TIME NOT NULL,
            party_size INTEGER NOT NULL,
            table_number TEXT,
            status TEXT DEFAULT 'confirmed' CHECK(status IN ('confirmed', 'seated', 'completed', 'cancelled', 'no_show')),
            special_requests TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
        )
    """)
    
    # 13. Restaurant Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reservation_id INTEGER,
            customer_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            table_number TEXT,
            order_status TEXT DEFAULT 'pending' CHECK(order_status IN ('pending', 'preparing', 'served', 'completed', 'cancelled')),
            subtotal REAL,
            tax REAL,
            total_amount REAL,
            payment_method TEXT,
            FOREIGN KEY (reservation_id) REFERENCES restaurant_reservations(reservation_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # 14. Order Details Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_details (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            special_instructions TEXT,
            FOREIGN KEY (order_id) REFERENCES restaurant_orders(order_id),
            FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
        )
    """)
    
    # ==================== CAR RENTAL TABLES ====================
    
    # 15. Car Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            description TEXT,
            base_daily_rate REAL NOT NULL,
            passenger_capacity INTEGER,
            luggage_capacity INTEGER
        )
    """)
    
    # 16. Cars Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            car_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            color TEXT,
            license_plate TEXT UNIQUE NOT NULL,
            vin TEXT UNIQUE,
            mileage INTEGER DEFAULT 0,
            fuel_type TEXT CHECK(fuel_type IN ('petrol', 'diesel', 'electric', 'hybrid')),
            transmission TEXT CHECK(transmission IN ('automatic', 'manual')),
            daily_rate REAL,
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'rented', 'maintenance', 'reserved')),
            location TEXT,
            FOREIGN KEY (category_id) REFERENCES car_categories(category_id)
        )
    """)
    
    # 17. Car Rentals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_rentals (
            rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            pickup_date DATE NOT NULL,
            return_date DATE NOT NULL,
            pickup_location TEXT,
            return_location TEXT,
            pickup_mileage INTEGER,
            return_mileage INTEGER,
            daily_rate REAL,
            total_days INTEGER,
            subtotal REAL,
            insurance_fee REAL,
            additional_fees REAL,
            total_amount REAL,
            rental_status TEXT DEFAULT 'active' CHECK(rental_status IN ('active', 'completed', 'cancelled', 'overdue')),
            payment_status TEXT DEFAULT 'pending' CHECK(payment_status IN ('pending', 'paid', 'refunded')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (car_id) REFERENCES cars(car_id)
        )
    """)
    
    # 18. Insurance Options Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insurance_options (
            insurance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            insurance_name TEXT NOT NULL,
            description TEXT,
            daily_rate REAL NOT NULL,
            coverage_amount REAL,
            is_mandatory INTEGER DEFAULT 0
        )
    """)
    
    # 19. Rental Insurance Table (Junction Table)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rental_insurance (
            rental_insurance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            insurance_id INTEGER NOT NULL,
            added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cost REAL,
            FOREIGN KEY (rental_id) REFERENCES car_rentals(rental_id),
            FOREIGN KEY (insurance_id) REFERENCES insurance_options(insurance_id)
        )
    """)
    
    # 20. Additional Services Table (for car rentals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_additional_services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            description TEXT,
            daily_rate REAL,
            one_time_fee REAL,
            service_type TEXT CHECK(service_type IN ('gps', 'child_seat', 'additional_driver', 'wifi', 'ski_rack', 'other'))
        )
    """)
    
    # 21. Rental Additional Services Table (Junction)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rental_additional_services (
            rental_service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            total_cost REAL,
            FOREIGN KEY (rental_id) REFERENCES car_rentals(rental_id),
            FOREIGN KEY (service_id) REFERENCES car_additional_services(service_id)
        )
    """)
    
    # 22. Payments Table (Common for all businesses)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            payment_method TEXT CHECK(payment_method IN ('credit_card', 'debit_card', 'cash', 'bank_transfer', 'digital_wallet')),
            payment_status TEXT DEFAULT 'completed' CHECK(payment_status IN ('pending', 'completed', 'failed', 'refunded')),
            reference_number TEXT,
            booking_type TEXT CHECK(booking_type IN ('hotel', 'restaurant', 'car_rental')),
            booking_id INTEGER,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    # 23. Reviews Table (Common for all businesses)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            business_type TEXT CHECK(business_type IN ('hotel', 'restaurant', 'car_rental')),
            business_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            title TEXT,
            comment TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_verified INTEGER DEFAULT 1,
            helpful_count INTEGER DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)
    
    conn.commit()
    return conn, cursor


def insert_dummy_data(conn, cursor):
    """Insert dummy data into all tables."""
    
    # ==================== CUSTOMERS ====================
    customers_data = [
        ('John', 'Smith', 'john.smith@email.com', '+1-555-0101', '123 Main St', 'New York', 'USA', '10001', '2024-01-15', 500),
        ('Emma', 'Johnson', 'emma.j@email.com', '+1-555-0102', '456 Oak Ave', 'Los Angeles', 'USA', '90001', '2024-02-20', 750),
        ('Michael', 'Brown', 'm.brown@email.com', '+44-20-5550103', '789 High St', 'London', 'UK', 'SW1A 1AA', '2024-03-10', 300),
        ('Sophie', 'Williams', 'sophie.w@email.com', '+33-1-5550104', '321 Rue de Paris', 'Paris', 'France', '75001', '2024-04-05', 1200),
        ('David', 'Garcia', 'd.garcia@email.com', '+34-91-5550105', '654 Gran Via', 'Madrid', 'Spain', '28001', '2024-05-12', 450)
    ]
    cursor.executemany("""
        INSERT INTO customers (first_name, last_name, email, phone, address, city, country, postal_code, registration_date, loyalty_points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, customers_data)
    
    # ==================== EMPLOYEES ====================
    employees_data = [
        ('Alice', 'Martinez', 'alice.m@business.com', '+1-555-0201', 'Manager', 'Operations', '2022-01-10', 75000, None),
        ('Bob', 'Wilson', 'bob.w@business.com', '+1-555-0202', 'Receptionist', 'Front Desk', '2023-03-15', 45000, 1),
        ('Carol', 'Davis', 'carol.d@business.com', '+1-555-0203', 'Chef', 'Kitchen', '2021-06-20', 65000, 1),
        ('Daniel', 'Miller', 'daniel.m@business.com', '+1-555-0204', 'Driver', 'Transport', '2023-08-01', 50000, 1),
        ('Eva', 'Anderson', 'eva.a@business.com', '+1-555-0205', 'Housekeeping Supervisor', 'Maintenance', '2022-11-05', 55000, 1)
    ]
    cursor.executemany("""
        INSERT INTO employees (first_name, last_name, email, phone, position, department, hire_date, salary, manager_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees_data)
    
    # ==================== HOTELS ====================
    hotels_data = [
        ('Grand Plaza Hotel', '100 Luxury Lane', 'New York', 'USA', 5, 200, '+1-555-1001', 'info@grandplaza.com', 'Pool, Spa, Gym, Restaurant, Bar', '15:00', '11:00'),
        ('Seaside Resort', '200 Beach Road', 'Miami', 'USA', 4, 150, '+1-555-1002', 'contact@seasideresort.com', 'Pool, Beach Access, Restaurant', '14:00', '10:00'),
        ('Mountain View Lodge', '300 Alpine Way', 'Denver', 'USA', 4, 100, '+1-555-1003', 'stay@mountainview.com', 'Spa, Gym, Ski Storage', '16:00', '11:00'),
        ('City Center Inn', '400 Downtown Blvd', 'Chicago', 'USA', 3, 80, '+1-555-1004', 'hello@citycenter.com', 'Gym, Business Center', '14:00', '12:00')
    ]
    cursor.executemany("""
        INSERT INTO hotels (hotel_name, address, city, country, star_rating, total_rooms, phone, email, amenities, check_in_time, check_out_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, hotels_data)
    
    # ==================== ROOM TYPES ====================
    room_types_data = [
        ('Standard Room', 'Comfortable room with essential amenities', 2, 120.00, 'Queen', 300),
        ('Deluxe Room', 'Spacious room with city view', 2, 180.00, 'King', 400),
        ('Executive Suite', 'Large suite with separate living area', 4, 350.00, 'King', 650),
        ('Presidential Suite', 'Ultimate luxury with panoramic views', 6, 800.00, 'King', 1200),
        ('Family Room', 'Perfect for families with children', 5, 220.00, '2 Queens', 500)
    ]
    cursor.executemany("""
        INSERT INTO room_types (type_name, description, max_occupancy, base_price, bed_type, room_size_sqft)
        VALUES (?, ?, ?, ?, ?, ?)
    """, room_types_data)
    
    # ==================== HOTEL ROOMS ====================
    hotel_rooms_data = [
        (1, 1, '101', 1, 'available', 'City'),
        (1, 2, '102', 1, 'available', 'City'),
        (1, 3, '201', 2, 'occupied', 'Ocean'),
        (2, 1, '301', 3, 'available', 'Beach'),
        (2, 4, '302', 3, 'reserved', 'Beach'),
        (3, 2, '401', 4, 'available', 'Mountain'),
        (3, 5, '402', 4, 'maintenance', 'Mountain'),
        (4, 1, '501', 5, 'available', 'Downtown')
    ]
    cursor.executemany("""
        INSERT INTO hotel_rooms (hotel_id, room_type_id, room_number, floor, status, view_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, hotel_rooms_data)
    
    # ==================== HOTEL BOOKINGS ====================
    today = datetime.now()
    hotel_bookings_data = [
        (1, 1, (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=2)).strftime('%Y-%m-%d'), 2, 840.00, 'checked_in', 'Late checkout requested'),
        (2, 3, (today - timedelta(days=2)).strftime('%Y-%m-%d'), (today + timedelta(days=5)).strftime('%Y-%m-%d'), 2, 1260.00, 'checked_in', 'Honeymoon package'),
        (3, 5, (today + timedelta(days=10)).strftime('%Y-%m-%d'), (today + timedelta(days=15)).strftime('%Y-%m-%d'), 4, 1750.00, 'confirmed', 'Extra towels needed'),
        (4, 7, (today + timedelta(days=20)).strftime('%Y-%m-%d'), (today + timedelta(days=25)).strftime('%Y-%m-%d'), 2, 600.00, 'confirmed', None),
        (1, 2, (today - timedelta(days=30)).strftime('%Y-%m-%d'), (today - timedelta(days=25)).strftime('%Y-%m-%d'), 1, 720.00, 'checked_out', None)
    ]
    cursor.executemany("""
        INSERT INTO hotel_bookings (customer_id, room_id, check_in_date, check_out_date, num_guests, total_price, booking_status, special_requests)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, hotel_bookings_data)
    
    # ==================== HOTEL SERVICES ====================
    hotel_services_data = [
        ('Room Service', '24/7 in-room dining', 25.00, 'room_service'),
        ('Spa Treatment', 'Relaxing massage and spa services', 150.00, 'spa'),
        ('Gym Access', 'Full access to fitness center', 0.00, 'gym'),
        ('Valet Parking', 'Secure valet parking service', 35.00, 'parking'),
        ('Laundry Service', 'Same-day laundry and dry cleaning', 20.00, 'laundry')
    ]
    cursor.executemany("""
        INSERT INTO hotel_services (service_name, description, price, service_type)
        VALUES (?, ?, ?, ?)
    """, hotel_services_data)
    
    # ==================== HOTEL SERVICE USAGE ====================
    hotel_service_usage_data = [
        (1, 1, (today - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'), 2, 50.00),
        (1, 4, (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 1, 35.00),
        (2, 2, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 1, 150.00),
        (2, 5, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 3, 60.00)
    ]
    cursor.executemany("""
        INSERT INTO hotel_service_usage (booking_id, service_id, usage_date, quantity, total_charge)
        VALUES (?, ?, ?, ?, ?)
    """, hotel_service_usage_data)
    
    # ==================== RESTAURANTS ====================
    restaurants_data = [
        ('The Golden Fork', 'Italian', '500 Food Street', 'New York', 'USA', '+1-555-2001', 'info@goldenfork.com', 4.5, '$$$', 120, '11:00-23:00'),
        ('Sakura Sushi', 'Japanese', '600 Ocean Drive', 'Los Angeles', 'USA', '+1-555-2002', 'contact@sakurasushi.com', 4.7, '$$$$', 80, '12:00-22:00'),
        ('Le Petit Bistro', 'French', '700 Charm Avenue', 'San Francisco', 'USA', '+1-555-2003', 'hello@lepetitbistro.com', 4.3, '$$', 60, '10:00-21:00'),
        ('Taco Fiesta', 'Mexican', '800 Spice Road', 'Austin', 'USA', '+1-555-2004', 'info@tacofiesta.com', 4.2, '$', 100, '11:00-00:00')
    ]
    cursor.executemany("""
        INSERT INTO restaurants (restaurant_name, cuisine_type, address, city, country, phone, email, rating, price_range, seating_capacity, opening_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, restaurants_data)
    
    # ==================== MENU CATEGORIES ====================
    menu_categories_data = [
        ('Appetizers', 'Start your meal right', 1),
        ('Main Course', 'Hearty main dishes', 2),
        ('Desserts', 'Sweet endings', 3),
        ('Beverages', 'Drinks and refreshments', 4),
        ('Specials', "Chef's special creations", 5)
    ]
    cursor.executemany("""
        INSERT INTO menu_categories (category_name, description, display_order)
        VALUES (?, ?, ?)
    """, menu_categories_data)
    
    # ==================== MENU ITEMS ====================
    menu_items_data = [
        (1, 1, 'Bruschetta', 'Toasted bread with tomatoes and basil', 12.00, 1, 10, 150, 1, 0),
        (1, 2, 'Spaghetti Carbonara', 'Classic Italian pasta with egg and bacon', 24.00, 1, 20, 650, 0, 0),
        (1, 3, 'Tiramisu', 'Traditional Italian dessert', 10.00, 1, 5, 400, 1, 0),
        (2, 1, 'Edamame', 'Steamed soybeans with sea salt', 8.00, 1, 5, 120, 1, 0),
        (2, 2, 'Salmon Sashimi', 'Fresh salmon slices', 32.00, 1, 15, 280, 0, 0),
        (2, 3, 'Mochi Ice Cream', 'Japanese rice cake with ice cream', 9.00, 1, 5, 200, 1, 0),
        (3, 2, 'Coq au Vin', 'Chicken braised in wine', 28.00, 1, 35, 550, 0, 0),
        (3, 3, 'Crème Brûlée', 'Vanilla custard with caramelized sugar', 12.00, 1, 10, 350, 1, 0),
        (4, 1, 'Guacamole & Chips', 'Fresh avocado dip with tortilla chips', 10.00, 1, 8, 300, 1, 0),
        (4, 2, 'Carne Asada Tacos', 'Grilled steak tacos with fresh salsa', 18.00, 1, 15, 450, 0, 1)
    ]
    cursor.executemany("""
        INSERT INTO menu_items (restaurant_id, category_id, item_name, description, price, is_available, preparation_time_minutes, calories, is_vegetarian, is_spicy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, menu_items_data)
    
    # ==================== RESTAURANT RESERVATIONS ====================
    restaurant_reservations_data = [
        (1, 1, (today + timedelta(days=2)).strftime('%Y-%m-%d'), '19:00', 4, 'T1', 'confirmed', 'Window seat preferred', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (2, 2, (today + timedelta(days=5)).strftime('%Y-%m-%d'), '20:00', 2, 'T5', 'confirmed', 'Anniversary dinner', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (3, 3, (today - timedelta(days=3)).strftime('%Y-%m-%d'), '18:30', 6, 'T10', 'completed', 'Birthday celebration', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (4, 4, (today + timedelta(days=1)).strftime('%Y-%m-%d'), '12:30', 3, 'T3', 'confirmed', None, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (1, 2, (today - timedelta(days=10)).strftime('%Y-%m-%d'), '19:30', 2, 'T8', 'completed', None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    cursor.executemany("""
        INSERT INTO restaurant_reservations (customer_id, restaurant_id, reservation_date, reservation_time, party_size, table_number, status, special_requests, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, restaurant_reservations_data)
    
    # ==================== RESTAURANT ORDERS ====================
    restaurant_orders_data = [
        (3, 3, (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 'T10', 'completed', 85.00, 7.65, 92.65, 'credit_card'),
        (5, 1, (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 'T8', 'completed', 56.00, 5.04, 61.04, 'debit_card'),
        (None, 2, (today - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), 'T12', 'completed', 120.00, 10.80, 130.80, 'credit_card'),
        (None, 4, (today - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 'T5', 'completed', 45.00, 4.05, 49.05, 'cash')
    ]
    cursor.executemany("""
        INSERT INTO restaurant_orders (reservation_id, customer_id, order_date, table_number, order_status, subtotal, tax, total_amount, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, restaurant_orders_data)
    
    # ==================== ORDER DETAILS ====================
    order_details_data = [
        (1, 7, 2, 28.00, 'No onions'),
        (1, 8, 2, 12.00, None),
        (1, 4, 1, 8.00, None),
        (2, 1, 2, 12.00, None),
        (2, 2, 1, 24.00, 'Extra cheese'),
        (2, 3, 2, 10.00, None),
        (3, 5, 2, 32.00, 'Wasabi on side'),
        (3, 6, 2, 9.00, None),
        (4, 9, 1, 10.00, 'Extra spicy'),
        (4, 10, 2, 18.00, None)
    ]
    cursor.executemany("""
        INSERT INTO order_details (order_id, item_id, quantity, unit_price, special_instructions)
        VALUES (?, ?, ?, ?, ?)
    """, order_details_data)
    
    # ==================== CAR CATEGORIES ====================
    car_categories_data = [
        ('Economy', 'Compact and fuel-efficient', 45.00, 5, 2),
        ('Midsize', 'Comfortable for small families', 65.00, 5, 3),
        ('Luxury', 'Premium vehicles with extra features', 150.00, 5, 3),
        ('SUV', 'Spacious sport utility vehicles', 95.00, 7, 5),
        ('Convertible', 'Open-top driving experience', 120.00, 4, 2)
    ]
    cursor.executemany("""
        INSERT INTO car_categories (category_name, description, base_daily_rate, passenger_capacity, luggage_capacity)
        VALUES (?, ?, ?, ?, ?)
    """, car_categories_data)
    
    # ==================== CARS ====================
    cars_data = [
        (1, 'Toyota', 'Corolla', 2023, 'Silver', 'ABC-1234', 'TOY123456789', 15000, 'hybrid', 'automatic', 45.00, 'available', 'New York'),
        (1, 'Honda', 'Civic', 2023, 'Blue', 'DEF-5678', 'HON987654321', 12000, 'petrol', 'automatic', 50.00, 'available', 'Los Angeles'),
        (2, 'Nissan', 'Altima', 2022, 'Black', 'GHI-9012', 'NIS456789123', 25000, 'petrol', 'automatic', 65.00, 'rented', 'Chicago'),
        (3, 'BMW', '5 Series', 2024, 'White', 'JKL-3456', 'BMW789123456', 5000, 'petrol', 'automatic', 150.00, 'available', 'Miami'),
        (3, 'Mercedes', 'E-Class', 2024, 'Gray', 'MNO-7890', 'MER321654987', 3000, 'hybrid', 'automatic', 165.00, 'available', 'San Francisco'),
        (4, 'Ford', 'Explorer', 2023, 'Red', 'PQR-1234', 'FOR147258369', 20000, 'petrol', 'automatic', 95.00, 'maintenance', 'Denver'),
        (4, 'Chevrolet', 'Tahoe', 2023, 'Black', 'STU-5678', 'CHE963852741', 18000, 'diesel', 'automatic', 110.00, 'available', 'Houston'),
        (5, 'Ford', 'Mustang', 2024, 'Yellow', 'VWX-9012', 'FOR852963741', 2000, 'petrol', 'manual', 120.00, 'available', 'Las Vegas')
    ]
    cursor.executemany("""
        INSERT INTO cars (category_id, make, model, year, color, license_plate, vin, mileage, fuel_type, transmission, daily_rate, status, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cars_data)
    
    # ==================== CAR RENTALS ====================
    car_rentals_data = [
        (1, 1, (today - timedelta(days=10)).strftime('%Y-%m-%d'), (today - timedelta(days=3)).strftime('%Y-%m-%d'), 'New York Airport', 'New York Airport', 15000, 15450, 45.00, 7, 315.00, 50.00, 25.00, 390.00, 'completed', 'paid', (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')),
        (2, 3, (today - timedelta(days=5)).strftime('%Y-%m-%d'), (today + timedelta(days=5)).strftime('%Y-%m-%d'), 'O\'Hare Airport', 'O\'Hare Airport', 25000, None, 65.00, 10, 650.00, 80.00, 0.00, 730.00, 'active', 'paid', (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')),
        (3, 4, (today + timedelta(days=7)).strftime('%Y-%m-%d'), (today + timedelta(days=14)).strftime('%Y-%m-%d'), 'Miami Airport', 'Miami Airport', None, None, 150.00, 7, 1050.00, 150.00, 50.00, 1250.00, 'active', 'pending', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        (4, 7, (today - timedelta(days=20)).strftime('%Y-%m-%d'), (today - timedelta(days=10)).strftime('%Y-%m-%d'), 'Houston Downtown', 'Houston Airport', 18000, 18800, 110.00, 10, 1100.00, 100.00, 75.00, 1275.00, 'completed', 'paid', (today - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')),
        (5, 8, (today + timedelta(days=30)).strftime('%Y-%m-%d'), (today + timedelta(days=35)).strftime('%Y-%m-%d'), 'Las Vegas Strip', 'Las Vegas Airport', None, None, 120.00, 5, 600.00, 75.00, 0.00, 675.00, 'active', 'pending', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    cursor.executemany("""
        INSERT INTO car_rentals (customer_id, car_id, pickup_date, return_date, pickup_location, return_location, pickup_mileage, return_mileage, daily_rate, total_days, subtotal, insurance_fee, additional_fees, total_amount, rental_status, payment_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, car_rentals_data)
    
    # ==================== INSURANCE OPTIONS ====================
    insurance_options_data = [
        ('Collision Damage Waiver', 'Reduces liability for vehicle damage', 25.00, 50000.00, 0),
        ('Liability Insurance', 'Third-party liability coverage', 20.00, 1000000.00, 1),
        ('Personal Accident Insurance', 'Coverage for driver and passengers', 15.00, 50000.00, 0),
        ('Theft Protection', 'Protection against vehicle theft', 18.00, 30000.00, 0),
        ('Roadside Assistance Plus', '24/7 emergency roadside help', 10.00, 5000.00, 0)
    ]
    cursor.executemany("""
        INSERT INTO insurance_options (insurance_name, description, daily_rate, coverage_amount, is_mandatory)
        VALUES (?, ?, ?, ?, ?)
    """, insurance_options_data)
    
    # ==================== RENTAL INSURANCE ====================
    rental_insurance_data = [
        (1, 1, (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 175.00),
        (1, 2, (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 140.00),
        (2, 2, (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 200.00),
        (2, 5, (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 100.00),
        (3, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 175.00),
        (3, 3, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 105.00),
        (4, 1, (today - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'), 250.00),
        (4, 2, (today - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S'), 200.00),
        (5, 2, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 100.00),
        (5, 4, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 90.00)
    ]
    cursor.executemany("""
        INSERT INTO rental_insurance (rental_id, insurance_id, added_date, cost)
        VALUES (?, ?, ?, ?)
    """, rental_insurance_data)
    
    # ==================== CAR ADDITIONAL SERVICES ====================
    car_additional_services_data = [
        ('GPS Navigation', 'Satellite navigation system', 12.00, None, 'gps'),
        ('Child Safety Seat', 'Safety seat for children', 8.00, None, 'child_seat'),
        ('Additional Driver', 'Add extra authorized driver', 15.00, 25.00, 'additional_driver'),
        ('Portable WiFi', 'Mobile internet hotspot', 10.00, None, 'wifi'),
        ('Ski Rack', 'Roof-mounted ski carrier', 20.00, None, 'ski_rack')
    ]
    cursor.executemany("""
        INSERT INTO car_additional_services (service_name, description, daily_rate, one_time_fee, service_type)
        VALUES (?, ?, ?, ?, ?)
    """, car_additional_services_data)
    
    # ==================== RENTAL ADDITIONAL SERVICES ====================
    rental_additional_services_data = [
        (1, 1, 7, 84.00),
        (1, 3, 1, 25.00),
        (2, 1, 10, 120.00),
        (2, 2, 10, 80.00),
        (3, 1, 7, 84.00),
        (3, 4, 7, 70.00),
        (4, 3, 1, 25.00),
        (5, 1, 5, 60.00),
        (5, 4, 5, 50.00)
    ]
    cursor.executemany("""
        INSERT INTO rental_additional_services (rental_id, service_id, quantity, total_cost)
        VALUES (?, ?, ?, ?)
    """, rental_additional_services_data)
    
    # ==================== PAYMENTS ====================
    payments_data = [
        (1, 390.00, (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 'credit_card', 'completed', 'PAY-HOT-001', 'hotel', 1, 'Hotel booking payment'),
        (2, 730.00, (today - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), 'debit_card', 'completed', 'PAY-CAR-001', 'car_rental', 2, 'Car rental payment'),
        (3, 92.65, (today - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), 'credit_card', 'completed', 'PAY-RES-001', 'restaurant', 1, 'Restaurant order payment'),
        (4, 1275.00, (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 'credit_card', 'completed', 'PAY-CAR-002', 'car_rental', 4, 'Car rental payment'),
        (5, 61.04, (today - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), 'debit_card', 'completed', 'PAY-RES-002', 'restaurant', 2, 'Restaurant order payment'),
        (1, 840.00, (today + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), 'credit_card', 'pending', 'PAY-HOT-002', 'hotel', 2, 'Pending hotel checkout'),
        (3, 1250.00, (today + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S'), 'credit_card', 'pending', 'PAY-CAR-003', 'car_rental', 3, 'Upcoming car rental')
    ]
    cursor.executemany("""
        INSERT INTO payments (customer_id, amount, payment_date, payment_method, payment_status, reference_number, booking_type, booking_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, payments_data)
    
    # ==================== REVIEWS ====================
    reviews_data = [
        (1, 'hotel', 1, 5, 'Excellent Stay', 'Amazing service and beautiful rooms. Will definitely come back!', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 12),
        (2, 'restaurant', 1, 4, 'Great Food', 'Delicious Italian cuisine. The carbonara was perfect.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 8),
        (3, 'car_rental', 1, 5, 'Smooth Experience', 'Easy pickup and return process. Car was clean and well-maintained.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 15),
        (4, 'hotel', 2, 4, 'Nice Beach Resort', 'Beautiful location right on the beach. Rooms could be updated.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 6),
        (5, 'restaurant', 2, 5, 'Best Sushi in Town', 'Fresh fish and excellent presentation. Worth every penny!', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 10),
        (1, 'car_rental', 3, 3, 'Good but Pricey', 'Car was nice but felt a bit overpriced for what we got.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 4),
        (2, 'hotel', 3, 5, 'Mountain Paradise', 'Stunning views and excellent spa facilities.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 9),
        (3, 'restaurant', 3, 4, 'Charming French Bistro', 'Authentic French cuisine in a cozy atmosphere.', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 7)
    ]
    cursor.executemany("""
        INSERT INTO reviews (customer_id, business_type, business_id, rating, title, comment, review_date, is_verified, helpful_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, reviews_data)
    
    conn.commit()
    print(f"Successfully inserted dummy data into all tables!")


def verify_data(cursor):
    """Verify that all tables have at least 4 records."""
    
    tables = [
        'customers', 'employees', 'hotels', 'room_types', 'hotel_rooms',
        'hotel_bookings', 'hotel_services', 'hotel_service_usage',
        'restaurants', 'menu_categories', 'menu_items', 'restaurant_reservations',
        'restaurant_orders', 'order_details', 'car_categories', 'cars',
        'car_rentals', 'insurance_options', 'rental_insurance',
        'car_additional_services', 'rental_additional_services',
        'payments', 'reviews'
    ]
    
    print("\n" + "="*60)
    print("DATA VERIFICATION REPORT")
    print("="*60)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "✓" if count >= 4 else "✗"
        print(f"{status} {table}: {count} records")
    
    print("="*60)


def main():
    """Main function to create database and populate with data."""
    
    db_name = "business_db.sqlite"
    
    print(f"Creating SQLite database: {db_name}")
    print("-"*60)
    
    # Create database and tables
    conn, cursor = create_database(db_name)
    print("✓ Database and tables created successfully!")
    
    # Insert dummy data
    print("\nInserting dummy data...")
    insert_dummy_data(conn, cursor)
    
    # Verify data
    verify_data(cursor)
    
    # Show summary statistics
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"Total Customers: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM hotels")
    print(f"Total Hotels: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM hotel_rooms")
    print(f"Total Hotel Rooms: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    print(f"Total Restaurants: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM menu_items")
    print(f"Total Menu Items: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM cars")
    print(f"Total Cars: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM car_rentals")
    print(f"Total Car Rentals: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM payments")
    print(f"Total Payments: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM reviews")
    print(f"Total Reviews: {cursor.fetchone()[0]}")
    
    print("="*60)
    print(f"\nDatabase '{db_name}' created successfully with 23 tables!")
    print("You can open it with any SQLite viewer or use Python to query it.")
    
    conn.close()


if __name__ == "__main__":
    main()
