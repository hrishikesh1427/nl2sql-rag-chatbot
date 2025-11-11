-- seed/seed.sql
CREATE TABLE IF NOT EXISTS customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(200),
  signup_date DATE
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  amount DECIMAL(10,2),
  status VARCHAR(50),
  created_at DATETIME,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

INSERT INTO customers (name, email, signup_date) VALUES
('Alice','alice@example.com','2023-01-02'),
('Bob','bob@example.com','2023-02-10'),
('Carol','carol@example.com','2023-03-20');

INSERT INTO orders (customer_id, amount, status, created_at) VALUES
(1, 100.50, 'shipped', '2023-04-01 10:00:00'),
(2, 75.00, 'processing', '2023-05-03 12:34:00'),
(1, 49.99, 'delivered', '2023-06-21 09:10:00');
