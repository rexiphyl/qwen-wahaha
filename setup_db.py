"""
Database Initialization Script
Creates the restaurant_orders table and populates it with sample data.
"""
import sqlite3
import os

DB_PATH = "business_db.sqlite"

def init_db():
    # Remove existing DB to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create restaurant_orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        order_date DATE NOT NULL,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'pending'
    )
    """)

    # Insert sample data
    sample_data = [
        ("Alice Johnson", "2023-10-01", "Margherita Pizza", 2, 12.50, 25.00, "paid"),
        ("Bob Smith", "2023-10-01", "Caesar Salad", 1, 8.50, 8.50, "paid"),
        ("Charlie Brown", "2023-10-02", "Pepperoni Pizza", 1, 14.00, 14.00, "pending"),
        ("Diana Prince", "2023-10-02", "Lasagna", 2, 15.00, 30.00, "paid"),
        ("Evan Wright", "2023-10-03", "Garlic Bread", 3, 5.00, 15.00, "paid"),
        ("Fiona Green", "2023-10-03", "Tiramisu", 2, 7.50, 15.00, "pending"),
        ("George King", "2023-10-04", "Margherita Pizza", 1, 12.50, 12.50, "paid"),
        ("Hannah Lee", "2023-10-04", "Spaghetti Carbonara", 1, 13.00, 13.00, "paid"),
        ("Ian Scott", "2023-10-05", "Caesar Salad", 2, 8.50, 17.00, "pending"),
        ("Julia Roberts", "2023-10-05", "Pepperoni Pizza", 2, 14.00, 28.00, "paid"),
    ]

    cursor.executemany("""
    INSERT INTO restaurant_orders (customer_name, order_date, item_name, quantity, price, total_amount, payment_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_data)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")
    print("Table 'restaurant_orders' created with 10 sample records.")

if __name__ == "__main__":
    init_db()
