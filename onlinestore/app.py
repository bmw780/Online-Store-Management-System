from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'onlinestore_da3_secret'

# ── DB CONFIG ── change user/password to match your MySQL setup ──
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'marika',   # <-- change this
    'database': 'onlinestore'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query(sql, params=(), fetchone=False, commit=False):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    if commit:
        conn.commit()
        result = cur.lastrowid
    elif fetchone:
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# ════════════════════════════════════════════
#  HOME
# ════════════════════════════════════════════
@app.route('/')
def index():
    stats = {
        'customers': query('SELECT COUNT(*) as c FROM CUSTOMER', fetchone=True)['c'],
        'products':  query('SELECT COUNT(*) as c FROM PRODUCT', fetchone=True)['c'],
        'orders':    query('SELECT COUNT(*) as c FROM `ORDER`', fetchone=True)['c'],
        'revenue':   query('SELECT COALESCE(SUM(amount),0) as c FROM PAYMENT WHERE status="Paid"', fetchone=True)['c'],
    }
    recent_orders = query('''
        SELECT o.order_id, c.name as customer, o.total_amount, o.status, o.order_date
        FROM `ORDER` o JOIN CUSTOMER c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC LIMIT 5
    ''')
    return render_template('index.html', stats=stats, recent_orders=recent_orders)

# ════════════════════════════════════════════
#  CUSTOMERS
# ════════════════════════════════════════════
@app.route('/customers')
def customers():
    rows = query('''
        SELECT c.customer_id, c.name, c.email, c.created_at,
               GROUP_CONCAT(cp.phone SEPARATOR ', ') as phones
        FROM CUSTOMER c
        LEFT JOIN CUSTOMER_PHONE cp ON c.customer_id = cp.customer_id
        GROUP BY c.customer_id
        ORDER BY c.customer_id DESC
    ''')
    return render_template('customers.html', customers=rows)

@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if request.method == 'POST':
        name   = request.form['name'].strip()
        email  = request.form['email'].strip()
        phones = [p.strip() for p in request.form['phones'].split(',') if p.strip()]
        street = request.form['street'].strip()
        city   = request.form['city'].strip()
        state  = request.form['state'].strip()
        pincode= request.form['pincode'].strip()

        if not name or not email:
            flash('Name and email are required.', 'error')
            return redirect(url_for('add_customer'))
        try:
            cid = query('INSERT INTO CUSTOMER (name, email) VALUES (%s,%s)',
                        (name, email), commit=True)
            for ph in phones:
                query('INSERT INTO CUSTOMER_PHONE (customer_id, phone) VALUES (%s,%s)',
                      (cid, ph), commit=True)
            if street:
                query('INSERT INTO ADDRESS (customer_id,street,city,state,pincode) VALUES (%s,%s,%s,%s,%s)',
                      (cid, street, city, state, pincode), commit=True)
            flash(f'Customer "{name}" added successfully!', 'success')
            return redirect(url_for('customers'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('add_customer.html')

@app.route('/customers/delete/<int:cid>', methods=['POST'])
def delete_customer(cid):
    query('DELETE FROM CUSTOMER WHERE customer_id=%s', (cid,), commit=True)
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers'))

# ════════════════════════════════════════════
#  PRODUCTS
# ════════════════════════════════════════════
@app.route('/products')
def products():
    rows = query('''
        SELECT p.*, c.name as category_name,
               ROUND(p.price * 0.90, 2) as discount_price
        FROM PRODUCT p JOIN CATEGORY c ON p.category_id = c.category_id
        ORDER BY p.product_id DESC
    ''')
    return render_template('products.html', products=rows)

@app.route('/products/add', methods=['GET','POST'])
def add_product():
    categories = query('SELECT * FROM CATEGORY ORDER BY name')
    if request.method == 'POST':
        try:
            query('INSERT INTO PRODUCT (category_id,name,price,stock_qty) VALUES (%s,%s,%s,%s)',
                  (request.form['category_id'], request.form['name'],
                   request.form['price'], request.form['stock_qty']), commit=True)
            flash('Product added!', 'success')
            return redirect(url_for('products'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('add_product.html', categories=categories)

@app.route('/products/delete/<int:pid>', methods=['POST'])
def delete_product(pid):
    try:
        query('DELETE FROM PRODUCT WHERE product_id=%s', (pid,), commit=True)
        flash('Product deleted.', 'success')
    except Exception as e:
        flash(f'Cannot delete: {e}', 'error')
    return redirect(url_for('products'))

@app.route('/categories', methods=['GET','POST'])
def categories():
    if request.method == 'POST':
        name = request.form['name'].strip()
        desc = request.form['description'].strip()
        if name:
            try:
                query('INSERT INTO CATEGORY (name,description) VALUES (%s,%s)',
                      (name, desc), commit=True)
                flash('Category added!', 'success')
            except Exception as e:
                flash(f'Error: {e}', 'error')
        return redirect(url_for('categories'))
    rows = query('SELECT c.*, COUNT(p.product_id) as product_count FROM CATEGORY c LEFT JOIN PRODUCT p ON c.category_id=p.category_id GROUP BY c.category_id')
    return render_template('categories.html', categories=rows)

# ════════════════════════════════════════════
#  ORDERS
# ════════════════════════════════════════════
@app.route('/orders')
def orders():
    rows = query('''
        SELECT o.order_id, c.name as customer, o.total_amount, o.status,
               o.order_date, p.status as payment_status, s.status as ship_status
        FROM `ORDER` o
        JOIN CUSTOMER c ON o.customer_id=c.customer_id
        LEFT JOIN PAYMENT p ON o.order_id=p.order_id
        LEFT JOIN SHIPMENT s ON o.order_id=s.order_id
        ORDER BY o.order_date DESC
    ''')
    return render_template('orders.html', orders=rows)

@app.route('/orders/new', methods=['GET','POST'])
def new_order():
    customers_list = query('''
        SELECT c.customer_id, c.name, a.address_id,
               CONCAT(a.street,', ',a.city) as address
        FROM CUSTOMER c JOIN ADDRESS a ON c.customer_id=a.customer_id
        ORDER BY c.name
    ''')
    products_list  = query('SELECT * FROM PRODUCT WHERE stock_qty > 0 ORDER BY name')

    if request.method == 'POST':
        cid   = request.form['customer_id']
        aid   = request.form['address_id']
        pids  = request.form.getlist('product_id[]')
        qtys  = request.form.getlist('quantity[]')
        method= request.form['payment_method']

        if not pids:
            flash('Add at least one product.', 'error')
            return redirect(url_for('new_order'))
        try:
            conn = get_db()
            cur  = conn.cursor(dictionary=True)

            # Create order
            cur.execute('INSERT INTO `ORDER` (customer_id,address_id,status) VALUES (%s,%s,"Pending")', (cid, aid))
            oid = cur.lastrowid

            total = 0
            for pid, qty in zip(pids, qtys):
                qty = int(qty)
                cur.execute('SELECT price, stock_qty FROM PRODUCT WHERE product_id=%s FOR UPDATE', (pid,))
                prod = cur.fetchone()
                if prod['stock_qty'] < qty:
                    conn.rollback()
                    flash(f'Insufficient stock for product #{pid}.', 'error')
                    return redirect(url_for('new_order'))
                up = prod['price']
                total += up * qty
                cur.execute('INSERT INTO ORDER_ITEM (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)',
                            (oid, pid, qty, up))
                cur.execute('UPDATE PRODUCT SET stock_qty=stock_qty-%s WHERE product_id=%s', (qty, pid))

            cur.execute('UPDATE `ORDER` SET total_amount=%s WHERE order_id=%s', (total, oid))

            # Payment record
            cur.execute('INSERT INTO PAYMENT (order_id,method,amount,status,paid_at) VALUES (%s,%s,%s,"Paid",NOW())',
                        (oid, method, total))

            # Shipment record
            tracking = f"TRK{oid:05d}"
            cur.execute('INSERT INTO SHIPMENT (order_id,tracking_no,carrier,carrier_contact,status,estimated_delivery) VALUES (%s,%s,"BlueDart","1800-123-456","Processing", DATE_ADD(NOW(), INTERVAL 5 DAY))',
                        (oid, tracking))

            conn.commit()
            cur.close(); conn.close()
            flash(f'Order #{oid} placed successfully! Total: ₹{total:.2f}', 'success')
            return redirect(url_for('order_detail', oid=oid))
        except Exception as e:
            flash(f'Error placing order: {e}', 'error')

    return render_template('new_order.html', customers=customers_list, products=products_list)

@app.route('/orders/<int:oid>')
def order_detail(oid):
    order = query('''
        SELECT o.*, c.name as customer_name, c.email,
               a.street, a.city, a.state, a.pincode
        FROM `ORDER` o
        JOIN CUSTOMER c ON o.customer_id=c.customer_id
        JOIN ADDRESS a ON o.address_id=a.address_id
        WHERE o.order_id=%s
    ''', (oid,), fetchone=True)

    items = query('''
        SELECT oi.quantity, oi.unit_price,
               oi.quantity * oi.unit_price AS total_price,
               p.name as product_name
        FROM ORDER_ITEM oi JOIN PRODUCT p ON oi.product_id=p.product_id
        WHERE oi.order_id=%s
    ''', (oid,))

    payment  = query('SELECT * FROM PAYMENT WHERE order_id=%s',  (oid,), fetchone=True)
    shipment = query('SELECT * FROM SHIPMENT WHERE order_id=%s', (oid,), fetchone=True)

    return render_template('order_detail.html', order=order, items=items,
                           payment=payment, shipment=shipment)

@app.route('/orders/<int:oid>/status', methods=['POST'])
def update_order_status(oid):
    status = request.form['status']
    query('UPDATE `ORDER` SET status=%s WHERE order_id=%s', (status, oid), commit=True)
    if status == 'Delivered':
        query('UPDATE SHIPMENT SET status="Delivered" WHERE order_id=%s', (oid,), commit=True)
    flash(f'Order status updated to {status}.', 'success')
    return redirect(url_for('order_detail', oid=oid))

# ════════════════════════════════════════════
#  REPORTS
# ════════════════════════════════════════════
@app.route('/reports')
def reports():
    top_products = query('''
        SELECT p.name, SUM(oi.quantity) as units_sold,
               SUM(oi.quantity * oi.unit_price) as revenue
        FROM ORDER_ITEM oi JOIN PRODUCT p ON oi.product_id=p.product_id
        GROUP BY p.product_id ORDER BY revenue DESC LIMIT 5
    ''')
    by_status = query('''
        SELECT status, COUNT(*) as count, SUM(total_amount) as total
        FROM `ORDER` GROUP BY status
    ''')
    by_category = query('''
        SELECT c.name as category, COUNT(p.product_id) as products,
               SUM(p.stock_qty) as total_stock
        FROM CATEGORY c LEFT JOIN PRODUCT p ON c.category_id=p.category_id
        GROUP BY c.category_id
    ''')
    low_stock = query('SELECT * FROM PRODUCT WHERE stock_qty < 5 ORDER BY stock_qty')
    return render_template('reports.html', top_products=top_products,
                           by_status=by_status, by_category=by_category, low_stock=low_stock)

if __name__ == '__main__':
    app.run(debug=True)
