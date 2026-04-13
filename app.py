import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, VendorProfile, Product, Order, OrderItem, CartItem
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Public & Auth Routes ---
@app.route('/')
def index():
    # Only show active/approved businesses on the homepage
    businesses = VendorProfile.query.filter_by(status='active').all()
    return render_template('index.html', businesses=businesses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'vendor':
                if not user.vendor_profile:
                    return redirect(url_for('vendor_setup'))
                return redirect(url_for('vendor_dashboard'))
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'customer')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username, email=email, role=role, 
            password_hash=generate_password_hash(password),
            phone_number=request.form.get('phone_number'),
            address=request.form.get('address')
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        
        if role == 'vendor':
            return redirect(url_for('vendor_setup'))
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Vendor Routes ---
@app.route('/vendor/setup', methods=['GET', 'POST'])
@login_required
def vendor_setup():
    if current_user.role != 'vendor':
        return redirect(url_for('index'))
    if current_user.vendor_profile:
        return redirect(url_for('vendor_dashboard'))
        
    if request.method == 'POST':
        b_name = request.form.get('business_name')
        desc = request.form.get('description')
        gst = request.form.get('gst_number')
        seller_name = request.form.get('seller_name')
        aadhar = request.form.get('aadhar_number')
        msme = request.form.get('msme_registration')
        family_bg = request.form.get('family_background')
        
        # File uploads
        logo_file = request.files.get('logo')
        banner_file = request.files.get('banner')
        
        logo_filename = 'default_logo.png'
        banner_filename = 'default_banner.png'
        
        if logo_file and logo_file.filename != '':
            logo_filename = secure_filename(logo_file.filename)
            logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'logos', logo_filename))
            
        if banner_file and banner_file.filename != '':
            banner_filename = secure_filename(banner_file.filename)
            banner_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'banners', banner_filename))
        
        profile = VendorProfile(
            user_id=current_user.id, business_name=b_name, description=desc,
            gst_number=gst, seller_name=seller_name, aadhar_number=aadhar,
            msme_registration=msme, family_background=family_bg,
            logo=logo_filename, banner=banner_filename, status='pending'
        )
        db.session.add(profile)
        db.session.commit()
        flash('Business details submitted for approval.', 'success')
        return redirect(url_for('vendor_add_product'))
        
    return render_template('vendor/setup.html')

@app.route('/vendor/add_product', methods=['GET', 'POST'])
@login_required
def vendor_add_product():
    if current_user.role != 'vendor' or not current_user.vendor_profile:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('title')
        desc = request.form.get('description')
        price = request.form.get('price')
        image_file = request.files.get('image')
        
        img_filename = 'default_product.png'
        if image_file and image_file.filename != '':
            img_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'products', img_filename))
            
        new_prod = Product(
            name=name, description=desc, price=float(price),
            image=img_filename, vendor_id=current_user.vendor_profile.id
        )
        db.session.add(new_prod)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('vendor_dashboard'))
    return render_template('vendor/add_product.html')

@app.route('/vendor/dashboard')
@login_required
def vendor_dashboard():
    if current_user.role != 'vendor':
        return redirect(url_for('index'))
    profile = current_user.vendor_profile
    if not profile:
        return redirect(url_for('vendor_setup'))
    products = Product.query.filter_by(vendor_id=profile.id).all()
    # Simple order fetching: products belong to this vendor, get order items
    return render_template('vendor/dashboard.html', profile=profile, products=products)

# --- Customer / Shopping Routes ---
@app.route('/business/<int:id>')
def business_details(id):
    business = VendorProfile.query.get_or_404(id)
    products = Product.query.filter_by(vendor_id=id, is_active=True).all()
    return render_template('customer/business.html', business=business, products=products)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    if current_user.role != 'customer':
        flash('Only customers can add to cart.', 'warning')
        return redirect(request.referrer or url_for('index'))
    
    existing = CartItem.query.filter_by(customer_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.quantity += 1
    else:
        new_item = CartItem(customer_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(new_item)
    db.session.commit()
    flash('Product added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
@login_required
def view_cart():
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    items = CartItem.query.filter_by(customer_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('customer/cart.html', items=items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    items = CartItem.query.filter_by(customer_id=current_user.id).all()
    if not items:
        flash('Cart is empty', 'warning')
        return redirect(url_for('index'))
        
    total = sum(item.product.price * item.quantity for item in items)
    
    if request.method == 'POST':
        address = request.form.get('delivery_address')
        payment_method = request.form.get('payment_method')
        
        new_order = Order(customer_id=current_user.id, total_price=total, payment_method=payment_method, delivery_address=address)
        db.session.add(new_order)
        db.session.flush() # get order id
        
        for item in items:
            order_item = OrderItem(order_id=new_order.id, product_id=item.product_id, quantity=item.quantity, price_at_time=item.product.price)
            db.session.add(order_item)
            db.session.delete(item) # remove from cart
            
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('customer_dashboard'))
        
    return render_template('customer/checkout.html', items=items, total=total)

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return redirect(url_for('index'))
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('customer/dashboard.html', orders=orders)


# --- Admin Routes ---
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    vendors = VendorProfile.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    users = User.query.all()
    return render_template('admin/dashboard.html', vendors=vendors, orders=orders, users=users)

@app.route('/admin/vendor/<int:id>/approve', methods=['POST'])
@login_required
def admin_approve_vendor(id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    vendor = VendorProfile.query.get_or_404(id)
    vendor.status = 'active'
    vendor.registration_number = f"BIZ-REG-{vendor.id}00X"
    db.session.commit()
    flash(f"Approved business: {vendor.business_name}", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/vendor/<int:id>/reject', methods=['POST'])
@login_required
def admin_reject_vendor(id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    vendor = VendorProfile.query.get_or_404(id)
    vendor.status = 'rejected'
    db.session.commit()
    flash(f"Rejected business: {vendor.business_name}", "danger")
    return redirect(url_for('admin_dashboard'))
    
@app.route('/admin/order/<int:id>/update_status', methods=['POST'])
@login_required
def admin_update_order(id):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    order = Order.query.get_or_404(id)
    order.status = request.form.get('status')
    db.session.commit()
    flash(f"Order status updated", "success")
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Host on 0.0.0.0 so we can access it externally if needed
    app.run(debug=True, use_reloader=False)

