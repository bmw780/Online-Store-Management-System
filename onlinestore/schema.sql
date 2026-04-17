-- Online Store Management System
-- DA2 Final Normalized Schema (BCNF)
-- Run this in MySQL Workbench or MySQL CLI before starting the app

CREATE DATABASE IF NOT EXISTS onlinestore;
USE onlinestore;

CREATE TABLE CUSTOMER (
    customer_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id)
);

CREATE TABLE CUSTOMER_PHONE (
    phone_id INT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL,
    phone VARCHAR(15) NOT NULL,
    PRIMARY KEY (phone_id),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ADDRESS (
    address_id INT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL,
    street VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    PRIMARY KEY (address_id),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE CATEGORY (
    category_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    PRIMARY KEY (category_id)
);

CREATE TABLE PRODUCT (
    product_id INT NOT NULL AUTO_INCREMENT,
    category_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_qty INT NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
    PRIMARY KEY (product_id),
    FOREIGN KEY (category_id) REFERENCES CATEGORY(category_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE `ORDER` (
    order_id INT NOT NULL AUTO_INCREMENT,
    customer_id INT NOT NULL,
    address_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (address_id) REFERENCES ADDRESS(address_id) ON DELETE RESTRICT
);

CREATE TABLE ORDER_ITEM (
    item_id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (item_id),
    FOREIGN KEY (order_id) REFERENCES `ORDER`(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES PRODUCT(product_id) ON DELETE RESTRICT
);

CREATE TABLE PAYMENT (
    payment_id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL UNIQUE,
    method VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    paid_at DATETIME,
    PRIMARY KEY (payment_id),
    FOREIGN KEY (order_id) REFERENCES `ORDER`(order_id) ON DELETE CASCADE
);

CREATE TABLE SHIPMENT (
    shipment_id INT NOT NULL AUTO_INCREMENT,
    order_id INT NOT NULL UNIQUE,
    tracking_no VARCHAR(100),
    carrier VARCHAR(100),
    carrier_contact VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'Processing',
    estimated_delivery DATE,
    PRIMARY KEY (shipment_id),
    FOREIGN KEY (order_id) REFERENCES `ORDER`(order_id) ON DELETE CASCADE
);

-- Sample seed data
INSERT INTO CATEGORY (name, description) VALUES
('Electronics', 'Phones, laptops, accessories'),
('Clothing', 'Men and women apparel'),
('Books', 'Academic and fiction');

INSERT INTO PRODUCT (category_id, name, price, stock_qty) VALUES
(1, 'Wireless Earbuds', 1499.00, 50),
(1, 'USB-C Hub', 899.00, 30),
(2, 'Cotton T-Shirt', 399.00, 100),
(3, 'DBMS Textbook', 549.00, 20);

INSERT INTO CUSTOMER (name, email) VALUES
('Arjun Kumar', 'arjun@mail.com'),
('Meena Iyer', 'meena@mail.com');

INSERT INTO CUSTOMER_PHONE (customer_id, phone) VALUES
(1, '9876543210'), (1, '9123456789'), (2, '8800112233');

INSERT INTO ADDRESS (customer_id, street, city, state, pincode) VALUES
(1, '12 Anna Nagar', 'Chennai', 'Tamil Nadu', '600040'),
(2, '5 MG Road', 'Bangalore', 'Karnataka', '560001');
