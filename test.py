from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# Use PyMySQL as a drop-in replacement for MySQLdb on Windows to avoid mysqlclient build issues
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception as _e:
    # Safe to continue; if MySQLdb is present, it'll be used. This helps Windows setups.
    pass
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "spiderman123" 


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Your MySQL password here
app.config['MYSQL_DB'] = 'MunchyDB'  # Make sure this database exists

mysql = MySQL(app)

def init_db():
    with app.app_context():
        cur = None
        try:
            # Attempt to get a cursor; if MySQL is down, this will fail gracefully
            cur = mysql.connection.cursor()
            # Check if delivery_address table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS delivery_address (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    location VARCHAR(255),
                    street VARCHAR(255),
                    apartment VARCHAR(255),
                    agent_message TEXT,
                    accepted BOOLEAN DEFAULT FALSE,
                    delivered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    food_id INT,
                    hidden BOOLEAN DEFAULT FALSE,
                    order_status VARCHAR(50) DEFAULT 'Order Placed',
                    payment_method VARCHAR(50),
                    FOREIGN KEY (user_id) REFERENCES customer(id),
                    FOREIGN KEY (food_id) REFERENCES food(id)
                )
            """)
            
            # Create reviews table if it doesn't exist
            print("Checking for reviews table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    food_id INT NOT NULL,
                    user_id INT NOT NULL,
                    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES customer(id) ON DELETE CASCADE
                )
            """)
            print("Reviews table checked/created")
            
            # Create payment table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payment (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    payment_method VARCHAR(50) NOT NULL,
                    card_number VARCHAR(255),
                    expiry VARCHAR(10),
                    cvc VARCHAR(10),
                    cardholder VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if payment_method column exists in delivery_address
            try:
                cur.execute("SHOW COLUMNS FROM delivery_address LIKE 'payment_method'")
                if not cur.fetchone():
                    print("Adding payment_method column to delivery_address table")
                    cur.execute("ALTER TABLE delivery_address ADD COLUMN payment_method VARCHAR(50)")
                
                mysql.connection.commit()
                print("Payment tables and columns checked and added if necessary")
            except Exception as e:
                print(f"Error checking payment columns: {str(e)}")
            
            # Ensure 'available' column exists in food table (used by multiple routes)
            try:
                cur.execute("SHOW COLUMNS FROM food LIKE 'available'")
                if not cur.fetchone():
                    print("Adding 'available' column to food table")
                    cur.execute("ALTER TABLE food ADD COLUMN available BOOLEAN DEFAULT TRUE")
                    mysql.connection.commit()
            except Exception as e:
                # If food table doesn't exist yet, skip silently
                print(f"Note: Could not ensure 'available' column on food table: {str(e)}")
                
            mysql.connection.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
        finally:
            if cur:
                cur.close()

# Initialize database when app starts
init_db()

@app.route("/")
def home():
    return render_template("home.html")

ADMIN_EMAIL = "munchadmin@gmail.com"
ADMIN_PASSWORD = "admin123!"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Admin login successful!")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('admin'))
    return render_template("admin.html")

@app.route("/restaurant/request", methods=["GET", "POST"])
def restaurant_request():
    if request.method == "POST":
        restaurant_name = request.form['restaurant_name']
        owner_name = request.form['owner_name']
        food_name = request.form['food_name']
        price = request.form['price']
        category = request.form['category']

        # Handle image upload
        image_file = request.files['image']
        image_filename = None
        if image_file and image_file.filename:
            # Save the image to the static/uploads folder (create this folder if it doesn't exist)
            import os
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_filename = image_file.filename
            image_path = os.path.join(upload_folder, image_filename)
            image_file.save(image_path)
        else:
            flash("Image upload failed.")
            return redirect(url_for('restaurant_request'))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO restaurant_requests 
            (restaurant_name, owner_name, food_name, image, price, category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (restaurant_name, owner_name, food_name, f"uploads/{image_filename}", price, category))
        mysql.connection.commit()
        cur.close()
        flash("Request submitted! Awaiting admin approval.")
        return redirect(url_for('home'))
    return render_template("restaurant_request.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Please login as admin first.")
        return redirect(url_for('admin'))
    cur = mysql.connection.cursor()
    
    try:
        # Fetch food items
        cur.execute("SELECT * FROM food")
        foods = [
            dict(
                id=row[0],
                name=row[1],
                image=row[2],
                rating=row[3],
                price=row[4]
            )
            for row in cur.fetchall()
        ]
        
        # Fetch pending restaurant requests
        cur.execute("SELECT * FROM restaurant_requests WHERE approved=FALSE")
        requests = cur.fetchall()
        
        # Fetch pending restaurant approvals
        cur.execute("SELECT * FROM restaurants WHERE approved=FALSE")
        pending_restaurants = cur.fetchall()
        
        # Fetch all reviews with food and user info
        print("DEBUG - Fetching reviews for admin dashboard")
        try:
            cur.execute("""
                SELECT reviews.id, food.name, customer.name, reviews.rating, reviews.review_text, reviews.created_at,
                       food.image, food.id as food_id, customer.id as user_id
                FROM reviews
                JOIN food ON reviews.food_id = food.id
                JOIN customer ON reviews.user_id = customer.id
                ORDER BY reviews.created_at DESC
            """)
            reviews = cur.fetchall()
            print(f"DEBUG - Fetched {len(reviews)} reviews")
            
            if not reviews:
                # Check if reviews table has any rows
                cur.execute("SELECT COUNT(*) FROM reviews")
                review_count = cur.fetchone()[0]
                print(f"DEBUG - Total reviews in database: {review_count}")
                
                # If we have reviews but the join failed, try without the joins
                if review_count > 0:
                    print("DEBUG - Reviews exist but join failed, fetching without joins")
                    cur.execute("""
                        SELECT id, food_id, user_id, rating, review_text, created_at
                        FROM reviews
                        ORDER BY created_at DESC
                    """)
                    reviews = cur.fetchall()
                    print(f"DEBUG - Fetched {len(reviews)} reviews without joins")
        except Exception as e:
            print(f"DEBUG - Error fetching reviews: {str(e)}")
            reviews = []
        
        return render_template(
            "admin_dashboard.html",
            foods=foods,
            requests=requests,
            pending_restaurants=pending_restaurants,
            reviews=reviews
        )
    except Exception as e:
        print(f"DEBUG - Error in admin dashboard: {str(e)}")
        flash("An error occurred while loading the dashboard.")
        return redirect(url_for('admin'))
    finally:
        cur.close()

@app.route("/admin/approve_request/<int:request_id>", methods=["POST"])
def approve_request(request_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin_dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM restaurant_requests WHERE id = %s", (request_id,))
    req = cur.fetchone()
    if req:
        # Check if restaurant is approved
        cur.execute("SELECT name FROM restaurants WHERE LOWER(name)=LOWER(%s) AND approved=TRUE", (req[1],))
        restaurant = cur.fetchone()
        if restaurant:
            # Restaurant is approved, add food
            cur.execute("""
                INSERT INTO food (name, image, rating, price, restaurant_name, category) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                req[3], req[4], 0, req[5], req[1], req[6]
            ))
            cur.execute("UPDATE restaurant_requests SET approved=TRUE WHERE id=%s", (request_id,))
            mysql.connection.commit()
            flash("Food approved and added to restaurant!")
        else:
            flash("Restaurant must be approved before approving food!")
    cur.close()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/reject_request/<int:request_id>", methods=["POST"])
def reject_request(request_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin_dashboard'))
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM restaurant_requests WHERE id = %s", (request_id,))
        mysql.connection.commit()
        flash("Food request rejected and removed.")
    except Exception as e:
        flash("Error rejecting food request.")
    finally:
        cur.close()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/food/delete/<int:food_id>", methods=["POST"])
def delete_food(food_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin'))
    cur = mysql.connection.cursor()
    try:
        # First check and delete any reviews for this food
        cur.execute("DELETE FROM reviews WHERE food_id = %s", (food_id,))
        
        # Then delete the food
        cur.execute("DELETE FROM food WHERE id = %s", (food_id,))
        mysql.connection.commit()
        flash("Food deleted.")
    except Exception as e:
        mysql.connection.rollback()
        print(f"Error deleting food: {str(e)}")
        flash(f"Error deleting food: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/food/edit/<int:food_id>", methods=["GET", "POST"])
def edit_food(food_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin'))
        
    cur = mysql.connection.cursor()
    
    if request.method == "POST":
        name = request.form['name']
        image = request.form['image']
        rating = request.form['rating']
        price = request.form['price']
        category = request.form['category']
        restaurant_name = request.form['restaurant_name']
        
        cur.execute("""
            UPDATE food 
            SET name=%s, image=%s, rating=%s, price=%s, category=%s, restaurant_name=%s 
            WHERE id=%s
        """, (name, image, rating, price, category, restaurant_name, food_id))
        
        mysql.connection.commit()
        flash("Food updated successfully!")
        return redirect(url_for('admin_dashboard'))
    else:
        cur.execute("SELECT * FROM food WHERE id = %s", (food_id,))
        food = cur.fetchone()
        cur.close()
        
        if not food:
            flash("Food not found!")
            return redirect(url_for('admin_dashboard'))
            
        return render_template("edit_food.html", food=food)

@app.route("/admin/food/add", methods=["GET", "POST"])
def add_food():
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin'))
    if request.method == "POST":
        name = request.form['name']
        image = request.form['image']
        rating = request.form['rating']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO food (name, image, rating, price) VALUES (%s, %s, %s, %s)",
                    (name, image, rating, price))
        mysql.connection.commit()
        cur.close()
        flash("Food added.")
        return redirect(url_for('admin_dashboard'))
    return render_template("add_food.html")

@app.route("/signup", methods=["POST"])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO customer (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, hashed_password))
    mysql.connection.commit()
    cur.close()
    flash("Signup successful! You can now login.")
    return redirect(url_for('home'))


@app.route("/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    
    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        flash("this is for admin login only")
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):  
        session['user_id'] = user[0]
        session['email'] = user[2]
        flash("Login successful!")
        return redirect(url_for('restaurant_list'))  
    else:
        flash("Invalid email or password.")
        return redirect(url_for('home'))

@app.route("/customer/dashboard")
def customer_dashboard():
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    # Use GROUP BY to ensure each food appears only once
    cur.execute("""
        SELECT f.id, f.name, f.image, f.rating, f.price, 
               COALESCE(r.restaurant_name, 'Admin') as restaurant_name,
               f.category, f.available
        FROM food f
        LEFT JOIN restaurant_requests r
            ON f.name = r.food_name AND r.approved = TRUE
        GROUP BY f.id
    """)
    foods = [
        dict(
            id=row[0],
            name=row[1],
            image=row[2] if row[2] else None,
            rating=row[3],
            price=row[4],
            restaurant_name=row[5],
            category=row[6].lower() if row[6] else 'other',
            available=row[7] if row[7] is not None else True
        )
        for row in cur.fetchall()
    ]
    cur.close()
    return render_template("customer_dashboard.html", foods=foods)

@app.route("/customer/dashboard/<int:restaurant_id>")
def customer_dashboard_restaurant(restaurant_id):
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT name FROM restaurants WHERE id=%s", (restaurant_id,))
    rest_name = cur.fetchone()
    if not rest_name:
        flash("Restaurant not found.")
        return redirect(url_for('restaurant_list'))

    cur.execute("""
        SELECT f.id, f.name, f.image, f.rating, f.price, f.restaurant_name, f.category, f.available
        FROM food f
        WHERE f.restaurant_name=%s
    """, (rest_name[0],))
    foods = [
        dict(
            id=row[0],
            name=row[1],
            image=row[2] if row[2] else None,
            rating=row[3],
            price=row[4],
            restaurant_name=row[5],
            category=row[6].lower() if row[6] else 'other',
            available=row[7] if row[7] is not None else True
        )
        for row in cur.fetchall()
    ]
    cur.close()
    return render_template("customer_dashboard.html", foods=foods, selected_restaurant=rest_name[0])

@app.route("/user/profile", methods=["GET", "POST"])
def user_profile():
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))
    
    cur = mysql.connection.cursor()
    try:
        # Process POST request for profile update
        if request.method == "POST":
            name = request.form.get('name')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Check if we need to update the password
            if new_password and new_password == confirm_password:
                # Generate hashed password and update both name and password
                hashed_password = generate_password_hash(new_password)
                cur.execute("""
                    UPDATE customer 
                    SET name = %s, password_hash = %s 
                    WHERE id = %s
                """, (name, hashed_password, session['user_id']))
                mysql.connection.commit()
                flash("Profile and password updated successfully!")
            elif new_password:
                # Passwords don't match
                flash("Passwords don't match. Profile not updated.")
            else:
                
                cur.execute("UPDATE customer SET name = %s WHERE id = %s", 
                          (name, session['user_id']))
                mysql.connection.commit()
                flash("Profile updated successfully!")
        
        # Get user info for display 
        cur.execute("SELECT * FROM customer WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        
        if not user:
            flash("User not found.")
            return redirect(url_for('home'))
        
        # Fetch all delivery 
        cur.execute("""
            SELECT da.id, da.agent_message, da.accepted, da.delivered, da.created_at, da.food_id,
                   f.name as food_name, f.image as food_image, da.order_status
            FROM delivery_address da
            LEFT JOIN food f ON da.food_id = f.id
            WHERE da.user_id = %s 
              AND (da.hidden IS NULL OR da.hidden = FALSE)
            ORDER BY da.created_at DESC
        """, (session['user_id'],))
        
        messages = cur.fetchall()
        
        delivery_messages = []
        if messages:
            for msg in messages:
                status = "Delivered" if msg[3] else ("Accepted" if msg[2] else "Pending")
                delivery_messages.append({
                    'id': msg[0],
                    'message': msg[1],
                    'status': status,
                    'delivered': msg[3],
                    'created_at': msg[4],
                    'food_id': msg[5],
                    'food_name': msg[6],
                    'food_image': msg[7],
                    'order_status': msg[8] if len(msg) > 8 else "Order Placed"
                })
        
        # Fetch reviewed food_ids for the user
        cur.execute("SELECT food_id FROM reviews WHERE user_id = %s", (session['user_id'],))
        reviewed_foods = set(row[0] for row in cur.fetchall())
        
        # Fetch user's reviews
        cur.execute("""
            SELECT r.id, r.food_id, f.name, r.rating, r.review_text, r.created_at
            FROM reviews r
            JOIN food f ON r.food_id = f.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (session['user_id'],))
        
        user_reviews = [
            {
                'id': row[0],
                'food_id': row[1],
                'food_name': row[2],
                'rating': row[3],
                'review_text': row[4],
                'created_at': row[5]
            }
            for row in cur.fetchall()
        ]
        
        return render_template(
            "user_profile.html", 
            user={"name": user[1], "email": user[2]}, 
            delivery_messages=delivery_messages,
            reviewed_foods=reviewed_foods,
            user_reviews=user_reviews
        )
    except Exception as e:
        print(f"Error in user_profile: {str(e)}")
        flash("Error loading profile.")
        return redirect(url_for('home'))
    finally:
        cur.close()

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    food_id = request.form.get('food_id')
    if not food_id:
        return "No food ID", 400

    
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

   
    if food_id in cart:
        cart[food_id] += 1
    else:
        cart[food_id] = 1

    session['cart'] = cart
    session.modified = True
    return jsonify({'success': True, 'cart': cart})

@app.route('/update-cart', methods=['POST'])
def update_cart():
    food_id = request.form.get('food_id')
    quantity = int(request.form.get('quantity', 1))
    if 'cart' in session and food_id in session['cart']:
        if quantity > 0:
            session['cart'][food_id] = quantity
        else:
            session['cart'].pop(food_id)
        session.modified = True
    return jsonify({'success': True, 'cart': session.get('cart', {})})

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    food_id = request.form.get('food_id')
    if 'cart' in session and food_id in session['cart']:
        session['cart'].pop(food_id)
        session.modified = True
    return jsonify({'success': True, 'cart': session.get('cart', {})})

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    food_details = []
    total = 0.0

    if cart:
        cur = mysql.connection.cursor()
        # Fetch all food details in one query
        format_strings = ','.join(['%s'] * len(cart))
        cur.execute(f"SELECT id, name, image, price FROM food WHERE id IN ({format_strings})", tuple(cart.keys()))
        foods = {str(row[0]): {'name': row[1], 'image': row[2], 'price': float(row[3])} for row in cur.fetchall()}
        cur.close()

        for food_id, quantity in cart.items():
            if food_id in foods:
                food = foods[food_id]
                subtotal = food['price'] * quantity
                total += subtotal
                food_details.append({
                    'id': food_id,
                    'name': food['name'],
                    'image': food['image'],
                    'price': food['price'],
                    'quantity': quantity,
                    'subtotal': subtotal
                })

    return render_template('cart.html', cart=food_details, total=total)

@app.route("/restaurant/register", methods=["GET", "POST"])
def restaurant_register():
    if request.method == "POST":
        restaurant_name = request.form['restaurant_name']
        owner_name = request.form['owner_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO restaurant_accounts (restaurant_name, owner_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (restaurant_name, owner_name, email, hashed_password))
            mysql.connection.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for('restaurant_login'))
        except Exception as e:
            flash("Registration failed. Email may already be registered.")
            return redirect(url_for('restaurant_register'))
        finally:
            cur.close()
    return render_template("resturant.html")

@app.route("/restaurant/login", methods=["GET", "POST"])
def restaurant_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM restaurant_accounts WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user[4], password):
            session['restaurant_id'] = user[0]
            session['restaurant_email'] = user[3]
            
            return redirect(url_for('restaurant_profile'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('restaurant_login'))
    return render_template("resturant.html")

@app.route("/restaurant/dashboard")
def restaurant_dashboard():
    if not session.get('restaurant_id'):
        flash("Please login first.")
        return redirect(url_for('restaurant_login'))
    return "Welcome to your restaurant dashboard!"

@app.route("/restaurant/profile")
def restaurant_profile():
    if not session.get('restaurant_id'):
        flash("Please login first.")
        return redirect(url_for('restaurant_login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT restaurant_name, owner_name, email, created_at FROM restaurant_accounts WHERE id=%s", (session['restaurant_id'],))
    info = cur.fetchone()
    # Fetch foods for this restaurant
    cur.execute("SELECT id, name, available FROM food WHERE restaurant_name=%s", (info[0],))
    foods = [dict(id=row[0], name=row[1], available=row[2]) for row in cur.fetchall()]
    cur.close()
    if not info:
        flash("Profile not found.")
        return redirect(url_for('restaurant_login'))
    return render_template("restueant_profile.html", info=info, foods=foods)

@app.route("/restaurant/logout")
def restaurant_logout():
    session.pop('restaurant_id', None)
    session.pop('restaurant_email', None)
    flash("Logged out.")
    return redirect(url_for('restaurant_login'))

@app.route("/restaurant/toggle_availability/<int:food_id>", methods=["POST"])
def toggle_availability(food_id):
    if not session.get('restaurant_id'):
        flash("Please login first.")
        return redirect(url_for('restaurant_login'))
    cur = mysql.connection.cursor()
    # Only allow the owner to toggle their own food
    cur.execute("SELECT restaurant_name FROM food WHERE id=%s", (food_id,))
    food = cur.fetchone()
    if not food:
        flash("Food not found.")
        return redirect(url_for('restaurant_profile'))
    # Toggle the available status
    cur.execute("UPDATE food SET available = NOT available WHERE id=%s", (food_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('restaurant_profile'))

@app.route("/restaurants")
def restaurant_list():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, image FROM restaurants WHERE approved=TRUE")
    restaurants = cur.fetchall()
    cur.close()
    return render_template("restaurant_list.html", restaurants=restaurants)

@app.route("/restaurant/add", methods=["POST"])
def restaurant_add():
    name = request.form['restaurant_name']
    image_file = request.files['restaurant_image']
    image_filename = None

    # Check for duplicate restaurant name (case-insensitive)
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM restaurants WHERE LOWER(name) = LOWER(%s)", (name,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        flash("Restaurant name already exists. Please choose a different name.")
        return redirect(url_for('restaurant_request'))

    if image_file and image_file.filename:
        import os
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_filename = image_file.filename
        image_path = os.path.join(upload_folder, image_filename)
        image_file.save(image_path)
    # Insert into restaurants table with approved=FALSE
    cur.execute("INSERT INTO restaurants (name, image, approved) VALUES (%s, %s, %s)", (name, f"uploads/{image_filename}", False))
    mysql.connection.commit()
    cur.close()
    flash("Restaurant submitted! Awaiting admin approval.")
    return redirect(url_for('restaurant_request'))

@app.route("/food/add", methods=["POST"])
def food_add():
    restaurant_name = request.form['restaurant_name']
    owner_name = request.form['owner_name']
    food_name = request.form['food_name']
    price = request.form['price']
    category = request.form['category']

    # Handle image upload
    image_file = request.files['image']
    image_filename = None
    if image_file and image_file.filename:
        import os
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        image_filename = image_file.filename
        image_path = os.path.join(upload_folder, image_filename)
        image_file.save(image_path)
    else:
        flash("Image upload failed.")
        return redirect(url_for('restaurant_request'))

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO restaurant_requests 
        (restaurant_name, owner_name, food_name, image, price, category, approved)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (restaurant_name, owner_name, food_name, f"uploads/{image_filename}", price, category, False))
    mysql.connection.commit()
    cur.close()
    flash("Food request submitted! Awaiting admin approval.")
    return redirect(url_for('home'))

@app.route("/admin/approve_restaurant/<int:restaurant_id>", methods=["POST"])
def approve_restaurant(restaurant_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin_dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("UPDATE restaurants SET approved=TRUE WHERE id=%s", (restaurant_id,))
    mysql.connection.commit()
    cur.close()
    flash("Restaurant approved successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/delete_restaurant/<int:restaurant_id>", methods=["POST"])
def delete_restaurant(restaurant_id):
    if not session.get('admin_logged_in'):
        flash("Unauthorized.")
        return redirect(url_for('admin_dashboard'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM restaurants WHERE id=%s", (restaurant_id,))
    mysql.connection.commit()
    cur.close()
    flash("Restaurant deleted successfully!")
    return redirect(url_for('admin_dashboard'))

@app.route('/delivery-address', methods=['GET', 'POST'])
def delivery_address():
    if request.method == 'POST':
        location = request.form.get('location')
        street = request.form.get('street')
        apartment = request.form.get('apartment')

        # Save to session
        session['location'] = location
        session['street'] = street
        session['apartment'] = apartment

        # Save to database
        user_id = session.get('user_id')
        food_id = session.get('food_id')
        
        if not user_id:
            flash("You must be logged in to save a delivery address.")
            return redirect(url_for('home'))
            
        if not food_id:
            # If no food_id in session, check if there are items in the cart
            if 'cart' in session and session['cart']:
                # Use the first food item from the cart
                food_id = list(session['cart'].keys())[0]
            else:
                flash("Please select a food item first.")
                return redirect(url_for('customer_dashboard'))
        
        # Convert food_id to integer to ensure it's valid
        try:
            food_id = int(food_id)
            
            # Verify food_id exists in the food table
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM food WHERE id = %s", (food_id,))
            food = cur.fetchone()
            
            if not food:
                flash("Selected food not found. Please select another item.")
                return redirect(url_for('customer_dashboard'))
                
            # Insert the delivery address with validated food_id
            cur.execute("""
                INSERT INTO delivery_address (user_id, location, street, apartment, food_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, location, street, apartment, food_id))
            mysql.connection.commit()
            cur.close()
            flash("Delivery address saved!")
            
        except (ValueError, TypeError):
            flash("Invalid food selection. Please try again.")
            return redirect(url_for('customer_dashboard'))

        return redirect(url_for('payment'))

    return render_template('delivery_address.html')


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        user_id = session.get('user_id')
        
        if not user_id:
            flash("Please login first.")
            return redirect(url_for('home'))
            
        # Get the latest delivery address entry for this user
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT id FROM delivery_address WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
            address_row = cur.fetchone()
            
            if not address_row:
                flash("Please provide delivery address first.")
                return redirect(url_for('delivery_address'))
                
            address_id = address_row[0]
            
            # Update delivery_address with payment method and status
            cur.execute("""
                UPDATE delivery_address 
                SET payment_method = %s,
                    order_status = 'Payment Received'
                WHERE id = %s
            """, (payment_method, address_id))
            
            # If credit card payment, insert into payment table
            if payment_method == 'card':
                card_number = request.form.get('card_number', '')
                expiry = request.form.get('expiry', '')
                cvc = request.form.get('cvc', '')
                cardholder = request.form.get('cardholder', '')
                
                # Insert into payment table
                cur.execute("""
                    INSERT INTO payment 
                    (payment_method, card_number, expiry, cvc, cardholder)
                    VALUES (%s, %s, %s, %s, %s)
                """, (payment_method, card_number, expiry, cvc, cardholder))
                
                print(f"Inserted card payment: {card_number}, {expiry}, {cvc}, {cardholder}")
            
            # Commit the transaction
            mysql.connection.commit()
            
            # Clear the cart after successful order placement
            if 'cart' in session:
                session.pop('cart')
                session.modified = True
            
            flash("Payment successful!")
            
        except Exception as e:
            print(f"Error processing payment: {str(e)}")
            flash("Error processing payment. Please try again.")
            return redirect(url_for('payment'))
        finally:
            cur.close()
            
        return redirect(url_for('waiting'))
        
    return render_template('payment.html')

@app.route('/waiting')
def waiting():
  
    user_id = session.get('user_id')
    if not user_id:
        flash("Please login first.")
        return redirect(url_for('home'))
        
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT agent_message, order_status, payment_method
            FROM delivery_address 
            WHERE user_id = %s 
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        
        order_row = cur.fetchone()
        
        if not order_row:
            flash("No order found.")
            return redirect(url_for('customer_dashboard'))
            
        agent_message = order_row[0]
        order_status = order_row[1] or "Order Placed"
        payment_method = order_row[2]
        payment_info = None
        
        return render_template(
            'waiting.html', 
            agent_message=agent_message, 
            order_status=order_status,
            payment_method=payment_method,
            payment_info=payment_info
        )
    except Exception as e:
        print(f"Error in waiting route: {str(e)}")
        flash("Error retrieving order information.")
        return redirect(url_for('customer_dashboard'))
    finally:
        cur.close()

@app.route('/agent', methods=['GET'])
def agent_portal():
    agent = session.get('agent')
    cur = mysql.connection.cursor()
    # Add food information to the query
    cur.execute("""
        SELECT da.id, da.location, da.street, da.apartment, da.accepted, da.delivered, da.food_id,
               f.name as food_name, f.image as food_image
        FROM delivery_address da
        LEFT JOIN food f ON da.food_id = f.id
        ORDER BY da.id DESC
    """)
    orders = cur.fetchall()
    pending_orders = []
    for row in orders:
        pending_orders.append({
            'id': row[0],
            'location': row[1],
            'street': row[2],
            'apartment': row[3],
            'accepted': row[4] if len(row) > 4 else False,
            'delivered': row[5] if len(row) > 5 else False,
            'food_id': row[6] if len(row) > 6 else None,
            'food_name': row[7] if len(row) > 7 else None,
            'food_image': row[8] if len(row) > 8 else None
        })
    cur.close()
    return render_template('agent.html', agent=agent, pending_orders=pending_orders)

@app.route('/agent/login', methods=['POST'])
def agent_login():
    email = request.form['email']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email FROM delivery_agents WHERE email=%s AND password=%s", (email, password))
    agent = cur.fetchone()
    cur.close()
    if agent:
        session['agent'] = {'id': agent[0], 'name': agent[1], 'email': agent[2]}
        flash("Login successful!")
    else:
        flash("Invalid credentials.")
    return redirect(url_for('agent_portal'))

@app.route('/agent/signup', methods=['POST'])
def agent_signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO delivery_agents (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    mysql.connection.commit()
    cur.close()
    flash("Signup successful! Please login.")
    return redirect(url_for('agent_portal'))

@app.route('/agent/logout', methods=['POST'])
def agent_logout():
    session.pop('agent', None)
    flash("Logged out.")
    return redirect(url_for('home'))

@app.route('/agent/accept_order/<int:order_id>', methods=['POST'])
def agent_accept_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE delivery_address SET accepted=TRUE WHERE id=%s", (order_id,))
    mysql.connection.commit()
    cur.close()
    flash("Order accepted!")
    return redirect(url_for('agent_portal'))

@app.route('/agent/reject_order/<int:order_id>', methods=['POST'])
def agent_reject_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM delivery_address WHERE id=%s", (order_id,))
    mysql.connection.commit()
    cur.close()
    flash("Order rejected.")
    return redirect(url_for('agent_portal'))

@app.route('/agent/message_customer/<int:order_id>', methods=['POST'])
def agent_message_customer(order_id):
    message = request.form['message']
    cur = mysql.connection.cursor()
    try:
        # First check if the order exists and get user_id
        cur.execute("SELECT user_id FROM delivery_address WHERE id = %s", (order_id,))
        order = cur.fetchone()
        if not order:
            flash("Order not found.")
            return redirect(url_for('agent_portal'))
            
        # Update the agent_message and set accepted to true
        cur.execute("""
            UPDATE delivery_address 
            SET agent_message = %s, accepted = TRUE 
            WHERE id = %s
        """, (message, order_id))
        mysql.connection.commit()
        print(f"Debug - Message saved for order {order_id}: {message}")  # Debug log
        flash("Message sent to customer.")
    except Exception as e:
        print(f"Error saving message: {str(e)}")  # Debug log
        flash("Error sending message.")
    finally:
        cur.close()
    return redirect(url_for('agent_portal'))

@app.route('/agent/parcel_delivered/<int:order_id>', methods=['POST'])
def agent_parcel_delivered(order_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            UPDATE delivery_address
            SET accepted = TRUE, delivered = TRUE
            WHERE id = %s
        """, (order_id,))
        mysql.connection.commit()
        flash("Parcel marked as delivered.")
    except Exception as e:
        flash("Error marking as delivered.")
    finally:
        cur.close()
    return redirect(url_for('agent_portal'))

@app.route('/review/<int:food_id>', methods=['GET', 'POST'])
def review(food_id):
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))
        
    cur = mysql.connection.cursor()
    try:
        # Get food details
        cur.execute("SELECT id, name FROM food WHERE id = %s", (food_id,))
        food = cur.fetchone()
        
        if not food:
            flash("Food not found.")
            return redirect(url_for('customer_dashboard'))
            
        if request.method == 'POST':
            try:
                rating = int(request.form.get('rating', 0))
                review_text = request.form.get('review', '').strip()
                
                print(f"DEBUG - Review submission - food_id: {food_id}, user_id: {session['user_id']}, rating: {rating}, text: {review_text}")
                
                if not rating or rating < 1 or rating > 5:
                    flash("Please provide a valid rating (1-5).")
                    return redirect(url_for('review', food_id=food_id))
                    
                if not review_text:
                    flash("Please provide a review text.")
                    return redirect(url_for('review', food_id=food_id))
                
                # Check if user has already reviewed this food
                cur.execute("SELECT id FROM reviews WHERE user_id = %s AND food_id = %s", 
                           (session['user_id'], food_id))
                if cur.fetchone():
                    flash("You have already reviewed this food.")
                    return redirect(url_for('user_profile'))
                
                # Insert the review - using explicit column names to avoid potential mismatches
                try:
                    # First attempt to insert the review
                    cur.execute("""
                        INSERT INTO reviews (food_id, user_id, rating, review_text)
                        VALUES (%s, %s, %s, %s)
                    """, (food_id, session['user_id'], rating, review_text))
                    
                    # Verify the insert by checking if the review was added
                    cur.execute("SELECT id FROM reviews WHERE user_id = %s AND food_id = %s", 
                               (session['user_id'], food_id))
                    review_id = cur.fetchone()
                    
                    if not review_id:
                        print("DEBUG - Review insertion failed - no review found after insert")
                        mysql.connection.rollback()
                        flash("Error saving review. Please try again.")
                        return redirect(url_for('review', food_id=food_id))
                    
                    print(f"DEBUG - Review inserted successfully with ID: {review_id[0]}")
                    
                    # Update food rating
                    cur.execute("""
                        UPDATE food 
                        SET rating = (
                            SELECT COALESCE(AVG(rating), 0)
                            FROM reviews 
                            WHERE food_id = %s
                        )
                        WHERE id = %s
                    """, (food_id, food_id))
                    
                    # Commit the transaction
                    mysql.connection.commit()
                    print("DEBUG - Transaction committed successfully")
                    flash("Thank you for your review!")
                    return redirect(url_for('user_profile'))
                    
                except Exception as db_error:
                    mysql.connection.rollback()
                    print(f"DEBUG - Database error: {str(db_error)}")
                    flash("An error occurred while saving your review.")
                    return redirect(url_for('review', food_id=food_id))
                
            except ValueError as ve:
                print(f"DEBUG - Value error: {str(ve)}")
                flash("Invalid rating value.")
                return redirect(url_for('review', food_id=food_id))
            except Exception as e:
                mysql.connection.rollback()
                print(f"DEBUG - Error saving review: {str(e)}")
                flash("An error occurred while saving your review.")
                return redirect(url_for('user_profile'))
            
        return render_template('review.html', food={'id': food[0], 'name': food[1]})
        
    except Exception as e:
        print(f"DEBUG - Error in review route: {str(e)}")
        flash("An error occurred while processing your review.")
        return redirect(url_for('user_profile'))
    finally:
        cur.close()

def get_food_id_by_name(food_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM food WHERE name = %s", (food_name,))
    result = cur.fetchone()
    cur.close()
    if result:
        return result[0]
    return None

@app.route('/order/<int:food_id>', methods=['GET'])
def order_food(food_id):
    # Optionally, check if food_id exists in food table
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM food WHERE id = %s", (food_id,))
    food = cur.fetchone()
    cur.close()
    if not food:
        flash("Food not found.")
        return redirect(url_for('customer_dashboard'))
    session['food_id'] = food_id
    return redirect(url_for('delivery_address'))

@app.route('/user/message_not_interested/<int:delivery_id>', methods=['POST'])
def message_not_interested(delivery_id):
    if not session.get('user_id'):
        flash("Thank you for your feedback!", "success")
        return redirect(url_for('home'))
    cur = mysql.connection.cursor()
    cur.execute("UPDATE delivery_address SET hidden = TRUE WHERE id = %s AND user_id = %s", (delivery_id, session['user_id']))
    mysql.connection.commit()
    cur.close()
    flash("Thank you for your feedback!", "success")
    return redirect(url_for('user_profile'))

@app.route('/agent/general_message', methods=['POST'])
def agent_general_message():
    message = request.form['message']
    cur = mysql.connection.cursor()
    try:
        # Update agent_message for all undelivered orders
        cur.execute("""
            UPDATE delivery_address
            SET agent_message = %s
            WHERE delivered = 0
        """, (message,))
        mysql.connection.commit()
        flash("Message sent to all customers with pending orders!")
    except Exception as e:
        flash("Error sending message.")
        print(f"Error in agent_general_message: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('agent_portal'))

@app.route('/agent/update_status/<int:order_id>/<status>', methods=['POST'])
def agent_update_status(order_id, status):
    status_map = {
        'received': 'Order Received',
        'on_the_way': 'On the Way',
        'delivered': 'Order Delivered'
    }
    if status not in status_map:
        flash("Invalid status.")
        return redirect(url_for('agent_portal'))
    cur = mysql.connection.cursor()
    try:
        # Update order status
        cur.execute("""
            UPDATE delivery_address
            SET order_status = %s, 
                accepted = TRUE,
                delivered = %s
            WHERE id = %s
        """, (
            status_map[status],
            1 if status == 'delivered' else 0,
            order_id
        ))
        
        # If delivered, add a message for the customer
        if status == 'delivered':
            cur.execute("""
                UPDATE delivery_address
                SET agent_message = 'Your order has been delivered! Please leave a review.'
                WHERE id = %s AND agent_message IS NULL
            """, (order_id,))
        
        mysql.connection.commit()
        flash(f"Order status updated to {status_map[status]}.")
    except Exception as e:
        flash("Error updating status.")
        print(f"Error updating status: {str(e)}")
    finally:
        cur.close()
    return redirect(url_for('agent_portal'))

@app.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))
        
    cur = mysql.connection.cursor()
    try:
        # Check if the review belongs to the current user
        cur.execute("""
            SELECT r.id, r.food_id, r.rating, r.review_text, f.name 
            FROM reviews r
            JOIN food f ON r.food_id = f.id
            WHERE r.id = %s AND r.user_id = %s
        """, (review_id, session['user_id']))
        review = cur.fetchone()
        
        if not review:
            flash("Review not found or unauthorized access.")
            return redirect(url_for('user_profile'))
            
        if request.method == 'POST':
            try:
                rating = int(request.form.get('rating', 0))
                review_text = request.form.get('review', '').strip()
                
                print(f"DEBUG - Review update - review_id: {review_id}, rating: {rating}, text: {review_text}")
                
                if not rating or rating < 1 or rating > 5:
                    flash("Please provide a valid rating (1-5).")
                    return redirect(url_for('edit_review', review_id=review_id))
                    
                if not review_text:
                    flash("Please provide a review text.")
                    return redirect(url_for('edit_review', review_id=review_id))
                
                # Update the review
                cur.execute("""
                    UPDATE reviews 
                    SET rating = %s, review_text = %s 
                    WHERE id = %s AND user_id = %s
                """, (rating, review_text, review_id, session['user_id']))
                
                # Update the food rating average
                cur.execute("""
                    UPDATE food 
                    SET rating = (
                        SELECT COALESCE(AVG(rating), 0)
                        FROM reviews 
                        WHERE food_id = %s
                    )
                    WHERE id = %s
                """, (review[1], review[1]))  # review[1] contains food_id
                
                mysql.connection.commit()
                print(f"DEBUG - Review updated successfully: {review_id}")
                flash("Your review has been updated!")
                return redirect(url_for('user_profile'))
                
            except ValueError as ve:
                print(f"DEBUG - Value error in edit_review: {str(ve)}")
                flash("Invalid rating value.")
                return redirect(url_for('edit_review', review_id=review_id))
            except Exception as e:
                mysql.connection.rollback()
                print(f"DEBUG - Error updating review: {str(e)}")
                flash("An error occurred while updating your review.")
                return redirect(url_for('edit_review', review_id=review_id))
        
        # GET request - show edit form
        return render_template('edit_review.html', review={
            'id': review[0],
            'food_id': review[1],
            'rating': review[2],
            'review_text': review[3],
            'food_name': review[4]
        })
        
    except Exception as e:
        print(f"DEBUG - Error in edit_review route: {str(e)}")
        flash("An error occurred while processing your request.")
        return redirect(url_for('user_profile'))
    finally:
        cur.close()

@app.route('/review/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if not session.get('user_id'):
        flash("Please login first.")
        return redirect(url_for('home'))
        
    cur = mysql.connection.cursor()
    try:
        # First, get the food_id from the review for updating the average rating later
        cur.execute("SELECT food_id FROM reviews WHERE id = %s AND user_id = %s", 
                   (review_id, session['user_id']))
        review = cur.fetchone()
        
        if not review:
            flash("Review not found or unauthorized access.")
            return redirect(url_for('user_profile'))
            
        food_id = review[0]
        
        # Delete the review
        cur.execute("DELETE FROM reviews WHERE id = %s AND user_id = %s", 
                   (review_id, session['user_id']))
                   
        if cur.rowcount == 0:
            flash("Failed to delete the review.")
            return redirect(url_for('user_profile'))
            
        # Update the food rating average
        cur.execute("""
            UPDATE food 
            SET rating = (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews 
                WHERE food_id = %s
            )
            WHERE id = %s
        """, (food_id, food_id))
        
        mysql.connection.commit()
        print(f"DEBUG - Review deleted successfully: {review_id}")
        flash("Your review has been deleted.")
        
    except Exception as e:
        mysql.connection.rollback()
        print(f"DEBUG - Error deleting review: {str(e)}")
        flash("An error occurred while deleting the review.")
        
    finally:
        cur.close()
        
    return redirect(url_for('user_profile'))

if __name__ == "__main__":
    app.run(debug=True)
