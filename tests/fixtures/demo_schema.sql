CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    amount INTEGER NOT NULL
);
INSERT INTO customers(customer_id, customer_name) VALUES
    (1, 'Ada'), (2, 'Ben'), (3, 'Cara');
INSERT INTO orders(order_id, customer_id, amount) VALUES
    (101, 1, 120), (102, 1, 80), (103, 2, 140);
