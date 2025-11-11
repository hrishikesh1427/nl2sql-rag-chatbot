import os
import random
from datetime import datetime, timedelta
from faker import Faker
import pymysql
from dotenv import load_dotenv
import time 
load_dotenv()
fake = Faker()
HOST = os.getenv("DB_HOST", "127.0.0.1")
PORT = int(os.getenv("DB_PORT", "3307"))
USER = os.getenv("DB_USER", "demo_user")
PASSWORD = os.getenv("DB_PASS", "demo_pass")
DB_NAME = os.getenv("DB_NAME", "demo_db")

# Try connecting multiple times if MySQL is still starting up
for i in range(10):
    try:
        conn = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            autocommit=True
        )
        print("✅ Connected to MySQL!")
        break
    except Exception as e:
        print(f"⏳ Attempt {i+1}/10: MySQL not ready yet -> {e}")
        time.sleep(5)
else:
    raise RuntimeError("❌ Could not connect to MySQL after several retries.")

cursor = conn.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
cursor.execute(f"USE {DB_NAME}")
print(f"📦 Using database: {DB_NAME}")
# # Step 1: Create database
# cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
# cursor.execute(f"USE {DB_NAME}")

# Step 2: Define schema
tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        location VARCHAR(100)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        hire_date DATE,
        department_id INT,
        salary DECIMAL(10,2),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        join_date DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        category VARCHAR(50),
        price DECIMAL(10,2),
        stock INT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        employee_id INT,
        order_date DATE,
        total_amount DECIMAL(10,2),
        status VARCHAR(50),
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT,
        product_id INT,
        quantity INT,
        price DECIMAL(10,2),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS suppliers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        contact_email VARCHAR(100),
        phone VARCHAR(50)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT,
        supplier_id INT,
        received_date DATE,
        quantity INT,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        order_id INT,
        payment_date DATE,
        amount DECIMAL(10,2),
        method VARCHAR(50),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        product_id INT,
        rating INT,
        comment TEXT,
        review_date DATE,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """
]

for sql in tables_sql:
    cursor.execute(sql)
print("✅ Tables created successfully!")

# Step 3: Populate data
def seed_departments(n=10):
    for _ in range(n):
        cursor.execute("INSERT INTO departments (name, location) VALUES (%s, %s)", 
                       (fake.company(), fake.city()))
    print(f"Inserted {n} departments")

def seed_employees(n=200):
    dept_ids = [i+1 for i in range(10)]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO employees (name, email, hire_date, department_id, salary)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.email(),
            fake.date_between(start_date="-10y", end_date="today"),
            random.choice(dept_ids),
            round(random.uniform(40000, 120000), 2)
        ))
    print(f"Inserted {n} employees")

def seed_customers(n=1000):
    for _ in range(n):
        cursor.execute("INSERT INTO customers (name, email, join_date) VALUES (%s, %s, %s)",
                       (fake.name(), fake.email(), fake.date_between(start_date="-3y", end_date="today")))
    print(f"Inserted {n} customers")

def seed_products(n=500):
    categories = ["Electronics", "Clothing", "Home", "Books", "Sports"]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO products (name, category, price, stock)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.word().capitalize(),
            random.choice(categories),
            round(random.uniform(10, 5000), 2),
            random.randint(1, 500)
        ))
    print(f"Inserted {n} products")

def seed_suppliers(n=50):
    for _ in range(n):
        cursor.execute("INSERT INTO suppliers (name, contact_email, phone) VALUES (%s, %s, %s)",
                       (fake.company(), fake.email(), fake.phone_number()))
    print(f"Inserted {n} suppliers")

def seed_orders(n=2000):
    customer_ids = [i+1 for i in range(1000)]
    employee_ids = [i+1 for i in range(200)]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO orders (customer_id, employee_id, order_date, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            random.choice(customer_ids),
            random.choice(employee_ids),
            fake.date_between(start_date="-3y", end_date="today"),
            round(random.uniform(50, 5000), 2),
            random.choice(["pending", "shipped", "delivered", "cancelled"])
        ))
    print(f"Inserted {n} orders")
def seed_inventory(n=500):
    product_ids = [i+1 for i in range(500)]
    supplier_ids = [i+1 for i in range(50)]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO inventory (product_id, supplier_id, received_date, quantity)
            VALUES (%s, %s, %s, %s)
        """, (
            random.choice(product_ids),
            random.choice(supplier_ids),
            fake.date_between(start_date="-1y", end_date="today"),  # random within last 1 year
            random.randint(1, 100)
        ))
    print(f"Inserted {n} inventory rows")
def seed_order_items(n=5000):
    order_ids = [i + 1 for i in range(2000)]
    product_ids = [i + 1 for i in range(500)]

    for _ in range(n):
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (
            random.choice(order_ids),
            random.choice(product_ids),
            random.randint(1, 10),
            round(random.uniform(10, 5000), 2)
        ))
    print(f"Inserted {n} order_items")
def seed_payments(n=2000):
    order_ids = [i + 1 for i in range(2000)]
    for _ in range(n):
        cursor.execute("""
            INSERT INTO payments (order_id, payment_date, amount, method)
            VALUES (%s, %s, %s, %s)
        """, (
            random.choice(order_ids),
            fake.date_between(start_date="-2y", end_date="today"),
            round(random.uniform(50, 5000), 2),
            random.choice(["credit_card", "paypal", "cash", "bank_transfer"])
        ))
    print(f"Inserted {n} payments")

# Run seeding in order
seed_departments()
seed_employees()
seed_customers()
seed_products()
seed_suppliers()
seed_orders()
seed_inventory()
seed_order_items()
seed_payments()
print("🎉 Complex fake enterprise DB generated successfully!")
cursor.close()
conn.close()
