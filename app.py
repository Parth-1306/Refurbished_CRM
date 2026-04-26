from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import random
import os
import urllib.parse
import socket
from functools import wraps

app = Flask(__name__)
app.secret_key = "roll37_crm_key_super_secret"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_db():
    config = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", "admin"),
        "database": os.environ.get("DB_NAME", "RefurbishedTech_CRM"),
        "port": int(os.environ.get("DB_PORT", 3306))
    }
    
    if os.environ.get("DB_USE_SSL", "false").lower() == "true":
        config["ssl_verify_cert"] = True
        config["ssl_verify_identity"] = True
        
    return mysql.connector.connect(**config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session.get('role') == 'customer':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['role'] = 'admin'
            session['username'] = user['Username']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    if role == 'customer':
        return redirect(url_for('customer_login'))
    return redirect(url_for('login'))

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        contact = request.form['contact']
        password = request.form['password']
        
        if password != 'customer':
            return render_template('customer_login.html', error="Invalid Password! Use 'customer'.")
            
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customers WHERE Contact = %s", (contact,))
        customer = cursor.fetchone()
        conn.close()
        
        if customer:
            session['logged_in'] = True
            session['role'] = 'customer'
            session['customer_id'] = customer['CustomerID']
            session['customer_name'] = customer['FullName']
            return redirect(url_for('customer_dashboard'))
        else:
            return render_template('customer_login.html', error="Customer account not found!")
    return render_template('customer_login.html')

@app.route('/customer_dashboard')
def customer_dashboard():
    if not session.get('logged_in') or session.get('role') != 'customer':
        return redirect(url_for('customer_login'))
        
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Devices WHERE OwnerID = %s ORDER BY DeviceID DESC", (session['customer_id'],))
    devices = cursor.fetchall()
    
    # Fetch Notifications (Interaction History)
    cursor.execute("""
        SELECT dl.*, d.Brand, d.Model, d.TicketID 
        FROM DeviceLogs dl
        JOIN Devices d ON dl.DeviceID = d.DeviceID
        WHERE d.OwnerID = %s
        ORDER BY dl.LogID DESC LIMIT 15
    """, (session['customer_id'],))
    notifications = cursor.fetchall()
    
    # Fetch Customer Complaints
    cursor.execute("""
        SELECT c.*, d.Brand, d.Model 
        FROM Complaints c
        JOIN Devices d ON c.DeviceID = d.DeviceID
        WHERE c.CustomerID = %s
        ORDER BY c.CreatedAt DESC
    """, (session['customer_id'],))
    complaints = cursor.fetchall()
    
    conn.close()
    
    return render_template('customer_dashboard.html', devices=devices, customer_name=session.get('customer_name'), notifications=notifications, complaints=complaints)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_device', methods=['POST'])
def add_device():
    name = request.form['cust_name']
    brand = request.form['brand']
    model = request.form['model']
    contact = request.form.get('contact', '')
    
    month_val = request.form.get('purchase_month')
    month_num = int(month_val) if month_val and month_val.isdigit() else 1
    
    year_val = request.form.get('purchase_year')
    purchase_year = year_val if year_val and year_val.isdigit() else '2026'
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    purchase_date_combined = f"{month_names[month_num - 1]} {purchase_year}"
    
    device_type = request.form.get('device_type', 'Smartphone')
    storage = request.form.get('storage', '')
    battery_val = request.form.get('battery')
    battery = int(battery_val) if battery_val and battery_val.isdigit() else 0
    condition = request.form.get('screen_condition', 'Good')

    base_price_input = request.form.get('base_price', '0')
    market_price = int(base_price_input) if base_price_input.isdigit() else 0

    # 1. Base Age Depreciation
    age = 2026 - int(purchase_year)
    if age <= 0: factor = 0.80
    elif age == 1: factor = 0.65
    elif age == 2: factor = 0.50
    elif age == 3: factor = 0.35
    else: factor = 0.20
         
    depreciated_base = market_price * factor

    # 2. Dynamic Penalties based on condition
    condition_penalties = {
        'Brand New': 0, 'Like New': 2, 'Excellent': 5, 'Good': 10,
        'Fair': 15, 'Average': 20, 'Heavily Used': 30,
        'Minor Crack': 40, 'Cracked': 50, 'Heavily Cracked': 65,
        'Broken': 80, 'Fully Damaged': 95
    }
    screen_penalty = condition_penalties.get(condition, 10)

    if battery <= 300: bat_penalty = 0
    elif battery <= 500: bat_penalty = 5
    elif battery <= 800: bat_penalty = 12
    else: bat_penalty = 20
    
    scratches_pen = 5 if request.form.get('scratches') else 0
    dents_pen = 15 if request.form.get('dents') else 0
    water_pen = 40 if request.form.get('water') else 0
    btns_pen = 10 if not request.form.get('buttons') else 0
    cam_pen = 15 if not request.form.get('camera') else 0
    spk_pen = 10 if not request.form.get('speaker') else 0
    charger_pen = 0 if request.form.get('charger') else 5
    box_pen = 0 if request.form.get('box') else 3
    
    total_penalty = screen_penalty + bat_penalty + scratches_pen + dents_pen + water_pen + btns_pen + cam_pen + spk_pen + charger_pen + box_pen
    score = max(0, 100 - total_penalty)
    
    buyback_price = int((depreciated_base * score) / 100) if market_price > 0 else 0

    waterfall = [[0, market_price], [int(depreciated_base), market_price], [buyback_price, int(depreciated_base)], [0, buyback_price]]
    fomo_data = [buyback_price]
    temp_price = buyback_price
    for _ in range(6):
        temp_price = int(temp_price * 0.95)
        fomo_data.append(temp_price)

    heatmap = {
        'screen': screen_penalty <= 10, 'battery': battery <= 800,
        'body': not (request.form.get('scratches') or request.form.get('dents') or request.form.get('water')),
        'hardware': not (btns_pen or cam_pen or spk_pen),
    }
    
    battery_health = max(0, 100 - int(battery / 25))
    repair_cost = 0
    if screen_penalty >= 40: repair_cost += market_price * 0.15
    if btns_pen or cam_pen or spk_pen: repair_cost += market_price * 0.05
    if water_pen: repair_cost += market_price * 0.20
    if bat_penalty >= 12: repair_cost += 1500
    if dents_pen: repair_cost += 1000
    repair_cost = int(repair_cost)
    
    if score < 40 or water_pen: status = 'Salvage'
    elif repair_cost == 0 and score >= 80: status = 'Resale'
    else: status = 'Repair'
    
    ticket_id = f"RT-{random.randint(10000, 99999)}"
    raw_url = f"{request.host_url.rstrip('/')}/track/{ticket_id}"
    tracking_url = urllib.parse.quote(raw_url)
    
    total_investment = buyback_price + repair_cost
    
    # --- AI Price Prediction Engine (Regression) ---
    # 1. Brand Retention Premium (Brand value strength in 2nd-hand market)
    brand_retention = {
        'Apple': 1.15, 'Samsung': 1.05, 'Google': 1.02, 'OnePlus': 1.00, 
        'Xiaomi': 0.95, 'Vivo': 0.90, 'OPPO': 0.90
    }
    b_factor = brand_retention.get(brand, 0.85)
    
    # 2. Market Age Depreciation for Resale (Percentage of Original MRP)
    age_depreciation = {0: 0.85, 1: 0.68, 2: 0.52, 3: 0.38, 4: 0.25}
    age_factor = age_depreciation.get(age, 0.15)
    
    # 3. Permanent Issue Penalties (History of water/hardware damage reduces trust)
    issue_factor = 0.60 if water_pen else (0.85 if (cam_pen or btns_pen) else 1.0)
    
    # 4. Post-Repair Condition (Assuming we restore it to 95% health if repaired)
    post_repair_score = 95 if status == 'Repair' else score
    condition_factor = post_repair_score / 100.0
    
    # Raw AI Predicted Market Value
    ai_raw_val = market_price * b_factor * age_factor * condition_factor * issue_factor
    ai_price = int(ai_raw_val) if market_price > 0 else int(total_investment * 1.25)
    
    # Actual Resale Listing & Profit Margin Calculation
    if status == 'Salvage':
        resale_value = int(total_investment * 1.20)  # Parts salvage markup
        ai_price = int(total_investment * 1.10)
    else:
        # Smart Pricing: Sell at AI Market Value, but guarantee at least a 15% safety margin
        resale_value = max(int(total_investment * 1.15), ai_price)
        
    profit = resale_value - total_investment
    margin_perc = round((profit / total_investment) * 100, 1) if total_investment > 0 else 0
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Safely handle Customers to prevent Duplicate Entry errors
        if contact:
            cursor.execute("SELECT CustomerID FROM Customers WHERE Contact = %s", (contact,))
        else:
            cursor.execute("SELECT CustomerID FROM Customers WHERE FullName = %s", (name,))
            
        existing_cust = cursor.fetchone()
        if existing_cust:
            cust_id = existing_cust[0]
        else:
            cursor.execute("INSERT INTO Customers (FullName, Contact) VALUES (%s, %s)", (name, contact))
            cust_id = cursor.lastrowid
            
        # 2. Ensure Strict Data Types for Devices Insert
        safe_storage = storage if storage else "N/A"
        safe_year = int(purchase_year)
        screen_score = 100 - screen_penalty
        
        sql = """INSERT INTO Devices (OwnerID, Brand, Model, DeviceType, Storage, PurchaseYear, 
                 BatteryCycleCount, ScreenCondition, HealthScore, CurrentStatus, BuybackPrice, TicketID) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (cust_id, brand, model, device_type, safe_storage, safe_year, battery, screen_score, score, status, buyback_price, ticket_id)
        cursor.execute(sql, val)
        
        device_id = cursor.lastrowid
        cursor.execute("INSERT INTO DeviceLogs (DeviceID, OldStatus, NewStatus, ChangedBy) VALUES (%s, 'System Received', %s, 'System')", (device_id, status))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"\n{'='*50}\nDATABASE INSERT ERROR:\n{e}\n{'='*50}\n")
    
    return render_template('result.html', status=status, score=score, brand=brand, model=model, 
                           purchase_date=purchase_date_combined, price=buyback_price, 
                           waterfall=waterfall, fomo_data=fomo_data, heatmap=heatmap, 
                           ticket_id=ticket_id, tracking_url=tracking_url, battery_health=battery_health, 
                           repair_cost=repair_cost, resale_value=resale_value, ai_price=ai_price, profit=profit, margin_perc=margin_perc, condition=condition)

@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('q', '')
    time_filter = request.args.get('filter', 'all')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    if search_query:
        search_pattern = f"%{search_query}%"
        cursor.execute("""
            SELECT d.*, c.FullName, c.Contact, c.CustomerID FROM Devices d 
            JOIN Customers c ON d.OwnerID = c.CustomerID 
            WHERE c.FullName LIKE %s OR c.Contact LIKE %s OR d.Brand LIKE %s OR d.Model LIKE %s OR d.TicketID LIKE %s
            ORDER BY d.DeviceID DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    else:
        cursor.execute("""
            SELECT d.*, c.FullName, c.Contact, c.CustomerID FROM Devices d 
            JOIN Customers c ON d.OwnerID = c.CustomerID 
            ORDER BY d.DeviceID DESC
        """)
    devices = cursor.fetchall()
    
    total_devices = len(devices)
    total_buyback = sum(d['BuybackPrice'] for d in devices)
    
    # Calculate simulated actuals since we don't store exact historical profit in DB
    total_revenue = sum(int(d['BuybackPrice'] * 1.35) for d in devices)
    total_profit = sum(int(d['BuybackPrice'] * 0.25) for d in devices)
    avg_profit = int(total_profit / total_devices) if total_devices > 0 else 0
    
    stats = {
        'total_val': total_buyback,
        'total_devices': total_devices,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'avg_profit': avg_profit,
        'repair': len([d for d in devices if d['CurrentStatus'] == 'Repair']),
        'resale': len([d for d in devices if d['CurrentStatus'] == 'Resale'])
    }
    
    cursor.execute("SELECT Brand, COUNT(*) as count FROM Devices GROUP BY Brand")
    brand_share = cursor.fetchall()
    
    # Fetch All Complaints
    cursor.execute("""
        SELECT c.*, d.Brand, d.Model, cust.FullName, cust.Contact 
        FROM Complaints c
        JOIN Devices d ON c.DeviceID = d.DeviceID
        JOIN Customers cust ON c.CustomerID = cust.CustomerID
        ORDER BY c.CreatedAt DESC
    """)
    complaints = cursor.fetchall()
    
    conn.close()
    
    # Mocking 6-month trend data for the visual dashboard
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    current_month_idx = 3 # April is index 3 (0-based)
    trend_labels = []
    trend_revenue = []
    trend_profit = []
    
    base_rev = total_revenue / 6 if total_revenue > 0 else 15000
    base_prof = total_profit / 6 if total_profit > 0 else 3500
    
    for i in range(5, -1, -1):
        m_idx = (current_month_idx - i) % 12
        trend_labels.append(months[m_idx])
        multiplier = random.uniform(0.7, 1.3)
        trend_revenue.append(int(base_rev * multiplier))
        trend_profit.append(int(base_prof * multiplier))
        
    trend_data = {'labels': trend_labels, 'revenue': trend_revenue, 'profit': trend_profit}
    
    return render_template('dashboard.html', devices=devices, stats=stats, brand_share=brand_share, search_query=search_query, time_filter=time_filter, trend_data=trend_data, complaints=complaints)

@app.route('/customer/<int:customer_id>')
@login_required
def customer_profile(customer_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = %s", (customer_id,))
    customer = cursor.fetchone()
    
    if not customer:
        conn.close()
        return redirect(url_for('dashboard'))
        
    cursor.execute("SELECT * FROM Devices WHERE OwnerID = %s ORDER BY DeviceID DESC", (customer_id,))
    devices = cursor.fetchall()
    
    cursor.execute("""
        SELECT dl.*, d.Brand, d.Model, d.TicketID 
        FROM DeviceLogs dl
        JOIN Devices d ON dl.DeviceID = d.DeviceID
        WHERE d.OwnerID = %s
        ORDER BY dl.LogID DESC
    """, (customer_id,))
    logs = cursor.fetchall()
    conn.close()
    
    total_value = sum(d['BuybackPrice'] for d in devices)
    return render_template('customer_profile.html', customer=customer, devices=devices, logs=logs, total_value=total_value)

@app.route('/edit_status/<int:device_id>', methods=['POST'])
@login_required
def edit_status(device_id):
    new_status = request.form['new_status']
    username = session.get('username', 'admin')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CurrentStatus FROM Devices WHERE DeviceID = %s", (device_id,))
    device = cursor.fetchone()
    old_status = device['CurrentStatus']
    
    if old_status != new_status:
        cursor.execute("UPDATE Devices SET CurrentStatus = %s WHERE DeviceID = %s", (new_status, device_id))
        cursor.execute("INSERT INTO DeviceLogs (DeviceID, OldStatus, NewStatus, ChangedBy) VALUES (%s, %s, %s, %s)", (device_id, old_status, new_status, username))
        conn.commit()
        
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_device/<int:device_id>')
@login_required
def delete_device(device_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Devices WHERE DeviceID = %s", (device_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/clear_inventory')
@login_required
def clear_inventory():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Devices")
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/track/<ticket_id>')
def track_device(ticket_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CurrentStatus, BuybackPrice FROM Devices WHERE TicketID = %s", (ticket_id,))
    device = cursor.fetchone()
    conn.close()
    
    if device:
        status = device['CurrentStatus']
        price = device['BuybackPrice']
    else:
        status = 'Repair'
        price = 'Evaluating...'
    
    if status == 'Resale': stage = "Quality Passed - Ready for Sale"
    elif status == 'Salvage': stage = "Scrapped & Salvaging Parts"
    else: stage = "In Repair Facility"
    return render_template('track.html', ticket_id=ticket_id, stage=stage, price=price, status=status)

@app.route('/raise_complaint', methods=['POST'])
def raise_complaint():
    if not session.get('logged_in') or session.get('role') != 'customer':
        return redirect(url_for('customer_login'))
        
    device_id = request.form['device_id']
    issue = request.form['issue']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Complaints (DeviceID, CustomerID, Issue) VALUES (%s, %s, %s)", (device_id, session['customer_id'], issue))
    conn.commit()
    conn.close()
    return redirect(url_for('customer_dashboard'))

@app.route('/update_complaint/<int:complaint_id>', methods=['POST'])
@login_required
def update_complaint(complaint_id):
    new_status = request.form['status']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Complaints SET Status = %s WHERE ComplaintID = %s", (new_status, complaint_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
