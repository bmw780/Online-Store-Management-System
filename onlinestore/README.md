# Online Store Management System — DA3
Flask + MySQL | Database Systems Project

## Setup (step by step)

### 1. Install MySQL
Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
Remember the root password you set during install.

### 2. Install Python packages
Open terminal/command prompt and run:
```
pip install flask mysql-connector-python
```

### 3. Set up the database
Open MySQL Workbench (or the MySQL CLI) and run the schema.sql file:
- In Workbench: File → Open SQL Script → select schema.sql → click ⚡ (Execute)
- In CLI: mysql -u root -p < schema.sql

### 4. Configure your password
Open app.py and change line 16:
```python
'password': 'your_mysql_password',   # put your actual MySQL root password here
```

### 5. Run the app
```
cd onlinestore
python app.py
```
Open browser → http://127.0.0.1:5000

---

## What the app demonstrates

| Page | Operations |
|------|-----------|
| Dashboard | SELECT with JOINs, COUNT, SUM aggregates |
| Customers | INSERT into CUSTOMER + CUSTOMER_PHONE + ADDRESS (3 tables), DELETE CASCADE |
| Products | INSERT into PRODUCT, SELECT with JOIN to CATEGORY, computed discount_price |
| Categories | INSERT into CATEGORY |
| New Order | INSERT into ORDER, ORDER_ITEM, PAYMENT, SHIPMENT; UPDATE stock_qty |
| Order Detail | Multi-table SELECT JOIN, computed total_price per item, UPDATE status |
| Reports | GROUP BY, SUM, COUNT, GROUP_CONCAT |

## DA2 normalization visible in the app

- `discount_price` is NOT stored — computed live: `price * 0.90`
- `total_price` per order item is NOT stored — computed live: `quantity * unit_price`
- Phone numbers are in `CUSTOMER_PHONE` (separate table) — shown with GROUP_CONCAT
- `carrier_info` is split into `carrier` + `carrier_contact` (atomic columns)

## File structure
```
onlinestore/
├── app.py          ← Flask routes and DB logic
├── schema.sql      ← MySQL schema (run this first)
├── README.md       ← this file
└── templates/
    ├── base.html
    ├── index.html
    ├── customers.html
    ├── add_customer.html
    ├── products.html
    ├── add_product.html
    ├── categories.html
    ├── orders.html
    ├── new_order.html
    ├── order_detail.html
    └── reports.html
```
