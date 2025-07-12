from flask import Flask, render_template, request, redirect, url_for, session, flash

from db_config import connect
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret for session cookies




# =======================
# Landing Page
# =======================
@app.route('/')
def home():
    return render_template("landingpage.html")


@app.route('/landingpage')
def landing_page():
    if 'user_id' not in session:
        return redirect('/login')  # force login if session expired

    return render_template('landingpage.html', name=session.get('name'), email=session.get('email'), points=session.get('points'))




# =======================
# Registration Page
# =======================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect('/register')

        conn = connect()
        cur = conn.cursor()
        
        # Check if email already exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        if existing_user:
            flash("Email already registered", "warning")
            conn.close()
            return redirect('/register')

        # Insert user
        cur.execute("INSERT INTO users (name, email, password, points) VALUES (%s, %s, %s, 0)", 
                    (name, email, password))
        conn.commit()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect('/login')

    return render_template('registration.html')


# =======================
# Login Page
# =======================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Check if admin
        cur.execute("SELECT * FROM admins WHERE email = %s AND password = %s", (email, password))
        admin = cur.fetchone()

        if admin:
            session['admin_id'] = admin['admin_id']
            flash("Welcome Admin!", "info")
            return redirect('/admin')

        # Check if user
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            flash(f"Welcome {user['name']}!", "success")
            return redirect('/userdashboard')

        flash("Invalid credentials", "danger")
        return redirect('/login')

    return render_template('login.html')

# =======================
# User Dashboard
# =======================
@app.route("/userdashboard")
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name, email, points FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    cur.execute("SELECT * FROM items WHERE user_id = %s", (user_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("userdashboard.html", name=user[0], email=user[1], points=user[2], items=items)

# =======================
# Item Listing Page (Show all items)
# =======================
@app.route('/itemListing')
def item_listing():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE user_id = %s", (session['user_id'],))
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('itemListing.html', items=items)


# =======================
# Add New Item (Form)
# =======================
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        user_id = session['user_id']
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        type_ = request.form['type']  # avoid using 'type' keyword
        size = request.form['size']
        condition = request.form['condition']
        tags = request.form['tags']
        image_url = request.form['image_url']
        status = 'available'

        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO items (user_id, title, description, category, type, size, condition, tags, image_url, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, title, description, category, type_, size, condition, tags, image_url, status))
        conn.commit()
        cur.close()
        conn.close()

        flash("Item listed successfully!", "success")
        return redirect('/dashboard')

    # Render the item upload form on GET
    return render_template("itemListing.html")


#--------------------------
#admin_dashboard
@app.route('/admin')
def admin_dashboard():
    if 'admin_id' not in session:
        flash("Access denied. Admins only.", "danger")
        return redirect('/login')

    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("adminDashboard.html", users=users, items=items)

# =======================
# View Item Details by ID
# =======================
@app.route('/product/<int:item_id>')
def product_details(item_id):
    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("ProductdetailsPage.html", item=item)

# =======================
# Logout
# =======================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect('/login')


@app.route('/')
def landing():
    return render_template("landingpage.html")


# =======================
# Run Flask App
# =======================
if __name__ == '__main__':
    app.run(debug=True)
